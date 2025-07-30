"""Regression tests for get_ad_creatives function bug fix.

Tests for issue where get_ad_creatives would throw:
'TypeError: 'dict' object is not callable'

This was caused by trying to call ad_creative_images(creative) where 
ad_creative_images is a dictionary, not a function.

The fix was to create extract_creative_image_urls() function and use that instead.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import get_ad_creatives
from meta_ads_mcp.core.utils import ad_creative_images


@pytest.mark.asyncio
class TestGetAdCreativesBugFix:
    """Regression test cases for the get_ad_creatives function bug fix."""
    
    async def test_get_ad_creatives_regression_fix(self):
        """Regression test: ensure get_ad_creatives works correctly and doesn't throw 'dict' object is not callable."""
        
        # Mock the make_api_request to return sample creative data
        sample_creative_data = {
            "data": [
                {
                    "id": "123456789",
                    "name": "Test Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://example.com/thumb.jpg",
                    "image_url": "https://example.com/image.jpg",
                    "image_hash": "abc123",
                    "object_story_spec": {
                        "page_id": "987654321",
                        "link_data": {
                            "image_hash": "abc123",
                            "link": "https://example.com",
                            "name": "Test Ad"
                        }
                    }
                }
            ]
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            # This should NOT raise a TypeError anymore
            # Previously this would fail with: TypeError: 'dict' object is not callable
            result = await get_ad_creatives(access_token="test_token", ad_id="120228922933270272")
            
            # Parse the result
            result_data = json.loads(result)
            
            # Verify the structure is correct
            assert "data" in result_data
            assert len(result_data["data"]) == 1
            
            creative = result_data["data"][0]
            assert creative["id"] == "123456789"
            assert creative["name"] == "Test Creative"
            assert "image_urls_for_viewing" in creative
            assert isinstance(creative["image_urls_for_viewing"], list)
    
    async def test_extract_creative_image_urls_function(self):
        """Test the extract_creative_image_urls function works correctly."""
        from meta_ads_mcp.core.utils import extract_creative_image_urls
        
        # Test creative with various image URL fields
        test_creative = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "image_url": "https://example.com/image.jpg",
            "image_hash": "abc123",
            "object_story_spec": {
                "page_id": "987654321",
                "link_data": {
                    "image_hash": "abc123",
                    "link": "https://example.com",
                    "name": "Test Ad",
                    "picture": "https://example.com/picture.jpg"
                }
            }
        }
        
        urls = extract_creative_image_urls(test_creative)
        
        # Should extract URLs in order: image_url, picture, thumbnail_url (new priority order)
        expected_urls = [
            "https://example.com/image.jpg",
            "https://example.com/picture.jpg",
            "https://example.com/thumb.jpg"
        ]
        
        assert urls == expected_urls
        
        # Test with empty creative
        empty_urls = extract_creative_image_urls({})
        assert empty_urls == []
        
        # Test with duplicates (should remove them)
        duplicate_creative = {
            "image_url": "https://example.com/same.jpg",
            "thumbnail_url": "https://example.com/same.jpg",  # Same URL
        }
        unique_urls = extract_creative_image_urls(duplicate_creative)
        assert unique_urls == ["https://example.com/same.jpg"]
    
    async def test_get_ad_creatives_no_ad_id(self):
        """Test get_ad_creatives with no ad_id provided."""
        
        result = await get_ad_creatives(access_token="test_token", ad_id=None)
        result_data = json.loads(result)
        
        # The @meta_api_tool decorator wraps the result in a data field
        assert "data" in result_data
        error_data = json.loads(result_data["data"])
        assert "error" in error_data
        assert error_data["error"] == "No ad ID provided"

    async def test_get_ad_creatives_empty_data(self):
        """Test get_ad_creatives when API returns empty data."""
        
        empty_data = {"data": []}
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = empty_data
            
            result = await get_ad_creatives(access_token="test_token", ad_id="120228922933270272")
            result_data = json.loads(result)
            
            assert "data" in result_data
            assert len(result_data["data"]) == 0


def test_ad_creative_images_is_dict():
    """Test that ad_creative_images is a dictionary, not a function.
    
    This confirms the original issue: ad_creative_images is a dict for storing image data,
    but was being called as a function ad_creative_images(creative), which would fail.
    This test ensures we don't accidentally change ad_creative_images to a function
    and break its intended purpose as a storage dictionary.
    """
    assert isinstance(ad_creative_images, dict)
    
    # This would raise TypeError: 'dict' object is not callable
    # This is the original bug - trying to call a dict as a function
    with pytest.raises(TypeError, match="'dict' object is not callable"):
        ad_creative_images({"test": "data"}) 