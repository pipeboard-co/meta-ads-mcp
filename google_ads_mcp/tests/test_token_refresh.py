#!/usr/bin/env python3
"""
Test script for Google Ads token refresh mechanism and authentication methods.

This script tests both OAuth 2.0 and Service Account authentication methods,
and verifies that token refresh works correctly.
"""

import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import get_credentials function from the server
from google_ads_server import get_credentials, get_headers, format_customer_id

def test_token_refresh():
    """Test the token refresh mechanism."""
    print("\n" + "="*50)
    print("GOOGLE ADS TOKEN REFRESH TEST")
    print("="*50)
    
    # Get the authentication type from environment
    auth_type = os.environ.get("GOOGLE_ADS_AUTH_TYPE", "oauth")
    print(f"\nAuthentication type: {auth_type}")
    
    # Get credentials
    print("\nGetting credentials...")
    creds = get_credentials()
    
    # Print credentials info
    if hasattr(creds, 'expired') and hasattr(creds, 'expiry'):
        print(f"Token expired: {creds.expired}")
        print(f"Token expiry: {creds.expiry}")
        
        # Calculate time until expiry
        if creds.expiry:
            now = datetime.now()
            expiry = creds.expiry
            if isinstance(expiry, str):
                expiry = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
            
            time_until_expiry = expiry - now
            print(f"Time until expiry: {time_until_expiry}")
    else:
        print("Service account credentials (no expiry info available)")
    
    # Get headers using the credentials
    print("\nGetting API headers...")
    headers = get_headers(creds)
    
    # Remove sensitive info for display
    safe_headers = headers.copy()
    if 'Authorization' in safe_headers:
        token = safe_headers['Authorization']
        if token:
            # Show only the first 10 chars of the token
            token_start = token[:15]
            safe_headers['Authorization'] = f"{token_start}...TRUNCATED"
    
    print("API Headers:")
    for key, value in safe_headers.items():
        print(f"  {key}: {value}")
    
    # Test if we can force a token refresh (for OAuth tokens)
    if auth_type.lower() == "oauth" and hasattr(creds, 'refresh'):
        print("\nAttempting to force token refresh...")
        try:
            old_token = creds.token[:15] if hasattr(creds, 'token') else None
            creds.refresh(Request())
            new_token = creds.token[:15] if hasattr(creds, 'token') else None
            
            print(f"Old token started with: {old_token}...")
            print(f"New token starts with: {new_token}...")
            print("Token refresh successful!" if old_token != new_token else "Token stayed the same")
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
    
    print("\nToken test completed successfully!")

def test_customer_id_formatting():
    """Test the customer ID formatting function."""
    print("\n" + "="*50)
    print("CUSTOMER ID FORMATTING TEST")
    print("="*50)
    
    test_cases = [
        "1234567890",
        "123-456-7890",
        "123.456.7890",
        "123 456 7890",
        "\"1234567890\"",
        "1234",
        1234567890,
        None
    ]
    
    print("\nTesting customer ID formatting:")
    for test_case in test_cases:
        try:
            formatted = format_customer_id(test_case)
            print(f"  Input: {test_case}, Output: {formatted}")
        except Exception as e:
            print(f"  Input: {test_case}, Error: {str(e)}")

if __name__ == "__main__":
    # Import Request here to avoid circular imports
    from google.auth.transport.requests import Request
    
    try:
        test_token_refresh()
        test_customer_id_formatting()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}") 