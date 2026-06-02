from app.core.config import settings
from app.llm.anthropic import AnthropicChatModel
from app.llm.base import ChatModel
from app.llm.groq import GroqChatModel


def get_chat_model() -> ChatModel:
    provider = settings.llm_provider.lower().strip()
    if provider in {"anthropic", "claude"}:
        return AnthropicChatModel()
    return GroqChatModel()
