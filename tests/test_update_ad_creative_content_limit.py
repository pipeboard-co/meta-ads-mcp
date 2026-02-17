"""Tests for update_ad_creative content update limitation handling.

Tests that update_ad_creative provides clear, actionable error messages
when Meta API rejects content updates (error_subcode 1815573).
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import update_ad_creative


def _unwrap_result(result_str):
    """Unwrap the result, handling the meta_api_tool data wrapping."""
    result_data = json.loads(result_str)
    if "data" in result_data:
        return json.loads(result_data["data"])
    return result_data


@pytest.mark.asyncio
class TestUpdateAdCreativeContentLimit:
    """Test cases for update_ad_creative content update limitation."""

    async def test_content_update_1815573_returns_workaround(self):
        """When Meta rejects content update with 1815573, return clear workaround."""

        # Simulate the error structure returned by make_api_request for HTTP 400
        api_error = {
            "error": {
                "message": "HTTP Error: 400",
                "details": {
                    "error": {
                        "message": "(#100) The parameter is not supported",
                        "type": "OAuthException",
                        "code": 100,
                        "error_subcode": 1815573,
                        "fbtrace_id": "abc123"
                    }
                },
                "full_response": {
                    "status_code": 400
                }
            }
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = api_error

            result = await update_ad_creative(
                creative_id="test_creative_123",
                message="New message text",
                access_token="test_token"
            )

            result_data = _unwrap_result(result)
            assert result_data["error"] == "Content updates are not allowed on existing creatives"
            assert "workaround" in result_data
            assert "create_ad_creative" in result_data["workaround"]
            assert "update_ad" in result_data["workaround"]
            assert result_data["creative_id"] == "test_creative_123"
            assert "attempted_updates" in result_data

    async def test_content_update_1815573_headline(self):
        """Headline update also triggers the helpful error."""

        api_error = {
            "error": {
                "message": "HTTP Error: 400",
                "details": {
                    "error": {
                        "message": "(#100) The parameter is not supported",
                        "type": "OAuthException",
                        "code": 100,
                        "error_subcode": 1815573,
                    }
                },
                "full_response": {"status_code": 400}
            }
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = api_error

            result = await update_ad_creative(
                creative_id="test_creative_123",
                headline="New headline",
                access_token="test_token"
            )

            result_data = _unwrap_result(result)
            assert result_data["error"] == "Content updates are not allowed on existing creatives"
            assert "workaround" in result_data

    async def test_name_update_still_works(self):
        """Name-only updates should succeed normally (not trigger 1815573 path)."""

        success_response = {"id": "test_creative_123"}
        creative_details = {
            "id": "test_creative_123",
            "name": "Updated Name",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.side_effect = [success_response, creative_details]

            result = await update_ad_creative(
                creative_id="test_creative_123",
                name="Updated Name",
                access_token="test_token"
            )

            result_data = _unwrap_result(result)
            assert result_data["success"] is True
            assert result_data["creative_id"] == "test_creative_123"

    async def test_other_errors_not_intercepted(self):
        """Non-1815573 errors should pass through unchanged."""

        api_error = {
            "error": {
                "message": "HTTP Error: 400",
                "details": {
                    "error": {
                        "message": "Invalid creative ID",
                        "type": "OAuthException",
                        "code": 100,
                        "error_subcode": 9999,
                    }
                },
                "full_response": {"status_code": 400}
            }
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = api_error

            result = await update_ad_creative(
                creative_id="test_creative_123",
                message="New message",
                access_token="test_token"
            )

            result_data = _unwrap_result(result)
            # Should pass through the raw error, not the workaround message
            assert "workaround" not in result_data
            assert "error" in result_data
