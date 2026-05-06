#!/usr/bin/env python3
"""
Unit Tests for CBO Budget Conflict Detection in create_adset

When a campaign uses Campaign Budget Optimization (CBO), the campaign itself holds
a daily_budget or lifetime_budget. Meta rejects any create_adset request that also
includes a budget at the ad-set level, returning a cryptic "Invalid parameter" error
(subcode 1885621).

This test suite validates that create_adset detects the conflict early, before hitting
Meta's API, and returns a clear, actionable error message.

Usage:
    uv run python -m pytest tests/test_cbo_budget_conflict.py -v
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, call

from meta_ads_mcp.core.adsets import create_adset


def parse_result(result: str) -> dict:
    """
    Parse the result from create_adset, handling the data wrapper.

    The meta_api_tool decorator wraps responses in {"data": "..."} format,
    where the inner value is a JSON string. This helper unwraps it.
    """
    result_data = json.loads(result)
    if "data" in result_data and isinstance(result_data["data"], str):
        return json.loads(result_data["data"])
    return result_data


@pytest.fixture
def basic_adset_params():
    """Minimal valid adset parameters shared across tests."""
    return {
        "account_id": "act_123456789",
        "campaign_id": "campaign_111222333",
        "name": "Test Ad Set",
        "optimization_goal": "LINK_CLICKS",
        "billing_event": "IMPRESSIONS",
        "targeting": {
            "age_min": 18,
            "age_max": 65,
            "geo_locations": {"countries": ["US"]},
        },
        "access_token": "test_token",
    }


@pytest.fixture
def cbo_campaign_response():
    """API response simulating a CBO campaign with a daily_budget."""
    return {
        "id": "campaign_111222333",
        "name": "My CBO Campaign",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "daily_budget": "10000",  # $100 — indicates CBO mode
    }


@pytest.fixture
def cbo_campaign_lifetime_response():
    """API response simulating a CBO campaign with a lifetime_budget."""
    return {
        "id": "campaign_111222333",
        "name": "My CBO Lifetime Campaign",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "lifetime_budget": "500000",  # $5000 — indicates CBO mode
    }


@pytest.fixture
def abo_campaign_response():
    """API response simulating an ABO campaign (no campaign-level budget)."""
    return {
        "id": "campaign_111222333",
        "name": "My ABO Campaign",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        # No daily_budget or lifetime_budget — ABO mode
    }


@pytest.fixture
def adset_created_response():
    """Successful adset creation response."""
    return {
        "id": "adset_999888777",
        "name": "Test Ad Set",
    }


class TestCboBudgetConflict:
    """Tests for CBO budget conflict detection in create_adset."""

    @pytest.mark.asyncio
    async def test_daily_budget_with_cbo_campaign_returns_error(
        self, basic_adset_params, cbo_campaign_response
    ):
        """
        When daily_budget is provided and the campaign already has a daily_budget,
        create_adset should return a clear error before calling the create endpoint.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = cbo_campaign_response

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        assert "error" in result_data
        assert "Budget conflict" in result_data["error"]
        assert "CBO" in result_data["error"] or "CBO" in result_data.get("details", "")
        assert "fix" in result_data
        assert "daily_budget" in result_data["fix"] or "lifetime_budget" in result_data["fix"]

        # Should have made exactly ONE call (campaign check), not two (campaign + create)
        assert mock_api.call_count == 1

    @pytest.mark.asyncio
    async def test_lifetime_budget_with_cbo_campaign_daily_budget_returns_error(
        self, basic_adset_params, cbo_campaign_response
    ):
        """
        lifetime_budget on the ad set also conflicts with a CBO campaign.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = cbo_campaign_response

            result = await create_adset(**basic_adset_params, lifetime_budget=50000)

        result_data = parse_result(result)

        assert "error" in result_data
        assert "Budget conflict" in result_data["error"]
        assert mock_api.call_count == 1

    @pytest.mark.asyncio
    async def test_lifetime_budget_with_cbo_campaign_lifetime_budget_returns_error(
        self, basic_adset_params, cbo_campaign_lifetime_response
    ):
        """
        When the campaign has a lifetime_budget (CBO), providing lifetime_budget
        on the ad set should also be caught.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = cbo_campaign_lifetime_response

            result = await create_adset(**basic_adset_params, lifetime_budget=50000)

        result_data = parse_result(result)

        assert "error" in result_data
        assert "Budget conflict" in result_data["error"]
        assert mock_api.call_count == 1

    @pytest.mark.asyncio
    async def test_daily_budget_with_abo_campaign_succeeds(
        self, basic_adset_params, abo_campaign_response, adset_created_response
    ):
        """
        When the campaign has no budget (ABO mode), providing daily_budget on the
        ad set is valid and the create request should proceed normally.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            # First call: campaign check → ABO (no budget)
            # Second call: adset create → success
            mock_api.side_effect = [abo_campaign_response, adset_created_response]

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        assert "error" not in result_data
        assert result_data["id"] == "adset_999888777"

        # Campaign check + create = 2 calls
        assert mock_api.call_count == 2

        # Verify daily_budget was sent in the create call
        create_call_params = mock_api.call_args_list[1][0][2]
        assert create_call_params["daily_budget"] == "5000"

    @pytest.mark.asyncio
    async def test_no_adset_budget_with_cbo_campaign_succeeds(
        self, basic_adset_params, cbo_campaign_response, adset_created_response
    ):
        """
        When no budget is provided for the ad set (standard CBO usage),
        create_adset should proceed without any conflict check error.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            # First call: campaign check (needed for bid_amount check; no budget provided)
            # Second call: adset create
            mock_api.side_effect = [cbo_campaign_response, adset_created_response]

            result = await create_adset(**basic_adset_params)

        result_data = parse_result(result)

        assert "error" not in result_data
        assert result_data["id"] == "adset_999888777"

    @pytest.mark.asyncio
    async def test_error_includes_campaign_name(
        self, basic_adset_params, cbo_campaign_response
    ):
        """
        The error message should include the campaign name to help the user identify
        which campaign triggered the conflict.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = cbo_campaign_response

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        # Campaign name should appear in the error
        assert "My CBO Campaign" in result_data["error"]

    @pytest.mark.asyncio
    async def test_error_includes_campaign_id(
        self, basic_adset_params, cbo_campaign_response
    ):
        """
        The error message should include the campaign ID so the user can look it up.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = cbo_campaign_response

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        assert basic_adset_params["campaign_id"] in result_data["error"]

    @pytest.mark.asyncio
    async def test_error_includes_fix_instructions(
        self, basic_adset_params, cbo_campaign_response
    ):
        """
        The error response should include a 'fix' field explaining how to resolve it.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = cbo_campaign_response

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        assert "fix" in result_data
        # The fix should mention removing budget fields
        fix_text = result_data["fix"]
        assert "daily_budget" in fix_text or "budget" in fix_text.lower()

    @pytest.mark.asyncio
    async def test_error_includes_alternative(
        self, basic_adset_params, cbo_campaign_response
    ):
        """
        The error response should include an 'alternative' field for users who
        actually want ABO (ad set-level budgets).
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = cbo_campaign_response

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        assert "alternative" in result_data

    @pytest.mark.asyncio
    async def test_campaign_check_failure_falls_through_to_create(
        self, basic_adset_params, adset_created_response
    ):
        """
        If the campaign pre-flight check itself fails (e.g., network error, permission),
        create_adset should fall through and attempt the create call normally.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            # First call: campaign check fails
            # Second call: adset create succeeds
            mock_api.side_effect = [Exception("Network error"), adset_created_response]

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        # Should NOT return a budget conflict error — fell through to create
        assert "Budget conflict" not in result_data.get("error", "")
        assert result_data["id"] == "adset_999888777"

        # Both calls should have been made
        assert mock_api.call_count == 2

    @pytest.mark.asyncio
    async def test_no_budget_no_bid_amount_with_campaign_bid_cap_strategy(
        self, basic_adset_params
    ):
        """
        Regression: when no budget is provided but campaign uses LOWEST_COST_WITH_BID_CAP,
        the bid strategy check should still fire (original behavior preserved).
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = {
                "id": "campaign_111222333",
                "name": "Bid Cap Campaign",
                "bid_strategy": "LOWEST_COST_WITH_BID_CAP",
                # No budget — ABO or no budget
            }

            result = await create_adset(**basic_adset_params)

        result_data = parse_result(result)

        assert "error" in result_data
        assert "bid_amount is required" in result_data["error"]
        assert "LOWEST_COST_WITH_BID_CAP" in result_data["error"]

    @pytest.mark.asyncio
    async def test_daily_budget_identifies_correct_budget_type_in_error(
        self, basic_adset_params, cbo_campaign_response
    ):
        """
        The error message should identify which budget type (daily vs lifetime) is
        set on the campaign.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            # CBO campaign with daily_budget
            mock_api.return_value = cbo_campaign_response  # has daily_budget

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        assert "daily_budget" in result_data["error"]

    @pytest.mark.asyncio
    async def test_lifetime_budget_campaign_identifies_correct_budget_type_in_error(
        self, basic_adset_params, cbo_campaign_lifetime_response
    ):
        """
        The error message should identify 'lifetime_budget' when that's what the
        campaign has set.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = cbo_campaign_lifetime_response  # has lifetime_budget

            result = await create_adset(**basic_adset_params, daily_budget=5000)

        result_data = parse_result(result)

        assert "lifetime_budget" in result_data["error"]

    @pytest.mark.asyncio
    async def test_campaign_check_fetches_budget_fields(
        self, basic_adset_params, abo_campaign_response, adset_created_response
    ):
        """
        The campaign pre-flight check should request daily_budget and lifetime_budget
        fields so it can detect CBO mode.
        """
        with patch(
            "meta_ads_mcp.core.adsets.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.side_effect = [abo_campaign_response, adset_created_response]

            await create_adset(**basic_adset_params, daily_budget=5000)

        # First call is the campaign check
        campaign_check_call = mock_api.call_args_list[0]
        fields_param = campaign_check_call[0][2]["fields"]
        assert "daily_budget" in fields_param
        assert "lifetime_budget" in fields_param
