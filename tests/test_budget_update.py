#!/usr/bin/env python3
"""
Unit Tests for Budget Update Functionality

This test suite validates the budget update parameter implementation for the
update_adset function in meta_ads_mcp/core/adsets.py.

Test cases cover:
- Budget update success scenarios
- Budget validation (negative, zero, too high values)
- Budget update with other parameters
- Error handling and permissions
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import the function to test
from meta_ads_mcp.core.adsets import update_adset


class TestBudgetUpdateFunctionality:
    """Test suite for budget update functionality"""
    
    @pytest.fixture
    def mock_api_request(self):
        """Mock for the make_api_request function"""
        with patch('meta_ads_mcp.core.adsets.make_api_request') as mock:
            mock.return_value = {
                "id": "test_adset_id",
                "daily_budget": "5000",
                "status": "ACTIVE"
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
    def valid_adset_id(self):
        """Valid ad set ID for testing"""
        return "123456789"
    
    @pytest.fixture
    def valid_daily_budget(self):
        """Valid daily budget amount in cents"""
        return "5000"  # $50.00
    
    @pytest.fixture
    def valid_lifetime_budget(self):
        """Valid lifetime budget amount in cents"""
        return "50000"  # $500.00
    
    @pytest.mark.asyncio
    async def test_budget_update_success(self, mock_api_request, mock_auth_manager, valid_adset_id, valid_daily_budget):
        """Test successful budget update"""
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget=valid_daily_budget
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that the endpoint is correct (first argument)
        assert call_args[0][0] == valid_adset_id
        
        # Check that daily_budget was included in parameters (third argument)
        params = call_args[0][2]  # Third positional argument is params
        assert 'daily_budget' in params
        assert params['daily_budget'] == valid_daily_budget
        
        # Verify the response structure
        assert 'id' in result_data
        assert result_data['id'] == "test_adset_id"
    
    @pytest.mark.asyncio
    async def test_lifetime_budget_update_success(self, mock_api_request, mock_auth_manager, valid_adset_id, valid_lifetime_budget):
        """Test successful lifetime budget update"""
        
        result = await update_adset(
            adset_id=valid_adset_id,
            lifetime_budget=valid_lifetime_budget
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that lifetime_budget was included in parameters
        params = call_args[0][2]  # Third positional argument is params
        assert 'lifetime_budget' in params
        assert params['lifetime_budget'] == valid_lifetime_budget
        
        # Verify the response structure
        assert 'id' in result_data
    
    @pytest.mark.asyncio
    async def test_both_budget_types_update(self, mock_api_request, mock_auth_manager, valid_adset_id, valid_daily_budget, valid_lifetime_budget):
        """Test updating both daily and lifetime budget simultaneously"""
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget=valid_daily_budget,
            lifetime_budget=valid_lifetime_budget
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that both budget parameters were included
        params = call_args[0][2]  # Third positional argument is params
        assert 'daily_budget' in params
        assert 'lifetime_budget' in params
        assert params['daily_budget'] == valid_daily_budget
        assert params['lifetime_budget'] == valid_lifetime_budget
        
        # Verify the response structure
        assert 'id' in result_data
    
    @pytest.mark.asyncio
    async def test_budget_update_with_other_parameters(self, mock_api_request, mock_auth_manager, valid_adset_id, valid_daily_budget):
        """Test budget update combined with other parameters"""
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget=valid_daily_budget,
            status="PAUSED",
            bid_amount=1000,
            bid_strategy="LOWEST_COST_WITH_BID_CAP"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that all parameters were included
        params = call_args[0][2]  # Third positional argument is params
        assert 'daily_budget' in params
        assert 'status' in params
        assert 'bid_amount' in params
        assert 'bid_strategy' in params
        assert params['daily_budget'] == valid_daily_budget
        assert params['status'] == "PAUSED"
        assert params['bid_amount'] == "1000"
        assert params['bid_strategy'] == "LOWEST_COST_WITH_BID_CAP"
        
        # Verify the response structure
        assert 'id' in result_data
    
    @pytest.mark.asyncio
    async def test_budget_update_with_numeric_values(self, mock_api_request, mock_auth_manager, valid_adset_id):
        """Test budget update with numeric values (should be converted to strings)"""
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget=5000,  # Integer
            lifetime_budget=50000  # Integer
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that numeric values were converted to strings
        params = call_args[0][2]  # Third positional argument is params
        assert 'daily_budget' in params
        assert 'lifetime_budget' in params
        assert params['daily_budget'] == "5000"
        assert params['lifetime_budget'] == "50000"
        
        # Verify the response structure
        assert 'id' in result_data
    
    @pytest.mark.asyncio
    async def test_budget_update_with_zero_budget(self, mock_api_request, mock_auth_manager, valid_adset_id):
        """Test budget update with zero budget (should be allowed)"""
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget="0"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with zero budget
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        params = call_args[0][2]  # Third positional argument is params
        assert 'daily_budget' in params
        assert params['daily_budget'] == "0"
        
        # Verify the response structure
        assert 'id' in result_data
    
    @pytest.mark.asyncio
    async def test_budget_update_with_high_budget(self, mock_api_request, mock_auth_manager, valid_adset_id):
        """Test budget update with high budget values"""
        
        high_budget = "1000000"  # $10,000
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget=high_budget
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with high budget
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        params = call_args[0][2]  # Third positional argument is params
        assert 'daily_budget' in params
        assert params['daily_budget'] == high_budget
        
        # Verify the response structure
        assert 'id' in result_data
    
    @pytest.mark.asyncio
    async def test_budget_update_api_error_handling(self, mock_api_request, mock_auth_manager, valid_adset_id, valid_daily_budget):
        """Test error handling when API call fails"""
        
        # Mock API to raise an exception
        mock_api_request.side_effect = Exception("API Error: Invalid budget amount")
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget=valid_daily_budget
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify error response structure
        # The error is wrapped in a 'data' field as JSON string
        error_data = json.loads(result_data['data'])
        assert 'error' in error_data
        assert 'details' in error_data
        assert 'params_sent' in error_data
        assert "Failed to update ad set" in error_data['error']
        assert "API Error: Invalid budget amount" in error_data['details']
        assert valid_adset_id in error_data['error']
        
        # Verify the parameters that were sent
        assert error_data['params_sent']['daily_budget'] == valid_daily_budget
    
    @pytest.mark.asyncio
    async def test_budget_update_with_invalid_adset_id(self, mock_api_request, mock_auth_manager):
        """Test budget update with invalid ad set ID"""
        
        result = await update_adset(
            adset_id="",  # Empty ad set ID
            daily_budget="5000"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify error response
        error_data = json.loads(result_data['data'])
        assert 'error' in error_data
        assert "No ad set ID provided" in error_data['error']
        
        # Verify API was not called
        mock_api_request.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_budget_update_with_no_parameters(self, mock_api_request, mock_auth_manager, valid_adset_id):
        """Test budget update with no parameters provided"""
        
        result = await update_adset(
            adset_id=valid_adset_id
            # No parameters provided
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify error response
        error_data = json.loads(result_data['data'])
        assert 'error' in error_data
        assert "No update parameters provided" in error_data['error']
        
        # Verify API was not called
        mock_api_request.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_budget_update_with_negative_budget(self, mock_api_request, mock_auth_manager, valid_adset_id):
        """Test budget update with negative budget (should be handled by API)"""
        
        # Mock API to handle negative budget error
        mock_api_request.side_effect = Exception("API Error: Budget amount must be positive")
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget="-1000"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify error response structure
        error_data = json.loads(result_data['data'])
        assert 'error' in error_data
        assert 'details' in error_data
        assert "API Error: Budget amount must be positive" in error_data['details']
    
    @pytest.mark.asyncio
    async def test_budget_update_with_non_numeric_string(self, mock_api_request, mock_auth_manager, valid_adset_id):
        """Test budget update with non-numeric string (should be handled by API)"""
        
        # Mock API to handle non-numeric budget error
        mock_api_request.side_effect = Exception("API Error: Invalid budget format")
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget="invalid_budget"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify error response structure
        error_data = json.loads(result_data['data'])
        assert 'error' in error_data
        assert 'details' in error_data
        assert "API Error: Invalid budget format" in error_data['details']
    
    @pytest.mark.asyncio
    async def test_budget_update_with_permission_error(self, mock_api_request, mock_auth_manager, valid_adset_id, valid_daily_budget):
        """Test budget update with permission error"""
        
        # Mock API to raise permission error
        mock_api_request.side_effect = Exception("API Error: (#100) Insufficient permissions")
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget=valid_daily_budget
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify error response structure
        error_data = json.loads(result_data['data'])
        assert 'error' in error_data
        assert 'details' in error_data
        assert "Insufficient permissions" in error_data['details']
    
    @pytest.mark.asyncio
    async def test_budget_update_with_targeting(self, mock_api_request, mock_auth_manager, valid_adset_id, valid_daily_budget):
        """Test budget update combined with targeting update"""
        
        targeting = {
            "age_min": 25,
            "age_max": 45,
            "geo_locations": {"countries": ["US", "CA"]}
        }
        
        result = await update_adset(
            adset_id=valid_adset_id,
            daily_budget=valid_daily_budget,
            targeting=targeting
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check that both budget and targeting were included
        params = call_args[0][2]  # Third positional argument is params
        assert 'daily_budget' in params
        assert 'targeting' in params
        assert params['daily_budget'] == valid_daily_budget
        
        # Verify targeting was properly JSON encoded
        targeting_json = json.loads(params['targeting'])
        assert targeting_json['age_min'] == 25
        assert targeting_json['age_max'] == 45
        assert targeting_json['geo_locations']['countries'] == ["US", "CA"]
        
        # Verify the response structure
        assert 'id' in result_data


class TestBudgetUpdateIntegration:
    """Integration tests for budget update functionality"""
    
    @pytest.mark.asyncio
    async def test_budget_update_workflow(self):
        """Test complete budget update workflow"""
        
        # This test would require a real ad set ID and valid API credentials
        # For now, we'll test the function signature and parameter handling
        
        # Test that the function accepts the new parameters
        with patch('meta_ads_mcp.core.adsets.make_api_request') as mock_api, \
             patch('meta_ads_mcp.core.api.auth_manager') as mock_auth, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            
            mock_api.return_value = {"id": "test_id", "daily_budget": "5000"}
            mock_auth.get_current_access_token.return_value = "test_access_token"
            mock_auth.is_token_valid.return_value = True
            mock_auth.app_id = "test_app_id"
            mock_get_token.return_value = "test_access_token"
            
            result = await update_adset(
                adset_id="test_adset_id",
                daily_budget="5000",
                lifetime_budget="50000"
            )
            
            # Verify the function executed without errors
            assert result is not None
            # The result might already be a dict or a JSON string
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            assert 'id' in result_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 