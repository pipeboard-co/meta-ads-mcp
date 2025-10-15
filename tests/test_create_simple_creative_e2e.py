"""End-to-end test for creating simple creatives with singular headline/description."""

import pytest
import json
import os
from meta_ads_mcp.core.ads import create_ad_creative


@pytest.mark.skip(reason="Requires authentication - run manually with: pytest tests/test_create_simple_creative_e2e.py -v")
@pytest.mark.asyncio
async def test_create_simple_creative_with_real_api():
    """Test creating a simple creative with singular headline/description using real Meta API."""
    
    # Account and image details from user
    account_id = "act_3182643988557192"
    image_hash = "ca228ac8ff3a66dca9435c90dd6953d6"
    
    # Create a simple creative with singular headline and description
    result = await create_ad_creative(
        account_id=account_id,
        image_hash=image_hash,
        name="E2E Test - Simple Creative",
        link_url="https://example.com/",
        message="This is a test message for the ad.",
        headline="Test Headline",
        description="Test description for ad.",
        call_to_action_type="LEARN_MORE"
    )
    
    print("\n=== API Response ===")
    print(result)
    
    result_data = json.loads(result)
    
    # Check if there's an error
    if "error" in result_data:
        pytest.fail(f"Creative creation failed: {result_data['error']}")
    
    # Verify success
    assert "success" in result_data or "creative_id" in result_data or "id" in result_data, \
        f"Expected success response, got: {result_data}"
    
    print("\n✅ Simple creative created successfully!")
    
    if "creative_id" in result_data:
        print(f"Creative ID: {result_data['creative_id']}")
    elif "details" in result_data and "id" in result_data["details"]:
        print(f"Creative ID: {result_data['details']['id']}")

