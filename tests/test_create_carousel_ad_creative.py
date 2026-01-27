"""
Tests for create_carousel_ad_creative function.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch


def extract_inner_json(result):
    """Extract inner JSON from MCP tool response which wraps in {"data": "..."}"""
    outer = json.loads(result)
    if "data" in outer and isinstance(outer["data"], str):
        return json.loads(outer["data"])
    return outer


class TestCreateCarouselAdCreativeValidation:
    """Test input validation for create_carousel_ad_creative."""

    @pytest.mark.asyncio
    async def test_missing_account_id(self):
        """Should return error when account_id is missing."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock):
            result = await create_carousel_ad_creative(
                account_id="",
                page_id="123456789",
                child_attachments=[
                    {"link": "https://example.com/1", "image_hash": "hash1"},
                    {"link": "https://example.com/2", "image_hash": "hash2"},
                ]
            )
        
        data = extract_inner_json(result)
        assert "error" in data
        assert "account ID" in data["error"]

    @pytest.mark.asyncio
    async def test_missing_page_id(self):
        """Should return error when page_id is missing."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock):
            result = await create_carousel_ad_creative(
                account_id="act_123456789",
                page_id="",
                child_attachments=[
                    {"link": "https://example.com/1", "image_hash": "hash1"},
                    {"link": "https://example.com/2", "image_hash": "hash2"},
                ]
            )
        
        data = extract_inner_json(result)
        assert "error" in data
        assert "page ID" in data["error"]

    @pytest.mark.asyncio
    async def test_too_few_cards(self):
        """Should return error when less than 2 cards provided."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock):
            result = await create_carousel_ad_creative(
                account_id="act_123456789",
                page_id="123456789",
                child_attachments=[
                    {"link": "https://example.com/1", "image_hash": "hash1"},
                ]
            )
        
        data = extract_inner_json(result)
        assert "error" in data
        assert "at least 2 cards" in data["error"]

    @pytest.mark.asyncio
    async def test_too_many_cards(self):
        """Should return error when more than 10 cards provided."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        cards = [{"link": f"https://example.com/{i}", "image_hash": f"hash{i}"} for i in range(11)]
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock):
            result = await create_carousel_ad_creative(
                account_id="act_123456789",
                page_id="123456789",
                child_attachments=cards
            )
        
        data = extract_inner_json(result)
        assert "error" in data
        assert "maximum 10 cards" in data["error"]

    @pytest.mark.asyncio
    async def test_card_missing_link(self):
        """Should return error when card is missing link."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock):
            result = await create_carousel_ad_creative(
                account_id="act_123456789",
                page_id="123456789",
                child_attachments=[
                    {"image_hash": "hash1"},  # Missing link
                    {"link": "https://example.com/2", "image_hash": "hash2"},
                ]
            )
        
        data = extract_inner_json(result)
        assert "error" in data
        assert "missing required 'link'" in data["error"]

    @pytest.mark.asyncio
    async def test_card_missing_media(self):
        """Should return error when card has neither image_hash nor video_id."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock):
            result = await create_carousel_ad_creative(
                account_id="act_123456789",
                page_id="123456789",
                child_attachments=[
                    {"link": "https://example.com/1"},  # Missing media
                    {"link": "https://example.com/2", "image_hash": "hash2"},
                ]
            )
        
        data = extract_inner_json(result)
        assert "error" in data
        assert "image_hash" in data["error"] or "video_id" in data["error"]

    @pytest.mark.asyncio
    async def test_headline_too_long(self):
        """Should return error when card headline exceeds 40 chars."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock):
            result = await create_carousel_ad_creative(
                account_id="act_123456789",
                page_id="123456789",
                child_attachments=[
                    {"link": "https://example.com/1", "image_hash": "hash1", "name": "A" * 41},
                    {"link": "https://example.com/2", "image_hash": "hash2"},
                ]
            )
        
        data = extract_inner_json(result)
        assert "error" in data
        assert "40 character" in data["error"]


class TestCreateCarouselAdCreativeSuccess:
    """Test successful carousel creation."""

    @pytest.mark.asyncio
    async def test_successful_carousel_creation(self):
        """Should successfully create carousel with valid inputs."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        mock_create_response = {"id": "120234567890"}
        mock_details_response = {
            "id": "120234567890",
            "name": "Test Carousel",
            "status": "ACTIVE",
            "object_story_spec": {
                "page_id": "123456789",
                "link_data": {
                    "child_attachments": [
                        {"link": "https://example.com/1", "image_hash": "hash1"},
                        {"link": "https://example.com/2", "image_hash": "hash2"},
                    ]
                }
            }
        }
        
        async def mock_api_request(endpoint, token, params, method="GET"):
            if method == "POST":
                return mock_create_response
            return mock_details_response
        
        with patch('meta_ads_mcp.core.ads.make_api_request', side_effect=mock_api_request):
            result = await create_carousel_ad_creative(
                account_id="act_123456789",
                page_id="123456789",
                child_attachments=[
                    {"link": "https://example.com/1", "image_hash": "hash1", "name": "Card 1"},
                    {"link": "https://example.com/2", "image_hash": "hash2", "name": "Card 2"},
                ],
                message="Check out our products!",
                call_to_action_type="SHOP_NOW"
            )
        
        data = extract_inner_json(result)
        assert data.get("success") == True
        assert data.get("creative_id") == "120234567890"
        assert data.get("format") == "carousel"
        assert data.get("cards_count") == 2

    @pytest.mark.asyncio
    async def test_carousel_with_video(self):
        """Should accept video_id instead of image_hash."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        mock_create_response = {"id": "120234567890"}
        mock_details_response = {"id": "120234567890", "name": "Video Carousel"}
        
        async def mock_api_request(endpoint, token, params, method="GET"):
            if method == "POST":
                return mock_create_response
            return mock_details_response
        
        with patch('meta_ads_mcp.core.ads.make_api_request', side_effect=mock_api_request):
            result = await create_carousel_ad_creative(
                account_id="act_123456789",
                page_id="123456789",
                child_attachments=[
                    {"link": "https://example.com/1", "video_id": "video123"},
                    {"link": "https://example.com/2", "image_hash": "hash2"},
                ]
            )
        
        data = extract_inner_json(result)
        assert data.get("success") == True

    @pytest.mark.asyncio
    async def test_account_id_prefix_normalization(self):
        """Should add act_ prefix if missing."""
        from meta_ads_mcp.core.ads import create_carousel_ad_creative
        
        captured_endpoint = None
        
        async def mock_api_request(endpoint, token, params, method="GET"):
            nonlocal captured_endpoint
            if method == "POST":
                captured_endpoint = endpoint
                return {"id": "120234567890"}
            return {"id": "120234567890"}
        
        with patch('meta_ads_mcp.core.ads.make_api_request', side_effect=mock_api_request):
            await create_carousel_ad_creative(
                account_id="123456789",  # Without act_ prefix
                page_id="123456789",
                child_attachments=[
                    {"link": "https://example.com/1", "image_hash": "hash1"},
                    {"link": "https://example.com/2", "image_hash": "hash2"},
                ]
            )
        
        assert captured_endpoint == "act_123456789/adcreatives"

