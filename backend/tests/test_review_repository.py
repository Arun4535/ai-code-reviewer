from app.repositories.review_repository import ReviewRepository
from app.schemas.review import PullRequestContext, ReviewSummary


async def test_create_and_get_review(db_session):
    repo = ReviewRepository(db_session)
    context = PullRequestContext(
        repository_full_name="acme/api",
        pull_request_number=2,
        title="Fix bug",
        author="dev",
        base_branch="main",
        head_branch="bugfix",
        changed_files=[],
    )
    summary = ReviewSummary(
        verdict="Approve with comments",
        risk_score=20,
        executive_summary="Low risk.",
        prioritized_actions=[],
    )

    created = await repo.create_review(context, "https://github.com/acme/api", "https://github.com/acme/api/pull/2", summary, [], [], "test-model")
    loaded = await repo.get_review(created.id)

    assert loaded is not None
    assert loaded.pull_request.repository.full_name == "acme/api"
