"""Test that create_ad_creative handles simple creatives correctly."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import create_ad_creative


@pytest.mark.asyncio
async def test_simple_creative_uses_object_story_spec():
    """Test that singular headline/description uses object_story_spec, not asset_feed_spec."""
    
    # Mock the make_api_request function
    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:
        
        # Mock page discovery
        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }
        
        # Mock creative creation response
        mock_api.side_effect = [
            # First call: Create creative
            {"id": "creative_123"},
            # Second call: Get creative details
            {
                "id": "creative_123",
                "name": "Test Creative",
                "status": "ACTIVE"
            }
        ]
        
        # Call create_ad_creative with singular headline and description
        result = await create_ad_creative(
            account_id="act_701351919139047",
            image_hash="test_hash_123",
            name="Math Problem - Hormozi",
            link_url="https://adrocketx.ai/",
            message="If you're spending 4+ hours per campaign...",
            headline="Stop paying yourself $12.50/hour",
            description="AI builds campaigns in 3min. 156% higher conversions. Free beta.",
            call_to_action_type="LEARN_MORE",
            access_token="test_token"
        )
        
        # Check that make_api_request was called
        assert mock_api.call_count == 2
        
        # Get the creative_data that was sent to the API
        create_call_args = mock_api.call_args_list[0]
        endpoint = create_call_args[0][0]
        creative_data = create_call_args[0][2]
        
        print("Creative data sent to API:")
        print(json.dumps(creative_data, indent=2))
        
        # Verify it uses object_story_spec, NOT asset_feed_spec
        assert "object_story_spec" in creative_data, "Should use object_story_spec for simple creatives"
        assert "asset_feed_spec" not in creative_data, "Should NOT use asset_feed_spec for simple creatives"
        
        # Verify object_story_spec structure
        assert "link_data" in creative_data["object_story_spec"]
        link_data = creative_data["object_story_spec"]["link_data"]
        
        # Verify simple creative fields are in link_data
        assert link_data["image_hash"] == "test_hash_123"
        assert link_data["link"] == "https://adrocketx.ai/"
        assert link_data["message"] == "If you're spending 4+ hours per campaign..."
        
        # The issue: headline and description should be in link_data for simple creatives
        # Not in asset_feed_spec
        print("\nlink_data structure:")
        print(json.dumps(link_data, indent=2))


@pytest.mark.asyncio
async def test_dynamic_creative_uses_asset_feed_spec():
    """Test that plural headlines/descriptions uses asset_feed_spec."""
    
    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:
        
        # Mock page discovery
        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }
        
        # Mock creative creation response
        mock_api.side_effect = [
            {"id": "creative_456"},
            {"id": "creative_456", "name": "Dynamic Creative", "status": "ACTIVE"}
        ]
        
        # Call with PLURAL headlines and descriptions (dynamic creative)
        result = await create_ad_creative(
            account_id="act_701351919139047",
            image_hash="test_hash_456",
            name="Dynamic Creative Test",
            link_url="https://example.com/",
            message="Test message",
            headlines=["Headline 1", "Headline 2"],
            descriptions=["Description 1", "Description 2"],
            access_token="test_token"
        )
        
        # Get the creative_data that was sent to the API
        create_call_args = mock_api.call_args_list[0]
        creative_data = create_call_args[0][2]
        
        print("\nDynamic creative data sent to API:")
        print(json.dumps(creative_data, indent=2))
        
        # Verify it uses asset_feed_spec for dynamic creatives
        assert "asset_feed_spec" in creative_data, "Should use asset_feed_spec for dynamic creatives"
        
        # Verify asset_feed_spec structure
        asset_feed_spec = creative_data["asset_feed_spec"]
        assert "headlines" in asset_feed_spec
        assert len(asset_feed_spec["headlines"]) == 2
        assert "descriptions" in asset_feed_spec
        assert len(asset_feed_spec["descriptions"]) == 2

