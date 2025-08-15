import json
from unittest.mock import AsyncMock, patch

import pytest

from meta_ads_mcp.core.ads import upload_ad_image


@pytest.mark.asyncio
async def test_upload_ad_image_normalizes_images_dict():
    mock_response = {
        "images": {
            "abc123": {
                "hash": "abc123",
                "url": "https://example.com/image.jpg",
                "width": 1200,
                "height": 628,
                "name": "image.jpg",
                "status": 1,
            }
        }
    }

    with patch("meta_ads_mcp.core.ads.make_api_request", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = mock_response

        # Use a data URL input to exercise that branch
        file_data_url = "data:image/png;base64,QUJDREVGRw=="  # 'ABCDEFG' base64
        result_json = await upload_ad_image(
            access_token="test",
            account_id="act_123",
            file=file_data_url,
            name="my-upload.png",
        )

        result = json.loads(result_json)

        assert result.get("success") is True
        assert result.get("account_id") == "act_123"
        assert result.get("name") == "my-upload.png"
        assert result.get("image_hash") == "abc123"
        assert result.get("images_count") == 1
        assert isinstance(result.get("images"), list) and result["images"][0]["hash"] == "abc123"


@pytest.mark.asyncio
async def test_upload_ad_image_error_structure_is_surfaced():
    mock_response = {"error": {"message": "Something went wrong", "code": 400}}

    with patch("meta_ads_mcp.core.ads.make_api_request", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = mock_response

        result_json = await upload_ad_image(
            access_token="test",
            account_id="act_123",
            file="data:image/png;base64,QUJD",
        )

        # Error responses from MCP functions may be wrapped multiple times under a data field
        payload = result_json
        for _ in range(5):
            # If it's a JSON string, parse it
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                    continue
                except Exception:
                    break
            # If it's a dict containing a JSON string in data, unwrap once
            if isinstance(payload, dict) and "data" in payload:
                payload = payload["data"]
                continue
            break
        error_payload = payload if isinstance(payload, dict) else json.loads(payload)

        assert "error" in error_payload
        assert error_payload["error"] == "Failed to upload image"
        assert isinstance(error_payload.get("details"), dict)
        assert error_payload.get("account_id") == "act_123"


@pytest.mark.asyncio
async def test_upload_ad_image_fallback_wraps_raw_response():
    mock_response = {"unexpected": "shape"}

    with patch("meta_ads_mcp.core.ads.make_api_request", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = mock_response

        result_json = await upload_ad_image(
            access_token="test",
            account_id="act_123",
            file="data:image/png;base64,QUJD",
        )

        result = json.loads(result_json)
        assert result.get("success") is True
        assert result.get("raw_response") == mock_response


@pytest.mark.asyncio
async def test_upload_ad_image_from_url_infers_name_and_prefixes_account_id():
    mock_response = {
        "images": {
            "hash999": {
                "url": "https://example.com/img.jpg",
                "width": 800,
                "height": 600,
                # omit nested hash intentionally to test normalization fallback
            }
        }
    }

    with patch("meta_ads_mcp.core.ads.try_multiple_download_methods", new_callable=AsyncMock) as mock_dl, \
         patch("meta_ads_mcp.core.ads.make_api_request", new_callable=AsyncMock) as mock_api:
        mock_dl.return_value = b"\xff\xd8\xff"  # minimal JPEG header bytes
        mock_api.return_value = mock_response

        # Provide raw account id (without act_) and ensure it is prefixed in the result
        result_json = await upload_ad_image(
            access_token="test",
            account_id="701351919139047",
            image_url="https://cdn.example.com/path/photo.jpg?x=1",
        )

        result = json.loads(result_json)
        assert result.get("success") is True
        assert result.get("account_id") == "act_701351919139047"
        # Name should be inferred from URL
        assert result.get("name") == "photo.jpg"
        # Primary hash should be derived from key when nested hash missing
        assert result.get("image_hash") == "hash999"
        assert result.get("images_count") == 1


