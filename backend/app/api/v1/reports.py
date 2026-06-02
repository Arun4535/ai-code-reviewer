from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.review_repository import ReviewRepository
from app.schemas.metrics import RepositoryReviewMetrics, ReviewExportResponse
from app.services.reporting_service import ReportingService

router = APIRouter()


def get_reporting_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ReportingService:
    return ReportingService(ReviewRepository(db))


@router.get("/repositories/metrics", response_model=RepositoryReviewMetrics)
async def get_repository_metrics(
    repository: str = Query(..., min_length=3),
    service: Annotated[ReportingService, Depends(get_reporting_service)] = None,
) -> RepositoryReviewMetrics:
    return await service.get_repository_metrics(repository)


@router.get("/reviews/{review_id}/export", response_model=ReviewExportResponse)
async def export_review(
    review_id: int,
    service: Annotated[ReportingService, Depends(get_reporting_service)] = None,
) -> ReviewExportResponse:
    try:
        return await service.export_review(review_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
