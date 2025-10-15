#!/usr/bin/env python3
"""
Integration test for DSA beneficiary functionality.

This test demonstrates the complete DSA beneficiary implementation working end-to-end,
including detection, parameter support, and error handling.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.adsets import create_adset, get_adset_details
from meta_ads_mcp.core.accounts import get_account_info


class TestDSAIntegration:
    """Integration tests for DSA beneficiary functionality"""
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_complete_workflow(self):
        """Test complete DSA beneficiary workflow from account detection to ad set creation"""
        
        # Step 1: Get account info and detect DSA requirement
        mock_account_response = {
            "id": "act_701351919139047",
            "name": "Test European Account",
            "account_status": 1,
            "business_country_code": "DE",  # Germany - DSA compliant
            "business_city": "Berlin",
            "currency": "EUR"
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_account_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_account_api.return_value = mock_account_response
                
                # Get account info and verify DSA detection
                result = await get_account_info(account_id="act_701351919139047")
                
                # Handle new return format (dictionary instead of JSON string)
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)
                
                # Verify DSA requirement is detected
                assert result_data["business_country_code"] == "DE"
                assert result_data["dsa_required"] == True
                assert "DSA (Digital Services Act)" in result_data["dsa_compliance_note"]
        
        # Step 2: Create ad set with DSA beneficiary
        mock_adset_response = {
            "id": "23842588888640185",
            "name": "Test European Ad Set",
            "status": "PAUSED",
            "dsa_beneficiary": "Test Organization GmbH"
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_adset_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_adset_api.return_value = mock_adset_response
                
                # Create ad set with DSA beneficiary
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test European Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS",
                    dsa_beneficiary="Test Organization GmbH"
                )
                
                result_data = json.loads(result)
                
                # Verify successful creation with DSA beneficiary
                assert result_data["id"] == "23842588888640185"
                assert result_data["dsa_beneficiary"] == "Test Organization GmbH"
                
                # Verify API call included DSA beneficiary parameter
                mock_adset_api.assert_called_once()
                call_args = mock_adset_api.call_args
                params = call_args[0][2]  # Third argument is params
                assert "dsa_beneficiary" in params
                assert params["dsa_beneficiary"] == "Test Organization GmbH"
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_error_handling_integration(self):
        """Test DSA beneficiary error handling in real-world scenarios"""
        
        # Test 1: Missing DSA beneficiary for European account
        mock_error_response = {
            "error": {
                "message": "Enter the person or organization that benefits from ads in this ad set",
                "type": "OAuthException",
                "code": 100
            }
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception(json.dumps(mock_error_response))
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test European Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS"
                    # No DSA beneficiary provided
                )
                
                result_data = json.loads(result)
                
                # Handle response wrapped in 'data' field by meta_api_tool decorator
                if "data" in result_data:
                    actual_data = json.loads(result_data["data"])
                else:
                    actual_data = result_data
                
                # Verify error is properly handled
                assert "error" in actual_data
                assert "benefits from ads" in actual_data["error"]
        
        # Test 2: Permission error for DSA beneficiary
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception("Permission denied: business_management permission required")
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test European Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS",
                    dsa_beneficiary="Test Organization GmbH"
                )
                
                result_data = json.loads(result)
                
                # Handle response wrapped in 'data' field by meta_api_tool decorator
                if "data" in result_data:
                    actual_data = json.loads(result_data["data"])
                else:
                    actual_data = result_data
                
                # Verify permission error is handled
                assert "error" in actual_data
                assert "permission" in actual_data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_regional_compliance_integration(self):
        """Test DSA beneficiary compliance across different regions"""
        
        # Test 1: European account (DSA required)
        mock_de_account_response = {
            "id": "act_de",
            "name": "German Account",
            "business_country_code": "DE",
            "currency": "EUR"
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_de_account_response
                
                result = await get_account_info(account_id="act_de")
                
                # Handle new return format (dictionary instead of JSON string)
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)
                
                # Verify DSA requirement for German account
                assert result_data["business_country_code"] == "DE"
                assert result_data["dsa_required"] == True
        
        # Test 2: US account (DSA not required)
        mock_us_account_response = {
            "id": "act_us",
            "name": "US Account",
            "business_country_code": "US",
            "currency": "USD"
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_us_account_response
                
                result = await get_account_info(account_id="act_us")
                
                # Handle new return format (dictionary instead of JSON string)
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)
                
                # Verify no DSA requirement for US account
                assert result_data["business_country_code"] == "US"
                assert result_data["dsa_required"] == False
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_parameter_formats_integration(self):
        """Test different DSA beneficiary parameter formats in real scenarios"""
        
        test_cases = [
            "Test Organization GmbH",
            "Test Organization, Inc.",
            "Test Organization Ltd.",
            "Test Organization AG",
            "Test Organization BV",
            "Test Organization SARL"
        ]
        
        for beneficiary_name in test_cases:
            mock_response = {
                "id": "23842588888640185",
                "name": "Test Ad Set",
                "status": "PAUSED",
                "dsa_beneficiary": beneficiary_name
            }
            
            with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
                with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                    mock_auth.return_value = "test_access_token"
                    mock_api.return_value = mock_response
                    
                    result = await create_adset(
                        account_id="act_701351919139047",
                        campaign_id="23842588888640184",
                        name="Test Ad Set",
                        optimization_goal="LINK_CLICKS",
                        billing_event="IMPRESSIONS",
                        dsa_beneficiary=beneficiary_name
                    )
                    
                    result_data = json.loads(result)
                    
                    # Verify successful creation with different formats
                    assert result_data["id"] == "23842588888640185"
                    assert result_data["dsa_beneficiary"] == beneficiary_name
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_retrieval_integration(self):
        """Test complete workflow including retrieving DSA beneficiary information"""
        
        # Step 1: Create ad set with DSA beneficiary
        mock_create_response = {
            "id": "120229746629010183",
            "name": "Test Ad Set with DSA",
            "status": "PAUSED"
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_create_response
                
                # Create ad set
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="120229656904980183",
                    name="Test Ad Set with DSA",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS",
                    dsa_beneficiary="Test Organization Inc"
                )
                
                result_data = json.loads(result)
                adset_id = result_data["id"]
                
                # Verify creation was successful
                assert adset_id == "120229746629010183"
        
        # Step 2: Retrieve ad set details including DSA beneficiary
        mock_details_response = {
            "id": "120229746629010183",
            "name": "Test Ad Set with DSA",
            "campaign_id": "120229656904980183",
            "status": "PAUSED",
            "daily_budget": "1000",
            "targeting": {
                "geo_locations": {"countries": ["US"]},
                "age_min": 25,
                "age_max": 65
            },
            "bid_amount": 200,
            "optimization_goal": "LINK_CLICKS",
            "billing_event": "IMPRESSIONS",
            "dsa_beneficiary": "Test Organization Inc"
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_details_response
                
                # Retrieve ad set details
                result = await get_adset_details(adset_id=adset_id)
                result_data = json.loads(result)
                
                # Verify DSA beneficiary field is retrieved correctly
                assert result_data["id"] == "120229746629010183"
                assert "dsa_beneficiary" in result_data
                assert result_data["dsa_beneficiary"] == "Test Organization Inc"
                
                # Verify API call included dsa_beneficiary in fields
                mock_api.assert_called_once()
                call_args = mock_api.call_args
                assert "dsa_beneficiary" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_us_account_integration(self):
        """Test DSA beneficiary behavior for US accounts (optional parameter)"""
        
        # Step 1: Verify US account doesn't require DSA
        mock_us_account_response = {
            "id": "act_701351919139047",
            "name": "US Business Account",
            "business_country_code": "US",
            "account_status": 1
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_us_account_response
                
                result = await get_account_info(account_id="act_701351919139047")
                result_data = json.loads(result)
                
                # Verify US account doesn't require DSA
                assert result_data["business_country_code"] == "US"
                assert result_data["dsa_required"] == False
        
        # Step 2: Create ad set without DSA beneficiary (should work for US)
        mock_create_response = {
            "id": "120229746624860183",
            "name": "Test US Ad Set",
            "status": "PAUSED"
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_create_response
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="120229656904980183",
                    name="Test US Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS"
                    # No DSA beneficiary provided
                )
                
                result_data = json.loads(result)
                
                # Verify creation was successful without DSA beneficiary
                assert result_data["id"] == "120229746624860183"
        
        # Step 3: Retrieve ad set details (should not have dsa_beneficiary field)
        mock_details_response = {
            "id": "120229746624860183",
            "name": "Test US Ad Set",
            "campaign_id": "120229656904980183",
            "status": "PAUSED",
            "daily_budget": "1000",
            "targeting": {
                "geo_locations": {"countries": ["US"]}
            },
            "bid_amount": 200,
            "optimization_goal": "LINK_CLICKS",
            "billing_event": "IMPRESSIONS"
            # No dsa_beneficiary field
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_details_response
                
                result = await get_adset_details(adset_id="120229746624860183")
                result_data = json.loads(result)
                
                # Verify ad set details are retrieved correctly
                assert result_data["id"] == "120229746624860183"
                assert "dsa_beneficiary" not in result_data  # Should not be present for US accounts 
    
    @pytest.mark.asyncio
    async def test_account_info_requires_account_id(self):
        """Test that get_account_info requires an account_id parameter"""
        
        with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = "test_access_token"
            
            # Test without account_id parameter
            result = await get_account_info(account_id=None)
            
            # Handle new return format (dictionary instead of JSON string)
            if isinstance(result, dict):
                result_data = result
            else:
                result_data = json.loads(result)
            
            # Verify error message for missing account_id
            assert "error" in result_data
            assert "Account ID is required" in result_data["error"]["message"]
            assert "Please specify an account_id parameter" in result_data["error"]["details"]
            assert "example" in result_data["error"]
    
    @pytest.mark.asyncio
    async def test_account_info_inaccessible_account_error(self):
        """Test that get_account_info provides helpful error for inaccessible accounts"""
        
        # Mock permission error for direct account access (first API call)
        mock_permission_error = {
            "error": {
                "message": "Insufficient access privileges",
                "type": "OAuthException",
                "code": 200
            }
        }
        
        # Mock accessible accounts response (second API call)
        mock_accessible_accounts = {
            "data": [
                {"id": "act_123", "name": "Test Account 1"},
                {"id": "act_456", "name": "Test Account 2"}
            ]
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                # First call returns permission error, second call returns accessible accounts
                mock_api.side_effect = [mock_permission_error, mock_accessible_accounts]
                
                result = await get_account_info(account_id="act_inaccessible")
                
                # Handle new return format (dictionary instead of JSON string)
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)
                
                # Verify helpful error message for inaccessible account
                assert "error" in result_data
                assert "not accessible to your user account" in result_data["error"]["message"]
                assert "accessible_accounts" in result_data["error"]
                assert "suggestion" in result_data["error"]
                assert len(result_data["error"]["accessible_accounts"]) == 2 