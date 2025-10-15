#!/usr/bin/env python3
"""
Unit tests for estimate_audience_size functionality in Meta Ads MCP.

This module tests the new estimate_audience_size function that replaces validate_interests
and provides comprehensive audience estimation using Meta's reachestimate API.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.targeting import estimate_audience_size


class TestEstimateAudienceSize:
    """Test cases for estimate_audience_size function"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_audience_estimation_success(self):
        """Test successful comprehensive audience estimation with complex targeting"""
        mock_response = {
            "data": [
                {
                    "estimate_mau": 1500000,
                    "estimate_dau": [
                        {"min_reach": 100000, "max_reach": 150000, "bid": 100},
                        {"min_reach": 200000, "max_reach": 250000, "bid": 200}
                    ],
                    "bid_estimates": {
                        "median": 150,
                        "min": 50,
                        "max": 300
                    },
                    "unsupported_targeting": []
                }
            ]
        }
        
        targeting_spec = {
            "age_min": 25,
            "age_max": 65,
            "geo_locations": {"countries": ["US"]},
            "flexible_spec": [
                {"interests": [{"id": "6003371567474"}]}
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await estimate_audience_size(
                access_token="test_token",
                account_id="act_123456789",
                targeting=targeting_spec,
                optimization_goal="REACH"
            )
            
            # Verify API call
            mock_api.assert_called_once_with(
                "act_123456789/reachestimate",
                "test_token",
                {
                    "targeting_spec": targeting_spec
                },
                method="GET"
            )
            
            # Verify response format
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["account_id"] == "act_123456789"
            assert result_data["targeting"] == targeting_spec
            assert result_data["optimization_goal"] == "REACH"
            assert result_data["estimated_audience_size"] == 1500000
            assert "estimate_details" in result_data
            assert result_data["estimate_details"]["monthly_active_users"] == 1500000
    
    @pytest.mark.asyncio
    async def test_different_optimization_goals(self):
        """Test audience estimation with different optimization goals (parameter is preserved in response)"""
        mock_response = {
            "data": [
                {
                    "estimate_mau": 800000,
                    "estimate_dau": [],
                    "bid_estimates": {},
                    "unsupported_targeting": []
                }
            ]
        }
        
        targeting_spec = {
            "age_min": 18,
            "age_max": 45,
            "geo_locations": {"countries": ["US"]}
        }
        
        # Test different optimization goals - they should all use the same reachestimate endpoint
        test_goals = ["REACH", "LINK_CLICKS", "LANDING_PAGE_VIEWS", "CONVERSIONS", "APP_INSTALLS"]
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            for optimization_goal in test_goals:
                mock_api.reset_mock()
                
                result = await estimate_audience_size(
                    access_token="test_token",
                    account_id="act_123456789",
                    targeting=targeting_spec,
                    optimization_goal=optimization_goal
                )
                
                # Verify API call uses reachestimate endpoint with simplified parameters
                mock_api.assert_called_once_with(
                    "act_123456789/reachestimate",
                    "test_token",
                    {
                        "targeting_spec": targeting_spec
                    },
                    method="GET"
                )
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["optimization_goal"] == optimization_goal
    
    @pytest.mark.asyncio
    async def test_backwards_compatibility_interest_names(self):
        """Test backwards compatibility with interest name validation"""
        mock_response = {
            "data": [
                {
                    "name": "Japan",
                    "valid": True,
                    "id": 6003700426513,
                    "audience_size": 68310258
                },
                {
                    "name": "invalidinterest",
                    "valid": False
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await estimate_audience_size(
                access_token="test_token",
                interest_list=["Japan", "invalidinterest"]
            )
            
            # Verify it uses the old validation API
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adinterestvalid",
                    "interest_list": '["Japan", "invalidinterest"]'
                }
            )
            
            # Verify response matches old format
            result_data = json.loads(result)
            assert result_data == mock_response
            assert result_data["data"][0]["valid"] is True
            assert result_data["data"][1]["valid"] is False
    
    @pytest.mark.asyncio
    async def test_backwards_compatibility_interest_fbids(self):
        """Test backwards compatibility with interest FBID validation"""
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
            
            # Verify it uses the old validation API
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adinterestvalid",
                    "interest_fbid_list": '["6003700426513"]'
                }
            )
            
            # Verify response matches old format
            result_data = json.loads(result)
            assert result_data == mock_response
            assert result_data["data"][0]["valid"] is True
    
    @pytest.mark.asyncio
    async def test_backwards_compatibility_both_interest_params(self):
        """Test backwards compatibility with both interest names and FBIDs"""
        mock_response = {
            "data": [
                {"name": "Japan", "valid": True, "id": 6003700426513, "audience_size": 68310258},
                {"id": "6003397425735", "valid": True, "audience_size": 12345678}
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await estimate_audience_size(
                access_token="test_token",
                interest_list=["Japan"],
                interest_fbid_list=["6003397425735"]
            )
            
            # Verify both parameters are passed
            mock_api.assert_called_once_with(
                "search",
                "test_token",
                {
                    "type": "adinterestvalid",
                    "interest_list": '["Japan"]',
                    "interest_fbid_list": '["6003397425735"]'
                }
            )
            
            result_data = json.loads(result)
            assert result_data == mock_response
    
    @pytest.mark.asyncio
    async def test_error_no_account_id_for_comprehensive(self):
        """Test error when account_id missing for comprehensive estimation"""
        targeting_spec = {
            "age_min": 25,
            "age_max": 65,
            "geo_locations": {"countries": ["US"]}
        }
        
        result = await estimate_audience_size(
            access_token="test_token",
            targeting=targeting_spec
        )
        
        result_data = json.loads(result)
        # The @meta_api_tool decorator wraps errors in a 'data' field
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert "error" in nested_data
        assert "account_id is required" in nested_data["error"]
        assert "details" in nested_data
    
    @pytest.mark.asyncio
    async def test_error_no_targeting_for_comprehensive(self):
        """Test error when targeting missing for comprehensive estimation"""
        result = await estimate_audience_size(
            access_token="test_token",
            account_id="act_123456789"
        )
        
        result_data = json.loads(result)
        # The @meta_api_tool decorator wraps errors in a 'data' field
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert "error" in nested_data
        assert "targeting specification is required" in nested_data["error"]
        assert "example" in nested_data
    
    @pytest.mark.asyncio
    async def test_error_no_parameters(self):
        """Test error when no parameters provided"""
        # Since we're using the @meta_api_tool decorator, we need to simulate
        # its behavior for error handling
        with patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_auth:
            mock_auth.return_value = "test_token"
            
            result = await estimate_audience_size()
            
            result_data = json.loads(result)
            # The @meta_api_tool decorator wraps errors in a 'data' field
            assert "data" in result_data
            nested_data = json.loads(result_data["data"])
            assert "error" in nested_data
    
    @pytest.mark.asyncio
    async def test_error_backwards_compatibility_no_interests(self):
        """Test error in backwards compatibility mode with no interest parameters"""
        result = await estimate_audience_size(
            access_token="test_token"
        )
        
        result_data = json.loads(result)
        # The @meta_api_tool decorator wraps errors in a 'data' field
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert "error" in nested_data
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test handling of API errors from reachestimate"""
        targeting_spec = {
            "age_min": 25,
            "age_max": 65,
            "geo_locations": {"countries": ["US"]}
        }
        
        # Simulate API exception
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.side_effect = Exception("API connection failed")
            
            result = await estimate_audience_size(
                access_token="test_token",
                account_id="act_123456789",
                targeting=targeting_spec
            )
            
            result_data = json.loads(result)
            # The @meta_api_tool decorator wraps errors in a 'data' field
            assert "data" in result_data
            nested_data = json.loads(result_data["data"])
            assert "error" in nested_data
            assert "Failed to get audience estimation from reachestimate endpoint" in nested_data["error"]
            assert "details" in nested_data
    
    @pytest.mark.asyncio
    async def test_empty_api_response(self):
        """Test handling of empty response from reachestimate API"""
        targeting_spec = {
            "age_min": 25,
            "age_max": 65,
            "geo_locations": {"countries": ["US"]}
        }
        
        # Simulate empty API response
        mock_response = {"data": []}
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await estimate_audience_size(
                access_token="test_token",
                account_id="act_123456789",
                targeting=targeting_spec
            )
            
            result_data = json.loads(result)
            # The @meta_api_tool decorator wraps errors in a 'data' field
            assert "data" in result_data
            nested_data = json.loads(result_data["data"])
            assert "error" in nested_data
            assert "No estimation data returned" in nested_data["error"]
            assert "raw_response" in nested_data
    
    @pytest.mark.asyncio
    async def test_comprehensive_estimation_with_minimal_targeting(self):
        """Test comprehensive estimation with minimal targeting requirements"""
        mock_response = {
            "data": [
                {
                    "estimate_mau": 500000,
                    "estimate_dau": [],
                    "bid_estimates": {},
                    "unsupported_targeting": []
                }
            ]
        }
        
        minimal_targeting = {
            "age_min": 18,
            "age_max": 65,
            "geo_locations": {"countries": ["US"]}
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await estimate_audience_size(
                access_token="test_token",
                account_id="act_123456789",
                targeting=minimal_targeting
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["estimated_audience_size"] == 500000
            assert result_data["targeting"] == minimal_targeting
    
    @pytest.mark.asyncio
    async def test_estimate_details_structure(self):
        """Test that estimate_details contains expected structure"""
        mock_response = {
            "data": [
                {
                    "estimate_mau": 2000000,
                    "estimate_dau": [
                        {"min_reach": 150000, "max_reach": 200000, "bid": 120}
                    ],
                    "bid_estimates": {
                        "median": 180,
                        "min": 80,
                        "max": 350
                    },
                    "unsupported_targeting": ["custom_audiences"]
                }
            ]
        }
        
        targeting_spec = {
            "age_min": 25,
            "age_max": 45,
            "geo_locations": {"countries": ["US"]},
            "flexible_spec": [
                {"interests": [{"id": "6003371567474"}, {"id": "6003462346642"}]}
            ]
        }
        
        with patch('meta_ads_mcp.core.targeting.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            
            result = await estimate_audience_size(
                access_token="test_token",
                account_id="act_123456789",
                targeting=targeting_spec,
                optimization_goal="CONVERSIONS"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Check estimate_details structure
            details = result_data["estimate_details"]
            assert "monthly_active_users" in details
            assert "daily_outcomes_curve" in details
            assert "bid_estimate" in details
            assert "unsupported_targeting" in details
            
            assert details["monthly_active_users"] == 2000000
            assert len(details["daily_outcomes_curve"]) == 1
            assert details["bid_estimate"]["median"] == 180
            assert "custom_audiences" in details["unsupported_targeting"]
    
    @pytest.mark.asyncio
    async def test_function_registration(self):
        """Test that the function is properly registered as an MCP tool"""
        # This test verifies the function has the correct decorators
        assert hasattr(estimate_audience_size, '__wrapped__')  # From @meta_api_tool
        
        # Verify function signature
        import inspect
        sig = inspect.signature(estimate_audience_size)
        
        expected_params = [
            'access_token', 'account_id', 'targeting', 'optimization_goal',
            'interest_list', 'interest_fbid_list'
        ]
        
        for param in expected_params:
            assert param in sig.parameters
        
        # Verify default values
        assert sig.parameters['optimization_goal'].default == "REACH"
        assert sig.parameters['access_token'].default is None
        assert sig.parameters['targeting'].default is None