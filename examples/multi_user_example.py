"""
Example: Multi-User Backend Service Implementation

This example demonstrates how to refactor the Meta Ads MCP server
to support multiple concurrent users with isolated authentication.

Usage:
    python examples/multi_user_example.py
"""

import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time
import uuid


# ============================================================================
# STEP 1: User Authentication Context
# ============================================================================

@dataclass
class UserAuthContext:
    """
    Per-user authentication context.
    Each user gets their own instance with isolated state.
    """
    user_id: str
    pipeboard_token: str
    meta_access_token: Optional[str] = None
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
    
    def get_meta_token(self) -> Optional[str]:
        """Get Meta access token for this user"""
        # In real implementation, this would call Pipeboard API
        # with this user's specific token
        return self.meta_access_token
    
    def is_valid(self) -> bool:
        """Check if this user's authentication is valid"""
        # In real implementation, validate against Meta API
        return self.meta_access_token is not None


# ============================================================================
# STEP 2: Request Handler with User Isolation
# ============================================================================

class MultiUserRequestHandler:
    """
    Handles requests from multiple users with proper isolation.
    No shared state between users.
    """
    
    def __init__(self):
        """Initialize handler - no user-specific state here"""
        self.request_count = 0  # Global counter is OK
    
    async def handle_request(
        self, 
        user_token: str,
        user_id: str,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle a request from a specific user.
        
        Args:
            user_token: User's Pipeboard API token
            user_id: User identifier
            tool_name: MCP tool to execute
            tool_args: Tool arguments
            
        Returns:
            Tool execution result
        """
        # Create user-specific context for THIS request only
        user_context = UserAuthContext(
            user_id=user_id,
            pipeboard_token=user_token
        )
        
        # Get Meta token for this user
        meta_token = await self._get_meta_token_for_user(user_context)
        user_context.meta_access_token = meta_token
        
        # Validate user's authentication
        if not user_context.is_valid():
            return {
                "error": "Authentication failed",
                "user_id": user_id
            }
        
        # Execute tool with user's context
        result = await self._execute_tool(tool_name, tool_args, user_context)
        
        self.request_count += 1
        return result
    
    async def _get_meta_token_for_user(self, user_context: UserAuthContext) -> Optional[str]:
        """
        Get Meta access token for a specific user.
        This creates a NEW Pipeboard auth manager for each user.
        """
        # Simulate Pipeboard API call with user's token
        print(f"[{user_context.user_id}] Fetching Meta token from Pipeboard...")
        
        # In real implementation:
        # from meta_ads_mcp.core.pipeboard_auth import PipeboardAuthManager
        # auth_manager = PipeboardAuthManager()
        # auth_manager.api_token = user_context.pipeboard_token
        # return auth_manager.get_access_token()
        
        # Simulate different tokens for different users
        await asyncio.sleep(0.1)  # Simulate API call
        return f"meta_token_for_{user_context.user_id}"
    
    async def _execute_tool(
        self, 
        tool_name: str, 
        tool_args: Dict[str, Any],
        user_context: UserAuthContext
    ) -> Dict[str, Any]:
        """
        Execute MCP tool with user-specific context.
        
        Args:
            tool_name: Tool to execute
            tool_args: Tool arguments
            user_context: User's authentication context
            
        Returns:
            Tool execution result
        """
        print(f"[{user_context.user_id}] Executing tool: {tool_name}")
        
        # Simulate tool execution with user's token
        await asyncio.sleep(0.2)  # Simulate API call to Meta
        
        return {
            "tool": tool_name,
            "user_id": user_context.user_id,
            "result": f"Data for {user_context.user_id}",
            "meta_token_used": user_context.meta_access_token[:20] + "..."
        }


# ============================================================================
# STEP 3: HTTP Server with Per-Request Authentication
# ============================================================================

class MultiUserHTTPServer:
    """
    HTTP server that handles multiple users with per-request authentication.
    """
    
    def __init__(self):
        self.handler = MultiUserRequestHandler()
    
    def extract_user_from_headers(self, headers: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Extract user authentication from HTTP headers.
        
        Args:
            headers: HTTP request headers
            
        Returns:
            Dict with user_id and user_token, or None if not found
        """
        # Check for Bearer token
        auth_header = headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:].strip()
            user_id = headers.get('X-User-ID', 'anonymous')
            return {
                'user_id': user_id,
                'user_token': token
            }
        
        return None
    
    async def handle_http_request(
        self,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle HTTP request with user authentication.
        
        Args:
            headers: HTTP request headers
            body: Request body (JSON-RPC format)
            
        Returns:
            JSON-RPC response
        """
        # Extract user authentication
        user_auth = self.extract_user_from_headers(headers)
        
        if not user_auth:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32001,
                    'message': 'Authentication required',
                    'data': 'Provide Bearer token in Authorization header'
                },
                'id': body.get('id')
            }
        
        # Extract tool call from JSON-RPC request
        if body.get('method') != 'tools/call':
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32601,
                    'message': 'Method not found'
                },
                'id': body.get('id')
            }
        
        params = body.get('params', {})
        tool_name = params.get('name')
        tool_args = params.get('arguments', {})
        
        # Handle request with user-specific context
        result = await self.handler.handle_request(
            user_token=user_auth['user_token'],
            user_id=user_auth['user_id'],
            tool_name=tool_name,
            tool_args=tool_args
        )
        
        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': body.get('id')
        }


# ============================================================================
# STEP 4: Demonstration
# ============================================================================

async def simulate_concurrent_users():
    """
    Simulate multiple users making concurrent requests.
    This demonstrates proper user isolation.
    """
    print("=" * 70)
    print("Multi-User Backend Service Example")
    print("=" * 70)
    print()
    
    server = MultiUserHTTPServer()
    
    # Simulate 3 different users making concurrent requests
    users = [
        {
            'user_id': 'alice',
            'token': 'pipeboard_token_alice_xyz123',
            'tool': 'get_ad_accounts'
        },
        {
            'user_id': 'bob',
            'token': 'pipeboard_token_bob_abc456',
            'tool': 'get_campaigns'
        },
        {
            'user_id': 'charlie',
            'token': 'pipeboard_token_charlie_def789',
            'tool': 'get_ad_accounts'
        }
    ]
    
    print("Simulating concurrent requests from 3 users...\n")
    
    # Create concurrent requests
    tasks = []
    for user in users:
        headers = {
            'Authorization': f"Bearer {user['token']}",
            'X-User-ID': user['user_id']
        }
        body = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'id': str(uuid.uuid4()),
            'params': {
                'name': user['tool'],
                'arguments': {'limit': 10}
            }
        }
        
        task = server.handle_http_request(headers, body)
        tasks.append(task)
    
    # Execute all requests concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start_time
    
    print(f"\nAll requests completed in {elapsed:.2f} seconds\n")
    print("=" * 70)
    print("Results:")
    print("=" * 70)
    
    # Display results
    for i, (user, result) in enumerate(zip(users, results), 1):
        print(f"\n{i}. User: {user['user_id']}")
        print(f"   Tool: {user['tool']}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
        else:
            print(f"   Result: {result['result']}")
    
    print("\n" + "=" * 70)
    print("Key Points:")
    print("=" * 70)
    print("✓ Each user has isolated authentication context")
    print("✓ No shared state between users")
    print("✓ Concurrent requests don't interfere with each other")
    print("✓ Each user gets their own Meta access token")
    print("✓ Stateless design - scales horizontally")
    print("=" * 70)


async def demonstrate_session_isolation():
    """
    Demonstrate that user sessions are properly isolated.
    """
    print("\n\n" + "=" * 70)
    print("Session Isolation Test")
    print("=" * 70)
    print()
    
    handler = MultiUserRequestHandler()
    
    # User 1 makes a request
    print("User 1 (Alice) makes request...")
    result1 = await handler.handle_request(
        user_token="token_alice",
        user_id="alice",
        tool_name="get_ad_accounts",
        tool_args={}
    )
    
    # User 2 makes a request at the same time
    print("User 2 (Bob) makes request...")
    result2 = await handler.handle_request(
        user_token="token_bob",
        user_id="bob",
        tool_name="get_ad_accounts",
        tool_args={}
    )
    
    print("\nResults:")
    print(f"Alice got: {result1['meta_token_used']}")
    print(f"Bob got: {result2['meta_token_used']}")
    
    # Verify isolation
    assert result1['meta_token_used'] != result2['meta_token_used']
    assert result1['user_id'] == 'alice'
    assert result2['user_id'] == 'bob'
    
    print("\n✓ Session isolation verified - users got different tokens!")
    print("=" * 70)


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all demonstrations"""
    await simulate_concurrent_users()
    await demonstrate_session_isolation()
    
    print("\n\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("""
This example demonstrates the key changes needed for multi-user support:

1. USER CONTEXT: Create UserAuthContext for each request
   - No singleton auth managers
   - Each user gets their own token

2. REQUEST HANDLER: Pass user context through all function calls
   - No global state
   - Proper isolation between users

3. HTTP SERVER: Extract user auth from headers
   - Stateless per-request authentication
   - Scales horizontally

4. TESTING: Verify concurrent access works correctly
   - No race conditions
   - Each user gets their own data

Next Steps:
- Implement UserAuthContext in your codebase
- Refactor tools to accept user_context parameter
- Update server.py to extract auth from headers
- Add tests for concurrent user access
- Consider database-backed token storage for production
    """)
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
