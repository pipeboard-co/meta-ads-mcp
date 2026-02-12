"""Tests for FLEX (DEGREES_OF_FREEDOM) creative features.

Tests for create_ad_creative and update_ad_creative support for:
- optimization_type="DEGREES_OF_FREEDOM" in asset_feed_spec
- Multiple image_hashes (up to 10)
- Multiple messages (primary text variants)
- Validation of mutual exclusivity and limits
- Backward compatibility (no optimization_type → same behavior as before)
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import create_ad_creative, update_ad_creative


@pytest.mark.asyncio
class TestFlexCreatives:
    """Test cases for FLEX (Advantage+) creative features."""

    async def test_flex_creative_includes_optimization_type(self):
        """FLEX creative with optimization_type='DEGREES_OF_FREEDOM' includes it in asset_feed_spec."""
        sample_creative_data = {
            "id": "123456789",
            "name": "FLEX Creative",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="FLEX Creative",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                optimization_type="DEGREES_OF_FREEDOM",
                call_to_action_type="LEARN_MORE"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            assert "asset_feed_spec" in creative_data
            assert creative_data["asset_feed_spec"]["optimization_type"] == "DEGREES_OF_FREEDOM"

    async def test_flex_creative_multiple_image_hashes(self):
        """Multiple image_hashes produces correct images array in asset_feed_spec."""
        sample_creative_data = {
            "id": "123456789",
            "name": "Multi-Image FLEX",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Multi-Image FLEX",
                image_hashes=["hash1", "hash2", "hash3"],
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                optimization_type="DEGREES_OF_FREEDOM"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            assert "asset_feed_spec" in creative_data
            assert creative_data["asset_feed_spec"]["images"] == [
                {"hash": "hash1"},
                {"hash": "hash2"},
                {"hash": "hash3"}
            ]

    async def test_flex_creative_multiple_messages(self):
        """Multiple messages produces correct bodies array in asset_feed_spec."""
        sample_creative_data = {
            "id": "123456789",
            "name": "Multi-Message FLEX",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Multi-Message FLEX",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                messages=["Primary text A", "Primary text B", "Primary text C"],
                optimization_type="DEGREES_OF_FREEDOM"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            assert "asset_feed_spec" in creative_data
            assert creative_data["asset_feed_spec"]["bodies"] == [
                {"text": "Primary text A"},
                {"text": "Primary text B"},
                {"text": "Primary text C"}
            ]

    async def test_validation_cannot_mix_image_hash_and_image_hashes(self):
        """Cannot specify both image_hash and image_hashes."""
        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test",
            image_hash="abc123",
            image_hashes=["hash1", "hash2"],
            page_id="987654321"
        )

        result_data = json.loads(result)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Cannot specify both 'image_hash' and 'image_hashes'" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Cannot specify both 'image_hash' and 'image_hashes'" in result_data["error"]

    async def test_validation_cannot_mix_message_and_messages(self):
        """Cannot specify both message and messages."""
        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test",
            image_hash="abc123",
            page_id="987654321",
            message="Single text",
            messages=["Text A", "Text B"]
        )

        result_data = json.loads(result)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Cannot specify both 'message' and 'messages'" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Cannot specify both 'message' and 'messages'" in result_data["error"]

    async def test_validation_max_10_image_hashes(self):
        """Maximum 10 image hashes allowed for FLEX creatives."""
        too_many = [f"hash{i}" for i in range(11)]

        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test",
            image_hashes=too_many,
            page_id="987654321"
        )

        result_data = json.loads(result)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Maximum 10 image hashes" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Maximum 10 image hashes" in result_data["error"]

    async def test_validation_invalid_optimization_type(self):
        """Invalid optimization_type values are rejected."""
        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test",
            image_hash="abc123",
            page_id="987654321",
            optimization_type="INVALID_VALUE"
        )

        result_data = json.loads(result)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Invalid optimization_type" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Invalid optimization_type" in result_data["error"]

    async def test_flex_creative_single_image_uses_asset_feed_spec(self):
        """FLEX creative with single image still uses asset_feed_spec when optimization_type is set."""
        sample_creative_data = {
            "id": "123456789",
            "name": "Single Image FLEX",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Single Image FLEX",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                optimization_type="DEGREES_OF_FREEDOM"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            # Should use asset_feed_spec even with single image when optimization_type is set
            assert "asset_feed_spec" in creative_data
            assert creative_data["asset_feed_spec"]["images"] == [{"hash": "abc123"}]
            assert creative_data["asset_feed_spec"]["optimization_type"] == "DEGREES_OF_FREEDOM"
            # object_story_spec should only have page_id (no link_data)
            assert creative_data["object_story_spec"] == {"page_id": "987654321"}

    async def test_no_optimization_type_unchanged_behavior(self):
        """Without optimization_type, single image+headline uses object_story_spec (backward compat)."""
        sample_creative_data = {
            "id": "123456789",
            "name": "Simple Creative",
            "status": "ACTIVE"
        }

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

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            # Should use traditional object_story_spec with link_data
            assert "object_story_spec" in creative_data
            assert "link_data" in creative_data["object_story_spec"]
            assert creative_data["object_story_spec"]["link_data"]["image_hash"] == "abc123"
            assert "asset_feed_spec" not in creative_data

    async def test_flex_creative_full_combination(self):
        """FLEX creative with all plural params: image_hashes, messages, headlines, descriptions."""
        sample_creative_data = {
            "id": "123456789",
            "name": "Full FLEX",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Full FLEX",
                image_hashes=["hash1", "hash2"],
                page_id="987654321",
                link_url="https://example.com",
                messages=["Text A", "Text B"],
                headlines=["Headline 1", "Headline 2"],
                descriptions=["Desc 1", "Desc 2"],
                optimization_type="DEGREES_OF_FREEDOM",
                call_to_action_type="SHOP_NOW"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            afs = creative_data["asset_feed_spec"]
            assert afs["optimization_type"] == "DEGREES_OF_FREEDOM"
            assert afs["images"] == [{"hash": "hash1"}, {"hash": "hash2"}]
            assert afs["bodies"] == [{"text": "Text A"}, {"text": "Text B"}]
            assert afs["titles"] == [{"text": "Headline 1"}, {"text": "Headline 2"}]
            assert afs["descriptions"] == [{"text": "Desc 1"}, {"text": "Desc 2"}]
            assert afs["call_to_action_types"] == ["SHOP_NOW"]

    async def test_image_hashes_without_optimization_type_uses_asset_feed(self):
        """image_hashes (plural) triggers asset_feed_spec even without optimization_type."""
        sample_creative_data = {
            "id": "123456789",
            "name": "Multi Image",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Multi Image",
                image_hashes=["hash1", "hash2"],
                page_id="987654321",
                link_url="https://example.com",
                message="Test message"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            assert "asset_feed_spec" in creative_data
            assert creative_data["asset_feed_spec"]["images"] == [
                {"hash": "hash1"}, {"hash": "hash2"}
            ]
            # No optimization_type should be set
            assert "optimization_type" not in creative_data["asset_feed_spec"]

    async def test_no_image_hash_or_image_hashes_returns_error(self):
        """Must provide either image_hash or image_hashes."""
        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test",
            page_id="987654321"
        )

        result_data = json.loads(result)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "image hash" in error_data["error"].lower()
        else:
            assert "error" in result_data
            assert "image hash" in result_data["error"].lower()


@pytest.mark.asyncio
class TestFlexCreativesUpdate:
    """Test cases for FLEX creative support in update_ad_creative."""

    async def test_update_with_optimization_type(self):
        """Update creative with optimization_type includes it in asset_feed_spec."""
        sample_creative_data = {
            "id": "123456789",
            "name": "Updated FLEX",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                optimization_type="DEGREES_OF_FREEDOM",
                headlines=["New Headline"]
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            assert "asset_feed_spec" in creative_data
            assert creative_data["asset_feed_spec"]["optimization_type"] == "DEGREES_OF_FREEDOM"

    async def test_update_with_messages_plural(self):
        """Update creative with messages (plural) produces correct bodies array."""
        sample_creative_data = {
            "id": "123456789",
            "name": "Updated",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                messages=["Text A", "Text B"]
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            assert "asset_feed_spec" in creative_data
            assert creative_data["asset_feed_spec"]["bodies"] == [
                {"text": "Text A"}, {"text": "Text B"}
            ]

    async def test_update_validation_cannot_mix_message_and_messages(self):
        """Cannot specify both message and messages in update."""
        result = await update_ad_creative(
            access_token="test_token",
            creative_id="123456789",
            message="Single",
            messages=["A", "B"]
        )

        result_data = json.loads(result)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Cannot specify both 'message' and 'messages'" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Cannot specify both 'message' and 'messages'" in result_data["error"]

    async def test_update_validation_invalid_optimization_type(self):
        """Invalid optimization_type rejected in update."""
        result = await update_ad_creative(
            access_token="test_token",
            creative_id="123456789",
            optimization_type="BAD_VALUE"
        )

        result_data = json.loads(result)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Invalid optimization_type" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Invalid optimization_type" in result_data["error"]

    async def test_update_optimization_type_alone_triggers_asset_feed(self):
        """Setting only optimization_type triggers asset_feed_spec path."""
        sample_creative_data = {
            "id": "123456789",
            "name": "FLEX",
            "status": "ACTIVE"
        }

        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data

            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                optimization_type="DEGREES_OF_FREEDOM"
            )

            result_data = json.loads(result)
            assert result_data["success"] is True

            call_args_list = mock_api.call_args_list
            first_call = call_args_list[0]
            creative_data = first_call[0][2]

            assert "asset_feed_spec" in creative_data
            assert creative_data["asset_feed_spec"]["optimization_type"] == "DEGREES_OF_FREEDOM"
