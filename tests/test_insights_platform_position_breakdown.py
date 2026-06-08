"""Regression tests for get_insights breakdown=platform_position.

platform_position is a Meta-restricted breakdown: it must be paired with
publisher_platform or Meta returns "(#100) Current combination of data
breakdown columns (action_type, platform_position) is invalid". Once paired,
Meta DOES return the action-typed fields (actions, cost_per_action_type,
conversions) per placement.

A previous version of get_insights worked around the (#100) error by dropping
the action-typed fields entirely, which made leads/CPL/conversions disappear
from placement-level reports. These tests pin the corrected behavior: auto-pair
publisher_platform AND keep the action-typed fields.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.insights import get_insights


@pytest.fixture
def mock_auth_manager():
    with patch('meta_ads_mcp.core.api.auth_manager') as mock, \
         patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:
        mock.get_current_access_token.return_value = "test_access_token"
        mock.is_token_valid.return_value = True
        mock.app_id = "test_app_id"
        mock_get_token.return_value = "test_access_token"
        yield mock


async def _call_and_get_params(breakdown, **kwargs):
    """Invoke get_insights with a mocked API and return the params dict sent to Meta."""
    with patch('meta_ads_mcp.core.insights.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = {"data": []}
        await get_insights(
            object_id="act_701351919139047",
            level="account",
            time_range="last_30d",
            breakdown=breakdown,
            **kwargs,
        )
        mock_api.assert_called_once()
        return mock_api.call_args[0][2]


class TestPlatformPositionBreakdown:
    @pytest.mark.asyncio
    async def test_platform_position_keeps_action_typed_fields(self, mock_auth_manager):
        """The core regression: action-typed fields must NOT be stripped."""
        params = await _call_and_get_params("platform_position")
        fields = params["fields"].split(",")
        for f in ("actions", "action_values", "conversions", "cost_per_action_type"):
            assert f in fields, f"{f} was stripped from fields for platform_position"

    @pytest.mark.asyncio
    async def test_platform_position_auto_pairs_publisher_platform(self, mock_auth_manager):
        """publisher_platform is auto-prepended so Meta does not reject the request."""
        params = await _call_and_get_params("platform_position")
        breakdowns = params["breakdowns"].split(",")
        assert "publisher_platform" in breakdowns
        assert "platform_position" in breakdowns

    @pytest.mark.asyncio
    async def test_platform_position_does_not_force_action_breakdowns(self, mock_auth_manager):
        """No explicit action_breakdowns is sent — Meta's default action_type slicing
        applies, which returns actions per placement (verified live against Meta)."""
        params = await _call_and_get_params("platform_position")
        assert "action_breakdowns" not in params

    @pytest.mark.asyncio
    async def test_caller_action_breakdowns_still_wins(self, mock_auth_manager):
        """An explicit action_breakdowns from the caller is still respected."""
        params = await _call_and_get_params("platform_position", action_breakdowns=[])
        assert params["action_breakdowns"] == "[]"

    @pytest.mark.asyncio
    async def test_already_paired_breakdown_is_not_duplicated(self, mock_auth_manager):
        """Passing publisher_platform,platform_position does not duplicate publisher_platform."""
        params = await _call_and_get_params("publisher_platform,platform_position")
        breakdowns = params["breakdowns"].split(",")
        assert breakdowns.count("publisher_platform") == 1
