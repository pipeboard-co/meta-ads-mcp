"""Account-related functionality for Meta Ads API."""

import json
from typing import Optional, Dict, Any
from .api import meta_api_tool, make_api_request
from .server import mcp_server

# Currencies that have no sub-units (i.e., are not denominated in cents).
# Meta API returns amount_spent and balance as integers in the smallest currency
# unit, which is cents for most currencies but the base unit for these.
_ZERO_DECIMAL_CURRENCIES = {
    "BIF", "CLP", "DJF", "GNF", "JPY", "KMF", "KRW", "MGA",
    "PYG", "RWF", "UGX", "VND", "VUV", "XAF", "XOF", "XPF",
}


def _cents_to_currency(amount, currency: str) -> str:
    """Convert a Meta API monetary value (cents) to a currency-unit string.

    Meta returns amount_spent and balance as integers representing the smallest
    currency unit (cents for USD/EUR/GBP, base unit for zero-decimal currencies
    like JPY). This converts to the human-readable decimal amount.
    """
    try:
        amount_int = int(amount)
    except (TypeError, ValueError):
        return str(amount)
    if currency.upper() in _ZERO_DECIMAL_CURRENCIES:
        return str(amount_int)
    return f"{amount_int / 100:.2f}"


def _normalize_account_monetary_fields(account: dict) -> dict:
    """Convert amount_spent and balance from cents to currency units in-place."""
    currency = account.get("currency", "USD")
    for field in ("amount_spent", "balance"):
        if field in account:
            account[field] = _cents_to_currency(account[field], currency)
    return account


@mcp_server.tool()
@meta_api_tool
async def get_ad_accounts(access_token: Optional[str] = None, user_id: str = "me", limit: int = 200) -> str:
    """
    Get ad accounts accessible by a user.

    amount_spent and balance are returned in currency units (e.g. USD dollars),
    not cents.

    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        user_id: Meta user ID or "me" for the current user
        limit: Maximum number of accounts to return (default: 200)
    """
    endpoint = f"{user_id}/adaccounts"
    params = {
        "fields": "id,name,account_id,account_status,amount_spent,balance,currency,age,business_city,business_country_code",
        "limit": limit
    }

    data = await make_api_request(endpoint, access_token, params)

    if "data" in data:
        data["data"] = [_normalize_account_monetary_fields(acc) for acc in data["data"]]

    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_account_info(account_id: str, access_token: Optional[str] = None) -> str:
    """
    Get detailed information about a specific ad account.
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not account_id:
        return {
            "error": {
                "message": "Account ID is required",
                "details": "Please specify an account_id parameter",
                "example": "Use account_id='act_123456789' or account_id='123456789'"
            }
        }
    
    # Ensure account_id has the 'act_' prefix for API compatibility
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    
    # Try to get the account info directly first
    endpoint = f"{account_id}"
    params = {
        "fields": "id,name,account_id,account_status,amount_spent,balance,currency,age,business_city,business_country_code,timezone_name"
    }
    
    data = await make_api_request(endpoint, access_token, params)

    # Check if the API request returned an error
    if "error" in data:
        # If access was denied, provide helpful error message with accessible accounts
        if "access" in str(data.get("error", {})).lower() or "permission" in str(data.get("error", {})).lower():
            # Get list of accessible accounts for helpful error message
            accessible_endpoint = "me/adaccounts"
            accessible_params = {
                "fields": "id,name,account_id,account_status,amount_spent,balance,currency,age,business_city,business_country_code",
                "limit": 50
            }
            accessible_accounts_data = await make_api_request(accessible_endpoint, access_token, accessible_params)
            
            if "data" in accessible_accounts_data:
                accessible_accounts = [
                    {"id": acc["id"], "name": acc["name"]} 
                    for acc in accessible_accounts_data["data"][:10]  # Show first 10
                ]
                return {
                    "error": {
                        "message": f"Account {account_id} is not accessible to your user account",
                        "details": "This account either doesn't exist or you don't have permission to access it",
                        "accessible_accounts": accessible_accounts,
                        "total_accessible_accounts": len(accessible_accounts_data["data"]),
                        "suggestion": "Try using one of the accessible account IDs listed above"
                    }
                }
        
        # Return the original error for non-permission related issues
        return data
    
    _normalize_account_monetary_fields(data)

    # Add DSA requirement detection
    if "business_country_code" in data:
        european_countries = ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "IE", "DK", "SE", "FI", "NO"]
        if data["business_country_code"] in european_countries:
            data["dsa_required"] = True
            data["dsa_compliance_note"] = "This account is subject to European DSA (Digital Services Act) requirements"
        else:
            data["dsa_required"] = False
            data["dsa_compliance_note"] = "This account is not subject to European DSA requirements"
    
    return data 