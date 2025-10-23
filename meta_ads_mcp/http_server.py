"""Custom HTTP server for stateless MCP over HTTP - Direct Tool Registration."""

import os
import json
import inspect
from typing import Dict, Any
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from meta_ads_mcp.core.http_auth_integration import AuthInjectionMiddleware, FastMCPAuthIntegration
from meta_ads_mcp.core.utils import logger

# Import all tool functions directly from their modules
from meta_ads_mcp.core.accounts import (
    get_ad_accounts,
    get_account_info,
)

from meta_ads_mcp.core.campaigns import (
    get_campaigns,
    get_campaign_details,
    create_campaign,
    update_campaign,
)

from meta_ads_mcp.core.adsets import (
    get_adsets,
    get_adset_details,
    create_adset,
    update_adset,
)

from meta_ads_mcp.core.ads import (
    get_ads,
    get_ad_details,
    create_ad,
    update_ad,
    get_ad_creatives,
    get_ad_image,
    upload_ad_image,
    create_ad_creative,
    update_ad_creative,
    search_pages_by_name,
    get_account_pages,
)

from meta_ads_mcp.core.insights import (
    get_insights,
)

from meta_ads_mcp.core.authentication import (
    get_login_link,
)

# Ads library is conditionally enabled
try:
    from meta_ads_mcp.core.ads_library import search_ads_archive
    HAS_ADS_LIBRARY = True
except (ImportError, AttributeError):
    search_ads_archive = None
    HAS_ADS_LIBRARY = False

from meta_ads_mcp.core.budget_schedules import (
    create_budget_schedule,
)

from meta_ads_mcp.core.targeting import (
    search_interests,
    get_interest_suggestions,
    estimate_audience_size,
    search_behaviors,
    search_demographics,
    search_geo_locations,
)

from meta_ads_mcp.core.openai_deep_research import (
    search,
    fetch,
)

# Create tool registry
TOOLS = {
    # Account tools
    "get_ad_accounts": get_ad_accounts,
    "get_account_info": get_account_info,
    "search_pages_by_name": search_pages_by_name,
    "get_account_pages": get_account_pages,
    
    # Campaign tools
    "get_campaigns": get_campaigns,
    "get_campaign_details": get_campaign_details,
    "create_campaign": create_campaign,
    "update_campaign": update_campaign,
    
    # Adset tools
    "get_adsets": get_adsets,
    "get_adset_details": get_adset_details,
    "create_adset": create_adset,
    "update_adset": update_adset,
    
    # Ad tools
    "get_ads": get_ads,
    "get_ad_details": get_ad_details,
    "create_ad": create_ad,
    "update_ad": update_ad,
    "get_ad_creatives": get_ad_creatives,
    "get_ad_image": get_ad_image,
    "upload_ad_image": upload_ad_image,
    "create_ad_creative": create_ad_creative,
    "update_ad_creative": update_ad_creative,
    
    # Insights
    "get_insights": get_insights,
    
    # Other
    "get_login_link": get_login_link,
    "create_budget_schedule": create_budget_schedule,
    
    # Targeting
    "search_interests": search_interests,
    "get_interest_suggestions": get_interest_suggestions,
    "estimate_audience_size": estimate_audience_size,
    "search_behaviors": search_behaviors,
    "search_demographics": search_demographics,
    "search_geo_locations": search_geo_locations,
    
    # OpenAI Research
    "search": search,
    "fetch": fetch,
}

# Add ads library search if available
if HAS_ADS_LIBRARY and search_ads_archive:
    TOOLS["search_ads_archive"] = search_ads_archive
    logger.info("✅ Ads Library search enabled")
else:
    logger.info("⚠️ Ads Library search disabled (set META_ADS_DISABLE_ADS_LIBRARY to enable)")

logger.info(f"✅ Registered {len(TOOLS)} tools directly")


def get_tool_schema(func):
    """Extract schema from function signature and docstring."""
    sig = inspect.signature(func)
    doc = (func.__doc__ or "").strip()
    
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        # Skip access_token - we inject it from auth
        if param_name in ['access_token', 'self', 'cls']:
            continue
        
        # Infer type from annotation or default value
        param_type = "string"  # Default
        
        if param.annotation != inspect.Parameter.empty:
            annotation = str(param.annotation)
            if 'int' in annotation:
                param_type = "integer"
            elif 'bool' in annotation:
                param_type = "boolean"
            elif 'List' in annotation or 'list' in annotation:
                param_type = "array"
            elif 'Dict' in annotation or 'dict' in annotation:
                param_type = "object"
        
        properties[param_name] = {
            "type": param_type,
            "description": f"Parameter: {param_name}"
        }
        
        # Mark as required if no default value
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


# Generate tool schemas
TOOL_SCHEMAS = []
for name, func in TOOLS.items():
    schema = {
        "name": name,
        "description": (func.__doc__ or f"Execute {name}").strip().split('\n')[0],  # First line only
        "inputSchema": get_tool_schema(func)
    }
    TOOL_SCHEMAS.append(schema)

logger.info(f"✅ Generated schemas for {len(TOOL_SCHEMAS)} tools")


