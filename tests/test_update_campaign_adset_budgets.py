"""Unit tests for update_campaign adset_budgets (CBO → ABO migration)."""

import json
import pytest
from unittest.mock import patch

from meta_ads_mcp.core.campaigns import update_campaign


@pytest.fixture
def mock_api_request():
    with patch("meta_ads_mcp.core.campaigns.make_api_request") as mock:
        mock.return_value = {"success": True, "id": "120243420658870518"}
        yield mock


@pytest.fixture
def mock_auth():
    with patch("meta_ads_mcp.core.api.auth_manager") as mgr, \
         patch("meta_ads_mcp.core.auth.get_current_access_token") as get_token:
        mgr.get_current_access_token.return_value = "tok"
        mgr.is_token_valid.return_value = True
        mgr.app_id = "app"
        get_token.return_value = "tok"
        yield mgr


@pytest.mark.asyncio
async def test_adset_budgets_forwarded_as_list(mock_api_request, mock_auth):
    budgets = [
        {"adset_id": "111", "daily_budget": 5000},
        {"adset_id": "222", "daily_budget": 7000},
    ]
    result = await update_campaign(
        campaign_id="120243420658870518",
        adset_budgets=budgets,
    )

    mock_api_request.assert_called_once()
    args, kwargs = mock_api_request.call_args
    sent_params = args[2] if len(args) > 2 else kwargs.get("params") or kwargs
    assert sent_params["adset_budgets"] == budgets

    data = json.loads(result)
    assert data["budget_strategy"] == "ad_set_level"
    assert "adset_budgets" in data["note"]


@pytest.mark.asyncio
async def test_adset_budgets_not_sent_when_omitted(mock_api_request, mock_auth):
    await update_campaign(
        campaign_id="120243420658870518",
        name="renamed",
    )
    args, kwargs = mock_api_request.call_args
    sent_params = args[2] if len(args) > 2 else kwargs.get("params") or kwargs
    assert "adset_budgets" not in sent_params


@pytest.mark.asyncio
async def test_use_adset_level_budgets_still_works_for_backcompat(mock_api_request, mock_auth):
    result = await update_campaign(
        campaign_id="120243420658870518",
        use_adset_level_budgets=True,
    )
    args, kwargs = mock_api_request.call_args
    sent_params = args[2] if len(args) > 2 else kwargs.get("params") or kwargs
    assert sent_params["daily_budget"] == ""
    assert sent_params["lifetime_budget"] == ""

    data = json.loads(result)
    assert data["budget_strategy"] == "ad_set_level"
    assert "adset_budgets" in data["note"]
