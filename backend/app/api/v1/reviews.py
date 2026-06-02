from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_review_service
from app.schemas.review import (
    FollowUpRequest,
    FollowUpResponse,
    ReviewCreateRequest,
    ReviewResponse,
)
from app.services.review_service import ReviewService

router = APIRouter()


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    payload: ReviewCreateRequest,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewResponse:
    return await service.review_pull_request(payload)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewResponse:
    return await service.get_review(review_id)


@router.post("/{review_id}/ask", response_model=FollowUpResponse)
async def ask_follow_up(
    review_id: int,
    payload: FollowUpRequest,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> FollowUpResponse:
    return await service.answer_follow_up(review_id, payload.question)
