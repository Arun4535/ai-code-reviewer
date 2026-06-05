import asyncio
import logging
import time
from collections import Counter

from app.agents.chunking import ReviewChunk, build_review_chunks
from app.agents.prompts import load_prompt
from app.core.config import settings
from app.llm.base import ChatModel
from app.schemas.review import AgentResult, PullRequestContext, ReviewFinding, ReviewSummary


SEVERITY_RANK = {
    "Critical": 0,
    "High": 1,
    "Medium": 2,
    "Low": 3,
}


class ReviewWorkflow:
    def __init__(self, model: ChatModel):
        self.model = model
        self.logger = logging.getLogger(__name__)

    async def run(self, context: PullRequestContext) -> tuple[ReviewSummary, list[ReviewFinding], list[AgentResult]]:
        start_time = time.perf_counter()
        chunks = build_review_chunks(
            context.changed_files,
            settings.max_changed_files_per_review,
            settings.max_lines_per_chunk,
            settings.max_chunk_patch_chars,
        )
        self.logger.info(
            "Review workflow using unified chunk review",
            extra={
                "file_count": len(context.changed_files),
                "chunk_count": len(chunks),
                "max_concurrent_reviews": settings.max_concurrent_chunk_reviews,
            },
        )
        results = await self._review_chunks(chunks, context)
        findings = self._aggregate_findings([output.findings for output in results])
        summary = self._build_summary(context, len(chunks), findings)
        self.logger.info(
            "Review workflow completed",
            extra={
                "duration_seconds": time.perf_counter() - start_time,
                "llm_calls": len(results),
                "estimated_tokens": sum(len(chunk.patch) // 4 for chunk in chunks),
                "finding_count": len(findings),
            },
        )
        return summary, findings, results

    async def _review_chunks(self, chunks: list[ReviewChunk], context: PullRequestContext) -> list[AgentResult]:
        semaphore = asyncio.Semaphore(settings.max_concurrent_chunk_reviews)

        async def run_chunk(chunk: ReviewChunk) -> AgentResult:
            async with semaphore:
                return await self._review_chunk(chunk, context)

        return await asyncio.gather(*(run_chunk(chunk) for chunk in chunks))

    async def _review_chunk(self, chunk: ReviewChunk, context: PullRequestContext) -> AgentResult:
        payload = {
            "pr_metadata": {
                "repository_full_name": context.repository_full_name,
                "pull_request_number": context.pull_request_number,
                "title": context.title,
                "author": context.author,
                "base_branch": context.base_branch,
                "head_branch": context.head_branch,
            },
            "chunk": {
                "filename": chunk.filename,
                "chunk_index": chunk.chunk_index,
                "patch": chunk.patch,
            },
        }
        result = await self.model.structured(
            system_prompt=load_prompt("unified_review"),
            user_payload=payload,
            schema=AgentResult,
        )
        if not result.agent:
            result.agent = "Unified Reviewer"
        return result

    def _aggregate_findings(self, findings_by_chunk: list[list[ReviewFinding]]) -> list[ReviewFinding]:
        merged: dict[tuple, ReviewFinding] = {}
        for findings in findings_by_chunk:
            for finding in findings:
                key = (
                    finding.file_path,
                    finding.line_start,
                    finding.line_end,
                    finding.category,
                    finding.severity,
                    finding.title.strip(),
                )
                existing = merged.get(key)
                if existing is None or finding.confidence > existing.confidence:
                    merged[key] = finding
        aggregated = list(merged.values())
        aggregated.sort(key=lambda item: (SEVERITY_RANK.get(item.severity, 4), item.file_path, item.line_start or 0))
        return aggregated

    def _build_summary(self, context: PullRequestContext, chunk_count: int, findings: list[ReviewFinding]) -> ReviewSummary:
        severity_counts = Counter(f.severity for f in findings)
        category_counts = Counter(f.category for f in findings)
        risk_score = min(
            100,
            severity_counts["Critical"] * 20
            + severity_counts["High"] * 10
            + severity_counts["Medium"] * 5
            + severity_counts["Low"] * 2,
        )
        if severity_counts["Critical"] or severity_counts["High"]:
            verdict = "Action required"
        elif findings:
            verdict = "Review recommended"
        else:
            verdict = "Low risk"

        executive_summary = (
            f"Reviewed {chunk_count} changed code chunk(s) from {len(context.changed_files)} changed file(s). "
            f"Found {len(findings)} issue(s) across {len(category_counts)} categories."
        )
        prioritized_actions = [
            f"{finding.category}: {finding.title} in {finding.file_path}" for finding in findings[:3]
        ]
        if not prioritized_actions:
            prioritized_actions = ["No significant issues detected in changed code chunks."]

        return ReviewSummary(
            verdict=verdict,
            risk_score=risk_score,
            executive_summary=executive_summary,
            prioritized_actions=prioritized_actions,
        )
