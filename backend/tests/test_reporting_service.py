from types import SimpleNamespace

import pytest

from app.services.reporting_service import ReportingService


class FakeReviewRepository:
    def __init__(self, reviews):
        self.reviews = reviews

    async def list_reviews_for_repository(self, repository_full_name: str):
        return self.reviews

    async def get_review(self, review_id: int):
        for review in self.reviews:
            if review.id == review_id:
                return review
        return None


def finding(severity: str, category: str, confidence: int, agent: str):
    return SimpleNamespace(
        title=f"{severity} {category}",
        severity=severity,
        category=category,
        file_path="app/example.py",
        line_start=10,
        line_end=12,
        confidence=confidence,
        agent=agent,
        recommended_fix="Add a focused fix.",
    )


def review(review_id: int, risk_score: int, findings):
    repository = SimpleNamespace(full_name="Arun4535/ai-code-reviewer")
    pull_request = SimpleNamespace(repository=repository, html_url=f"https://github.com/example/repo/pull/{review_id}")
    return SimpleNamespace(
        id=review_id,
        summary_json={
            "verdict": "Changes requested",
            "risk_score": risk_score,
            "prioritized_actions": ["Fix high confidence issues"],
        },
        pull_request=pull_request,
        findings=findings,
    )


@pytest.mark.asyncio
async def test_repository_metrics_groups_findings_by_severity_category_and_agent():
    reviews = [
        review(1, 80, [finding("High", "Security", 90, "security"), finding("Medium", "Performance", 70, "performance")]),
        review(2, 40, [finding("Low", "Maintainability", 60, "maintainability")]),
    ]
    service = ReportingService(FakeReviewRepository(reviews))

    metrics = await service.get_repository_metrics("Arun4535/ai-code-reviewer")

    assert metrics.review_count == 2
    assert metrics.finding_count == 3
    assert metrics.average_risk_score == 60
    assert metrics.severity_breakdown.high == 1
    assert metrics.highest_risk_reviews == [1, 2]


@pytest.mark.asyncio
async def test_export_review_flattens_findings():
    reviews = [review(5, 95, [finding("Critical", "Security", 99, "security")])]
    service = ReportingService(FakeReviewRepository(reviews))

    exported = await service.export_review(5)

    assert exported.review_id == 5
    assert exported.risk_score == 95
    assert exported.findings[0].severity == "Critical"
