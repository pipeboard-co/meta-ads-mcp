"""Tests for campaign field completeness (v25.0)."""

import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.campaigns import get_campaigns, get_campaign_details


class TestGetCampaignsFields:
    @pytest.mark.asyncio
    async def test_fields_include_effective_status(self):
        mock_response = {"data": [{"id": "123", "effective_status": "ACTIVE"}]}
        with patch(
            "meta_ads_mcp.core.campaigns.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_campaigns(account_id="act_123", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            fields = params["fields"]
            assert "effective_status" in fields

    @pytest.mark.asyncio
    async def test_fields_include_spend_cap(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.campaigns.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_campaigns(account_id="act_123", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            fields = params["fields"]
            assert "spend_cap" in fields

    @pytest.mark.asyncio
    async def test_fields_include_budget_remaining(self):
        mock_response = {"data": []}
        with patch(
            "meta_ads_mcp.core.campaigns.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_campaigns(account_id="act_123", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            fields = params["fields"]
            assert "budget_remaining" in fields


class TestGetCampaignDetailsFields:
    @pytest.mark.asyncio
    async def test_fields_include_effective_status(self):
        mock_response = {"id": "123", "effective_status": "ACTIVE"}
        with patch(
            "meta_ads_mcp.core.campaigns.make_api_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            await get_campaign_details(campaign_id="123", access_token="test_token")
            call_args = mock_api.call_args
            params = call_args[0][2]
            fields = params["fields"]
            assert "effective_status" in fields
