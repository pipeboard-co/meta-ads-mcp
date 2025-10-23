#!/usr/bin/env python3
"""Quick test script for multi-tenant setup."""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime

# Set up environment
os.environ.setdefault("DATABASE_URL", "postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")
os.environ.setdefault("BOOTSTRAP_TOKEN", "bootstrap_secret_change_me")

BASE_URL = "http://localhost:8080"
BOOTSTRAP_TOKEN = os.environ["BOOTSTRAP_TOKEN"]

def test_health():
    """Test health endpoint."""
    print("\n[TEST] Health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_create_user():
    """Test user creation."""
    print("\n[TEST] Creating user...")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/users",
            headers={
                "X-BOOTSTRAP-TOKEN": BOOTSTRAP_TOKEN,
                "Content-Type": "application/json"
            },
            json={"email": f"test-{int(time.time())}@example.com"}
        )
        if response.status_code in [201, 409]:  # Created or already exists
            data = response.json()
            print(f"✅ User created/exists: {data}")
            return data.get("id")
        else:
            print(f"❌ User creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None

def test_create_pat(user_id=None):
    """Test PAT creation."""
    print("\n[TEST] Creating PAT...")
    try:
        body = {"name": "Test Token"}
        if user_id:
            body["user_id"] = user_id
        
        response = requests.post(
            f"{BASE_URL}/v1/pats",
            headers={
                "X-BOOTSTRAP-TOKEN": BOOTSTRAP_TOKEN,
                "Content-Type": "application/json"
            },
            json=body
        )
        if response.status_code == 201:
            data = response.json()
            print(f"✅ PAT created: {data['name']}")
            print(f"   Token: {data['token']}")
            print(f"   Prefix: {data['prefix']}")
            return data["token"]
        else:
            print(f"❌ PAT creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ PAT creation error: {e}")
        return None

def test_save_meta_token(pat):
    """Test saving Meta token."""
    print("\n[TEST] Saving Meta token...")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/meta/token",
            headers={
                "Authorization": f"Bearer {pat}",
                "Content-Type": "application/json"
            },
            json={
                "access_token": "test_meta_token_12345",
                "account_id": "act_test123"
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Meta token saved: {data}")
            return True
        else:
            print(f"❌ Meta token save failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Meta token save error: {e}")
        return False

def test_whoami(pat):
    """Test whoami endpoint."""
    print("\n[TEST] Whoami check...")
    try:
        response = requests.get(
            f"{BASE_URL}/v1/me",
            headers={"Authorization": f"Bearer {pat}"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Whoami succeeded:")
            print(f"   Email: {data['email']}")
            print(f"   User ID: {data['id']}")
            print(f"   Providers: {len(data.get('providers', []))}")
            return True
        else:
            print(f"❌ Whoami failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Whoami error: {e}")
        return False

def test_list_pats(pat):
    """Test listing PATs."""
    print("\n[TEST] Listing PATs...")
    try:
        response = requests.get(
            f"{BASE_URL}/v1/pats",
            headers={"Authorization": f"Bearer {pat}"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PATs listed: {len(data['tokens'])} token(s)")
            for token in data['tokens']:
                print(f"   - {token['name']} ({token['prefix']})")
            return True
        else:
            print(f"❌ List PATs failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ List PATs error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Multi-Tenant System Test Suite")
    print("=" * 60)
    print(f"\nServer URL: {BASE_URL}")
    print(f"Bootstrap Token: {BOOTSTRAP_TOKEN[:10]}...")
    
    # Check if server is running
    print("\n[SETUP] Checking if server is running...")
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("✅ Server is running")
    except:
        print("❌ Server is not running!")
        print("\nPlease start the server first:")
        print("  python -m meta_ads_mcp --transport streamable-http --host 0.0.0.0 --port 8080")
        return 1
    
    # Run tests
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Create user
    user_id = test_create_user()
    results.append(("Create User", user_id is not None))
    
    # Test 3: Create PAT
    pat = test_create_pat(user_id)
    results.append(("Create PAT", pat is not None))
    
    if pat:
        # Test 4: Save Meta token
        results.append(("Save Meta Token", test_save_meta_token(pat)))
        
        # Test 5: Whoami
        results.append(("Whoami", test_whoami(pat)))
        
        # Test 6: List PATs
        results.append(("List PATs", test_list_pats(pat)))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
