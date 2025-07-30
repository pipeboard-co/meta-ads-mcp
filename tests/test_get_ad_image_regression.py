"""Regression tests for get_ad_image function fixes.

Tests for multiple issues that were fixed:

1. JSON Parsing Error: 'TypeError: the JSON object must be str, bytes or bytearray, not dict'
   - Caused by wrong parameter order and incorrect JSON parsing
   - Fixed by correcting parameter order and JSON parsing logic

2. Missing Image Hash Support: "Error: No image hashes found in creative"
   - Many modern creatives don't have image_hash but have direct URLs
   - Fixed by adding direct URL fallback using image_urls_for_viewing and thumbnail_url

3. Image Quality Issue: Function was returning profile thumbnails instead of ad creative images
   - Fixed by prioritizing image_urls_for_viewing over thumbnail_url
   - Added proper fallback hierarchy: image_urls_for_viewing > image_url > object_story_spec.picture > thumbnail_url

The fixes enable get_ad_image to work with both traditional hash-based and modern URL-based creatives,
and ensure high-quality images are returned instead of thumbnails.
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
    
    async def test_get_ad_image_direct_url_fallback_with_image_urls_for_viewing(self):
        """Test direct URL fallback using image_urls_for_viewing when no image_hash found."""
        
        # Mock responses for modern creative without image_hash
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Modern Creative"
            # No image_hash - this will trigger fallback
        }
        
        # Mock get_ad_creatives response with direct URLs
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789",
                    "name": "Modern Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://example.com/thumb.jpg",
                    "image_urls_for_viewing": [
                        "https://example.com/full_image.jpg",
                        "https://example.com/alt_image.jpg"
                    ]
                }
            ]
        })
        
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
            
            mock_api.side_effect = [mock_ad_data, mock_creative_details]
            mock_get_creatives.return_value = mock_get_ad_creatives_response
            mock_download.return_value = b"fake_image_bytes"
            mock_pil_open.return_value = mock_pil_image
            mock_bytesio.return_value = mock_byte_stream
            
            # This should use direct URL fallback successfully
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify it used the direct URL approach
            assert result is not None
            mock_get_creatives.assert_called_once()
            mock_download.assert_called_once_with("https://example.com/full_image.jpg")
    
    async def test_get_ad_image_direct_url_fallback_with_thumbnail_url_only(self):
        """Test direct URL fallback using thumbnail_url when image_urls_for_viewing not available."""
        
        # Mock responses for creative with only thumbnail_url
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Thumbnail Only Creative"
            # No image_hash
        }
        
        # Mock get_ad_creatives response with only thumbnail_url
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789",
                    "name": "Thumbnail Only Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://example.com/thumb_only.jpg"
                    # No image_urls_for_viewing
                }
            ]
        })
        
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
            
            mock_api.side_effect = [mock_ad_data, mock_creative_details]
            mock_get_creatives.return_value = mock_get_ad_creatives_response
            mock_download.return_value = b"fake_image_bytes"
            mock_pil_open.return_value = mock_pil_image
            mock_bytesio.return_value = mock_byte_stream
            
            # This should fall back to thumbnail_url
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify it used the thumbnail URL
            assert result is not None
            mock_download.assert_called_once_with("https://example.com/thumb_only.jpg")
    
    async def test_get_ad_image_no_direct_urls_available(self):
        """Test error handling when no direct URLs are available."""
        
        # Mock responses for creative without any URLs
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "No URLs Creative"
            # No image_hash
        }
        
        # Mock get_ad_creatives response without URLs
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789", 
                    "name": "No URLs Creative",
                    "status": "ACTIVE"
                    # No thumbnail_url or image_urls_for_viewing
                }
            ]
        })
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api, \
             patch('meta_ads_mcp.core.ads.get_ad_creatives', new_callable=AsyncMock) as mock_get_creatives:
            
            mock_api.side_effect = [mock_ad_data, mock_creative_details]
            mock_get_creatives.return_value = mock_get_ad_creatives_response
            
            # This should return appropriate error
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Should get error about no URLs
            assert isinstance(result, str)
            assert "No image URLs found" in result
    
    async def test_get_ad_image_direct_url_download_failure(self):
        """Test error handling when direct URL download fails."""
        
        # Mock responses for creative with URLs but download failure
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Download Fail Creative"
        }
        
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789",
                    "name": "Download Fail Creative",
                    "image_urls_for_viewing": ["https://example.com/broken_image.jpg"]
                }
            ]
        })
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api, \
             patch('meta_ads_mcp.core.ads.get_ad_creatives', new_callable=AsyncMock) as mock_get_creatives, \
             patch('meta_ads_mcp.core.ads.download_image', new_callable=AsyncMock) as mock_download:
            
            mock_api.side_effect = [mock_ad_data, mock_creative_details]
            mock_get_creatives.return_value = mock_get_ad_creatives_response
            mock_download.return_value = None  # Simulate download failure
            
            # This should return download error
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Should get error about download failure
            assert isinstance(result, str)
            assert "Failed to download image from direct URL" in result
    
    async def test_get_ad_image_quality_improvement_prioritizes_high_quality(self):
        """Test that the image quality improvement correctly prioritizes high-quality images over thumbnails."""
        
        # Mock responses for creative with both high-quality and thumbnail URLs
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Quality Test Creative"
        }
        
        # Mock get_ad_creatives response with both URLs
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789",
                    "name": "Quality Test Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://example.com/thumbnail_64x64.jpg",  # Low quality thumbnail
                    "image_url": "https://example.com/full_image.jpg",  # Medium quality
                    "image_urls_for_viewing": [
                        "https://example.com/high_quality_image.jpg",  # Highest quality
                        "https://example.com/alt_high_quality.jpg"
                    ],
                    "object_story_spec": {
                        "link_data": {
                            "picture": "https://example.com/object_story_picture.jpg"
                        }
                    }
                }
            ]
        })
        
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
            
            mock_api.side_effect = [mock_ad_data, mock_creative_details]
            mock_get_creatives.return_value = mock_get_ad_creatives_response
            mock_download.return_value = b"fake_image_bytes"
            mock_pil_open.return_value = mock_pil_image
            mock_bytesio.return_value = mock_byte_stream
            
            # This should prioritize image_urls_for_viewing[0] over thumbnail_url
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify it used the highest quality URL, not the thumbnail
            assert result is not None
            mock_download.assert_called_once_with("https://example.com/high_quality_image.jpg")
            
            # Verify it did NOT use the thumbnail URL
            # Check that the call was made with the high-quality URL, not the thumbnail
            mock_download.assert_called_once_with("https://example.com/high_quality_image.jpg") 