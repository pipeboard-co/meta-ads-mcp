"""Tests for the duplication module."""

import os
import json
import pytest
from unittest.mock import patch, AsyncMock, Mock
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
async def test_forward_duplication_request_no_pipeboard_token():
    """Test that _forward_duplication_request handles missing Pipeboard token."""
    from meta_ads_mcp.core.duplication import _forward_duplication_request
    
    # Mock the auth integration to return no Pipeboard token but a Facebook token
    with patch("meta_ads_mcp.core.duplication.FastMCPAuthIntegration") as mock_auth:
        mock_auth.get_pipeboard_token.return_value = None  # No Pipeboard token
        mock_auth.get_auth_token.return_value = "facebook_token"  # Has Facebook token
        
        result = await _forward_duplication_request("campaign", "123456789", None, {})
        result_json = json.loads(result)
        
        assert result_json["error"] == "authentication_required"
        assert "Pipeboard API token not found" in result_json["message"]


@pytest.mark.asyncio
async def test_forward_duplication_request_no_facebook_token():
    """Test that _forward_duplication_request handles missing Facebook token."""
    from meta_ads_mcp.core.duplication import _forward_duplication_request
    
    # Mock the auth integration to return Pipeboard token but no Facebook token
    with patch("meta_ads_mcp.core.duplication.FastMCPAuthIntegration") as mock_auth:
        mock_auth.get_pipeboard_token.return_value = "pipeboard_token"  # Has Pipeboard token
        mock_auth.get_auth_token.return_value = None  # No Facebook token
        
        # Mock get_current_access_token to also return None
        with patch("meta_ads_mcp.core.auth.get_current_access_token") as mock_get_token:
            mock_get_token.return_value = None
            
            result = await _forward_duplication_request("campaign", "123456789", None, {})
            result_json = json.loads(result)
            
            assert result_json["error"] == "authentication_required"
            assert "Meta Ads access token not found" in result_json["message"]


@pytest.mark.asyncio
async def test_forward_duplication_request_with_both_tokens():
    """Test that _forward_duplication_request makes HTTP request with dual headers."""
    from meta_ads_mcp.core.duplication import _forward_duplication_request
    
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.json.return_value = {"error": "premium_feature"}
    
    # Mock the auth integration to return both tokens
    with patch("meta_ads_mcp.core.duplication.FastMCPAuthIntegration") as mock_auth:
        mock_auth.get_pipeboard_token.return_value = "pipeboard_token"
        mock_auth.get_auth_token.return_value = "facebook_token"
        
        with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await _forward_duplication_request("campaign", "123456789", None, {
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
            
            # Check dual headers (the key change!)
            headers = call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer facebook_token"  # Facebook token for Meta API
            assert headers["X-Pipeboard-Token"] == "pipeboard_token"   # Pipeboard token for auth
            assert headers["Content-Type"] == "application/json"
            
            # Check JSON payload
            json_payload = call_args[1]["json"]
            assert json_payload == {"name_suffix": " - Test"}


@pytest.mark.asyncio
async def test_forward_duplication_request_with_provided_access_token():
    """Test that provided access_token parameter is used when available."""
    from meta_ads_mcp.core.duplication import _forward_duplication_request
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "new_campaign_id": "987654321"}
    
    # Mock the auth integration to return Pipeboard token but no Facebook token in context
    with patch("meta_ads_mcp.core.duplication.FastMCPAuthIntegration") as mock_auth:
        mock_auth.get_pipeboard_token.return_value = "pipeboard_token"
        mock_auth.get_auth_token.return_value = None  # No Facebook token in context
        
        with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Provide access_token as parameter
            result = await _forward_duplication_request("campaign", "123456789", "provided_facebook_token", {})
            result_json = json.loads(result)
            
            # Should succeed
            assert result_json["success"] is True
            
            # Verify the HTTP request used the provided token
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            headers = call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer provided_facebook_token"
            assert headers["X-Pipeboard-Token"] == "pipeboard_token"


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


@pytest.mark.asyncio 
async def test_dual_header_authentication_integration():
    """Test that the dual-header authentication works end-to-end."""
    from meta_ads_mcp.core.duplication import _forward_duplication_request
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "new_campaign_id": "987654321",
        "subscription": {"status": "active"}
    }
    
    # Test the complete dual-header flow
    with patch("meta_ads_mcp.core.duplication.FastMCPAuthIntegration") as mock_auth:
        mock_auth.get_pipeboard_token.return_value = "pb_token_12345"
        mock_auth.get_auth_token.return_value = "fb_token_67890" 
        
        with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await _forward_duplication_request("adset", "456789", None, {
                "target_campaign_id": "123456",
                "include_ads": True
            })
            result_json = json.loads(result)
            
            # Should succeed
            assert result_json["success"] is True
            assert result_json["new_campaign_id"] == "987654321"
            
            # Verify correct endpoint was called
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            assert "adset/456789" in call_args[0][0]
            
            # Verify dual headers were sent correctly
            headers = call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer fb_token_67890"
            assert headers["X-Pipeboard-Token"] == "pb_token_12345"
            
            # Verify payload
            payload = call_args[1]["json"]
            assert payload["target_campaign_id"] == "123456"
            assert payload["include_ads"] is True 