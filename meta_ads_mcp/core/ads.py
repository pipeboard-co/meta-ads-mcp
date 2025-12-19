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
    Get creative details for a specific ad. Best if combined with get_ad_image to get the full image.
    
    Args:
        ad_id: Meta Ads ad ID
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not ad_id:
        return json.dumps({"error": "No ad ID provided"}, indent=2)
        
    endpoint = f"{ad_id}/adcreatives"
    params = {
        "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec,asset_feed_spec,image_urls_for_viewing"
    }
    
    data = await make_api_request(endpoint, access_token, params)
    
    # Add image URLs for direct viewing if available
    if 'data' in data:
        for creative in data['data']:
            creative['image_urls_for_viewing'] = extract_creative_image_urls(creative)

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
    status: Optional[str] = None,
    bid_amount: Optional[int] = None,
    tracking_specs: Optional[List[Dict[str, Any]]] = None,
    creative_id: Optional[str] = None,
    access_token: Optional[str] = None
) -> str:
    """
    Update an ad with new settings.
    
    Args:
        ad_id: Meta Ads ad ID
        status: Update ad status (ACTIVE, PAUSED, etc.)
        bid_amount: Bid amount in account currency (in cents for USD)
        tracking_specs: Optional tracking specifications (e.g., for pixel events).
        creative_id: ID of the creative to associate with this ad (changes the ad's image/content)
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
    if creative_id is not None:
        # Creative parameter needs to be a JSON object containing creative_id
        params["creative"] = json.dumps({"creative_id": creative_id})

    if not params:
        return json.dumps({"error": "No update parameters provided (status, bid_amount, tracking_specs, or creative_id)"}, indent=2)

    endpoint = f"{ad_id}"
    try:
        data = await make_api_request(endpoint, access_token, params, method='POST')
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
    
    # Ensure account_id has the 'act_' prefix for API compatibility
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    
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
                        "Make sure the link is publicly reachable (no login, VPN, or IP restrictions).",
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
                        "Double‑check that the link is public and does not require login, VPN, or IP allow‑listing.",
                        "If the image is stored in a private app (for example, a self‑hosted gallery), upload it to a public URL or a CDN and try again.",
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


@mcp_server.tool()
@meta_api_tool
async def create_ad_creative(
    account_id: str,
    image_hash: str,
    access_token: Optional[str] = None,
    name: Optional[str] = None,
    page_id: Optional[str] = None,
    link_url: Optional[str] = None,
    message: Optional[str] = None,
    headline: Optional[str] = None,
    headlines: Optional[List[str]] = None,
    description: Optional[str] = None,
    descriptions: Optional[List[str]] = None,
    dynamic_creative_spec: Optional[Dict[str, Any]] = None,
    call_to_action_type: Optional[str] = None,
    lead_gen_form_id: Optional[str] = None,
    instagram_actor_id: Optional[str] = None
) -> str:
    """
    Create a new ad creative using an uploaded image hash.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        image_hash: Hash of the uploaded image
        access_token: Meta API access token (optional - will use cached token if not provided)
        name: Creative name
        page_id: Facebook Page ID to be used for the ad
        link_url: Destination URL for the ad
        message: Ad copy/text
        headline: Single headline for simple ads (cannot be used with headlines)
        headlines: List of headlines for dynamic creative testing (cannot be used with headline)
        description: Single description for simple ads (cannot be used with descriptions)
        descriptions: List of descriptions for dynamic creative testing (cannot be used with description)
        dynamic_creative_spec: Dynamic creative optimization settings
        call_to_action_type: Call to action button type (e.g., 'LEARN_MORE', 'SIGN_UP', 'SHOP_NOW')
        lead_gen_form_id: Lead generation form ID for lead generation campaigns. Required when using
                         lead generation CTAs like 'SIGN_UP', 'GET_OFFER', 'SUBSCRIBE', etc.
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
    
    # Enhanced page discovery: If no page ID is provided, use robust discovery methods
    if not page_id:
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
    
    # Prepare the creative data
    creative_data = {
        "name": name
    }
    
    # Choose between asset_feed_spec (dynamic creative) or object_story_spec (traditional)
    # ONLY use asset_feed_spec when user explicitly provides plural parameters (headlines/descriptions)
    if headlines or descriptions:
        # Use asset_feed_spec for dynamic creatives with multiple variants
        # Structure based on Meta API working example from documentation
        # ad_formats must be specified with exactly one format
        asset_feed_spec = {
            "images": [{"hash": image_hash}],
            "link_urls": [{"website_url": link_url if link_url else "https://facebook.com"}],
            "ad_formats": ["SINGLE_IMAGE"]
        }
        
        # Handle headlines - Meta API uses "titles" not "headlines" in asset_feed_spec
        if headlines:
            asset_feed_spec["titles"] = [{"text": headline_text} for headline_text in headlines]
            
        # Handle descriptions  
        if descriptions:
            asset_feed_spec["descriptions"] = [{"text": description_text} for description_text in descriptions]
        
        # Add message as bodies - Meta API uses "bodies" not "primary_texts" in asset_feed_spec
        if message:
            asset_feed_spec["bodies"] = [{"text": message}]
        
        # Add call_to_action_types if provided
        if call_to_action_type:
            asset_feed_spec["call_to_action_types"] = [call_to_action_type]
        
        creative_data["asset_feed_spec"] = asset_feed_spec
        
        # For dynamic creatives with asset_feed_spec, object_story_spec only needs page_id
        # Link information is already in asset_feed_spec.link_urls
        creative_data["object_story_spec"] = {
            "page_id": page_id
        }
    else:
        # Use traditional object_story_spec with link_data for simple creatives
        creative_data["object_story_spec"] = {
            "page_id": page_id,
            "link_data": {
                "image_hash": image_hash,
                "link": link_url if link_url else "https://facebook.com"
            }
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
        
        # Add call_to_action to link_data for simple creatives
        if call_to_action_type:
            cta_data = {"type": call_to_action_type}
            
            # Add lead form ID to value object if provided (required for lead generation campaigns)
            if lead_gen_form_id:
                cta_data["value"] = {"lead_gen_form_id": lead_gen_form_id}
            
            creative_data["object_story_spec"]["link_data"]["call_to_action"] = cta_data
    
    # Add dynamic creative spec if provided
    if dynamic_creative_spec:
        creative_data["dynamic_creative_spec"] = dynamic_creative_spec
    
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
                "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec,asset_feed_spec,url_tags,link_url"
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
async def update_ad_creative(
    creative_id: str,
    access_token: Optional[str] = None,
    name: Optional[str] = None,
    message: Optional[str] = None,
    headline: Optional[str] = None,
    headlines: Optional[List[str]] = None,
    description: Optional[str] = None,
    descriptions: Optional[List[str]] = None,
    dynamic_creative_spec: Optional[Dict[str, Any]] = None,
    call_to_action_type: Optional[str] = None,
    lead_gen_form_id: Optional[str] = None
) -> str:
    """
    Update an existing ad creative with new content or settings.
    
    Args:
        creative_id: Meta Ads creative ID to update
        access_token: Meta API access token (optional - will use cached token if not provided)
        name: New creative name
        message: New ad copy/text
        headline: Single headline for simple ads (cannot be used with headlines)
        headlines: New list of headlines for dynamic creative testing (cannot be used with headline)
        description: Single description for simple ads (cannot be used with descriptions)
        descriptions: New list of descriptions for dynamic creative testing (cannot be used with description)
        dynamic_creative_spec: New dynamic creative optimization settings
        call_to_action_type: New call to action button type
        lead_gen_form_id: Lead generation form ID for lead generation campaigns. Required when using
                         lead generation CTAs like 'SIGN_UP', 'GET_OFFER', 'SUBSCRIBE', etc.
    
    Returns:
        JSON response with updated creative details
    """
    # Check required parameters
    if not creative_id:
        return json.dumps({"error": "No creative ID provided"}, indent=2)
    
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
    
    # Prepare the update data
    update_data = {}
    
    if name:
        update_data["name"] = name
    
    # Choose between asset_feed_spec (dynamic creative) or object_story_spec (traditional)
    # ONLY use asset_feed_spec when user explicitly provides plural parameters (headlines/descriptions)
    if headlines or descriptions or dynamic_creative_spec:
        # Handle dynamic creative assets via asset_feed_spec
        asset_feed_spec = {}
        
        # Add required ad_formats field for dynamic creatives
        asset_feed_spec["ad_formats"] = ["SINGLE_IMAGE"]
        
        # Handle headlines - Meta API uses "titles" not "headlines" in asset_feed_spec
        if headlines:
            asset_feed_spec["titles"] = [{"text": headline_text} for headline_text in headlines]
            
        # Handle descriptions  
        if descriptions:
            asset_feed_spec["descriptions"] = [{"text": description_text} for description_text in descriptions]
        
        # Add message as bodies - Meta API uses "bodies" not "primary_texts" in asset_feed_spec
        if message:
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
    
    # Prepare the API endpoint for updating the creative
    endpoint = f"{creative_id}"
    
    try:
        # Make API request to update the creative
        data = await make_api_request(endpoint, access_token, update_data, method="POST")
        
        # If successful, get more details about the updated creative
        if "id" in data:
            creative_endpoint = f"{creative_id}"
            creative_params = {
                "fields": "id,name,status,thumbnail_url,image_url,image_hash,object_story_spec,url_tags,link_url,dynamic_creative_spec"
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
                "page_id": page["id"],
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
                "page_id": page["id"],
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
    # Ensure account_id has the 'act_' prefix
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    
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
    
    # Ensure account_id has the 'act_' prefix for regular accounts
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    
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





