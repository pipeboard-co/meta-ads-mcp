"""Test get_creative_details tool."""

import pytest
import json
from unittest.mock import patch
from meta_ads_mcp.core.ads import get_creative_details


def parse_result(result: str) -> dict:
    """Parse result, unwrapping the meta_api_tool decorator envelope if present."""
    data = json.loads(result)
    if "data" in data and isinstance(data["data"], str):
        return json.loads(data["data"])
    return data


@pytest.mark.asyncio
async def test_get_creative_details_returns_fields():
    """Test that get_creative_details returns creative fields from the API."""
    mock_main_response = {
        "id": "creative_123",
        "name": "Test Creative",
        "status": "ACTIVE",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "image_url": "https://example.com/image.jpg",
        "object_story_spec": {
            "page_id": "page_456",
            "video_data": {
                "video_id": "vid_789",
                "message": "Test message",
            },
        },
        "asset_feed_spec": {
            "bodies": [{"text": "Body A"}],
            "optimization_type": "DEGREES_OF_FREEDOM",
        },
    }
    mock_dcs_response = {
        "dynamic_creative_spec": {"some_field": "some_value"},
    }

    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [mock_main_response, mock_dcs_response]

        result = await get_creative_details(
            creative_id="creative_123", access_token="test_token"
        )

        data = parse_result(result)
        assert data["id"] == "creative_123"
        assert data["name"] == "Test Creative"
        assert data["status"] == "ACTIVE"
        assert data["object_story_spec"]["video_data"]["video_id"] == "vid_789"
        assert data["asset_feed_spec"]["optimization_type"] == "DEGREES_OF_FREEDOM"
        assert data["dynamic_creative_spec"] == {"some_field": "some_value"}

        # Verify the API was called twice: main fields + dynamic_creative_spec
        assert mock_api.call_count == 2
        # First call: main fields (should NOT include dynamic_creative_spec)
        first_call = mock_api.call_args_list[0]
        assert first_call[0][0] == "creative_123"
        assert "object_story_spec" in first_call[0][2]["fields"]
        assert "asset_feed_spec" in first_call[0][2]["fields"]
        assert "dynamic_creative_spec" not in first_call[0][2]["fields"]
        # Second call: dynamic_creative_spec only
        second_call = mock_api.call_args_list[1]
        assert second_call[0][2]["fields"] == "dynamic_creative_spec"


@pytest.mark.asyncio
async def test_get_creative_details_without_dynamic_creative_spec():
    """Test that get_creative_details works when dynamic_creative_spec is not available."""
    mock_main_response = {
        "id": "creative_456",
        "name": "Simple Creative",
        "status": "ACTIVE",
        "object_story_spec": {
            "page_id": "page_789",
            "video_data": {"video_id": "vid_111"},
        },
    }
    # Second call fails (field doesn't exist on this creative type)
    mock_dcs_error = {
        "error": {"message": "Tried accessing nonexisting field", "code": 100}
    }

    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [mock_main_response, mock_dcs_error]

        result = await get_creative_details(
            creative_id="creative_456", access_token="test_token"
        )

        data = parse_result(result)
        assert data["id"] == "creative_456"
        assert "dynamic_creative_spec" not in data


@pytest.mark.asyncio
async def test_get_creative_details_empty_id():
    """Test that empty creative_id returns an error."""
    result = await get_creative_details(creative_id="", access_token="test_token")
    data = parse_result(result)
    assert "error" in data
    assert "No creative ID" in data["error"]


@pytest.mark.asyncio
async def test_get_creative_details_api_error():
    """Test that API errors are propagated."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.return_value = {
            "error": {"message": "Invalid creative ID", "code": 100}
        }

        result = await get_creative_details(
            creative_id="bad_id", access_token="test_token"
        )

        data = parse_result(result)
        assert "error" in data
