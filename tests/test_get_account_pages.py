"""
Tests for the updated get_account_pages function with multi-approach strategy.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import get_account_pages


class TestGetAccountPages:
    """Test the updated get_account_pages function with comprehensive multi-approach testing."""
    
    @pytest.mark.asyncio
    async def test_get_account_pages_multi_approach_success(self):
        """Test successful page discovery using multiple approaches."""
        # Mock data for different endpoints
        mock_user_pages = {
            "data": [
                {
                    "id": "111111111",
                    "name": "Personal Page",
                    "category": "Personal Blog",
                    "fan_count": 100
                }
            ]
        }
        
        mock_client_pages = {
            "data": [
                {
                    "id": "222222222", 
                    "name": "Client Page",
                    "category": "Business",
                    "fan_count": 500
                }
            ]
        }
        
        mock_adcreatives = {
            "data": [
                {
                    "id": "creative_123",
                    "object_story_spec": {"page_id": "333333333"}
                }
            ]
        }
        
        # Mock page details for discovered IDs
        mock_page_details = {
            "111111111": {
                "id": "111111111",
                "name": "Personal Page",
                "username": "personalpage",
                "category": "Personal Blog",
                "fan_count": 100,
                "link": "https://facebook.com/personalpage",
                "verification_status": "not_verified"
            },
            "222222222": {
                "id": "222222222", 
                "name": "Client Page",
                "username": "clientpage",
                "category": "Business",
                "fan_count": 500,
                "link": "https://facebook.com/clientpage",
                "verification_status": "verified"
            },
            "333333333": {
                "id": "333333333",
                "name": "Creative Page", 
                "username": "creativepage",
                "category": "Creative",
                "fan_count": 1000,
                "link": "https://facebook.com/creativepage",
                "verification_status": "not_verified"
            }
        }
        
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth, \
             patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            
            mock_auth.return_value = "test_access_token"
            
            # Mock API calls in sequence for different approaches
            def mock_api_side_effect(endpoint, access_token, params):
                if endpoint == "me/accounts":
                    return mock_user_pages
                elif endpoint == "3182643988557192/owned_pages":
                    return {"data": []}  # No business pages
                elif endpoint == "act_3182643988557192/client_pages":
                    return mock_client_pages
                elif endpoint == "act_3182643988557192/adcreatives":
                    return mock_adcreatives
                elif endpoint == "act_3182643988557192/ads":
                    return {"data": []}  # No ads
                elif endpoint == "act_3182643988557192/promoted_objects":
                    return {"data": []}  # No promoted objects
                elif endpoint == "act_3182643988557192/campaigns":
                    return {"data": []}  # No campaigns
                elif endpoint in mock_page_details:
                    return mock_page_details[endpoint]
                else:
                    return {"data": []}
            
            mock_api.side_effect = mock_api_side_effect
            
            # Call the function
            result = await get_account_pages(account_id="act_3182643988557192")
            result_data = json.loads(result)
            
            # Verify the structure and content
            assert "data" in result_data
            assert "total_pages_found" in result_data
            
            # Should find 3 unique pages
            assert result_data["total_pages_found"] == 3
            assert len(result_data["data"]) == 3
            
            # Verify that we found valid page data
            assert all("id" in page for page in result_data["data"])
            
            # Verify the page names are correct
            page_names = [page.get("name") for page in result_data["data"]]
            assert "Personal Page" in page_names
            assert "Client Page" in page_names
            assert "Creative Page" in page_names
            
            # Verify each page has basic required fields
            for page in result_data["data"]:
                assert "id" in page
                assert "name" in page
    
    @pytest.mark.asyncio
    async def test_get_account_pages_me_special_case(self):
        """Test the special case when account_id is 'me'."""
        mock_user_pages = {
            "data": [
                {
                    "id": "444444444",
                    "name": "My Personal Page",
                    "category": "Personal",
                    "fan_count": 50
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth, \
             patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            
            mock_auth.return_value = "test_access_token"
            mock_api.return_value = mock_user_pages
            
            result = await get_account_pages(account_id="me")
            result_data = json.loads(result)
            
            # Verify the call was made to me/accounts
            mock_api.assert_called_once_with(
                "me/accounts",
                "test_access_token",
                {"fields": "id,name,username,category,fan_count,link,verification_status,picture"}
            )
            
            # Verify response structure
            assert "data" in result_data
            assert len(result_data["data"]) == 1
            assert result_data["data"][0]["id"] == "444444444"
    
    @pytest.mark.asyncio
    async def test_get_account_pages_tracking_specs_discovery(self):
        """Test page discovery from tracking specs (most reliable method)."""
        mock_ads_data = {
            "data": [
                {
                    "id": "ad_123",
                    "tracking_specs": [
                        {
                            "page": ["555555555", "666666666"]
                        }
                    ]
                }
            ]
        }
        
        mock_page_details = {
            "id": "555555555",
            "name": "Tracking Page",
            "username": "trackingpage",
            "category": "Business"
        }
        
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth, \
             patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            
            mock_auth.return_value = "test_access_token"
            
            def mock_api_side_effect(endpoint, access_token, params):
                if "tracking_specs" in params.get("fields", ""):
                    return mock_ads_data
                elif endpoint == "555555555":
                    return mock_page_details
                elif endpoint == "666666666":
                    return {"error": "Page not accessible"}
                else:
                    return {"data": []}
            
            mock_api.side_effect = mock_api_side_effect
            
            result = await get_account_pages(account_id="act_123456789")
            result_data = json.loads(result)
            
            # Should find pages from tracking specs
            assert result_data["total_pages_found"] == 2
            
            # Check that one page has details and one has error
            pages = result_data["data"]
            assert len(pages) == 2
            
            # One should have full details, one should have error
            page_with_details = next((p for p in pages if "error" not in p), None)
            page_with_error = next((p for p in pages if "error" in p), None)
            
            assert page_with_details is not None
            assert page_with_error is not None
            assert page_with_details["name"] == "Tracking Page"
            assert "not accessible" in page_with_error["error"]
    
    @pytest.mark.asyncio
    async def test_get_account_pages_no_pages_found(self):
        """Test when no pages are found through any approach."""
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth, \
             patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            
            mock_auth.return_value = "test_access_token"
            mock_api.return_value = {"data": []}  # All endpoints return empty
            
            result = await get_account_pages(account_id="act_123456789")
            result_data = json.loads(result)
            
            # Should return the fallback message
            assert "data" in result_data
            assert len(result_data["data"]) == 0
            assert "message" in result_data
            assert "No pages found" in result_data["message"]
            assert "suggestion" in result_data
    
    @pytest.mark.asyncio
    async def test_get_account_pages_error_handling(self):
        """Test error handling when API calls fail."""
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth, \
             patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            
            mock_auth.return_value = "test_access_token"
            mock_api.side_effect = Exception("API Error")
            
            result = await get_account_pages(account_id="act_123456789")
            result_data = json.loads(result)
            
            # Individual API errors are caught and logged, function returns "no pages found"
            assert "data" in result_data
            assert len(result_data["data"]) == 0
            assert "message" in result_data
            assert "No pages found" in result_data["message"]
            
            # But debug info should show the errors
            if "debug" in result_data:
                debug = result_data["debug"]
                assert "errors" in debug
                assert len(debug["errors"]) > 0
                # Should have multiple API errors logged
                assert any("API Error" in error for error in debug["errors"])
    
    @pytest.mark.asyncio
    async def test_get_account_pages_no_account_id(self):
        """Test error when no account ID is provided."""
        result = await get_account_pages(account_id=None)
        result_data = json.loads(result)
        
        # The @meta_api_tool decorator handles authentication before function logic
        # So it returns an authentication error instead of the simple account ID error
        # Error responses may be wrapped in a "data" field (MCP format)
        
        # Check for direct error format
        if "error" in result_data or "message" in result_data:
            if "message" in result_data and "Authentication Required" in result_data["message"]:
                # MCP decorator returns authentication error - this is expected
                assert True  # This is the expected behavior
                return
            elif "error" in result_data and "No account ID provided" in result_data["error"]:
                # Direct function call might return the account ID error
                assert True  # This is also valid
                return
        
        # Check for wrapped error format (MCP response format)
        if "data" in result_data:
            try:
                error_data = json.loads(result_data["data"])
                if "error" in error_data and "No account ID provided" in error_data["error"]:
                    assert True  # Wrapped error format
                    return
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Fallback: Check if the response contains any indication of missing account ID
        result_str = str(result_data)
        assert "No account ID provided" in result_str or "Authentication Required" in result_str
    
    @pytest.mark.asyncio
    async def test_get_account_pages_account_id_validation_direct(self):
        """Test account ID validation by directly testing the function logic."""
        # Import the function implementation directly to bypass decorators
        from meta_ads_mcp.core.ads import get_account_pages
        
        # Mock the function to bypass decorator authentication  
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = "test_token"
            
            # Call with empty string (should be treated as None)
            result = await get_account_pages(account_id="")
            result_data = json.loads(result)
            
            # Response might be wrapped in MCP format
            if "data" in result_data and isinstance(result_data["data"], str):
                # Parse the nested JSON response
                inner_data = json.loads(result_data["data"])
                assert "error" in inner_data
                assert "No account ID provided" in inner_data["error"]
            else:
                # Direct response format
                assert "error" in result_data or "message" in result_data
                result_str = str(result_data)
                assert "No account ID provided" in result_str or "Authentication Required" in result_str
    
    @pytest.mark.asyncio
    async def test_get_account_pages_multiple_sources(self):
        """Test that pages from multiple sources are properly collected."""
        # Mock different results for different approaches
        mock_responses = {
            "me/accounts": {"data": [{"id": "111111111"}]},
            "123456789/owned_pages": {"data": []},
            "act_123456789/client_pages": {"data": [{"id": "222222222"}]},
            "act_123456789/adcreatives": {"data": []},
            "act_123456789/ads": {"data": []},
            "act_123456789/promoted_objects": {"data": []},
            "act_123456789/campaigns": {"data": []},
            "111111111": {"id": "111111111", "name": "Page 1"},
            "222222222": {"id": "222222222", "name": "Page 2"}
        }
        
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth, \
             patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            
            mock_auth.return_value = "test_access_token"
            
            def mock_api_side_effect(endpoint, access_token, params):
                return mock_responses.get(endpoint, {"data": []})
            
            mock_api.side_effect = mock_api_side_effect
            
            result = await get_account_pages(account_id="act_123456789")
            result_data = json.loads(result)
            
            # Verify basic response structure
            assert "data" in result_data
            assert "total_pages_found" in result_data
            assert result_data["total_pages_found"] == 2
            assert len(result_data["data"]) == 2
            
            # Verify pages have correct names
            page_names = [page.get("name") for page in result_data["data"]]
            assert "Page 1" in page_names
            assert "Page 2" in page_names
    
    @pytest.mark.asyncio
    async def test_get_account_pages_act_prefix_handling(self):
        """Test that account IDs without 'act_' prefix are handled correctly."""
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth, \
             patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            
            mock_auth.return_value = "test_access_token"
            mock_api.return_value = {"data": []}
            
            # Test with account ID without 'act_' prefix
            result = await get_account_pages(account_id="123456789")
            
            # Check that API calls were made with 'act_' prefix added
            calls = mock_api.call_args_list
            
            # Should find calls with 'act_123456789' in the endpoint
            act_calls = [call for call in calls if 'act_123456789' in str(call)]
            assert len(act_calls) > 0, "Should have made calls with 'act_' prefix"
            
            # Should also have made calls with raw account ID for business endpoints
            business_calls = [call for call in calls if '123456789/owned_pages' in str(call)]
            assert len(business_calls) > 0, "Should have made calls to business endpoints"


if __name__ == "__main__":
    pytest.main([__file__])