"""Test pagination functionality for insights endpoint."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.insights import get_insights


class TestInsightsPagination:
    """Test suite for pagination functionality in get_insights"""

    @pytest.fixture
    def mock_auth_manager(self):
        """Mock for the authentication manager"""
        with patch('meta_ads_mcp.core.api.auth_manager') as mock, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            # Mock a valid access token
            mock.get_current_access_token.return_value = "test_access_token"
            mock.is_token_valid.return_value = True
            mock.app_id = "test_app_id"
            mock_get_token.return_value = "test_access_token"
            yield mock

    @pytest.fixture
    def valid_account_id(self):
        return "act_701351919139047"

    @pytest.fixture
    def mock_paginated_response_page1(self):
        """Mock first page of paginated response"""
        return {
            "data": [
                {
                    "campaign_id": "campaign_1",
                    "campaign_name": "Test Campaign 1",
                    "spend": "100.50",
                    "impressions": "1000",
                    "clicks": "50"
                },
                {
                    "campaign_id": "campaign_2", 
                    "campaign_name": "Test Campaign 2",
                    "spend": "200.75",
                    "impressions": "2000",
                    "clicks": "100"
                }
            ],
            "paging": {
                "cursors": {
                    "before": "before_cursor_1",
                    "after": "after_cursor_1"
                },
                "next": "https://graph.facebook.com/v20.0/act_123/insights?after=after_cursor_1&limit=2"
            }
        }

    @pytest.fixture
    def mock_paginated_response_page2(self):
        """Mock second page of paginated response"""
        return {
            "data": [
                {
                    "campaign_id": "campaign_3",
                    "campaign_name": "Test Campaign 3", 
                    "spend": "150.25",
                    "impressions": "1500",
                    "clicks": "75"
                }
            ],
            "paging": {
                "cursors": {
                    "before": "before_cursor_2",
                    "after": "after_cursor_2"
                }
            }
        }

    @pytest.mark.asyncio
    async def test_insights_with_limit_parameter(self, mock_auth_manager, valid_account_id, mock_paginated_response_page1):
        """Test that limit parameter is properly passed to API"""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_paginated_response_page1

            result = await get_insights(
                object_id=valid_account_id,
                level="campaign",
                time_range="last_30d",
                limit=2
            )

            # Verify the API was called with correct parameters
            mock_api_request.assert_called_once()
            call_args = mock_api_request.call_args
            
            # Check that limit is included in params
            params = call_args[0][2]
            assert params["limit"] == 2
            assert params["level"] == "campaign"
            assert params["date_preset"] == "last_30d"

            # Verify the response structure
            result_data = json.loads(result)
            assert "data" in result_data
            assert len(result_data["data"]) == 2
            assert "paging" in result_data

    @pytest.mark.asyncio
    async def test_insights_with_after_cursor(self, mock_auth_manager, valid_account_id, mock_paginated_response_page2):
        """Test that after cursor is properly passed to API for pagination"""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_paginated_response_page2

            after_cursor = "after_cursor_1"
            result = await get_insights(
                object_id=valid_account_id,
                level="campaign",
                time_range="last_30d",
                limit=10,
                after=after_cursor
            )

            # Verify the API was called with correct parameters
            mock_api_request.assert_called_once()
            call_args = mock_api_request.call_args
            
            # Check that after cursor is included in params
            params = call_args[0][2]
            assert params["after"] == after_cursor
            assert params["limit"] == 10

            # Verify the response structure
            result_data = json.loads(result)
            assert "data" in result_data
            assert len(result_data["data"]) == 1

    @pytest.mark.asyncio
    async def test_insights_default_limit(self, mock_auth_manager, valid_account_id, mock_paginated_response_page1):
        """Test that default limit is 25 when not specified"""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_paginated_response_page1

            result = await get_insights(
                object_id=valid_account_id,
                level="campaign"
            )

            # Verify the API was called with default limit
            mock_api_request.assert_called_once()
            call_args = mock_api_request.call_args
            
            params = call_args[0][2]
            assert params["limit"] == 25  # Default value

    @pytest.mark.asyncio
    async def test_insights_without_after_cursor(self, mock_auth_manager, valid_account_id, mock_paginated_response_page1):
        """Test that after parameter is not included when empty"""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_paginated_response_page1

            result = await get_insights(
                object_id=valid_account_id,
                level="campaign",
                after=""  # Empty after cursor
            )

            # Verify the API was called without after parameter
            mock_api_request.assert_called_once()
            call_args = mock_api_request.call_args
            
            params = call_args[0][2]
            assert "after" not in params  # Should not be included when empty

    @pytest.mark.asyncio
    async def test_insights_pagination_with_custom_time_range(self, mock_auth_manager, valid_account_id, mock_paginated_response_page1):
        """Test pagination works with custom time range"""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_paginated_response_page1

            custom_time_range = {"since": "2024-01-01", "until": "2024-01-31"}
            result = await get_insights(
                object_id=valid_account_id,
                level="campaign",
                time_range=custom_time_range,
                limit=5,
                after="test_cursor"
            )

            # Verify the API was called with correct parameters
            mock_api_request.assert_called_once()
            call_args = mock_api_request.call_args
            
            params = call_args[0][2]
            assert params["limit"] == 5
            assert params["after"] == "test_cursor"
            assert params["time_range"] == json.dumps(custom_time_range)

    @pytest.mark.asyncio
    async def test_insights_pagination_with_breakdown(self, mock_auth_manager, valid_account_id, mock_paginated_response_page1):
        """Test pagination works with breakdown parameter"""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_paginated_response_page1

            result = await get_insights(
                object_id=valid_account_id,
                level="campaign",
                breakdown="age",
                limit=10,
                after="test_cursor_2"
            )

            # Verify the API was called with correct parameters
            mock_api_request.assert_called_once()
            call_args = mock_api_request.call_args
            
            params = call_args[0][2]
            assert params["limit"] == 10
            assert params["after"] == "test_cursor_2"
            assert params["breakdowns"] == "age"

    @pytest.mark.asyncio
    async def test_insights_large_limit_value(self, mock_auth_manager, valid_account_id, mock_paginated_response_page1):
        """Test that large limit values are accepted (API will enforce its own limits)"""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_paginated_response_page1

            result = await get_insights(
                object_id=valid_account_id,
                level="campaign",
                limit=1000  # Large limit - API will enforce its own max
            )

            # Verify the API was called with the large limit
            mock_api_request.assert_called_once()
            call_args = mock_api_request.call_args
            
            params = call_args[0][2]
            assert params["limit"] == 1000

    @pytest.mark.asyncio
    async def test_insights_paging_response_structure(self, mock_auth_manager, valid_account_id, mock_paginated_response_page1):
        """Test that paging information is preserved in the response"""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_paginated_response_page1

            result = await get_insights(
                object_id=valid_account_id,
                level="campaign",
                limit=2
            )

            # Verify the response includes paging information
            result_data = json.loads(result)
            assert "data" in result_data
            assert "paging" in result_data
            assert "cursors" in result_data["paging"]
            assert "after" in result_data["paging"]["cursors"]
            assert "next" in result_data["paging"]
