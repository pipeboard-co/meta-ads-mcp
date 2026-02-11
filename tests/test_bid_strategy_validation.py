#!/usr/bin/env python3
"""
Unit Tests for Bid Strategy Validation in Adset Functions

This test suite validates the bid strategy validation implementation for the
create_adset and update_adset functions in meta_ads_mcp/core/adsets.py.

Test cases cover:
- Invalid 'LOWEST_COST' bid strategy detection (common mistake)
- Bid amount requirement validation for various bid strategies
- Valid bid strategy combinations
- Helpful error messages with workarounds
- Documentation accuracy

Usage:
    uv run python -m pytest tests/test_bid_strategy_validation.py -v

Related to Error 1815857: "Bid Amount Required For The Bid Strategy Provided"
"""

import pytest
import json
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.adsets import create_adset, update_adset


def parse_result(result: str) -> dict:
    """
    Parse the result from create_adset/update_adset, handling the data wrapper.
    
    The meta_api_tool decorator wraps responses in {"data": "..."} format,
    where the inner value is a JSON string. This helper unwraps it.
    """
    result_data = json.loads(result)
    
    # If wrapped in data field (from meta_api_tool decorator), unwrap it
    if "data" in result_data and isinstance(result_data["data"], str):
        return json.loads(result_data["data"])
    
    return result_data


