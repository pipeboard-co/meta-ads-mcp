#!/usr/bin/env python3
"""
HTTP-to-stdio proxy for Meta Ads MCP.
This creates a stateless HTTP server that launches stdio MCP servers per request.
Works perfectly for hosting and is what Cursor expects for HTTP transport.
"""

import os
import json
import asyncio
import subprocess
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

# Set environment variables
os.environ.setdefault("META_APP_ID", "665587869862344")
os.environ.setdefault("META_APP_SECRET", "2eebb6109153f476f9df8625d673917e")
os.environ.setdefault("POSTGRES_URL", "postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")


async def call_stdio_mcp(request_data: dict, pat_token: str) -> dict:
    """
    Call the stdio MCP server with a request and return the response.
    This launches a subprocess for each request (stateless).
    """
    try:
        # Set up environment with PAT token
        env = os.environ.copy()
        env["MCP_PAT_TOKEN"] = pat_token
        
        # Launch the stdio MCP server
        process = await asyncio.create_subprocess_exec(
            "python3",
            "/Users/naveengarhwal/meta-ads-mcp-1/run_mcp_stdio.py",
            pat_token,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        # Send the request
        request_json = json.dumps(request_data) + "\n"
        stdout, stderr = await asyncio.wait_for(
            process.communicate(request_json.encode()),
            timeout=30.0  # 30 second timeout
        )
        
        # Parse response
        if stdout:
            response = json.loads(stdout.decode().strip())
            return response
        else:
            error_msg = stderr.decode() if stderr else "No response from MCP server"
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {error_msg}"
                }
            }
            
    except asyncio.TimeoutError:
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "error": {
                "code": -32603,
                "message": "Request timeout"
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


async def mcp_endpoint(request: Request):
    """Main MCP endpoint - proxies to stdio server."""
    try:
        # Extract PAT token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Missing or invalid Authorization header"
                }
            }, status_code=401)
        
        pat_token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Parse request body
        request_data = await request.json()
        
        # Call stdio MCP server
        response = await call_stdio_mcp(request_data, pat_token)
        
        return JSONResponse(response)
        
    except json.JSONDecodeError:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        }, status_code=400)
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }, status_code=500)


async def health_check(request: Request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "ok",
        "service": "meta-ads-mcp",
        "transport": "http-to-stdio-proxy",
        "auth": "PAT via Authorization header"
    })


# Create the Starlette app
app = Starlette(
    debug=True,
    routes=[
        Route("/mcp", mcp_endpoint, methods=["POST"]),
        Route("/health", health_check, methods=["GET"]),
    ]
)

print("=" * 70)
print("🚀 Meta Ads MCP - HTTP-to-stdio Proxy")
print("=" * 70)
print("  URL: http://0.0.0.0:8080/mcp")
print("  Auth: PAT tokens via Authorization: Bearer <token>")
print("  Health: http://0.0.0.0:8080/health")
print("  Mode: Stateless (launches stdio server per request)")
print("=" * 70)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

