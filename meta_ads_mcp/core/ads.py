"""Ad and Creative-related functionality for Meta Ads API."""

import json
from typing import Optional, Dict, Any, List
import io
from PIL import Image as PILImage
from mcp.server.fastmcp import Image
import os
import time

from .api import meta_api_tool, make_api_request
from .accounts import get_ad_accounts
from .utils import download_image, try_multiple_download_methods, ad_creative_images, extract_creative_image_urls
from .server import mcp_server


@mcp_server.tool()
@meta_api_tool
async def get_ads(access_token: str = None, account_id: str = None, limit: int = 10, 
                 campaign_id: str = "", adset_id: str = "") -> str:
    """
    Get ads for a Meta Ads account with optional filtering.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        limit: Maximum number of ads to return (default: 10)
        campaign_id: Optional campaign ID to filter by
        adset_id: Optional ad set ID to filter by
    """
    # If no account ID is specified, try to get the first one for the user
    if not account_id:
        accounts_json = await get_ad_accounts("me", json.dumps({"limit": 1}), access_token)
        accounts_data = json.loads(accounts_json)
        
        if "data" in accounts_data and accounts_data["data"]:
            account_id = accounts_data["data"][0]["id"]
        else:
            return json.dumps({"error": "No account ID specified and no accounts found for user"}, indent=2)
    
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
async def get_ad_details(access_token: str = None, ad_id: str = None) -> str:
    """
    Get detailed information about a specific ad.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        ad_id: Meta Ads ad ID
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
async def create_ad(
    account_id: str = None,
    name: str = None,
    adset_id: str = None,
    creative_id: str = None,
    status: str = "PAUSED",
    bid_amount = None,
    tracking_specs: Optional[List[Dict[str, Any]]] = None,
    access_token: str = None
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
async def get_ad_creatives(access_token: str = None, ad_id: str = None) -> str:
    """
    Get creative details for a specific ad. Best if combined with get_ad_image to get the full image.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        ad_id: Meta Ads ad ID
    """
    if not ad_id:
        return json.dumps({"error": "No ad ID provided"}, indent=2)
        
    endpoint = f"{ad_id}/adcreatives"
    params = {
        "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec" # Added image_hash
    }
    
    data = await make_api_request(endpoint, access_token, params)
    
    # Add image URLs for direct viewing if available
    if 'data' in data:
        for creative in data['data']:
            creative['image_urls_for_viewing'] = extract_creative_image_urls(creative)

    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_ad_image(access_token: str = None, ad_id: str = None) -> Image:
    """
    Get, download, and visualize a Meta ad image in one step. Useful to see the image in the LLM.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        ad_id: Meta Ads ad ID
    
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
        # Get creative for ad to try to extract hash
        creative_json = await get_ad_creatives(access_token=access_token, ad_id=ad_id)
        # The result is wrapped by @meta_api_tool, so we need to extract the data
        creative_wrapper = json.loads(creative_json)
        creative_data = json.loads(creative_wrapper["data"])
        
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
    
    if not image_hashes:
        return "Error: No image hashes found in creative"
    
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
async def save_ad_image_locally(access_token: str = None, ad_id: str = None, output_dir: str = "ad_images") -> str:
    """
    Get, download, and save a Meta ad image locally, returning the file path.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        ad_id: Meta Ads ad ID
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
        # The result is wrapped by @meta_api_tool, so we need to extract the data
        creative_wrapper = json.loads(creative_json)
        creative_data_list = json.loads(creative_wrapper["data"])
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
    status: str = None,
    bid_amount: int = None,
    tracking_specs = None,
    access_token: str = None
) -> str:
    """
    Update an ad with new settings.
    
    Args:
        ad_id: Meta Ads ad ID
        status: Update ad status (ACTIVE, PAUSED, etc.)
        bid_amount: Bid amount in account currency (in cents for USD)
        tracking_specs: Optional tracking specifications (e.g., for pixel events).
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not ad_id:
        return json.dumps({"error": "Ad ID is required"}, indent=2)

    params = {}
    if status:
        params["status"] = status
    if bid_amount is not None:
        # Ensure bid_amount is sent as a string if it's not null
        params["bid_amount"] = str(bid_amount)
    if tracking_specs is not None: # Add tracking_specs to params if provided
        params["tracking_specs"] = json.dumps(tracking_specs) # Needs to be JSON encoded string

    if not params:
        return json.dumps({"error": "No update parameters provided (status, bid_amount, or tracking_specs)"}, indent=2)

    endpoint = f"{ad_id}"
    data = await make_api_request(endpoint, access_token, params, method='POST')

    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def upload_ad_image(
    access_token: str = None,
    account_id: str = None,
    image_path: str = None,
    name: str = None
) -> str:
    """
    Upload an image to use in Meta Ads creatives.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        image_path: Path to the image file to upload
        name: Optional name for the image (default: filename)
    
    Returns:
        JSON response with image details including hash for creative creation
    """
    # Check required parameters
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)
    
    if not image_path:
        return json.dumps({"error": "No image path provided"}, indent=2)
    
    # Ensure account_id has the 'act_' prefix for API compatibility
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    
    # Check if image file exists
    if not os.path.exists(image_path):
        return json.dumps({"error": f"Image file not found: {image_path}"}, indent=2)
    
    try:
        # Read image file
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        
        # Get image filename if name not provided
        if not name:
            name = os.path.basename(image_path)
        
        # Prepare the API endpoint for uploading images
        endpoint = f"{account_id}/adimages"
        
        # We need to convert the binary data to base64 for API upload
        import base64
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Prepare POST parameters
        params = {
            "bytes": encoded_image,
            "name": name
        }
        
        # Make API request to upload the image
        print(f"Uploading image to Facebook Ad Account {account_id}")
        data = await make_api_request(endpoint, access_token, params, method="POST")
        
        return json.dumps(data, indent=2)
    
    except Exception as e:
        return json.dumps({
            "error": "Failed to upload image",
            "details": str(e)
        }, indent=2)


