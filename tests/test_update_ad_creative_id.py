"""Tests for update_ad function with creative_id parameter.

Tests for the enhanced update_ad function that supports:
- Updating ad creative via creative_id parameter
- Combining creative updates with other parameters (status, bid_amount, tracking_specs)
- Error handling for invalid creative_id values
- Validation of creative permissions and compatibility
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import update_ad


@pytest.mark.asyncio
class TestUpdateAdCreativeId:
    """Test cases for update_ad function with creative_id parameter."""
    
    async def test_update_ad_creative_id_success(self):
        """Test successfully updating ad with new creative_id."""
        
        sample_response = {
            "success": True,
            "id": "test_ad_123"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_response
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="new_creative_456",
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            assert "success" in result_data
            assert result_data["success"] is True
            
            # Verify API was called with correct parameters
            mock_api.assert_called_once()
            call_args = mock_api.call_args
            
            # Check endpoint
            assert call_args[0][0] == "test_ad_123"
            
            # Check parameters
            params = call_args[0][2]  # Third argument is params
            assert "creative" in params
            creative_data = json.loads(params["creative"])
            assert creative_data["creative_id"] == "new_creative_456"
    
    async def test_update_ad_creative_id_with_other_params(self):
        """Test updating creative_id along with status and bid_amount."""
        
        sample_response = {
            "success": True,
            "id": "test_ad_123"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_response
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="new_creative_456",
                status="ACTIVE",
                bid_amount=150,
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            assert "success" in result_data
            assert result_data["success"] is True
            
            # Verify API was called with all parameters
            mock_api.assert_called_once()
            call_args = mock_api.call_args
            params = call_args[0][2]
            
            assert "creative" in params
            assert "status" in params
            assert "bid_amount" in params
            
            creative_data = json.loads(params["creative"])
            assert creative_data["creative_id"] == "new_creative_456"
            assert params["status"] == "ACTIVE"
            assert params["bid_amount"] == "150"
    
    async def test_update_ad_creative_id_with_tracking_specs(self):
        """Test updating creative_id along with tracking_specs."""
        
        sample_response = {
            "success": True,
            "id": "test_ad_123"
        }
        
        tracking_specs = [{"action.type": "offsite_conversion", "fb_pixel": ["123456"]}]
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_response
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="new_creative_456",
                tracking_specs=tracking_specs,
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            assert "success" in result_data
            assert result_data["success"] is True
            
            # Verify API was called with all parameters
            mock_api.assert_called_once()
            call_args = mock_api.call_args
            params = call_args[0][2]
            
            assert "creative" in params
            assert "tracking_specs" in params
            
            creative_data = json.loads(params["creative"])
            assert creative_data["creative_id"] == "new_creative_456"
            
            # tracking_specs should be JSON encoded
            tracking_data = json.loads(params["tracking_specs"])
            assert tracking_data == tracking_specs
    
    async def test_update_ad_invalid_creative_id(self):
        """Test updating ad with invalid creative_id."""
        
        # Simulate API error for invalid creative_id
        api_error = {
            "error": {
                "message": "Invalid creative ID",
                "type": "OAuthException",
                "code": 100
            }
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = api_error
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="invalid_creative_999",
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            # The error might be wrapped in a 'data' field per the memory
            if "data" in result_data:
                error_data = json.loads(result_data["data"])
                assert "error" in error_data
            else:
                assert "error" in result_data
    
    async def test_update_ad_nonexistent_creative_id(self):
        """Test updating ad with non-existent creative_id."""
        
        # Simulate API error for non-existent creative_id
        api_error = {
            "error": {
                "message": "Creative does not exist",
                "type": "OAuthException",
                "code": 803
            }
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = api_error
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="nonexistent_creative_999",
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            # The error might be wrapped in a 'data' field per the memory
            if "data" in result_data:
                error_data = json.loads(result_data["data"])
                assert "error" in error_data
            else:
                assert "error" in result_data
    
    async def test_update_ad_creative_id_from_different_account(self):
        """Test updating ad with creative_id from different account."""
        
        # Simulate API error for cross-account creative access
        api_error = {
            "error": {
                "message": "Creative does not belong to this account",
                "type": "OAuthException",
                "code": 200
            }
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = api_error
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="other_account_creative_456",
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            # The error might be wrapped in a 'data' field per the memory
            if "data" in result_data:
                error_data = json.loads(result_data["data"])
                assert "error" in error_data
            else:
                assert "error" in result_data
    
    async def test_update_ad_no_parameters(self):
        """Test update_ad with no parameters provided."""
        
        result = await update_ad(
            ad_id="test_ad_123",
            access_token="test_token"
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "No update parameters provided" in error_data["error"]
        else:
            assert "error" in result_data
            assert "No update parameters provided" in result_data["error"]
    
    async def test_update_ad_missing_ad_id(self):
        """Test update_ad with missing ad_id."""
        
        result = await update_ad(
            ad_id="",
            creative_id="new_creative_456",
            access_token="test_token"
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Ad ID is required" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Ad ID is required" in result_data["error"]
    
    async def test_update_ad_creative_id_only(self):
        """Test updating only the creative_id without other parameters."""
        
        sample_response = {
            "success": True,
            "id": "test_ad_123"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_response
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="new_creative_456",
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            assert "success" in result_data
            assert result_data["success"] is True
            
            # Verify API was called with only creative parameter
            mock_api.assert_called_once()
            call_args = mock_api.call_args
            params = call_args[0][2]
            
            # Should only have creative parameter, no status or bid_amount
            assert "creative" in params
            assert "status" not in params
            assert "bid_amount" not in params
            assert "tracking_specs" not in params
            
            creative_data = json.loads(params["creative"])
            assert creative_data["creative_id"] == "new_creative_456"
    
    async def test_update_ad_creative_compatibility_validation(self):
        """Test creative compatibility validation with different creative types."""
        
        # This test simulates an API error for incompatible creative types
        api_error = {
            "error": {
                "message": "Creative format not compatible with ad set placement",
                "type": "OAuthException",
                "code": 1487
            }
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = api_error
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="incompatible_creative_456",
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            # The error might be wrapped in a 'data' field per the memory
            if "data" in result_data:
                error_data = json.loads(result_data["data"])
                assert "error" in error_data
            else:
                assert "error" in result_data
    
    async def test_update_ad_api_error_handling(self):
        """Test general API error handling for update_ad."""
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            # Simulate API request throwing an exception
            mock_api.side_effect = Exception("API connection failed")
            
            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="new_creative_456",
                access_token="test_token"
            )
            
            result_data = json.loads(result)
            # The error might be wrapped in a 'data' field
            if "data" in result_data:
                error_data = json.loads(result_data["data"])
                assert "error" in error_data
                assert "API connection failed" in error_data["error"]
            else:
                assert "error" in result_data
                assert "API connection failed" in result_data["error"]