"""Tests for the duplication module."""

import os
import json
import pytest
from unittest.mock import patch, AsyncMock
from meta_ads_mcp.core.duplication import ENABLE_DUPLICATION


def test_duplication_disabled_by_default():
    """Test that duplication is disabled by default."""
    # Test with no environment variable set
    with patch.dict(os.environ, {}, clear=True):
        from meta_ads_mcp.core import duplication
        # When imported fresh, it should be disabled
        assert not duplication.ENABLE_DUPLICATION


def test_duplication_enabled_with_env_var():
    """Test that duplication is enabled when environment variable is set."""
    with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
        # Need to reload the module to pick up the new environment variable
        import importlib
        from meta_ads_mcp.core import duplication
        importlib.reload(duplication)
        assert duplication.ENABLE_DUPLICATION


@pytest.mark.asyncio
async def test_forward_duplication_request_no_token():
    """Test that _forward_duplication_request handles missing access token."""
    from meta_ads_mcp.core.duplication import _forward_duplication_request
    
    result = await _forward_duplication_request("campaign", "123456789", None, {})
    result_json = json.loads(result)
    
    assert result_json["error"] == "authentication_required"
    assert "access token not found" in result_json["message"]


@pytest.mark.asyncio
async def test_forward_duplication_request_with_token():
    """Test that _forward_duplication_request makes HTTP request with proper headers."""
    from meta_ads_mcp.core.duplication import _forward_duplication_request
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.json.return_value = {"error": "premium_feature"}
    
    with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await _forward_duplication_request("campaign", "123456789", "test_token", {
            "name_suffix": " - Test"
        })
        result_json = json.loads(result)
        
        # Should return premium feature message for 403 response
        assert result_json["error"] == "premium_feature_required"
        assert "premium feature" in result_json["message"]
        
        # Verify the HTTP request was made with correct parameters
        mock_client.return_value.__aenter__.return_value.post.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        
        # Check URL
        assert call_args[0][0] == "https://mcp.pipeboard.co/api/meta/duplicate/campaign/123456789"
        
        # Check headers
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Content-Type"] == "application/json"
        
        # Check JSON payload
        json_payload = call_args[1]["json"]
        assert json_payload == {"name_suffix": " - Test"}


@pytest.mark.asyncio
async def test_duplicate_campaign_function_available_when_enabled():
    """Test that duplicate_campaign function is available when feature is enabled."""
    with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
        # Reload module to pick up environment variable
        import importlib
        from meta_ads_mcp.core import duplication
        importlib.reload(duplication)
        
        # Function should be available
        assert hasattr(duplication, 'duplicate_campaign')
        
        # Test that it calls the forwarding function
        with patch("meta_ads_mcp.core.duplication._forward_duplication_request") as mock_forward:
            mock_forward.return_value = '{"success": true}'
            
            result = await duplication.duplicate_campaign("123456789", access_token="test_token")
            
            mock_forward.assert_called_once_with(
                "campaign",
                "123456789",
                "test_token",
                {
                    "name_suffix": " - Copy",
                    "include_ad_sets": True,
                    "include_ads": True,
                    "include_creatives": True,
                    "copy_schedule": False,
                    "new_daily_budget": None,
                    "new_status": "PAUSED"
                }
            )


def test_get_estimated_components():
    """Test the _get_estimated_components helper function."""
    from meta_ads_mcp.core.duplication import _get_estimated_components
    
    # Test campaign with all components
    campaign_result = _get_estimated_components("campaign", {
        "include_ad_sets": True,
        "include_ads": True,
        "include_creatives": True
    })
    assert campaign_result["campaigns"] == 1
    assert "ad_sets" in campaign_result
    assert "ads" in campaign_result
    assert "creatives" in campaign_result
    
    # Test adset
    adset_result = _get_estimated_components("adset", {"include_ads": True})
    assert adset_result["ad_sets"] == 1
    assert "ads" in adset_result
    
    # Test creative only
    creative_result = _get_estimated_components("creative", {})
    assert creative_result == {"creatives": 1} 