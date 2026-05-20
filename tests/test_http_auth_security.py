"""Regression tests for GHSA-9gw6-46qc-99vr.

Covers two fixes:
1. AuthInjectionMiddleware rejects unauthenticated HTTP requests with 401
   instead of falling through to tool handlers that would use the
   META_ACCESS_TOKEN env var.
2. make_api_request() scrubs access_token/appsecret_proof from URLs returned
   in error payloads.
"""

import asyncio
import json
from unittest.mock import patch, AsyncMock, MagicMock

import httpx
import pytest
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from meta_ads_mcp.core.api import _redact_url, make_api_request
from meta_ads_mcp.core.http_auth_integration import AuthInjectionMiddleware


def _build_app():
    async def downstream(request):
        # If middleware ever lets the request through unauthenticated, this
        # endpoint would be reached and return a token-shaped body.
        return JSONResponse({"reached_handler": True})

    app = Starlette(routes=[Route("/mcp", downstream, methods=["POST", "GET"])])
    app.add_middleware(AuthInjectionMiddleware)
    return app


def test_middleware_rejects_unauthenticated_request():
    client = TestClient(_build_app())
    resp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "tools/call", "id": 1,
              "params": {"name": "get_ad_accounts", "arguments": {}}},
        headers={"Accept": "application/json, text/event-stream"},
    )
    assert resp.status_code == 401
    assert resp.headers.get("WWW-Authenticate") == "Bearer"
    body = resp.json()
    assert body["error"] == "Unauthorized"
    assert "reached_handler" not in resp.text


def test_middleware_accepts_bearer_token():
    client = TestClient(_build_app())
    resp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        headers={"Authorization": "Bearer some-meta-token-value-xyz"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"reached_handler": True}


def test_middleware_accepts_pipeboard_token():
    client = TestClient(_build_app())
    resp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        headers={"X-PIPEBOARD-API-TOKEN": "pb-token-abc"},
    )
    assert resp.status_code == 200


def test_redact_url_strips_access_token():
    url = (
        "https://graph.facebook.com/v24.0/me/adaccounts"
        "?fields=id&limit=1&access_token=SECRET_TOKEN_VALUE_123456789"
    )
    redacted = _redact_url(url)
    assert "SECRET_TOKEN_VALUE_123456789" not in redacted
    assert "access_token=REDACTED" in redacted
    assert "fields=id" in redacted
    assert "limit=1" in redacted


def test_redact_url_strips_appsecret_proof():
    url = "https://graph.facebook.com/v24.0/me?access_token=T&appsecret_proof=PROOF"
    redacted = _redact_url(url)
    assert "PROOF" not in redacted
    assert "appsecret_proof=REDACTED" in redacted
    assert "access_token=REDACTED" in redacted


def test_redact_url_no_query_string():
    url = "https://graph.facebook.com/v24.0/me/adaccounts"
    assert _redact_url(url) == url


def test_redact_url_empty():
    assert _redact_url("") == ""


@pytest.mark.asyncio
async def test_make_api_request_error_response_does_not_leak_token():
    """End-to-end check: 4xx from Graph API must not echo the access token."""
    secret = "FAKE_ACCESS_TOKEN_VALUE_FOR_TEST_123"

    # Mock httpx response: 400 with a Graph-style error body.
    error_body = {"error": {"message": "Invalid OAuth access token data.",
                            "type": "OAuthException", "code": 190}}

    fake_request = httpx.Request(
        "GET",
        f"https://graph.facebook.com/v24.0/me/adaccounts?fields=id&access_token={secret}",
    )
    fake_response = httpx.Response(
        status_code=400,
        request=fake_request,
        headers={"content-type": "application/json"},
        content=json.dumps(error_body).encode(),
    )

    async def fake_get(self, url, params=None, headers=None, timeout=None):
        # httpx.AsyncClient.get is called with params separately; build the
        # final URL the same way httpx would for an accurate test.
        req = httpx.Request("GET", url, params=params, headers=headers)
        resp = httpx.Response(
            status_code=400,
            request=req,
            headers={"content-type": "application/json"},
            content=json.dumps(error_body).encode(),
        )
        return resp

    with patch("httpx.AsyncClient.get", new=fake_get):
        result = await make_api_request("me/adaccounts", secret, {"fields": "id"})

    assert "error" in result
    full = result["error"]["full_response"]
    serialized = json.dumps(result)
    assert secret not in serialized, (
        f"access_token leaked in error payload: {serialized}"
    )
    assert "access_token=REDACTED" in full["request_url"]
    assert "access_token=REDACTED" in full["url"]
