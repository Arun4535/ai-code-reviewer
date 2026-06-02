import json
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.errors import ExternalServiceError

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class AnthropicChatModel:
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model_name = model_name or settings.anthropic_model

    async def structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: type[SchemaT],
    ) -> SchemaT:
        if not self.api_key:
            return self._deterministic_fallback(user_payload, schema)

        tool_name = f"emit_{schema.__name__.lower()}"
        body = {
            "model": self.model_name,
            "max_tokens": 4096,
            "temperature": 0.1,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False),
                }
            ],
            "tools": [
                {
                    "name": tool_name,
                    "description": f"Emit a valid {schema.__name__} JSON object.",
                    "input_schema": schema.model_json_schema(),
                }
            ],
            "tool_choice": {"type": "tool", "name": tool_name},
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=settings.llm_request_timeout_seconds) as client:
                resp = await client.post("https://api.anthropic.com/v1/messages", json=body, headers=headers)
        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                f"Anthropic request timed out after {settings.llm_request_timeout_seconds:g} seconds. "
                "Try again, reduce the PR size, or increase LLM_REQUEST_TIMEOUT_SECONDS."
            ) from exc
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"Anthropic request failed before a response was received: {exc}") from exc
        if resp.status_code >= 400:
            raise ExternalServiceError(f"Anthropic request failed: {resp.status_code} {resp.text[:500]}")

        for block in resp.json().get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == tool_name:
                return schema.model_validate(block["input"])
        raise ExternalServiceError("Anthropic response did not include the expected structured tool output.")

    def _deterministic_fallback(self, user_payload: dict[str, Any], schema: type[SchemaT]) -> SchemaT:
        name = schema.__name__
        if name == "AgentResult":
            return schema.model_validate(
                {
                    "agent": user_payload.get("agent", "offline-agent"),
                    "intent": "Offline deterministic review used because ANTHROPIC_API_KEY is not configured.",
                    "findings": [],
                    "notes": ["Configure ANTHROPIC_API_KEY for real Claude review."],
                }
            )
        if name == "ReviewSummary":
            return schema.model_validate(
                {
                    "verdict": "Needs human review",
                    "risk_score": 35,
                    "executive_summary": "Offline mode completed structural analysis without model-generated findings.",
                    "prioritized_actions": ["Set ANTHROPIC_API_KEY and rerun the review.", "Inspect changed files manually before merge."],
                }
            )
        if name == "FollowUpResponse":
            return schema.model_validate(
                {
                    "answer": "This environment is running without ANTHROPIC_API_KEY, so follow-up answers use stored review context only.",
                    "citations": [],
                }
            )
        raise ExternalServiceError(f"No fallback registered for schema {name}")
