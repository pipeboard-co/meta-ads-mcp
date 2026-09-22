"""Regression tests for the FRZ MCP output security boundary.

Provider responses are untrusted: Meta can echo request credentials in paging
URLs, error messages, or nested objects.  Nothing crossing the MCP boundary may
contain those credentials or a provider pagination URL.
"""

import json

import pytest

from meta_ads_mcp.core.api import (
    McpToolError,
    _assert_no_secret,
    _sanitize_mcp_payload,
    meta_api_tool,
)


SECRET = "sentinel-secret-token"


def test_recursive_payload_redaction_and_opaque_pagination():
    payload = {
        "data": [
            {
                "id": "120012345678901234",
                "nested": {
                    "url": (
                        "https://graph.facebook.com/v24.0/items"
                        f"?after=opaque-cursor&access_token={SECRET}"
                        "&appsecret_proof=proof-secret"
                    ),
                    "authorization": f"Bearer {SECRET}",
                },
            }
        ],
        "paging": {
            "cursors": {"after": "opaque-cursor"},
            "next": (
                "https://graph.facebook.com/v24.0/items"
                f"?after=opaque-cursor&access_token={SECRET}"
            ),
        },
    }

    sanitized = _sanitize_mcp_payload(payload, secrets=(SECRET, "proof-secret"))
    serialized = json.dumps(sanitized)

    assert sanitized == {
        "items": [
            {
                "id": "120012345678901234",
                "nested": {
                    "url": (
                        "https://graph.facebook.com/v24.0/items"
                        "?after=opaque-cursor&access_token=REDACTED"
                        "&appsecret_proof=REDACTED"
                    ),
                    "authorization": "REDACTED",
                },
            }
        ],
        "next_cursor": "opaque-cursor",
        "has_more": True,
    }
    assert SECRET not in serialized
    assert "proof-secret" not in serialized
    assert "paging.next" not in serialized


def test_percent_encoded_query_and_bearer_are_redacted():
    payload = {
        "encoded": (
            "https%3A%2F%2Fgraph.facebook.com%2Fv24.0%2Fme"
            f"%3Faccess_token%3D{SECRET}%26after%3Dcursor"
        ),
        "message": f"request failed with Authorization: Bearer {SECRET}",
        "client_secret": SECRET,
        "cookies": {"session": SECRET},
    }

    serialized = json.dumps(_sanitize_mcp_payload(payload, secrets=(SECRET,)))

    assert SECRET not in serialized
    assert "client_secret" in serialized
    assert "REDACTED" in serialized


def test_legitimate_meta_ids_are_not_false_positives():
    payload = {
        "account_id": "act_120012345678901234",
        "campaign_id": "120012345678901234",
        "name": "Campaign access_token awareness",
    }

    assert _sanitize_mcp_payload(payload, secrets=(SECRET,)) == payload


def test_secret_detector_rejects_a_remaining_sentinel():
    with pytest.raises(McpToolError, match="unsafe_output_blocked"):
        _assert_no_secret({"nested": ["prefix sentinel-secret-token suffix"]}, (SECRET,))


@pytest.mark.asyncio
async def test_tool_boundary_sanitizes_successful_provider_response(monkeypatch):
    monkeypatch.setenv("META_ACCESS_TOKEN", SECRET)
    monkeypatch.delenv("META_APP_SECRET", raising=False)

    @meta_api_tool
    async def list_items(access_token=None):
        return {
            "data": [{"id": "1"}],
            "paging": {
                "cursors": {"after": "cursor-2"},
                "next": f"https://graph.facebook.com/items?access_token={SECRET}",
            },
        }

    result = json.loads(await list_items(access_token=SECRET))

    assert result == {
        "items": [{"id": "1"}],
        "next_cursor": "cursor-2",
        "has_more": True,
    }
    assert SECRET not in json.dumps(result)


@pytest.mark.asyncio
async def test_tool_boundary_allows_a_redacted_bearer_message(monkeypatch):
    monkeypatch.setenv("META_ACCESS_TOKEN", SECRET)
    monkeypatch.delenv("META_APP_SECRET", raising=False)

    @meta_api_tool
    async def diagnose(access_token=None):
        return {"message": f"provider echoed Bearer {SECRET}"}

    result = json.loads(await diagnose(access_token=SECRET))

    assert result == {"message": "provider echoed Bearer REDACTED"}
