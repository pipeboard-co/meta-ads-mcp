"""Report generation functionality for Meta Ads API."""

import json
import os
from typing import Optional, Dict, Any, List, Union
from .api import meta_api_tool
from .server import mcp_server


# Only register the generate_report function if the environment variable is set
ENABLE_REPORT_GENERATION = bool(os.environ.get("META_ADS_ENABLE_REPORTS", ""))

if ENABLE_REPORT_GENERATION:
    @mcp_server.tool()
    async def generate_report(
        account_id: str,
        access_token: Optional[str] = None,
        report_type: str = "account",
        time_range: str = "last_30d",
        campaign_ids: Optional[List[str]] = None,
        export_format: str = "pdf",
        report_name: Optional[str] = None,
        include_sections: Optional[List[str]] = None,
        breakdowns: Optional[List[str]] = None,
        comparison_period: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive Meta Ads performance reports.

        **This is a premium feature available with Pipeboard Pro.**
        
        Args:
            account_id: Meta Ads account ID (format: act_XXXXXXXXX)
            access_token: Meta API access token (optional - will use cached token if not provided)
            report_type: Type of report to generate (account, campaign, comparison)
            time_range: Time period for the report (e.g., 'last_30d', 'last_7d', 'this_month')
            campaign_ids: Specific campaign IDs (required for campaign/comparison reports)
            export_format: Output format for the report (pdf, json, html)
            report_name: Custom name for the report (auto-generated if not provided)
            include_sections: Specific sections to include in the report
            breakdowns: Audience breakdown dimensions (age, gender, country, etc.)
            comparison_period: Time period for comparison analysis
        """
        
        # Validate required parameters
        if not account_id:
            return json.dumps({
                "error": "invalid_parameters",
                "message": "Account ID is required",
                "details": {
                    "required_parameter": "account_id",
                    "format": "act_XXXXXXXXX"
                }
            }, indent=2)
        
        # For campaign and comparison reports, campaign_ids are required
        if report_type in ["campaign", "comparison"] and not campaign_ids:
            return json.dumps({
                "error": "invalid_parameters", 
                "message": f"Campaign IDs are required for {report_type} reports",
                "details": {
                    "required_parameter": "campaign_ids",
                    "format": "Array of campaign ID strings"
                }
            }, indent=2)

        # Return premium feature upgrade message
        return json.dumps({
            "error": "premium_feature_required",
            "message": "Professional report generation is a premium feature",
            "details": {
                "feature": "Automated PDF Report Generation",
                "description": "Create professional client-ready reports with performance insights, recommendations, and white-label branding",
                "benefits": [
                    "Executive summary with key metrics",
                    "Performance breakdowns and trends", 
                    "Audience insights and recommendations",
                    "Professional PDF formatting",
                    "White-label branding options",
                    "Campaign comparison analysis",
                    "Creative performance insights",
                    "Automated scheduling options"
                ],
                "upgrade_url": "https://pipeboard.co/upgrade",
                "contact_email": "info@pipeboard.co",
                "early_access": "Contact us for early access and special pricing"
            },
            "request_parameters": {
                "account_id": account_id,
                "report_type": report_type,
                "time_range": time_range,
                "export_format": export_format,
                "campaign_ids": campaign_ids or [],
                "include_sections": include_sections or [],
                "breakdowns": breakdowns or []
            },
            "preview": {
                "available_data": {
                    "account_name": f"Account {account_id}",
                    "campaigns_count": len(campaign_ids) if campaign_ids else "All campaigns",
                    "time_range": time_range,
                    "estimated_report_pages": 8 if report_type == "account" else 6,
                    "report_format": export_format.upper()
                },
                "sample_metrics": {
                    "total_spend": "$12,450",
                    "total_impressions": "2.3M", 
                    "total_clicks": "45.2K",
                    "average_cpc": "$0.85",
                    "average_cpm": "$15.20",
                    "click_through_rate": "1.96%",
                    "roas": "4.2x"
                },
                "available_sections": [
                    "executive_summary",
                    "performance_overview", 
                    "campaign_breakdown",
                    "audience_insights",
                    "creative_performance",
                    "recommendations",
                    "appendix"
                ],
                "supported_breakdowns": [
                    "age",
                    "gender", 
                    "country",
                    "region",
                    "placement",
                    "device_platform",
                    "publisher_platform"
                ]
            }
        }, indent=2) 