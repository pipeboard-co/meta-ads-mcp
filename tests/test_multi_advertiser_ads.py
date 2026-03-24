import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.adsets import create_adset, update_adset


@pytest.mark.asyncio
async def test_create_adset_includes_multi_advertiser_ads_opt_out():
    """multi_advertiser_ads=0 should be sent as string '0' in POST params."""
    sample_response = {"id": "adset_1"}

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="Opt Out Adset",
            optimization_goal="LINK_CLICKS",
            billing_event="IMPRESSIONS",
            targeting={"geo_locations": {"countries": ["US"]}},
            multi_advertiser_ads=0,
            access_token="test_token",
        )

        assert json.loads(result)["id"] == "adset_1"
        params = mock_api.call_args[0][2]
        assert params["multi_advertiser_ads"] == "0"


@pytest.mark.asyncio
async def test_create_adset_includes_multi_advertiser_ads_opt_in():
    """multi_advertiser_ads=1 should be sent as string '1' in POST params."""
    sample_response = {"id": "adset_2"}

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="Opt In Adset",
            optimization_goal="LINK_CLICKS",
            billing_event="IMPRESSIONS",
            targeting={"geo_locations": {"countries": ["US"]}},
            multi_advertiser_ads=1,
            access_token="test_token",
        )

        assert json.loads(result)["id"] == "adset_2"
        params = mock_api.call_args[0][2]
        assert params["multi_advertiser_ads"] == "1"


@pytest.mark.asyncio
async def test_create_adset_omits_multi_advertiser_ads_when_none():
    """When multi_advertiser_ads is not provided, it should not appear in params."""
    sample_response = {"id": "adset_3"}

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="No Multi Adset",
            optimization_goal="LINK_CLICKS",
            billing_event="IMPRESSIONS",
            targeting={"geo_locations": {"countries": ["US"]}},
            access_token="test_token",
        )

        params = mock_api.call_args[0][2]
        assert "multi_advertiser_ads" not in params


@pytest.mark.asyncio
async def test_create_adset_multi_advertiser_ads_coexists_with_other_params():
    """multi_advertiser_ads should coexist with other optional params."""
    sample_response = {"id": "adset_4"}

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="Full Adset",
            optimization_goal="LINK_CLICKS",
            billing_event="IMPRESSIONS",
            daily_budget=5000,
            targeting={"geo_locations": {"countries": ["US"]}},
            is_dynamic_creative=False,
            multi_advertiser_ads=0,
            access_token="test_token",
        )

        params = mock_api.call_args[0][2]
        assert params["multi_advertiser_ads"] == "0"
        assert params["daily_budget"] == "5000"
        assert params["is_dynamic_creative"] == "false"


@pytest.mark.asyncio
async def test_update_adset_includes_multi_advertiser_ads():
    """update_adset should pass multi_advertiser_ads as string in params."""
    sample_response = {"success": True}

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await update_adset(
            adset_id="120",
            multi_advertiser_ads=0,
            access_token="test_token",
        )

        assert json.loads(result)["success"] is True
        params = mock_api.call_args[0][2]
        assert params["multi_advertiser_ads"] == "0"


@pytest.mark.asyncio
async def test_update_adset_omits_multi_advertiser_ads_when_none():
    """When multi_advertiser_ads is not provided to update_adset, it should not appear in params."""
    sample_response = {"success": True}

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        await update_adset(
            adset_id="120",
            name="Renamed",
            access_token="test_token",
        )

        params = mock_api.call_args[0][2]
        assert "multi_advertiser_ads" not in params
