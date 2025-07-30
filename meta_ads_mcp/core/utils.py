"""Utility functions for Meta Ads API."""

from typing import Optional, Dict, Any, List
import httpx
import io
from PIL import Image as PILImage
import base64
import time
import asyncio
import os
import json
import logging
import pathlib
import platform

# Check for Meta app credentials in environment
META_APP_ID = os.environ.get("META_APP_ID", "")
META_APP_SECRET = os.environ.get("META_APP_SECRET", "")

# Only show warnings about Meta credentials if we're not using Pipeboard
# Check for Pipeboard token in environment
using_pipeboard = bool(os.environ.get("PIPEBOARD_API_TOKEN", ""))

# Print warning if Meta app credentials are not configured and not using Pipeboard
if not using_pipeboard:
    if not META_APP_ID:
        print("WARNING: META_APP_ID environment variable is not set.")
        print("RECOMMENDED: Use Pipeboard authentication by setting PIPEBOARD_API_TOKEN instead.")
        print("ALTERNATIVE: For direct Meta authentication, set META_APP_ID to your Meta App ID.")
    if not META_APP_SECRET:
        print("WARNING: META_APP_SECRET environment variable is not set.")
        print("NOTE: This is only needed for direct Meta authentication. Pipeboard authentication doesn't require this.")
        print("RECOMMENDED: Use Pipeboard authentication by setting PIPEBOARD_API_TOKEN instead.")

# Configure logging to file
def setup_logging():
    """Set up logging to file for troubleshooting."""
    # Get platform-specific path for logs
    if platform.system() == "Windows":
        base_path = pathlib.Path(os.environ.get("APPDATA", ""))
    elif platform.system() == "Darwin":  # macOS
        base_path = pathlib.Path.home() / "Library" / "Application Support"
    else:  # Assume Linux/Unix
        base_path = pathlib.Path.home() / ".config"
    
    # Create directory if it doesn't exist
    log_dir = base_path / "meta-ads-mcp"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "meta_ads_debug.log"
    
    # Configure file logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=str(log_file),
        filemode='a'  # Append mode
    )
    
    # Create a logger
    logger = logging.getLogger("meta-ads-mcp")
    logger.setLevel(logging.DEBUG)
    
    # Log startup information
    logger.info(f"Logging initialized. Log file: {log_file}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Using Pipeboard authentication: {using_pipeboard}")
    
    return logger

# Create the logger instance to be imported by other modules
logger = setup_logging()

# Global store for ad creative images
ad_creative_images = {}


def extract_creative_image_urls(creative: Dict[str, Any]) -> List[str]:
    """
    Extract image URLs from a creative object for direct viewing.
    Prioritizes higher quality images over thumbnails.
    
    Args:
        creative: Meta Ads creative object
        
    Returns:
        List of image URLs found in the creative, prioritized by quality
    """
    image_urls = []
    
    # Prioritize higher quality image URLs in this order:
    # 1. image_urls_for_viewing (usually highest quality)
    # 2. image_url (direct field)
    # 3. object_story_spec.link_data.picture (usually full size)
    # 4. asset_feed_spec images (multiple high-quality images)
    # 5. thumbnail_url (last resort - often profile thumbnail)
    
    # Check for image_urls_for_viewing (highest priority)
    if "image_urls_for_viewing" in creative and creative["image_urls_for_viewing"]:
        image_urls.extend(creative["image_urls_for_viewing"])
    
    # Check for direct image_url field
    if "image_url" in creative and creative["image_url"]:
        image_urls.append(creative["image_url"])
    
    # Check object_story_spec for image URLs
    if "object_story_spec" in creative:
        story_spec = creative["object_story_spec"]
        
        # Check link_data for image fields
        if "link_data" in story_spec:
            link_data = story_spec["link_data"]
            
            # Check for picture field (usually full size)
            if "picture" in link_data and link_data["picture"]:
                image_urls.append(link_data["picture"])
                
            # Check for image_url field in link_data
            if "image_url" in link_data and link_data["image_url"]:
                image_urls.append(link_data["image_url"])
        
        # Check video_data for thumbnail (if present)
        if "video_data" in story_spec and "image_url" in story_spec["video_data"]:
            image_urls.append(story_spec["video_data"]["image_url"])
    
    # Check asset_feed_spec for multiple images
    if "asset_feed_spec" in creative and "images" in creative["asset_feed_spec"]:
        for image in creative["asset_feed_spec"]["images"]:
            if "url" in image and image["url"]:
                image_urls.append(image["url"])
    
    # Check for thumbnail_url field (lowest priority)
    if "thumbnail_url" in creative and creative["thumbnail_url"]:
        image_urls.append(creative["thumbnail_url"])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in image_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls


async def download_image(url: str) -> Optional[bytes]:
    """
    Download an image from a URL.
    
    Args:
        url: Image URL
        
    Returns:
        Image data as bytes if successful, None otherwise
    """
    try:
        print(f"Attempting to download image from URL: {url}")
        
        # Use minimal headers like curl does
        headers = {
            "User-Agent": "curl/8.4.0",
            "Accept": "*/*"
        }
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            # Simple GET request just like curl
            response = await client.get(url, headers=headers)
            
            # Check response
            if response.status_code == 200:
                print(f"Successfully downloaded image: {len(response.content)} bytes")
                return response.content
            else:
                print(f"Failed to download image: HTTP {response.status_code}")
                return None
                
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error when downloading image: {e}")
        return None
    except httpx.RequestError as e:
        print(f"Request Error when downloading image: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error downloading image: {e}")
        return None


async def try_multiple_download_methods(url: str) -> Optional[bytes]:
    """
    Try multiple methods to download an image, with different approaches for Meta CDN.
    
    Args:
        url: Image URL
        
    Returns:
        Image data as bytes if successful, None otherwise
    """
    # Method 1: Direct download with custom headers
    image_data = await download_image(url)
    if image_data:
        return image_data
    
    print("Direct download failed, trying alternative methods...")
    
    # Method 2: Try adding Facebook cookie simulation
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Cookie": "presence=EDvF3EtimeF1697900316EuserFA21B00112233445566AA0EstateFDutF0CEchF_7bCC"  # Fake cookie
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            print(f"Method 2 succeeded with cookie simulation: {len(response.content)} bytes")
            return response.content
    except Exception as e:
        print(f"Method 2 failed: {str(e)}")
    
    # Method 3: Try with session that keeps redirects and cookies
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # First visit Facebook to get cookies
            await client.get("https://www.facebook.com/", timeout=30.0)
            # Then try the image URL
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            print(f"Method 3 succeeded with Facebook session: {len(response.content)} bytes")
            return response.content
    except Exception as e:
        print(f"Method 3 failed: {str(e)}")
    
    return None


def create_resource_from_image(image_bytes: bytes, resource_id: str, name: str) -> Dict[str, Any]:
    """
    Create a resource entry from image bytes.
    
    Args:
        image_bytes: Raw image data
        resource_id: Unique identifier for the resource
        name: Human-readable name for the resource
        
    Returns:
        Dictionary with resource information
    """
    ad_creative_images[resource_id] = {
        "data": image_bytes,
        "mime_type": "image/jpeg",
        "name": name
    }
    
    return {
        "resource_id": resource_id,
        "resource_uri": f"meta-ads://images/{resource_id}",
        "name": name,
        "size": len(image_bytes)
    } 