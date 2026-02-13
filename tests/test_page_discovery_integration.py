"""
Integration tests for page discovery functionality.
Tests the complete workflow from page discovery to ad creative creation.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import create_ad_creative, search_pages_by_name, get_account_pages


class TestPageDiscoveryIntegration:
    """Integration tests for page discovery functionality."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_page_discovery_in_create_ad_creative(self):
        """Test that create_ad_creative automatically discovers pages when no page_id is provided."""
        # Mock the page discovery to return a successful result
        mock_discovery_result = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
            "source": "tracking_specs"
        }
        
        # Mock the API request for creating the creative (will fail due to invalid image, but that's expected)
        mock_creative_response = {
            "error": {
                "message": "Invalid parameter",
                "type": "OAuthException",
                "code": 100,
                "error_subcode": 2446386,
                "error_user_title": "Image Not Found",
                "error_user_msg": "The image you selected is not available."
            }
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover, \
             patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            
            # Provide a valid access token to bypass authentication
            mock_get_token.return_value = "test_token_123"
            
            mock_discover.return_value = mock_discovery_result
            mock_api.return_value = mock_creative_response
            
            # Call create_ad_creative without providing page_id
            result = await create_ad_creative(
                account_id="act_123456789",
                name="Test Creative",
                image_hash="test_hash_123",
                message="Test message",
                access_token="test_token_123"  # Provide explicit token
            )
            
            result_data = json.loads(result)
            
            # Handle MCP wrapper - check if result is wrapped in 'data' field
            if "data" in result_data:
                actual_result = json.loads(result_data["data"])
            else:
                actual_result = result_data
            
            # Verify that the function attempted to create a creative (even though it failed due to invalid image)
            assert "error" in actual_result
            assert "Image Not Found" in actual_result["error"]["error_user_title"]
            
            # Verify that page discovery was called
            mock_discover.assert_called_once_with("act_123456789", "test_token_123")
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_integration(self):
        """Test the complete search_pages_by_name function with real-like data."""
        # Mock the page discovery to return a successful result
        mock_discovery_result = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Injury Payouts",
            "source": "tracking_specs"
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            
            # Provide a valid access token to bypass authentication
            mock_get_token.return_value = "test_token_123"
            
            mock_discover.return_value = mock_discovery_result
            
            # Test searching for pages
            result = await search_pages_by_name(
                account_id="act_123456789",
                search_term="Injury",
                access_token="test_token_123"  # Provide explicit token
            )
            
            result_data = json.loads(result)
            
            # Handle MCP wrapper - check if result is wrapped in 'data' field
            if "data" in result_data and isinstance(result_data["data"], str):
                actual_result = json.loads(result_data["data"])
            else:
                actual_result = result_data
            
            # Verify the search results
            assert len(actual_result["data"]) == 1
            assert actual_result["data"][0]["id"] == "123456789"
            assert actual_result["data"][0]["name"] == "Injury Payouts"
            assert actual_result["search_term"] == "Injury"
            assert actual_result["total_found"] == 1
            assert actual_result["total_available"] == 1
    
    @pytest.mark.asyncio
    async def test_create_ad_creative_with_manual_page_id(self):
        """Test that create_ad_creative works with manually provided page_id."""
        # Mock the API request for creating the creative
        mock_creative_response = {
            "error": {
                "message": "Invalid parameter",
                "type": "OAuthException",
                "code": 100,
                "error_subcode": 2446386,
                "error_user_title": "Image Not Found",
                "error_user_msg": "The image you selected is not available."
            }
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            
            # Provide a valid access token to bypass authentication
            mock_get_token.return_value = "test_token_123"
            
            mock_api.return_value = mock_creative_response
            
            # Call create_ad_creative with a manual page_id
            result = await create_ad_creative(
                account_id="act_123456789",
                name="Test Creative",
                image_hash="test_hash_123",
                page_id="123456789",  # Manual page ID
                message="Test message",
                access_token="test_token_123"  # Provide explicit token
            )
            
            result_data = json.loads(result)
            
            # Handle MCP wrapper - check if result is wrapped in 'data' field
            if "data" in result_data:
                actual_result = json.loads(result_data["data"])
            else:
                actual_result = result_data
            
            # Verify that the function attempted to create a creative
            assert "error" in actual_result
            assert "Image Not Found" in actual_result["error"]["error_user_title"]
            
            # Verify that make_api_request was called for creating the creative
            mock_api.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_ad_creative_no_pages_found(self):
        """Test create_ad_creative when no pages are found."""
        # Mock the page discovery to return no pages
        mock_discovery_result = {
            "success": False,
            "message": "No suitable pages found for this account"
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            
            # Provide a valid access token to bypass authentication
            mock_get_token.return_value = "test_token_123"
            
            mock_discover.return_value = mock_discovery_result
            
            # Call create_ad_creative without providing page_id
            result = await create_ad_creative(
                account_id="act_123456789",
                name="Test Creative",
                image_hash="test_hash_123",
                message="Test message",
                access_token="test_token_123"  # Provide explicit token
            )
            
            result_data = json.loads(result)
            
            # Handle MCP wrapper - check if result is wrapped in 'data' field
            if "data" in result_data:
                actual_result = json.loads(result_data["data"])
            else:
                actual_result = result_data
            
            # Verify that the function returned an error about no pages found
            assert "error" in actual_result
            assert "No page ID provided and no suitable pages found" in actual_result["error"]
            assert "suggestions" in actual_result
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_no_search_term(self):
        """Test search_pages_by_name without a search term (should return all pages)."""
        # Mock the page discovery to return a successful result
        mock_discovery_result = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
            "source": "tracking_specs"
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            
            # Provide a valid access token to bypass authentication
            mock_get_token.return_value = "test_token_123"
            
            mock_discover.return_value = mock_discovery_result
            
            # Test searching without a search term
            result = await search_pages_by_name(
                account_id="act_123456789",
                access_token="test_token_123"  # Provide explicit token
            )
            
            result_data = json.loads(result)
            
            # Handle MCP wrapper - check if result is wrapped in 'data' field
            if "data" in result_data and isinstance(result_data["data"], str):
                actual_result = json.loads(result_data["data"])
            else:
                actual_result = result_data
            
            # Verify the results
            assert len(actual_result["data"]) == 1
            assert actual_result["data"][0]["id"] == "123456789"
            assert actual_result["data"][0]["name"] == "Test Page"
            assert actual_result["total_available"] == 1
            assert "note" in actual_result
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_no_matches(self):
        """Test search_pages_by_name when no pages match the search term."""
        # Mock the page discovery to return a successful result
        mock_discovery_result = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
            "source": "tracking_specs"
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            
            # Provide a valid access token to bypass authentication
            mock_get_token.return_value = "test_token_123"
            
            mock_discover.return_value = mock_discovery_result
            
            # Test searching for a term that doesn't match
            result = await search_pages_by_name(
                account_id="act_123456789",
                search_term="Nonexistent",
                access_token="test_token_123"  # Provide explicit token
            )
            
            result_data = json.loads(result)
            
            # Handle MCP wrapper - check if result is wrapped in 'data' field
            if "data" in result_data and isinstance(result_data["data"], str):
                actual_result = json.loads(result_data["data"])
            else:
                actual_result = result_data
            
            # Verify that no pages were found
            assert len(actual_result["data"]) == 0
            assert actual_result["search_term"] == "Nonexistent"
            assert actual_result["total_found"] == 0
            assert actual_result["total_available"] == 1


if __name__ == "__main__":
    pytest.main([__file__]) 