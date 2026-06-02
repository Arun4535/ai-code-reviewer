from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class Severity(str, Enum):
    critical = "Critical"
    high = "High"
    medium = "Medium"
    low = "Low"


class Category(str, Enum):
    bug_risk = "Bug Risk"
    security = "Security"
    performance = "Performance"
    maintainability = "Maintainability"
    readability = "Readability"
    testing = "Testing Coverage"
    architecture = "Architecture Concerns"


class ReviewFinding(BaseModel):
    file_path: str
    line_start: int | None = None
    line_end: int | None = None
    category: Category
    severity: Severity
    confidence: int = Field(ge=0, le=100)
    title: str
    explanation: str
    recommended_fix: str
    agent: str


class AgentResult(BaseModel):
    agent: str
    intent: str | None = None
    findings: list[ReviewFinding] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ReviewSummary(BaseModel):
    verdict: str
    risk_score: int = Field(ge=0, le=100)
    executive_summary: str
    prioritized_actions: list[str] = Field(default_factory=list)


class ReviewCreateRequest(BaseModel):
    repository_url: HttpUrl
    pull_request_url: HttpUrl


class ChangedFile(BaseModel):
    filename: str
    status: str
    additions: int = 0
    deletions: int = 0
    patch: str | None = None


class PullRequestContext(BaseModel):
    repository_full_name: str
    pull_request_number: int
    title: str
    author: str
    base_branch: str
    head_branch: str
    changed_files: list[ChangedFile]


class ReviewResponse(BaseModel):
    id: int
    repository_url: str
    pull_request_url: str
    summary: ReviewSummary
    findings: list[ReviewFinding]
    agent_outputs: list[AgentResult]


class FollowUpRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class FollowUpResponse(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)
