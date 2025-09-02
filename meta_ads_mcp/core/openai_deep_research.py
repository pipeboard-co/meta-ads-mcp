"""OpenAI MCP Deep Research tools for Meta Ads API.

This module implements the required 'search' and 'fetch' tools for OpenAI's 
ChatGPT Deep Research feature, providing access to Meta Ads data in the format 
expected by ChatGPT.

The tools expose Meta Ads data (accounts, campaigns, ads, etc.) as searchable 
and fetchable records for ChatGPT Deep Research analysis.
"""

import json
import re
from typing import List, Dict, Any, Optional
from .api import meta_api_tool, make_api_request
from .server import mcp_server
from .utils import logger


class MetaAdsDataManager:
    """Manages Meta Ads data for OpenAI MCP search and fetch operations"""
    
    def __init__(self):
        self._cache = {}
        logger.debug("MetaAdsDataManager initialized")
    
    async def _get_ad_accounts(self, access_token: str, limit: int = 200) -> List[Dict[str, Any]]:
        """Get ad accounts data"""
        try:
            endpoint = "me/adaccounts"
            params = {
                "fields": "id,name,account_id,account_status,amount_spent,balance,currency,business_city,business_country_code",
                "limit": limit
            }
            
            data = await make_api_request(endpoint, access_token, params)
            
            if "data" in data:
                return data["data"]
            return []
        except Exception as e:
            logger.error(f"Error fetching ad accounts: {e}")
            return []
    
    async def _get_campaigns(self, access_token: str, account_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get campaigns data for an account"""
        try:
            endpoint = f"{account_id}/campaigns"
            params = {
                "fields": "id,name,status,objective,daily_budget,lifetime_budget,start_time,stop_time,created_time,updated_time",
                "limit": limit
            }
            
            data = await make_api_request(endpoint, access_token, params)
            
            if "data" in data:
                return data["data"]
            return []
        except Exception as e:
            logger.error(f"Error fetching campaigns for {account_id}: {e}")
            return []
    
    async def _get_ads(self, access_token: str, account_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get ads data for an account"""
        try:
            endpoint = f"{account_id}/ads"
            params = {
                "fields": "id,name,status,creative,targeting,bid_amount,created_time,updated_time",
                "limit": limit
            }
            
            data = await make_api_request(endpoint, access_token, params)
            
            if "data" in data:
                return data["data"]
            return []
        except Exception as e:
            logger.error(f"Error fetching ads for {account_id}: {e}")
            return []
    
    async def _get_pages_for_account(self, access_token: str, account_id: str) -> List[Dict[str, Any]]:
        """Get pages associated with an account"""
        try:
            # Import the page discovery function from ads module
            from .ads import _discover_pages_for_account
            
            # Ensure account_id has the 'act_' prefix
            if not account_id.startswith("act_"):
                account_id = f"act_{account_id}"
            
            page_discovery_result = await _discover_pages_for_account(account_id, access_token)
            
            if not page_discovery_result.get("success"):
                return []
            
            # Return page data in a consistent format
            return [{
                "id": page_discovery_result["page_id"],
                "name": page_discovery_result.get("page_name", "Unknown"),
                "source": page_discovery_result.get("source", "unknown"),
                "account_id": account_id
            }]
        except Exception as e:
            logger.error(f"Error fetching pages for {account_id}: {e}")
            return []
    
    async def _get_businesses(self, access_token: str, user_id: str = "me", limit: int = 25) -> List[Dict[str, Any]]:
        """Get businesses accessible by the current user"""
        try:
            endpoint = f"{user_id}/businesses"
            params = {
                "fields": "id,name,created_time,verification_status",
                "limit": limit
            }
            
            data = await make_api_request(endpoint, access_token, params)
            
            if "data" in data:
                return data["data"]
            return []
        except Exception as e:
            logger.error(f"Error fetching businesses: {e}")
            return []
    
    async def search_records(self, query: str, access_token: str) -> List[str]:
        """Search Meta Ads data and return matching record IDs
        
        Args:
            query: Search query string
            access_token: Meta API access token
            
        Returns:
            List of record IDs that match the query
        """
        logger.info(f"Searching Meta Ads data with query: {query}")
        
        # Normalize query for matching
        query_lower = query.lower()
        query_terms = re.findall(r'\w+', query_lower)
        
        matching_ids = []
        
        try:
            # Search ad accounts
            accounts = await self._get_ad_accounts(access_token, limit=200)
            for account in accounts:
                account_text = f"{account.get('name', '')} {account.get('id', '')} {account.get('account_status', '')} {account.get('business_city', '')} {account.get('business_country_code', '')}".lower()
                
                if any(term in account_text for term in query_terms):
                    record_id = f"account:{account['id']}"
                    matching_ids.append(record_id)
                    
                    # Cache the account data
                    self._cache[record_id] = {
                        "id": record_id,
                        "type": "account",
                        "title": f"Ad Account: {account.get('name', 'Unnamed Account')}",
                        "text": f"Meta Ads Account {account.get('name', 'Unnamed')} (ID: {account.get('id', 'N/A')}) - Status: {account.get('account_status', 'Unknown')}, Currency: {account.get('currency', 'Unknown')}, Spent: ${account.get('amount_spent', 0)}, Balance: ${account.get('balance', 0)}",
                        "metadata": {
                            "account_id": account.get('id'),
                            "account_name": account.get('name'),
                            "status": account.get('account_status'),
                            "currency": account.get('currency'),
                            "business_location": f"{account.get('business_city', '')}, {account.get('business_country_code', '')}".strip(', '),
                            "data_type": "meta_ads_account"
                        },
                        "raw_data": account
                    }
                    
                    # Also search campaigns for this account if it matches
                    campaigns = await self._get_campaigns(access_token, account['id'], limit=10)
                    for campaign in campaigns:
                        campaign_text = f"{campaign.get('name', '')} {campaign.get('objective', '')} {campaign.get('status', '')}".lower()
                        
                        if any(term in campaign_text for term in query_terms):
                            campaign_record_id = f"campaign:{campaign['id']}"
                            matching_ids.append(campaign_record_id)
                            
                            # Cache the campaign data
                            self._cache[campaign_record_id] = {
                                "id": campaign_record_id,
                                "type": "campaign",
                                "title": f"Campaign: {campaign.get('name', 'Unnamed Campaign')}",
                                "text": f"Meta Ads Campaign {campaign.get('name', 'Unnamed')} (ID: {campaign.get('id', 'N/A')}) - Objective: {campaign.get('objective', 'Unknown')}, Status: {campaign.get('status', 'Unknown')}, Daily Budget: ${campaign.get('daily_budget', 'Not set')}, Account: {account.get('name', 'Unknown')}",
                                "metadata": {
                                    "campaign_id": campaign.get('id'),
                                    "campaign_name": campaign.get('name'),
                                    "objective": campaign.get('objective'),
                                    "status": campaign.get('status'),
                                    "account_id": account.get('id'),
                                    "account_name": account.get('name'),
                                    "data_type": "meta_ads_campaign"
                                },
                                "raw_data": campaign
                            }
            
            # If query specifically mentions "ads" or "ad", also search individual ads
            if any(term in ['ad', 'ads', 'advertisement', 'creative'] for term in query_terms):
                for account in accounts[:3]:  # Limit to first 3 accounts for performance
                    ads = await self._get_ads(access_token, account['id'], limit=10)
                    for ad in ads:
                        ad_text = f"{ad.get('name', '')} {ad.get('status', '')}".lower()
                        
                        if any(term in ad_text for term in query_terms):
                            ad_record_id = f"ad:{ad['id']}"
                            matching_ids.append(ad_record_id)
                            
                            # Cache the ad data
                            self._cache[ad_record_id] = {
                                "id": ad_record_id,
                                "type": "ad",
                                "title": f"Ad: {ad.get('name', 'Unnamed Ad')}",
                                "text": f"Meta Ad {ad.get('name', 'Unnamed')} (ID: {ad.get('id', 'N/A')}) - Status: {ad.get('status', 'Unknown')}, Bid Amount: ${ad.get('bid_amount', 'Not set')}, Account: {account.get('name', 'Unknown')}",
                                "metadata": {
                                    "ad_id": ad.get('id'),
                                    "ad_name": ad.get('name'),
                                    "status": ad.get('status'),
                                    "account_id": account.get('id'),
                                    "account_name": account.get('name'),
                                    "data_type": "meta_ads_ad"
                                },
                                "raw_data": ad
                            }
            
            # If query specifically mentions "page" or "pages", also search pages
            if any(term in ['page', 'pages', 'facebook page'] for term in query_terms):
                for account in accounts[:5]:  # Limit to first 5 accounts for performance
                    pages = await self._get_pages_for_account(access_token, account['id'])
                    for page in pages:
                        page_text = f"{page.get('name', '')} {page.get('source', '')}".lower()
                        
                        if any(term in page_text for term in query_terms):
                            page_record_id = f"page:{page['id']}"
                            matching_ids.append(page_record_id)
                            
                            # Cache the page data
                            self._cache[page_record_id] = {
                                "id": page_record_id,
                                "type": "page",
                                "title": f"Facebook Page: {page.get('name', 'Unnamed Page')}",
                                "text": f"Facebook Page {page.get('name', 'Unnamed')} (ID: {page.get('id', 'N/A')}) - Source: {page.get('source', 'Unknown')}, Account: {account.get('name', 'Unknown')}",
                                "metadata": {
                                    "page_id": page.get('id'),
                                    "page_name": page.get('name'),
                                    "source": page.get('source'),
                                    "account_id": account.get('id'),
                                    "account_name": account.get('name'),
                                    "data_type": "meta_ads_page"
                                },
                                "raw_data": page
                            }
            
            # If query specifically mentions "business" or "businesses", also search businesses
            if any(term in ['business', 'businesses', 'company', 'companies'] for term in query_terms):
                businesses = await self._get_businesses(access_token, limit=25)
                for business in businesses:
                    business_text = f"{business.get('name', '')} {business.get('verification_status', '')}".lower()
                    
                    if any(term in business_text for term in query_terms):
                        business_record_id = f"business:{business['id']}"
                        matching_ids.append(business_record_id)
                        
                        # Cache the business data
                        self._cache[business_record_id] = {
                            "id": business_record_id,
                            "type": "business",
                            "title": f"Business: {business.get('name', 'Unnamed Business')}",
                            "text": f"Meta Business {business.get('name', 'Unnamed')} (ID: {business.get('id', 'N/A')}) - Created: {business.get('created_time', 'Unknown')}, Verification: {business.get('verification_status', 'Unknown')}",
                            "metadata": {
                                "business_id": business.get('id'),
                                "business_name": business.get('name'),
                                "created_time": business.get('created_time'),
                                "verification_status": business.get('verification_status'),
                                "data_type": "meta_ads_business"
                            },
                            "raw_data": business
                        }
        
        except Exception as e:
            logger.error(f"Error during search operation: {e}")
            # Return empty list on error, but don't raise exception
            return []
        
        logger.info(f"Search completed. Found {len(matching_ids)} matching records")
        return matching_ids[:50]  # Limit to 50 results for performance
    
    def fetch_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a cached record by ID
        
        Args:
            record_id: The record ID to fetch
            
        Returns:
            Record data or None if not found
        """
        logger.info(f"Fetching record: {record_id}")
        
        record = self._cache.get(record_id)
        if record:
            logger.debug(f"Record found in cache: {record['type']}")
            return record
        else:
            logger.warning(f"Record not found in cache: {record_id}")
            return None


# Global data manager instance
_data_manager = MetaAdsDataManager()


@mcp_server.tool()
@meta_api_tool
async def search(
    query: str,
    access_token: Optional[str] = None
) -> str:
    """
    Search through Meta Ads data and return matching record IDs.
    It searches across ad accounts, campaigns, ads, pages, and businesses to find relevant records
    based on the provided query.
    
    Args:
        query: Search query string to find relevant Meta Ads records
        access_token: Meta API access token (optional - will use cached token if not provided)
        
    Returns:
        JSON response with list of matching record IDs
        
    Example Usage:
        search(query="active campaigns")
        search(query="account spending")
        search(query="facebook ads performance")
        search(query="facebook pages")
        search(query="user businesses")
    """
    if not query:
        return json.dumps({
            "error": "query parameter is required",
            "ids": []
        }, indent=2)
    
    try:
        # Use the data manager to search records
        matching_ids = await _data_manager.search_records(query, access_token)
        
        response = {
            "ids": matching_ids,
            "query": query,
            "total_results": len(matching_ids)
        }
        
        logger.info(f"Search successful. Query: '{query}', Results: {len(matching_ids)}")
        return json.dumps(response, indent=2)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in search tool: {error_msg}")
        
        return json.dumps({
            "error": "Failed to search Meta Ads data",
            "details": error_msg,
            "ids": [],
            "query": query
        }, indent=2)


@mcp_server.tool()
async def fetch(
    id: str
) -> str:
    """
    Fetch complete record data by ID.
    It retrieves the full data for a specific record identified by its ID.
    
    Args:
        id: The record ID to fetch (format: "type:id", e.g., "account:act_123456")
        
    Returns:
        JSON response with complete record data including id, title, text, and metadata
        
    Example Usage:
        fetch(id="account:act_123456789")
        fetch(id="campaign:23842588888640185")
        fetch(id="ad:23842614006130185")
        fetch(id="page:123456789")
    """
    if not id:
        return json.dumps({
            "error": "id parameter is required"
        }, indent=2)
    
    try:
        # Use the data manager to fetch the record
        record = _data_manager.fetch_record(id)
        
        if record:
            logger.info(f"Record fetched successfully: {id}")
            return json.dumps(record, indent=2)
        else:
            logger.warning(f"Record not found: {id}")
            return json.dumps({
                "error": f"Record not found: {id}",
                "id": id
            }, indent=2)
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in fetch tool: {error_msg}")
        
        return json.dumps({
            "error": "Failed to fetch record",
            "details": error_msg,
            "id": id
        }, indent=2) 