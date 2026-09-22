"""Regression tests for GHSA-6v2r-2m4r-768m.

The OAuth callback server reflected the `error` query parameter into an HTML
error page with no output encoding, so any page in the browser could navigate
to http://localhost:8080-8089/callback?error=<script>... during the 180s
authorization window and run script on the localhost origin.
"""

import threading
from http.server import HTTPServer
from urllib.parse import quote

import httpx
import pytest

from meta_ads_mcp.core.callback_server import (
    CallbackHandler,
    MAX_ERROR_DISPLAY_LENGTH,
)

XSS_PAYLOAD = "<script>alert(document.domain)</script>"


@pytest.fixture
def callback_url():
    """Run a real CallbackHandler on an ephemeral localhost port."""
    server = HTTPServer(("localhost", 0), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://localhost:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_error_parameter_is_html_escaped(callback_url):
    response = httpx.get(f"{callback_url}/callback?error={quote(XSS_PAYLOAD)}")

    assert response.status_code == 200
    assert XSS_PAYLOAD not in response.text
    assert "<script>" not in response.text
    # The error is still shown to the user, just entity-encoded.
    assert "&lt;script&gt;" in response.text
    assert "Authorization Failed" in response.text


def test_error_parameter_cannot_break_out_of_attributes(callback_url):
    payload = '" onload="alert(1)'
    response = httpx.get(f"{callback_url}/callback?error={quote(payload)}")

    assert 'onload="alert(1)' not in response.text
    assert "&quot;" in response.text


def test_error_parameter_is_truncated(callback_url):
    payload = "A" * (MAX_ERROR_DISPLAY_LENGTH + 500)
    response = httpx.get(f"{callback_url}/callback?error={payload}")

    assert "A" * MAX_ERROR_DISPLAY_LENGTH in response.text
    assert "A" * (MAX_ERROR_DISPLAY_LENGTH + 1) not in response.text


def test_error_page_sets_locked_down_security_headers(callback_url):
    response = httpx.get(f"{callback_url}/callback?error=access_denied")

    assert response.headers["content-security-policy"] == "default-src 'none'"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_success_page_allows_only_its_own_nonced_script(callback_url):
    response = httpx.get(f"{callback_url}/callback?code=test-auth-code&state=xyz")

    csp = response.headers["content-security-policy"]
    assert csp.startswith("default-src 'none'; script-src 'nonce-")
    nonce = csp.split("'nonce-")[1].rstrip("'")
    # The inline script carries the nonce, so an injected script would not run.
    assert f'<script nonce="{nonce}">' in response.text
    assert response.headers["x-content-type-options"] == "nosniff"


def test_token_endpoint_no_longer_exposes_the_auth_code(callback_url):
    """/token was unreferenced and handed the stored auth code to any
    same-origin page reachable via the XSS above."""
    httpx.get(f"{callback_url}/callback?code=test-auth-code&state=xyz")

    response = httpx.get(f"{callback_url}/token")

    assert response.status_code == 404
    assert "test-auth-code" not in response.text
