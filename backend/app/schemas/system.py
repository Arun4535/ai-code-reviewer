from pydantic import BaseModel


class SystemSettingsResponse(BaseModel):
    llm_provider: str
    default_model: str
    vector_store: str
    database: str
