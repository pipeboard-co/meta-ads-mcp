import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.adsets import create_adset


@pytest.mark.asyncio
async def test_create_adset_includes_frequency_control_specs():
    """frequency_control_specs should be JSON-encoded in the POST params."""
    sample_response = {"id": "adset_1", "name": "Freq Cap Adset"}
    specs = [{"event": "IMPRESSIONS", "interval_days": 7, "max_frequency": 1}]

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="Freq Cap Adset",
            optimization_goal="REACH",
            billing_event="IMPRESSIONS",
            targeting={"geo_locations": {"countries": ["US"]}},
            frequency_control_specs=specs,
            access_token="test_token",
        )

        assert json.loads(result)["id"] == "adset_1"
        call_args = mock_api.call_args
        params = call_args[0][2]
        assert "frequency_control_specs" in params
        assert json.loads(params["frequency_control_specs"]) == specs


@pytest.mark.asyncio
async def test_create_adset_frequency_control_specs_multiple_rules():
    """Multiple frequency rules should all be included."""
    sample_response = {"id": "adset_2"}
    specs = [
        {"event": "IMPRESSIONS", "interval_days": 7, "max_frequency": 3},
        {"event": "IMPRESSIONS", "interval_days": 1, "max_frequency": 1},
    ]

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="Multi Rule Adset",
            optimization_goal="REACH",
            billing_event="IMPRESSIONS",
            targeting={"geo_locations": {"countries": ["US"]}},
            frequency_control_specs=specs,
            access_token="test_token",
        )

        assert json.loads(result)["id"] == "adset_2"
        params = mock_api.call_args[0][2]
        parsed = json.loads(params["frequency_control_specs"])
        assert len(parsed) == 2
        assert parsed[0]["max_frequency"] == 3
        assert parsed[1]["interval_days"] == 1


@pytest.mark.asyncio
async def test_create_adset_omits_frequency_control_specs_when_none():
    """When frequency_control_specs is not provided, it should not appear in params."""
    sample_response = {"id": "adset_3"}

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="No Freq Cap",
            optimization_goal="LINK_CLICKS",
            billing_event="IMPRESSIONS",
            targeting={"geo_locations": {"countries": ["US"]}},
            access_token="test_token",
        )

        params = mock_api.call_args[0][2]
        assert "frequency_control_specs" not in params


@pytest.mark.asyncio
async def test_create_adset_frequency_control_specs_with_other_params():
    """frequency_control_specs should coexist with other optional params."""
    sample_response = {"id": "adset_4"}
    specs = [{"event": "IMPRESSIONS", "interval_days": 7, "max_frequency": 2}]

    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        await create_adset(
            account_id="act_123",
            campaign_id="cmp_1",
            name="Full Adset",
            optimization_goal="REACH",
            billing_event="IMPRESSIONS",
            daily_budget=5000,
            targeting={"geo_locations": {"countries": ["US"]}},
            frequency_control_specs=specs,
            is_dynamic_creative=False,
            access_token="test_token",
        )

        params = mock_api.call_args[0][2]
        assert json.loads(params["frequency_control_specs"]) == specs
        assert params["daily_budget"] == "5000"
        assert params["is_dynamic_creative"] == "false"
