import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.adsets import create_adset, update_adset, get_adsets, get_adset_details


@pytest.mark.asyncio
async def test_create_adset_passes_regional_regulation_identities():
    sample_response = {"id": "adset_sg_1", "name": "SG Adset"}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await create_adset(
            account_id="act_198610914369515",
            campaign_id="cmp_1",
            name="SG Adset",
            optimization_goal="LINK_CLICKS",
            billing_event="IMPRESSIONS",
            targeting={"geo_locations": {"countries": ["SG"]}},
            regional_regulated_categories=["SINGAPORE_UNIVERSAL"],
            regional_regulation_identities={
                "singapore_universal_beneficiary": "id_123",
                "singapore_universal_payer": "id_456",
            },
            access_token="test_token",
        )

        assert json.loads(result)["id"] == "adset_sg_1"
        call_args = mock_api.call_args
        params = call_args[0][2]
        assert json.loads(params["regional_regulated_categories"]) == ["SINGAPORE_UNIVERSAL"]
        identities = json.loads(params["regional_regulation_identities"])
        assert identities["singapore_universal_beneficiary"] == "id_123"
        assert identities["singapore_universal_payer"] == "id_456"


@pytest.mark.asyncio
async def test_update_adset_passes_regional_regulation_identities():
    sample_response = {"success": True}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await update_adset(
            adset_id="120",
            regional_regulated_categories=["TAIWAN_UNIVERSAL"],
            regional_regulation_identities={
                "taiwan_universal_beneficiary": "id_tw_1",
                "taiwan_universal_payer": "id_tw_2",
            },
            access_token="test_token",
        )

        assert json.loads(result)["success"] is True
        call_args = mock_api.call_args
        params = call_args[0][2]
        assert json.loads(params["regional_regulated_categories"]) == ["TAIWAN_UNIVERSAL"]
        identities = json.loads(params["regional_regulation_identities"])
        assert identities["taiwan_universal_beneficiary"] == "id_tw_1"


@pytest.mark.asyncio
async def test_get_adset_details_fields_include_regional_regulation():
    sample_response = {
        "id": "120",
        "name": "SG Adset",
        "regional_regulated_categories": ["SINGAPORE_UNIVERSAL"],
        "regional_regulation_identities": {
            "singapore_universal_beneficiary": "id_123",
            "singapore_universal_payer": "id_456",
        },
    }
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        result = await get_adset_details(adset_id="120", access_token="test_token")
        data = json.loads(result)
        assert data["regional_regulated_categories"] == ["SINGAPORE_UNIVERSAL"]

        call_args = mock_api.call_args
        params = call_args[0][2]
        fields = params.get("fields", "")
        assert "regional_regulated_categories" in fields
        assert "regional_regulation_identities" in fields


@pytest.mark.asyncio
async def test_get_adsets_fields_include_regional_regulation():
    sample_response = {"data": []}
    with patch('meta_ads_mcp.core.adsets.make_api_request', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = sample_response

        await get_adsets(account_id="act_123", access_token="test_token", limit=1)

        call_args = mock_api.call_args
        params = call_args[0][2]
        fields = params.get("fields", "")
        assert "regional_regulated_categories" in fields
        assert "regional_regulation_identities" in fields