class TestBidStrategyValidation:
    """Test suite for bid strategy validation in create_adset"""

    @pytest.fixture
    def mock_api_request(self):
        """Mock for the make_api_request function"""
        with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock:
            mock.return_value = {
                "id": "test_adset_id",
                "name": "Test Adset",
                "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
            }
            yield mock

    @pytest.fixture
    def basic_adset_params(self):
        """Basic valid adset parameters for testing"""
        return {
            "account_id": "act_123456789",
            "campaign_id": "campaign_123456789",
            "name": "Test Adset",
            "optimization_goal": "LINK_CLICKS",
            "billing_event": "IMPRESSIONS",
            "targeting": {
                "age_min": 18,
                "age_max": 65,
                "geo_locations": {"countries": ["US"]}
            },
            "access_token": "test_token"
        }

    # ========================================
    # Tests for Invalid 'LOWEST_COST' Value
    # ========================================

    @pytest.mark.asyncio
    async def test_create_adset_rejects_invalid_lowest_cost(self, mock_api_request, basic_adset_params):
        """Test that 'LOWEST_COST' (invalid) is rejected with helpful error message"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="LOWEST_COST"
        )

        result_data = parse_result(result)

        # Should return error without calling API
        assert "error" in result_data
        assert "'LOWEST_COST' is not a valid bid_strategy value" in result_data["error"]
        assert "LOWEST_COST_WITHOUT_CAP" in result_data["workaround"]
        assert "valid_values" in result_data
        
        # API should NOT have been called
        mock_api_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_adset_rejects_invalid_lowest_cost(self, mock_api_request):
        """Test that update_adset also rejects invalid 'LOWEST_COST'"""
        result = await update_adset(
            adset_id="adset_123",
            bid_strategy="LOWEST_COST",
            access_token="test_token"
        )

        result_data = parse_result(result)

        # Should return error without calling API
        assert "error" in result_data
        assert "'LOWEST_COST' is not a valid bid_strategy value" in result_data["error"]
        assert "LOWEST_COST_WITHOUT_CAP" in result_data["workaround"]
        
        # API should NOT have been called
        mock_api_request.assert_not_called()

    # ========================================
    # Tests for Bid Amount Requirements
    # ========================================

    @pytest.mark.asyncio
    async def test_create_adset_lowest_cost_with_bid_cap_requires_bid_amount(
        self, mock_api_request, basic_adset_params
    ):
        """Test that LOWEST_COST_WITH_BID_CAP requires bid_amount"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="LOWEST_COST_WITH_BID_CAP"
            # Missing bid_amount
        )

        result_data = parse_result(result)

        # Should return error
        assert "error" in result_data
        assert "bid_amount is required" in result_data["error"]
        assert "LOWEST_COST_WITH_BID_CAP" in result_data["error"]
        assert "workaround" in result_data
        assert "LOWEST_COST_WITHOUT_CAP" in result_data["workaround"]
        assert "example_with_bid_amount" in result_data
        assert "example_without_bid_amount" in result_data
        
        # API should NOT have been called
        mock_api_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_adset_cost_cap_requires_bid_amount(
        self, mock_api_request, basic_adset_params
    ):
        """Test that COST_CAP requires bid_amount"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="COST_CAP"
            # Missing bid_amount
        )

        result_data = parse_result(result)

        # Should return error
        assert "error" in result_data
        assert "bid_amount is required" in result_data["error"]
        assert "COST_CAP" in result_data["error"]
        
        # API should NOT have been called
        mock_api_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_adset_lowest_cost_with_min_roas_requires_bid_amount(
        self, mock_api_request, basic_adset_params
    ):
        """Test that LOWEST_COST_WITH_MIN_ROAS requires bid_amount"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="LOWEST_COST_WITH_MIN_ROAS"
            # Missing bid_amount
        )

        result_data = parse_result(result)

        # Should return error
        assert "error" in result_data
        assert "bid_amount is required" in result_data["error"]
        assert "LOWEST_COST_WITH_MIN_ROAS" in result_data["error"]
        
        # API should NOT have been called
        mock_api_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_adset_lowest_cost_with_bid_cap_requires_bid_amount(
        self, mock_api_request
    ):
        """Test that update_adset also validates bid_amount requirement"""
        result = await update_adset(
            adset_id="adset_123",
            bid_strategy="LOWEST_COST_WITH_BID_CAP",
            # Missing bid_amount
            access_token="test_token"
        )

        result_data = parse_result(result)

        # Should return error
        assert "error" in result_data
        assert "bid_amount is required" in result_data["error"]
        
        # API should NOT have been called
        mock_api_request.assert_not_called()

    # ========================================
    # Tests for Valid Bid Strategy Combinations
    # ========================================

    @pytest.mark.asyncio
    async def test_create_adset_lowest_cost_without_cap_no_bid_amount_needed(
        self, mock_api_request, basic_adset_params
    ):
        """Test that LOWEST_COST_WITHOUT_CAP works without bid_amount"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="LOWEST_COST_WITHOUT_CAP"
            # No bid_amount - should be fine
        )

        result_data = parse_result(result)

        # Should succeed
        assert "error" not in result_data
        assert result_data["id"] == "test_adset_id"

        # API should have been called (pre-flight campaign check + actual create)
        assert mock_api_request.call_count >= 1
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params["bid_strategy"] == "LOWEST_COST_WITHOUT_CAP"

    @pytest.mark.asyncio
    async def test_create_adset_lowest_cost_with_bid_cap_with_bid_amount(
        self, mock_api_request, basic_adset_params
    ):
        """Test that LOWEST_COST_WITH_BID_CAP works when bid_amount is provided"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="LOWEST_COST_WITH_BID_CAP",
            bid_amount=500  # 500 cents = $5
        )

        result_data = parse_result(result)

        # Should succeed
        assert "error" not in result_data
        
        # API should have been called with both parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params["bid_strategy"] == "LOWEST_COST_WITH_BID_CAP"
        assert params["bid_amount"] == "500"

    @pytest.mark.asyncio
    async def test_create_adset_cost_cap_with_bid_amount(
        self, mock_api_request, basic_adset_params
    ):
        """Test that COST_CAP works when bid_amount is provided"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="COST_CAP",
            bid_amount=1000  # 1000 cents = $10
        )

        result_data = parse_result(result)

        # Should succeed
        assert "error" not in result_data
        
        # API should have been called
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params["bid_strategy"] == "COST_CAP"
        assert params["bid_amount"] == "1000"

    @pytest.mark.asyncio
    async def test_update_adset_bid_strategy_with_bid_amount(
        self, mock_api_request
    ):
        """Test that update_adset works when bid_amount is provided with bid_strategy"""
        result = await update_adset(
            adset_id="adset_123",
            bid_strategy="LOWEST_COST_WITH_BID_CAP",
            bid_amount=750,
            access_token="test_token"
        )

        result_data = parse_result(result)

        # Should succeed
        assert "error" not in result_data
        
        # API should have been called
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params["bid_strategy"] == "LOWEST_COST_WITH_BID_CAP"
        assert params["bid_amount"] == "750"

    @pytest.mark.asyncio
    async def test_create_adset_no_bid_strategy_no_validation_needed(
        self, mock_api_request, basic_adset_params
    ):
        """Test that no validation error when bid_strategy is not specified"""
        result = await create_adset(
            **basic_adset_params
            # No bid_strategy, no bid_amount
        )

        result_data = parse_result(result)

        # Should succeed - let Meta API handle defaults
        assert "error" not in result_data

        # API should have been called (pre-flight campaign check + actual create)
        assert mock_api_request.call_count >= 1

    @pytest.mark.asyncio
    async def test_update_adset_lowest_cost_without_cap_no_bid_amount_needed(
        self, mock_api_request
    ):
        """Test that update_adset with LOWEST_COST_WITHOUT_CAP works without bid_amount"""
        result = await update_adset(
            adset_id="adset_123",
            bid_strategy="LOWEST_COST_WITHOUT_CAP",
            access_token="test_token"
        )

        result_data = parse_result(result)

        # Should succeed
        assert "error" not in result_data
        
        # API should have been called
        mock_api_request.assert_called_once()

    # ========================================
    # Tests for Error Message Quality
    # ========================================

    @pytest.mark.asyncio
    async def test_error_message_includes_valid_values(
        self, mock_api_request, basic_adset_params
    ):
        """Test that error message includes list of valid bid strategies"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="LOWEST_COST"
        )

        result_data = parse_result(result)

        # Should include valid values
        assert "valid_values" in result_data
        valid_values = result_data["valid_values"]
        assert any("LOWEST_COST_WITHOUT_CAP" in v for v in valid_values)
        assert any("LOWEST_COST_WITH_BID_CAP" in v for v in valid_values)
        assert any("COST_CAP" in v for v in valid_values)

    @pytest.mark.asyncio
    async def test_error_message_includes_examples(
        self, mock_api_request, basic_adset_params
    ):
        """Test that bid_amount required error includes helpful examples"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="LOWEST_COST_WITH_BID_CAP"
        )

        result_data = parse_result(result)

        # Should include examples
        assert "example_with_bid_amount" in result_data
        assert "example_without_bid_amount" in result_data
        assert "LOWEST_COST_WITH_BID_CAP" in result_data["example_with_bid_amount"]
        assert "bid_amount" in result_data["example_with_bid_amount"]
        assert "LOWEST_COST_WITHOUT_CAP" in result_data["example_without_bid_amount"]

    @pytest.mark.asyncio
    async def test_error_includes_details_explanation(
        self, mock_api_request, basic_adset_params
    ):
        """Test that error includes detailed explanation"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="COST_CAP"
        )

        result_data = parse_result(result)

        # Should include details
        assert "details" in result_data
        assert "bid amount in cents" in result_data["details"]

    # ========================================
    # Regression Tests
    # ========================================

    @pytest.mark.asyncio
    async def test_bid_amount_only_no_bid_strategy_works(
        self, mock_api_request, basic_adset_params
    ):
        """Test that providing bid_amount without bid_strategy works (Meta handles defaults)"""
        result = await create_adset(
            **basic_adset_params,
            bid_amount=500
            # No bid_strategy
        )

        result_data = parse_result(result)

        # Should succeed
        assert "error" not in result_data
        
        # API should have been called with bid_amount
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params["bid_amount"] == "500"

    @pytest.mark.asyncio
    async def test_backward_compatibility_all_valid_strategies(
        self, mock_api_request, basic_adset_params
    ):
        """Test that all documented valid strategies work with correct parameters"""
        valid_strategies_requiring_bid_amount = [
            "LOWEST_COST_WITH_BID_CAP",
            "COST_CAP",
            "LOWEST_COST_WITH_MIN_ROAS"
        ]
        
        for strategy in valid_strategies_requiring_bid_amount:
            mock_api_request.reset_mock()
            
            result = await create_adset(
                **basic_adset_params,
                bid_strategy=strategy,
                bid_amount=500
            )
            
            result_data = parse_result(result)
            
            # Should succeed
            assert "error" not in result_data, f"Strategy {strategy} with bid_amount should work"
            mock_api_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_lowest_cost_without_cap_works_with_optional_bid_amount(
        self, mock_api_request, basic_adset_params
    ):
        """Test that LOWEST_COST_WITHOUT_CAP can optionally accept bid_amount"""
        result = await create_adset(
            **basic_adset_params,
            bid_strategy="LOWEST_COST_WITHOUT_CAP",
            bid_amount=500  # Optional but allowed
        )

        result_data = parse_result(result)

        # Should succeed
        assert "error" not in result_data
        
        # Both parameters should be sent
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        params = call_args[0][2]
        assert params["bid_strategy"] == "LOWEST_COST_WITHOUT_CAP"
        assert params["bid_amount"] == "500"
