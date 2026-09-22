"""Regression tests for the OAuth `state` check (GHSA-75j5-qp3x-mx37, item 3).

`get_auth_url` emitted no `state` and the callback validated none, so any page
that could reach the callback server could hand it an authorization code of the
attacker's choosing (login CSRF, RFC 6749 §10.12). The callback now only stores
a code whose `state` matches the one minted for the flow this process started,
and the state is single-use.
"""

import threading
from http.server import HTTPServer
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from meta_ads_mcp.core import callback_server
from meta_ads_mcp.core.callback_server import (
    CALLBACK_SERVER_HOST,
    CallbackHandler,
    consume_oauth_state,
    get_oauth_state,
    new_oauth_state,
    token_container,
)


@pytest.fixture
def callback_url():
    """Run a real CallbackHandler on an ephemeral loopback port."""
    server = HTTPServer((CALLBACK_SERVER_HOST, 0), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{CALLBACK_SERVER_HOST}:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture(autouse=True)
def clean_auth_state():
    """Keep the module-level flow state from leaking between tests."""
    callback_server._oauth_state = None
    token_container.pop("auth_code", None)
    token_container.pop("state", None)
    yield
    callback_server._oauth_state = None
    token_container.pop("auth_code", None)
    token_container.pop("state", None)


def test_code_without_state_is_rejected(callback_url):
    new_oauth_state()

    response = httpx.get(f"{callback_url}/callback?code=attacker-code")

    assert response.status_code == 200
    assert "Authorization Rejected" in response.text
    assert "auth_code" not in token_container


def test_code_with_wrong_state_is_rejected(callback_url):
    new_oauth_state()

    response = httpx.get(f"{callback_url}/callback?code=attacker-code&state=guessed")

    assert "Authorization Rejected" in response.text
    assert "auth_code" not in token_container


def test_code_with_matching_state_is_accepted(callback_url):
    state = new_oauth_state()

    response = httpx.get(f"{callback_url}/callback?code=real-code&state={state}")

    assert "Authorization Successful" in response.text
    assert token_container["auth_code"] == "real-code"


def test_state_is_single_use(callback_url):
    state = new_oauth_state()
    httpx.get(f"{callback_url}/callback?code=real-code&state={state}")
    token_container.pop("auth_code", None)

    replay = httpx.get(f"{callback_url}/callback?code=replayed-code&state={state}")

    assert "Authorization Rejected" in replay.text
    assert "auth_code" not in token_container


def test_code_is_rejected_when_no_flow_is_in_flight(callback_url):
    """Nothing minted a state, so nothing may be stored."""
    response = httpx.get(f"{callback_url}/callback?code=attacker-code&state=anything")

    assert "Authorization Rejected" in response.text
    assert "auth_code" not in token_container


def test_consume_rejects_empty_and_mismatched_values():
    state = new_oauth_state()

    assert consume_oauth_state(None) is False
    assert consume_oauth_state("") is False
    assert consume_oauth_state(state + "x") is False
    assert get_oauth_state() == state, "a failed check must not burn the state"
    assert consume_oauth_state(state) is True
    assert get_oauth_state() is None


def test_auth_url_carries_the_state_the_callback_expects():
    from meta_ads_mcp.core.auth import auth_manager

    state = new_oauth_state()
    query = parse_qs(urlparse(auth_manager.get_auth_url()).query)

    assert query["state"] == [state]


def test_auth_url_mints_a_state_when_no_flow_is_in_flight():
    from meta_ads_mcp.core.auth import auth_manager

    query = parse_qs(urlparse(auth_manager.get_auth_url()).query)

    assert query["state"][0]
    assert query["state"][0] == get_oauth_state()


def test_callback_server_binds_loopback_only():
    assert CALLBACK_SERVER_HOST == "127.0.0.1"
