"""Tests for instagram_insights module."""

import pytest
import json
from unittest.mock import AsyncMock, patch, call

from meta_ads_mcp.core.instagram_insights import (
    list_media,
    get_media_insights,
    get_ig_account_insights,
    get_story_insights,
    publish_media,
)


class TestListMedia:
    EXPECTED_FIELDS = "id,media_type,media_product_type,timestamp,permalink,caption,like_count,comments_count,thumbnail_url"

    @pytest.mark.asyncio
    async def test_success(self):
        mock_response = {"data": [{"id": "123", "media_type": "REELS", "like_count": 50}]}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await list_media(ig_user_id="17841400000", access_token="test_token")
            mock_api.assert_called_once_with(
                "17841400000/media",
                "test_token",
                {
                    "fields": self.EXPECTED_FIELDS,
                    "limit": 20,
                },
            )
            result_data = json.loads(result)
            assert result_data["data"][0]["id"] == "123"

    @pytest.mark.asyncio
    async def test_since_until_params(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await list_media(
                ig_user_id="17841400000",
                access_token="test_token",
                since="2025-11-15",
                until="2026-03-14",
            )
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["since"] == "2025-11-15"
            assert params["until"] == "2026-03-14"

    @pytest.mark.asyncio
    async def test_since_without_until(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await list_media(
                ig_user_id="17841400000",
                access_token="test_token",
                since="2025-11-15",
            )
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["since"] == "2025-11-15"
            assert "until" not in params

    @pytest.mark.asyncio
    async def test_fields_include_media_product_type(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await list_media(ig_user_id="17841400000", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert "media_product_type" in params["fields"]

    @pytest.mark.asyncio
    async def test_fields_do_not_include_video_views(self):
        """video_views was removed — Graph API v25.0 never returns it for Reels."""
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await list_media(ig_user_id="17841400000", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert "video_views" not in params["fields"]

    @pytest.mark.asyncio
    async def test_no_ig_user_id(self):
        result = await list_media(ig_user_id="", access_token="test_token")
        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested


class TestGetMediaInsights:
    @pytest.mark.asyncio
    async def test_success_with_defaults(self):
        mock_response = {"data": [{"name": "reach", "values": [{"value": 500}]}]}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await get_media_insights(media_id="123", access_token="test_token")
            # Confirm metric param is the default comma-joined string
            call_args = mock_api.call_args
            params = call_args[0][2]
            default_metrics = ["reach", "impressions", "saved", "shares", "views", "total_interactions"]
            assert params["metric"] == ",".join(default_metrics)
            result_data = json.loads(result)
            assert result_data["data"][0]["name"] == "reach"

    @pytest.mark.asyncio
    async def test_default_metrics_do_not_include_plays(self):
        """plays was removed in v22.0 — passing it causes a hard 400 on v25.0."""
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_media_insights(media_id="123", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert "plays" not in params["metric"].split(",")

    @pytest.mark.asyncio
    async def test_custom_metrics(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_media_insights(
                media_id="123",
                access_token="test_token",
                metrics=["reach", "impressions"],
            )
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["metric"] == "reach,impressions"

    @pytest.mark.asyncio
    async def test_no_media_id(self):
        result = await get_media_insights(media_id="", access_token="test_token")
        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested


class TestGetIgAccountInsights:
    @pytest.mark.asyncio
    async def test_success_with_since_until(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await get_ig_account_insights(
                ig_user_id="17841400000",
                metrics=["follower_count"],
                period="day",
                since="2026-03-01",
                until="2026-03-11",
                access_token="test_token",
            )
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["since"] == "2026-03-01"
            assert params["until"] == "2026-03-11"
            result_data = json.loads(result)
            assert "data" in result_data

    @pytest.mark.asyncio
    async def test_invalid_period(self):
        result = await get_ig_account_insights(
            ig_user_id="17841400000",
            metrics=["follower_count"],
            period="quarterly",
            access_token="test_token",
        )
        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_no_metrics(self):
        result = await get_ig_account_insights(
            ig_user_id="17841400000",
            metrics=[],
            period="day",
            access_token="test_token",
        )
        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_metric_type_param_passed(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_ig_account_insights(
                ig_user_id="17841400000",
                metrics=["impressions"],
                period="day",
                metric_type="total_value",
                access_token="test_token",
            )
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["metric_type"] == "total_value"

    @pytest.mark.asyncio
    async def test_metric_type_not_set_by_default(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_ig_account_insights(
                ig_user_id="17841400000",
                metrics=["reach"],
                period="day",
                access_token="test_token",
            )
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert "metric_type" not in params

    @pytest.mark.asyncio
    async def test_follower_count_rejects_non_day_period(self):
        result = await get_ig_account_insights(
            ig_user_id="17841400000",
            metrics=["follower_count"],
            period="week",
            access_token="test_token",
        )
        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested
        assert "follower_count" in nested["error"]

    @pytest.mark.asyncio
    async def test_follower_count_with_day_period_succeeds(self):
        mock_response = {"data": [{"name": "follower_count", "values": [{"value": 4800}]}]}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await get_ig_account_insights(
                ig_user_id="17841400000",
                metrics=["follower_count"],
                period="day",
                access_token="test_token",
            )
            result_data = json.loads(result)
            assert "data" in result_data


class TestGetStoryInsights:
    @pytest.mark.asyncio
    async def test_success_with_defaults(self):
        mock_response = {"data": [{"name": "impressions", "values": [{"value": 200}]}]}
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await get_story_insights(story_id="story_123", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            default_metrics = ["impressions", "reach", "replies", "taps_forward", "taps_back", "exits"]
            assert params["metric"] == ",".join(default_metrics)
            result_data = json.loads(result)
            assert result_data["data"][0]["name"] == "impressions"
            assert result_data["data"][0]["values"][0]["value"] == 200


class TestPublishMedia:
    @pytest.mark.asyncio
    async def test_two_step_success(self):
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.side_effect = [{"id": "container_123"}, {"id": "published_456"}]
            result = await publish_media(
                ig_user_id="17841400000",
                media_url="https://example.com/video.mp4",
                media_type="REELS",
                access_token="test_token",
            )
            assert mock_api.call_count == 2
            result_data = json.loads(result)
            assert result_data["id"] == "published_456"

    @pytest.mark.asyncio
    async def test_invalid_media_url(self):
        result = await publish_media(
            ig_user_id="17841400000",
            media_url="ftp://not-valid",
            media_type="REELS",
            access_token="test_token",
        )
        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_invalid_media_type(self):
        result = await publish_media(
            ig_user_id="17841400000",
            media_url="https://example.com/image.jpg",
            media_type="CAROUSEL",
            access_token="test_token",
        )
        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_step1_failure(self):
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
            return_value={"error": {"message": "Upload failed"}},
        ) as mock_api:
            result = await publish_media(
                ig_user_id="17841400000",
                media_url="https://example.com/video.mp4",
                media_type="REELS",
                access_token="test_token",
            )
            # Only one call should be made — step 2 must not run
            assert mock_api.call_count == 1
            result_data = json.loads(result)
            assert "data" in result_data
            nested = json.loads(result_data["data"])
            assert "error" in nested
            # creation_id must NOT be in the response (step 1 failed cleanly)
            assert "creation_id" not in nested

    @pytest.mark.asyncio
    async def test_step2_failure(self):
        with patch(
            "meta_ads_mcp.core.instagram_insights.make_api_request",
            new_callable=AsyncMock,
        ) as mock_api:
            mock_api.side_effect = [
                {"id": "container_123"},
                {"error": {"message": "Publish failed"}},
            ]
            result = await publish_media(
                ig_user_id="17841400000",
                media_url="https://example.com/video.mp4",
                media_type="REELS",
                access_token="test_token",
            )
            result_data = json.loads(result)
            assert "error" in result_data
            # creation_id must be present so the caller can debug
            assert "creation_id" in result_data
            assert result_data["creation_id"] == "container_123"
