import json
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.errors import ExternalServiceError

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class GroqChatModel:
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key or settings.groq_api_key
        self.model_name = model_name or settings.groq_model

    async def structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: type[SchemaT],
    ) -> SchemaT:
        if not self.api_key:
            return self._deterministic_fallback(user_payload, schema)

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "schema": schema.model_json_schema(),
            },
        }
        body = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            "temperature": 0.1,
            "response_format": response_format,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=settings.llm_request_timeout_seconds) as client:
                resp = await client.post("https://api.groq.com/openai/v1/chat/completions", json=body, headers=headers)
        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                f"Groq request timed out after {settings.llm_request_timeout_seconds:g} seconds. "
                "Try again, reduce the PR size, or increase LLM_REQUEST_TIMEOUT_SECONDS."
            ) from exc
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"Groq request failed before a response was received: {exc}") from exc
        if resp.status_code >= 400:
            raise ExternalServiceError(f"Groq request failed: {resp.status_code} {resp.text[:500]}")
        content = resp.json()["choices"][0]["message"]["content"]
        return schema.model_validate_json(content)

    def _deterministic_fallback(self, user_payload: dict[str, Any], schema: type[SchemaT]) -> SchemaT:
        name = schema.__name__
        if name == "AgentResult":
            return schema.model_validate(
                {
                    "agent": user_payload.get("agent", "offline-agent"),
                    "intent": "Offline deterministic review used because GROQ_API_KEY is not configured.",
                    "findings": [],
                    "notes": ["Configure GROQ_API_KEY for real model review."],
                }
            )
        if name == "ReviewSummary":
            return schema.model_validate(
                {
                    "verdict": "Needs human review",
                    "risk_score": 35,
                    "executive_summary": "Offline mode completed structural analysis without model-generated findings.",
                    "prioritized_actions": ["Set GROQ_API_KEY and rerun the review.", "Inspect changed files manually before merge."],
                }
            )
        if name == "FollowUpResponse":
            return schema.model_validate(
                {
                    "answer": "This environment is running without GROQ_API_KEY, so follow-up answers use stored review context only.",
                    "citations": [],
                }
            )
        raise ExternalServiceError(f"No fallback registered for schema {name}")
