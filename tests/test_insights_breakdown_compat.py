"""Tests for breakdowns that conflict with the default action_breakdowns=[action_type].

Meta rejects certain data breakdowns when paired with the default
action_breakdowns=[action_type]. get_insights auto-drops the action-typed
fields (actions, action_values, cost_per_action_type, conversions) for those
breakdowns so the request returns rows successfully.
"""

import json

import pytest
from unittest.mock import patch

from meta_ads_mcp.core.insights import get_insights


_INCOMPATIBLE_MEDIA_BREAKDOWNS = [
    "media_asset_url",
    "media_creator",
    "media_destination_url",
    "media_format",
    "media_origin_url",
    "media_text_content",
    "media_type",
]


@pytest.fixture
def mock_api_request():
    with patch("meta_ads_mcp.core.insights.make_api_request") as mock:
        mock.return_value = {"data": [], "paging": {}}
        yield mock


@pytest.fixture
def mock_auth_manager():
    with patch("meta_ads_mcp.core.api.auth_manager") as mock, patch(
        "meta_ads_mcp.core.auth.get_current_access_token"
    ) as mock_get_token:
        mock.get_current_access_token.return_value = "test_access_token"
        mock.is_token_valid.return_value = True
        mock.app_id = "test_app_id"
        mock_get_token.return_value = "test_access_token"
        yield mock


@pytest.mark.asyncio
@pytest.mark.parametrize("breakdown", _INCOMPATIBLE_MEDIA_BREAKDOWNS)
async def test_media_breakdown_drops_action_typed_fields(
    breakdown, mock_api_request, mock_auth_manager
):
    """media_* breakdowns must drop action-typed fields to avoid Meta error #100."""
    await get_insights(account_id="act_test", level="ad", breakdown=breakdown)

    params = mock_api_request.call_args[0][2]
    fields = params["fields"]

    for action_field in ("actions", "action_values", "cost_per_action_type", "conversions"):
        assert action_field not in fields, (
            f"breakdown={breakdown} did not drop {action_field}; got fields={fields}"
        )

    assert params["breakdowns"] == breakdown


@pytest.mark.asyncio
async def test_compatible_breakdown_preserves_action_typed_fields(
    mock_api_request, mock_auth_manager
):
    """A compatible breakdown like image_asset must keep action-typed fields."""
    await get_insights(account_id="act_test", level="ad", breakdown="image_asset")

    fields = mock_api_request.call_args[0][2]["fields"]
    assert "actions" in fields
    assert "action_values" in fields
    assert "cost_per_action_type" in fields


@pytest.mark.asyncio
async def test_incompatible_breakdown_surfaces_dropped_fields_note(
    mock_api_request, mock_auth_manager
):
    """When fields are dropped, the response carries a note + dropped_fields list."""
    result = await get_insights(
        account_id="act_test", level="ad", breakdown="media_asset_url"
    )
    payload = json.loads(result)

    assert "note" in payload
    assert "media_asset_url" in payload["note"]
    assert "Dropped" in payload["note"]

    assert "dropped_fields" in payload
    assert set(payload["dropped_fields"]) == {
        "actions",
        "action_values",
        "cost_per_action_type",
        "conversions",
    }


@pytest.mark.asyncio
async def test_compatible_breakdown_does_not_emit_note(
    mock_api_request, mock_auth_manager
):
    """No drop happened, so no note/dropped_fields keys leak into the response."""
    result = await get_insights(account_id="act_test", level="ad", breakdown="age")
    payload = json.loads(result)

    assert "note" not in payload
    assert "dropped_fields" not in payload
