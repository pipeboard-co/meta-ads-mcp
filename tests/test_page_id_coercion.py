"""
Tests for page_id integer-to-string coercion in create_ad_creative.

Bug: When an LLM passes page_id as an integer (e.g., 641301092411249 instead of
"641301092411249"), the Meta API rejects the request because object_story_spec
is serialized with a numeric page_id instead of a string.

The fix (commit 5eee32e) adds str(page_id) normalization in create_ad_creative
and in _discover_pages_for_account.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, call


class TestPageIdCoercion:
    """Tests that page_id is always coerced to a string before hitting the Meta API."""

    @pytest.mark.asyncio
    async def test_integer_page_id_is_coerced_to_string(self):
        """When page_id is passed as an integer, it should be coerced to a string
        in the object_story_spec sent to the Meta API."""
        from meta_ads_mcp.core.ads import create_ad_creative

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:

            mock_get_token.return_value = "test_token"
            mock_api.return_value = {"id": "fake_creative_123"}

            await create_ad_creative(
                account_id="act_123456789",
                image_hash="abc123hash",
                page_id=641301092411249,  # INTEGER — the bug scenario
                name="Test Creative",
                message="Test message",
                link_url="https://example.com",
                access_token="test_token",
            )

            # The first call to make_api_request is the POST to create the creative
            create_call = mock_api.call_args_list[0]
            creative_data = create_call.args[2]  # third positional arg is params/data

            oss = creative_data["object_story_spec"]
            # If oss was already JSON-serialized (by make_api_request prep), parse it
            if isinstance(oss, str):
                oss = json.loads(oss)

            assert isinstance(oss["page_id"], str), (
                f"page_id should be a string but got {type(oss['page_id']).__name__}: {oss['page_id']!r}"
            )
            assert oss["page_id"] == "641301092411249"

    @pytest.mark.asyncio
    async def test_string_page_id_stays_string(self):
        """When page_id is already a string, it should remain a string."""
        from meta_ads_mcp.core.ads import create_ad_creative

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:

            mock_get_token.return_value = "test_token"
            mock_api.return_value = {"id": "fake_creative_123"}

            await create_ad_creative(
                account_id="act_123456789",
                image_hash="abc123hash",
                page_id="641301092411249",  # STRING — should work fine
                name="Test Creative",
                message="Test message",
                link_url="https://example.com",
                access_token="test_token",
            )

            create_call = mock_api.call_args_list[0]
            creative_data = create_call.args[2]

            oss = creative_data["object_story_spec"]
            if isinstance(oss, str):
                oss = json.loads(oss)

            assert isinstance(oss["page_id"], str)
            assert oss["page_id"] == "641301092411249"

    @pytest.mark.asyncio
    async def test_discovered_page_id_is_string(self):
        """When page_id is auto-discovered via _discover_pages_for_account,
        it should be a string in the API call."""
        from meta_ads_mcp.core.ads import create_ad_creative

        # Simulate _discover_pages_for_account returning an integer page_id
        # (as could happen if the Meta API returns numeric IDs)
        mock_discovery = {
            "success": True,
            "page_id": 641301092411249,  # INTEGER from discovery
            "page_name": "Test Page",
            "source": "client_pages",
        }

        with patch('meta_ads_mcp.core.ads._discover_pages_for_account', new_callable=AsyncMock) as mock_discover, \
             patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api, \
             patch('meta_ads_mcp.core.auth.get_current_access_token') as mock_get_token:

            mock_get_token.return_value = "test_token"
            mock_discover.return_value = mock_discovery
            mock_api.return_value = {"id": "fake_creative_123"}

            await create_ad_creative(
                account_id="act_123456789",
                image_hash="abc123hash",
                # page_id omitted — triggers auto-discovery
                name="Test Creative",
                message="Test message",
                link_url="https://example.com",
                access_token="test_token",
            )

            create_call = mock_api.call_args_list[0]
            creative_data = create_call.args[2]

            oss = creative_data["object_story_spec"]
            if isinstance(oss, str):
                oss = json.loads(oss)

            assert isinstance(oss["page_id"], str), (
                f"Discovered page_id should be a string but got {type(oss['page_id']).__name__}: {oss['page_id']!r}"
            )
            assert oss["page_id"] == "641301092411249"
