from collections import Counter, defaultdict
from statistics import mean

from app.models.entities import Review
from app.repositories.review_repository import ReviewRepository
from app.schemas.metrics import (
    AgentBreakdown,
    CategoryBreakdown,
    RepositoryReviewMetrics,
    ReviewExportFinding,
    ReviewExportResponse,
    SeverityBreakdown,
)


class ReportingService:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    async def get_repository_metrics(self, repository_full_name: str) -> RepositoryReviewMetrics:
        reviews = await self.repository.list_reviews_for_repository(repository_full_name)
        severity_counter: Counter[str] = Counter()
        category_confidence: dict[str, list[int]] = defaultdict(list)
        agent_confidence: dict[str, list[int]] = defaultdict(list)
        agent_categories: dict[str, Counter[str]] = defaultdict(Counter)
        risk_scores: list[int] = []

        for review in reviews:
            risk_scores.append(int(review.summary_json.get("risk_score", 0)))
            for finding in review.findings:
                severity_counter[finding.severity.lower()] += 1
                category_confidence[finding.category].append(finding.confidence)
                agent_confidence[finding.agent].append(finding.confidence)
                agent_categories[finding.agent][finding.category] += 1

        highest_risk_reviews = [
            review.id
            for review in sorted(
                reviews,
                key=lambda item: int(item.summary_json.get("risk_score", 0)),
                reverse=True,
            )[:5]
        ]

        return RepositoryReviewMetrics(
            repository=repository_full_name,
            review_count=len(reviews),
            finding_count=sum(len(review.findings) for review in reviews),
            average_risk_score=round(mean(risk_scores), 2) if risk_scores else 0,
            severity_breakdown=SeverityBreakdown(
                critical=severity_counter["critical"],
                high=severity_counter["high"],
                medium=severity_counter["medium"],
                low=severity_counter["low"],
            ),
            category_breakdown=[
                CategoryBreakdown(
                    category=category,
                    count=len(confidences),
                    average_confidence=round(mean(confidences), 2),
                )
                for category, confidences in sorted(category_confidence.items())
            ],
            agent_breakdown=[
                AgentBreakdown(
                    agent=agent,
                    finding_count=len(confidences),
                    average_confidence=round(mean(confidences), 2),
                    top_categories=[name for name, _count in agent_categories[agent].most_common(3)],
                )
                for agent, confidences in sorted(agent_confidence.items())
            ],
            highest_risk_reviews=highest_risk_reviews,
        )

    async def export_review(self, review_id: int) -> ReviewExportResponse:
        review = await self.repository.get_review(review_id)
        if review is None:
            raise ValueError(f"Review {review_id} does not exist")
        return self._build_export(review)

    def _build_export(self, review: Review) -> ReviewExportResponse:
        summary = review.summary_json
        pull_request = review.pull_request
        return ReviewExportResponse(
            review_id=review.id,
            repository=pull_request.repository.full_name,
            pull_request_url=pull_request.html_url,
            verdict=summary.get("verdict", "Unknown"),
            risk_score=int(summary.get("risk_score", 0)),
            prioritized_actions=list(summary.get("prioritized_actions", [])),
            findings=[
                ReviewExportFinding(
                    title=finding.title,
                    severity=finding.severity,
                    category=finding.category,
                    file_path=finding.file_path,
                    line_start=finding.line_start,
                    line_end=finding.line_end,
                    confidence=finding.confidence,
                    agent=finding.agent,
                    recommended_fix=finding.recommended_fix,
                )
                for finding in review.findings
            ],
        )
