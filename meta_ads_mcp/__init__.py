"""
Meta Ads MCP - Python Package

This package provides a Meta Ads MCP integration
"""

from meta_ads_mcp.core.server import main

__version__ = "1.0.20"

__all__ = [
    'get_ad_accounts',
    'get_account_info',
    'get_campaigns',
    'get_campaign_details',
    'create_campaign',
    'get_adsets',
    'get_adset_details',
    'update_adset',
    'get_ads',
    'get_ad_details',
    'get_ad_creatives',
    'get_ad_image',
    'update_ad',
    'get_insights',
    # 'get_login_link' is conditionally exported via core.__all__
    'login_cli',
    'main',
    'search_interests',
    'get_interest_suggestions',
    'estimate_audience_size',
    'search_behaviors',
    'search_demographics',
    'search_geo_locations'
]

# Import key functions to make them available at package level
from .core import (
    get_ad_accounts,
    get_account_info,
    get_campaigns,
    get_campaign_details,
    create_campaign,
    get_adsets,
    get_adset_details,
    update_adset,
    get_ads,
    get_ad_details,
    get_ad_creatives,
    get_ad_image,
    update_ad,
    get_insights,
    login_cli,
    main,
    search_interests,
    get_interest_suggestions,
    estimate_audience_size,
    search_behaviors,
    search_demographics,
    search_geo_locations
)

# Define a main function to be used as a package entry point
def entrypoint():
    """Main entry point for the package when invoked with uvx."""
    return main() 

# Re-export main for direct access
main = main 