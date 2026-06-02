from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.review_service import ReviewService


DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_review_service(db: DbSession) -> ReviewService:
    return ReviewService(db)
