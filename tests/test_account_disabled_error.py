"""Tests for distinguishing policy-blocked errors from token-expiry errors.

Meta returns code 368 ("action disallowed") and code 190 / subcode 459
("user checkpointed") for cases where the access token is still valid but
the requested action / account is restricted. The library must NOT
invalidate the token in those cases and MUST surface a distinct
is_account_disabled flag so callers can branch on it.

Other code 190 subcodes (458, 460, 463, 464, 467) are genuine session
errors and keep the existing invalidate-token + reauth path.
"""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from meta_ads_mcp.core import api as api_module
from meta_ads_mcp.core.api import (
    GraphAPIError,
    _is_account_disabled_error,
    make_api_request,
)


class TestIsAccountDisabledError:
    """Pure helper — covers the code/subcode classification."""

    def test_code_368_is_account_disabled(self):
        assert _is_account_disabled_error(368, None) is True
        assert _is_account_disabled_error(368, 1404082) is True

    def test_code_190_subcode_459_is_account_disabled(self):
        assert _is_account_disabled_error(190, 459) is True

    @pytest.mark.parametrize("subcode", [458, 460, 463, 464, 467])
    def test_code_190_other_subcodes_are_not_account_disabled(self, subcode):
        # Genuine session errors — keep the reauth path
        assert _is_account_disabled_error(190, subcode) is False

    def test_code_190_no_subcode_is_not_account_disabled(self):
        assert _is_account_disabled_error(190, None) is False

    def test_unrelated_codes_are_not_account_disabled(self):
        assert _is_account_disabled_error(4, None) is False
        assert _is_account_disabled_error(102, None) is False
        assert _is_account_disabled_error(100, 33) is False
        assert _is_account_disabled_error(None, None) is False


class TestGraphAPIError:
    """The exception type checks codes at __init__ time and decides whether
    to invalidate the token."""

    def test_code_368_does_not_invalidate_token(self):
        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv:
            GraphAPIError({
                "code": 368,
                "message": "The action attempted has been deemed abusive",
            })
            mock_inv.assert_not_called()

    def test_code_190_subcode_459_does_not_invalidate_token(self):
        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv:
            GraphAPIError({
                "code": 190,
                "error_subcode": 459,
                "message": "User has been checkpointed",
            })
            mock_inv.assert_not_called()

    def test_code_190_subcode_463_still_invalidates_token(self):
        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv:
            GraphAPIError({
                "code": 190,
                "error_subcode": 463,
                "message": "Session has expired",
            })
            mock_inv.assert_called_once()

    def test_code_190_no_subcode_still_invalidates_token(self):
        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv:
            GraphAPIError({
                "code": 190,
                "message": "Error validating access token",
            })
            mock_inv.assert_called_once()

    def test_code_4_does_not_invalidate_token(self):
        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv:
            GraphAPIError({
                "code": 4,
                "error_subcode": 1504022,
                "message": "Application request limit reached",
            })
            mock_inv.assert_not_called()


def _build_http_error(status: int, body: dict) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://graph.facebook.com/v24.0/act_123/insights")
    response = httpx.Response(status, request=request, json=body)
    return httpx.HTTPStatusError("error", request=request, response=response)


class TestMakeApiRequestHttpErrors:
    """End-to-end on the HTTP error handler: account-disabled errors flow
    through with the is_account_disabled flag, token errors trigger
    invalidate_token and DO NOT set the flag."""

    @pytest.mark.asyncio
    async def test_code_368_returns_is_account_disabled_flag(self):
        body = {
            "error": {
                "message": "The action attempted has been deemed abusive",
                "type": "OAuthException",
                "code": 368,
                "error_subcode": 1404082,
                "fbtrace_id": "abc",
            }
        }
        http_err = _build_http_error(400, body)

        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        client.get = AsyncMock(side_effect=http_err)

        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv, \
                patch.object(api_module, "httpx") as mock_httpx:
            mock_httpx.AsyncClient = MagicMock(return_value=client)
            mock_httpx.HTTPStatusError = httpx.HTTPStatusError
            result = await make_api_request("act_123/insights", "tok")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"].get("is_account_disabled") is True
        assert result["error"].get("error_code") == 368
        assert result["error"].get("error_subcode") == 1404082
        # Original Meta error details preserved
        assert result["error"]["details"]["error"]["code"] == 368
        mock_inv.assert_not_called()

    @pytest.mark.asyncio
    async def test_code_190_subcode_459_returns_is_account_disabled_flag(self):
        body = {
            "error": {
                "message": "User has been checkpointed",
                "type": "OAuthException",
                "code": 190,
                "error_subcode": 459,
            }
        }
        http_err = _build_http_error(400, body)

        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        client.get = AsyncMock(side_effect=http_err)

        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv, \
                patch.object(api_module, "httpx") as mock_httpx:
            mock_httpx.AsyncClient = MagicMock(return_value=client)
            mock_httpx.HTTPStatusError = httpx.HTTPStatusError
            result = await make_api_request("act_123/insights", "tok")

        assert result["error"].get("is_account_disabled") is True
        assert result["error"].get("error_code") == 190
        assert result["error"].get("error_subcode") == 459
        mock_inv.assert_not_called()

    @pytest.mark.asyncio
    async def test_code_190_subcode_463_does_not_set_flag_and_invalidates(self):
        body = {
            "error": {
                "message": "Session has expired",
                "type": "OAuthException",
                "code": 190,
                "error_subcode": 463,
            }
        }
        http_err = _build_http_error(400, body)

        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        client.get = AsyncMock(side_effect=http_err)

        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv, \
                patch.object(api_module, "httpx") as mock_httpx:
            mock_httpx.AsyncClient = MagicMock(return_value=client)
            mock_httpx.HTTPStatusError = httpx.HTTPStatusError
            result = await make_api_request("act_123/insights", "tok")

        assert "is_account_disabled" not in result["error"]
        mock_inv.assert_called_once()

    @pytest.mark.asyncio
    async def test_code_190_no_subcode_does_not_set_flag_and_invalidates(self):
        body = {
            "error": {
                "message": "Error validating access token",
                "type": "OAuthException",
                "code": 190,
            }
        }
        http_err = _build_http_error(400, body)

        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        client.get = AsyncMock(side_effect=http_err)

        with patch.object(api_module.auth_manager, "invalidate_token") as mock_inv, \
                patch.object(api_module, "httpx") as mock_httpx:
            mock_httpx.AsyncClient = MagicMock(return_value=client)
            mock_httpx.HTTPStatusError = httpx.HTTPStatusError
            result = await make_api_request("act_123/insights", "tok")

        assert "is_account_disabled" not in result["error"]
        mock_inv.assert_called_once()
