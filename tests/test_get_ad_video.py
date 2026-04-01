"""Tests for get_ad_video function.

Tests video ID extraction from ad creatives (object_story_spec and asset_feed_spec)
and Meta Graph API source URL retrieval, including the advideos edge fallback.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, call
from meta_ads_mcp.core.ads import get_ad_video


@pytest.mark.asyncio
class TestGetAdVideo:

    async def test_get_ad_video_with_ad_id_object_story_spec(self):
        """Extract video_id from object_story_spec.video_data and return source URL via advideos edge."""
        mock_creatives = {
            "data": [{
                "id": "creative_123",
                "object_story_spec": {
                    "video_data": {
                        "video_id": "9999",
                        "image_url": "https://example.com/thumb.jpg"
                    }
                }
            }]
        }

        mock_ad_data = {"account_id": "111222333"}

        mock_advideos_response = {
            "data": [{
                "id": "9999",
                "source": "https://video-xx.fbcdn.net/v/example.mp4",
                "picture": "https://example.com/thumb.jpg",
                "title": "My Ad Video",
                "description": "Test description",
                "length": 30.5,
                "created_time": "2026-03-01T12:00:00+0000",
            }]
        }

        with patch('meta_ads_mcp.core.ads.get_ad_creatives', new_callable=AsyncMock) as mock_get_creatives, \
             patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:

            mock_get_creatives.return_value = json.dumps(mock_creatives)
            mock_api.side_effect = [mock_ad_data, mock_advideos_response]

            result = await get_ad_video(access_token="test_token", ad_id="ad_123")
            data = json.loads(result)

            assert data["video_id"] == "9999"
            assert data["source_url"] == "https://video-xx.fbcdn.net/v/example.mp4"
            assert data["thumbnail_url"] == "https://example.com/thumb.jpg"
            assert data["duration_seconds"] == 30.5
            assert data["ad_id"] == "ad_123"

            # Should call: 1) get account_id from ad, 2) advideos edge
            assert mock_api.call_count == 2
            mock_api.assert_any_call("ad_123", "test_token", {"fields": "account_id"})

    async def test_get_ad_video_advideos_edge_empty_falls_back(self):
        """When advideos edge returns empty (page-owned video), fall back to direct node."""
        mock_creatives = {
            "data": [{
                "id": "creative_456",
                "object_story_spec": {"link_data": {"link": "https://example.com"}},
                "asset_feed_spec": {
                    "videos": [
                        {"video_id": "7777", "thumbnail_url": "https://example.com/thumb2.jpg"},
                    ]
                }
            }]
        }

        mock_ad_data = {"account_id": "111222333"}
        mock_advideos_empty = {"data": []}
        mock_direct_video = {
            "source": "https://video-xx.fbcdn.net/v/page-video.mp4",
            "picture": "https://example.com/thumb2.jpg",
            "length": 15.0,
        }

        with patch('meta_ads_mcp.core.ads.get_ad_creatives', new_callable=AsyncMock) as mock_get_creatives, \
             patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:

            mock_get_creatives.return_value = json.dumps(mock_creatives)
            # 1) account_id lookup, 2) advideos edge (empty), 3) direct node fallback
            mock_api.side_effect = [mock_ad_data, mock_advideos_empty, mock_direct_video]

            result = await get_ad_video(access_token="test_token", ad_id="ad_456")
            data = json.loads(result)

            assert data["video_id"] == "7777"
            assert data["source_url"] == "https://video-xx.fbcdn.net/v/page-video.mp4"
            assert mock_api.call_count == 3

    async def test_get_ad_video_with_direct_video_id(self):
        """Bypass creative lookup when video_id is provided directly (no ad_id = no advideos edge)."""
        mock_video_details = {
            "source": "https://video-xx.fbcdn.net/v/direct.mp4",
            "picture": "https://example.com/thumb.jpg",
            "title": "Direct Video",
            "length": 60.0,
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_video_details

            result = await get_ad_video(access_token="test_token", video_id="5555")
            data = json.loads(result)

            assert data["video_id"] == "5555"
            assert data["source_url"] == "https://video-xx.fbcdn.net/v/direct.mp4"
            assert "ad_id" not in data

            # Without ad_id, only the direct node call is made
            mock_api.assert_called_once_with(
                "5555", "test_token",
                {"fields": "source,title,description,length,picture,thumbnails,created_time"}
            )

    async def test_get_ad_video_no_video_in_creative(self):
        """Return helpful error when the ad is an image ad, not a video ad."""
        mock_creatives = {
            "data": [{
                "id": "creative_789",
                "image_hash": "abc123",
                "object_story_spec": {
                    "link_data": {"image_hash": "abc123", "link": "https://example.com"}
                }
            }]
        }

        with patch('meta_ads_mcp.core.ads.get_ad_creatives', new_callable=AsyncMock) as mock_get_creatives:
            mock_get_creatives.return_value = json.dumps(mock_creatives)

            result = await get_ad_video(access_token="test_token", ad_id="ad_789")
            result_str = result if isinstance(result, str) else json.dumps(result)
            assert "No video found" in result_str
            assert "get_ad_image" in result_str

    async def test_get_ad_video_no_ids_provided(self):
        """Return error when neither ad_id nor video_id is provided."""
        result = await get_ad_video(access_token="test_token")
        result_str = result if isinstance(result, str) else json.dumps(result)
        assert "error" in result_str
        assert "ad_id" in result_str or "video_id" in result_str

    async def test_get_ad_video_api_error(self):
        """Handle Meta API errors gracefully."""
        mock_video_error = {
            "error": {
                "message": "Unsupported get request.",
                "type": "GraphMethodException",
                "code": 100
            }
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_video_error

            result = await get_ad_video(access_token="test_token", video_id="invalid_id")
            data = json.loads(result)

            assert "error" in data
            assert "Could not get video" in data["error"]

    async def test_get_ad_video_account_id_lookup_fails(self):
        """When account_id lookup fails, skip advideos edge and go direct."""
        mock_creatives = {
            "data": [{
                "id": "creative_999",
                "object_story_spec": {
                    "video_data": {"video_id": "4444"}
                }
            }]
        }

        mock_ad_data_error = {"error": {"message": "Not found"}}
        mock_direct_video = {
            "source": "https://video-xx.fbcdn.net/v/fallback.mp4",
            "picture": "https://example.com/thumb.jpg",
            "length": 20.0,
        }

        with patch('meta_ads_mcp.core.ads.get_ad_creatives', new_callable=AsyncMock) as mock_get_creatives, \
             patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:

            mock_get_creatives.return_value = json.dumps(mock_creatives)
            # 1) account_id lookup fails (no account_id key), 2) direct fallback
            mock_api.side_effect = [mock_ad_data_error, mock_direct_video]

            result = await get_ad_video(access_token="test_token", ad_id="ad_999")
            data = json.loads(result)

            assert data["video_id"] == "4444"
            assert data["source_url"] == "https://video-xx.fbcdn.net/v/fallback.mp4"
            assert mock_api.call_count == 2
