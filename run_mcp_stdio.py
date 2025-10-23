#!/usr/bin/env python3
"""
Stdio wrapper for Meta Ads MCP server.
This allows Cursor to launch the MCP server as a command.
"""
import sys
import os

# Set environment variables
os.environ.setdefault("META_APP_ID", "665587869862344")
os.environ.setdefault("META_APP_SECRET", "2eebb6109153f476f9df8625d673917e")
os.environ.setdefault("POSTGRES_URL", "postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

# The PAT token will be provided by Cursor via environment variable
if len(sys.argv) > 1:
    os.environ["MCP_PAT_TOKEN"] = sys.argv[1]

from meta_ads_mcp.core.server import mcp_server

# Run in stdio mode (standard MCP transport)
mcp_server.run(transport="stdio")
