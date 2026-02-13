#!/usr/bin/env python3
"""
Unit tests for DSA (Digital Services Act) beneficiary functionality in Meta Ads MCP.

This module tests the implementation of DSA beneficiary field support for ad set creation,
including detection of DSA requirements, parameter validation, and error handling.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from meta_ads_mcp.core.adsets import create_adset, get_adset_details
from meta_ads_mcp.core.accounts import get_account_info


class TestDSABeneficiaryDetection:
    """Test cases for detecting DSA beneficiary requirements"""
    
    @pytest.mark.asyncio
    async def test_dsa_requirement_detection_business_account(self):
        """Test DSA requirement detection for European business accounts"""
        mock_account_response = {
            "id": "act_701351919139047",
            "name": "Test European Business Account",
            "account_status": 1,
            "business_country_code": "DE",  # Germany - DSA compliant
            "business_city": "Berlin",
            "currency": "EUR"
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_account_response
                
                result = await get_account_info(account_id="act_701351919139047")
                
                # Handle new return format (dictionary instead of JSON string)
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)
                
                # Verify account info is retrieved
                assert result_data["id"] == "act_701351919139047"
                assert result_data["business_country_code"] == "DE"
                
                # Verify DSA requirement detection
                assert "dsa_required" in result_data or "business_country_code" in result_data
    
    @pytest.mark.asyncio
    async def test_dsa_requirement_detection_non_dsa_region(self):
        """Test detection for non-DSA compliant regions"""
        mock_account_response = {
            "id": "act_123456789",
            "name": "Test US Account",
            "account_status": 1,
            "business_country_code": "US",  # US - not DSA compliant
            "business_city": "New York",
            "currency": "USD"
        }
        
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_account_response
                
                result = await get_account_info(account_id="act_123456789")
                
                # Handle new return format (dictionary instead of JSON string)
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)
                
                # Verify no DSA requirement for US accounts
                assert result_data["business_country_code"] == "US"
    
    @pytest.mark.asyncio
    async def test_dsa_requirement_detection_error_handling(self):
        """Test error handling when account info cannot be retrieved"""
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception("API Error")
                
                result = await get_account_info(account_id="act_invalid")
                
                # Handle new return format (dictionary instead of JSON string)
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)
                
                # Verify error is properly handled
                assert "error" in result_data
    
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


class TestDSABeneficiaryParameter:
    """Test cases for DSA beneficiary parameter support"""
    
    @pytest.mark.asyncio
    async def test_create_adset_with_dsa_beneficiary_success(self):
        """Test successful ad set creation with DSA beneficiary parameter"""
        mock_response = {
            "id": "23842588888640185",
            "name": "Test Ad Set with DSA",
            "status": "PAUSED",
            "dsa_beneficiary": "Test Organization GmbH"
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_response
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test Ad Set with DSA",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS",
                    dsa_beneficiary="Test Organization GmbH"
                )
                
                # Verify the API was called with DSA beneficiary parameter
                mock_api.assert_called_once()
                call_args = mock_api.call_args
                assert "dsa_beneficiary" in str(call_args)
                
                # Verify response contains ad set ID
                result_data = json.loads(result)
                assert "id" in result_data
    
    @pytest.mark.asyncio
    async def test_create_adset_with_dsa_beneficiary_validation_error(self):
        """Test error handling when DSA beneficiary parameter is invalid"""
        mock_error_response = {
            "error": {
                "message": "DSA beneficiary required for European compliance",
                "type": "OAuthException",
                "code": 100
            }
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception("DSA beneficiary required for European compliance")
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS"
                    # No DSA beneficiary provided
                )
                
                # Verify error message is clear and actionable
                result_data = json.loads(result)
                
                # Handle response wrapped in 'data' field by meta_api_tool decorator
                if "data" in result_data:
                    actual_data = json.loads(result_data["data"])
                else:
                    actual_data = result_data
                
                assert "DSA beneficiary required" in actual_data.get("error", "")
    
    @pytest.mark.asyncio
    async def test_create_adset_without_dsa_beneficiary_dsa_required(self):
        """Test error when DSA beneficiary is required but not provided"""
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception("Enter the person or organization that benefits from ads in this ad set")
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS"
                    # No DSA beneficiary provided
                )
                
                # Verify error message is clear and actionable
                result_data = json.loads(result)
                
                # Handle response wrapped in 'data' field by meta_api_tool decorator
                if "data" in result_data:
                    actual_data = json.loads(result_data["data"])
                else:
                    actual_data = result_data
                
                assert "benefits from ads" in actual_data.get("error", "")
    
    @pytest.mark.asyncio
    async def test_create_adset_dsa_beneficiary_in_targeting(self):
        """Test that DSA beneficiary is not added to targeting spec"""
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = {"id": "23842588888640185"}
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS",
                    targeting={"geo_locations": {"countries": ["DE"]}},
                    dsa_beneficiary="Test Organization GmbH"
                )
                
                # Verify the API was called
                mock_api.assert_called_once()
                call_args = mock_api.call_args
                
                # Verify DSA beneficiary is sent as separate parameter, not in targeting
                call_str = str(call_args)
                assert "dsa_beneficiary" in call_str
                assert "Test Organization GmbH" in call_str
    
    @pytest.mark.asyncio
    async def test_create_adset_dsa_beneficiary_parameter_formats(self):
        """Test different formats for DSA beneficiary parameter"""
        test_cases = [
            "Simple Organization",
            "Organization with Special Chars: GmbH & Co. KG",
            "Organization with Numbers: Test123 Inc.",
            "Very Long Organization Name That Exceeds Normal Limits But Should Still Work"
        ]
        
        for beneficiary_name in test_cases:
            with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
                with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                    mock_auth.return_value = "test_access_token"
                    mock_api.return_value = {"id": "23842588888640185"}
                    
                    result = await create_adset(
                        account_id="act_701351919139047",
                        campaign_id="23842588888640184",
                        name="Test Ad Set",
                        optimization_goal="LINK_CLICKS",
                        billing_event="IMPRESSIONS",
                        dsa_beneficiary=beneficiary_name
                    )
                    
                    # Verify the API was called with the beneficiary name
                    mock_api.assert_called_once()
                    call_args = mock_api.call_args
                    assert beneficiary_name in str(call_args)


class TestDSAPermissionHandling:
    """Test cases for permission-related DSA beneficiary issues"""
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_missing_business_management_permission(self):
        """Test error handling when business_management permissions are missing"""
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception("Permission denied: business_management permission required")
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS",
                    dsa_beneficiary="Test Organization GmbH"
                )
                
                # Verify permission error is handled
                result_data = json.loads(result)
                
                # Handle response wrapped in 'data' field by meta_api_tool decorator
                if "data" in result_data:
                    actual_data = json.loads(result_data["data"])
                else:
                    actual_data = result_data
                
                assert "permission" in actual_data.get("error", "").lower()
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_api_limitation_handling(self):
        """Test handling when API doesn't support dsa_beneficiary parameter"""
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception("Parameter dsa_beneficiary is not supported")
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS",
                    dsa_beneficiary="Test Organization GmbH"
                )
                
                # Verify API limitation error is handled
                result_data = json.loads(result)
                
                # Handle response wrapped in 'data' field by meta_api_tool decorator
                if "data" in result_data:
                    actual_data = json.loads(result_data["data"])
                else:
                    actual_data = result_data
                
                assert "not supported" in actual_data.get("error", "").lower()


