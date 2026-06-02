from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_review_service
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.review_service import ReviewService

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    payload: FeedbackCreate,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> FeedbackResponse:
    return await service.save_feedback(payload)
