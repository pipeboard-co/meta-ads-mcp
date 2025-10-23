"""
Example: Backend Service with External Auth and Token Storage

This demonstrates the recommended architecture where:
1. YOUR backend handles Meta OAuth and stores tokens
2. MCP server is stateless and receives tokens per request
3. Complete separation of concerns

Run this example:
    python examples/backend_service_example.py
"""

import asyncio
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json


# ============================================================================
# PART 1: Your Backend - Token Storage
# ============================================================================

@dataclass
class StoredMetaToken:
    """Represents a Meta token stored in YOUR database"""
    user_id: int
    access_token: str
    expires_at: datetime
    meta_user_id: str
    meta_user_name: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def days_until_expiry(self) -> int:
        """Days until token expires"""
        delta = self.expires_at - datetime.utcnow()
        return delta.days


class TokenDatabase:
    """
    Simulates YOUR database storing user tokens
    In production: Use PostgreSQL, MySQL, etc.
    """
    
    def __init__(self):
        self.tokens: Dict[int, StoredMetaToken] = {}
    
    def store_token(self, user_id: int, token_data: Dict) -> StoredMetaToken:
        """Store user's Meta token"""
        stored_token = StoredMetaToken(
            user_id=user_id,
            access_token=token_data['access_token'],
            expires_at=token_data['expires_at'],
            meta_user_id=token_data['meta_user_id'],
            meta_user_name=token_data['meta_user_name']
        )
        
        self.tokens[user_id] = stored_token
        print(f"✓ Stored token for user {user_id} (expires in {stored_token.days_until_expiry()} days)")
        return stored_token
    
    def get_token(self, user_id: int) -> Optional[StoredMetaToken]:
        """Retrieve user's Meta token"""
        token = self.tokens.get(user_id)
        
        if not token:
            print(f"✗ No token found for user {user_id}")
            return None
        
        if token.is_expired():
            print(f"✗ Token expired for user {user_id}")
            return None
        
        print(f"✓ Retrieved valid token for user {user_id}")
        return token
    
    def delete_token(self, user_id: int) -> bool:
        """Delete user's token (disconnect)"""
        if user_id in self.tokens:
            del self.tokens[user_id]
            print(f"✓ Deleted token for user {user_id}")
            return True
        return False


# ============================================================================
# PART 2: Your Backend - Meta OAuth Handler
# ============================================================================

class MetaOAuthHandler:
    """
    Handles Meta OAuth flow in YOUR backend
    This is YOUR code, not MCP server code
    """
    
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self) -> str:
        """Get URL to redirect user for Meta authorization"""
        scope = "ads_read,ads_management,business_management"
        return (
            f"https://www.facebook.com/v22.0/dialog/oauth?"
            f"client_id={self.app_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope={scope}"
        )
    
    def simulate_oauth_flow(self, user_id: int) -> Dict:
        """
        Simulate Meta OAuth flow
        In production: User clicks authorize, Meta redirects back with code
        """
        print(f"\n[OAuth Flow for User {user_id}]")
        print(f"1. User clicks: {self.get_authorization_url()}")
        print(f"2. User authorizes on Meta")
        print(f"3. Meta redirects to: {self.redirect_uri}?code=ABC123")
        print(f"4. Backend exchanges code for token")
        
        # Simulate token exchange
        # In production: POST to Meta's token endpoint
        return {
            'access_token': f'EAABwzLixnjYBO{user_id}ZCZCxyz123',
            'token_type': 'bearer',
            'expires_at': datetime.utcnow() + timedelta(days=60),
            'meta_user_id': f'meta_user_{user_id}',
            'meta_user_name': f'User {user_id}'
        }


# ============================================================================
# PART 3: Your Backend - API Endpoints
# ============================================================================

