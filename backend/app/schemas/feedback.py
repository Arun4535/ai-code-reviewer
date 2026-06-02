from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    review_id: int
    finding_id: int | None = None
    rating: int = Field(ge=-1, le=1)
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackResponse(BaseModel):
    id: int
    review_id: int
    finding_id: int | None
    rating: int
    comment: str | None
