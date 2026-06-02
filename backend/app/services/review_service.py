from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.workflow import ReviewWorkflow
from app.core.config import settings
from app.core.errors import ExternalServiceError, not_found
from app.llm.factory import get_chat_model
from app.repositories.review_repository import ReviewRepository
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.schemas.review import FollowUpResponse, ReviewCreateRequest, ReviewFinding, ReviewResponse, ReviewSummary
from app.services.github_service import GitHubService
from app.services.rag_service import ReviewKnowledgeBase


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReviewRepository(db)
        self.github = GitHubService()
        self.model = get_chat_model()
        self.workflow = ReviewWorkflow(self.model)
        self.knowledge_base = ReviewKnowledgeBase()

    async def review_pull_request(self, payload: ReviewCreateRequest) -> ReviewResponse:
        try:
            self.github.validate_same_repository(str(payload.repository_url), str(payload.pull_request_url))
            context = await self.github.fetch_pull_request(str(payload.pull_request_url))
            standards = self.knowledge_base.retrieve(" ".join(file.filename for file in context.changed_files))
            summary, findings, agent_outputs = await self.workflow.run(context)
            if standards and agent_outputs:
                agent_outputs[0].notes.extend([f"Grounding: {item.source}: {item.text}" for item in standards])
            review = await self.repository.create_review(
                context=context,
                repository_url=str(payload.repository_url),
                pull_request_url=str(payload.pull_request_url),
                summary=summary,
                findings=findings,
                agent_outputs=[a.model_dump(mode="json") for a in agent_outputs],
                model=self.model.model_name,
            )
            await self.repository.save_evaluation(
                review_id=review.id,
                prompt_name="langgraph_review_workflow",
                model=self.model.model_name,
                input_json=context.model_dump(mode="json"),
                output_json={"summary": summary.model_dump(mode="json"), "findings": [f.model_dump(mode="json") for f in findings]},
            )
            return self._to_response(review)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ExternalServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    async def get_review(self, review_id: int) -> ReviewResponse:
        review = await self.repository.get_review(review_id)
        if not review:
            raise not_found("Review not found")
        return self._to_response(review)

    async def answer_follow_up(self, review_id: int, question: str) -> FollowUpResponse:
        review = await self.repository.get_review(review_id)
        if not review:
            raise not_found("Review not found")
        findings = [self._finding_schema(f).model_dump(mode="json") for f in review.findings]
        return await self.model.structured(
            system_prompt=(
                "Answer questions about this pull request review using only the supplied context. "
                "Be concise, practical, and cite file paths or finding titles when relevant."
            ),
            user_payload={"question": question, "summary": review.summary_json, "findings": findings},
            schema=FollowUpResponse,
        )

    async def save_feedback(self, payload: FeedbackCreate) -> FeedbackResponse:
        feedback = await self.repository.save_feedback(payload)
        return FeedbackResponse(
            id=feedback.id,
            review_id=feedback.review_id,
            finding_id=feedback.finding_id,
            rating=feedback.rating,
            comment=feedback.comment,
        )

    def _to_response(self, review) -> ReviewResponse:
        pull_request = review.pull_request
        repository = pull_request.repository
        return ReviewResponse(
            id=review.id,
            repository_url=repository.html_url,
            pull_request_url=pull_request.html_url,
            summary=ReviewSummary.model_validate(review.summary_json),
            findings=[self._finding_schema(f) for f in review.findings],
            agent_outputs=review.agent_outputs_json,
        )

    def _finding_schema(self, finding) -> ReviewFinding:
        return ReviewFinding(
            file_path=finding.file_path,
            line_start=finding.line_start,
            line_end=finding.line_end,
            category=finding.category,
            severity=finding.severity,
            confidence=finding.confidence,
            title=finding.title,
            explanation=finding.explanation,
            recommended_fix=finding.recommended_fix,
            agent=finding.agent,
        )
