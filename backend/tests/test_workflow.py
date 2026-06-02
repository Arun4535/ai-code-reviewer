from app.agents.workflow import ReviewWorkflow
from app.llm.groq import GroqChatModel
from app.schemas.review import ChangedFile, PullRequestContext


async def test_workflow_runs_without_groq_key():
    context = PullRequestContext(
        repository_full_name="acme/api",
        pull_request_number=1,
        title="Add endpoint",
        author="dev",
        base_branch="main",
        head_branch="feature",
        changed_files=[ChangedFile(filename="app.py", status="modified", patch="+print('hello')")],
    )

    summary, findings, outputs = await ReviewWorkflow(GroqChatModel(api_key=None)).run(context)

    assert summary.risk_score >= 0
    assert findings == []
    assert len(outputs) == 4
