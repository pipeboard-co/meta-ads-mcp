"""End-to-end test for event_id parameter in create_ad_creative.

Run manually with PIPEBOARD_API_TOKEN set:
    PIPEBOARD_API_TOKEN=pk_xxx python tests/test_event_id_e2e.py
"""

import asyncio
import json
import os
import sys

# Ensure we import the LOCAL meta_ads_mcp, not the installed site-packages version
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _repo_root)

from meta_ads_mcp.core import ads as ads_module

ACCOUNT_ID = "act_1775818363064545"
PAGE_ID = "1041573382375102"
EVENT_ID = "2699305693795917"
IMAGE_HASH = "ca228ac8ff3a66dca9435c90dd6953d6"
EVENT_URL = f"https://www.facebook.com/events/{EVENT_ID}"


async def main():
    if not os.environ.get("PIPEBOARD_API_TOKEN"):
        print("ERROR: PIPEBOARD_API_TOKEN not set")
        sys.exit(1)

    create_fn = ads_module.create_ad_creative
    get_fn = ads_module.get_creative_details

    print("=== Creating EVENT_RSVP creative with event_id ===")
    create_result = await create_fn(
        account_id=ACCOUNT_ID,
        page_id=PAGE_ID,
        image_hash=IMAGE_HASH,
        name="E2E Test - event_id EVENT_RSVP",
        link_url=EVENT_URL,
        message="Join our event!",
        headline="RSVP Now",
        call_to_action_type="EVENT_RSVP",
        event_id=EVENT_ID,
    )
    print(create_result)

    data = json.loads(create_result)
    if "error" in data:
        print(f"\nFAIL: create returned error: {data['error']}")
        sys.exit(1)

    creative_id = data.get("creative_id") or data.get("details", {}).get("id")
    if not creative_id:
        print(f"\nFAIL: no creative_id in response")
        sys.exit(1)

    print(f"\n=== Read-back creative {creative_id} ===")
    read_result = await get_fn(creative_id=creative_id)
    print(read_result)

    read_data = json.loads(read_result)
    oss = read_data.get("object_story_spec", {})
    link_data = oss.get("link_data", {})
    got_event_id = link_data.get("event_id")
    cta = link_data.get("call_to_action", {})
    cta_value_event_id = cta.get("value", {}).get("event_id")

    print("\n=== Verification ===")
    print(f"link_data.event_id               = {got_event_id}")
    print(f"call_to_action.value.event_id    = {cta_value_event_id}")
    print(f"call_to_action.type              = {cta.get('type')}")

    ok = str(got_event_id) == EVENT_ID
    if ok:
        print(f"\nPASS: link_data.event_id matches expected {EVENT_ID}")
    else:
        print(f"\nFAIL: expected {EVENT_ID}, got {got_event_id}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
