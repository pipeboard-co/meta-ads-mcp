"""Tests for the `fields` passthrough behavior in get_insights.

Verifies that:
- Without a `fields` argument, the legacy default set is requested.
- With a `fields` argument, the listed fields are merged with required
  dimension identifiers and sent through to Meta verbatim.
- Video milestone fields and ranking diagnostics survive the merge so the
  Meta API will return them.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.insights import get_insights


class TestInsightsFieldsPassthrough:
    @pytest.fixture
    def mock_auth_manager(self):
        with patch('meta_ads_mcp.core.api.auth_manager') as mock, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
            mock.get_current_access_token.return_value = "test_access_token"
            mock.is_token_valid.return_value = True
            mock.app_id = "test_app_id"
            mock_get_token.return_value = "test_access_token"
            yield mock

    @pytest.fixture
    def valid_account_id(self):
        return "act_701351919139047"

    @pytest.fixture
    def mock_empty_response(self):
        return {"data": []}

    @pytest.mark.asyncio
    async def test_default_fields_are_legacy_list(self, mock_auth_manager, valid_account_id, mock_empty_response):
        """When `fields` is omitted, the call sends the legacy default field list."""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_empty_response

            await get_insights(object_id=valid_account_id, level="ad", time_range="last_7d")

            call_args = mock_api_request.call_args
            params = call_args[0][2]
            fields_csv = params["fields"]
            fields = fields_csv.split(",")

            # Sanity: identifier fields are present
            assert "account_id" in fields
            assert "campaign_id" in fields
            assert "adset_id" in fields
            assert "ad_id" in fields
            # Sanity: legacy metric fields are present
            assert "impressions" in fields
            assert "spend" in fields
            assert "actions" in fields

            # Video milestone fields should NOT be in the default set
            assert "video_p25_watched_actions" not in fields
            assert "quality_ranking" not in fields

    @pytest.mark.asyncio
    async def test_video_milestone_fields_passthrough(self, mock_auth_manager, valid_account_id, mock_empty_response):
        """Caller-supplied video milestone fields are forwarded to Meta verbatim."""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_empty_response

            await get_insights(
                object_id=valid_account_id,
                level="ad",
                time_range="last_7d",
                fields=[
                    "video_p25_watched_actions",
                    "video_p50_watched_actions",
                    "video_p75_watched_actions",
                    "video_p95_watched_actions",
                    "video_p100_watched_actions",
                    "video_thruplay_watched_actions",
                    "video_avg_time_watched_actions",
                    "video_play_actions",
                    "video_30_sec_watched_actions",
                ],
            )

            call_args = mock_api_request.call_args
            params = call_args[0][2]
            fields = params["fields"].split(",")

            for expected in [
                "video_p25_watched_actions",
                "video_p50_watched_actions",
                "video_p75_watched_actions",
                "video_p95_watched_actions",
                "video_p100_watched_actions",
                "video_thruplay_watched_actions",
                "video_avg_time_watched_actions",
                "video_play_actions",
                "video_30_sec_watched_actions",
            ]:
                assert expected in fields, f"Expected {expected} in passthrough fields"

            # Required identifier fields are still present
            assert "ad_id" in fields
            assert "campaign_id" in fields
            assert "account_id" in fields

    @pytest.mark.asyncio
    async def test_ranking_fields_passthrough(self, mock_auth_manager, valid_account_id, mock_empty_response):
        """Caller-supplied ranking diagnostic fields are forwarded to Meta verbatim."""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_empty_response

            await get_insights(
                object_id=valid_account_id,
                level="ad",
                time_range="last_7d",
                fields=[
                    "quality_ranking",
                    "engagement_rate_ranking",
                    "conversion_rate_ranking",
                ],
            )

            call_args = mock_api_request.call_args
            params = call_args[0][2]
            fields = params["fields"].split(",")

            assert "quality_ranking" in fields
            assert "engagement_rate_ranking" in fields
            assert "conversion_rate_ranking" in fields
            # Required dimension fields still merged in
            assert "ad_id" in fields
            assert "date_start" in fields
            assert "date_stop" in fields

    @pytest.mark.asyncio
    async def test_custom_fields_dedupe_with_dimensions(self, mock_auth_manager, valid_account_id, mock_empty_response):
        """Overlapping fields (e.g. ad_id) appear once, not twice."""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_empty_response

            await get_insights(
                object_id=valid_account_id,
                level="ad",
                time_range="last_7d",
                fields=["ad_id", "video_p25_watched_actions", "ad_name"],
            )

            call_args = mock_api_request.call_args
            params = call_args[0][2]
            fields = params["fields"].split(",")

            # Identifier fields appear exactly once
            assert fields.count("ad_id") == 1
            assert fields.count("ad_name") == 1
            assert "video_p25_watched_actions" in fields

    @pytest.mark.asyncio
    async def test_platform_position_drops_action_typed_fields_with_passthrough(
        self, mock_auth_manager, valid_account_id, mock_empty_response
    ):
        """Existing platform_position guard still drops action-typed fields when custom fields supplied."""
        with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api_request:
            mock_api_request.return_value = mock_empty_response

            await get_insights(
                object_id=valid_account_id,
                level="ad",
                time_range="last_7d",
                breakdown="platform_position",
                fields=["video_p25_watched_actions"],
            )

            call_args = mock_api_request.call_args
            params = call_args[0][2]
            fields = params["fields"].split(",")

            # video field still passes through
            assert "video_p25_watched_actions" in fields
            # action-typed fields are dropped because platform_position conflicts with them
            assert "actions" not in fields
            assert "action_values" not in fields
            assert "conversions" not in fields
            assert "cost_per_action_type" not in fields
