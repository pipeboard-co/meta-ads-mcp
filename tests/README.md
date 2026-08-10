# Meta Ads MCP Tests

This directory contains integration tests for the Meta Ads MCP HTTP transport functionality.

## Test Structure

- `test_http_transport.py` - Comprehensive HTTP transport integration tests
- `conftest.py` - Pytest configuration and shared fixtures
- `__init__.py` - Python package marker

## Running Tests

### Prerequisites

1. **Start the MCP server:**
   ```bash
   python -m meta_ads_mcp --transport streamable-http --port 8080 --host localhost
   ```

2. **Install test dependencies:**
   ```bash
   pip install pytest requests
   ```

### Running with pytest (recommended)

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_http_transport.py -v

# Run with custom server URL
MCP_TEST_SERVER_URL=http://localhost:9000 python -m pytest tests/ -v
```

### Running directly

```bash
# Run the main integration test
python tests/test_http_transport.py

# Or from project root
python -m tests.test_http_transport
```

## What the Tests Validate

### ✅ HTTP Transport Layer
- Server availability and responsiveness
- JSON-RPC 2.0 protocol compliance
- Proper HTTP status codes and headers
- Request/response format validation

### ✅ MCP Protocol Compliance
- `initialize` method - Server capability exchange
- `tools/list` method - Tool discovery and enumeration
- `tools/call` method - Tool execution with parameters
- Error handling and edge cases

### ✅ Authentication Integration
- **No Authentication** - Proper rejection of unauthenticated requests
- **Bearer Token** - Primary authentication method (`Authorization: Bearer <meta token>`)
- **Meta App ID** - Fallback authentication method (`X-META-APP-ID`)
- **Multiple Auth Methods** - Priority handling (bearer token takes precedence)

### ✅ Tool Execution
- All 26 Meta Ads tools accessible via HTTP
- Authentication context properly passed to tools
- Expected behavior with test tokens (authentication required responses)

## Test Scenarios

The test suite runs multiple authentication scenarios:

1. **No Authentication**: Tests that tools properly require authentication
2. **Bearer Token**: Tests the primary authentication path
3. **Custom Meta App**: Tests the fallback authentication path  
4. **Both Methods**: Tests authentication priority (bearer token preferred)

## Expected Results

With **test tokens** (used in automated tests):
- ✅ HTTP transport: All requests succeed (200 OK)
- ✅ MCP protocol: All methods work correctly
- ✅ Authentication: Headers processed and passed to tools
- ✅ Tool responses: "Authentication Required" (expected with invalid tokens)

With **real tokens** (production usage):
- ✅ All of the above PLUS actual Meta Ads data returned

## Continuous Integration

These tests are designed to be run in CI/CD pipelines:

```bash
# Start server in background
python -m meta_ads_mcp --transport streamable-http --port 8080 &
SERVER_PID=$!

# Wait for server startup
sleep 3

# Run tests
python -m pytest tests/ -v --tb=short

# Cleanup
kill $SERVER_PID
```

## Troubleshooting

**Server not running:**
```
SKIPPED [1] tests/conftest.py:25: MCP server not running at http://localhost:8080
```
→ Start the server first: `python -m meta_ads_mcp --transport streamable-http`

**Connection refused:**
```
requests.exceptions.ConnectionError: ('Connection aborted.', ...)
```
→ Check that the server is running on the expected port

**406 Not Acceptable:**
```
❌ Request failed: 406
```
→ Ensure proper Accept headers are being sent (handled automatically by test suite)

## Contributing

When adding new tests:

1. **Follow naming convention**: `test_*.py` for pytest discovery
2. **Use fixtures**: Leverage existing fixtures in `conftest.py`
3. **Test both success and failure cases**
4. **Document expected behavior** with test tokens vs real tokens
5. **Keep tests isolated**: Each test should be independent 