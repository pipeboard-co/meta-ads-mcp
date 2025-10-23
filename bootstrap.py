#!/usr/bin/env python3
"""Bootstrap script for Meta Ads MCP multi-tenant setup.

This script helps initialize the database and create the first user.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Set up environment before imports
load_dotenv()
if not os.environ.get("DATABASE_URL"):
    print("⚠️  DATABASE_URL not set, using default Neon DB")
    os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

if not os.environ.get("BOOTSTRAP_TOKEN"):
    print("⚠️  BOOTSTRAP_TOKEN not set, using default (change for production!)")
    os.environ["BOOTSTRAP_TOKEN"] = "bootstrap_secret_change_me"

def main():
    """Bootstrap the database and create first user."""
    print("=" * 60)
    print("Meta Ads MCP - Multi-Tenant Bootstrap")
    print("=" * 60)
    
    # Import after environment is set
    from meta_ads_mcp.core.db import init_db, get_db
    from meta_ads_mcp.core.models import User, PersonalAccessToken, OAuthToken
    from meta_ads_mcp.core.pat import generate_pat
    from sqlalchemy import select
    
    # Step 1: Initialize database
    print("\n[1/4] Initializing database...")
    try:
        init_db()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return 1
    
    # Step 2: Check for existing users
    print("\n[2/4] Checking for existing users...")
    try:
        with get_db() as db:
            user_count = db.execute(select(User)).scalars().all()
            if user_count:
                print(f"ℹ️  Found {len(user_count)} existing user(s)")
                response = input("Do you want to create another user? (y/n): ")
                if response.lower() != 'y':
                    print("Exiting...")
                    return 0
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return 1
    
    # Step 3: Create user
    print("\n[3/4] Creating new user...")
    email = input("Enter user email: ").strip()
    if not email:
        print("❌ Email is required")
        return 1
    
    user_id = None
    try:
        with get_db() as db:
            # Check if user exists
            existing = db.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()
            
            if existing:
                print(f"⚠️  User {email} already exists")
                user_id = existing.id
            else:
                user = User(email=email)
                db.add(user)
                db.commit()
                db.refresh(user)
                user_id = user.id
                print(f"✅ Created user: {email}")
                print(f"   User ID: {user_id}")
    
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return 1
    
    # Step 4: Create PAT
    print("\n[4/4] Creating Personal Access Token...")
    token_name = input(f"Enter token name (default: 'Bootstrap Token'): ").strip()
    if not token_name:
        token_name = "Bootstrap Token"
    
    full_token = None
    pat_id = None
    prefix = None
    
    try:
        with get_db() as db:
            # Generate PAT
            full_token, prefix, token_hash = generate_pat()
            
            pat = PersonalAccessToken(
                user_id=user_id,
                name=token_name,
                token_prefix=prefix,
                token_hash=token_hash
            )
            db.add(pat)
            db.commit()
            db.refresh(pat)
            pat_id = pat.id
            
            print(f"✅ Created PAT: {token_name}")
            print(f"   Token ID: {pat_id}")
            print(f"   Prefix: {prefix}")
    
    except Exception as e:
        print(f"❌ Error creating PAT: {e}")
        return 1
    
    # Display summary
    print("\n" + "=" * 60)
    print("✅ Bootstrap complete!")
    print("=" * 60)
    print(f"\nUser Email: {email}")
    print(f"User ID: {user_id}")
    print(f"\n🔑 Personal Access Token:")
    print(f"   {full_token}")
    print("\n⚠️  IMPORTANT: Save this token now! You won't see it again.")
    print("\n📋 Next steps:")
    print("1. Save your Meta access token:")
    print(f"   curl -X POST http://localhost:8080/v1/meta/token \\")
    print(f"     -H 'Authorization: Bearer {full_token}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"access_token\": \"YOUR_META_TOKEN\"}}'")
    print("\n2. Test your setup:")
    print(f"   curl http://localhost:8080/v1/me \\")
    print(f"     -H 'Authorization: Bearer {full_token}'")
    print("\n3. Use this token in Claude or other MCP clients:")
    print("   {")
    print('     "meta-ads": {')
    print('       "transport": "http",')
    print('       "url": "http://localhost:8080/mcp/stream",')
    print(f'       "headers": {{"Authorization": "Bearer {full_token}"}}')
    print('     }')
    print("   }")
    print("\n" + "=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
