"""
Tests for the SSRF guard on server-side image fetches.

Covers GHSA-45gf-fjxp-cjpq: upload_ad_image / the image-viewing tools fetch a
caller-supplied URL server-side, so the URL must be restricted to public
http(s) targets before any connection is opened.

These tests use literal IPs for the block/allow matrix so they do not depend on
network DNS; only the "localhost" case exercises real name resolution (which is
universally available).
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from meta_ads_mcp.core.utils import (
    BlockedURLError,
    validate_public_url,
    download_image,
    try_multiple_download_methods,
    _ssrf_guard_request_hook,
)


# --- validate_public_url: blocked targets -----------------------------------

BLOCKED_URLS = [
    "http://127.0.0.1/poc.jpg",            # loopback
    "http://127.0.0.1:9009/x",             # loopback w/ port
    "http://169.254.169.254/latest/meta-data/",  # cloud metadata (link-local)
    "http://10.0.0.1/internal",            # RFC 1918
    "http://10.255.255.255/",              # RFC 1918
    "http://192.168.1.1/admin",            # RFC 1918
    "http://172.16.0.1/",                  # RFC 1918
    "http://0.0.0.0/",                     # unspecified
    "http://[::1]/",                       # IPv6 loopback
    "http://[::ffff:127.0.0.1]/",          # IPv4-mapped IPv6 loopback bypass
    "http://[fe80::1]/",                   # IPv6 link-local
    "http://[fc00::1]/",                   # IPv6 unique-local (private)
    "https://169.254.169.254/",            # https also blocked
]


@pytest.mark.parametrize("url", BLOCKED_URLS)
def test_validate_public_url_blocks_internal_targets(url):
    with pytest.raises(BlockedURLError):
        validate_public_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/x",
        "gopher://127.0.0.1:6379/_INFO",
        "data:image/png;base64,AAAA",
        "//example.com/x",       # no scheme
        "example.com/x",         # no scheme
    ],
)
def test_validate_public_url_blocks_non_http_schemes(url):
    with pytest.raises(BlockedURLError):
        validate_public_url(url)


@pytest.mark.parametrize("url", ["", None, "http://", "https:///path"])
def test_validate_public_url_blocks_empty_or_hostless(url):
    with pytest.raises(BlockedURLError):
        validate_public_url(url)


def test_validate_public_url_blocks_localhost_name():
    # Resolves (127.0.0.1 / ::1) and must be rejected.
    with pytest.raises(BlockedURLError):
        validate_public_url("http://localhost:8080/admin")


# --- validate_public_url: allowed targets -----------------------------------

@pytest.mark.parametrize(
    "url",
    [
        "https://1.1.1.1/image.jpg",       # public IPv4 literal
        "http://8.8.8.8/x.png",            # public IPv4 literal
        "https://[2606:4700:4700::1111]/x.jpg",  # public IPv6 literal
    ],
)
def test_validate_public_url_allows_public_ip_literals(url):
    # Should not raise.
    validate_public_url(url)


# --- request event hook (covers redirect hops) ------------------------------

async def test_ssrf_guard_request_hook_blocks_internal():
    req = httpx.Request("GET", "http://169.254.169.254/latest/meta-data/")
    with pytest.raises(BlockedURLError):
        await _ssrf_guard_request_hook(req)


async def test_ssrf_guard_request_hook_allows_public():
    req = httpx.Request("GET", "https://8.8.8.8/x.png")
    await _ssrf_guard_request_hook(req)  # should not raise


async def test_redirect_to_internal_is_blocked_via_hook():
    """A public URL that 302-redirects to an internal address must be blocked
    at the redirect hop by the event hook, not followed."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "8.8.8.8":
            # The public entry point redirects inward.
            return httpx.Response(302, headers={"Location": "http://169.254.169.254/secret"})
        # Reaching the internal target means the guard failed; return 200 so the
        # get() would succeed and the pytest.raises below would fail the test.
        return httpx.Response(200, content=b"SHOULD-NOT-BE-FETCHED")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        follow_redirects=True,
        event_hooks={"request": [_ssrf_guard_request_hook]},
    ) as client:
        with pytest.raises(BlockedURLError):
            await client.get("https://8.8.8.8/start")


# --- download_image: returns None (does not raise) for blocked URLs ---------

async def test_download_image_returns_none_for_blocked_url():
    # No network: validation fails before any connection attempt.
    result = await download_image("http://127.0.0.1/secret")
    assert result is None


# --- try_multiple_download_methods: raises for blocked URLs -----------------

async def test_try_multiple_download_methods_raises_for_blocked_url():
    with pytest.raises(BlockedURLError):
        await try_multiple_download_methods("http://169.254.169.254/latest/meta-data/")


# --- upload_ad_image surfaces a clear error for an internal image_url --------

async def test_upload_ad_image_rejects_internal_image_url():
    from meta_ads_mcp.core.ads import upload_ad_image

    # make_api_request must never be called — the fetch is rejected first.
    with patch(
        "meta_ads_mcp.core.ads.make_api_request", new_callable=AsyncMock
    ) as mock_api:
        result_json = await upload_ad_image(
            access_token="test",
            account_id="act_123",
            image_url="http://169.254.169.254/latest/meta-data/",
        )

    mock_api.assert_not_called()

    # The MCP tool wrapper may nest the payload under a data field; just assert
    # the rejection signal is present in the serialized response.
    assert "error" in result_json
    assert "non-public address" in result_json
