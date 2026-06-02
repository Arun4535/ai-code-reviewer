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
            files_resp = await client.get(f"/repos/{owner}/{repo}/pulls/{number}/files", params={"per_page": 100})
        if pr_resp.status_code >= 400:
            raise ExternalServiceError(f"GitHub PR fetch failed: {pr_resp.status_code} {pr_resp.text[:300]}")
        if files_resp.status_code >= 400:
            raise ExternalServiceError(f"GitHub file fetch failed: {files_resp.status_code} {files_resp.text[:300]}")
        pr = pr_resp.json()
        files = files_resp.json()
        return PullRequestContext(
            repository_full_name=f"{owner}/{repo}",
            pull_request_number=number,
            title=pr["title"],
            author=pr["user"]["login"],
            base_branch=pr["base"]["ref"],
            head_branch=pr["head"]["ref"],
            changed_files=[
                ChangedFile(
                    filename=item["filename"],
                    status=item["status"],
                    additions=item.get("additions", 0),
                    deletions=item.get("deletions", 0),
                    patch=item.get("patch"),
                )
                for item in files
            ],
        )

    def validate_same_repository(self, repository_url: str, pull_request_url: str) -> None:
        repo_path = urlparse(repository_url).path.strip("/").removesuffix(".git")
        owner, repo, _ = self.parse_pull_request_url(pull_request_url)
        if repo_path.lower() != f"{owner}/{repo}".lower():
            raise ValueError("Repository URL and pull request URL point to different repositories.")
