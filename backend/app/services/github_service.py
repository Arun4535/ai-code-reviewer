import re
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError
from app.schemas.review import ChangedFile, PullRequestContext


PR_RE = re.compile(r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)")


class GitHubService:
    def parse_pull_request_url(self, pull_request_url: str) -> tuple[str, str, int]:
        match = PR_RE.search(pull_request_url)
        if not match:
            raise ValueError("Expected a GitHub pull request URL like https://github.com/owner/repo/pull/123")
        return match.group("owner"), match.group("repo"), int(match.group("number"))

    async def fetch_pull_request(self, pull_request_url: str) -> PullRequestContext:
        owner, repo, number = self.parse_pull_request_url(pull_request_url)
        headers = {"Accept": "application/vnd.github+json"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        async with httpx.AsyncClient(base_url="https://api.github.com", headers=headers, timeout=30) as client:
            pr_resp = await client.get(f"/repos/{owner}/{repo}/pulls/{number}")
            files = await self._fetch_pull_request_files(client, owner, repo, number)
        if pr_resp.status_code >= 400:
            raise ExternalServiceError(f"GitHub PR fetch failed: {pr_resp.status_code} {pr_resp.text[:300]}")
        pr = pr_resp.json()
        changed_files = self._prepare_changed_files(files)
        return PullRequestContext(
            repository_full_name=f"{owner}/{repo}",
            pull_request_number=number,
            title=pr["title"],
            author=pr["user"]["login"],
            base_branch=pr["base"]["ref"],
            head_branch=pr["head"]["ref"],
            changed_files=changed_files,
        )

    async def _fetch_pull_request_files(self, client: httpx.AsyncClient, owner: str, repo: str, number: int) -> list[dict]:
        files: list[dict] = []
        page = 1
        while True:
            response = await client.get(
                f"/repos/{owner}/{repo}/pulls/{number}/files",
                params={"per_page": 100, "page": page},
            )
            if response.status_code >= 400:
                raise ExternalServiceError(f"GitHub file fetch failed: {response.status_code} {response.text[:300]}")
            page_files = response.json()
            if not page_files:
                break
            files.extend(page_files)
            if not self._has_next_link(response) or len(page_files) < 100:
                break
            page += 1
        return files

    def _has_next_link(self, response: httpx.Response) -> bool:
        link_header = response.headers.get("link", "")
        return 'rel="next"' in link_header

    def validate_same_repository(self, repository_url: str, pull_request_url: str) -> None:
        repo_path = urlparse(repository_url).path.strip("/").removesuffix(".git")
        owner, repo, _ = self.parse_pull_request_url(pull_request_url)
        if repo_path.lower() != f"{owner}/{repo}".lower():
            raise ValueError("Repository URL and pull request URL point to different repositories.")

    def _prepare_changed_files(self, files: list[dict]) -> list[ChangedFile]:
        prepared: list[ChangedFile] = []
        total_patch_chars = 0
        omitted = max(0, len(files) - settings.max_changed_files_per_review)

        for item in files[: settings.max_changed_files_per_review]:
            patch = item.get("patch")
            if patch:
                patch = self._truncate_patch(patch, settings.max_patch_chars_per_file, "file patch")
                remaining_budget = settings.max_total_patch_chars - total_patch_chars
                if remaining_budget <= 0:
                    patch = "[Diff omitted: total review diff budget exceeded.]"
                else:
                    patch = self._truncate_patch(patch, remaining_budget, "total review payload")
                    total_patch_chars += len(patch)
            prepared.append(
                ChangedFile(
                    filename=item["filename"],
                    status=item["status"],
                    additions=item.get("additions", 0),
                    deletions=item.get("deletions", 0),
                    patch=patch,
                )
            )

        if omitted:
            prepared.append(
                ChangedFile(
                    filename="[review payload truncated]",
                    status="omitted",
                    additions=0,
                    deletions=0,
                    patch=(
                        f"{omitted} changed file(s) were omitted because "
                        f"MAX_CHANGED_FILES_PER_REVIEW is {settings.max_changed_files_per_review}."
                    ),
                )
            )
        return prepared

    def _truncate_patch(self, patch: str, max_chars: int, label: str) -> str:
        if len(patch) <= max_chars:
            return patch
        return (
            patch[:max_chars]
            + f"\n\n[Diff truncated: {label} exceeded {max_chars} characters. Review may need a focused rerun.]"
        )