class YourBackendAPI:
    """
    YOUR backend API that users interact with
    Handles auth, stores tokens, calls MCP server
    """
    
    def __init__(self, token_db: TokenDatabase, mcp_server_url: str):
        self.token_db = token_db
        self.mcp_server_url = mcp_server_url
        self.oauth_handler = MetaOAuthHandler(
            app_id="YOUR_APP_ID",
            app_secret="YOUR_APP_SECRET",
            redirect_uri="https://your-backend.com/auth/callback"
        )
    
    async def connect_meta_account(self, user_id: int) -> Dict:
        """
        Endpoint: POST /api/meta/connect
        Initiates Meta OAuth and stores token
        """
        print(f"\n{'='*70}")
        print(f"User {user_id}: Connecting Meta Account")
        print(f"{'='*70}")
        
        # Simulate OAuth flow
        token_data = self.oauth_handler.simulate_oauth_flow(user_id)
        
        # Store token in YOUR database
        stored_token = self.token_db.store_token(user_id, token_data)
        
        return {
            'success': True,
            'message': 'Meta account connected',
            'meta_user': stored_token.meta_user_name,
            'expires_in_days': stored_token.days_until_expiry()
        }
    
    async def get_ad_accounts(self, user_id: int) -> Dict:
        """
        Endpoint: GET /api/meta-ads/accounts
        Gets user's ad accounts via MCP server
        """
        print(f"\n{'='*70}")
        print(f"User {user_id}: Getting Ad Accounts")
        print(f"{'='*70}")
        
        # 1. Get user's token from YOUR database
        token = self.token_db.get_token(user_id)
        
        if not token:
            return {
                'error': 'Meta account not connected',
                'action': 'Please connect your Meta account first'
            }
        
        # 2. Call MCP server with user's token
        print(f"→ Calling MCP server with user's token")
        result = await self._call_mcp_server(
            tool_name='get_ad_accounts',
            tool_args={'limit': 10},
            meta_token=token.access_token
        )
        
        print(f"✓ Received {len(result.get('accounts', []))} accounts from MCP server")
        return result
    
    async def get_campaigns(self, user_id: int, account_id: str) -> Dict:
        """
        Endpoint: GET /api/meta-ads/campaigns
        Gets campaigns for an account
        """
        print(f"\n{'='*70}")
        print(f"User {user_id}: Getting Campaigns for {account_id}")
        print(f"{'='*70}")
        
        # Get user's token
        token = self.token_db.get_token(user_id)
        
        if not token:
            return {'error': 'Meta account not connected'}
        
        # Call MCP server
        print(f"→ Calling MCP server")
        result = await self._call_mcp_server(
            tool_name='get_campaigns',
            tool_args={'account_id': account_id},
            meta_token=token.access_token
        )
        
        print(f"✓ Received campaigns from MCP server")
        return result
    
    async def _call_mcp_server(
        self,
        tool_name: str,
        tool_args: Dict,
        meta_token: str
    ) -> Dict:
        """
        Call MCP server with user's Meta token
        
        Key point: MCP server is STATELESS
        It receives the token in each request
        """
        payload = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'id': 1,
            'params': {
                'name': tool_name,
                'arguments': tool_args
            }
        }
        
        # Pass Meta token in header (NOT stored by MCP server)
        headers = {
            'Content-Type': 'application/json',
            'X-META-ACCESS-TOKEN': meta_token
        }
        
        # Simulate MCP server call
        # In production: requests.post(self.mcp_server_url, json=payload, headers=headers)
        return self._simulate_mcp_response(tool_name, tool_args, meta_token)
    
    def _simulate_mcp_response(self, tool_name: str, tool_args: Dict, token: str) -> Dict:
        """Simulate MCP server response"""
        if tool_name == 'get_ad_accounts':
            return {
                'accounts': [
                    {'id': 'act_123', 'name': 'Main Ad Account'},
                    {'id': 'act_456', 'name': 'Test Account'}
                ],
                'token_used': token[:20] + '...'
            }
        elif tool_name == 'get_campaigns':
            return {
                'campaigns': [
                    {'id': 'camp_1', 'name': 'Summer Sale'},
                    {'id': 'camp_2', 'name': 'Product Launch'}
                ],
                'token_used': token[:20] + '...'
            }
        return {}


# ============================================================================
# PART 4: MCP Server (Stateless)
# ============================================================================

