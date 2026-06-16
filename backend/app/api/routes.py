from fastapi import APIRouter

from app.api.v1 import feedback, reports, reviews, system

api_router = APIRouter()
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
