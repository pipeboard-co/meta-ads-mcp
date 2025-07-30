"""Tests for get_ad_image quality improvements.

These tests verify that the get_ad_image function now correctly prioritizes
high-quality ad creative images over profile thumbnails.

Key improvements tested:
1. Prioritizes image_urls_for_viewing over thumbnail_url
2. Uses image_url as second priority
3. Uses object_story_spec.link_data.picture as third priority
4. Only uses thumbnail_url as last resort
5. Better logging to show which image source is being used
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from meta_ads_mcp.core.ads import get_ad_image
from meta_ads_mcp.core.utils import extract_creative_image_urls


class TestGetAdImageQualityImprovements:
    """Test cases for image quality improvements in get_ad_image function."""
    
    @pytest.mark.asyncio
    async def test_prioritizes_image_urls_for_viewing_over_thumbnail(self):
        """Test that image_urls_for_viewing is prioritized over thumbnail_url."""
        
        # Mock responses for creative with both high-quality and thumbnail URLs
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Test Creative"
            # No image_hash - triggers fallback
        }
        
        # Mock get_ad_creatives response with both URLs
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789",
                    "name": "Test Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://example.com/thumbnail_64x64.jpg",  # Low quality
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
            
            # This should prioritize image_urls_for_viewing[0]
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify it used the highest quality URL
            assert result is not None
            mock_download.assert_called_once_with("https://example.com/high_quality_image.jpg")
    
    @pytest.mark.asyncio
    async def test_falls_back_to_image_url_when_image_urls_for_viewing_unavailable(self):
        """Test fallback to image_url when image_urls_for_viewing is not available."""
        
        # Mock responses for creative without image_urls_for_viewing
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Test Creative"
        }
        
        # Mock get_ad_creatives response without image_urls_for_viewing
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789",
                    "name": "Test Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://example.com/thumbnail.jpg",
                    "image_url": "https://example.com/full_image.jpg",  # Should be used
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
            
            # This should fall back to image_url
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify it used image_url
            assert result is not None
            mock_download.assert_called_once_with("https://example.com/full_image.jpg")
    
    @pytest.mark.asyncio
    async def test_falls_back_to_object_story_spec_picture_when_image_url_unavailable(self):
        """Test fallback to object_story_spec.link_data.picture when image_url is not available."""
        
        # Mock responses for creative without image_url
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Test Creative"
        }
        
        # Mock get_ad_creatives response without image_url
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789",
                    "name": "Test Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://example.com/thumbnail.jpg",
                    "object_story_spec": {
                        "link_data": {
                            "picture": "https://example.com/object_story_picture.jpg"  # Should be used
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
            
            # This should fall back to object_story_spec.link_data.picture
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify it used object_story_spec.link_data.picture
            assert result is not None
            mock_download.assert_called_once_with("https://example.com/object_story_picture.jpg")
    
    @pytest.mark.asyncio
    async def test_uses_thumbnail_url_only_as_last_resort(self):
        """Test that thumbnail_url is only used when no other options are available."""
        
        # Mock responses for creative with only thumbnail_url
        mock_ad_data = {
            "account_id": "act_123456789",
            "creative": {"id": "creative_123456789"}
        }
        
        mock_creative_details = {
            "id": "creative_123456789",
            "name": "Test Creative"
        }
        
        # Mock get_ad_creatives response with only thumbnail_url
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "creative_123456789",
                    "name": "Test Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://example.com/thumbnail_only.jpg"  # Only option
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
            
            # This should use thumbnail_url as last resort
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify it used thumbnail_url
            assert result is not None
            mock_download.assert_called_once_with("https://example.com/thumbnail_only.jpg")
    
    def test_extract_creative_image_urls_prioritizes_quality(self):
        """Test that extract_creative_image_urls correctly prioritizes image quality."""
        
        # Test creative with multiple image URLs
        test_creative = {
            "id": "creative_123456789",
            "name": "Test Creative",
            "thumbnail_url": "https://example.com/thumbnail.jpg",  # Lowest priority
            "image_url": "https://example.com/image.jpg",  # Medium priority
            "image_urls_for_viewing": [
                "https://example.com/high_quality_1.jpg",  # Highest priority
                "https://example.com/high_quality_2.jpg"
            ],
            "object_story_spec": {
                "link_data": {
                    "picture": "https://example.com/object_story_picture.jpg"  # High priority
                }
            }
        }
        
        # Extract URLs
        urls = extract_creative_image_urls(test_creative)
        
        # Verify correct priority order
        assert len(urls) >= 4
        assert urls[0] == "https://example.com/high_quality_1.jpg"  # First priority
        assert urls[1] == "https://example.com/high_quality_2.jpg"  # Second priority
        assert "https://example.com/image.jpg" in urls  # Medium priority
        assert "https://example.com/object_story_picture.jpg" in urls  # High priority
        assert urls[-1] == "https://example.com/thumbnail.jpg"  # Last priority
    
    def test_extract_creative_image_urls_handles_missing_fields(self):
        """Test that extract_creative_image_urls handles missing fields gracefully."""
        
        # Test creative with minimal fields
        test_creative = {
            "id": "creative_123456789",
            "name": "Minimal Creative",
            "thumbnail_url": "https://example.com/thumbnail.jpg"
        }
        
        # Extract URLs
        urls = extract_creative_image_urls(test_creative)
        
        # Should still work with only thumbnail_url
        assert len(urls) == 1
        assert urls[0] == "https://example.com/thumbnail.jpg"
    
    def test_extract_creative_image_urls_removes_duplicates(self):
        """Test that extract_creative_image_urls removes duplicate URLs."""
        
        # Test creative with duplicate URLs
        test_creative = {
            "id": "creative_123456789",
            "name": "Duplicate URLs Creative",
            "thumbnail_url": "https://example.com/same_url.jpg",
            "image_url": "https://example.com/same_url.jpg",  # Duplicate
            "image_urls_for_viewing": [
                "https://example.com/same_url.jpg",  # Duplicate
                "https://example.com/unique_url.jpg"
            ]
        }
        
        # Extract URLs
        urls = extract_creative_image_urls(test_creative)
        
        # Should remove duplicates while preserving order
        assert len(urls) == 2
        assert urls[0] == "https://example.com/same_url.jpg"  # First occurrence
        assert urls[1] == "https://example.com/unique_url.jpg"
    
    @pytest.mark.asyncio
    async def test_get_ad_image_with_real_world_example(self):
        """Test with a real-world example that mimics the actual API response structure."""
        
        # Mock responses based on real API data
        mock_ad_data = {
            "account_id": "act_15975950",
            "creative": {"id": "606995022142818"}
        }
        
        mock_creative_details = {
            "id": "606995022142818",
            "name": "Test Creative"
        }
        
        # Mock get_ad_creatives response based on real data
        mock_get_ad_creatives_response = json.dumps({
            "data": [
                {
                    "id": "606995022142818",
                    "name": "Test Creative",
                    "status": "ACTIVE",
                    "thumbnail_url": "https://external.fbsb6-1.fna.fbcdn.net/emg1/v/t13/13476424677788553381?url=https%3A%2F%2Fwww.facebook.com%2Fads%2Fimage%2F%3Fd%3DAQLuJ5l4AROBvIUchp4g4JXxIT5uAZiAsgHQkD8Iw7BeVtkXNUUfs3leWpqQplJCJdixVIg3mq9KichJ64eRfM-r8aY4GtVQp8TvS_HBByJ8fGg_Cs7Kb8YkN4IDwJ4iQIIkMx30LycCKzuYtp9M-vOk&fb_obo=1&utld=facebook.com&stp=c0.5000x0.5000f_dst-emg0_p64x64_q75_tt6&edm=AEuWsiQEAAAA&_nc_gid=_QBCRbZxDq-i1ZiGEXxW2w&_nc_eui2=AeEbQXzmAdoqWLIXjuTDJ0xAoThZu47BlQqhOFm7jsGVCloP48Ep6Y_qIA5tcqrcSDff5f_k8xGzFIpD7PnUws8c&_nc_oc=Adn3GeYlXxbfEeY0wCBSgNdlwO80wXt5R5bgY2NozdroZ6CRSaXIaOSjVSK9S1LsqsY4GL_0dVzU80RY8QMucEkZ&ccb=13-1&oh=06_Q3-1AcBKUD0rfLGATAveIM5hMSWG9c7DsJzq2arvOl8W4Bpn&oe=688C87B2&_nc_sid=58080a",
                    "image_url": "https://scontent.fbsb6-1.fna.fbcdn.net/v/t45.1600-4/518574136_1116014047008737_2492837958169838537_n.png?stp=dst-jpg_tt6&_nc_cat=109&ccb=1-7&_nc_sid=890911&_nc_eui2=AeHbHqoiAUgF0QeX-tvUoDjYeTyJad_QEPF5PIlp39AQ8dP8cvOlHwiJjny8AUv7xxAlYyy5BGCqFU_oVM9CI7ln&_nc_ohc=VTTYlMOAWZoQ7kNvwGjLMW5&_nc_oc=AdnYDrpNrLovWZC_RG4tvoICGPjBNfzNJimhx-4SKW4BU2i_yzL00dX0-OiYEYokq394g8xR-1a-OuVDAm4HsSJy&_nc_zt=1&_nc_ht=scontent.fbsb6-1.fna&edm=AEuWsiQEAAAA&_nc_gid=_QBCRbZxDq-i1ZiGEXxW2w&oh=00_AfTujKmF365FnGgcokkkdWnK-vmnzQK8Icvlk0kB8SKM3g&oe=68906FC4",
                    "image_urls_for_viewing": [
                        "https://scontent.fbsb6-1.fna.fbcdn.net/v/t45.1600-4/518574136_1116014047008737_2492837958169838537_n.png?stp=dst-jpg_tt6&_nc_cat=109&ccb=1-7&_nc_sid=890911&_nc_eui2=AeHbHqoiAUgF0QeX-tvUoDjYeTyJad_QEPF5PIlp39AQ8dP8cvOlHwiJjny8AUv7xxAlYyy5BGCqFU_oVM9CI7ln&_nc_ohc=VTTYlMOAWZoQ7kNvwGjLMW5&_nc_oc=AdnYDrpNrLovWZC_RG4tvoICGPjBNfzNJimhx-4SKW4BU2i_yzL00dX0-OiYEYokq394g8xR-1a-OuVDAm4HsSJy&_nc_zt=1&_nc_ht=scontent.fbsb6-1.fna&edm=AEuWsiQEAAAA&_nc_gid=_QBCRbZxDq-i1ZiGEXxW2w&oh=00_AfTujKmF365FnGgcokkkdWnK-vmnzQK8Icvlk0kB8SKM3g&oe=68906FC4",
                        "https://external.fbsb6-1.fna.fbcdn.net/emg1/v/t13/13476424677788553381?url=https%3A%2F%2Fwww.facebook.com%2Fads%2Fimage%2F%3Fd%3DAQLuJ5l4AROBvIUchp4g4JXxIT5uAZiAsgHQkD8Iw7BeVtkXNUUfs3leWpqQplJCJdixVIg3mq9KichJ64eRfM-r8aY4GtVQp8TvS_HBByJ8fGg_Cs7Kb8YkN4IDwJ4iQIIkMx30LycCKzuYtp9M-vOk&fb_obo=1&utld=facebook.com&stp=c0.5000x0.5000f_dst-emg0_p64x64_q75_tt6&edm=AEuWsiQEAAAA&_nc_gid=_QBCRbZxDq-i1ZiGEXxW2w&_nc_eui2=AeEbQXzmAdoqWLIXjuTDJ0xAoThZu47BlQqhOFm7jsGVCloP48Ep6Y_qIA5tcqrcSDff5f_k8xGzFIpD7PnUws8c&_nc_oc=Adn3GeYlXxbfEeY0wCBSgNdlwO80wXt5R5bgY2NozdroZ6CRSaXIaOSjVSK9S1LsqsY4GL_0dVzU80RY8QMucEkZ&ccb=13-1&oh=06_Q3-1AcBKUD0rfLGATAveIM5hMSWG9c7DsJzq2arvOl8W4Bpn&oe=688C87B2&_nc_sid=58080a"
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
            
            # This should use the first image_urls_for_viewing URL (high quality)
            result = await get_ad_image(access_token="test_token", ad_id="test_ad_id")
            
            # Verify it used the high-quality URL (not the thumbnail)
            assert result is not None
            expected_url = "https://scontent.fbsb6-1.fna.fbcdn.net/v/t45.1600-4/518574136_1116014047008737_2492837958169838537_n.png?stp=dst-jpg_tt6&_nc_cat=109&ccb=1-7&_nc_sid=890911&_nc_eui2=AeHbHqoiAUgF0QeX-tvUoDjYeTyJad_QEPF5PIlp39AQ8dP8cvOlHwiJjny8AUv7xxAlYyy5BGCqFU_oVM9CI7ln&_nc_ohc=VTTYlMOAWZoQ7kNvwGjLMW5&_nc_oc=AdnYDrpNrLovWZC_RG4tvoICGPjBNfzNJimhx-4SKW4BU2i_yzL00dX0-OiYEYokq394g8xR-1a-OuVDAm4HsSJy&_nc_zt=1&_nc_ht=scontent.fbsb6-1.fna&edm=AEuWsiQEAAAA&_nc_gid=_QBCRbZxDq-i1ZiGEXxW2w&oh=00_AfTujKmF365FnGgcokkkdWnK-vmnzQK8Icvlk0kB8SKM3g&oe=68906FC4"
            mock_download.assert_called_once_with(expected_url) 