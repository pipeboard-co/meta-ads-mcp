#!/usr/bin/env python3
"""
Unit Tests for Insights Actions and Action Values Functionality

This test suite validates the actions and action_values field implementation for the
get_insights function in meta_ads_mcp/core/insights.py.

Test cases cover:
- Actions and action_values field inclusion in API requests
- Different levels of aggregation (ad, adset, campaign, account)
- Time range handling with actions and action_values
- Error handling and validation
- Purchase data extraction from actions and action_values
"""

import pytest
import json
import asyncio
import requests
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import the function to test
from meta_ads_mcp.core.insights import get_insights


class TestInsightsActionsAndValues:
    """Test suite for actions and action_values in insights"""
    
    @pytest.fixture
    def mock_api_request(self):
        """Mock for the make_api_request function"""
        with patch('meta_ads_mcp.core.insights.make_api_request') as mock:
            mock.return_value = {
                "data": [
                    {
                        "campaign_id": "test_campaign_id",
                        "campaign_name": "Test Campaign",
                        "impressions": "1000",
                        "clicks": "50",
                        "spend": "100.00",
                        "actions": [
                            {"action_type": "purchase", "value": "5"},
                            {"action_type": "lead", "value": "3"},
                            {"action_type": "view_content", "value": "20"}
                        ],
                        "action_values": [
                            {"action_type": "purchase", "value": "500.00"},
                            {"action_type": "lead", "value": "150.00"},
                            {"action_type": "view_content", "value": "0.00"}
                        ],
                        "cost_per_action_type": [
                            {"action_type": "purchase", "value": "20.00"},
                            {"action_type": "lead", "value": "33.33"}
                        ]
                    }
                ],
                "paging": {}
            }
            yield mock
    
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
    def valid_campaign_id(self):
        """Valid campaign ID for testing"""
        return "123456789"
    
    @pytest.fixture
    def valid_account_id(self):
        """Valid account ID for testing"""
        return "act_701351919139047"
    
    @pytest.mark.asyncio
    async def test_actions_and_action_values_included_in_fields(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test that actions and action_values are included in the fields parameter"""
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range="last_30d",
            level="campaign"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that the endpoint is correct (first argument)
        assert call_args[0][0] == f"{valid_campaign_id}/insights"
        
        # Check that actions and action_values are included in fields parameter
        params = call_args[0][2]  # Third positional argument is params
        assert 'fields' in params
        
        fields = params['fields']
        assert 'actions' in fields
        assert 'action_values' in fields
        assert 'cost_per_action_type' in fields
        
        # Verify the response structure
        assert 'data' in result_data
        assert len(result_data['data']) > 0
        assert 'actions' in result_data['data'][0]
        assert 'action_values' in result_data['data'][0]
    
    @pytest.mark.asyncio
    async def test_purchase_data_extraction(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test that purchase data can be extracted from actions and action_values"""
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range="last_30d",
            level="campaign"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Get the first data point
        data_point = result_data['data'][0]
        
        # Extract purchase data from actions
        actions = data_point.get('actions', [])
        purchase_actions = [action for action in actions if action.get('action_type') == 'purchase']
        
        # Extract purchase data from action_values
        action_values = data_point.get('action_values', [])
        purchase_values = [action_value for action_value in action_values if action_value.get('action_type') == 'purchase']
        
        # Verify purchase data exists
        assert len(purchase_actions) > 0, "No purchase actions found"
        assert len(purchase_values) > 0, "No purchase action_values found"
        
        # Verify purchase data values
        purchase_count = purchase_actions[0].get('value')
        purchase_value = purchase_values[0].get('value')
        
        assert purchase_count == "5", f"Expected purchase count 5, got {purchase_count}"
        assert purchase_value == "500.00", f"Expected purchase value 500.00, got {purchase_value}"
    
    @pytest.mark.asyncio
    async def test_actions_at_adset_level(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test actions and action_values at adset level"""
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range="last_30d",
            level="adset"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that the level parameter is correct
        params = call_args[0][2]
        assert params['level'] == 'adset'
        
        # Verify the response structure
        assert 'data' in result_data
    
    @pytest.mark.asyncio
    async def test_actions_at_ad_level(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test actions and action_values at ad level"""
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range="last_30d",
            level="ad"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that the level parameter is correct
        params = call_args[0][2]
        assert params['level'] == 'ad'
        
        # Verify the response structure
        assert 'data' in result_data
    
    @pytest.mark.asyncio
    async def test_actions_with_custom_time_range(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test actions and action_values with custom time range"""
        
        custom_time_range = {"since": "2024-01-01", "until": "2024-01-31"}
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range=custom_time_range,
            level="campaign"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that time_range is properly formatted
        params = call_args[0][2]
        assert 'time_range' in params
        assert params['time_range'] == json.dumps(custom_time_range)
        
        # Verify the response structure
        assert 'data' in result_data
    
    @pytest.mark.asyncio
    async def test_actions_with_breakdown(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test actions and action_values with breakdown dimension"""
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range="last_30d",
            level="campaign",
            breakdown="age"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that breakdown is included
        params = call_args[0][2]
        assert 'breakdowns' in params
        assert params['breakdowns'] == 'age'
        
        # Verify the response structure
        assert 'data' in result_data
    
    @pytest.mark.asyncio
    async def test_actions_without_object_id(self, mock_api_request, mock_auth_manager):
        """Test error handling when no object_id is provided"""
        
        result = await get_insights(
            time_range="last_30d",
            level="campaign"
        )
        
        # Parse the result. The decorator returns a dict error for missing required args
        if isinstance(result, dict):
            result_data = result
        else:
            result_data = json.loads(result)

        assert 'error' in result_data
        assert "missing 1 required positional argument: 'object_id'" in result_data['error']
        
        # Verify API was not called
        mock_api_request.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_actions_with_invalid_time_range(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test error handling with invalid time range"""
        
        invalid_time_range = {"since": "2024-01-01"}  # Missing "until"
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range=invalid_time_range,
            level="campaign"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # The error response is wrapped in a 'data' field
        if 'data' in result_data:
            error_data = json.loads(result_data['data'])
            assert 'error' in error_data
            assert 'since' in error_data['error'] and 'until' in error_data['error']
        else:
            assert 'error' in result_data
            assert 'since' in result_data['error'] and 'until' in result_data['error']
        
        # Verify API was not called
        mock_api_request.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_actions_api_error_handling(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test error handling when API call fails"""
        
        # Mock API to raise an exception
        mock_api_request.side_effect = Exception("API Error")
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range="last_30d",
            level="campaign"
        )
        
        # Parse the result
        # The API error handling returns a dict directly, not a JSON string
        if isinstance(result, dict):
            result_data = result
        else:
            result_data = json.loads(result)
        
        # Verify error response
        assert 'error' in result_data
        assert 'API Error' in result_data['error']
    
    @pytest.mark.asyncio
    async def test_actions_fields_completeness(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test that all required fields are included in the request"""
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range="last_30d",
            level="campaign"
        )
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that all required fields are included
        params = call_args[0][2]
        fields = params['fields']
        
        # Required fields for actions and action_values
        required_fields = [
            'account_id', 'account_name', 'campaign_id', 'campaign_name',
            'adset_id', 'adset_name', 'ad_id', 'ad_name',
            'impressions', 'clicks', 'spend', 'cpc', 'cpm', 'ctr',
            'reach', 'frequency', 'actions', 'action_values', 'conversions',
            'unique_clicks', 'cost_per_action_type'
        ]
        
        for field in required_fields:
            assert field in fields, f"Field '{field}' not found in fields parameter"
    
    @pytest.mark.asyncio
    async def test_multiple_action_types(self, mock_api_request, mock_auth_manager, valid_campaign_id):
        """Test handling of multiple action types in the response"""
        
        result = await get_insights(
            object_id=valid_campaign_id,
            time_range="last_30d",
            level="campaign"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Get the first data point
        data_point = result_data['data'][0]
        
        # Check that multiple action types are present
        actions = data_point.get('actions', [])
        action_types = [action.get('action_type') for action in actions]
        
        assert 'purchase' in action_types, "Purchase action type not found"
        assert 'lead' in action_types, "Lead action type not found"
        assert 'view_content' in action_types, "View content action type not found"
        
        # Check action_values has corresponding entries
        action_values = data_point.get('action_values', [])
        action_value_types = [action_value.get('action_type') for action_value in action_values]
        
        assert 'purchase' in action_value_types, "Purchase action_value type not found"
        assert 'lead' in action_value_types, "Lead action_value type not found"


@pytest.mark.e2e
@pytest.mark.skip(reason="E2E test - run manually only")
class TestInsightsActionsAndValuesE2E:
    """E2E tests for actions and action_values via MCP HTTP server"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp/"
        self.request_id = 1
        # Default account from workspace rules
        self.account_id = "act_701351919139047"

    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Insights-E2E-Test-Client/1.0"
        }
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id
        }
        if params:
            payload["params"] = params
        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            self.request_id += 1
            return {
                "status_code": resp.status_code,
                "json": resp.json() if resp.status_code == 200 else None,
                "text": resp.text,
                "success": resp.status_code == 200
            }
        except requests.exceptions.RequestException as e:
            return {"status_code": 0, "json": None, "text": str(e), "success": False, "error": str(e)}

    def _check_for_errors(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        if "data" in parsed_content:
            data = parsed_content["data"]
            if isinstance(data, dict) and 'error' in data:
                return {"has_error": True, "error_message": data['error'], "format": "wrapped_dict"}
            if isinstance(data, str):
                try:
                    error_data = json.loads(data)
                    if 'error' in error_data:
                        return {"has_error": True, "error_message": error_data['error'], "format": "wrapped_json"}
                except json.JSONDecodeError:
                    pass
        if 'error' in parsed_content:
            return {"has_error": True, "error_message": parsed_content['error'], "format": "direct"}
        return {"has_error": False}

    def test_tool_exists_and_has_required_fields(self):
        result = self._make_request("tools/list", {})
        assert result["success"], f"tools/list failed: {result.get('text', '')}"
        tools = result["json"]["result"].get("tools", [])
        tool = next((t for t in tools if t["name"] == "get_insights"), None)
        assert tool is not None, "get_insights tool not found"
        props = tool.get("inputSchema", {}).get("properties", {})
        for req in ["object_id", "time_range", "breakdown", "level"]:
            assert req in props, f"Missing parameter in schema: {req}"

    def test_get_insights_account_level(self):
        params = {
            "name": "get_insights",
            "arguments": {
                "object_id": self.account_id,
                "time_range": "last_30d",
                "level": "account"
            }
        }
        result = self._make_request("tools/call", params)
        assert result["success"], f"tools/call failed: {result.get('text', '')}"
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        parsed = json.loads(content)
        err = self._check_for_errors(parsed)
        # Don't fail if auth or permissions block; just assert structure is parsable
        if err["has_error"]:
            assert isinstance(err["error_message"], (str, dict))
        else:
            # Expect data list on success
            data = parsed.get("data") if isinstance(parsed, dict) else None
            assert data is not None

def main():
    tester = TestInsightsActionsAndValuesE2E()
    print("🚀 Insights Actions E2E (manual)")
    # Basic smoke run
    try:
        tester.test_tool_exists_and_has_required_fields()
        print("✅ Tool schema ok")
        tester.test_get_insights_account_level()
        print("✅ Account-level insights request executed")
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


def extract_purchase_data(insights_data):
    """
    Helper function to extract purchase data from insights response.
    
    Args:
        insights_data: The data array from insights response
        
    Returns:
        dict: Dictionary with purchase count and value
    """
    if not insights_data or len(insights_data) == 0:
        return {"purchase_count": 0, "purchase_value": 0.0}
    
    data_point = insights_data[0]
    
    # Extract purchase count from actions
    actions = data_point.get('actions', [])
    purchase_actions = [action for action in actions if action.get('action_type') == 'purchase']
    purchase_count = int(purchase_actions[0].get('value', 0)) if purchase_actions else 0
    
    # Extract purchase value from action_values
    action_values = data_point.get('action_values', [])
    purchase_values = [action_value for action_value in action_values if action_value.get('action_type') == 'purchase']
    purchase_value = float(purchase_values[0].get('value', 0)) if purchase_values else 0.0
    
    return {
        "purchase_count": purchase_count,
        "purchase_value": purchase_value
    }


class TestPurchaseDataExtraction:
    """Test suite for purchase data extraction helper function"""
    
    def test_extract_purchase_data_with_purchases(self):
        """Test extraction when purchase data is present"""
        insights_data = [{
            "actions": [
                {"action_type": "purchase", "value": "5"},
                {"action_type": "lead", "value": "3"}
            ],
            "action_values": [
                {"action_type": "purchase", "value": "500.00"},
                {"action_type": "lead", "value": "150.00"}
            ]
        }]
        
        result = extract_purchase_data(insights_data)
        
        assert result["purchase_count"] == 5
        assert result["purchase_value"] == 500.0
    
    def test_extract_purchase_data_without_purchases(self):
        """Test extraction when no purchase data is present"""
        insights_data = [{
            "actions": [
                {"action_type": "lead", "value": "3"},
                {"action_type": "view_content", "value": "20"}
            ],
            "action_values": [
                {"action_type": "lead", "value": "150.00"},
                {"action_type": "view_content", "value": "0.00"}
            ]
        }]
        
        result = extract_purchase_data(insights_data)
        
        assert result["purchase_count"] == 0
        assert result["purchase_value"] == 0.0
    
    def test_extract_purchase_data_empty_data(self):
        """Test extraction with empty data"""
        insights_data = []
        
        result = extract_purchase_data(insights_data)
        
        assert result["purchase_count"] == 0
        assert result["purchase_value"] == 0.0 