@mcp_server.tool()
@meta_api_tool
async def create_ad_creative(
    access_token: str = None,
    account_id: str = None,
    name: str = None,
    image_hash: str = None,
    page_id: str = None,
    link_url: str = None,
    message: str = None,
    headline: str = None,
    description: str = None,
    call_to_action_type: str = None,
    instagram_actor_id: str = None
) -> str:
    """
    Create a new ad creative using an uploaded image hash.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        name: Creative name
        image_hash: Hash of the uploaded image
        page_id: Facebook Page ID to be used for the ad
        link_url: Destination URL for the ad
        message: Ad copy/text
        headline: Ad headline
        description: Ad description
        call_to_action_type: Call to action button type (e.g., 'LEARN_MORE', 'SIGN_UP', 'SHOP_NOW')
        instagram_actor_id: Optional Instagram account ID for Instagram placements
    
    Returns:
        JSON response with created creative details
    """
    # Check required parameters
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)
    
    if not image_hash:
        return json.dumps({"error": "No image hash provided"}, indent=2)
    
    if not name:
        name = f"Creative {int(time.time())}"
    
    # Ensure account_id has the 'act_' prefix
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    
    # If no page ID is provided, try to find a page associated with the account
    if not page_id:
        try:
            # Query to get pages associated with the account
            pages_endpoint = f"{account_id}/assigned_pages"
            pages_params = {
                "fields": "id,name",
                "limit": 1 
            }
            
            pages_data = await make_api_request(pages_endpoint, access_token, pages_params)
            
            if "data" in pages_data and pages_data["data"]:
                page_id = pages_data["data"][0]["id"]
                print(f"Using page ID: {page_id} ({pages_data['data'][0].get('name', 'Unknown')})")
            else:
                return json.dumps({
                    "error": "No page ID provided and no pages found for this account",
                    "suggestion": "Please provide a page_id parameter"
                }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": "Error finding page for account",
                "details": str(e),
                "suggestion": "Please provide a page_id parameter"
            }, indent=2)
    
    # Prepare the creative data
    creative_data = {
        "name": name,
        "object_story_spec": {
            "page_id": page_id,
            "link_data": {
                "image_hash": image_hash,
                "link": link_url if link_url else "https://facebook.com"
            }
        }
    }
    
    # Add optional parameters if provided
    if message:
        creative_data["object_story_spec"]["link_data"]["message"] = message
    
    if headline:
        creative_data["object_story_spec"]["link_data"]["name"] = headline
        
    if description:
        creative_data["object_story_spec"]["link_data"]["description"] = description
    
    if call_to_action_type:
        creative_data["object_story_spec"]["link_data"]["call_to_action"] = {
            "type": call_to_action_type
        }
    
    if instagram_actor_id:
        creative_data["instagram_actor_id"] = instagram_actor_id
    
    # Prepare the API endpoint for creating a creative
    endpoint = f"{account_id}/adcreatives"
    
    try:
        # Make API request to create the creative
        data = await make_api_request(endpoint, access_token, creative_data, method="POST")
        
        # If successful, get more details about the created creative
        if "id" in data:
            creative_id = data["id"]
            creative_endpoint = f"{creative_id}"
            creative_params = {
                "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec,url_tags,link_url"
            }
            
            creative_details = await make_api_request(creative_endpoint, access_token, creative_params)
            return json.dumps({
                "success": True,
                "creative_id": creative_id,
                "details": creative_details
            }, indent=2)
        
        return json.dumps(data, indent=2)
    
    except Exception as e:
        return json.dumps({
            "error": "Failed to create ad creative",
            "details": str(e),
            "creative_data_sent": creative_data
        }, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_account_pages(access_token: str = None, account_id: str = None) -> str:
    """
    Get pages associated with a Meta Ads account.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
    
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
    
    # Ensure account_id has the 'act_' prefix for regular accounts
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    
    try:
        # Try all approaches that might work
        
        # Approach 1: Get active ads and extract page IDs
        endpoint = f"{account_id}/ads"
        params = {
            "fields": "creative{object_story_spec{page_id}}",
            "limit": 100
        }
        
        ads_data = await make_api_request(endpoint, access_token, params)
        
        # Extract unique page IDs from ads
        page_ids = set()
        if "data" in ads_data:
            for ad in ads_data.get("data", []):
                if "creative" in ad and "creative" in ad and "object_story_spec" in ad["creative"] and "page_id" in ad["creative"]["object_story_spec"]:
                    page_ids.add(ad["creative"]["object_story_spec"]["page_id"])
        
        # If we found page IDs, get details for each
        if page_ids:
            page_details = {"data": []}
            
            for page_id in page_ids:
                page_endpoint = f"{page_id}"
                page_params = {
                    "fields": "id,name,username,category,fan_count,link,verification_status,picture"
                }
                
                page_data = await make_api_request(page_endpoint, access_token, page_params)
                if "id" in page_data:
                    page_details["data"].append(page_data)
            
            if page_details["data"]:
                return json.dumps(page_details, indent=2)
        
        # Approach 2: Try client_pages endpoint
        endpoint = f"{account_id}/client_pages"
        params = {
            "fields": "id,name,username,category,fan_count,link,verification_status,picture"
        }
        
        client_pages_data = await make_api_request(endpoint, access_token, params)
        
        if "data" in client_pages_data and client_pages_data["data"]:
            return json.dumps(client_pages_data, indent=2)
        
        # Approach 3: Try promoted_objects endpoint to find page IDs
        endpoint = f"{account_id}/promoted_objects"
        params = {
            "fields": "page_id"
        }
        
        promoted_objects_data = await make_api_request(endpoint, access_token, params)
        
        if "data" in promoted_objects_data and promoted_objects_data["data"]:
            page_ids = set()
            for obj in promoted_objects_data["data"]:
                if "page_id" in obj:
                    page_ids.add(obj["page_id"])
            
            if page_ids:
                page_details = {"data": []}
                for page_id in page_ids:
                    page_endpoint = f"{page_id}"
                    page_params = {
                        "fields": "id,name,username,category,fan_count,link,verification_status,picture"
                    }
                    
                    page_data = await make_api_request(page_endpoint, access_token, page_params)
                    if "id" in page_data:
                        page_details["data"].append(page_data)
                
                if page_details["data"]:
                    return json.dumps(page_details, indent=2)
        
        # Approach 4: Extract page IDs from tracking_specs in ads
        # Inspired by praveen92y's implementation for robust page detection
        # This approach is often the most reliable as confirmed by community feedback
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
                        # If 'page' key exists, add all page IDs
                        if isinstance(spec, dict) and "page" in spec:
                            page_list = spec["page"]
                            if isinstance(page_list, list):
                                for page_id in page_list:
                                    # Validate page ID format (should be numeric string)
                                    if isinstance(page_id, (str, int)) and str(page_id).isdigit():
                                        tracking_page_ids.add(str(page_id))
        
        if tracking_page_ids:
            page_details = {"data": [], "source": "tracking_specs", "note": "Page IDs extracted from active ads - these are the most reliable for ad creation"}
            for page_id in tracking_page_ids:
                page_endpoint = f"{page_id}"
                page_params = {
                    "fields": "id,name,username,category,fan_count,link,verification_status,picture"
                }
                
                page_data = await make_api_request(page_endpoint, access_token, page_params)
                if "id" in page_data:
                    # Add additional context about this page ID being suitable for ads
                    page_data["_meta"] = {
                        "suitable_for_ads": True,
                        "found_in_tracking_specs": True,
                        "recommended_for_create_ad_creative": True
                    }
                    page_details["data"].append(page_data)
                else:
                    page_details["data"].append({
                        "id": page_id, 
                        "error": "Page details not found",
                        "_meta": {
                            "suitable_for_ads": True,
                            "found_in_tracking_specs": True,
                            "note": "Page ID exists in ads but details not accessible - you can still use this ID for ad creation"
                        }
                    })
            
            if page_details["data"]:
                return json.dumps(page_details, indent=2)
        
        # If all approaches failed, return empty data with a message
        return json.dumps({
            "data": [],
            "message": "No pages found associated with this account using automated methods",
            "troubleshooting": {
                "suggestion_1": "If you have existing ads, run 'get_ads' and look for page IDs in the 'tracking_specs' field",
                "suggestion_2": "Use the exact page ID from existing ads' tracking_specs for creating new ad creatives",
                "suggestion_3": "Verify your page ID format - it should be a numeric string (e.g., '123456789')",
                "suggestion_4": "Check for digit transpositions or formatting errors in your page ID"
            },
            "note": "Based on community feedback, page IDs from existing ads' tracking_specs are the most reliable for ad creation"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": "Failed to get account pages",
            "details": str(e)
        }, indent=2)