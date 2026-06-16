from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import Evaluation, Feedback, PullRequest, Repository, Review, ReviewFinding
from app.schemas.feedback import FeedbackCreate
from app.schemas.review import PullRequestContext, ReviewFinding as FindingSchema, ReviewSummary


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review(
        self,
        context: PullRequestContext,
        repository_url: str,
        pull_request_url: str,
        summary: ReviewSummary,
        findings: list[FindingSchema],
        agent_outputs: list[dict],
        model: str,
    ) -> Review:
        repository = await self._get_or_create_repository(context.repository_full_name, repository_url)
        pull_request = await self._get_or_create_pull_request(context, repository.id, pull_request_url)
        review = Review(
            pull_request_id=pull_request.id,
            summary_json=summary.model_dump(mode="json"),
            agent_outputs_json=agent_outputs,
            model=model,
        )
        self.db.add(review)
        await self.db.flush()
        for finding in findings:
            self.db.add(
                ReviewFinding(
                    review_id=review.id,
                    file_path=finding.file_path,
                    line_start=finding.line_start,
                    line_end=finding.line_end,
                    category=finding.category.value,
                    severity=finding.severity.value,
                    confidence=finding.confidence,
                    title=finding.title,
                    explanation=finding.explanation,
                    recommended_fix=finding.recommended_fix,
                    agent=finding.agent,
                )
            )
        await self.db.commit()
        return await self.get_review(review.id)

    async def get_review(self, review_id: int) -> Review | None:
        result = await self.db.execute(
            select(Review)
            .options(selectinload(Review.findings), selectinload(Review.pull_request).selectinload(PullRequest.repository))
            .where(Review.id == review_id)
        )
        return result.scalar_one_or_none()

    async def list_reviews_for_repository(self, repository_full_name: str) -> list[Review]:
        result = await self.db.execute(
            select(Review)
            .join(Review.pull_request)
            .join(PullRequest.repository)
            .options(selectinload(Review.findings), selectinload(Review.pull_request).selectinload(PullRequest.repository))
            .where(Repository.full_name == repository_full_name)
            .order_by(Review.created_at.desc())
        )
        return list(result.scalars().all())

    async def save_feedback(self, payload: FeedbackCreate) -> Feedback:
        feedback = Feedback(**payload.model_dump())
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def save_evaluation(self, review_id: int | None, prompt_name: str, model: str, input_json: dict, output_json: dict) -> None:
        self.db.add(
            Evaluation(
                review_id=review_id,
                prompt_name=prompt_name,
                model=model,
                input_json=input_json,
                output_json=output_json,
            )
        )
        await self.db.commit()

    async def _get_or_create_repository(self, full_name: str, html_url: str) -> Repository:
        result = await self.db.execute(select(Repository).where(Repository.full_name == full_name))
        repository = result.scalar_one_or_none()
        if repository:
            return repository
        repository = Repository(full_name=full_name, html_url=html_url)
        self.db.add(repository)
        await self.db.flush()
        return repository

    async def _get_or_create_pull_request(self, context: PullRequestContext, repository_id: int, html_url: str) -> PullRequest:
        result = await self.db.execute(
            select(PullRequest).where(PullRequest.repository_id == repository_id, PullRequest.number == context.pull_request_number)
        )
        pull_request = result.scalar_one_or_none()
        if pull_request:
            return pull_request
        pull_request = PullRequest(
            repository_id=repository_id,
            number=context.pull_request_number,
            title=context.title,
            author=context.author,
            base_branch=context.base_branch,
            head_branch=context.head_branch,
            html_url=html_url,
            metadata_json=context.model_dump(mode="json"),
        )
        self.db.add(pull_request)
        await self.db.flush()
        return pull_request
