#!/usr/bin/env python3
"""
Regression tests: make_api_request must NOT mutate the caller's params dict.

make_api_request injects credentials (access_token, appsecret_proof) and
JSON-stringifies dict/list values into the outgoing request. Before the fix it
did this on the caller's own dict (request_params = params or {} shares the
reference for non-empty dicts), so any tool that echoes its params back to the
user AFTER the call leaked the access token — real case: update_ad_creative
returns `attempted_updates` in its error_subcode-1815573 response, which came
back carrying `access_token` plus json.dumps-stringified specs.
"""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from meta_ads_mcp.core.api import make_api_request


def _mock_response():
    """A minimal successful httpx response."""
    response = MagicMock()
    response.status_code = 200
    response.headers = {}
    response.json.return_value = {"success": True}
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_httpx_client():
    """Patch httpx.AsyncClient so no network I/O happens."""
    with patch("meta_ads_mcp.core.api.httpx.AsyncClient") as mock_client_cls:
        client = MagicMock()
        client.get = AsyncMock(return_value=_mock_response())
        client.post = AsyncMock(return_value=_mock_response())
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        yield client


@pytest.mark.asyncio
async def test_post_does_not_mutate_caller_params(mock_httpx_client):
    """POST path: credentials and json.dumps'd values must stay out of the caller's dict."""
    caller_params = {
        "name": "My creative",
        "object_story_spec": {"link_data": {"message": "New text"}},
        "headlines": [{"text": "H1"}],
    }
    snapshot = {
        "name": "My creative",
        "object_story_spec": {"link_data": {"message": "New text"}},
        "headlines": [{"text": "H1"}],
    }

    await make_api_request("123/endpoint", "SECRET_TOKEN", caller_params, method="POST")

    assert caller_params == snapshot, (
        "make_api_request mutated the caller's params dict — tools that echo "
        "their params back (e.g. update_ad_creative attempted_updates) would "
        "leak the access token and stringified specs"
    )
    assert "access_token" not in caller_params
    assert "appsecret_proof" not in caller_params
    assert isinstance(caller_params["object_story_spec"], dict)


@pytest.mark.asyncio
async def test_post_still_sends_credentials_and_stringified_values(mock_httpx_client):
    """The outgoing request keeps the old wire format (token + JSON strings)."""
    caller_params = {"object_story_spec": {"link_data": {"message": "x"}}}

    await make_api_request("123/endpoint", "SECRET_TOKEN", caller_params, method="POST")

    sent = mock_httpx_client.post.call_args.kwargs["data"]
    assert sent["access_token"] == "SECRET_TOKEN"
    assert isinstance(sent["object_story_spec"], str)


@pytest.mark.asyncio
async def test_get_does_not_mutate_caller_params(mock_httpx_client):
    """GET path: same guarantee for query-style calls."""
    caller_params = {"fields": "id,name", "targeting_spec": {"geo_locations": {"countries": ["US"]}}}
    snapshot = {"fields": "id,name", "targeting_spec": {"geo_locations": {"countries": ["US"]}}}

    await make_api_request("123/endpoint", "SECRET_TOKEN", caller_params, method="GET")

    assert caller_params == snapshot
    assert "access_token" not in caller_params
