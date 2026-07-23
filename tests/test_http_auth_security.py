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
from meta_ads_mcp.core.http_auth_integration import (
    AuthInjectionMiddleware,
    setup_fastmcp_http_auth,
)


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


def test_middleware_rejects_supplementary_token_alone():
    """X-Pipeboard-Token is a supplementary service token (duplication
    callback) and must not, on its own, admit a request — without a primary
    access-token credential the request must be rejected with 401."""
    client = TestClient(_build_app())
    resp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        headers={"X-Pipeboard-Token": "anything-not-validated"},
    )
    assert resp.status_code == 401
    assert resp.headers.get("WWW-Authenticate") == "Bearer"
    assert resp.json()["error"] == "Unauthorized"
    assert "reached_handler" not in resp.text


def test_middleware_accepts_supplementary_token_with_primary_credential():
    """The legitimate flow forwards X-Pipeboard-Token alongside a primary
    credential; the request must still be admitted."""
    client = TestClient(_build_app())
    resp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        headers={
            "Authorization": "Bearer some-meta-token-value-xyz",
            "X-Pipeboard-Token": "pb-supplementary-token",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"reached_handler": True}


# ---------------------------------------------------------------------------
# GHSA-8353-5qhw-8hfw: AuthInjectionMiddleware must be attached to the app that
# the streamable-http transport actually serves (streamable_http_app), in BOTH
# JSON mode and --sse-response mode. The two tests above exercise the
# middleware's dispatch() logic in isolation; these exercise the wiring in
# setup_fastmcp_http_auth() that decides which served app the middleware lands
# on. That wiring is where the vulnerability lived.
# ---------------------------------------------------------------------------

def _has_auth_middleware(app):
    return any(m.cls == AuthInjectionMiddleware for m in app.user_middleware)


def _fresh_fastmcp():
    # Imported lazily so the rest of the suite runs even if the SDK is absent.
    from mcp.server.fastmcp import FastMCP

    return FastMCP("meta-ads-test")


@pytest.mark.parametrize("sse_response", [False, True], ids=["json_mode", "sse_response_mode"])
def test_served_app_has_auth_middleware(sse_response):
    """The served streamable_http_app must carry AuthInjectionMiddleware in
    both wire-format modes. Under --sse-response the previous code attached the
    middleware to sse_app only (never served), leaving /mcp unauthenticated."""
    server = _fresh_fastmcp()
    # server.py:339 -> json_response = not args.sse_response
    server.settings.json_response = not sse_response

    setup_fastmcp_http_auth(server)

    # This is the exact app run_streamable_http_async() serves.
    served_app = server.streamable_http_app()
    assert _has_auth_middleware(served_app), (
        "streamable_http_app (the served app) is missing AuthInjectionMiddleware "
        f"with sse_response={sse_response}; unauthenticated callers could reach tools"
    )


def test_served_app_rejects_unauthenticated_request_in_sse_mode():
    """End-to-end: with --sse-response wiring, an unauthenticated POST /mcp to
    the served app is rejected with 401 rather than reaching a tool handler."""
    server = _fresh_fastmcp()
    server.settings.json_response = False  # simulate --sse-response

    setup_fastmcp_http_auth(server)
    served_app = server.streamable_http_app()

    client = TestClient(served_app)
    resp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "tools/call", "id": 1,
              "params": {"name": "get_ad_accounts", "arguments": {}}},
        headers={"Accept": "application/json, text/event-stream"},
    )
    assert resp.status_code == 401
    assert resp.headers.get("WWW-Authenticate") == "Bearer"


def test_patched_app_providers_do_not_cross_wire():
    """Regression for the late-binding closure: patching both streamable_http_app
    and sse_app must not make one provider call the other's original (which would
    swap which app gets served / recurse). Each served app must be its own type
    and carry the middleware."""
    server = _fresh_fastmcp()
    server.settings.json_response = True

    setup_fastmcp_http_auth(server)

    streamable = server.streamable_http_app()
    sse = server.sse_app()
    # Both are Starlette apps but distinct instances with the middleware present.
    assert streamable is not sse
    assert _has_auth_middleware(streamable)
    assert _has_auth_middleware(sse)


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
