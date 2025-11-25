#!/usr/bin/env node

/**
 * Gateway MCP - Meta Gateway Infrastructure Management
 * 
 * Entry point for the Model Context Protocol server that manages
 * Meta CAPI Gateway and Signals Gateway infrastructure.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { logger } from './utils/logger.js';
import { setupTools } from './tools/index.js';
import { setupResources } from './resources/index.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Main function to start the MCP server
 */
async function main() {
  logger.info('Starting Gateway MCP Server...');

  // Create MCP server instance
  const server = new Server(
    {
      name: 'gateway-mcp',
      version: '0.1.0',
    },
    {
      capabilities: {
        tools: {},
        resources: {},
      },
    }
  );

  // Set up tools
  setupTools(server);

  // Set up resources
  setupResources(server);

  // Error handling
  server.onerror = (error) => {
    logger.error('Server error:', error);
  };

  // Connect to transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  logger.info('Gateway MCP Server running on stdio');
  logger.info('Waiting for requests...');
}

// Start the server
main().catch((error) => {
  logger.error('Failed to start server:', error);
  process.exit(1);
});
