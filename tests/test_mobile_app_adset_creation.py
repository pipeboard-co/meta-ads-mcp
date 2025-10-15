#!/usr/bin/env python3
"""
Unit Tests for Mobile App Adset Creation Functionality

This test suite validates the mobile app parameters implementation for the
create_adset function in meta_ads_mcp/core/adsets.py.

Test cases cover:
- Mobile app adset creation success scenarios
- promoted_object parameter validation and formatting
- destination_type parameter validation
- Mobile app specific error handling
- Cross-platform mobile app support (iOS, Android)
- Integration with APP_INSTALLS optimization goal

Usage:
    uv run python -m pytest tests/test_mobile_app_adset_creation.py -v

Related to Issue #008: Missing Mobile App Parameters in create_adset Function
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import the function to test
from meta_ads_mcp.core.adsets import create_adset


class TestMobileAppAdsetCreation:
    """Test suite for mobile app adset creation functionality"""
    
    @pytest.fixture
    def mock_api_request(self):
        """Mock for the make_api_request function"""
        with patch('meta_ads_mcp.core.adsets.make_api_request') as mock:
            mock.return_value = {
                "id": "test_mobile_adset_id",
                "name": "Test Mobile App Adset",
                "optimization_goal": "APP_INSTALLS",
                "promoted_object": {
                    "application_id": "123456789012345",
                    "object_store_url": "https://apps.apple.com/app/id123456789"
                },
                "destination_type": "APP_STORE"
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
    def valid_mobile_app_params(self):
        """Valid mobile app parameters for testing"""
        return {
            "account_id": "act_123456789",
            "campaign_id": "campaign_123456789",
            "name": "Test Mobile App Adset",
            "optimization_goal": "APP_INSTALLS",
            "billing_event": "IMPRESSIONS",
            "targeting": {
                "age_min": 18,
                "age_max": 65,
                "app_install_state": "not_installed",
                "geo_locations": {"countries": ["US"]},
                "user_device": ["Android_Smartphone", "iPhone"],
                "user_os": ["Android", "iOS"]
            }
        }
    
    @pytest.fixture
    def ios_promoted_object(self):
        """Valid iOS app promoted object"""
        return {
            "application_id": "123456789012345",
            "object_store_url": "https://apps.apple.com/app/id123456789",
            "custom_event_type": "APP_INSTALL"
        }
    
    @pytest.fixture
    def android_promoted_object(self):
        """Valid Android app promoted object"""
        return {
            "application_id": "987654321098765",
            "object_store_url": "https://play.google.com/store/apps/details?id=com.example.app",
            "custom_event_type": "APP_INSTALL"
        }
    
    @pytest.fixture 
    def promoted_object_with_pixel(self):
        """Promoted object with Facebook pixel for tracking"""
        return {
            "application_id": "123456789012345",
            "object_store_url": "https://apps.apple.com/app/id123456789",
            "custom_event_type": "APP_INSTALL",
            "pixel_id": "pixel_123456789"
        }

    # Test: Mobile App Adset Creation Success
    @pytest.mark.asyncio
    async def test_mobile_app_adset_creation_success_ios(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params, ios_promoted_object
    ):
        """Test successful iOS mobile app adset creation"""
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=ios_promoted_object,
            destination_type="APP_STORE"
        )
        
        # Parse the result
        result_data = json.loads(result)
        
        # Verify the API was called with correct parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        
        # Check endpoint (first argument)
        assert call_args[0][0] == f"{valid_mobile_app_params['account_id']}/adsets"
        
        # Check parameters (third argument)
        params = call_args[0][2]
        assert 'promoted_object' in params
        assert 'destination_type' in params
        
        # Verify promoted_object is properly JSON-encoded
        promoted_obj_param = json.loads(params['promoted_object']) if isinstance(params['promoted_object'], str) else params['promoted_object']
        assert promoted_obj_param['application_id'] == ios_promoted_object['application_id']
        assert promoted_obj_param['object_store_url'] == ios_promoted_object['object_store_url']
        
        # Verify destination_type
        assert params['destination_type'] == "APP_STORE"
        
        # Verify response structure
        assert 'id' in result_data
        assert result_data['optimization_goal'] == "APP_INSTALLS"

    @pytest.mark.asyncio
    async def test_mobile_app_adset_creation_success_android(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params, android_promoted_object
    ):
        """Test successful Android mobile app adset creation"""
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=android_promoted_object,
            destination_type="APP_STORE"
        )
        
        # Parse the result  
        result_data = json.loads(result)
        
        # Verify the API was called
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        
        # Verify Android-specific promoted_object
        promoted_obj_param = json.loads(params['promoted_object']) if isinstance(params['promoted_object'], str) else params['promoted_object']
        assert promoted_obj_param['application_id'] == android_promoted_object['application_id']
        assert "play.google.com" in promoted_obj_param['object_store_url']
        
        # Verify response
        assert 'id' in result_data

    @pytest.mark.asyncio
    async def test_mobile_app_adset_with_pixel_tracking(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params, promoted_object_with_pixel
    ):
        """Test mobile app adset creation with Facebook pixel tracking"""
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=promoted_object_with_pixel,
            destination_type="APP_STORE"
        )
        
        # Verify pixel_id is included
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        promoted_obj_param = json.loads(params['promoted_object']) if isinstance(params['promoted_object'], str) else params['promoted_object']
        
        assert 'pixel_id' in promoted_obj_param
        assert promoted_obj_param['pixel_id'] == promoted_object_with_pixel['pixel_id']

    # Test: Parameter Validation
    @pytest.mark.asyncio
    async def test_invalid_promoted_object_missing_application_id(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params
    ):
        """Test validation error for promoted_object missing application_id"""
        
        invalid_promoted_object = {
            "object_store_url": "https://apps.apple.com/app/id123456789",
            "custom_event_type": "APP_INSTALL"
        }
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=invalid_promoted_object,
            destination_type="APP_STORE"
        )
        
        result_data = json.loads(result)
        
        # Should return validation error - check for data wrapper format
        if "data" in result_data:
            error_data = json.loads(result_data["data"]) 
            assert 'error' in error_data
            assert 'application_id' in error_data['error'].lower()
        else:
            assert 'error' in result_data
            assert 'application_id' in result_data['error'].lower()

    @pytest.mark.asyncio 
    async def test_invalid_promoted_object_missing_store_url(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params
    ):
        """Test validation error for promoted_object missing object_store_url"""
        
        invalid_promoted_object = {
            "application_id": "123456789012345",
            "custom_event_type": "APP_INSTALL"
        }
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=invalid_promoted_object,
            destination_type="APP_STORE"
        )
        
        result_data = json.loads(result)
        
        # Should return validation error - check for data wrapper format
        if "data" in result_data:
            error_data = json.loads(result_data["data"]) 
            assert 'error' in error_data
            assert 'object_store_url' in error_data['error'].lower()
        else:
            assert 'error' in result_data
            assert 'object_store_url' in result_data['error'].lower()

    @pytest.mark.asyncio
    async def test_invalid_destination_type(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params, ios_promoted_object
    ):
        """Test validation error for invalid destination_type value"""
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=ios_promoted_object,
            destination_type="INVALID_TYPE"
        )
        
        result_data = json.loads(result)
        
        # Should return validation error - check for data wrapper format
        if "data" in result_data:
            error_data = json.loads(result_data["data"]) 
            assert 'error' in error_data
            assert 'destination_type' in error_data['error'].lower()
        else:
            assert 'error' in result_data
            assert 'destination_type' in result_data['error'].lower()

    @pytest.mark.asyncio
    async def test_app_installs_requires_promoted_object(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params
    ):
        """Test that APP_INSTALLS optimization goal requires promoted_object"""
        
        result = await create_adset(
            **valid_mobile_app_params,
            # Missing promoted_object
            destination_type="APP_STORE"
        )
        
        result_data = json.loads(result)
        
        # Should return validation error - check for data wrapper format
        if "data" in result_data:
            error_data = json.loads(result_data["data"]) 
            assert 'error' in error_data
            assert 'promoted_object' in error_data['error'].lower()
            assert 'app_installs' in error_data['error'].lower()
        else:
            assert 'error' in result_data
            assert 'promoted_object' in result_data['error'].lower()
            assert 'app_installs' in result_data['error'].lower()

    # Test: Cross-platform Support
    @pytest.mark.asyncio
    async def test_ios_app_store_url_validation(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params
    ):
        """Test iOS App Store URL format validation"""
        
        ios_promoted_object = {
            "application_id": "123456789012345",
            "object_store_url": "https://apps.apple.com/app/id123456789",
            "custom_event_type": "APP_INSTALL"
        }
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=ios_promoted_object,
            destination_type="APP_STORE"
        )
        
        result_data = json.loads(result)
        
        # Should succeed for valid iOS URL
        assert 'error' not in result_data or result_data.get('error') is None

    @pytest.mark.asyncio
    async def test_google_play_url_validation(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params
    ):
        """Test Google Play Store URL format validation"""
        
        android_promoted_object = {
            "application_id": "987654321098765",
            "object_store_url": "https://play.google.com/store/apps/details?id=com.example.app",
            "custom_event_type": "APP_INSTALL"
        }
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=android_promoted_object,
            destination_type="APP_STORE"
        )
        
        result_data = json.loads(result)
        
        # Should succeed for valid Google Play URL
        assert 'error' not in result_data or result_data.get('error') is None

    @pytest.mark.asyncio
    async def test_invalid_store_url_format(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params
    ):
        """Test validation error for invalid app store URL format"""
        
        invalid_promoted_object = {
            "application_id": "123456789012345",
            "object_store_url": "https://example.com/invalid-url",
            "custom_event_type": "APP_INSTALL"
        }
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=invalid_promoted_object,
            destination_type="APP_STORE"
        )
        
        result_data = json.loads(result)
        
        # Should return validation error for invalid URL - check for data wrapper format
        if "data" in result_data:
            error_data = json.loads(result_data["data"]) 
            assert 'error' in error_data
            assert 'store url' in error_data['error'].lower() or 'object_store_url' in error_data['error'].lower()
        else:
            assert 'error' in result_data
            assert 'store url' in result_data['error'].lower() or 'object_store_url' in result_data['error'].lower()

    # Test: Destination Type Variations
    @pytest.mark.asyncio
    async def test_deeplink_destination_type(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params, ios_promoted_object
    ):
        """Test DEEPLINK destination_type"""
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=ios_promoted_object,
            destination_type="DEEPLINK"
        )
        
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params['destination_type'] == "DEEPLINK"

    @pytest.mark.asyncio
    async def test_app_install_destination_type(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params, ios_promoted_object
    ):
        """Test APP_INSTALL destination_type"""
        
        result = await create_adset(
            **valid_mobile_app_params,
            promoted_object=ios_promoted_object,
            destination_type="APP_INSTALL"
        )
        
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params['destination_type'] == "APP_INSTALL"

    @pytest.mark.asyncio
    async def test_on_ad_destination_type_for_lead_generation(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params
    ):
        """Test ON_AD destination_type for lead generation campaigns (Issue #009 fix)"""
        
        # Create a lead generation adset configuration (without promoted_object since it's for lead gen, not mobile apps)
        lead_gen_params = valid_mobile_app_params.copy()
        lead_gen_params.update({
            "optimization_goal": "LEAD_GENERATION",
            "billing_event": "IMPRESSIONS"
        })
        
        result = await create_adset(
            **lead_gen_params,
            destination_type="ON_AD"
        )
        
        # Should pass validation and include destination_type in API call
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params['destination_type'] == "ON_AD"

    @pytest.mark.asyncio
    async def test_on_ad_validation_passes(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params
    ):
        """Test that ON_AD destination_type passes validation (Issue #009 regression test)"""
        
        # Use parameters that work with ON_AD (lead generation, not mobile app)
        lead_gen_params = valid_mobile_app_params.copy()
        lead_gen_params.update({
            "optimization_goal": "LEAD_GENERATION",
            "billing_event": "IMPRESSIONS"
        })
        
        result = await create_adset(
            **lead_gen_params,
            destination_type="ON_AD"
        )
        
        result_data = json.loads(result)
        
        # Should NOT return a validation error about destination_type
        # Before the fix, this would return: "Invalid destination_type: ON_AD" 
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" not in error_data or "destination_type" not in error_data.get("error", "").lower()
        else:
            assert "error" not in result_data or "destination_type" not in result_data.get("error", "").lower()

    # Test: Error Handling
    @pytest.mark.asyncio
    async def test_meta_api_error_handling(
        self, mock_auth_manager, valid_mobile_app_params, ios_promoted_object
    ):
        """Test handling of Meta API errors for mobile app adsets"""
        
        with patch('meta_ads_mcp.core.adsets.make_api_request') as mock_api:
            # Mock Meta API error response
            mock_api.side_effect = Exception("HTTP Error: 400 - Select a dataset and conversion event for your ad set")
            
            result = await create_adset(
                **valid_mobile_app_params,
                promoted_object=ios_promoted_object,
                destination_type="APP_STORE"
            )
            
            result_data = json.loads(result)
            
            # Should handle the error gracefully - check for data wrapper format
            if "data" in result_data:
                error_data = json.loads(result_data["data"]) 
                assert 'error' in error_data
                # Check for error text in either error message or details
                error_text = error_data.get('error', '').lower()
                details_text = error_data.get('details', '').lower()
                assert 'dataset' in error_text or 'conversion event' in error_text or \
                       'dataset' in details_text or 'conversion event' in details_text
            else:
                assert 'error' in result_data
                error_text = result_data.get('error', '').lower()
                details_text = result_data.get('details', '').lower()
                assert 'dataset' in error_text or 'conversion event' in error_text or \
                       'dataset' in details_text or 'conversion event' in details_text

    # Test: Backward Compatibility
    @pytest.mark.asyncio
    async def test_backward_compatibility_non_mobile_campaigns(
        self, mock_api_request, mock_auth_manager
    ):
        """Test that non-mobile campaigns still work without mobile app parameters"""
        
        non_mobile_params = {
            "account_id": "act_123456789",
            "campaign_id": "campaign_123456789", 
            "name": "Test Web Adset",
            "optimization_goal": "LINK_CLICKS",
            "billing_event": "LINK_CLICKS",
            "targeting": {
                "age_min": 18,
                "age_max": 65,
                "geo_locations": {"countries": ["US"]}
            }
        }
        
        result = await create_adset(**non_mobile_params)
        
        # Should work without mobile app parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        
        # Should not include mobile app parameters
        assert 'promoted_object' not in params
        assert 'destination_type' not in params

    @pytest.mark.asyncio
    async def test_optional_mobile_parameters(
        self, mock_api_request, mock_auth_manager, valid_mobile_app_params, ios_promoted_object
    ):
        """Test that mobile app parameters are optional for non-APP_INSTALLS campaigns"""
        
        non_app_install_params = valid_mobile_app_params.copy()
        non_app_install_params['optimization_goal'] = "REACH"
        
        result = await create_adset(
            **non_app_install_params,
            # Mobile app parameters should be optional for non-APP_INSTALLS
            promoted_object=ios_promoted_object,
            destination_type="APP_STORE"
        )
        
        # Should work and include mobile parameters if provided
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        
        # Mobile parameters should be included if provided
        assert 'promoted_object' in params
        assert 'destination_type' in params