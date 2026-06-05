import pytest

from app.services.github_service import GitHubService


def test_parse_pull_request_url():
    owner, repo, number = GitHubService().parse_pull_request_url("https://github.com/acme/api/pull/42")
    assert owner == "acme"
    assert repo == "api"
    assert number == 42


def test_repository_validation_rejects_mismatch():
    service = GitHubService()
    with pytest.raises(ValueError):
        service.validate_same_repository("https://github.com/acme/web", "https://github.com/acme/api/pull/42")


class DummyResponse:
    def __init__(self, status_code, json_data, headers=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self._headers = headers or {}
        self.text = text

    def json(self):
        return self._json_data

    @property
    def headers(self):
        return self._headers


class DummyClient:
    def __init__(self, responses):
        self._responses = responses
        self.requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None):
        self.requests.append((url, params))
        return self._responses.pop(0)


@pytest.mark.asyncio
async def test_fetch_pull_request_files_paginated(monkeypatch):
    pr_response = DummyResponse(
        200,
        {
            "title": "Add feature",
            "user": {"login": "alice"},
            "base": {"ref": "main"},
            "head": {"ref": "feature-branch"},
        },
    )
    first_page = DummyResponse(
        200,
        [{"filename": "file1.py", "status": "modified", "patch": "diff1"}] * 100,
        headers={"link": '<https://api.github.com/repos/acme/api/pulls/42/files?page=2&per_page=100>; rel="next"'},
    )
    second_page = DummyResponse(
        200,
        [{"filename": "file101.py", "status": "modified", "patch": "diff101"}],
    )

    dummy_client = DummyClient([pr_response, first_page, second_page])

    monkeypatch.setattr("app.services.github_service.httpx.AsyncClient", lambda *args, **kwargs: dummy_client)

    service = GitHubService()
    context = await service.fetch_pull_request("https://github.com/acme/api/pull/42")

    assert len(context.changed_files) == 101
    assert context.changed_files[0].filename == "file1.py"
    assert context.changed_files[-1].filename == "[review payload truncated]"
    assert dummy_client.requests[1][1]["page"] == 1
    assert dummy_client.requests[2][1]["page"] == 2
