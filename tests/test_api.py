"""Tests for core API request behavior — token reduction fixes."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx


class TestHttpErrorSlimming:
    @pytest.mark.asyncio
    async def test_http_error_response_has_no_full_response(self):
        """HTTP error returns must NOT include full_response (leaks tokens + access token URLs)."""
        from meta_ads_mcp.core.api import make_api_request

        # Build a minimal mock HTTPStatusError
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.headers = {}
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid parameter",
                "type": "OAuthException",
                "code": 100,
                "fbtrace_id": "abc123",
            }
        }
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = "https://graph.facebook.com/v25.0/me?access_token=EAAabc123secret"

        http_error = httpx.HTTPStatusError(
            message="400 Bad Request",
            request=mock_request,
            response=mock_response,
        )
        mock_response.raise_for_status.side_effect = http_error
        mock_response.url = mock_request.url

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = await make_api_request("me", "test_token")

        assert "error" in result
        assert "full_response" not in result["error"], (
            "full_response leaks headers and access token URLs — must be removed"
        )
        assert "details" in result["error"]


class TestPagingUrlStripping:
    @pytest.mark.asyncio
    async def test_paging_urls_stripped_from_success_response(self):
        """paging.next / paging.previous embed the full access token — must be stripped."""
        from meta_ads_mcp.core.api import make_api_request

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": [{"id": "123", "name": "reach"}],
            "paging": {
                "cursors": {
                    "before": "cursor_before_abc",
                    "after": "cursor_after_xyz",
                },
                "next": "https://graph.facebook.com/v25.0/insights?access_token=EAAtoken&after=cursor_after_xyz",
                "previous": "https://graph.facebook.com/v25.0/insights?access_token=EAAtoken&before=cursor_before_abc",
            },
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = await make_api_request("act_123/insights", "test_token")

        assert "paging" in result
        assert "next" not in result["paging"], (
            "paging.next embeds access token in URL — must be stripped"
        )
        assert "previous" not in result["paging"], (
            "paging.previous embeds access token in URL — must be stripped"
        )
        assert "cursors" in result["paging"], "paging.cursors must be preserved for pagination"


class TestInsightsMetadataStripping:
    @pytest.mark.asyncio
    async def test_insights_metadata_stripped(self):
        """title, description, id fields in insights data items are noise — must be stripped."""
        from meta_ads_mcp.core.api import make_api_request

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "17841473732194608/insights/reach/lifetime",
                    "name": "reach",
                    "title": "Reach",
                    "description": "The number of unique accounts that have seen any of your posts at least once.",
                    "values": [{"value": 1200, "end_time": "2026-03-14T07:00:00+0000"}],
                    "period": "lifetime",
                }
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = await make_api_request("17841473732194608/insights", "test_token")

        assert "data" in result
        item = result["data"][0]
        assert "title" not in item, "title is verbose metadata — must be stripped"
        assert "description" not in item, "description is verbose metadata — must be stripped"
        assert "id" not in item, "id is a noisy path string — must be stripped"
        assert "name" in item, "name must be preserved (identifies the metric)"
        assert "values" in item, "values must be preserved (the actual data)"


class TestInsightsMetadataDiscriminator:
    @pytest.mark.asyncio
    async def test_campaign_list_id_not_stripped(self):
        """_strip_insights_metadata must not fire on campaign/adset/ad list shapes."""
        from meta_ads_mcp.core.api import make_api_request

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": [
                {"id": "123456789", "name": "Campaign A", "status": "ACTIVE"},
                {"id": "987654321", "name": "Campaign B", "status": "PAUSED"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = await make_api_request("act_123/campaigns", "test_token")

        assert result["data"][0]["id"] == "123456789", "id must not be stripped from list responses"
        assert result["data"][1]["id"] == "987654321", "id must not be stripped from list responses"
