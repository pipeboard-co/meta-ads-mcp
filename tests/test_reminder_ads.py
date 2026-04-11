"""
Tests for Instagram Reminder Ads support (REMINDERS_SET optimization goal).

Reminder Ads use reminder_data inside object_story_spec.link_data to define
an inline event (name, start_time, end_time) without requiring an existing
FB event / ig_upcoming_event_id.
"""

import json
import pytest
from unittest.mock import patch

from meta_ads_mcp.core.ads import create_ad_creative


REMINDER = {
    "event_name": "Summer Sale",
    "start_time": 1745596800,
    "end_time": 1745611200,
}


def _mock_discovery():
    return {"success": True, "page_id": "123456789", "page_name": "Test Page"}


def _mock_api_responses(creative_id="creative_reminder_1"):
    return [
        {"id": creative_id},
        {"id": creative_id, "name": "Reminder Ad", "status": "ACTIVE"},
    ]


# ---------------------------------------------------------------------------
# Simple image creative (no asset_feed_spec)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reminder_data_in_simple_image_link_data():
    """reminder_data is placed inside object_story_spec.link_data for a simple image creative."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, \
         patch("meta_ads_mcp.core.ads._discover_pages_for_account") as mock_discover:

        mock_discover.return_value = _mock_discovery()
        mock_api.side_effect = _mock_api_responses()

        result = await create_ad_creative(
            account_id="act_123456789",
            image_hash="test_hash_abc",
            name="IG Reminder Ad",
            link_url="https://example.com/sale",
            message="Don't miss our sale!",
            reminder_data=REMINDER,
            access_token="test_token",
        )

        data = json.loads(result)
        assert data.get("success") is True

        create_call_args = mock_api.call_args_list[0]
        creative_data = create_call_args[0][2]

        # Must use object_story_spec, not asset_feed_spec
        assert "object_story_spec" in creative_data
        assert "asset_feed_spec" not in creative_data

        link_data = creative_data["object_story_spec"]["link_data"]
        assert "reminder_data" in link_data, "reminder_data must be in link_data"
        assert link_data["reminder_data"]["event_name"] == "Summer Sale"
        assert link_data["reminder_data"]["start_time"] == 1745596800
        assert link_data["reminder_data"]["end_time"] == 1745611200

        # Other link_data fields must still be present
        assert link_data["image_hash"] == "test_hash_abc"
        assert link_data["link"] == "https://example.com/sale"


@pytest.mark.asyncio
async def test_reminder_data_without_link_url():
    """reminder_data can be used without link_url (link_url is optional when reminder_data is provided)."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, \
         patch("meta_ads_mcp.core.ads._discover_pages_for_account") as mock_discover:

        mock_discover.return_value = _mock_discovery()
        mock_api.side_effect = _mock_api_responses()

        result = await create_ad_creative(
            account_id="act_123456789",
            image_hash="test_hash_abc",
            name="IG Reminder No URL",
            reminder_data=REMINDER,
            access_token="test_token",
        )

        data = json.loads(result)
        # Should not fail with "No link_url provided" error
        assert "error" not in data or "No link_url" not in data.get("error", "")
        assert data.get("success") is True

        create_call_args = mock_api.call_args_list[0]
        creative_data = create_call_args[0][2]
        link_data = creative_data["object_story_spec"]["link_data"]

        assert "reminder_data" in link_data
        # link field should not be present when link_url was not provided
        assert "link" not in link_data


@pytest.mark.asyncio
async def test_reminder_data_as_json_string_is_coerced():
    """reminder_data passed as a JSON string (some MCP transports) is coerced to a dict."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, \
         patch("meta_ads_mcp.core.ads._discover_pages_for_account") as mock_discover:

        mock_discover.return_value = _mock_discovery()
        mock_api.side_effect = _mock_api_responses()

        reminder_json_str = json.dumps(REMINDER)

        result = await create_ad_creative(
            account_id="act_123456789",
            image_hash="test_hash_abc",
            name="IG Reminder JSON String",
            link_url="https://example.com/sale",
            reminder_data=reminder_json_str,  # type: ignore[arg-type]
            access_token="test_token",
        )

        data = json.loads(result)
        assert data.get("success") is True

        create_call_args = mock_api.call_args_list[0]
        creative_data = create_call_args[0][2]
        link_data = creative_data["object_story_spec"]["link_data"]

        assert isinstance(link_data["reminder_data"], dict)
        assert link_data["reminder_data"]["event_name"] == "Summer Sale"


@pytest.mark.asyncio
async def test_no_reminder_data_does_not_inject_field():
    """When reminder_data is not provided, link_data must NOT contain a reminder_data key."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, \
         patch("meta_ads_mcp.core.ads._discover_pages_for_account") as mock_discover:

        mock_discover.return_value = _mock_discovery()
        mock_api.side_effect = [
            {"id": "creative_regular"},
            {"id": "creative_regular", "name": "Regular Ad", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456789",
            image_hash="test_hash_abc",
            name="Regular Image Ad",
            link_url="https://example.com/page",
            message="Check this out",
            access_token="test_token",
        )

        data = json.loads(result)
        assert data.get("success") is True

        create_call_args = mock_api.call_args_list[0]
        creative_data = create_call_args[0][2]
        link_data = creative_data["object_story_spec"]["link_data"]

        assert "reminder_data" not in link_data


# ---------------------------------------------------------------------------
# Missing link_url without reminder_data still returns an error
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_link_url_without_reminder_data_returns_error():
    """Omitting both link_url and reminder_data (and lead_gen_form_id) should still error."""
    with patch("meta_ads_mcp.core.ads._discover_pages_for_account") as mock_discover:
        mock_discover.return_value = _mock_discovery()

        result = await create_ad_creative(
            account_id="act_123456789",
            image_hash="test_hash_abc",
            name="Bad Ad",
            access_token="test_token",
            # No link_url, no lead_gen_form_id, no reminder_data
        )

        # The @meta_api_tool decorator may wrap the error JSON in a "data" key.
        outer = json.loads(result)
        if "data" in outer:
            error_data = json.loads(outer["data"])
        else:
            error_data = outer
        assert "error" in error_data
        assert "link_url" in error_data["error"]
