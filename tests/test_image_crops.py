import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.ads import create_ad_creative


@pytest.mark.asyncio
async def test_simple_creative_includes_image_crops():
    """image_crops should appear in link_data for simple image creatives."""
    crops = {"100x100": [[0, 0], [600, 600]]}

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }
        mock_api.side_effect = [
            {"id": "creative_1"},
            {"id": "creative_1", "name": "Test", "status": "ACTIVE"},
        ]

        await create_ad_creative(
            account_id="act_123",
            image_hash="abc123",
            name="Crop Test",
            link_url="https://example.com/",
            message="Hello",
            image_crops=crops,
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]
        link_data = creative_data["object_story_spec"]["link_data"]
        assert link_data["image_crops"] == crops


@pytest.mark.asyncio
async def test_dof_creative_includes_image_crops():
    """image_crops should appear in link_data for DOF/FLEX creatives."""
    crops = {"191x100": [[0, 0], [1200, 628]]}

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }
        mock_api.side_effect = [
            {"id": "creative_2"},
            {"id": "creative_2", "name": "DOF Crop", "status": "ACTIVE"},
        ]

        await create_ad_creative(
            account_id="act_123",
            image_hashes=["abc123", "def456"],
            name="DOF Crop Test",
            link_url="https://example.com/",
            messages=["Msg 1", "Msg 2"],
            optimization_type="DEGREES_OF_FREEDOM",
            image_crops=crops,
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]
        link_data = creative_data["object_story_spec"]["link_data"]
        assert link_data["image_crops"] == crops


@pytest.mark.asyncio
async def test_simple_creative_omits_image_crops_when_none():
    """When image_crops is not provided, link_data should not contain it."""
    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }
        mock_api.side_effect = [
            {"id": "creative_3"},
            {"id": "creative_3", "name": "No Crop", "status": "ACTIVE"},
        ]

        await create_ad_creative(
            account_id="act_123",
            image_hash="abc123",
            name="No Crop Test",
            link_url="https://example.com/",
            message="Hello",
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]
        link_data = creative_data["object_story_spec"]["link_data"]
        assert "image_crops" not in link_data


@pytest.mark.asyncio
async def test_image_crops_json_string_coercion():
    """image_crops passed as a JSON string should be parsed into a dict."""
    crops_str = '{"100x100": [[0, 0], [600, 600]]}'
    expected = {"100x100": [[0, 0], [600, 600]]}

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }
        mock_api.side_effect = [
            {"id": "creative_4"},
            {"id": "creative_4", "name": "Coerce", "status": "ACTIVE"},
        ]

        await create_ad_creative(
            account_id="act_123",
            image_hash="abc123",
            name="Coerce Test",
            link_url="https://example.com/",
            message="Hello",
            image_crops=crops_str,
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]
        link_data = creative_data["object_story_spec"]["link_data"]
        assert link_data["image_crops"] == expected


@pytest.mark.asyncio
async def test_image_crops_coexists_with_caption():
    """image_crops and caption should both appear in link_data."""
    crops = {"100x100": [[0, 0], [600, 600]]}

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }
        mock_api.side_effect = [
            {"id": "creative_5"},
            {"id": "creative_5", "name": "Both", "status": "ACTIVE"},
        ]

        await create_ad_creative(
            account_id="act_123",
            image_hash="abc123",
            name="Both Test",
            link_url="https://example.com/",
            message="Hello",
            caption="example.com/shoes",
            image_crops=crops,
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]
        link_data = creative_data["object_story_spec"]["link_data"]
        assert link_data["caption"] == "example.com/shoes"
        assert link_data["image_crops"] == crops
