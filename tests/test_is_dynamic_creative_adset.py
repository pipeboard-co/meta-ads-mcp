import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.adsets import create_adset, update_adset, get_adsets, get_adset_details


@pytest.mark.asyncio
async def test_create_adset_includes_is_dynamic_creative_true():
    sample_response = {"id": "adset_1", "name": "DC Adset"}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="DC Adset",
            optimization_goal="LINK_CLICKS",
            billing_event="IMPRESSIONS",
            targeting={"geo_locations": {"countries": ["US"]}},
            is_dynamic_creative=True,
            access_token="test_token",
        )

        assert json.loads(result)["id"] == "adset_1"
        # Verify param was sent as string boolean
        call_args = mock_api.call_args
        params = call_args[0][2]
        assert params["is_dynamic_creative"] == "true"


@pytest.mark.asyncio
async def test_update_adset_includes_is_dynamic_creative_false():
    sample_response = {"success": True}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await update_adset(
            adset_id="120",
            is_dynamic_creative=False,
            access_token="test_token",
        )

        assert json.loads(result)["success"] is True
        call_args = mock_api.call_args
        params = call_args[0][2]
        assert params["is_dynamic_creative"] == "false"


@pytest.mark.asyncio
async def test_get_adsets_fields_include_is_dynamic_creative():
    sample_response = {"data": []}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await get_adsets(account_id="act_123", access_token="test_token", limit=1)
        assert json.loads(result)["data"] == []

        call_args = mock_api.call_args
        params = call_args[0][2]
        assert "is_dynamic_creative" in params.get("fields", "")


@pytest.mark.asyncio
async def test_get_adset_details_fields_include_is_dynamic_creative():
    sample_response = {"id": "120", "name": "Test", "is_dynamic_creative": True}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await get_adset_details(adset_id="120", access_token="test_token")
        assert json.loads(result)["id"] == "120"

        call_args = mock_api.call_args
        params = call_args[0][2]
        assert "is_dynamic_creative" in params.get("fields", "")


