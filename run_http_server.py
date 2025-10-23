#!/usr/bin/env python3
"""Run the Meta Ads MCP HTTP server."""

import os
import uvicorn

# Set environment variables
os.environ.setdefault("META_APP_ID", "665587869862344")
os.environ.setdefault("META_APP_SECRET", "2eebb6109153f476f9df8625d673917e")
os.environ.setdefault("POSTGRES_URL", "postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

from meta_ads_mcp.http_server import app

print("=" * 70)
print("🚀 Meta Ads MCP - Remote Server")
print("=" * 70)
print("  URL: http://0.0.0.0:8080/mcp")
print("  Auth: PAT tokens via Authorization: Bearer <token>")
print("  Health: http://0.0.0.0:8080/health")
print("=" * 70)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")