class StatelessMCPServer:
    """
    MCP Server - Completely stateless
    
    Key characteristics:
    - Does NOT store any tokens
    - Does NOT manage users
    - Receives token in each request
    - Validates and proxies to Meta API
    """
    
    def handle_request(self, headers: Dict[str, str], body: Dict) -> Dict:
        """
        Handle incoming request
        
        Expects: X-META-ACCESS-TOKEN header
        """
        print(f"\n[MCP Server] Received request")
        
        # Extract Meta token from header
        meta_token = headers.get('X-META-ACCESS-TOKEN')
        
        if not meta_token:
            print(f"[MCP Server] ✗ No token provided")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32001,
                    'message': 'Authentication required',
                    'data': 'Provide X-META-ACCESS-TOKEN header'
                },
                'id': body.get('id')
            }
        
        print(f"[MCP Server] ✓ Token received: {meta_token[:20]}...")
        
        # Validate token (call Meta API)
        if not self._validate_token(meta_token):
            print(f"[MCP Server] ✗ Invalid token")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32002,
                    'message': 'Invalid token'
                },
                'id': body.get('id')
            }
        
        print(f"[MCP Server] ✓ Token validated with Meta API")
        
        # Execute tool
        method = body.get('method')
        if method == 'tools/call':
            params = body.get('params', {})
            tool_name = params.get('name')
            tool_args = params.get('arguments', {})
            
            print(f"[MCP Server] → Calling Meta API: {tool_name}")
            result = self._execute_tool(tool_name, tool_args, meta_token)
            print(f"[MCP Server] ✓ Returning results")
            
            return {
                'jsonrpc': '2.0',
                'result': result,
                'id': body.get('id')
            }
        
        return {'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'Method not found'}, 'id': body.get('id')}
    
    def _validate_token(self, token: str) -> bool:
        """Validate token with Meta API"""
        # In production: Call Meta Graph API /me endpoint
        # requests.get('https://graph.facebook.com/v22.0/me', headers={'Authorization': f'Bearer {token}'})
        return True  # Simulate success
    
    def _execute_tool(self, tool_name: str, tool_args: Dict, token: str) -> Dict:
        """Execute tool by calling Meta API"""
        # In production: Call actual Meta Graph API with token
        # This is where the real Meta API calls happen
        return {
            'message': f'Called Meta API with token',
            'tool': tool_name,
            'args': tool_args
        }


# ============================================================================
# DEMONSTRATION
# ============================================================================

async def demonstrate_architecture():
    """
    Demonstrate the complete architecture flow
    """
    print("\n" + "="*70)
    print("BACKEND SERVICE ARCHITECTURE DEMONSTRATION")
    print("="*70)
    print("\nArchitecture:")
    print("  User → Your Backend → MCP Server (stateless) → Meta API")
    print("         ↓")
    print("      Database (stores tokens)")
    print("="*70)
    
    # Initialize components
    token_db = TokenDatabase()
    mcp_server = StatelessMCPServer()
    your_backend = YourBackendAPI(
        token_db=token_db,
        mcp_server_url="http://localhost:8080/mcp"
    )
    
    # ========================================================================
    # Scenario 1: User 1 connects Meta account
    # ========================================================================
    
    print("\n" + "="*70)
    print("SCENARIO 1: User 1 Connects Meta Account")
    print("="*70)
    
    result = await your_backend.connect_meta_account(user_id=1)
    print(f"\nResult: {json.dumps(result, indent=2)}")
    
    # ========================================================================
    # Scenario 2: User 1 gets ad accounts
    # ========================================================================
    
    print("\n" + "="*70)
    print("SCENARIO 2: User 1 Gets Ad Accounts")
    print("="*70)
    
    result = await your_backend.get_ad_accounts(user_id=1)
    print(f"\nResult: {json.dumps(result, indent=2)}")
    
    # ========================================================================
    # Scenario 3: User 2 tries without connecting (should fail)
    # ========================================================================
    
    print("\n" + "="*70)
    print("SCENARIO 3: User 2 Tries Without Connecting")
    print("="*70)
    
    result = await your_backend.get_ad_accounts(user_id=2)
    print(f"\nResult: {json.dumps(result, indent=2)}")
    
    # ========================================================================
    # Scenario 4: User 2 connects and gets data
    # ========================================================================
    
    print("\n" + "="*70)
    print("SCENARIO 4: User 2 Connects and Gets Data")
    print("="*70)
    
    await your_backend.connect_meta_account(user_id=2)
    result = await your_backend.get_ad_accounts(user_id=2)
    print(f"\nResult: {json.dumps(result, indent=2)}")
    
    # ========================================================================
    # Scenario 5: Concurrent requests from multiple users
    # ========================================================================
    
    print("\n" + "="*70)
    print("SCENARIO 5: Concurrent Requests from Multiple Users")
    print("="*70)
    
    tasks = [
        your_backend.get_ad_accounts(user_id=1),
        your_backend.get_campaigns(user_id=1, account_id='act_123'),
        your_backend.get_ad_accounts(user_id=2),
    ]
    
    results = await asyncio.gather(*tasks)
    print(f"\n✓ All {len(results)} concurrent requests completed successfully")
    
    # ========================================================================
    # Summary
    # ========================================================================
    
    print("\n" + "="*70)
    print("ARCHITECTURE SUMMARY")
    print("="*70)
    print("""
✅ YOUR BACKEND RESPONSIBILITIES:
   - User authentication (login/signup)
   - Meta OAuth flow
   - Token storage in database
   - Token refresh logic
   - User authorization
   - Rate limiting

✅ MCP SERVER RESPONSIBILITIES:
   - Receive Meta token per request
   - Validate token with Meta API
   - Proxy requests to Meta Graph API
   - Return formatted results
   - NO token storage
   - NO user management

✅ KEY BENEFITS:
   - Complete separation of concerns
   - MCP server is stateless (scales horizontally)
   - You control all user data
   - Flexible authentication
   - Easy to maintain

✅ SECURITY:
   - Tokens encrypted in your database
   - Token validation on every request
   - No shared state between users
   - Each user isolated
    """)
    print("="*70)


if __name__ == "__main__":
    asyncio.run(demonstrate_architecture())