class TestDSARegionalCompliance:
    """Test cases for regional DSA compliance"""
    
    @pytest.mark.asyncio
    async def test_dsa_compliance_european_regions(self):
        """Test DSA compliance for European regions"""
        european_countries = ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "IE", "DK", "SE", "FI", "NO"]
        
        for country_code in european_countries:
            mock_account_response = {
                "id": f"act_{country_code.lower()}",
                "name": f"Test {country_code} Account",
                "account_status": 1,
                "business_country_code": country_code,
                "currency": "EUR"
            }
            
            with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
                with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                    mock_auth.return_value = "test_access_token"
                    mock_api.return_value = mock_account_response
                    
                    result = await get_account_info(account_id=f"act_{country_code.lower()}")
                    result_data = json.loads(result)
                    
                    # Verify European countries are detected as DSA compliant
                    assert result_data["business_country_code"] == country_code
    
    @pytest.mark.asyncio
    async def test_dsa_compliance_non_european_regions(self):
        """Test DSA compliance for non-European regions"""
        non_european_countries = ["US", "CA", "AU", "JP", "BR", "IN"]
        
        for country_code in non_european_countries:
            mock_account_response = {
                "id": f"act_{country_code.lower()}",
                "name": f"Test {country_code} Account",
                "account_status": 1,
                "business_country_code": country_code,
                "currency": "USD"
            }
            
            with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
                with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                    mock_auth.return_value = "test_access_token"
                    mock_api.return_value = mock_account_response
                    
                    result = await get_account_info(account_id=f"act_{country_code.lower()}")
                    result_data = json.loads(result)
                    
                    # Verify non-European countries are not DSA compliant
                    assert result_data["business_country_code"] == country_code
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_validation_by_region(self):
        """Test DSA beneficiary validation based on region"""
        # Test European account (should require DSA beneficiary)
        european_mock_response = {
            "id": "act_de",
            "name": "German Account",
            "business_country_code": "DE"
        }
        
        # Test US account (should not require DSA beneficiary)
        us_mock_response = {
            "id": "act_us",
            "name": "US Account",
            "business_country_code": "US"
        }
        
        # Test European account
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = european_mock_response
                
                result = await get_account_info(account_id="act_de")
                result_data = json.loads(result)
                
                assert result_data["business_country_code"] == "DE"
        
        # Test US account
        with patch('meta_ads_mcp.core.accounts.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = us_mock_response
                
                result = await get_account_info(account_id="act_us")
                result_data = json.loads(result)
                
                assert result_data["business_country_code"] == "US"


class TestDSAErrorHandling:
    """Test cases for comprehensive DSA error handling"""
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_clear_error_message(self):
        """Test that DSA-related errors provide clear, actionable messages"""
        error_scenarios = [
            ("DSA beneficiary required for European compliance", "DSA beneficiary"),
            ("Enter the person or organization that benefits from ads", "benefits from ads"),
            ("Permission denied: business_management required", "permission"),
            ("Parameter dsa_beneficiary is not supported", "not supported")
        ]
        
        for error_message, expected_keyword in error_scenarios:
            with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
                with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                    mock_auth.return_value = "test_access_token"
                    mock_api.side_effect = Exception(error_message)
                    
                    result = await create_adset(
                        account_id="act_701351919139047",
                        campaign_id="23842588888640184",
                        name="Test Ad Set",
                        optimization_goal="LINK_CLICKS",
                        billing_event="IMPRESSIONS"
                    )
                    
                    # Verify error message contains expected keyword
                    result_data = json.loads(result)
                    
                    # Handle response wrapped in 'data' field by meta_api_tool decorator
                    if "data" in result_data:
                        actual_data = json.loads(result_data["data"])
                    else:
                        actual_data = result_data
                    
                    assert expected_keyword.lower() in actual_data.get("error", "").lower()
    
    @pytest.mark.asyncio
    async def test_dsa_beneficiary_fallback_behavior(self):
        """Test fallback behavior for unexpected DSA-related errors"""
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception("Unexpected DSA-related error")
                
                result = await create_adset(
                    account_id="act_701351919139047",
                    campaign_id="23842588888640184",
                    name="Test Ad Set",
                    optimization_goal="LINK_CLICKS",
                    billing_event="IMPRESSIONS"
                )
                
                # Verify fallback error handling
                result_data = json.loads(result)
                
                # Handle response wrapped in 'data' field by meta_api_tool decorator
                if "data" in result_data:
                    actual_data = json.loads(result_data["data"])
                else:
                    actual_data = result_data
                
                assert "error" in actual_data


class TestDSABeneficiaryRetrieval:
    """Test cases for retrieving DSA beneficiary information from ad sets"""
    
    @pytest.mark.asyncio
    async def test_get_adset_details_with_dsa_beneficiary(self):
        """Test retrieving ad set details that include DSA beneficiary field"""
        mock_adset_response = {
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
                mock_api.return_value = mock_adset_response
                
                result = await get_adset_details(adset_id="120229746629010183")
                result_data = json.loads(result)
                
                # Verify DSA beneficiary field is present and correct
                assert "dsa_beneficiary" in result_data
                assert result_data["dsa_beneficiary"] == "Test Organization Inc"
                assert result_data["id"] == "120229746629010183"
    
    @pytest.mark.asyncio
    async def test_get_adset_details_without_dsa_beneficiary(self):
        """Test retrieving ad set details that don't have DSA beneficiary field"""
        mock_adset_response = {
            "id": "120229746624860183",
            "name": "Test Ad Set without DSA",
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
            "billing_event": "IMPRESSIONS"
            # No dsa_beneficiary field
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_adset_response
                
                result = await get_adset_details(adset_id="120229746624860183")
                result_data = json.loads(result)
                
                # Verify ad set details are retrieved correctly
                assert result_data["id"] == "120229746624860183"
                assert "dsa_beneficiary" not in result_data  # Should not be present
    
    @pytest.mark.asyncio
    async def test_get_adset_details_empty_dsa_beneficiary(self):
        """Test retrieving ad set details with empty DSA beneficiary field"""
        mock_adset_response = {
            "id": "120229746629010183",
            "name": "Test Ad Set with Empty DSA",
            "campaign_id": "120229656904980183",
            "status": "PAUSED",
            "daily_budget": "1000",
            "targeting": {
                "geo_locations": {"countries": ["US"]}
            },
            "bid_amount": 200,
            "optimization_goal": "LINK_CLICKS",
            "billing_event": "IMPRESSIONS",
            "dsa_beneficiary": ""  # Empty string
        }
        
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = mock_adset_response
                
                result = await get_adset_details(adset_id="120229746629010183")
                result_data = json.loads(result)
                
                # Verify empty DSA beneficiary field is handled correctly
                assert "dsa_beneficiary" in result_data
                assert result_data["dsa_beneficiary"] == ""
    
    @pytest.mark.asyncio
    async def test_get_adset_details_dsa_beneficiary_field_requested(self):
        """Test that the API request includes dsa_beneficiary in the fields parameter"""
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.return_value = {"id": "120229746629010183"}
                
                result = await get_adset_details(adset_id="120229746629010183")
                
                # Verify the API was called with dsa_beneficiary in fields
                mock_api.assert_called_once()
                call_args = mock_api.call_args
                assert "dsa_beneficiary" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_get_adset_details_error_handling(self):
        """Test error handling when retrieving ad set details fails"""
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
            with patch('meta_ads_mcp.core.auth.get_current_access_token', new_callable=AsyncMock) as mock_auth:
                mock_auth.return_value = "test_access_token"
                mock_api.side_effect = Exception("Ad set not found")
                
                result = await get_adset_details(adset_id="invalid_adset_id")
                
                # Handle response format - could be dict or JSON string
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)
                
                # Verify error is properly handled
                assert "error" in result_data 