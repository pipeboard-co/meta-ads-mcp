import pytest
import json
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.audiences import (
    get_custom_audiences,
    create_custom_audience,
    create_lookalike_audience,
)


class TestGetCustomAudiences:
    """Test cases for get_custom_audiences function."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful retrieval of custom audiences."""
        mock_response = {
            "data": [
                {
                    "id": "123",
                    "name": "Test Audience",
                    "subtype": "ENGAGEMENT",
                    "approximate_count": 1000,
                }
            ]
        }

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            result = await get_custom_audiences(
                account_id="act_123456789", access_token="test_token"
            )

            mock_api.assert_called_once_with(
                "act_123456789/customaudiences",
                "test_token",
                {"fields": "id,name,subtype,approximate_count,data_source,delivery_status"},
            )

            result_data = json.loads(result)
            assert result_data["data"][0]["name"] == "Test Audience"

    @pytest.mark.asyncio
    async def test_no_account_id(self):
        """Test that an empty account_id returns an error."""
        result = await get_custom_audiences(account_id="", access_token="test_token")

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_act_prefix_normalization(self):
        """Test that account_id without act_ prefix is normalized."""
        mock_response = {"data": []}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            await get_custom_audiences(
                account_id="123456789", access_token="test_token"
            )

            mock_api.assert_called_once_with(
                "act_123456789/customaudiences",
                "test_token",
                {"fields": "id,name,subtype,approximate_count,data_source,delivery_status"},
            )


class TestCreateCustomAudience:
    """Test cases for create_custom_audience function."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful creation of a custom audience."""
        mock_response = {"id": "audience_123"}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            result = await create_custom_audience(
                account_id="act_123",
                name="My Audience",
                subtype="ENGAGEMENT",
                access_token="test_token",
            )

            # Verify a POST call was made to the correct endpoint
            call_args = mock_api.call_args
            assert call_args[0][0] == "act_123/customaudiences"
            assert call_args[1].get("method") == "POST" or (
                len(call_args[0]) > 3 and call_args[0][3] == "POST"
            )

            result_data = json.loads(result)
            assert result_data["id"] == "audience_123"

    @pytest.mark.asyncio
    async def test_with_rule_dict(self):
        """Test that a rule dict is passed through to make_api_request."""
        mock_response = {"id": "audience_456"}
        rule = {"inclusions": {"operator": "or", "rules": []}}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            await create_custom_audience(
                account_id="act_123",
                name="My Audience",
                subtype="ENGAGEMENT",
                access_token="test_token",
                rule=rule,
            )

            call_args = mock_api.call_args
            # params is the third positional arg
            params = call_args[0][2]
            assert params["rule"] == rule

    @pytest.mark.asyncio
    async def test_missing_name(self):
        """Test that an empty name returns an error."""
        result = await create_custom_audience(
            account_id="act_123",
            name="",
            subtype="ENGAGEMENT",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_invalid_subtype(self):
        """Test that an invalid subtype returns an error."""
        result = await create_custom_audience(
            account_id="act_123",
            name="My Audience",
            subtype="INVALID_TYPE",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested
        assert "INVALID_TYPE" in nested["error"]

    @pytest.mark.asyncio
    async def test_ig_business_subtype_rejected(self):
        """Test that IG_BUSINESS subtype is rejected (removed in v25.0)."""
        result = await create_custom_audience(
            account_id="act_123",
            name="My IG Audience",
            subtype="IG_BUSINESS",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested
        assert "IG_BUSINESS" in nested["error"] and "v25.0" in nested["error"]


class TestCreateLookalikeAudience:
    """Test cases for create_lookalike_audience function."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful creation of a lookalike audience."""
        mock_response = {"id": "lookalike_456"}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            result = await create_lookalike_audience(
                account_id="act_123",
                name="Lookalike",
                origin_audience_id="audience_123",
                country="GR",
                access_token="test_token",
            )

            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["lookalike_spec"]["country"] == "GR"
            assert params["lookalike_spec"]["ratio"] == 0.01

            result_data = json.loads(result)
            assert result_data["id"] == "lookalike_456"

    @pytest.mark.asyncio
    async def test_default_ratio(self):
        """Test that the default ratio is 0.01."""
        mock_response = {"id": "lookalike_789"}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            await create_lookalike_audience(
                account_id="act_123",
                name="Lookalike",
                origin_audience_id="audience_123",
                country="GR",
                access_token="test_token",
            )

            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["lookalike_spec"]["ratio"] == 0.01

    @pytest.mark.asyncio
    async def test_invalid_ratio_too_high(self):
        """Test that a ratio above 0.20 returns an error."""
        result = await create_lookalike_audience(
            account_id="act_123",
            name="Lookalike",
            origin_audience_id="audience_123",
            country="GR",
            access_token="test_token",
            ratio=0.5,
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested
