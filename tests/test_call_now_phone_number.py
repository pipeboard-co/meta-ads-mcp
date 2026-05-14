"""Test that create_ad_creative serializes phone_number into call_to_action.value.link.

Meta v24 rejects a literal "phone_number" key inside call_to_action.value with
code 100 ("Invalid keys phone_number were found in param call_to_action[value]").
The supported shape is call_to_action.value.link = "tel:<E.164 number>".
"""

import pytest
import json
from unittest.mock import patch
from meta_ads_mcp.core.ads import create_ad_creative


@pytest.mark.asyncio
async def test_simple_image_call_now_serializes_phone_number_as_tel_link():
    """Simple image creative with CALL_NOW should serialize phone_number into call_to_action.value.link as tel:<number>."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            {"id": "creative_123"},
            {"id": "creative_123", "name": "Test Creative", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_701351919139047",
            image_hash="test_hash_123",
            name="Plumbing Call Ad",
            link_url="https://facebook.com/105246524341910/",
            message="Need a plumber? Call now!",
            headline="Call Now",
            call_to_action_type="CALL_NOW",
            phone_number="+18005551234",
            access_token="test_token"
        )

        create_call_args = mock_api.call_args_list[0]
        creative_data = create_call_args[0][2]

        # Verify object_story_spec with link_data
        assert "object_story_spec" in creative_data
        link_data = creative_data["object_story_spec"]["link_data"]
        assert "call_to_action" in link_data

        cta = link_data["call_to_action"]
        assert cta["type"] == "CALL_NOW"
        assert "value" in cta
        # Meta v24: tel: link is the only supported shape.
        assert cta["value"]["link"] == "tel:+18005551234"
        # The deprecated literal "phone_number" key must NOT be sent.
        assert "phone_number" not in cta["value"]


@pytest.mark.asyncio
async def test_simple_image_without_phone_number_has_no_tel_link_in_cta():
    """Simple image creative with LEARN_MORE should NOT include a tel: link in cta.value."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            {"id": "creative_456"},
            {"id": "creative_456", "name": "Test Creative", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_701351919139047",
            image_hash="test_hash_456",
            name="Regular Ad",
            link_url="https://example.com/",
            message="Learn more about us",
            headline="Learn More",
            call_to_action_type="LEARN_MORE",
            access_token="test_token"
        )

        create_call_args = mock_api.call_args_list[0]
        creative_data = create_call_args[0][2]

        link_data = creative_data["object_story_spec"]["link_data"]
        cta = link_data["call_to_action"]
        assert cta["type"] == "LEARN_MORE"
        # No phone-related fields should be in value. The deprecated
        # "phone_number" key must never appear, and the link (if set) must
        # not be a tel: URI when no phone_number was passed.
        if "value" in cta:
            assert "phone_number" not in cta["value"]
            link_value = cta["value"].get("link")
            if link_value is not None:
                assert not link_value.startswith("tel:")


@pytest.mark.asyncio
async def test_dof_image_call_now_serializes_phone_number_as_tel_link():
    """DOF (DEGREES_OF_FREEDOM) image creative with CALL_NOW should serialize phone_number as call_to_action.value.link = tel:<number>."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            {"id": "creative_789"},
            {"id": "creative_789", "name": "DOF Creative", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_701351919139047",
            image_hashes=["hash_a"],
            name="Plumbing DOF Call Ad",
            link_url="https://facebook.com/105246524341910/",
            messages=["Need a plumber? Call now!"],
            headlines=["Call Now"],
            call_to_action_type="CALL_NOW",
            optimization_type="DEGREES_OF_FREEDOM",
            phone_number="+18005551234",
            access_token="test_token"
        )

        create_call_args = mock_api.call_args_list[0]
        creative_data = create_call_args[0][2]

        # DOF puts CTA in link_data
        assert "object_story_spec" in creative_data
        link_data = creative_data["object_story_spec"]["link_data"]
        assert "call_to_action" in link_data

        cta = link_data["call_to_action"]
        assert cta["type"] == "CALL_NOW"
        assert cta["value"]["link"] == "tel:+18005551234"
        assert "phone_number" not in cta["value"]


@pytest.mark.asyncio
async def test_simple_video_call_now_serializes_phone_number_as_tel_link():
    """Simple video creative with CALL_NOW should serialize phone_number as call_to_action.value.link = tel:<number>."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            # First call: fetch video thumbnail (picture field)
            {"picture": "https://example.com/thumb.jpg"},
            # Second call: create creative
            {"id": "creative_vid1"},
            # Third call: get creative details
            {"id": "creative_vid1", "name": "Video Call Ad", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_701351919139047",
            video_id="video_123",
            name="Plumbing Video Call Ad",
            link_url="https://facebook.com/105246524341910/",
            message="Need a plumber? Call now!",
            headline="Call Now",
            call_to_action_type="CALL_NOW",
            phone_number="+18005551234",
            access_token="test_token"
        )

        # Index 1 because index 0 is the video thumbnail fetch
        create_call_args = mock_api.call_args_list[1]
        creative_data = create_call_args[0][2]

        # Simple video uses video_data
        assert "object_story_spec" in creative_data
        video_data = creative_data["object_story_spec"]["video_data"]
        assert "call_to_action" in video_data

        cta = video_data["call_to_action"]
        assert cta["type"] == "CALL_NOW"
        assert cta["value"]["link"] == "tel:+18005551234"
        assert "phone_number" not in cta["value"]
