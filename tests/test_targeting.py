#!/usr/bin/env python3
"""
Unit tests for targeting search functionality in Meta Ads MCP.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.targeting import (
    search_interests,
    get_interest_suggestions,
    estimate_audience_size,
    search_behaviors,
    search_demographics,
    search_geo_locations
)


class TestSearchInterests:
    """Test cases for search_interests function"""
    
    @pytest.mark.asyncio
    async def test_search_interests_success(self):
        """Test successful interest search"""
        mock_response = {
            "data": [
                {
                    "id": "6003139266461",
                    "name": "Movies",
                    "audience_size": 1234567890,
                    "path": ["Entertainment", "Movies"]
                },
                {
                    "id": "6003397425735", 
                    "name": "Tennis",
                    "audience_size": 987654321,
                    "path": ["Sports", "Tennis"]
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await search_interests(access_token="test_token", query="movies", limit=10)
            
            # Verify API call
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adinterest",
                    "q": "movies",
                    "limit": 10
                }
            )
            
            # Verify response
            result_data = json.loads(result)
            assert result_data == mock_response
            assert len(result_data["data"]) == 2
            assert result_data["data"][0]["name"] == "Movies"
    
    @pytest.mark.asyncio
    async def test_search_interests_no_query(self):
        """Test search_interests with empty query parameter"""
        result = await search_interests(
            query="",  # Now provide the required parameter but with empty value
            access_token="test_token"
        )
        
        result_data = json.loads(result)
        # The @meta_api_tool decorator wraps errors in a 'data' field
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert "error" in nested_data
        assert nested_data["error"] == "No search query provided"
    
    @pytest.mark.asyncio
    async def test_search_interests_default_limit(self):
        """Test search_interests with default limit"""
        mock_response = {"data": []}
        
        # Mock both the API request and the auth system to bypass decorator issues
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_auth:
                mock_auth.return_value = "test_token"
                mock_api.return_value = mock_response
                
                result = await search_interests(query="test")
                
                # Verify default limit is used
                mock_api.assert_called_once_with(
                    "search",
                    "test_token",
                    {
                        "type": "adinterest",
                        "q": "test",
                        "limit": 25
                    }
                )
                
                # Verify the result is properly formatted
                result_data = json.loads(result)
                assert "data" in result_data


class TestGetInterestSuggestions:
    """Test cases for get_interest_suggestions function"""
    
    @pytest.mark.asyncio
    async def test_get_interest_suggestions_success(self):
        """Test successful interest suggestions"""
        mock_response = {
            "data": [
                {
                    "id": "6003022269556",
                    "name": "Rugby football",
                    "audience_size": 13214830,
                    "path": [],
                    "description": None
                },
                {
                    "id": "6003146664949",
                    "name": "Netball", 
                    "audience_size": 4333770,
                    "path": [],
                    "description": None
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await get_interest_suggestions(
                access_token="test_token",
                interest_list=["Basketball", "Soccer"],
                limit=15
            )
            
            # Verify API call
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adinterestsuggestion",
                    "interest_list": '["Basketball", "Soccer"]',
                    "limit": 15
                }
            )
            
            # Verify response
            result_data = json.loads(result)
            assert result_data == mock_response
            assert len(result_data["data"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_interest_suggestions_no_list(self):
        """Test get_interest_suggestions with empty interest list"""
        result = await get_interest_suggestions(
            interest_list=[],  # Now provide the required parameter but with empty value
            access_token="test_token"
        )
        
        result_data = json.loads(result)
        # The @meta_api_tool decorator wraps errors in a 'data' field
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert "error" in nested_data
        assert nested_data["error"] == "No interest list provided"


class TestEstimateAudienceSizeBackwardsCompatibility:
    """Test cases for estimate_audience_size function backwards compatibility"""
    
    @pytest.mark.asyncio
    async def test_validate_interests_by_name_success(self):
        """Test successful interest validation by name"""
        mock_response = {
            "data": [
                {
                    "name": "Japan",
                    "valid": True,
                    "id": 6003700426513,
                    "audience_size": 68310258
                },
                {
                    "name": "nonexistantkeyword",
                    "valid": False
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await estimate_audience_size(
                access_token="test_token",
                interest_list=["Japan", "nonexistantkeyword"]
            )
            
            # Verify API call
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adinterestvalid",
                    "interest_list": '["Japan", "nonexistantkeyword"]'
                }
            )
            
            # Verify response
            result_data = json.loads(result)
            assert result_data == mock_response
            assert result_data["data"][0]["valid"] is True
            assert result_data["data"][1]["valid"] is False
    
    @pytest.mark.asyncio
    async def test_validate_interests_by_fbid_success(self):
        """Test successful interest validation by FBID"""
        mock_response = {
            "data": [
                {
                    "id": "6003700426513",
                    "valid": True,
                    "audience_size": 68310258
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await estimate_audience_size(
                access_token="test_token",
                interest_fbid_list=["6003700426513"]
            )
            
            # Verify API call
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adinterestvalid",
                    "interest_fbid_list": '["6003700426513"]'
                }
            )
            
            # Verify response
            result_data = json.loads(result)
            assert result_data == mock_response
    
    @pytest.mark.asyncio
    async def test_validate_interests_no_input(self):
        """Test estimate_audience_size with no input lists (backwards compatibility)"""
        result = await estimate_audience_size(access_token="test_token")
        
        result_data = json.loads(result)
        # The @meta_api_tool decorator wraps errors in a 'data' field
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert "error" in nested_data
        assert nested_data["error"] == "No interest list or FBID list provided"


class TestSearchBehaviors:
    """Test cases for search_behaviors function"""
    
    @pytest.mark.asyncio
    async def test_search_behaviors_success(self):
        """Test successful behavior search"""
        mock_response = {
            "data": [
                {
                    "id": 6007101597783,
                    "name": "Business Travelers",
                    "audience_size_lower_bound": 1000000,
                    "audience_size_upper_bound": 2000000,
                    "path": ["Travel", "Business Travel"],
                    "description": "People who travel for business",
                    "type": "behaviors"
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await search_behaviors(access_token="test_token", limit=25)
            
            # Verify API call
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adTargetingCategory",
                    "class": "behaviors",
                    "limit": 25
                }
            )
            
            # Verify response
            result_data = json.loads(result)
            assert result_data == mock_response


class TestSearchDemographics:
    """Test cases for search_demographics function"""
    
    @pytest.mark.asyncio
    async def test_search_demographics_success(self):
        """Test successful demographics search"""
        mock_response = {
            "data": [
                {
                    "id": 6015559470583,
                    "name": "Parents (All)",
                    "audience_size_lower_bound": 500000000,
                    "audience_size_upper_bound": 750000000,
                    "path": ["Family", "Parents"],
                    "description": "Parents of children of any age",
                    "type": "demographics"
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await search_demographics(
                access_token="test_token",
                demographic_class="life_events",
                limit=30
            )
            
            # Verify API call
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adTargetingCategory",
                    "class": "life_events",
                    "limit": 30
                }
            )
            
            # Verify response
            result_data = json.loads(result)
            assert result_data == mock_response


class TestSearchGeoLocations:
    """Test cases for search_geo_locations function"""
    
    @pytest.mark.asyncio
    async def test_search_geo_locations_success(self):
        """Test successful geo location search"""
        mock_response = {
            "data": [
                {
                    "key": "US",
                    "name": "United States",
                    "type": "country",
                    "supports_city": True,
                    "supports_region": True
                },
                {
                    "key": "3847",
                    "name": "California",
                    "type": "region",
                    "country_code": "US",
                    "country_name": "United States",
                    "supports_city": True,
                    "supports_region": True
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await search_geo_locations(
                access_token="test_token",
                query="United States",
                location_types=["country", "region"],
                limit=10
            )
            
            # Verify API call
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adgeolocation",
                    "q": "United States",
                    "location_types": '["country", "region"]',
                    "limit": 10
                }
            )
            
            # Verify response
            result_data = json.loads(result)
            assert result_data == mock_response
    
    @pytest.mark.asyncio
    async def test_search_geo_locations_no_query(self):
        """Test search_geo_locations with empty query"""
        result = await search_geo_locations(
            query="",  # Now provide the required parameter but with empty value
            access_token="test_token"
        )
        
        result_data = json.loads(result)
        # The @meta_api_tool decorator wraps errors in a 'data' field
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert "error" in nested_data
        assert nested_data["error"] == "No search query provided"
    
    @pytest.mark.asyncio
    async def test_search_geo_locations_no_location_types(self):
        """Test search_geo_locations without location_types filter"""
        mock_response = {"data": []}
        
        # Mock both the API request and the auth system to bypass decorator issues
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_auth:
                mock_auth.return_value = "test_token"
                mock_api.return_value = mock_response
                
                result = await search_geo_locations(query="test")
                
                # Verify API call doesn't include location_types
                mock_api.assert_called_once_with(
                    "search",
                    "test_token",
                    {
                        "type": "adgeolocation",
                        "q": "test",
                        "limit": 25
                    }
                )
                
                # Verify the result is properly formatted
                result_data = json.loads(result)
                assert "data" in result_data 