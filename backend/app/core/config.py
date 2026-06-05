from functools import lru_cache
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: PostgresDsn | str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_reviewer"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    llm_provider: str = "ollama"
    allow_paid_llm: bool = False
    llm_timeout_seconds: float = 600
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5"
    max_changed_files_per_review: int = 100
    max_lines_per_chunk: int = 300
    max_chunk_patch_chars: int = 15000
    max_concurrent_chunk_reviews: int = 5
    max_patch_chars_per_file: int = 12000
    max_total_patch_chars: int = 60000
    github_token: str | None = None
    cors_origins_raw: str = Field(
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
        alias="CORS_ORIGINS",
    )
    rate_limit_per_minute: int = 30
    chroma_path: str = "./.chroma"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
