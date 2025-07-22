"""Regression tests for get_ad_image function JSON parsing fix.

Tests for issue where get_ad_image would throw:
'TypeError: the JSON object must be str, bytes or bytearray, not dict'

This was caused by:
1. Wrong parameter order when calling get_ad_creatives (ad_id, "", access_token instead of access_token=x, ad_id=y)
2. Incorrect JSON parsing of the @meta_api_tool decorator wrapped response

The fix:
1. Corrected the parameter order in get_ad_creatives calls
2. Updated JSON parsing to handle the wrapped response format: {"data": "JSON_STRING"}
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from meta_ads_mcp.core.ads import get_ad_image


@pytest.mark.asyncio
class TestGetAdImageRegressionFix:
    """Regression test cases for the get_ad_image JSON parsing bug fix."""
    
    async def test_get_ad_image_json_parsing_regression_fix(self):
        """Regression test: ensure get_ad_image doesn't throw JSON parsing error."""
        
        # Mock responses for the main API flow
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Test Creative", 
            "image_hash": "test_hash_123"
        }
        
        mock_image_data = {
            "data": [{
                "hash": "test_hash_123",
                "url": "https://example.com/image.jpg",
                "width": 1200,
                "height": 628,
                "name": "test_image.jpg",
                "status": "ACTIVE"
            }]
        }
        
        # Mock PIL Image processing to return a valid Image object
        mock_pil_image = MagicMock()
        mock_pil_image.mode = "RGB"
        mock_pil_image.convert.return_value = mock_pil_image
        
        mock_byte_stream = MagicMock()
        mock_byte_stream.getvalue.return_value = b"fake_jpeg_data"
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api, \
             patch('meta_ads_mcp.core.ads.download_image', new_callable=AsyncMock) as mock_download, \
             patch('meta_ads_mcp.core.ads.PILImage.open') as mock_pil_open, \
             patch('meta_ads_mcp.core.ads.io.BytesIO') as mock_bytesio:
            
            mock_api.side_effect = [mock_ad_data, mock_creative_details, mock_image_data]
            mock_download.return_value = b"fake_image_bytes"
            mock_pil_open.return_value = mock_pil_image
            mock_bytesio.return_value = mock_byte_stream
            
            # This should NOT raise "the JSON object must be str, bytes or bytearray, not dict"
            # Previously this would fail with: TypeError: the JSON object must be str, bytes or bytearray, not dict
            result = await get_ad_image(access_token="test_token", ad_id="120228922871870272")
            
            # Verify we get an Image object (success) - the exact test depends on the mocking
            # The key is that we don't get the JSON parsing error
            assert result is not None
            
            # The main regression check: if we got here without an exception, the JSON parsing is fixed
            # We might get different results based on mocking, but the critical JSON parsing should work
            
    async def test_get_ad_image_fallback_path_json_parsing(self):
        """Test the fallback path that calls get_ad_creatives handles JSON parsing correctly."""
        
        # Mock responses that trigger the fallback path (no direct image hash)
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Test Creative"
            # No image_hash - this will trigger the fallback
        }
        
        # Mock get_ad_creatives response (wrapped format that caused the original bug)
        mock_get_ad_creatives_response = json.dumps({
            "data": json.dumps({
                "data": [
                    {
                        "id": "creative_123456789",
                        "name": "Test Creative",
                        "object_story_spec": {
                            "link_data": {
                                "image_hash": "fallback_hash_123"
                            }
                        }
                    }
                ]
            })
        })
        
        mock_image_data = {
            "data": [{
                "hash": "fallback_hash_123",
                "url": "https://example.com/fallback_image.jpg",
                "width": 1200,
                "height": 628
            }]
        }
        
        # Mock PIL Image processing
        mock_pil_image = MagicMock()
        mock_pil_image.mode = "RGB"
        mock_pil_image.convert.return_value = mock_pil_image
        
        mock_byte_stream = MagicMock()
        mock_byte_stream.getvalue.return_value = b"fake_jpeg_data"
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api, \
             patch('meta_ads_mcp.core.ads.get_ad_creatives', new_callable=AsyncMock) as mock_get_creatives, \
             patch('meta_ads_mcp.core.ads.download_image', new_callable=AsyncMock) as mock_download, \
             patch('meta_ads_mcp.core.ads.PILImage.open') as mock_pil_open, \
             patch('meta_ads_mcp.core.ads.io.BytesIO') as mock_bytesio:
            
            mock_api.side_effect = [mock_ad_data, mock_creative_details, mock_image_data]
            mock_get_creatives.return_value = mock_get_ad_creatives_response
            mock_download.return_value = b"fake_image_bytes"
            mock_pil_open.return_value = mock_pil_image
            mock_bytesio.return_value = mock_byte_stream
            
            # This should handle the wrapped JSON response correctly
            # Previously would fail: TypeError: the JSON object must be str, bytes or bytearray, not dict
            result = await get_ad_image(access_token="test_token", ad_id="120228922871870272")
            
            # Verify the fallback path worked - key is no JSON parsing exception
            assert result is not None
            # Verify get_ad_creatives was called (fallback path was triggered)
            mock_get_creatives.assert_called_once()
    
    async def test_get_ad_image_no_ad_id(self):
        """Test get_ad_image with no ad_id provided."""
        
        result = await get_ad_image(access_token="test_token", ad_id=None)
        
        # Should return error string, not throw JSON parsing error
        assert isinstance(result, str)
        assert "Error: No ad ID provided" in result
    
    async def test_get_ad_image_parameter_order_regression(self):
        """Regression test: ensure get_ad_creatives is called with correct parameter order."""
        
        # This test ensures we don't regress to calling get_ad_creatives(ad_id, "", access_token)
        # which was the original bug
        
        mock_ad_data = {
            "account_id": "act_123456789", 
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Test Creative"
            # No image_hash to trigger fallback
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api, \
             patch('meta_ads_mcp.core.ads.get_ad_creatives', new_callable=AsyncMock) as mock_get_creatives:
            
            mock_api.side_effect = [mock_ad_data, mock_creative_details]
            mock_get_creatives.return_value = json.dumps({"data": json.dumps({"data": []})})
            
            # Call get_ad_image - it should reach the fallback path
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify get_ad_creatives was called with correct parameter names (not positional)
            mock_get_creatives.assert_called_once_with(ad_id="test_ad_id", access_token="test_token")
            
            # The key regression test: this should not have raised a JSON parsing error 