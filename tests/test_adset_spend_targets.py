"""
Tests that get_adsets / get_adset_details request the CBO ad set spend-limit
fields (daily_min_spend_target, daily_spend_cap, lifetime_min_spend_target,
lifetime_spend_cap) so a caller can verify whether create_adset / update_adset
actually persisted them.

Note: create_adset / update_adset themselves do NOT accept these fields as
kwargs here — they are forwarded on the Next.js (pipeboard.co) side instead,
which forks create_adset onto a direct Meta Graph API call. This file only
covers the read-side field lists, which remain served by this Python backend.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.adsets import get_adsets, get_adset_details

SPEND_TARGET_FIELDS = [
    "daily_min_spend_target",
    "daily_spend_cap",
    "lifetime_min_spend_target",
    "lifetime_spend_cap",
]


@pytest.mark.asyncio
async def test_get_adset_details_fields_include_spend_targets():
    sample_response = {
        "id": "120",
        "name": "CBO Adset",
        "daily_min_spend_target": "7000",
    }
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await get_adset_details(adset_id="120", access_token="test_token")
        data = json.loads(result)
        assert data["daily_min_spend_target"] == "7000"

        call_args = mock_api.call_args
        params = call_args[0][2]
        fields = params.get("fields", "")
        for field in SPEND_TARGET_FIELDS:
            assert field in fields


@pytest.mark.asyncio
async def test_get_adsets_fields_include_spend_targets_account_endpoint():
    sample_response = {"data": []}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        await get_adsets(account_id="act_123", access_token="test_token", limit=1)

        call_args = mock_api.call_args
        params = call_args[0][2]
        fields = params.get("fields", "")
        for field in SPEND_TARGET_FIELDS:
            assert field in fields


@pytest.mark.asyncio
async def test_get_adsets_fields_include_spend_targets_campaign_endpoint():
    sample_response = {"data": []}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        await get_adsets(
            account_id="act_123", access_token="test_token", limit=1, campaign_id="cmp_1"
        )

        call_args = mock_api.call_args
        endpoint = call_args[0][0]
        params = call_args[0][2]
        fields = params.get("fields", "")
        assert endpoint == "cmp_1/adsets"
        for field in SPEND_TARGET_FIELDS:
            assert field in fields
