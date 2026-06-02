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
