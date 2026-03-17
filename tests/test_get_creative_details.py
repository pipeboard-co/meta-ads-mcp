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
    # degrees_of_freedom_spec fetch returns CFS data
    mock_dof_response = {
        "degrees_of_freedom_spec": {"creative_features_spec": {"profile_card": {"enroll_status": "OPT_IN"}}},
    }
    # product_set_id fetch returns empty (not a DPA creative)
    mock_product_set_response = {}

    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [mock_main_response, mock_dcs_response, mock_dof_response, mock_product_set_response]

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
        assert data["degrees_of_freedom_spec"]["creative_features_spec"]["profile_card"]["enroll_status"] == "OPT_IN"

        # Verify the API was called 4 times: main fields + dynamic_creative_spec + degrees_of_freedom_spec + product_set_id
        assert mock_api.call_count == 4
        # First call: main fields (should NOT include dynamic_creative_spec)
        first_call = mock_api.call_args_list[0]
        assert first_call[0][0] == "creative_123"
        assert "object_story_spec" in first_call[0][2]["fields"]
        assert "asset_feed_spec" in first_call[0][2]["fields"]
        assert "dynamic_creative_spec" not in first_call[0][2]["fields"]
        # Second call: dynamic_creative_spec only
        second_call = mock_api.call_args_list[1]
        assert second_call[0][2]["fields"] == "dynamic_creative_spec"
        # Third call: degrees_of_freedom_spec
        third_call = mock_api.call_args_list[2]
        assert third_call[0][2]["fields"] == "degrees_of_freedom_spec"
        # Fourth call: product_set_id
        fourth_call = mock_api.call_args_list[3]
        assert fourth_call[0][2]["fields"] == "product_set_id"


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
    # Optional field calls fail (fields do not exist on this creative type)
    mock_dcs_error = {
        "error": {"message": "Tried accessing nonexisting field", "code": 100}
    }
    mock_dof_error = {
        "error": {"message": "Tried accessing nonexisting field", "code": 100}
    }
    mock_ps_error = {
        "error": {"message": "Tried accessing nonexisting field", "code": 100}
    }

    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [mock_main_response, mock_dcs_error, mock_dof_error, mock_ps_error]

        result = await get_creative_details(
            creative_id="creative_456", access_token="test_token"
        )

        data = parse_result(result)
        assert data["id"] == "creative_456"
        assert "dynamic_creative_spec" not in data
        assert "product_set_id" not in data


@pytest.mark.asyncio
async def test_get_creative_details_dpa_with_product_set():
    """Test that DPA creatives return product_set_id and resolved catalog info."""
    mock_main_response = {
        "id": "creative_dpa",
        "name": "DPA Creative",
        "status": "ACTIVE",
        "object_story_spec": {
            "page_id": "page_123",
            "template_data": {"link": "https://example.com"},
        },
    }
    mock_dcs_response = {}  # No dynamic_creative_spec on DPA
    mock_dof_response = {}  # No degrees_of_freedom_spec on DPA
    mock_ps_response = {"product_set_id": "ps_999"}
    mock_catalog_response = {
        "product_catalog": {"id": "catalog_555", "name": "My Catalog"},
    }

    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [
            mock_main_response,
            mock_dcs_response,
            mock_dof_response,
            mock_ps_response,
            mock_catalog_response,
        ]

        result = await get_creative_details(
            creative_id="creative_dpa", access_token="test_token"
        )

        data = parse_result(result)
        assert data["product_set_id"] == "ps_999"
        assert data["catalog_id"] == "catalog_555"
        assert data["catalog_name"] == "My Catalog"

        # 5 calls: core + dynamic_creative_spec + degrees_of_freedom_spec + product_set_id + catalog resolution
        assert mock_api.call_count == 5


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
