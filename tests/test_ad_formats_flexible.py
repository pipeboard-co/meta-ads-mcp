"""Tests for ad_formats parameter and AUTOMATIC_FORMAT (Flexible) default behavior.

When using optimization_type="DEGREES_OF_FREEDOM" with image_hashes, the ad_formats
should default to ["AUTOMATIC_FORMAT"] (Flexible format in Ads Manager) instead of
["SINGLE_IMAGE"]. Users can also explicitly pass ad_formats to override the default.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import create_ad_creative, update_ad_creative


@pytest.mark.asyncio
class TestAdFormatsDefaultCreate:
    """Test ad_formats defaults in create_ad_creative."""

    async def test_dof_with_image_hashes_defaults_to_automatic_format(self):
        """DEGREES_OF_FREEDOM + image_hashes should default ad_formats to AUTOMATIC_FORMAT."""
        sample_creative_data = {"id": "123", "name": "Flex", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Flexible Creative",
                image_hashes=["hash1", "hash2", "hash3"],
                page_id="987654321",
                link_url="https://example.com",
                messages=["Text A", "Text B"],
                optimization_type="DEGREES_OF_FREEDOM"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["AUTOMATIC_FORMAT"]

    async def test_dof_without_image_hashes_defaults_to_single_image(self):
        """DEGREES_OF_FREEDOM with single image_hash (no image_hashes) defaults to SINGLE_IMAGE."""
        sample_creative_data = {"id": "123", "name": "Flex", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Single Image FLEX",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test",
                optimization_type="DEGREES_OF_FREEDOM"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["SINGLE_IMAGE"]

    async def test_no_dof_defaults_to_single_image(self):
        """Without DEGREES_OF_FREEDOM, ad_formats defaults to SINGLE_IMAGE."""
        sample_creative_data = {"id": "123", "name": "Dynamic", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Dynamic Creative",
                image_hashes=["hash1", "hash2"],
                page_id="987654321",
                link_url="https://example.com",
                message="Test"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["SINGLE_IMAGE"]

    async def test_explicit_ad_formats_overrides_default(self):
        """Explicit ad_formats parameter overrides the smart default."""
        sample_creative_data = {"id": "123", "name": "Override", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Override Format",
                image_hashes=["hash1", "hash2"],
                page_id="987654321",
                link_url="https://example.com",
                message="Test",
                optimization_type="DEGREES_OF_FREEDOM",
                ad_formats=["SINGLE_IMAGE"]  # explicit override
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            # Should use the explicit value, not the AUTOMATIC_FORMAT default
            assert afs["ad_formats"] == ["SINGLE_IMAGE"]

    async def test_explicit_automatic_format_without_dof(self):
        """Explicit AUTOMATIC_FORMAT works even without DEGREES_OF_FREEDOM."""
        sample_creative_data = {"id": "123", "name": "Explicit", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Explicit Format",
                image_hashes=["hash1", "hash2"],
                page_id="987654321",
                link_url="https://example.com",
                message="Test",
                ad_formats=["AUTOMATIC_FORMAT"]
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["AUTOMATIC_FORMAT"]

    async def test_ad_formats_json_string_coercion(self):
        """ad_formats passed as JSON string is coerced to list (MCP transport compat)."""
        sample_creative_data = {"id": "123", "name": "Coerced", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Coerced Format",
                image_hashes=["hash1", "hash2"],
                page_id="987654321",
                link_url="https://example.com",
                message="Test",
                ad_formats='["AUTOMATIC_FORMAT"]'  # JSON string
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["AUTOMATIC_FORMAT"]


@pytest.mark.asyncio
class TestAdFormatsDefaultUpdate:
    """Test ad_formats defaults in update_ad_creative."""

    async def test_update_dof_defaults_to_automatic_format(self):
        """update_ad_creative with DEGREES_OF_FREEDOM defaults to AUTOMATIC_FORMAT."""
        sample_data = {"id": "123", "name": "Updated", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_data

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                optimization_type="DEGREES_OF_FREEDOM",
                headlines=["New Headline"]
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["AUTOMATIC_FORMAT"]

    async def test_update_without_dof_defaults_to_single_image(self):
        """update_ad_creative without DEGREES_OF_FREEDOM defaults to SINGLE_IMAGE."""
        sample_data = {"id": "123", "name": "Updated", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_data

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                headlines=["New Headline"]
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["SINGLE_IMAGE"]

    async def test_update_explicit_ad_formats_overrides(self):
        """update_ad_creative with explicit ad_formats overrides default."""
        sample_data = {"id": "123", "name": "Updated", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_data

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                optimization_type="DEGREES_OF_FREEDOM",
                headlines=["New Headline"],
                ad_formats=["SINGLE_IMAGE"]  # explicit override
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["SINGLE_IMAGE"]


@pytest.mark.asyncio
class TestFlexibleCreativeFullFlow:
    """Integration-style tests for the full Flexible creative flow."""

    async def test_full_flexible_creative_payload(self):
        """Full DEGREES_OF_FREEDOM + image_hashes creative produces correct Flexible payload."""
        sample_creative_data = {"id": "123", "name": "Full Flex", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Full Flexible Creative",
                image_hashes=["hash1", "hash2", "hash3"],
                page_id="987654321",
                link_url="https://example.com",
                messages=["Primary text A", "Primary text B"],
                headlines=["Headline 1", "Headline 2"],
                descriptions=["Desc 1", "Desc 2"],
                optimization_type="DEGREES_OF_FREEDOM",
                call_to_action_type="SHOP_NOW"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]

            # Key assertion: AUTOMATIC_FORMAT for Flexible
            assert afs["ad_formats"] == ["AUTOMATIC_FORMAT"]
            assert afs["optimization_type"] == "DEGREES_OF_FREEDOM"
            assert afs["images"] == [
                {"hash": "hash1"}, {"hash": "hash2"}, {"hash": "hash3"}
            ]
            assert afs["bodies"] == [
                {"text": "Primary text A"}, {"text": "Primary text B"}
            ]
            assert afs["titles"] == [
                {"text": "Headline 1"}, {"text": "Headline 2"}
            ]
            assert afs["descriptions"] == [
                {"text": "Desc 1"}, {"text": "Desc 2"}
            ]
            assert afs["call_to_action_types"] == ["SHOP_NOW"]
            assert afs["link_urls"] == [{"website_url": "https://example.com"}]

            # object_story_spec still required
            assert creative_data["object_story_spec"] == {
                "page_id": "987654321",
                "link_data": {"link": "https://example.com"}
            }

    async def test_backward_compat_simple_creative_unaffected(self):
        """Simple creative (no asset_feed_spec) is unaffected by ad_formats changes."""
        sample_creative_data = {"id": "123", "name": "Simple", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Simple Creative",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                headline="Single Headline"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]

            # Simple creative should NOT use asset_feed_spec at all
            assert "asset_feed_spec" not in creative_data
            assert "object_story_spec" in creative_data
            assert creative_data["object_story_spec"]["link_data"]["image_hash"] == "abc123"
