"""Ad and Creative-related functionality for Meta Ads API."""

import json
import logging
from typing import Optional, Dict, Any, List, Union
import io
from PIL import Image as PILImage
from mcp.server.fastmcp import Image
import os
import time

logger = logging.getLogger(__name__)

from .api import meta_api_tool, make_api_request, ensure_act_prefix
from .accounts import get_ad_accounts

# ---------------------------------------------------------------------------
# Placement asset customization helpers
# ---------------------------------------------------------------------------

# Maps our user-friendly placement group names to Meta API positions.
# customization_spec in Meta's API is the placement SELECTOR (WHERE),
# while image_label/video_label at the rule level is the asset REFERENCE (WHAT).
_PLACEMENT_GROUP_TO_POSITIONS: Dict[str, Dict[str, List[str]]] = {
    "FEED": {
        "publisher_platforms": ["facebook", "instagram"],
        "facebook_positions": ["feed"],
        "instagram_positions": ["stream", "profile_feed"],
    },
    "STORY": {
        "publisher_platforms": ["facebook", "instagram"],
        "facebook_positions": ["story"],
        "instagram_positions": ["story"],
    },
    "MESSENGER": {
        "publisher_platforms": ["messenger"],
    },
    "INSTREAM_VIDEO": {
        "publisher_platforms": ["facebook"],
        "facebook_positions": ["instream_video"],
    },
    "SEARCH": {
        "publisher_platforms": ["facebook"],
        "facebook_positions": ["search"],
    },
    "SHOP": {
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["shop"],
    },
    "AUDIENCE_NETWORK": {
        "publisher_platforms": ["audience_network"],
        "audience_network_positions": ["classic", "instream_video"],
    },
}


