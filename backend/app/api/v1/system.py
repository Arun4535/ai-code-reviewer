from fastapi import APIRouter

from app.core.config import settings
from app.schemas.system import SystemSettingsResponse

router = APIRouter()


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_settings() -> SystemSettingsResponse:
    provider = settings.llm_provider.lower().strip()
    default_model = settings.anthropic_model if provider in {"anthropic", "claude"} else settings.groq_model

    return SystemSettingsResponse(
        llm_provider=provider,
        default_model=default_model,
        vector_store="ChromaDB-ready",
        database="PostgreSQL",
    )
