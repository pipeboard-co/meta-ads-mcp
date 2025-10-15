#!/usr/bin/env python3
"""
Unit tests for get_account_info accessibility fix.

This module tests the fix for the issue where get_account_info couldn't access
accounts that were visible in get_ad_accounts but not in the limited direct
accessibility list.

The fix changes the logic to try fetching account info directly first,
rather than pre-checking against a limited accessibility list.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.accounts import get_account_info


class TestAccountInfoAccessFix:
    """Test cases for the get_account_info accessibility fix"""
    
    @pytest.mark.asyncio
    async def test_account_info_direct_access_success(self):
        """Test that get_account_info works when direct API call succeeds"""
        
        # Mock the direct account info API response
        mock_account_response = {
            "id": "act_414174661097171",
            "name": "Venture Hunting & Outdoors",
            "account_id": "414174661097171",
            "account_status": 1,
            "amount_spent": "5818510",
            "balance": "97677",
            "currency": "AUD",
            "timezone_name": "Australia/Brisbane",
            "business_country_code": "AU"
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_account_response
                
                result = await get_account_info(account_id="414174661097171")
                
                # Handle both string and dict return formats
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
                
                # Verify the account info was returned successfully
                assert "error" not in result_data
                assert result_data["id"] == "act_414174661097171"
                assert result_data["name"] == "Venture Hunting & Outdoors"
                assert result_data["account_id"] == "414174661097171"
                assert result_data["currency"] == "AUD"
                assert result_data["timezone_name"] == "Australia/Brisbane"
                
                # Verify DSA compliance detection was added
                assert "dsa_required" in result_data
                assert result_data["dsa_required"] is False  # AU is not European
                assert "dsa_compliance_note" in result_data
                
                # Verify the API was called with correct parameters
                mock_api.assert_called_once_with(
                    "act_414174661097171",
                    "test_access_token",
                    {
                        "fields": "id,name,account_id,account_status,amount_spent,balance,currency,age,business_city,business_country_code,timezone_name"
                    }
                )
    
    @pytest.mark.asyncio
    async def test_account_info_permission_error_with_helpful_message(self):
        """Test that permission errors provide helpful error messages with accessible accounts"""
        
        # Mock the permission error response from direct API call
        mock_permission_error = {
            "error": {
                "message": "Insufficient privileges to access the object",
                "type": "OAuthException",
                "code": 200
            }
        }
        
        # Mock accessible accounts response for helpful error message
        mock_accessible_accounts = {
            "data": [
                {"id": "act_123456", "name": "Accessible Account 1"},
                {"id": "act_789012", "name": "Accessible Account 2"},
                {"id": "act_345678", "name": "Accessible Account 3"}
            ]
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                
                # First call returns permission error, second call returns accessible accounts
                mock_api.side_effect = [mock_permission_error, mock_accessible_accounts]
                
                result = await get_account_info(account_id="414174661097171")
                
                # Handle both string and dict return formats
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
                
                # Verify helpful error message
                assert "error" in result_data
                assert "not accessible to your user account" in result_data["error"]["message"]
                assert "accessible_accounts" in result_data["error"]
                assert "suggestion" in result_data["error"]
                assert result_data["error"]["total_accessible_accounts"] == 3
                
                # Verify accessible accounts list
                accessible_accounts = result_data["error"]["accessible_accounts"]
                assert len(accessible_accounts) == 3
                assert accessible_accounts[0]["id"] == "act_123456"
                assert accessible_accounts[0]["name"] == "Accessible Account 1"
                
                # Verify API calls were made
                assert mock_api.call_count == 2
                
                # First call: direct account access attempt
                mock_api.assert_any_call(
                    "act_414174661097171",
                    "test_access_token",
                    {
                        "fields": "id,name,account_id,account_status,amount_spent,balance,currency,age,business_city,business_country_code,timezone_name"
                    }
                )
                
                # Second call: get accessible accounts for error message
                mock_api.assert_any_call(
                    "me/adaccounts",
                    "test_access_token",
                    {
                        "fields": "id,name,account_id,account_status,amount_spent,balance,currency,age,business_city,business_country_code",
                        "limit": 50
                    }
                )
    
    @pytest.mark.asyncio
    async def test_account_info_non_permission_error_passthrough(self):
        """Test that non-permission errors are passed through unchanged"""
        
        # Mock a non-permission error (e.g., invalid account ID)
        mock_error_response = {
            "error": {
                "message": "Invalid account ID format",
                "type": "GraphAPIException",
                "code": 100
            }
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_error_response
                
                result = await get_account_info(account_id="invalid_id")
                
                # Handle both string and dict return formats
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
                
                # Verify the original error is returned unchanged
                assert result_data == mock_error_response
                
                # Verify only one API call was made (no attempt to get accessible accounts)
                mock_api.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_account_info_missing_account_id_error(self):
        """Test that missing account_id parameter returns appropriate error"""
        
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = "test_access_token"
            
            result = await get_account_info(account_id=None)
            
            # Handle both string and dict return formats
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            # Verify error message
            assert "error" in result_data
            assert "Account ID is required" in result_data["error"]["message"]
            assert "Please specify an account_id parameter" in result_data["error"]["details"]
    
    @pytest.mark.asyncio
    async def test_account_info_act_prefix_handling(self):
        """Test that account_id prefix handling works correctly"""
        
        mock_account_response = {
            "id": "act_123456789",
            "name": "Test Account",
            "account_id": "123456789"
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_account_response
                
                # Test with account ID without act_ prefix
                result = await get_account_info(account_id="123456789")
                
                # Verify the API was called with the act_ prefix added
                mock_api.assert_called_once_with(
                    "act_123456789",  # Should have act_ prefix added
                    "test_access_token",
                    {
                        "fields": "id,name,account_id,account_status,amount_spent,balance,currency,age,business_city,business_country_code,timezone_name"
                    }
                )
    
    @pytest.mark.asyncio 
    async def test_account_info_european_dsa_detection(self):
        """Test that DSA requirements are properly detected for European accounts"""
        
        # Mock account response for German business
        mock_account_response = {
            "id": "act_999888777",
            "name": "German Test Account",
            "account_id": "999888777",
            "business_country_code": "DE"  # Germany - should trigger DSA
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_account_response
                
                result = await get_account_info(account_id="999888777")
                
                # Handle both string and dict return formats
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
                
                # Verify DSA requirements were properly detected
                assert "dsa_required" in result_data
                assert result_data["dsa_required"] is True  # DE is European
                assert "dsa_compliance_note" in result_data
                assert "European DSA" in result_data["dsa_compliance_note"]


class TestAccountInfoAccessRegression:
    """Regression tests to ensure the fix doesn't break existing functionality"""
    
    @pytest.mark.asyncio
    async def test_regression_basic_account_info_still_works(self):
        """Regression test: ensure basic account info functionality still works"""
        
        mock_account_response = {
            "id": "act_123456789",
            "name": "Basic Test Account",
            "account_id": "123456789",
            "account_status": 1,
            "currency": "USD",
            "business_country_code": "US"
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_account_response
                
                result = await get_account_info(account_id="act_123456789")
                
                # Handle both string and dict return formats
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
                
                # Verify basic functionality works
                assert "error" not in result_data
                assert result_data["id"] == "act_123456789"
                assert result_data["name"] == "Basic Test Account"
                
    def test_account_info_fix_comparison(self):
        """
        Documentation test: explains what the fix changed
        
        BEFORE: get_account_info checked accessibility first against limited list (50 accounts)
        AFTER: get_account_info tries direct API call first, only shows error if API fails
        
        This allows accounts visible through business manager (like 414174661097171)
        to work properly even if they're not in the limited direct accessibility list.
        """
        
        # This is a documentation test - no actual code execution
        old_behavior = "Pre-check accessibility against limited 50 account list"
        new_behavior = "Try direct API call first, handle permission errors gracefully"
        
        assert old_behavior != new_behavior
        
        # The key insight: get_ad_accounts shows 107 accounts through business manager,
        # but "me/adaccounts" only shows 50 directly accessible accounts
        total_visible_accounts = 107
        directly_accessible_accounts = 50
        
        assert total_visible_accounts > directly_accessible_accounts
        
        # Account 414174661097171 was in the 107 but not in the 50
        # The fix allows get_account_info to work for such accounts