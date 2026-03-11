#!/usr/bin/env python3
"""
Unit tests for audience management tools in Meta Ads MCP.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.audiences import (
    get_custom_audiences,
    create_custom_audience,
    create_lookalike_audience,
)


class TestGetCustomAudiences:
    """Test cases for get_custom_audiences function."""

    @pytest.mark.asyncio
    async def test_get_custom_audiences_success(self):
        """Test successful custom audience listing."""
        mock_response = {
            "data": [
                {
                    "id": "238400000000001",
                    "name": "Website Visitors - 30d",
                    "subtype": "WEBSITE",
                    "approximate_count": 12345,
                    "data_source": {"type": "EVENT_BASED"},
                    "delivery_status": {"code": 200, "description": "Ready"},
                },
                {
                    "id": "238400000000002",
                    "name": "Video Viewers - 30d",
                    "subtype": "VIDEO",
                    "approximate_count": 6789,
                    "data_source": {"type": "EVENT_BASED"},
                    "delivery_status": {"code": 200, "description": "Ready"},
                    "lookalike_spec": None,
                },
            ]
        }

        with patch("meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response

            result = await get_custom_audiences(
                account_id="act_123456789",
                access_token="test_token",
                limit=10,
            )

            mock_api.assert_called_once_with(
                "act_123456789/customaudiences",
                "test_token",
                {
                    "fields": "id,name,subtype,approximate_count,data_source,delivery_status,lookalike_spec",
                    "limit": 10,
                },
            )

            result_data = json.loads(result)
            assert result_data == mock_response
            assert len(result_data["data"]) == 2
            assert result_data["data"][0]["name"] == "Website Visitors - 30d"

    @pytest.mark.asyncio
    async def test_get_custom_audiences_no_account_id(self):
        """Test get_custom_audiences with empty account_id."""
        result = await get_custom_audiences(account_id="", access_token="test_token")

        result_data = json.loads(result)
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert nested_data["error"] == "No account ID provided"

    @pytest.mark.asyncio
    async def test_get_custom_audiences_default_limit(self):
        """Test get_custom_audiences uses the default limit."""
        mock_response = {"data": []}

        with patch("meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response

            result = await get_custom_audiences(
                account_id="act_123456789",
                access_token="test_token",
            )

            mock_api.assert_called_once_with(
                "act_123456789/customaudiences",
                "test_token",
                {
                    "fields": "id,name,subtype,approximate_count,data_source,delivery_status,lookalike_spec",
                    "limit": 20,
                },
            )

            result_data = json.loads(result)
            assert result_data == mock_response


class TestCreateCustomAudience:
    """Test cases for create_custom_audience function."""

    @pytest.mark.asyncio
    async def test_create_custom_audience_success_minimal(self):
        """Test successful custom audience creation with required fields only."""
        mock_response = {"id": "238400000000003"}

        with patch("meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response

            result = await create_custom_audience(
                account_id="act_123456789",
                name="CRM Customers",
                subtype="CUSTOM",
                access_token="test_token",
            )

            mock_api.assert_called_once_with(
                "act_123456789/customaudiences",
                "test_token",
                {
                    "name": "CRM Customers",
                    "subtype": "CUSTOM",
                    "retention_days": 30,
                },
                method="POST",
            )

            result_data = json.loads(result)
            assert result_data == mock_response
            assert result_data["id"] == "238400000000003"

    @pytest.mark.asyncio
    async def test_create_custom_audience_success_with_optional_fields(self):
        """Test custom audience creation with description, rule, and custom retention."""
        mock_response = {"id": "238400000000004"}
        rule = json.dumps(
            {
                "inclusions": {
                    "operator": "or",
                    "rules": [
                        {
                            "event_sources": [{"id": "1234567890", "type": "video"}],
                            "retention_seconds": 2592000,
                            "filter": {
                                "operator": "and",
                                "filters": [{"field": "event", "operator": "eq", "value": "video_view"}],
                            },
                        }
                    ],
                }
            }
        )

        with patch("meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response

            result = await create_custom_audience(
                account_id="act_123456789",
                name="Video Viewers 30d",
                subtype="VIDEO_VIEWS",
                access_token="test_token",
                description="People who watched launch videos",
                rule=rule,
                retention_days=60,
            )

            mock_api.assert_called_once_with(
                "act_123456789/customaudiences",
                "test_token",
                {
                    "name": "Video Viewers 30d",
                    "subtype": "VIDEO_VIEWS",
                    "retention_days": 60,
                    "description": "People who watched launch videos",
                    "rule": rule,
                },
                method="POST",
            )

            result_data = json.loads(result)
            assert result_data == mock_response

    @pytest.mark.asyncio
    async def test_create_custom_audience_no_account_id(self):
        """Test create_custom_audience with empty account_id."""
        result = await create_custom_audience(
            account_id="",
            name="CRM Customers",
            subtype="CUSTOM",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert nested_data["error"] == "No account ID provided"

    @pytest.mark.asyncio
    async def test_create_custom_audience_no_name(self):
        """Test create_custom_audience with empty name."""
        result = await create_custom_audience(
            account_id="act_123456789",
            name="",
            subtype="CUSTOM",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert nested_data["error"] == "No audience name provided"

    @pytest.mark.asyncio
    async def test_create_custom_audience_no_subtype(self):
        """Test create_custom_audience with empty subtype."""
        result = await create_custom_audience(
            account_id="act_123456789",
            name="CRM Customers",
            subtype="",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert nested_data["error"] == "No subtype provided"


class TestCreateLookalikeAudience:
    """Test cases for create_lookalike_audience function."""

    @pytest.mark.asyncio
    async def test_create_lookalike_audience_success_default_ratio(self):
        """Test successful lookalike audience creation with default ratio."""
        mock_response = {"id": "238400000000005"}

        with patch("meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response

            result = await create_lookalike_audience(
                account_id="act_123456789",
                name="Lookalike 1% - GR",
                origin_audience_id="238400000000001",
                country="GR",
                access_token="test_token",
            )

            mock_api.assert_called_once()
            call_args = mock_api.call_args
            assert call_args.args[0] == "act_123456789/customaudiences"
            assert call_args.args[1] == "test_token"
            assert call_args.kwargs["method"] == "POST"

            params = call_args.args[2]
            assert params["name"] == "Lookalike 1% - GR"
            assert params["subtype"] == "LOOKALIKE"
            assert params["origin_audience_id"] == "238400000000001"
            assert json.loads(params["lookalike_spec"]) == {
                "country": "GR",
                "ratio": 0.01,
                "type": "similarity",
            }

            result_data = json.loads(result)
            assert result_data == mock_response

    @pytest.mark.asyncio
    async def test_create_lookalike_audience_success_custom_ratio(self):
        """Test successful lookalike audience creation with a custom ratio."""
        mock_response = {"id": "238400000000006"}

        with patch("meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response

            result = await create_lookalike_audience(
                account_id="act_123456789",
                name="Lookalike 3% - US",
                origin_audience_id="238400000000002",
                country="US",
                access_token="test_token",
                ratio=0.03,
            )

            mock_api.assert_called_once()
            call_args = mock_api.call_args
            assert call_args.args[0] == "act_123456789/customaudiences"
            assert call_args.args[1] == "test_token"
            assert call_args.kwargs["method"] == "POST"

            params = call_args.args[2]
            assert params["name"] == "Lookalike 3% - US"
            assert params["subtype"] == "LOOKALIKE"
            assert params["origin_audience_id"] == "238400000000002"
            assert json.loads(params["lookalike_spec"]) == {
                "country": "US",
                "ratio": 0.03,
                "type": "similarity",
            }

            result_data = json.loads(result)
            assert result_data == mock_response

    @pytest.mark.asyncio
    async def test_create_lookalike_audience_no_account_id(self):
        """Test create_lookalike_audience with empty account_id."""
        result = await create_lookalike_audience(
            account_id="",
            name="Lookalike 1% - GR",
            origin_audience_id="238400000000001",
            country="GR",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert nested_data["error"] == "No account ID provided"

    @pytest.mark.asyncio
    async def test_create_lookalike_audience_no_origin_audience_id(self):
        """Test create_lookalike_audience with empty origin_audience_id."""
        result = await create_lookalike_audience(
            account_id="act_123456789",
            name="Lookalike 1% - GR",
            origin_audience_id="",
            country="GR",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested_data = json.loads(result_data["data"])
        assert nested_data["error"] == "No origin_audience_id provided"


class TestAudienceToolRegistration:
    """Ensure the audience tools are registered and discoverable."""

    @pytest.mark.asyncio
    async def test_functions_are_mcp_tools(self):
        """Ensure all audience functions are registered as MCP tools."""
        from meta_ads_mcp.core.server import mcp_server

        tools = await mcp_server.list_tools()
        tool_names = [tool.name for tool in tools]

        expected_tools = [
            "get_custom_audiences",
            "create_custom_audience",
            "create_lookalike_audience",
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"{tool_name} should be registered as an MCP tool"
