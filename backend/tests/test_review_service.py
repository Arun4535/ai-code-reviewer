import pytest

from app.llm.groq import GroqChatModel
from app.schemas.review import ChangedFile, PullRequestContext, ReviewCreateRequest
from app.services.review_service import ReviewService


@pytest.mark.asyncio
async def test_review_service_runs_small_pr_number_3(monkeypatch, db_session):
    payload = ReviewCreateRequest(
        repository_url="https://github.com/acme/api",
        pull_request_url="https://github.com/acme/api/pull/3",
    )

    context = PullRequestContext(
        repository_full_name="acme/api",
        pull_request_number=3,
        title="Fix typo in README",
        author="dev",
        base_branch="main",
        head_branch="fix/readme-typo",
        changed_files=[
            ChangedFile(
                filename="README.md",
                status="modified",
                patch="@@ -1,2 +1,2 @@\n-Hello wrld\n+Hello world\n",
            )
        ],
    )

    monkeypatch.setattr(
        "app.services.review_service.get_chat_model",
        lambda: GroqChatModel(api_key=None),
    )

    service = ReviewService(db_session)

    async def fake_fetch_pull_request(pull_request_url: str):
        return context

    service.github.fetch_pull_request = fake_fetch_pull_request

    response = await service.review_pull_request(payload)

    assert response.id > 0
    assert response.pull_request_url.endswith("/pull/3")
    assert response.summary.verdict
    assert response.summary.risk_score >= 0
    assert response.agent_outputs