def _translate_asset_customization_rules(
    rules: List[Dict[str, Any]],
    images_array: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Translate user-friendly placement_groups format to Meta API format.

    Our user-facing format:
        [{"placement_groups": ["FEED"], "customization_spec": {"image_hashes": ["h1"]}},
         {"placement_groups": ["STORY"], "customization_spec": {"image_hashes": ["h2"]}}]

    Meta API format:
        [{"customization_spec": {"publisher_platforms": [...], "facebook_positions": [...]},
          "image_label": {"name": "PBOARD_IMG_0"}},
         ...]
    And images in asset_feed_spec.images get adlabels assigned.

    Rules that do NOT contain placement_groups are passed through unchanged
    (allows raw Meta API format to be used directly).
    """
    if not rules or not any("placement_groups" in r for r in rules):
        return rules, images_array

    # Build hash → label mapping across all rules
    hash_to_label: Dict[str, str] = {}
    label_counter = 0

    translated_rules = []
    for rule in rules:
        if "placement_groups" not in rule:
            translated_rules.append(rule)
            continue

        placement_groups = rule.get("placement_groups", [])
        cspec_input = rule.get("customization_spec", {})

        # Build Meta-format customization_spec from placement_groups
        publisher_platforms: set = set()
        facebook_positions: set = set()
        instagram_positions: set = set()
        audience_network_positions: set = set()

        for pg in placement_groups:
            mapping = _PLACEMENT_GROUP_TO_POSITIONS.get(pg, {})
            publisher_platforms.update(mapping.get("publisher_platforms", []))
            facebook_positions.update(mapping.get("facebook_positions", []))
            instagram_positions.update(mapping.get("instagram_positions", []))
            audience_network_positions.update(mapping.get("audience_network_positions", []))

        meta_cspec: Dict[str, Any] = {}
        if publisher_platforms:
            meta_cspec["publisher_platforms"] = sorted(publisher_platforms)
        if facebook_positions:
            meta_cspec["facebook_positions"] = sorted(facebook_positions)
        if instagram_positions:
            meta_cspec["instagram_positions"] = sorted(instagram_positions)
        if audience_network_positions:
            meta_cspec["audience_network_positions"] = sorted(audience_network_positions)

        # Carry over text overrides (bodies, titles, etc.) into customization_spec
        for text_field in ("bodies", "titles", "descriptions", "link_urls", "call_to_action_types"):
            if text_field in cspec_input:
                meta_cspec[text_field] = cspec_input[text_field]

        translated_rule: Dict[str, Any] = {"customization_spec": meta_cspec}

        # Assign label for image or video asset
        img_hashes = cspec_input.get("image_hashes", [])
        vid_ids = cspec_input.get("video_ids", [])
        if img_hashes:
            h = img_hashes[0]
            if h not in hash_to_label:
                hash_to_label[h] = f"PBOARD_IMG_{label_counter}"
                label_counter += 1
            translated_rule["image_label"] = {"name": hash_to_label[h]}
        elif vid_ids:
            v = vid_ids[0]
            if v not in hash_to_label:
                hash_to_label[v] = f"PBOARD_VID_{label_counter}"
                label_counter += 1
            translated_rule["video_label"] = {"name": hash_to_label[v]}

        translated_rules.append(translated_rule)

    # Add adlabels to images_array for referenced hashes
    updated_images = []
    for img in images_array:
        img_hash = img.get("hash", "")
        if img_hash in hash_to_label:
            updated = dict(img)
            updated["adlabels"] = [{"name": hash_to_label[img_hash]}]
            updated_images.append(updated)
        else:
            updated_images.append(img)

    return translated_rules, updated_images


# All writable creative_features_spec keys for Meta Ads API v24+.
# Mirrors ALL_ENHANCEMENT_KEYS in pipeboard.co/lib/meta-ads-enhancement-keys.ts.
# Setting each key to {"enroll_status": "OPT_OUT"} disables the enhancement.
# NOTE: The legacy "standard_enhancements" key is deprecated for POST operations
# (Meta error subcode 3858504) — individual keys must be used instead.
_ALL_ENHANCEMENT_KEYS: tuple[str, ...] = (
    "add_text_overlay",
    "creative_stickers",
    "description_automation",
    "image_animation",
    "image_background_gen",
    "image_templates",
    "image_touchups",
    "image_uncrop",
    "inline_comment",
    "media_type_automation",
    "music_generation",
    "pac_relaxation",
    "product_extensions",
    "profile_card",
    "reveal_details_over_time",
    "show_destination_blurbs",
    "show_summary",
    "site_extensions",
    "text_optimizations",
    "text_translation",
    "translate_voiceover",
    "video_auto_crop",
    "video_highlights",
)


def _translate_video_customization_rules_for_existing_post(
    rules: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Translate placement_groups-format customization rules to Meta API format,
    building a videos array for use alongside object_story_id.

    Used when object_story_id is combined with asset_customization_rules
    to override specific placements (e.g., a 9:16 video for Story/Reels
    while the organic post shows in feed).

    Our user-facing format:
        [{"placement_groups": ["STORY"], "customization_spec": {"video_ids": ["vid123"]}}]

    Meta API format in asset_feed_spec:
        videos: [{"video_id": "vid123", "adlabels": [{"name": "PBOARD_VID_0"}]}]
        asset_customization_rules: [
            {"customization_spec": {"publisher_platforms": [...], "instagram_positions": ["story"], ...},
             "video_label": {"name": "PBOARD_VID_0"}}
        ]

    Rules that do NOT contain placement_groups are passed through unchanged
    (allows raw Meta API format to be used directly).

    Returns:
        (translated_rules, videos_array) where videos_array has adlabels assigned.
    """
    if not rules or not any("placement_groups" in r for r in rules):
        # Pass through raw rules if already in Meta API format
        return rules, []

    vid_to_label: Dict[str, str] = {}
    label_counter = 0
    translated_rules = []

    for rule in rules:
        if "placement_groups" not in rule:
            translated_rules.append(rule)
            continue

        placement_groups = rule.get("placement_groups", [])
        cspec_input = rule.get("customization_spec", {})

        # Build Meta-format customization_spec from placement_groups
        publisher_platforms: set = set()
        facebook_positions: set = set()
        instagram_positions: set = set()
        audience_network_positions: set = set()

        for pg in placement_groups:
            mapping = _PLACEMENT_GROUP_TO_POSITIONS.get(pg, {})
            publisher_platforms.update(mapping.get("publisher_platforms", []))
            facebook_positions.update(mapping.get("facebook_positions", []))
            instagram_positions.update(mapping.get("instagram_positions", []))
            audience_network_positions.update(mapping.get("audience_network_positions", []))

        meta_cspec: Dict[str, Any] = {}
        if publisher_platforms:
            meta_cspec["publisher_platforms"] = sorted(publisher_platforms)
        if facebook_positions:
            meta_cspec["facebook_positions"] = sorted(facebook_positions)
        if instagram_positions:
            meta_cspec["instagram_positions"] = sorted(instagram_positions)
        if audience_network_positions:
            meta_cspec["audience_network_positions"] = sorted(audience_network_positions)

        # Carry over text overrides into customization_spec
        for text_field in ("bodies", "titles", "descriptions", "link_urls", "call_to_action_types"):
            if text_field in cspec_input:
                meta_cspec[text_field] = cspec_input[text_field]

        translated_rule: Dict[str, Any] = {"customization_spec": meta_cspec}

        # Assign label for video asset
        vid_ids = cspec_input.get("video_ids", [])
        if vid_ids:
            v = vid_ids[0]
            if v not in vid_to_label:
                vid_to_label[v] = f"PBOARD_VID_{label_counter}"
                label_counter += 1
            translated_rule["video_label"] = {"name": vid_to_label[v]}

        translated_rules.append(translated_rule)

    # Build videos_array with adlabels
    videos_array = [
        {"video_id": vid_id, "adlabels": [{"name": label}]}
        for vid_id, label in vid_to_label.items()
    ]

    return translated_rules, videos_array


from .utils import download_image, try_multiple_download_methods, ad_creative_images, extract_creative_image_urls
from .server import mcp_server


# Only register the save_ad_image_locally function if explicitly enabled via environment variable
ENABLE_SAVE_AD_IMAGE_LOCALLY = bool(os.environ.get("META_ADS_ENABLE_SAVE_AD_IMAGE_LOCALLY", ""))


@mcp_server.tool()
@meta_api_tool
async def get_ads(account_id: str, access_token: Optional[str] = None, limit: int = 10, 
                 campaign_id: str = "", adset_id: str = "") -> str:
    """
    Get ads for a Meta Ads account with optional filtering.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
        limit: Maximum number of ads to return (default: 10)
        campaign_id: Optional campaign ID to filter by
        adset_id: Optional ad set ID to filter by
    """
    # Require explicit account_id
    if not account_id:
        return json.dumps({"error": "No account ID specified"}, indent=2)
    
    # Prioritize adset_id over campaign_id - use adset-specific endpoint
    if adset_id:
        endpoint = f"{adset_id}/ads"
        params = {
            "fields": "id,name,adset_id,campaign_id,status,creative,created_time,updated_time,bid_amount,conversion_domain,tracking_specs",
            "limit": limit
        }
    # Use campaign-specific endpoint if campaign_id is provided
    elif campaign_id:
        endpoint = f"{campaign_id}/ads"
        params = {
            "fields": "id,name,adset_id,campaign_id,status,creative,created_time,updated_time,bid_amount,conversion_domain,tracking_specs",
            "limit": limit
        }
    else:
        # Default to account-level endpoint if no specific filters
        endpoint = f"{account_id}/ads"
        params = {
            "fields": "id,name,adset_id,campaign_id,status,creative,created_time,updated_time,bid_amount,conversion_domain,tracking_specs",
            "limit": limit
        }

    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_ad_details(ad_id: str, access_token: Optional[str] = None) -> str:
    """
    Get detailed information about a specific ad.
    
    Args:
        ad_id: Meta Ads ad ID
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not ad_id:
        return json.dumps({"error": "No ad ID provided"}, indent=2)
        
    endpoint = f"{ad_id}"
    params = {
        "fields": "id,name,adset_id,campaign_id,status,creative,created_time,updated_time,bid_amount,conversion_domain,tracking_specs,preview_shareable_link"
    }
    
    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_creative_details(creative_id: str, access_token: Optional[str] = None) -> str:
    """Get detailed information about a specific ad creative by its ID.

    Args:
        creative_id: Meta Ads creative ID (required)
        access_token: Meta API access token (optional)
    """
    if not creative_id:
        return json.dumps({"error": "No creative ID provided"}, indent=2)
    endpoint = f"{creative_id}"
    # Note: dynamic_creative_spec is only valid on dynamic creatives and causes
    # "(#100) Tried accessing nonexisting field" on simple creatives in API v24.
    # We fetch the safe fields first, then try dynamic_creative_spec separately.
    params = {
        "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec,object_type,body,title,effective_object_story_id,asset_feed_spec{images,videos,bodies,titles,descriptions,link_urls,ad_formats,call_to_action_types,optimization_type,asset_customization_rules},url_tags,link_url"
    }
    data = await make_api_request(endpoint, access_token, params)

    # Try to fetch optional fields separately (may not exist on all creative types)
    if isinstance(data, dict) and "id" in data:
        for opt_field in ["dynamic_creative_spec", "degrees_of_freedom_spec", "product_set_id"]:
            try:
                opt_data = await make_api_request(
                    endpoint, access_token, {"fields": opt_field}
                )
                if isinstance(opt_data, dict) and opt_field in opt_data:
                    data[opt_field] = opt_data[opt_field]
            except Exception:
                pass  # Field doesn't exist on this creative type

        # Resolve product_set_id -> catalog info for DPA/catalog creatives
        if "product_set_id" in data:
            try:
                catalog_data = await make_api_request(
                    data["product_set_id"], access_token,
                    {"fields": "product_catalog{id,name}"}
                )
                catalog = catalog_data.get("product_catalog", {})
                if catalog.get("id"):
                    data["catalog_id"] = catalog["id"]
                    if catalog.get("name"):
                        data["catalog_name"] = catalog["name"]
            except Exception:
                pass  # Non-critical

    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def create_ad(
    account_id: str,
    name: str,
    adset_id: str,
    creative_id: str,
    status: str = "PAUSED",
    bid_amount: Optional[int] = None,
    tracking_specs: Optional[List[Dict[str, Any]]] = None,
    access_token: Optional[str] = None
) -> str:
    """
    Create a new ad with an existing creative.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        name: Ad name
        adset_id: Ad set ID where this ad will be placed
        creative_id: ID of an existing creative to use
        status: Initial ad status (default: PAUSED)
        bid_amount: Optional bid amount in account currency (in cents)
        tracking_specs: Optional tracking specifications (e.g., for pixel events).
                      Example: [{"action.type":"offsite_conversion","fb_pixel":["YOUR_PIXEL_ID"]}]
        access_token: Meta API access token (optional - will use cached token if not provided)

    Note:
        Dynamic Creative creatives require the parent ad set to have `is_dynamic_creative=true`.
        Otherwise, ad creation will fail with error_subcode 1885998.
    """
    # Check required parameters
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)
    
    if not name:
        return json.dumps({"error": "No ad name provided"}, indent=2)
    
    if not adset_id:
        return json.dumps({"error": "No ad set ID provided"}, indent=2)
    
    if not creative_id:
        return json.dumps({"error": "No creative ID provided"}, indent=2)
    
    endpoint = f"{account_id}/ads"
    
    params = {
        "name": name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": status
    }
    
    # Add bid amount if provided
    if bid_amount is not None:
        params["bid_amount"] = str(bid_amount)
        
    # Add tracking specs if provided
    if tracking_specs is not None:
        params["tracking_specs"] = json.dumps(tracking_specs) # Needs to be JSON encoded string
    
    try:
        data = await make_api_request(endpoint, access_token, params, method="POST")
        return json.dumps(data, indent=2)
    except Exception as e:
        error_msg = str(e)
        return json.dumps({
            "error": "Failed to create ad",
            "details": error_msg,
            "params_sent": params
        }, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_ad_creatives(ad_id: str, access_token: Optional[str] = None) -> str:
    """
    Get creative details for a specific ad. Requires an ad_id (not account_id). Use get_ads first to find ad IDs.
    
    Args:
        ad_id: Meta Ads ad ID (required)
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not ad_id:
        return json.dumps({"error": "No ad ID provided"}, indent=2)
        
    endpoint = f"{ad_id}/adcreatives"
    params = {
        "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec,object_type,body,title,effective_object_story_id,asset_feed_spec,url_tags,image_urls_for_viewing,product_set_id,degrees_of_freedom_spec"
    }
    
    data = await make_api_request(endpoint, access_token, params)

    if 'data' in data:
        # Resolve asset_feed_spec image hashes to URLs
        image_hashes = set()
        for creative in data['data']:
            if 'asset_feed_spec' in creative and 'images' in creative['asset_feed_spec']:
                for image in creative['asset_feed_spec']['images']:
                    if 'hash' in image and 'url' not in image:
                        image_hashes.add(image['hash'])

        if image_hashes:
            # Get account_id from the ad to look up image URLs
            ad_data = await make_api_request(ad_id, access_token, {"fields": "account_id"})
            account_id = ad_data.get("account_id")
            if account_id:
                hashes_str = json.dumps(list(image_hashes))
                image_data = await make_api_request(
                    f"act_{account_id}/adimages",
                    access_token,
                    {"fields": "hash,url,width,height", "hashes": hashes_str},
                )
                hash_to_url = {}
                if 'data' in image_data:
                    for img in image_data['data']:
                        if 'hash' in img and 'url' in img:
                            hash_to_url[img['hash']] = img['url']

                if hash_to_url:
                    for creative in data['data']:
                        if 'asset_feed_spec' in creative and 'images' in creative['asset_feed_spec']:
                            for image in creative['asset_feed_spec']['images']:
                                if 'hash' in image and image['hash'] in hash_to_url:
                                    image['url'] = hash_to_url[image['hash']]

        # Add image URLs for direct viewing if available
        for creative in data['data']:
            creative['image_urls_for_viewing'] = extract_creative_image_urls(creative)

        # Resolve product_set_id -> catalog info for DPA/catalog creatives
        for creative in data['data']:
            ps_id = creative.get('product_set_id')
            if ps_id:
                try:
                    catalog_data = await make_api_request(
                        ps_id, access_token,
                        {"fields": "product_catalog{id,name}"}
                    )
                    catalog = catalog_data.get("product_catalog", {})
                    if catalog.get("id"):
                        creative["catalog_id"] = catalog["id"]
                        if catalog.get("name"):
                            creative["catalog_name"] = catalog["name"]
                except Exception:
                    pass  # Non-critical

    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_ad_image(ad_id: str, access_token: Optional[str] = None) -> Image:
    """
    Get, download, and visualize a Meta ad image in one step. Useful to see the image in the LLM.
    
    Args:
        ad_id: Meta Ads ad ID
        access_token: Meta API access token (optional - will use cached token if not provided)
    
    Returns:
        The ad image ready for direct visual analysis
    """
    if not ad_id:
        return "Error: No ad ID provided"
        
    print(f"Attempting to get and analyze creative image for ad {ad_id}")
    
    # First, get creative and account IDs
    ad_endpoint = f"{ad_id}"
    ad_params = {
        "fields": "creative{id},account_id"
    }
    
    ad_data = await make_api_request(ad_endpoint, access_token, ad_params)
    
    if "error" in ad_data:
        return f"Error: Could not get ad data - {json.dumps(ad_data)}"
    
    # Extract account_id
    account_id = ad_data.get("account_id", "")
    if not account_id:
        return "Error: No account ID found"
    
    # Extract creative ID
    if "creative" not in ad_data:
        return "Error: No creative found for this ad"
        
    creative_data = ad_data.get("creative", {})
    creative_id = creative_data.get("id")
    if not creative_id:
        return "Error: No creative ID found"
    
    # Get creative details to find image hash
    creative_endpoint = f"{creative_id}"
    creative_params = {
        "fields": "id,name,image_hash,asset_feed_spec"
    }
    
    creative_details = await make_api_request(creative_endpoint, access_token, creative_params)
    
    # Identify image hashes to use from creative
    image_hashes = []
    
    # Check for direct image_hash on creative
    if "image_hash" in creative_details:
        image_hashes.append(creative_details["image_hash"])
    
    # Check asset_feed_spec for image hashes - common in Advantage+ ads
    if "asset_feed_spec" in creative_details and "images" in creative_details["asset_feed_spec"]:
        for image in creative_details["asset_feed_spec"]["images"]:
            if "hash" in image:
                image_hashes.append(image["hash"])
    
    if not image_hashes:
        # If no hashes found, try to extract from the first creative we found in the API
        # and also check for direct URLs as fallback
        creative_json = await get_ad_creatives(access_token=access_token, ad_id=ad_id)
        creative_data = json.loads(creative_json)
        
        # Try to extract hash from data array
        if "data" in creative_data and creative_data["data"]:
            for creative in creative_data["data"]:
                # Check object_story_spec for image hash
                if "object_story_spec" in creative and "link_data" in creative["object_story_spec"]:
                    link_data = creative["object_story_spec"]["link_data"]
                    if "image_hash" in link_data:
                        image_hashes.append(link_data["image_hash"])
                # Check direct image_hash on creative
                elif "image_hash" in creative:
                    image_hashes.append(creative["image_hash"])
                # Check asset_feed_spec for image hashes
                elif "asset_feed_spec" in creative and "images" in creative["asset_feed_spec"]:
                    images = creative["asset_feed_spec"]["images"]
                    if images and len(images) > 0 and "hash" in images[0]:
                        image_hashes.append(images[0]["hash"])
        
        # If still no image hashes found, try direct URL fallback approach
        if not image_hashes:
            print("No image hashes found, trying direct URL fallback...")
            
            image_url = None
            if "data" in creative_data and creative_data["data"]:
                creative = creative_data["data"][0]
                
                # Prioritize higher quality image URLs in this order:
                # 1. image_urls_for_viewing (usually highest quality)
                # 2. image_url (direct field)
                # 3. object_story_spec.link_data.picture (usually full size)
                # 4. thumbnail_url (last resort - often profile thumbnail)
                
                if "image_urls_for_viewing" in creative and creative["image_urls_for_viewing"]:
                    image_url = creative["image_urls_for_viewing"][0]
                    print(f"Using image_urls_for_viewing: {image_url}")
                elif "image_url" in creative and creative["image_url"]:
                    image_url = creative["image_url"]
                    print(f"Using image_url: {image_url}")
                elif "object_story_spec" in creative and "link_data" in creative["object_story_spec"]:
                    link_data = creative["object_story_spec"]["link_data"]
                    if "picture" in link_data and link_data["picture"]:
                        image_url = link_data["picture"]
                        print(f"Using object_story_spec.link_data.picture: {image_url}")
                elif "thumbnail_url" in creative and creative["thumbnail_url"]:
                    image_url = creative["thumbnail_url"]
                    print(f"Using thumbnail_url (fallback): {image_url}")
            
            if not image_url:
                return "Error: No image URLs found in creative"
            
            # Download the image directly
            print(f"Downloading image from direct URL: {image_url}")
            image_bytes = await download_image(image_url)
            
            if not image_bytes:
                return "Error: Failed to download image from direct URL"
            
            try:
                # Convert bytes to PIL Image
                img = PILImage.open(io.BytesIO(image_bytes))
                
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")
                    
                # Create a byte stream of the image data
                byte_arr = io.BytesIO()
                img.save(byte_arr, format="JPEG")
                img_bytes = byte_arr.getvalue()
                
                # Return as an Image object that LLM can directly analyze
                return Image(data=img_bytes, format="jpeg")
                
            except Exception as e:
                return f"Error processing image from direct URL: {str(e)}"
    
    print(f"Found image hashes: {image_hashes}")
    
    # Now fetch image data using adimages endpoint with specific format
    image_endpoint = f"act_{account_id}/adimages"
    
    # Format the hashes parameter exactly as in our successful curl test
    hashes_str = f'["{image_hashes[0]}"]'  # Format first hash only, as JSON string array
    
    image_params = {
        "fields": "hash,url,width,height,name,status",
        "hashes": hashes_str
    }
    
    print(f"Requesting image data with params: {image_params}")
    image_data = await make_api_request(image_endpoint, access_token, image_params)
    
    if "error" in image_data:
        return f"Error: Failed to get image data - {json.dumps(image_data)}"
    
    if "data" not in image_data or not image_data["data"]:
        return "Error: No image data returned from API"
    
    # Get the first image URL
    first_image = image_data["data"][0]
    image_url = first_image.get("url")
    
    if not image_url:
        return "Error: No valid image URL found"
    
    print(f"Downloading image from URL: {image_url}")
    
    # Download the image
    image_bytes = await download_image(image_url)
    
    if not image_bytes:
        return "Error: Failed to download image"
    
    try:
        # Convert bytes to PIL Image
        img = PILImage.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
            
        # Create a byte stream of the image data
        byte_arr = io.BytesIO()
        img.save(byte_arr, format="JPEG")
        img_bytes = byte_arr.getvalue()
        
        # Return as an Image object that LLM can directly analyze
        return Image(data=img_bytes, format="jpeg")
        
    except Exception as e:
        return f"Error processing image: {str(e)}"


@mcp_server.tool()
@meta_api_tool
async def get_ad_video(ad_id: str = "", video_id: str = "", account_id: str = "", access_token: Optional[str] = None) -> str:
    """
    Get video details and source URL for a Meta ad video creative. Returns the video source URL
    (direct download link), thumbnail URL, and metadata (title, description, duration).

    Provide either ad_id (to auto-extract the video from the ad creative) or video_id directly.
    Providing account_id is strongly recommended — it enables the advideos edge which works
    with Business Manager tokens (avoids error 100/33 and error #10 on account-uploaded videos).

    Args:
        ad_id: Meta Ads ad ID (will extract video_id from the ad creative)
        video_id: Meta video ID (use this if you already have it from get_ad_creatives)
        account_id: Ad account ID (e.g. "act_123" or "123"). Enables advideos edge lookup.
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not ad_id and not video_id:
        return json.dumps({"error": "Provide either ad_id or video_id"}, indent=2)

    # If only ad_id provided, extract video_id from the creative
    if not video_id:
        creative_json = await get_ad_creatives(access_token=access_token, ad_id=ad_id)
        creative_data = json.loads(creative_json)

        if "error" in creative_data:
            return json.dumps({"error": f"Could not get creatives for ad {ad_id}", "details": creative_data}, indent=2)

        # Extract video_id from creative data
        if "data" in creative_data and creative_data["data"]:
            creative = creative_data["data"][0]

            # Check object_story_spec.video_data.video_id
            oss = creative.get("object_story_spec", {})
            if "video_data" in oss:
                video_id = str(oss["video_data"].get("video_id", ""))

            # Check asset_feed_spec.videos
            if not video_id:
                afs = creative.get("asset_feed_spec", {})
                videos = afs.get("videos", [])
                if videos:
                    video_id = str(videos[0].get("video_id", ""))

        if not video_id:
            return json.dumps({
                "error": "No video found in this ad creative",
                "hint": "This ad may be an image ad. Use get_ad_image instead."
            }, indent=2)

    video_fields = "source,title,description,length,picture,thumbnails,created_time"

    # Strategy 1: Try fetching via the ad account's advideos edge.
    # Direct GET /{video_id} fails for BM-shared tokens (error 100/33) and
    # page-owned videos (error #10). The ad account edge works for any video
    # that belongs to the account's video library.
    # Normalize: strip act_ prefix if present (we add it back below)
    if account_id and account_id.startswith("act_"):
        account_id = account_id[4:]

    if not account_id and ad_id:
        ad_data = await make_api_request(ad_id, access_token, {"fields": "account_id"})
        account_id = ad_data.get("account_id", "")

    video_data = None
    if account_id:
        advideos_data = await make_api_request(
            f"act_{account_id}/advideos",
            access_token,
            {
                "fields": video_fields,
                "filtering": json.dumps([{"field": "id", "operator": "IN", "value": [video_id]}]),
            },
        )
        if "data" in advideos_data and advideos_data["data"]:
            video_data = advideos_data["data"][0]
            logger.debug(f"Video {video_id} resolved via ad account advideos edge")

    # Strategy 2: Fall back to direct video node access.
    if not video_data:
        video_data = await make_api_request(
            video_id,
            access_token,
            {"fields": video_fields}
        )

    if "error" in video_data:
        return json.dumps({"error": f"Could not get video {video_id}", "details": video_data}, indent=2)

    result = {
        "video_id": video_id,
        "source_url": video_data.get("source"),
        "thumbnail_url": video_data.get("picture"),
        "title": video_data.get("title"),
        "description": video_data.get("description"),
        "duration_seconds": video_data.get("length"),
        "created_time": video_data.get("created_time"),
    }

    if ad_id:
        result["ad_id"] = ad_id

    if not result["source_url"]:
        result["warning"] = "No source URL returned. The video may have been deleted or you may lack permissions."

    return json.dumps(result, indent=2)


if ENABLE_SAVE_AD_IMAGE_LOCALLY:
    @mcp_server.tool()
    @meta_api_tool
    async def save_ad_image_locally(ad_id: str, access_token: Optional[str] = None, output_dir: str = "ad_images") -> str:
        """
        Get, download, and save a Meta ad image locally, returning the file path.
        
        Args:
            ad_id: Meta Ads ad ID
            access_token: Meta API access token (optional - will use cached token if not provided)
            output_dir: Directory to save the image file (default: 'ad_images')
        
        Returns:
            The file path to the saved image, or an error message string.
        """
        if not ad_id:
            return json.dumps({"error": "No ad ID provided"}, indent=2)
            
        print(f"Attempting to get and save creative image for ad {ad_id}")
        
        # First, get creative and account IDs
        ad_endpoint = f"{ad_id}"
        ad_params = {
            "fields": "creative{id},account_id"
        }
        
        ad_data = await make_api_request(ad_endpoint, access_token, ad_params)
        
        if "error" in ad_data:
            return json.dumps({"error": f"Could not get ad data - {json.dumps(ad_data)}"}, indent=2)
        
        account_id = ad_data.get("account_id")
        if not account_id:
            return json.dumps({"error": "No account ID found for ad"}, indent=2)
        
        if "creative" not in ad_data:
            return json.dumps({"error": "No creative found for this ad"}, indent=2)
            
        creative_data = ad_data.get("creative", {})
        creative_id = creative_data.get("id")
        if not creative_id:
            return json.dumps({"error": "No creative ID found"}, indent=2)
        
        # Get creative details to find image hash
        creative_endpoint = f"{creative_id}"
        creative_params = {
            "fields": "id,name,image_hash,asset_feed_spec"
        }
        creative_details = await make_api_request(creative_endpoint, access_token, creative_params)
        
        image_hashes = []
        if "image_hash" in creative_details:
            image_hashes.append(creative_details["image_hash"])
        if "asset_feed_spec" in creative_details and "images" in creative_details["asset_feed_spec"]:
            for image in creative_details["asset_feed_spec"]["images"]:
                if "hash" in image:
                    image_hashes.append(image["hash"])
        
        if not image_hashes:
            # Fallback attempt (as in get_ad_image)
            creative_json = await get_ad_creatives(ad_id=ad_id, access_token=access_token) # Ensure ad_id is passed correctly
            creative_data_list = json.loads(creative_json)
            if 'data' in creative_data_list and creative_data_list['data']:
                 first_creative = creative_data_list['data'][0]
                 if 'object_story_spec' in first_creative and 'link_data' in first_creative['object_story_spec'] and 'image_hash' in first_creative['object_story_spec']['link_data']:
                     image_hashes.append(first_creative['object_story_spec']['link_data']['image_hash'])
                 elif 'image_hash' in first_creative: # Check direct hash on creative data
                      image_hashes.append(first_creative['image_hash'])


        if not image_hashes:
            return json.dumps({"error": "No image hashes found in creative or fallback"}, indent=2)

        print(f"Found image hashes: {image_hashes}")
        
        # Fetch image data using the first hash
        image_endpoint = f"act_{account_id}/adimages"
        hashes_str = f'["{image_hashes[0]}"]'
        image_params = {
            "fields": "hash,url,width,height,name,status",
            "hashes": hashes_str
        }
        
        print(f"Requesting image data with params: {image_params}")
        image_data = await make_api_request(image_endpoint, access_token, image_params)
        
        if "error" in image_data:
            return json.dumps({"error": f"Failed to get image data - {json.dumps(image_data)}"}, indent=2)
        
        if "data" not in image_data or not image_data["data"]:
            return json.dumps({"error": "No image data returned from API"}, indent=2)
            
        first_image = image_data["data"][0]
        image_url = first_image.get("url")
        
        if not image_url:
            return json.dumps({"error": "No valid image URL found in API response"}, indent=2)
            
        print(f"Downloading image from URL: {image_url}")
        
        # Download and Save Image
        image_bytes = await download_image(image_url)
        
        if not image_bytes:
            return json.dumps({"error": "Failed to download image"}, indent=2)
            
        try:
            # Ensure output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Create a filename (e.g., using ad_id and image hash)
            file_extension = ".jpg" # Default extension, could try to infer from headers later
            filename = f"{ad_id}_{image_hashes[0]}{file_extension}"
            filepath = os.path.join(output_dir, filename)
            
            # Save the image bytes to the file
            with open(filepath, "wb") as f:
                f.write(image_bytes)
                
            print(f"Image saved successfully to: {filepath}")
            return json.dumps({"filepath": filepath}, indent=2) # Return JSON with filepath

        except Exception as e:
            return json.dumps({"error": f"Failed to save image: {str(e)}"}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def update_ad(
    ad_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    bid_amount: Optional[int] = None,
    tracking_specs: Optional[List[Dict[str, Any]]] = None,
    creative_id: Optional[Union[str, int]] = None,
    access_token: Optional[str] = None
) -> str:
    """
    Update an ad with new settings.

    Args:
        ad_id: Meta Ads ad ID
        name: New ad name
        status: Update ad status (ACTIVE, PAUSED, etc.)
        bid_amount: Bid amount in account currency (in cents for USD)
        tracking_specs: Optional tracking specifications (e.g., for pixel events).
        creative_id: ID of the creative to associate with this ad (changes the ad's image/content)
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not ad_id:
        return json.dumps({"error": "Ad ID is required"}, indent=2)

    # Coerce numeric IDs to strings (LLM clients may send integers for numeric-only IDs)
    if creative_id is not None:
        creative_id = str(creative_id)

    params = {}
    if name is not None:
        params["name"] = name
    if status:
        params["status"] = status
    if bid_amount is not None:
        # Ensure bid_amount is sent as a string if it's not null
        params["bid_amount"] = str(bid_amount)
    if tracking_specs is not None: # Add tracking_specs to params if provided
        params["tracking_specs"] = json.dumps(tracking_specs) # Needs to be JSON encoded string
    if creative_id is not None:
        # Creative parameter needs to be a JSON object containing creative_id
        params["creative"] = json.dumps({"creative_id": creative_id})

    if not params:
        return json.dumps({"error": "No update parameters provided (name, status, bid_amount, tracking_specs, or creative_id)"}, indent=2)

    endpoint = f"{ad_id}"
    try:
        data = await make_api_request(endpoint, access_token, params, method='POST')

        # Check for FLEX creative image mismatch error (3858355)
        if creative_id is not None and "error" in data:
            error_obj = data.get("error", {})
            if isinstance(error_obj, dict):
                error_details = error_obj.get("details", {})
                if isinstance(error_details, dict):
                    inner_error = error_details.get("error", {})
                    error_subcode = inner_error.get("error_subcode") if isinstance(inner_error, dict) else None
                else:
                    error_subcode = error_obj.get("error_subcode")
            else:
                error_subcode = None

            if error_subcode == 3858355:
                return json.dumps({
                    "error": "Cannot swap creative on this ad due to FLEX image mismatch",
                    "error_subcode": 3858355,
                    "explanation": (
                        "Meta requires the first image in the new creative's asset_feed_spec "
                        "to match the image in its object_story_spec. When swapping a FLEX "
                        "creative on an existing ad, this validation can fail if the new "
                        "creative has different images than the original."
                    ),
                    "workaround": (
                        "Create a new ad with the new creative instead of swapping: "
                        "(1) call create_ad with the new creative_id and the same adset_id, "
                        "(2) pause the old ad with update_ad(ad_id, status='PAUSED'). "
                        "Note: this will lose social proof (likes, comments, shares) from the original ad."
                    ),
                    "ad_id": ad_id,
                    "creative_id": creative_id
                }, indent=2)

        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to update ad: {str(e)}"}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def upload_ad_image(
    account_id: str,
    access_token: Optional[str] = None,
    file: Optional[str] = None,
    image_url: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """
    Upload an image to use in Meta Ads creatives.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
        file: Data URL or raw base64 string of the image (e.g., "data:image/png;base64,iVBORw0KG...")
        image_url: Direct URL to an image to fetch and upload
        name: Optional name for the image (default: filename)
    
    Returns:
        JSON response with image details including hash for creative creation
    """
    # Check required parameters
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)
    
    # Ensure we have image data
    if not file and not image_url:
        return json.dumps({"error": "Provide either 'file' (data URL or base64) or 'image_url'"}, indent=2)
    
    account_id = ensure_act_prefix(account_id)

    try:
        # Determine encoded_image (base64 string without data URL prefix) and a sensible name
        encoded_image: str = ""
        inferred_name: str = name or ""

        if file:
            # Support data URL (e.g., data:image/png;base64,...) and raw base64
            data_url_prefix = "data:"
            base64_marker = "base64,"
            if file.startswith(data_url_prefix) and base64_marker in file:
                header, base64_payload = file.split(base64_marker, 1)
                encoded_image = base64_payload.strip()

                # Infer file extension from MIME type if name not provided
                if not inferred_name:
                    # Example header: data:image/png;...
                    mime_type = header[len(data_url_prefix):].split(";")[0].strip()
                    extension_map = {
                        "image/png": ".png",
                        "image/jpeg": ".jpg",
                        "image/jpg": ".jpg",
                        "image/webp": ".webp",
                        "image/gif": ".gif",
                        "image/bmp": ".bmp",
                        "image/tiff": ".tiff",
                    }
                    ext = extension_map.get(mime_type, ".png")
                    inferred_name = f"upload{ext}"
            else:
                # Assume it's already raw base64
                encoded_image = file.strip()
                if not inferred_name:
                    inferred_name = "upload.png"
        else:
            # Download image from URL
            try:
                image_bytes = await try_multiple_download_methods(image_url)
            except Exception as download_error:
                return json.dumps({
                    "error": "We couldn’t download the image from the link provided.",
                    "reason": "The server returned an error while trying to fetch the image.",
                    "image_url": image_url,
                    "details": str(download_error),
                    "suggestions": [
                        "Easiest fix: upload your image at https://pipeboard.co/creatives, then copy the image hash and use it directly instead of a URL.",
                        "Make sure the link is publicly reachable (no login, VPN, or IP restrictions). Local file paths (file://...) cannot be accessed by the server.",
                        "If the image is hosted on a private app or server, move it to a public URL or a CDN and try again.",
                        "Verify the URL is correct and serves the actual image file."
                    ]
                }, indent=2)

            if not image_bytes:
                return json.dumps({
                    "error": "We couldn’t access the image at the link you provided.",
                    "reason": "The image link doesn’t appear to be publicly accessible or didn’t return any data.",
                    "image_url": image_url,
                    "suggestions": [
                        "Easiest fix: upload your image at https://pipeboard.co/creatives, then copy the image hash and use it directly instead of a URL.",
                        "Double-check that the link is public and does not require login, VPN, or IP allow-listing. Local file paths (file://...) cannot be accessed by the server.",
                        "If the image is stored in a private app (for example, a self-hosted gallery), upload it to a public URL or a CDN and try again.",
                        "Confirm the URL is correct and points directly to an image file (e.g., .jpg, .png)."
                    ]
                }, indent=2)

            import base64  # Local import
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

            # Infer name from URL if not provided
            if not inferred_name:
                try:
                    path_no_query = image_url.split("?")[0]
                    filename_from_url = os.path.basename(path_no_query)
                    inferred_name = filename_from_url if filename_from_url else "upload.jpg"
                except Exception:
                    inferred_name = "upload.jpg"

        # Final name resolution
        final_name = name or inferred_name or "upload.png"

        # Prepare the API endpoint for uploading images
        endpoint = f"{account_id}/adimages"

        # Prepare POST parameters expected by Meta API
        params = {
            "bytes": encoded_image,
            "name": final_name,
        }

        # Make API request to upload the image
        print(f"Uploading image to Facebook Ad Account {account_id}")
        data = await make_api_request(endpoint, access_token, params, method="POST")

        # Normalize/structure the response for callers (e.g., to easily grab image_hash)
        # Typical Graph API response shape:
        # { "images": { "<hash>": { "hash": "<hash>", "url": "...", "width": ..., "height": ..., "name": "...", "status": 1 } } }
        if isinstance(data, dict) and "images" in data and isinstance(data["images"], dict) and data["images"]:
            images_dict = data["images"]
            images_list = []
            for hash_key, info in images_dict.items():
                # Some responses may omit the nested hash, so ensure it's present
                normalized = {
                    "hash": (info.get("hash") or hash_key),
                    "url": info.get("url"),
                    "width": info.get("width"),
                    "height": info.get("height"),
                    "name": info.get("name"),
                }
                # Drop null/None values
                normalized = {k: v for k, v in normalized.items() if v is not None}
                images_list.append(normalized)

            # Sort deterministically by hash
            images_list.sort(key=lambda i: i.get("hash", ""))
            primary_hash = images_list[0].get("hash") if images_list else None

            result = {
                "success": True,
                "account_id": account_id,
                "name": final_name,
                "image_hash": primary_hash,
                "images_count": len(images_list),
                "images": images_list
            }
            return json.dumps(result, indent=2)

        # If the API returned an error-like structure, surface it consistently
        if isinstance(data, dict) and "error" in data:
            return json.dumps({
                "error": "Failed to upload image",
                "details": data.get("error"),
                "account_id": account_id,
                "name": final_name
            }, indent=2)

        # Fallback: return a wrapped raw response to avoid breaking callers
        return json.dumps({
            "success": True,
            "account_id": account_id,
            "name": final_name,
            "raw_response": data
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Failed to upload image",
            "details": str(e)
        }, indent=2)


# Valid image_crops keys accepted by Meta's API and their aspect ratios (width/height).
_VALID_CROP_KEYS: list[tuple[str, int, int]] = [
    ("100x100", 100, 100),   # 1:1 square — Feed, Marketplace, Search
    ("100x72",  100,  72),   # ~1.39:1 horizontal — Marketplace, some placements
    ("400x500", 400, 500),   # 4:5 portrait — Feed on mobile, Stories fallback
    ("400x150", 400, 150),   # ~2.67:1 wide banner — Audience Network
    ("600x360", 600, 360),   # ~1.67:1 horizontal — Right column, some placements
    ("90x160",   90, 160),   # 9:16 tall portrait — Stories
]
_VALID_CROP_KEY_NAMES = [k for k, _, _ in _VALID_CROP_KEYS]


def _compute_crop_box(
    src_w: int, src_h: int, kw: int, kh: int
) -> list[list[int]]:
    """
    Compute the largest centered crop box that fits within src_w×src_h
    while matching the aspect ratio kw:kh.

    Returns [[x1, y1], [x2, y2]] in pixel coordinates.
    """
    # Scale to fill the full height; check if it fits within width.
    crop_w_from_h = src_h * kw / kh
    if crop_w_from_h <= src_w:
        # Use full height; crop width centered.
        crop_w = round(crop_w_from_h)
        crop_h = src_h
    else:
        # Use full width; crop height centered.
        crop_w = src_w
        crop_h = round(src_w * kh / kw)

    x1 = (src_w - crop_w) // 2
    y1 = (src_h - crop_h) // 2
    return [[x1, y1], [x1 + crop_w, y1 + crop_h]]


@mcp_server.tool()
async def compute_image_crops(
    image_width: int,
    image_height: int,
    crop_keys: Optional[List[str]] = None,
) -> str:
    """
    Compute image_crops coordinates for a source image of the given dimensions.

    Returns the image_crops dict ready to pass directly to create_ad_creative
    or bulk_create_ad_creatives. For each crop key the result is the largest
    centered region that fits within the source image while matching the key's
    aspect ratio — equivalent to "Original" crop (no content is cut off beyond
    what the ratio requires).

    Args:
        image_width: Width of the source image in pixels (e.g. 1080).
        image_height: Height of the source image in pixels (e.g. 1080).
        crop_keys: Optional list of specific crop keys to compute. Defaults to
            all 6 keys accepted by Meta's API:
              "100x100"  — 1:1 square (Feed, Marketplace, Search)
              "100x72"   — ~1.39:1 horizontal (Marketplace, some placements)
              "400x500"  — 4:5 portrait (Feed on mobile, Stories fallback)
              "400x150"  — ~2.67:1 wide banner (Audience Network)
              "600x360"  — ~1.67:1 horizontal (Right column, some placements)
              "90x160"   — 9:16 tall portrait (Stories)

    Returns:
        JSON with the image_crops dict (ready for copy-paste into create_ad_creative),
        plus validation notes for any invalid keys requested.
    """
    if image_width <= 0 or image_height <= 0:
        return json.dumps({
            "error": "image_width and image_height must be positive integers."
        }, indent=2)

    # Resolve which keys to compute.
    if crop_keys:
        requested = crop_keys
    else:
        requested = _VALID_CROP_KEY_NAMES

    crops: dict[str, list[list[int]]] = {}
    warnings: list[str] = []

    key_map = {k: (kw, kh) for k, kw, kh in _VALID_CROP_KEYS}

    for key in requested:
        if key not in key_map:
            warnings.append(
                f"'{key}' is not a valid Meta API crop key and was skipped. "
                f"Valid keys: {', '.join(_VALID_CROP_KEY_NAMES)}."
            )
            continue
        kw, kh = key_map[key]
        crops[key] = _compute_crop_box(image_width, image_height, kw, kh)

    result: dict = {
        "image_crops": crops,
        "usage": (
            "Pass image_crops directly to create_ad_creative or as the image_crops "
            "field inside each element of bulk_create_ad_creatives."
        ),
        "source_dimensions": {"width": image_width, "height": image_height},
    }
    if warnings:
        result["warnings"] = warnings

    return json.dumps(result, indent=2)


@mcp_server.tool()
@meta_api_tool
async def create_ad_creative(
    account_id: str,
    image_hash: Optional[str] = None,
    access_token: Optional[str] = None,
    name: Optional[str] = None,
    page_id: Optional[Union[str, int]] = None,
    link_url: Optional[str] = None,
    message: Optional[str] = None,
    messages: Optional[List[str]] = None,
    headline: Optional[str] = None,
    headlines: Optional[List[str]] = None,
    description: Optional[str] = None,
    descriptions: Optional[List[str]] = None,
    image_hashes: Optional[List[str]] = None,
    video_id: Optional[Union[str, int]] = None,
    thumbnail_url: Optional[str] = None,
    optimization_type: Optional[str] = None,
    dynamic_creative_spec: Optional[Dict[str, Any]] = None,
    call_to_action_type: Optional[str] = None,
    lead_gen_form_id: Optional[Union[str, int]] = None,
    instagram_actor_id: Optional[str] = None,
    ad_formats: Optional[List[str]] = None,
    asset_customization_rules: Optional[List[Dict[str, Any]]] = None,
    creative_features_spec: Optional[Dict[str, Any]] = None,
    phone_number: Optional[str] = None,
    url_tags: Optional[str] = None,
    caption: Optional[str] = None,
    image_crops: Optional[Dict[str, Any]] = None,
    object_story_id: Optional[str] = None,
    disable_all_enhancements: Optional[bool] = None,
    event_id: Optional[Union[str, int]] = None,
    reminder_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a new ad creative using an uploaded image hash, video ID, or an existing post.

    Supports five creative modes:
    - **Existing post**: Provide object_story_id (format: {page_id}_{post_id}) to promote an existing
      organic or published post. No image_hash or video_id required. Optionally combine with
      asset_customization_rules to attach a 9:16 video for Story/Reels placements.
    - **Simple image/video**: Single image_hash or video_id with object_story_spec
    - **Multi-variant copy**: Use plural text params (messages[], headlines[], descriptions[]) to test
      multiple text variants with a single image/video. No optimization_type or is_dynamic_creative needed.
    - **Dynamic Creative**: Multiple variants with dynamic_creative_spec (requires is_dynamic_creative on ad set)
    - **FLEX/DOF (Advantage+)**: Set optimization_type="DEGREES_OF_FREEDOM" for Meta to auto-optimize
      across all asset combinations without requiring is_dynamic_creative on the ad set

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        image_hash: Hash of a single uploaded image (cannot be used with image_hashes or video_id)
        access_token: Meta API access token (optional - will use cached token if not provided)
        name: Creative name
        page_id: Facebook Page ID (string or int; coerced to string)
        link_url: Destination URL for the ad (required unless using lead_gen_form_id or reminder_data)
        message: Single ad copy/text (cannot be used with messages)
        messages: List of primary text variants for multi-variant copy testing (cannot be used with message)
        headline: Single headline for simple ads (cannot be used with headlines)
        headlines: List of headline variants for multi-variant copy testing (cannot be used with headline)
        description: Single description for simple ads (cannot be used with descriptions)
        descriptions: List of description variants for multi-variant copy testing (cannot be used with description)
        image_hashes: List of image hashes for FLEX creatives (up to 10, cannot be used with image_hash or video_id)
        video_id: Meta video ID for video creatives (cannot be used with image_hash or image_hashes).
                  Upload a video first via the Meta API, then use the returned video ID here.
        thumbnail_url: Thumbnail image URL for video creatives. Recommended when using video_id.
                      Meta will auto-generate a thumbnail if not provided.
        optimization_type: Optional. Set to "DEGREES_OF_FREEDOM" for FLEX (Advantage+) creatives that
                          allow Meta to auto-optimize across all asset combinations. Not required for
                          text-only multi-variant creatives (messages[], headlines[], descriptions[]
                          work without it). When using DEGREES_OF_FREEDOM, at least one asset field
                          (image_hashes, messages, headlines, or descriptions) must contain more than
                          one variant.
                          NOTE: If asset_customization_rules is also provided, optimization_type
                          is automatically removed because Meta ignores placement rules for DOF
                          creatives. The creative will use regular dynamic creative mode instead.
        dynamic_creative_spec: Dynamic creative optimization settings
        call_to_action_type: Call to action button type (e.g., 'LEARN_MORE', 'SIGN_UP', 'SHOP_NOW',
                            'CALL_NOW'). When using CALL_NOW, also provide phone_number.
        lead_gen_form_id: Lead generation form ID for lead generation campaigns. Required when using
                         lead generation CTAs like 'SIGN_UP', 'GET_OFFER', 'SUBSCRIBE', etc.
        instagram_actor_id: Instagram account ID for Instagram placements (must be a string
                           to avoid JavaScript integer precision loss for IDs exceeding
                           Number.MAX_SAFE_INTEGER). Sent as instagram_user_id inside
                           object_story_spec (Meta deprecated instagram_actor_id in Jan 2026).
        ad_formats: List of ad format strings for asset_feed_spec (e.g., ["AUTOMATIC_FORMAT"] for
                   Flexible ads, ["SINGLE_IMAGE"] for single image, ["SINGLE_VIDEO"] for video).
                   When optimization_type is "DEGREES_OF_FREEDOM" with image_hashes, defaults to
                   ["AUTOMATIC_FORMAT"] (Flexible format). For video creatives, defaults to
                   ["SINGLE_VIDEO"]. Otherwise defaults to ["SINGLE_IMAGE"].
        asset_customization_rules: List of placement-specific asset overrides for asset_feed_spec.
        phone_number: Phone number for CALL_NOW call-to-action ads (click-to-call).
                     Required when call_to_action_type is CALL_NOW. Use E.164 format
                     (e.g., "+18005551234"). The number is passed to Meta in
                     call_to_action.value.phone_number. Common use case: geo-routed
                     call ads with different phone numbers per ad set.
        creative_features_spec: Advantage+ Creative feature opt-ins/opt-outs. Controls individual
                   creative enhancements like image_touchups, text_optimizations, inline_comment,
                   add_text_overlay, music, 3d_animation, etc. Each feature is a dict with
                   "enroll_status" set to "OPT_IN" or "OPT_OUT".
                   Example: {"image_touchups": {"enroll_status": "OPT_IN"},
                            "inline_comment": {"enroll_status": "OPT_IN"}}
                   Sent to Meta as degrees_of_freedom_spec.creative_features_spec.
        url_tags: URL tracking parameters appended to the destination URL (e.g.,
                 "utm_source=facebook&utm_medium=cpc&utm_campaign=spring_sale").
                 Sets the url_tags field on the creative.
        caption: Display URL shown in the ad (e.g., "example.com/shoes"). Sets the
                caption field in link_data. If not provided, Meta auto-generates it
                from the destination URL. Only applies to image (link_data) creatives.
        image_crops: Crop coordinates for different aspect ratios. Applied in link_data for
                    image creatives.

                    Use the compute_image_crops tool first to get the correct coordinates
                    for your specific image dimensions — it computes centered crop boxes
                    for any source size automatically.

                    Valid crop keys (only these 6 are accepted by Meta's API):
                      "100x100"  — 1:1 square (Feed, Marketplace, Search)
                      "100x72"   — ~1.39:1 horizontal (Marketplace, some placements)
                      "400x500"  — 4:5 portrait (Feed on mobile, Stories fallback)
                      "400x150"  — ~2.67:1 wide banner (Audience Network)
                      "600x360"  — ~1.67:1 horizontal (Right column, some placements)
                      "90x160"   — 9:16 tall portrait (Stories)

                    Format: {"100x100": [[x1,y1],[x2,y2]], "400x500": [[x1,y1],[x2,y2]]}
                    Coordinates are pixel-based (top-left and bottom-right corners).
                    The bounding box aspect ratio must match the key ratio as closely as possible.
                    Image origin (0,0) is the upper-left corner.

                    Omit to let Meta auto-crop (default for horizontal is 1.91:1 recommended).
        object_story_id: ID of an existing organic or published Facebook/Instagram post to promote
                        as an ad. Format: "{page_id}_{post_id}" (e.g., "124965744226834_3888007311337206").
                        When provided, image_hash and video_id are not required. page_id is also not
                        required (it is encoded in the story ID). Combine with asset_customization_rules
                        to attach a 9:16 video for Story/Reels placements while the organic post
                        serves as the feed creative — a common "Use Existing Post" workflow.
                        Example: object_story_id="124965744226834_3888007311337206",
                                 asset_customization_rules=[{"placement_groups": ["STORY"],
                                   "customization_spec": {"video_ids": ["890310874031162"]}}]
        disable_all_enhancements: When True, opts out of all Advantage+ Creative enhancements by
                        setting every known creative_features_spec key (image_touchups,
                        text_optimizations, video_auto_crop, etc.) to OPT_OUT and also
                        disabling contextual_multi_ads. Use when you want full creative
                        control without Meta's auto-modifications.
        event_id: Facebook Event ID for EVENT_RESPONSES campaigns. Required for
                 event RSVP/ticket ads so the event card renders properly. Placed
                 inside link_data.event_id, and also inside call_to_action.value
                 when call_to_action_type is EVENT_RSVP or BUY_TICKETS. Use with
                 link_url set to the Facebook event URL
                 (https://www.facebook.com/events/EVENT_ID).
        asset_customization_rules: Lets you assign different images or videos to specific placement groups
                   (e.g., feed vs. stories). Only valid with image_hashes or plural asset params.
                   Each rule uses a user-friendly format that is automatically translated to
                   Meta's API format (adlabels + customization_spec positions):
                     - placement_groups: list of placement group names
                       Valid values: FEED, STORY, MESSENGER, INSTREAM_VIDEO, SEARCH, SHOP,
                       AUDIENCE_NETWORK
                     - customization_spec: dict specifying the asset to use for those placements
                       Supported keys: image_hashes (list), video_ids (list),
                       bodies, titles, descriptions (text overrides)
                   All image hashes referenced in rules must also be in image_hashes.
                   Example (feed gets one image, stories gets another):
                   [
                     {"placement_groups": ["FEED"],
                      "customization_spec": {"image_hashes": ["<feed_hash>"]}},
                     {"placement_groups": ["STORY"],
                      "customization_spec": {"image_hashes": ["<story_hash>"]}}
                   ]
        reminder_data: Inline reminder event data for Instagram Reminder Ads
                      (REMINDERS_SET optimization goal). Placed in
                      object_story_spec.link_data.reminder_data. Use this instead of
                      upcoming_events (which requires an existing ig_upcoming_event_id).
                      Required fields:
                        - event_name (str): Display title of the reminder event
                        - start_time (int): Event start as a Unix timestamp (seconds)
                        - end_time (int): Event end as a Unix timestamp (seconds)
                      Example:
                        {"event_name": "Summer Sale", "start_time": 1745596800, "end_time": 1745611200}
                      The ad set must use optimization_goal=REMINDERS_SET and the placement
                      must be restricted to Instagram feeds/stories. link_url is still
                      recommended (the URL users visit after the reminder fires).

    Returns:
        JSON response with created creative details
    """
    # Check required parameters
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)

    # Coerce numeric IDs to strings (LLM clients may send integers for numeric-only IDs)
    if video_id is not None:
        video_id = str(video_id)
    if instagram_actor_id is not None:
        instagram_actor_id = str(instagram_actor_id).strip('"').strip("'")
    if lead_gen_form_id is not None:
        lead_gen_form_id = str(lead_gen_form_id)
    if event_id is not None:
        event_id = str(event_id)

    # Defensive coercion: some MCP transports deliver array/dict params as JSON strings
    if isinstance(asset_customization_rules, str):
        try:
            _parsed = json.loads(asset_customization_rules)
            if isinstance(_parsed, list):
                asset_customization_rules = _parsed
        except (json.JSONDecodeError, TypeError):
            pass

    if isinstance(creative_features_spec, str):
        try:
            _parsed = json.loads(creative_features_spec)
            if isinstance(_parsed, dict):
                creative_features_spec = _parsed
        except (json.JSONDecodeError, TypeError):
            pass

    if isinstance(image_crops, str):
        try:
            _parsed = json.loads(image_crops)
            if isinstance(_parsed, dict):
                image_crops = _parsed
        except (json.JSONDecodeError, TypeError):
            pass

    if isinstance(reminder_data, str):
        try:
            _parsed = json.loads(reminder_data)
            if isinstance(_parsed, dict):
                reminder_data = _parsed
        except (json.JSONDecodeError, TypeError):
            pass

    for _param_name, _param_val in [
        ('image_hashes', image_hashes),
        ('messages', messages),
        ('headlines', headlines),
        ('descriptions', descriptions),
        ('ad_formats', ad_formats),
    ]:
        if isinstance(_param_val, str):
            try:
                _parsed = json.loads(_param_val)
                if isinstance(_parsed, list):
                    if _param_name == 'image_hashes':
                        image_hashes = _parsed
                    elif _param_name == 'messages':
                        messages = _parsed
                    elif _param_name == 'headlines':
                        headlines = _parsed
                    elif _param_name == 'descriptions':
                        descriptions = _parsed
                    elif _param_name == 'ad_formats':
                        ad_formats = _parsed
            except (json.JSONDecodeError, TypeError):
                pass

    logger.debug(
        "create_ad_creative called: image_hash=%s, image_hashes=%s(%s), video_id=%s, "
        "messages=%s, headlines=%s, descriptions=%s, optimization_type=%s",
        type(image_hash).__name__,
        type(image_hashes).__name__, image_hashes,
        video_id,
        type(messages).__name__,
        type(headlines).__name__,
        type(descriptions).__name__,
        optimization_type,
    )

    # Validate media mutual exclusivity: exactly one of image_hash, image_hashes, or video_id
    # (object_story_id is an alternative media source — it references an existing post)
    media_params = sum(1 for x in [image_hash, image_hashes, video_id] if x)
    if media_params > 1:
        return json.dumps({"error": "Only one media source allowed. Use 'image_hash' for a single image, 'image_hashes' for multiple images, or 'video_id' for video."}, indent=2)

    if media_params == 0 and not object_story_id:
        return json.dumps({"error": "No media provided. Specify 'image_hash' for a single image, 'image_hashes' for multiple images, 'video_id' for a video, or 'object_story_id' to promote an existing post (format: {page_id}_{post_id})."}, indent=2)

    # Validate image_hashes limits
    if image_hashes:
        if len(image_hashes) > 10:
            return json.dumps({"error": "Maximum 10 image hashes allowed for FLEX creatives"}, indent=2)

    # Validate thumbnail_url only with video_id
    if thumbnail_url and not video_id:
        return json.dumps({"error": "thumbnail_url can only be used with video_id"}, indent=2)

    # Validate optimization_type
    if optimization_type and optimization_type != "DEGREES_OF_FREEDOM":
        return json.dumps({"error": f"Invalid optimization_type '{optimization_type}'. Only 'DEGREES_OF_FREEDOM' is supported."}, indent=2)

    # Validate message / messages mutual exclusivity
    if message and messages:
        return json.dumps({"error": "Cannot specify both 'message' and 'messages'. Use 'message' for single text or 'messages' for multiple variants."}, indent=2)
    
    if not link_url and not lead_gen_form_id and not object_story_id and not reminder_data:
        return json.dumps({"error": "No link_url provided. A destination URL is required for ad creatives (unless using lead_gen_form_id, object_story_id, or reminder_data)."}, indent=2)

    if not name:
        name = f"Creative {int(time.time())}"

    account_id = ensure_act_prefix(account_id)

    # Enhanced page discovery: If no page ID is provided, use robust discovery methods.
    # Skip when object_story_id is provided — the page is embedded in the story ID format.
    if not page_id and not object_story_id:
        try:
            # Use the comprehensive page discovery logic from get_account_pages
            page_discovery_result = await _discover_pages_for_account(account_id, access_token)

            if page_discovery_result.get("success"):
                page_id = page_discovery_result["page_id"]
                page_name = page_discovery_result.get("page_name", "Unknown")
                print(f"Auto-discovered page ID: {page_id} ({page_name})")
            else:
                return json.dumps({
                    "error": "No page ID provided and no suitable pages found for this account",
                    "details": page_discovery_result.get("message", "Page discovery failed"),
                    "suggestions": [
                        "Use get_account_pages to see available pages",
                        "Use search_pages_by_name to find specific pages",
                        "Provide a page_id parameter manually"
                    ]
                }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": "Error during page discovery",
                "details": str(e),
                "suggestion": "Please provide a page_id parameter or use get_account_pages to find available pages"
            }, indent=2)

    # Normalize page_id to string after all assignment paths (input param + discovery).
    # Skip when object_story_id is used — page_id may be None in that path.
    if page_id is not None:
        page_id = str(page_id)

    # Validate headline/description parameters - cannot mix simple and complex
    if headline and headlines:
        return json.dumps({"error": "Cannot specify both 'headline' and 'headlines'. Use 'headline' for single headline or 'headlines' for multiple."}, indent=2)
    
    if description and descriptions:
        return json.dumps({"error": "Cannot specify both 'description' and 'descriptions'. Use 'description' for single description or 'descriptions' for multiple."}, indent=2)
    
    # Validate dynamic creative parameters (plural forms only)
    if headlines:
        if len(headlines) > 5:
            return json.dumps({"error": "Maximum 5 headlines allowed for dynamic creatives"}, indent=2)
        for i, h in enumerate(headlines):
            if len(h) > 40:
                return json.dumps({"error": f"Headline {i+1} exceeds 40 character limit"}, indent=2)

    if descriptions:
        if len(descriptions) > 5:
            return json.dumps({"error": "Maximum 5 descriptions allowed for dynamic creatives"}, indent=2)
        for i, d in enumerate(descriptions):
            if len(d) > 125:
                return json.dumps({"error": f"Description {i+1} exceeds 125 character limit"}, indent=2)

    # Prepare the API endpoint for creating a creative
    endpoint = f"{account_id}/adcreatives"

    try:
        # Prepare the creative data
        creative_data = {
            "name": name
        }

        # Auto-downgrade DOF when asset_customization_rules is provided.
        # Meta silently ignores asset_customization_rules for DEGREES_OF_FREEDOM
        # creatives (confirmed by e2e testing). Dropping optimization_type lets the
        # rules take effect under regular dynamic creative mode instead.
        dof_downgraded = False
        if optimization_type and asset_customization_rules:
            logger.info(
                "Dropping optimization_type=%s because asset_customization_rules is set "
                "(Meta ignores placement rules for DOF creatives)",
                optimization_type,
            )
            optimization_type = None
            dof_downgraded = True

        # Determine whether to use asset_feed_spec path:
        # - plural parameters (headlines/descriptions/messages/image_hashes), OR
        # - optimization_type is set (FLEX creatives always use asset_feed_spec), OR
        # - asset_customization_rules requires asset_feed_spec, OR
        # - video_id + description: Meta's video_data rejects "description" directly,
        #   so route through asset_feed_spec which supports descriptions for video ads
        use_asset_feed = bool(
            headlines or descriptions or messages or image_hashes or optimization_type
            or asset_customization_rules or (video_id and description)
        )

        # Track if this is a video creative
        is_video = bool(video_id)

        # Meta API v24 REQUIRES a thumbnail (image_hash or image_url) in video_data.
        # If the caller didn't provide one, auto-fetch from the video object.
        if is_video and not thumbnail_url:
            try:
                video_info = await make_api_request(
                    video_id, access_token, {"fields": "picture"}
                )
                if isinstance(video_info, dict) and "picture" in video_info:
                    thumbnail_url = video_info["picture"]
                    logger.info(f"Auto-fetched video thumbnail: {thumbnail_url[:80]}...")
                else:
                    logger.warning(f"Could not auto-fetch thumbnail for video {video_id}: {video_info}")
            except Exception as e:
                logger.warning(f"Failed to auto-fetch thumbnail for video {video_id}: {e}")

        if object_story_id:
            # ---------------------------------------------------------------------------
            # Existing-post (object_story_id) path: promote an organic/published post
            # ---------------------------------------------------------------------------
            creative_data["object_story_id"] = object_story_id

            if asset_customization_rules:
                # Build asset_feed_spec with placement-specific video overrides
                # (e.g., a 9:16 video for Story/Reels while the post shows in feed)
                translated_rules_osi, videos_array_osi = _translate_video_customization_rules_for_existing_post(
                    asset_customization_rules
                )
                asset_feed_spec_osi: Dict[str, Any] = {}
                if videos_array_osi:
                    asset_feed_spec_osi["videos"] = videos_array_osi
                if translated_rules_osi:
                    asset_feed_spec_osi["asset_customization_rules"] = translated_rules_osi
                if link_url:
                    asset_feed_spec_osi["link_urls"] = [{"website_url": link_url}]
                if call_to_action_type:
                    asset_feed_spec_osi["call_to_action_types"] = [call_to_action_type]
                if asset_feed_spec_osi:
                    creative_data["asset_feed_spec"] = asset_feed_spec_osi
            elif call_to_action_type:
                # No asset_feed_spec: put CTA at top level for simple existing-post creatives
                cta_osi: Dict[str, Any] = {"type": call_to_action_type}
                cta_osi_value: Dict[str, Any] = {}
                if link_url:
                    cta_osi_value["link"] = link_url
                if lead_gen_form_id:
                    cta_osi_value["lead_gen_form_id"] = lead_gen_form_id
                if phone_number:
                    cta_osi_value["phone_number"] = phone_number
                if cta_osi_value:
                    cta_osi["value"] = cta_osi_value
                creative_data["call_to_action"] = cta_osi

            if instagram_actor_id:
                creative_data["instagram_actor_id"] = instagram_actor_id

        elif use_asset_feed:
            # Build the media array from the provided source
            if is_video:
                # Video in asset_feed_spec uses "videos" key
                videos_array = [{"video_id": video_id}]
                if thumbnail_url:
                    videos_array[0]["thumbnail_url"] = thumbnail_url
            elif image_hashes:
                images_array = [{"hash": h} for h in image_hashes]
            else:
                images_array = [{"hash": image_hash}]

            # Translate placement_groups-style asset_customization_rules to Meta API format.
            # Meta API uses customization_spec for placement selection (publisher_platforms,
            # facebook_positions, instagram_positions) and image_label/video_label at the
            # rule level for asset selection. Images also need adlabels assigned.
            if asset_customization_rules and not is_video:
                asset_customization_rules, images_array = _translate_asset_customization_rules(
                    asset_customization_rules, images_array
                )

            # ------------------------------------------------------------------
            # Build asset_feed_spec base: DOF vs non-DOF use different patterns.
            #
            # DOF (DEGREES_OF_FREEDOM / FLEX / Advantage+):
            #   asset_feed_spec has ONLY: media, optimization_type, text variants.
            #   URL, ad_formats, and CTA go in object_story_spec.link_data.
            #   This matches the working Next.js duplication pattern — Meta's
            #   own GET response omits link_urls/ad_formats/call_to_action_types
            #   from asset_feed_spec, and the duplication passes it through AS-IS.
            #   Including those fields causes Meta to silently ignore
            #   asset_feed_spec for multi-image creatives.
            #
            # Non-DOF (regular Dynamic Creative):
            #   asset_feed_spec includes link_urls, ad_formats, call_to_action_types
            #   as before (this path is verified working).
            # ------------------------------------------------------------------
            if optimization_type:
                asset_feed_spec = {"optimization_type": optimization_type}
                # Only include ad_formats if explicitly provided by the caller
                if ad_formats:
                    asset_feed_spec["ad_formats"] = ad_formats
            else:
                resolved_ad_formats = ad_formats or (["SINGLE_VIDEO"] if is_video else ["SINGLE_IMAGE"])
                asset_feed_spec = {
                    "link_urls": [{"website_url": link_url}],
                    "ad_formats": resolved_ad_formats,
                }

            # Add media to asset_feed_spec (shared by both paths)
            if is_video:
                asset_feed_spec["videos"] = videos_array
            else:
                asset_feed_spec["images"] = images_array

            # Handle headlines - Meta API uses "titles" not "headlines" in asset_feed_spec
            # Auto-promote singular headline to single-element array when in asset_feed_spec path
            if headlines:
                asset_feed_spec["titles"] = [{"text": headline_text} for headline_text in headlines]
            elif headline:
                asset_feed_spec["titles"] = [{"text": headline}]

            # Handle descriptions
            # Auto-promote singular description to single-element array when in asset_feed_spec path
            if descriptions:
                asset_feed_spec["descriptions"] = [{"text": description_text} for description_text in descriptions]
            elif description:
                asset_feed_spec["descriptions"] = [{"text": description}]

            # Handle bodies: messages (plural) or message (singular)
            if messages:
                asset_feed_spec["bodies"] = [{"text": m} for m in messages]
            elif message:
                asset_feed_spec["bodies"] = [{"text": message}]

            # CTA in asset_feed_spec only for non-DOF (DOF puts CTA in link_data)
            if call_to_action_type and not optimization_type:
                asset_feed_spec["call_to_action_types"] = [call_to_action_type]

            # Add placement-specific asset customization rules if provided
            if asset_customization_rules:
                asset_feed_spec["asset_customization_rules"] = asset_customization_rules

            creative_data["asset_feed_spec"] = asset_feed_spec

            # ------------------------------------------------------------------
            # Build object_story_spec for asset_feed_spec creatives.
            # Meta rejects bare page_id (error 2061015) — needs a link anchor.
            # ------------------------------------------------------------------
            if is_video:
                # Video FLEX: use video_data with call_to_action carrying
                # the link URL. This is required for Meta to associate the
                # video and destination URL with the creative.
                video_anchor = {"video_id": video_id}
                if thumbnail_url:
                    video_anchor["image_url"] = thumbnail_url
                cta_type = call_to_action_type or "LEARN_MORE"
                cta_value = {}
                if link_url:
                    cta_value["link"] = link_url
                if lead_gen_form_id:
                    cta_value["lead_gen_form_id"] = lead_gen_form_id
                if phone_number:
                    cta_value["phone_number"] = phone_number
                cta_data = {"type": cta_type}
                if cta_value:
                    cta_data["value"] = cta_value
                video_anchor["call_to_action"] = cta_data
                creative_data["object_story_spec"] = {
                    "page_id": page_id,
                    "video_data": video_anchor
                }
            else:
                if not optimization_type:
                    # Non-DOF asset_feed_spec: Meta requires bare
                    # object_story_spec (no link_data).  URLs, images, CTA
                    # live exclusively in asset_feed_spec.
                    # Ref: developers.facebook.com/docs/marketing-api/asset-customization-rules
                    creative_data["object_story_spec"] = {
                        "page_id": page_id,
                    }
                else:
                    # DOF: link_data serves as the "anchor" creative template.
                    link_data = {}
                    if link_url:
                        link_data["link"] = link_url
                    if image_hashes:
                        link_data["image_hash"] = image_hashes[0]
                    elif image_hash:
                        link_data["image_hash"] = image_hash
                    if caption:
                        link_data["caption"] = caption
                    if image_crops:
                        link_data["image_crops"] = image_crops
                    if event_id:
                        link_data["event_id"] = event_id
                    if reminder_data:
                        link_data["reminder_data"] = reminder_data
                    if call_to_action_type:
                        cta = {"type": call_to_action_type}
                        cta_value = {}
                        if link_url:
                            cta_value["link"] = link_url
                        if lead_gen_form_id:
                            cta_value["lead_gen_form_id"] = lead_gen_form_id
                        if phone_number:
                            cta_value["phone_number"] = phone_number
                        if event_id and call_to_action_type in ("EVENT_RSVP", "BUY_TICKETS"):
                            cta_value["event_id"] = event_id
                        if cta_value:
                            cta["value"] = cta_value
                        link_data["call_to_action"] = cta
                    creative_data["object_story_spec"] = {
                        "page_id": page_id,
                        "link_data": link_data,
                    }
        else:
            if is_video:
                # Use object_story_spec with video_data for simple video creatives.
                # NOTE: video_data does NOT support a "link" field directly.
                # The destination URL goes in call_to_action.value.link.
                # Thumbnail auto-fetch is handled earlier (before use_asset_feed branch).
                video_data = {
                    "video_id": video_id,
                }

                if thumbnail_url:
                    video_data["image_url"] = thumbnail_url

                if message:
                    video_data["message"] = message

                if headline:
                    video_data["title"] = headline

                # NOTE: Meta API v24 rejects "description" in video_data AND
                # "link_description" in call_to_action.value (deprecated).
                # Description is not settable for simple video creatives.

                # Build call_to_action with the destination URL.
                # For video creatives, link_url MUST go in call_to_action.value.link
                # (not as a top-level field in video_data).
                cta_value = {}
                if link_url:
                    cta_value["link"] = link_url
                if lead_gen_form_id:
                    cta_value["lead_gen_form_id"] = lead_gen_form_id
                if phone_number:
                    cta_value["phone_number"] = phone_number
                cta_type = call_to_action_type or ("LEARN_MORE" if link_url else None)
                if cta_type:
                    cta_data = {"type": cta_type}
                    if cta_value:
                        cta_data["value"] = cta_value
                    video_data["call_to_action"] = cta_data

                creative_data["object_story_spec"] = {
                    "page_id": page_id,
                    "video_data": video_data
                }
            else:
                # Use traditional object_story_spec with link_data for simple image creatives
                link_data: Dict[str, Any] = {
                    "image_hash": image_hash,
                }
                if link_url:
                    link_data["link"] = link_url

                creative_data["object_story_spec"] = {
                    "page_id": page_id,
                    "link_data": link_data,
                }

                # Add optional parameters if provided
                if message:
                    creative_data["object_story_spec"]["link_data"]["message"] = message

                # Add headline (singular) to link_data
                if headline:
                    creative_data["object_story_spec"]["link_data"]["name"] = headline

                # Add description (singular) to link_data
                if description:
                    creative_data["object_story_spec"]["link_data"]["description"] = description

                # Add caption (display URL) to link_data
                if caption:
                    creative_data["object_story_spec"]["link_data"]["caption"] = caption

                # Add image crops to link_data for placement-specific cropping
                if image_crops:
                    creative_data["object_story_spec"]["link_data"]["image_crops"] = image_crops

                # Add event_id to link_data for EVENT_RESPONSES campaigns
                if event_id:
                    creative_data["object_story_spec"]["link_data"]["event_id"] = event_id

                # Add reminder_data to link_data for Instagram Reminder Ads (REMINDERS_SET goal).
                # The event details (name, start/end timestamps) are set inline rather than
                # linking to an existing FB event via upcoming_events/ig_upcoming_event_id.
                if reminder_data:
                    creative_data["object_story_spec"]["link_data"]["reminder_data"] = reminder_data

                # Add call_to_action to link_data for simple creatives
                if call_to_action_type:
                    cta_data = {"type": call_to_action_type}
                    cta_value = {}

                    # Add lead form ID to value object if provided (required for lead generation campaigns)
                    if lead_gen_form_id:
                        cta_value["lead_gen_form_id"] = lead_gen_form_id
                    if phone_number:
                        cta_value["phone_number"] = phone_number
                    if event_id and call_to_action_type in ("EVENT_RSVP", "BUY_TICKETS"):
                        cta_value["event_id"] = event_id
                    if cta_value:
                        cta_data["value"] = cta_value

                    creative_data["object_story_spec"]["link_data"]["call_to_action"] = cta_data

        # Add dynamic creative spec if provided
        if dynamic_creative_spec:
            creative_data["dynamic_creative_spec"] = dynamic_creative_spec

        # Add Advantage+ Creative feature opt-ins if provided.
        # Only sent when the user explicitly passes creative_features_spec.
        if creative_features_spec:
            creative_data["degrees_of_freedom_spec"] = {
                "creative_features_spec": creative_features_spec
            }

        # Opt out of all Advantage+ Creative enhancements when requested.
        # Sets every known individual creative_features_spec key to OPT_OUT and
        # disables contextual_multi_ads.  The legacy "standard_enhancements" key
        # is deprecated for POST operations (Meta error subcode 3858504), so we
        # enumerate each key explicitly — matching the TS expandDisableAllEnhancements().
        if disable_all_enhancements:
            dof = creative_data.setdefault("degrees_of_freedom_spec", {})
            cfs = dof.setdefault("creative_features_spec", {})
            for key in _ALL_ENHANCEMENT_KEYS:
                if key not in cfs:
                    cfs[key] = {"enroll_status": "OPT_OUT"}
            if "contextual_multi_ads" not in creative_data:
                creative_data["contextual_multi_ads"] = {"enroll_status": "OPT_OUT"}

        # Add URL tracking parameters if provided.
        if url_tags:
            creative_data["url_tags"] = url_tags

        # instagram_actor_id → instagram_user_id migration (Jan 2026).
        # Meta deprecated instagram_actor_id; the replacement is instagram_user_id
        # inside object_story_spec (sibling of page_id and video_data/link_data).
        if instagram_actor_id and "object_story_spec" in creative_data:
            creative_data["object_story_spec"]["instagram_user_id"] = instagram_actor_id

        # Make API request to create the creative
        data = await make_api_request(endpoint, access_token, creative_data, method="POST")

        # Check for instagram_actor_id / instagram_user_id permission errors.
        # This happens when the user's Meta access token lacks the instagram_basic
        # permission. Re-connecting the Facebook account refreshes the token.
        if instagram_actor_id and "error" in data:
            err_details = data.get("error", {}).get("details", {})
            inner_msg = ""
            if isinstance(err_details, dict):
                inner_err = err_details.get("error", {})
                if isinstance(inner_err, dict):
                    inner_msg = inner_err.get("message", "")
            if "valid Instagram account id" in inner_msg or "instagram_actor_id" in inner_msg.lower():
                return json.dumps({
                    "error": "Instagram account not authorized for advertising",
                    "explanation": (
                        "The Meta API rejected the Instagram account ID. This usually means "
                        "your Facebook access token is missing the 'instagram_basic' permission, "
                        "which is required to use Instagram placements in ad creatives."
                    ),
                    "fix": (
                        "Reconnect your Facebook account at https://pipeboard.co/connections "
                        "to refresh your access token with the required permissions."
                    ),
                    "instagram_actor_id": instagram_actor_id,
                    "meta_error": inner_msg
                }, indent=2)

        # If successful, get more details about the created creative
        if "id" in data:
            creative_id = data["id"]
            creative_endpoint = f"{creative_id}"
            creative_params = {
                "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec,object_type,body,title,effective_object_story_id,asset_feed_spec{images,videos,bodies,titles,descriptions,link_urls,ad_formats,call_to_action_types,optimization_type,asset_customization_rules},url_tags,link_url"
            }

            creative_details = await make_api_request(creative_endpoint, access_token, creative_params)
            result = {
                "success": True,
                "creative_id": creative_id,
                "details": creative_details,
            }
            if dof_downgraded:
                result["warning"] = (
                    "optimization_type DEGREES_OF_FREEDOM was automatically removed because "
                    "asset_customization_rules was provided. Meta silently ignores placement "
                    "rules for DOF creatives. The creative was created using regular dynamic "
                    "creative mode so placement-specific images are respected. To use DOF "
                    "instead, remove asset_customization_rules."
                )
            return json.dumps(result, indent=2)

        return json.dumps(data, indent=2)

    except Exception as e:
        logger.exception("create_ad_creative failed")
        return json.dumps({
            "error": "Failed to create ad creative",
            "details": str(e)
        }, indent=2)


@mcp_server.tool()
@meta_api_tool
async def update_ad_creative(
    creative_id: str,
    access_token: Optional[str] = None,
    name: Optional[str] = None,
    message: Optional[str] = None,
    messages: Optional[List[str]] = None,
    headline: Optional[str] = None,
    headlines: Optional[List[str]] = None,
    description: Optional[str] = None,
    descriptions: Optional[List[str]] = None,
    optimization_type: Optional[str] = None,
    dynamic_creative_spec: Optional[Dict[str, Any]] = None,
    call_to_action_type: Optional[str] = None,
    lead_gen_form_id: Optional[Union[str, int]] = None,
    ad_formats: Optional[List[str]] = None,
    creative_features_spec: Optional[Dict[str, Any]] = None
) -> str:
    """
    Update an existing ad creative's name or optimization settings.

    IMPORTANT — Meta API limitation: The Meta API does NOT allow updating content
    fields (message, headline, description, CTA, image, video, URL) on existing
    creatives. Only the creative `name` and optimization settings (asset_feed_spec)
    can be changed. To change ad content, create a new creative with the desired
    content and update the ad to reference the new creative via `update_ad`.

    Args:
        creative_id: Meta Ads creative ID to update
        access_token: Meta API access token (optional - will use cached token if not provided)
        name: New creative name (this is the most reliable update)
        message: New ad copy/text — NOTE: Meta API may reject this on existing creatives
        messages: List of primary text variants — NOTE: Meta API may reject this on existing creatives
        headline: Single headline — NOTE: Meta API may reject this on existing creatives
        headlines: New list of headlines — NOTE: Meta API may reject this on existing creatives
        description: Single description — NOTE: Meta API may reject this on existing creatives
        descriptions: New list of descriptions — NOTE: Meta API may reject this on existing creatives
        optimization_type: Set to "DEGREES_OF_FREEDOM" for FLEX (Advantage+) creatives
        dynamic_creative_spec: New dynamic creative optimization settings
        call_to_action_type: New call to action button type — NOTE: Meta API may reject this on existing creatives
        lead_gen_form_id: Lead generation form ID for lead generation campaigns
        ad_formats: List of ad format strings for asset_feed_spec (e.g., ["AUTOMATIC_FORMAT"] for
                   Flexible ads, ["SINGLE_IMAGE"] for single image)
        creative_features_spec: Dict of Advantage+ Creative feature opt-ins/opt-outs.
                   Each key is a feature name, value is {"enroll_status": "OPT_IN"|"OPT_OUT"}.
                   Sent as a top-level field (not inside degrees_of_freedom_spec).

    Returns:
        JSON response with updated creative details
    """
    # Coerce numeric IDs to strings (LLM clients may send integers for numeric-only IDs)
    if lead_gen_form_id is not None:
        lead_gen_form_id = str(lead_gen_form_id)
    # Check required parameters
    if not creative_id:
        return json.dumps({"error": "No creative ID provided"}, indent=2)

    # Validate headline/description parameters - cannot mix simple and complex
    if headline and headlines:
        return json.dumps({"error": "Cannot specify both 'headline' and 'headlines'. Use 'headline' for single headline or 'headlines' for multiple."}, indent=2)

    if description and descriptions:
        return json.dumps({"error": "Cannot specify both 'description' and 'descriptions'. Use 'description' for single description or 'descriptions' for multiple."}, indent=2)

    # Validate message / messages mutual exclusivity
    if message and messages:
        return json.dumps({"error": "Cannot specify both 'message' and 'messages'. Use 'message' for single text or 'messages' for multiple variants."}, indent=2)

    # Validate optimization_type
    if optimization_type and optimization_type != "DEGREES_OF_FREEDOM":
        return json.dumps({"error": f"Invalid optimization_type '{optimization_type}'. Only 'DEGREES_OF_FREEDOM' is supported."}, indent=2)

    # Validate dynamic creative parameters (plural forms only)
    if headlines:
        if len(headlines) > 5:
            return json.dumps({"error": "Maximum 5 headlines allowed for dynamic creatives"}, indent=2)
        for i, h in enumerate(headlines):
            if len(h) > 40:
                return json.dumps({"error": f"Headline {i+1} exceeds 40 character limit"}, indent=2)

    if descriptions:
        if len(descriptions) > 5:
            return json.dumps({"error": "Maximum 5 descriptions allowed for dynamic creatives"}, indent=2)
        for i, d in enumerate(descriptions):
            if len(d) > 125:
                return json.dumps({"error": f"Description {i+1} exceeds 125 character limit"}, indent=2)

    # Prepare the update data
    update_data = {}

    if name:
        update_data["name"] = name

    # Choose between asset_feed_spec (dynamic/FLEX creative) or object_story_spec (traditional)
    use_asset_feed = bool(headlines or descriptions or messages or optimization_type or dynamic_creative_spec)

    if use_asset_feed:
        # Handle dynamic/FLEX creative assets via asset_feed_spec
        asset_feed_spec = {}

        # Determine ad_formats: use explicit value if provided, otherwise smart default.
        # NOTE: AUTOMATIC_FORMAT is NOT valid for creation/update — Meta silently
        # ignores the entire asset_feed_spec when it encounters it.
        # Always use SINGLE_IMAGE; Meta handles format selection automatically
        # via optimization_type=DEGREES_OF_FREEDOM.
        if ad_formats:
            asset_feed_spec["ad_formats"] = ad_formats
        else:
            asset_feed_spec["ad_formats"] = ["SINGLE_IMAGE"]

        # Add optimization_type for FLEX (Advantage+) creatives
        if optimization_type:
            asset_feed_spec["optimization_type"] = optimization_type

        # Handle headlines - Meta API uses "titles" not "headlines" in asset_feed_spec
        # Auto-promote singular headline to single-element array when in asset_feed_spec path
        if headlines:
            asset_feed_spec["titles"] = [{"text": headline_text} for headline_text in headlines]
        elif headline:
            asset_feed_spec["titles"] = [{"text": headline}]

        # Handle descriptions
        # Auto-promote singular description to single-element array when in asset_feed_spec path
        if descriptions:
            asset_feed_spec["descriptions"] = [{"text": description_text} for description_text in descriptions]
        elif description:
            asset_feed_spec["descriptions"] = [{"text": description}]

        # Handle bodies: messages (plural) or message (singular)
        if messages:
            asset_feed_spec["bodies"] = [{"text": m} for m in messages]
        elif message:
            asset_feed_spec["bodies"] = [{"text": message}]

        # Add call_to_action_types if provided
        if call_to_action_type:
            asset_feed_spec["call_to_action_types"] = [call_to_action_type]

        update_data["asset_feed_spec"] = asset_feed_spec
    else:
        # Use traditional object_story_spec with link_data for simple creatives
        if message or headline or description or call_to_action_type or lead_gen_form_id:
            update_data["object_story_spec"] = {"link_data": {}}
            
            if message:
                update_data["object_story_spec"]["link_data"]["message"] = message
            
            # Add headline (singular) to link_data
            if headline:
                update_data["object_story_spec"]["link_data"]["name"] = headline
            
            # Add description (singular) to link_data
            if description:
                update_data["object_story_spec"]["link_data"]["description"] = description
            
            # Add call_to_action to link_data for simple creatives
            if call_to_action_type or lead_gen_form_id:
                cta_data = {}
                if call_to_action_type:
                    cta_data["type"] = call_to_action_type
                
                # Add lead form ID to value object if provided (required for lead generation campaigns)
                if lead_gen_form_id:
                    cta_data["value"] = {"lead_gen_form_id": lead_gen_form_id}
                
                if cta_data:
                    update_data["object_story_spec"]["link_data"]["call_to_action"] = cta_data
    
    # Add dynamic creative spec if provided
    if dynamic_creative_spec:
        update_data["dynamic_creative_spec"] = dynamic_creative_spec

    # Add Advantage+ Creative feature opt-ins/opt-outs if provided.
    # Meta API docs: PUT /{ad_creative_id} accepts creative_features_spec
    # as a top-level field (NOT inside degrees_of_freedom_spec, which is immutable).
    if creative_features_spec:
        update_data["creative_features_spec"] = creative_features_spec

    # Prepare the API endpoint for updating the creative
    endpoint = f"{creative_id}"

    try:
        # Meta Graph API uses POST for all mutations (PUT returns "Object Not Found").
        # creative_features_spec is sent as a top-level POST field, NOT inside
        # degrees_of_freedom_spec (which is immutable after creation).
        data = await make_api_request(endpoint, access_token, update_data, method="POST")

        # If successful, get more details about the updated creative
        if "id" in data:
            creative_endpoint = f"{creative_id}"
            creative_params = {
                "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec,url_tags,link_url,dynamic_creative_spec,degrees_of_freedom_spec"
            }

            creative_details = await make_api_request(creative_endpoint, access_token, creative_params)
            return json.dumps({
                "success": True,
                "creative_id": creative_id,
                "details": creative_details
            }, indent=2)

        # Check for Meta API content update limitation (error_subcode 1815573)
        error_obj = data.get("error", {})
        if isinstance(error_obj, dict):
            error_details = error_obj.get("details", {})
            if isinstance(error_details, dict):
                inner_error = error_details.get("error", {})
                error_subcode = inner_error.get("error_subcode") if isinstance(inner_error, dict) else None
            else:
                error_subcode = error_obj.get("error_subcode")
        else:
            error_subcode = None

        if error_subcode == 1815573:
            return json.dumps({
                "error": "Content updates are not allowed on existing creatives",
                "explanation": (
                    "The Meta API does not allow updating content fields (message, headline, "
                    "description, CTA, image, video, URL) on existing creatives. "
                    "Only the creative 'name' can be changed."
                ),
                "workaround": (
                    "To change ad content: (1) create a new creative with the desired content "
                    "using create_ad_creative, then (2) call update_ad with the ad's ID and the "
                    "new creative_id to swap it on the ad."
                ),
                "creative_id": creative_id,
                "attempted_updates": update_data
            }, indent=2)

        return json.dumps(data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Failed to update ad creative",
            "details": str(e),
            "update_data_sent": update_data
        }, indent=2)


async def _discover_pages_for_account(account_id: str, access_token: str) -> dict:
    """
    Internal function to discover pages for an account using multiple approaches.
    Returns the best available page ID for ad creation.
    """
    try:
        # Approach 1: Extract page IDs from tracking_specs in ads (most reliable)
        endpoint = f"{account_id}/ads"
        params = {
            "fields": "id,name,adset_id,campaign_id,status,creative,created_time,updated_time,bid_amount,conversion_domain,tracking_specs",
            "limit": 100
        }
        
        tracking_ads_data = await make_api_request(endpoint, access_token, params)
        
        tracking_page_ids = set()
        if "data" in tracking_ads_data:
            for ad in tracking_ads_data.get("data", []):
                tracking_specs = ad.get("tracking_specs", [])
                if isinstance(tracking_specs, list):
                    for spec in tracking_specs:
                        if isinstance(spec, dict) and "page" in spec:
                            page_list = spec["page"]
                            if isinstance(page_list, list):
                                for page_id in page_list:
                                    if isinstance(page_id, (str, int)) and str(page_id).isdigit():
                                        tracking_page_ids.add(str(page_id))
        
        if tracking_page_ids:
            # Get details for the first page found
            page_id = list(tracking_page_ids)[0]
            page_endpoint = f"{page_id}"
            page_params = {
                "fields": "id,name,username,category,fan_count,link,verification_status,picture"
            }
            
            page_data = await make_api_request(page_endpoint, access_token, page_params)
            if "id" in page_data:
                return {
                    "success": True,
                    "page_id": page_id,
                    "page_name": page_data.get("name", "Unknown"),
                    "source": "tracking_specs",
                    "note": "Page ID extracted from existing ads - most reliable for ad creation"
                }
        
        # Approach 2: Try client_pages endpoint
        endpoint = f"{account_id}/client_pages"
        params = {
            "fields": "id,name,username,category,fan_count,link,verification_status,picture"
        }
        
        client_pages_data = await make_api_request(endpoint, access_token, params)
        
        if "data" in client_pages_data and client_pages_data["data"]:
            page = client_pages_data["data"][0]
            return {
                "success": True,
                "page_id": str(page["id"]),
                "page_name": page.get("name", "Unknown"),
                "source": "client_pages"
            }
        
        # Approach 3: Try assigned_pages endpoint
        pages_endpoint = f"{account_id}/assigned_pages"
        pages_params = {
            "fields": "id,name",
            "limit": 1 
        }
        
        pages_data = await make_api_request(pages_endpoint, access_token, pages_params)
        
        if "data" in pages_data and pages_data["data"]:
            page = pages_data["data"][0]
            return {
                "success": True,
                "page_id": str(page["id"]),
                "page_name": page.get("name", "Unknown"),
                "source": "assigned_pages"
            }
        
        # If all approaches failed
        return {
            "success": False,
            "message": "No suitable pages found for this account",
            "note": "Try using get_account_pages to see all available pages or provide page_id manually"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error during page discovery: {str(e)}"
        }


async def _search_pages_by_name_core(access_token: str, account_id: str, search_term: str = None) -> str:
    """
    Core logic for searching pages by name.
    
    Args:
        access_token: Meta API access token
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        search_term: Search term to find pages by name (optional - returns all pages if not provided)
    
    Returns:
        JSON string with search results
    """
    account_id = ensure_act_prefix(account_id)

    try:
        # Use the internal discovery function directly
        page_discovery_result = await _discover_pages_for_account(account_id, access_token)
        
        if not page_discovery_result.get("success"):
            return json.dumps({
                "data": [],
                "message": "No pages found for this account",
                "details": page_discovery_result.get("message", "Page discovery failed")
            }, indent=2)
        
        # Create a single page result
        page_data = {
            "id": page_discovery_result["page_id"],
            "name": page_discovery_result.get("page_name", "Unknown"),
            "source": page_discovery_result.get("source", "unknown")
        }
        
        all_pages_data = {"data": [page_data]}
        
        # Filter pages by search term if provided
        if search_term:
            search_term_lower = search_term.lower()
            filtered_pages = []
            
            for page in all_pages_data["data"]:
                page_name = page.get("name", "").lower()
                if search_term_lower in page_name:
                    filtered_pages.append(page)
            
            return json.dumps({
                "data": filtered_pages,
                "search_term": search_term,
                "total_found": len(filtered_pages),
                "total_available": len(all_pages_data["data"])
            }, indent=2)
        else:
            # Return all pages if no search term provided
            return json.dumps({
                "data": all_pages_data["data"],
                "total_available": len(all_pages_data["data"]),
                "note": "Use search_term parameter to filter pages by name"
            }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "error": "Failed to search pages by name",
            "details": str(e)
        }, indent=2)


@mcp_server.tool()
@meta_api_tool
async def search_pages_by_name(account_id: str, access_token: Optional[str] = None, search_term: Optional[str] = None) -> str:
    """
    Search for pages by name within an account.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
        search_term: Search term to find pages by name (optional - returns all pages if not provided)
    
    Returns:
        JSON response with matching pages
    """
    # Check required parameters
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)
    
    # Call the core function
    result = await _search_pages_by_name_core(access_token, account_id, search_term)
    return result


@mcp_server.tool()
@meta_api_tool
async def get_account_pages(account_id: str, access_token: Optional[str] = None) -> str:
    """
    Get pages associated with a Meta Ads account.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
    
    Returns:
        JSON response with pages associated with the account
    """
    # Check required parameters
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)
    
    # Handle special case for 'me'
    if account_id == "me":
        try:
            endpoint = "me/accounts"
            params = {
                "fields": "id,name,username,category,fan_count,link,verification_status,picture"
            }
            
            user_pages_data = await make_api_request(endpoint, access_token, params)
            return json.dumps(user_pages_data, indent=2)
        except Exception as e:
            return json.dumps({
                "error": "Failed to get user pages",
                "details": str(e)
            }, indent=2)
    
    account_id = ensure_act_prefix(account_id)
    
    try:
        # Collect all page IDs from multiple approaches
        all_page_ids = set()
        
        # Approach 1: Get user's personal pages (broad scope)
        try:
            endpoint = "me/accounts"
            params = {
                "fields": "id,name,username,category,fan_count,link,verification_status,picture"
            }
            user_pages_data = await make_api_request(endpoint, access_token, params)
            if "data" in user_pages_data:
                for page in user_pages_data["data"]:
                    if "id" in page:
                        all_page_ids.add(page["id"])
        except Exception:
            pass
        
        # Approach 2: Try business manager pages
        try:
            # Strip 'act_' prefix to get raw account ID for business endpoints
            raw_account_id = account_id.replace("act_", "")
            endpoint = f"{raw_account_id}/owned_pages"
            params = {
                "fields": "id,name,username,category,fan_count,link,verification_status,picture"
            }
            business_pages_data = await make_api_request(endpoint, access_token, params)
            if "data" in business_pages_data:
                for page in business_pages_data["data"]:
                    if "id" in page:
                        all_page_ids.add(page["id"])
        except Exception:
            pass
        
        # Approach 3: Try ad account client pages
        try:
            endpoint = f"{account_id}/client_pages"
            params = {
                "fields": "id,name,username,category,fan_count,link,verification_status,picture"
            }
            client_pages_data = await make_api_request(endpoint, access_token, params)
            if "data" in client_pages_data:
                for page in client_pages_data["data"]:
                    if "id" in page:
                        all_page_ids.add(page["id"])
        except Exception:
            pass
        
        # Approach 4: Extract page IDs from all ad creatives (broader creative search)
        try:
            endpoint = f"{account_id}/adcreatives"
            params = {
                "fields": "id,name,object_story_spec,link_url,call_to_action,image_hash",
                "limit": 100
            }
            creatives_data = await make_api_request(endpoint, access_token, params)
            if "data" in creatives_data:
                for creative in creatives_data["data"]:
                    if "object_story_spec" in creative and "page_id" in creative["object_story_spec"]:
                        all_page_ids.add(creative["object_story_spec"]["page_id"])
        except Exception:
            pass
            
        # Approach 5: Get active ads and extract page IDs from creatives
        try:
            endpoint = f"{account_id}/ads"
            params = {
                "fields": "creative{object_story_spec{page_id},link_url,call_to_action}",
                "limit": 100
            }
            ads_data = await make_api_request(endpoint, access_token, params)
            if "data" in ads_data:
                for ad in ads_data.get("data", []):
                    if "creative" in ad and "object_story_spec" in ad["creative"] and "page_id" in ad["creative"]["object_story_spec"]:
                        all_page_ids.add(ad["creative"]["object_story_spec"]["page_id"])
        except Exception:
            pass

        # Approach 6: Try promoted_objects endpoint
        try:
            endpoint = f"{account_id}/promoted_objects"
            params = {
                "fields": "page_id,object_store_url,product_set_id,application_id"
            }
            promoted_objects_data = await make_api_request(endpoint, access_token, params)
            if "data" in promoted_objects_data:
                for obj in promoted_objects_data["data"]:
                    if "page_id" in obj:
                        all_page_ids.add(obj["page_id"])
        except Exception:
            pass

        # Approach 7: Extract page IDs from tracking_specs in ads (most reliable)
        try:
            endpoint = f"{account_id}/ads"
            params = {
                "fields": "id,name,status,creative,tracking_specs",
                "limit": 100
            }
            tracking_ads_data = await make_api_request(endpoint, access_token, params)
            if "data" in tracking_ads_data:
                for ad in tracking_ads_data.get("data", []):
                    tracking_specs = ad.get("tracking_specs", [])
                    if isinstance(tracking_specs, list):
                        for spec in tracking_specs:
                            if isinstance(spec, dict) and "page" in spec:
                                page_list = spec["page"]
                                if isinstance(page_list, list):
                                    for page_id in page_list:
                                        if isinstance(page_id, (str, int)) and str(page_id).isdigit():
                                            all_page_ids.add(str(page_id))
        except Exception:
            pass
            
        # Approach 8: Try campaigns and extract page info
        try:
            endpoint = f"{account_id}/campaigns"
            params = {
                "fields": "id,name,promoted_object,objective",
                "limit": 50
            }
            campaigns_data = await make_api_request(endpoint, access_token, params)
            if "data" in campaigns_data:
                for campaign in campaigns_data["data"]:
                    if "promoted_object" in campaign and "page_id" in campaign["promoted_object"]:
                        all_page_ids.add(campaign["promoted_object"]["page_id"])
        except Exception:
            pass
            
        # If we found any page IDs, get details for each
        if all_page_ids:
            page_details = {
                "data": [], 
                "total_pages_found": len(all_page_ids)
            }
            
            for page_id in all_page_ids:
                try:
                    page_endpoint = f"{page_id}"
                    page_params = {
                        "fields": "id,name,username,category,fan_count,link,verification_status,picture"
                    }
                    
                    page_data = await make_api_request(page_endpoint, access_token, page_params)
                    if "id" in page_data:
                        page_details["data"].append(page_data)
                    else:
                        page_details["data"].append({
                            "id": page_id, 
                            "error": "Page details not accessible"
                        })
                except Exception as e:
                    page_details["data"].append({
                        "id": page_id,
                        "error": f"Failed to get page details: {str(e)}"
                    })
            
            if page_details["data"]:
                return json.dumps(page_details, indent=2)
        
        # If all approaches failed, return empty data with a message
        return json.dumps({
            "data": [],
            "message": "No pages found associated with this account",
            "suggestion": "Create a Facebook page and connect it to this ad account, or ensure existing pages are properly connected through Business Manager"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": "Failed to get account pages",
            "details": str(e)
        }, indent=2)





