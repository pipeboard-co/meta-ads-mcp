"""Tests for update_ad FLEX creative swap error handling.

Tests that update_ad provides clear, actionable error messages
when Meta API rejects creative swaps on FLEX ads (error_subcode 3858355).
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import update_ad


def _unwrap_result(result_str):
    """Unwrap the result, handling the meta_api_tool data wrapping."""
    result_data = json.loads(result_str)
    if "data" in result_data:
        return json.loads(result_data["data"])
    return result_data


@pytest.mark.asyncio
class TestUpdateAdFlexSwap:
    """Test cases for update_ad FLEX creative swap (error 3858355)."""

    async def test_flex_swap_3858355_returns_workaround(self):
        """When Meta rejects creative swap with 3858355, return clear workaround."""

        api_error = {
            "error": {
                "message": "HTTP Error: 400",
                "details": {
                    "error": {
                        "message": (
                            "The first image or video of the first asset group for "
                            "flexible format must match the image or video in the "
                            "creative specification."
                        ),
                        "type": "OAuthException",
                        "code": 100,
                        "error_subcode": 3858355,
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

            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="new_creative_456",
                access_token="test_token"
            )

            result_data = _unwrap_result(result)
            assert result_data["error"] == "Cannot swap creative on this ad due to FLEX image mismatch"
            assert result_data["error_subcode"] == 3858355
            assert "workaround" in result_data
            assert "create_ad" in result_data["workaround"]
            assert "PAUSED" in result_data["workaround"]
            assert result_data["ad_id"] == "test_ad_123"
            assert result_data["creative_id"] == "new_creative_456"

    async def test_flex_swap_success_passes_through(self):
        """Successful creative swap returns the API response."""

        success_response = {"success": True}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = success_response

            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="new_creative_456",
                access_token="test_token"
            )

            result_data = _unwrap_result(result)
            assert result_data["success"] is True

    async def test_other_errors_not_intercepted(self):
        """Non-3858355 errors pass through unchanged."""

        api_error = {
            "error": {
                "message": "HTTP Error: 400",
                "details": {
                    "error": {
                        "message": "Some other error",
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

            result = await update_ad(
                ad_id="test_ad_123",
                creative_id="new_creative_456",
                access_token="test_token"
            )

            result_data = _unwrap_result(result)
            # Should pass through the raw error, not the workaround message
            assert "workaround" not in result_data
            assert "error" in result_data

    async def test_status_update_ignores_3858355_check(self):
        """Status-only updates skip the creative swap error check."""

        success_response = {"success": True}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = success_response

            result = await update_ad(
                ad_id="test_ad_123",
                status="PAUSED",
                access_token="test_token"
            )

            result_data = _unwrap_result(result)
            assert result_data["success"] is True
