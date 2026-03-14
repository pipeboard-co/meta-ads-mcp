"""Tests for ad set field completeness (v25.0)."""

import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.adsets import get_adsets, get_adset_details


class TestGetAdsetsFields:
    @pytest.mark.asyncio
    async def test_fields_include_effective_status_account_endpoint(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_adsets(account_id="act_123", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert "effective_status" in params["fields"]

    @pytest.mark.asyncio
    async def test_fields_include_effective_status_campaign_endpoint(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_adsets(
                account_id="act_123",
                campaign_id="camp_456",
                access_token="test_token",
            )
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert "effective_status" in params["fields"]


class TestGetAdsetDetailsFields:
    @pytest.mark.asyncio
    async def test_fields_include_effective_status(self):
        mock_response = {"id": "123", "effective_status": "ACTIVE"}
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_adset_details(adset_id="123", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            assert "effective_status" in params["fields"]
