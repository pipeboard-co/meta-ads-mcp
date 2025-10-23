#!/usr/bin/env python3
"""Setup script for production PAT authentication testing."""

import sys
import os
import json

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_ads_mcp.core.db import get_db, init_db
from meta_ads_mcp.core.models import User, PersonalAccessToken
from meta_ads_mcp.core.pat import generate_pat
from datetime import datetime, timedelta

def load_cached_token():
    """Load the Meta token from the cache."""
    cache_path = os.path.expanduser("~/Library/Application Support/meta-ads-mcp/token_cache.json")
    
    if not os.path.exists(cache_path):
        print(f"❌ Token cache not found at: {cache_path}")
        return None
    
    try:
        with open(cache_path, 'r') as f:
            data = json.load(f)
            access_token = data.get('access_token')
            if access_token:
                print(f"✅ Loaded Meta token from cache")
                print(f"   Token preview: {access_token[:20]}...")
                return access_token
            else:
                print("❌ No access_token found in cache")
                return None
    except Exception as e:
        print(f"❌ Error loading token cache: {e}")
        return None

def main():
    print("=" * 60)
    print("Production PAT Authentication Setup")
    print("=" * 60)
    print()
    
    # Initialize database
    print("1. Initializing database...")
    try:
        init_db()
        print("   ✅ Database initialized")
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        return 1
    
    # Load Meta token from cache
    print("\n2. Loading Meta token from cache...")
    meta_token = load_cached_token()
    if not meta_token:
        print("   ❌ Failed to load Meta token")
        print("   Run: python -m meta_ads_mcp --login")
        return 1
    
    # Create or get test user
    print("\n3. Creating test user...")
    try:
        with get_db() as db:
            # Check if user already exists
            user = db.query(User).filter_by(email="test@example.com").first()
            
            if user:
                print(f"   ✅ User already exists (ID: {user.id})")
            else:
                # Create new user
                user = User(
                    email="test@example.com",
                    created_at=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"   ✅ Created user (ID: {user.id})")
            
            # Store or update Meta token in OAuthToken table
            from meta_ads_mcp.core.models import OAuthToken
            oauth_token = db.query(OAuthToken).filter_by(
                user_id=user.id,
                provider="meta"
            ).first()
            
            if oauth_token:
                # Update existing token
                if oauth_token.access_token != meta_token:
                    oauth_token.access_token = meta_token
                    oauth_token.updated_at = datetime.utcnow()
                    db.commit()
                    print(f"   ✅ Updated Meta OAuth token")
                else:
                    print(f"   ✅ Meta OAuth token already up to date")
            else:
                # Create new OAuth token
                oauth_token = OAuthToken(
                    user_id=user.id,
                    provider="meta",
                    access_token=meta_token,
                    updated_at=datetime.utcnow()
                )
                db.add(oauth_token)
                db.commit()
                print(f"   ✅ Created Meta OAuth token")
    
    except Exception as e:
        print(f"   ❌ Failed to create/update user: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Generate PAT for user
    print("\n4. Generating Personal Access Token (PAT)...")
    try:
        with get_db() as db:
            user = db.query(User).filter_by(email="test@example.com").first()
            
            # Check if user already has a PAT
            existing_pat = db.query(PersonalAccessToken).filter_by(
                user_id=user.id,
                is_active=True
            ).first()
            
            if existing_pat:
                print(f"   ✅ Active PAT already exists")
                print(f"   PAT ID: {existing_pat.id}")
                print(f"   Prefix: {existing_pat.token_prefix}")
                print(f"   Created: {existing_pat.created_at}")
                print(f"   \n   ⚠️  You need to use the original token that was shown when created")
                print(f"   If you don't have it, you'll need to create a new one")
            else:
                # Generate new PAT
                full_token, prefix, token_hash = generate_pat()
                
                # Create PAT record
                pat = PersonalAccessToken(
                    user_id=user.id,
                    name="Test PAT",
                    token_prefix=prefix,
                    token_hash=token_hash,
                    expires_at=datetime.utcnow() + timedelta(days=90),
                    created_at=datetime.utcnow()
                )
                db.add(pat)
                db.commit()
                db.refresh(pat)
                
                print(f"   ✅ Generated new PAT")
                print(f"   PAT ID: {pat.id}")
                print(f"   Prefix: {prefix}")
                print()
                print("=" * 60)
                print("🔐 IMPORTANT: Save this token - it won't be shown again!")
                print("=" * 60)
                print()
                print(f"   {full_token}")
                print()
                print("=" * 60)
    
    except Exception as e:
        print(f"   ❌ Failed to generate PAT: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n5. Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Copy the PAT token shown above")
    print("2. Start the server:")
    print("   python -m meta_ads_mcp --transport streamable-http --port 8080")
    print()
    print("3. Test PAT authentication with curl:")
    print("   curl -X POST http://localhost:8080/mcp/v1/ \\")
    print("     -H 'Authorization: Bearer YOUR_PAT_TOKEN' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "jsonrpc": "2.0",')
    print('       "method": "tools/list",')
    print('       "id": 1')
    print("     }'")
    print()
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
