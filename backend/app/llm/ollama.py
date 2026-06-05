import json
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.errors import ExternalServiceError

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class OllamaChatModel:
    preferred_models = ("llama3.2:latest", "llama3.1:8b", "qwen2.5:1.5b", "deepseek-r1:1.5b")

    def __init__(self, base_url: str | None = None, model_name: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model_name = model_name or settings.ollama_model
        self._cached_model_name: str | None = None
        self._client = httpx.AsyncClient(timeout=settings.llm_timeout_seconds)

    async def structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: type[SchemaT],
    ) -> SchemaT:
        try:
            client = self._client
            model_name = await self._available_model_name(client)
            body = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                ],
                "format": schema.model_json_schema(),
                "stream": False,
                "options": {"temperature": 0.1},
            }
            resp = await client.post(f"{self.base_url}/api/chat", json=body)
        except httpx.HTTPError as exc:
            raise ExternalServiceError(
                f"Ollama request failed. Make sure Ollama is running at {self.base_url} "
                "and at least one local model is installed."
            ) from exc
        if resp.status_code >= 400:
            raise ExternalServiceError(f"Ollama request failed: {resp.status_code} {resp.text[:500]}")
        content = resp.json().get("message", {}).get("content", "")
        try:
            return schema.model_validate_json(content)
        except ValueError as exc:
            raise ExternalServiceError(f"Ollama returned invalid JSON for {schema.__name__}: {content[:500]}") from exc

    async def _available_model_name(self, client: httpx.AsyncClient) -> str:
        if self._cached_model_name:
            return self._cached_model_name

        resp = await client.get(f"{self.base_url}/api/tags")
        if resp.status_code >= 400:
            raise ExternalServiceError(f"Ollama model lookup failed: {resp.status_code} {resp.text[:500]}")

        models = resp.json().get("models", [])
        local_model_names = [
            model["name"]
            for model in models
            if model.get("name") and not model.get("remote_model") and not model.get("remote_host")
        ]
        if self.model_name in local_model_names:
            self._cached_model_name = self.model_name
            return self.model_name
        for model_name in self.preferred_models:
            if model_name in local_model_names:
                self._cached_model_name = model_name
                return model_name
        if local_model_names:
            self._cached_model_name = local_model_names[0]
            return local_model_names[0]
        raise ExternalServiceError("Ollama is running, but no local models are installed.")