class MCPHTTPHandler:
    """Handles HTTP requests and routes them to MCP tools."""
    
    async def handle_mcp_request(self, request: Request) -> JSONResponse:
        """Handle MCP JSON-RPC requests."""
        try:
            body = await request.json()
            method = body.get("method")
            params = body.get("params", {})
            request_id = body.get("id")
            
            logger.info(f"📥 MCP Request: method={method}, id={request_id}")
            
            if method == "initialize":
                return await self.handle_initialize(request_id, params)
            elif method == "tools/list":
                return await self.handle_tools_list(request_id)
            elif method == "tools/call":
                return await self.handle_tool_call(request_id, params)
            elif method == "prompts/list":
                return await self.handle_prompts_list(request_id)
            elif method and method.startswith("notifications/"):
                # Handle notifications (no response required per MCP spec)
                logger.info(f"📢 Notification received: {method}")
                return JSONResponse({"jsonrpc": "2.0"}, status_code=200)
            else:
                logger.warning(f"❌ Unknown method: {method}")
                logger.warning(f"   Request ID: {request_id}")
                logger.warning(f"   Params: {params}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }, status_code=404)
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": "error",
                "error": {
                    "code": -32700,
                    "message": "Parse error: Invalid JSON"
                }
            }, status_code=400)
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}", exc_info=True)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": "error",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }, status_code=500)
    
    async def handle_initialize(self, request_id, params):
        """Handle MCP initialize request."""
        logger.info("🔄 Handling initialize request")
        
        # Get client protocol version if provided
        client_protocol = params.get("protocolVersion", "2024-11-05") if params else "2024-11-05"
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "prompts": {
                        "listChanged": False
                    }
                },
                "serverInfo": {
                    "name": "meta-ads-mcp",
                    "version": "1.0.0"
                },
                "_meta": {
                    "availableTools": len(TOOLS),
                    "clientProtocol": client_protocol
                }
            }
        })
    
    async def handle_tools_list(self, request_id):
        """Handle tools/list request."""
        logger.info(f"📋 Listing {len(TOOL_SCHEMAS)} tools")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": TOOL_SCHEMAS
            }
        })
    
    async def handle_prompts_list(self, request_id):
        """Handle prompts/list request."""
        logger.info("📝 Listing prompts (none available)")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": []
            }
        })
    
    async def handle_tool_call(self, request_id, params):
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Missing tool name"
                }
            }, status_code=400)
        
        if tool_name not in TOOLS:
            logger.warning(f"Tool not found: {tool_name}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }, status_code=404)
        
        try:
            logger.info(f"🔧 Executing tool: {tool_name}")
            logger.debug(f"   Arguments: {arguments}")
            
            # Get the tool function
            tool_func = TOOLS[tool_name]
            
            # Get Meta access token from context (set by middleware)
            meta_token = FastMCPAuthIntegration.get_auth_token()
            logger.debug(f"   Using Meta token: {meta_token[:20]}..." if meta_token else "   No Meta token")
            
            # Inject access_token if the function accepts it
            sig = inspect.signature(tool_func)
            if 'access_token' in sig.parameters:
                arguments['access_token'] = meta_token
            
            # Execute the tool
            result = await tool_func(**arguments)
            
            # Format result
            if isinstance(result, dict):
                result_str = json.dumps(result, indent=2)
            elif isinstance(result, str):
                # Already a string
                result_str = result
            else:
                result_str = str(result)
            
            logger.info(f"✅ Tool executed successfully: {tool_name}")
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_str
                        }
                    ]
                }
            })
            
        except TypeError as e:
            logger.error(f"Invalid arguments for {tool_name}: {e}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Invalid arguments: {str(e)}"
                }
            }, status_code=400)
        except Exception as e:
            logger.error(f"Tool execution error: {e}", exc_info=True)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }, status_code=500)


handler = MCPHTTPHandler()


async def mcp_endpoint(request: Request):
    """Main MCP endpoint."""
    return await handler.handle_mcp_request(request)


async def health_check(request: Request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "ok",
        "service": "meta-ads-mcp",
        "tools": len(TOOLS),
        "transport": "streamable-http-json",
        "auth": "PAT via Authorization header"
    })


# Create the Starlette app
app = Starlette(
    debug=True,
    routes=[
        Route("/mcp", mcp_endpoint, methods=["POST", "OPTIONS"]),
        Route("/health", health_check, methods=["GET", "OPTIONS"]),
    ]
)

# Add CORS middleware (must be added before auth middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add authentication middleware
logger.info("🔐 Adding AuthInjectionMiddleware to app...")
app.add_middleware(AuthInjectionMiddleware)
logger.info("✅ AuthInjectionMiddleware added successfully")

logger.info("=" * 80)
logger.info("✅ Meta Ads MCP HTTP Server initialized (Option 1: Direct Tool Registration)")
logger.info(f"   📦 Tools registered: {len(TOOLS)}")
logger.info(f"   🔐 Auth: PAT tokens via Authorization: Bearer header")
logger.info(f"   🌐 Transport: Stateless JSON/HTTP")
logger.info(f"   🔒 Middleware: AuthInjectionMiddleware + CORSMiddleware")
logger.info("=" * 80)
