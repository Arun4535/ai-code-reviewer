from pydantic import BaseModel, Field


class SeverityBreakdown(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    average_confidence: float


class AgentBreakdown(BaseModel):
    agent: str
    finding_count: int
    average_confidence: float
    top_categories: list[str] = Field(default_factory=list)


class RepositoryReviewMetrics(BaseModel):
    repository: str
    review_count: int
    finding_count: int
    average_risk_score: float
    severity_breakdown: SeverityBreakdown
    category_breakdown: list[CategoryBreakdown]
    agent_breakdown: list[AgentBreakdown]
    highest_risk_reviews: list[int] = Field(default_factory=list)


class ReviewExportFinding(BaseModel):
    title: str
    severity: str
    category: str
    file_path: str
    line_start: int | None = None
    line_end: int | None = None
    confidence: int
    agent: str
    recommended_fix: str


class ReviewExportResponse(BaseModel):
    review_id: int
    repository: str
    pull_request_url: str
    verdict: str
    risk_score: int
    prioritized_actions: list[str]
    findings: list[ReviewExportFinding]
