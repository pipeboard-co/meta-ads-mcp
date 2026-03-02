"""Tests for ad_formats parameter defaults and explicit override behavior.

ad_formats always defaults to ["SINGLE_IMAGE"] (even with DEGREES_OF_FREEDOM).
AUTOMATIC_FORMAT is NOT valid for creation/update — Meta silently ignores the
entire asset_feed_spec when it encounters it. Users can explicitly pass ad_formats
to override the default (e.g., for future-proofing if Meta adds support).
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import create_ad_creative, update_ad_creative


@pytest.mark.asyncio
class TestAdFormatsDefaultCreate:
    """Test ad_formats defaults in create_ad_creative."""

    async def test_dof_with_image_hashes_omits_ad_formats(self):
        """DEGREES_OF_FREEDOM + image_hashes should omit ad_formats entirely.

        For DOF creatives, ad_formats is not needed — Meta handles format
        selection via optimization_type=DEGREES_OF_FREEDOM.
        """
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
            assert "ad_formats" not in afs

    async def test_dof_without_image_hashes_omits_ad_formats(self):
        """DEGREES_OF_FREEDOM with single image_hash (no image_hashes) omits ad_formats."""
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
            assert "ad_formats" not in afs

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
    """Test ad_formats handling in update_ad_creative.

    With DOF content updates going through the ad endpoint, these tests verify
    that the existing ad_formats in the creative's asset_feed_spec are preserved
    or that the legacy path defaults correctly for non-DOF creatives.
    """

    async def test_update_dof_preserves_existing_ad_formats(self):
        """DOF creative update preserves existing ad_formats from asset_feed_spec."""
        existing_creative = {
            "id": "123456789",
            "asset_feed_spec": {
                "titles": [{"text": "Old"}],
                "images": [{"hash": "abc"}],
                "ad_formats": ["SINGLE_IMAGE"],
                "optimization_type": "DEGREES_OF_FREEDOM"
            }
        }

        with patch('meta_ads_mcp.core.ads._fetch_creative_details', new_callable=AsyncMock) as mock_fetch, \
             patch('meta_ads_mcp.core.ads._find_ads_by_creative_id', new_callable=AsyncMock) as mock_find, \
             patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_fetch.return_value = existing_creative
            mock_find.return_value = ["ad_999"]
            mock_api.return_value = {"success": True}

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                optimization_type="DEGREES_OF_FREEDOM",
                headlines=["New Headline"]
            )

            result_data = json.loads(result)
            assert result_data["success"] is True
            merged = result_data["merged_asset_feed_spec"]
            assert merged["ad_formats"] == ["SINGLE_IMAGE"]

    async def test_update_non_dof_creative_defaults_to_single_image(self):
        """Non-DOF creative (no asset_feed_spec) falls to legacy path with SINGLE_IMAGE default."""
        existing_creative = {
            "id": "123456789",
            "object_story_spec": {"link_data": {"message": "Old"}}
        }
        sample_data = {"id": "123", "name": "Updated", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads._fetch_creative_details', new_callable=AsyncMock) as mock_fetch, \
             patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_fetch.return_value = existing_creative
            mock_api.return_value = sample_data

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                headlines=["New Headline"]
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            # Legacy path: make_api_request called with asset_feed_spec on the creative endpoint
            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]
            assert afs["ad_formats"] == ["SINGLE_IMAGE"]

    async def test_update_dof_explicit_ad_formats_not_needed(self):
        """DOF creative update merges from existing spec, ad_formats param not used in DOF path."""
        existing_creative = {
            "id": "123456789",
            "asset_feed_spec": {
                "titles": [{"text": "Old"}],
                "images": [{"hash": "abc"}],
                "ad_formats": ["SINGLE_IMAGE"],
                "optimization_type": "DEGREES_OF_FREEDOM"
            }
        }

        with patch('meta_ads_mcp.core.ads._fetch_creative_details', new_callable=AsyncMock) as mock_fetch, \
             patch('meta_ads_mcp.core.ads._find_ads_by_creative_id', new_callable=AsyncMock) as mock_find, \
             patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_fetch.return_value = existing_creative
            mock_find.return_value = ["ad_999"]
            mock_api.return_value = {"success": True}

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                optimization_type="DEGREES_OF_FREEDOM",
                headlines=["New Headline"],
                ad_formats=["SINGLE_IMAGE"]
            )

            result_data = json.loads(result)
            assert result_data["success"] is True
            merged = result_data["merged_asset_feed_spec"]
            # ad_formats comes from existing spec (merged), not from the parameter
            assert merged["ad_formats"] == ["SINGLE_IMAGE"]


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

            # DOF creatives omit ad_formats — Meta handles format via optimization_type
            assert "ad_formats" not in afs
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
            # DOF: CTA goes in object_story_spec.link_data, not in asset_feed_spec
            assert "call_to_action_types" not in afs
            # DOF: link_urls omitted, link goes in link_data.link
            assert "link_urls" not in afs

            # Multi-image: link_data must include image_hash as primary anchor.
            # Without it, Meta silently ignores asset_feed_spec.
            # CTA is placed in link_data for DOF creatives.
            assert creative_data["object_story_spec"] == {
                "page_id": "987654321",
                "link_data": {
                    "link": "https://example.com",
                    "image_hash": "hash1",
                    "call_to_action": {"type": "SHOP_NOW", "value": {"link": "https://example.com"}},
                },
            }

    async def test_full_flexible_creative_single_image_keeps_link_data(self):
        """Single-image DEGREES_OF_FREEDOM creative keeps link_data in object_story_spec.

        Meta historically required link_data for single-image asset_feed_spec
        creatives (error 2061015). This test preserves the verified behavior.
        """
        sample_creative_data = {"id": "123", "name": "Single Flex", "status": "ACTIVE"}

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Single Image Flexible Creative",
                image_hash="hash1",
                page_id="987654321",
                link_url="https://example.com",
                messages=["Primary text A", "Primary text B"],
                headlines=["Headline 1", "Headline 2"],
                optimization_type="DEGREES_OF_FREEDOM",
                call_to_action_type="SHOP_NOW"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            creative_data = mock_api.call_args_list[0][0][2]
            afs = creative_data["asset_feed_spec"]

            assert "ad_formats" not in afs
            assert afs["optimization_type"] == "DEGREES_OF_FREEDOM"
            assert afs["images"] == [{"hash": "hash1"}]

            # Single-image: object_story_spec keeps link_data (error 2061015 without it)
            # CTA is placed in link_data for DOF creatives.
            assert creative_data["object_story_spec"] == {
                "page_id": "987654321",
                "link_data": {
                    "link": "https://example.com",
                    "call_to_action": {"type": "SHOP_NOW", "value": {"link": "https://example.com"}},
                }
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
