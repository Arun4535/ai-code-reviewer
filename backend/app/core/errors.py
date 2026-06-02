from fastapi import HTTPException, status


class ExternalServiceError(RuntimeError):
    """Raised when GitHub, Groq, or another external provider fails."""


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
