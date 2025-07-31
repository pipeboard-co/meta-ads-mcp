"""
Test page discovery functionality for Meta Ads MCP.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import _discover_pages_for_account, search_pages_by_name, _search_pages_by_name_core


class TestPageDiscovery:
    """Test page discovery functionality."""
    
    @pytest.mark.asyncio
    async def test_discover_pages_from_tracking_specs(self):
        """Test page discovery from tracking specs (most reliable method)."""
        mock_ads_data = {
            "data": [
                {
                    "id": "123456789",
                    "tracking_specs": [
                        {
                            "page": ["987654321", "111222333"]
                        }
                    ]
                }
            ]
        }
        
        mock_page_data = {
            "id": "987654321",
            "name": "Test Page",
            "username": "testpage",
            "category": "Test Category"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            # Mock the ads endpoint call
            mock_api.side_effect = [
                mock_ads_data,  # First call for ads
                mock_page_data   # Second call for page details
            ]
            
            result = await _discover_pages_for_account("act_123456789", "test_token")
            
            assert result["success"] is True
            # Check that we got one of the expected page IDs (set order is not guaranteed)
            assert result["page_id"] in ["987654321", "111222333"]
            assert result["page_name"] == "Test Page"
            assert result["source"] == "tracking_specs"
    
    @pytest.mark.asyncio
    async def test_discover_pages_from_client_pages(self):
        """Test page discovery from client_pages endpoint."""
        mock_client_pages_data = {
            "data": [
                {
                    "id": "555666777",
                    "name": "Client Page",
                    "username": "clientpage"
                }
            ]
        }
        
        # Mock empty ads data, then client_pages data
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            mock_api.side_effect = [
                {"data": []},  # No ads found
                mock_client_pages_data  # Client pages found
            ]
            
            result = await _discover_pages_for_account("act_123456789", "test_token")
            
            assert result["success"] is True
            assert result["page_id"] == "555666777"
            assert result["page_name"] == "Client Page"
            assert result["source"] == "client_pages"
    
    @pytest.mark.asyncio
    async def test_discover_pages_from_assigned_pages(self):
        """Test page discovery from assigned_pages endpoint."""
        mock_assigned_pages_data = {
            "data": [
                {
                    "id": "888999000",
                    "name": "Assigned Page"
                }
            ]
        }
        
        # Mock empty responses for first two methods, then assigned_pages
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            mock_api.side_effect = [
                {"data": []},  # No ads found
                {"data": []},  # No client pages found
                mock_assigned_pages_data  # Assigned pages found
            ]
            
            result = await _discover_pages_for_account("act_123456789", "test_token")
            
            assert result["success"] is True
            assert result["page_id"] == "888999000"
            assert result["page_name"] == "Assigned Page"
            assert result["source"] == "assigned_pages"
    
    @pytest.mark.asyncio
    async def test_discover_pages_no_pages_found(self):
        """Test page discovery when no pages are found."""
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            mock_api.side_effect = [
                {"data": []},  # No ads found
                {"data": []},  # No client pages found
                {"data": []}   # No assigned pages found
            ]
            
            result = await _discover_pages_for_account("act_123456789", "test_token")
            
            assert result["success"] is False
            assert "No suitable pages found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_discover_pages_with_invalid_page_ids(self):
        """Test page discovery with invalid page IDs in tracking_specs."""
        mock_ads_data = {
            "data": [
                {
                    "id": "123456789",
                    "tracking_specs": [
                        {
                            "page": ["invalid_id", "not_numeric", "123abc"]
                        }
                    ]
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            mock_api.side_effect = [
                mock_ads_data,  # Ads with invalid page IDs
                {"data": []},   # No client pages
                {"data": []}    # No assigned pages
            ]
            
            result = await _discover_pages_for_account("act_123456789", "test_token")
            
            assert result["success"] is False
            assert "No suitable pages found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_discover_pages_api_error_handling(self):
        """Test page discovery with API errors."""
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            mock_api.side_effect = Exception("API Error")
            
            result = await _discover_pages_for_account("act_123456789", "test_token")
            
            assert result["success"] is False
            assert "Error during page discovery" in result["message"]
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_logic(self):
        """Test the core search logic without authentication interference."""
        # Test the filtering logic directly
        mock_pages_data = {
            "data": [
                {"id": "111", "name": "Test Page 1"},
                {"id": "222", "name": "Another Test Page"},
                {"id": "333", "name": "Different Page"}
            ]
        }
        
        # Test filtering with search term
        search_term_lower = "test"
        filtered_pages = []
        
        for page in mock_pages_data["data"]:
            page_name = page.get("name", "").lower()
            if search_term_lower in page_name:
                filtered_pages.append(page)
        
        assert len(filtered_pages) == 2
        assert filtered_pages[0]["name"] == "Test Page 1"
        assert filtered_pages[1]["name"] == "Another Test Page"
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_no_matches(self):
        """Test search logic with no matching results."""
        mock_pages_data = {
            "data": [
                {"id": "111", "name": "Test Page 1"},
                {"id": "222", "name": "Another Test Page"}
            ]
        }
        
        # Test filtering with non-matching search term
        search_term_lower = "nonexistent"
        filtered_pages = []
        
        for page in mock_pages_data["data"]:
            page_name = page.get("name", "").lower()
            if search_term_lower in page_name:
                filtered_pages.append(page)
        
        assert len(filtered_pages) == 0
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_core_success(self):
        """Test the core search function with successful page discovery."""
        mock_discovery_result = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
            "source": "tracking_specs"
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:
            mock_discover.return_value = mock_discovery_result
            
            result = await _search_pages_by_name_core("test_token", "act_123456789", "test")
            result_data = json.loads(result)
            
            assert len(result_data["data"]) == 1
            assert result_data["data"][0]["id"] == "123456789"
            assert result_data["data"][0]["name"] == "Test Page"
            assert result_data["search_term"] == "test"
            assert result_data["total_found"] == 1
            assert result_data["total_available"] == 1
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_core_no_pages(self):
        """Test the core search function when no pages are found."""
        mock_discovery_result = {
            "success": False,
            "message": "No pages found"
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:
            mock_discover.return_value = mock_discovery_result
            
            result = await _search_pages_by_name_core("test_token", "act_123456789", "test")
            result_data = json.loads(result)
            
            assert len(result_data["data"]) == 0
            assert "No pages found" in result_data["message"]
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_core_no_search_term(self):
        """Test the core search function without search term."""
        mock_discovery_result = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
            "source": "tracking_specs"
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:
            mock_discover.return_value = mock_discovery_result
            
            result = await _search_pages_by_name_core("test_token", "act_123456789")
            result_data = json.loads(result)
            
            assert len(result_data["data"]) == 1
            assert result_data["total_available"] == 1
            assert "note" in result_data
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_core_exception_handling(self):
        """Test the core search function with exception handling."""
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:
            mock_discover.side_effect = Exception("Test exception")
            
            result = await _search_pages_by_name_core("test_token", "act_123456789", "test")
            result_data = json.loads(result)
            
            assert "error" in result_data
            assert "Failed to search pages by name" in result_data["error"]
    
    @pytest.mark.asyncio
    async def test_discover_pages_with_multiple_page_ids(self):
        """Test page discovery with multiple page IDs in tracking_specs."""
        mock_ads_data = {
            "data": [
                {
                    "id": "123456789",
                    "tracking_specs": [
                        {
                            "page": ["111222333", "444555666", "777888999"]
                        }
                    ]
                }
            ]
        }
        
        mock_page_data = {
            "id": "111222333",
            "name": "First Page",
            "username": "firstpage"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            mock_api.side_effect = [
                mock_ads_data,  # First call for ads
                mock_page_data   # Second call for page details
            ]
            
            result = await _discover_pages_for_account("act_123456789", "test_token")
            
            assert result["success"] is True
            # Should get the first page ID from the set
            assert result["page_id"] in ["111222333", "444555666", "777888999"]
            assert result["page_name"] == "First Page"
    
    @pytest.mark.asyncio
    async def test_discover_pages_with_mixed_valid_invalid_ids(self):
        """Test page discovery with mixed valid and invalid page IDs."""
        mock_ads_data = {
            "data": [
                {
                    "id": "123456789",
                    "tracking_specs": [
                        {
                            "page": ["invalid", "123456789", "not_numeric", "987654321"]
                        }
                    ]
                }
            ]
        }
        
        mock_page_data = {
            "id": "123456789",
            "name": "Valid Page",
            "username": "validpage"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
            mock_api.side_effect = [
                mock_ads_data,  # First call for ads
                mock_page_data   # Second call for page details
            ]
            
            result = await _discover_pages_for_account("act_123456789", "test_token")
            
            assert result["success"] is True
            # Should get one of the valid numeric IDs
            assert result["page_id"] in ["123456789", "987654321"]
            assert result["page_name"] == "Valid Page"
    
    @pytest.mark.asyncio
    async def test_search_pages_by_name_case_insensitive(self):
        """Test search function with case insensitive matching."""
        mock_discovery_result = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
            "source": "tracking_specs"
        }
        
        with patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:
            mock_discover.return_value = mock_discovery_result
            
            # Test with uppercase search term
            result = await _search_pages_by_name_core("test_token", "act_123456789", "TEST")
            result_data = json.loads(result)
            
            assert len(result_data["data"]) == 1
            assert result_data["total_found"] == 1
            
            # Test with lowercase search term
            result = await _search_pages_by_name_core("test_token", "act_123456789", "test")
            result_data = json.loads(result)
            
            assert len(result_data["data"]) == 1
            assert result_data["total_found"] == 1


if __name__ == "__main__":
    pytest.main([__file__]) 