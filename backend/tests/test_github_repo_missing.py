"""github_repo_is_missing is True only for a real 404; every other outcome is "unknown" so students are never blocked by us."""
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.github_repo_service import github_repo_is_missing

URL = "https://github.com/acme/repo"


def _client(response=None, error=None):
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client


@pytest.mark.parametrize("status,expected", [(404, True), (200, False), (403, False), (500, False)])
async def test_only_a_404_means_missing(status, expected):
    with patch("app.services.github_repo_service._gh_get", new=AsyncMock(return_value=MagicMock(status_code=status))), \
            patch("app.services.github_repo_service.httpx.AsyncClient", return_value=_client()):
        assert await github_repo_is_missing(URL) is expected


async def test_network_trouble_is_not_missing():
    with patch("app.services.github_repo_service._gh_get", new=AsyncMock(side_effect=httpx.ConnectTimeout("t"))), \
            patch("app.services.github_repo_service.httpx.AsyncClient", return_value=_client()):
        assert await github_repo_is_missing(URL) is False


async def test_a_non_github_url_is_not_judged():
    assert await github_repo_is_missing("https://example.com/x") is False
