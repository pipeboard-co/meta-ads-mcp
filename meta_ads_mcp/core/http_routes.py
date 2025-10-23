"""HTTP routes for user and token management."""

import os
import json
from datetime import datetime
from typing import Optional
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from sqlalchemy import select
from .db import get_db
from .models import User, OAuthToken, PersonalAccessToken
from .pat import generate_pat, extract_prefix
from .utils import logger

# Bootstrap token for admin operations
BOOTSTRAP_TOKEN = os.environ.get("BOOTSTRAP_TOKEN", "bootstrap_secret_change_me")


def check_bootstrap_auth(request: Request) -> bool:
    """Check if request has valid bootstrap token."""
    token = request.headers.get("X-BOOTSTRAP-TOKEN")
    return token == BOOTSTRAP_TOKEN


def get_current_user_from_request(request: Request) -> Optional[User]:
    """Get current user from request state (set by middleware)."""
    return getattr(request.state, "user", None)


async def health_check(request: Request):
    """Health check endpoint."""
    return JSONResponse({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


async def create_user(request: Request):
    """Create a new user (bootstrap protected).
    
    Body:
        {
            "email": "user@example.com",
            "password": "optional"
        }
    """
    if not check_bootstrap_auth(request):
        return JSONResponse(
            {"error": "Bootstrap token required", "header": "X-BOOTSTRAP-TOKEN"},
            status_code=401
        )
    
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        if not email:
            return JSONResponse({"error": "Email is required"}, status_code=400)
        
        with get_db() as db:
            # Check if user exists
            existing = db.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()
            
            if existing:
                return JSONResponse(
                    {"error": "User with this email already exists"},
                    status_code=409
                )
            
            # Create user
            user = User(email=email, password_hash=password)  # TODO: hash password
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Created user: {user.email}")
            
            return JSONResponse({
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            }, status_code=201)
    
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def create_pat(request: Request):
    """Create a Personal Access Token.
    
    Body:
        {
            "user_id": "uuid",  # Required if using bootstrap auth
            "name": "My Token",
            "scopes": ["ads.read", "ads.write"]  # Optional
        }
    """
    try:
        body = await request.json()
        
        # Get user - either from PAT auth or bootstrap + user_id
        user = get_current_user_from_request(request)
        
        if not user:
            # Check bootstrap auth
            if not check_bootstrap_auth(request):
                return JSONResponse(
                    {"error": "Authentication required"},
                    status_code=401
                )
            
            user_id = body.get("user_id")
            if not user_id:
                return JSONResponse(
                    {"error": "user_id required when using bootstrap auth"},
                    status_code=400
                )
            
            with get_db() as db:
                user = db.get(User, user_id)
                if not user:
                    return JSONResponse(
                        {"error": "User not found"},
                        status_code=404
                    )
        
        name = body.get("name", "API Token")
        scopes = body.get("scopes", [])
        
        # Generate PAT
        full_token, prefix, token_hash = generate_pat()
        
        with get_db() as db:
            # Refresh user in this session
            user = db.merge(user)
            
            pat = PersonalAccessToken(
                user_id=user.id,
                name=name,
                token_prefix=prefix,
                token_hash=token_hash,
                scopes=json.dumps(scopes) if scopes else None
            )
            db.add(pat)
            db.commit()
            db.refresh(pat)
            
            logger.info(f"Created PAT '{name}' for user {user.email}")
            
            return JSONResponse({
                "id": pat.id,
                "name": pat.name,
                "token": full_token,  # Show once!
                "prefix": prefix,
                "created_at": pat.created_at.isoformat(),
                "warning": "Save this token now. You won't be able to see it again."
            }, status_code=201)
    
    except Exception as e:
        logger.error(f"Error creating PAT: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def list_pats(request: Request):
    """List Personal Access Tokens for current user."""
    user = get_current_user_from_request(request)
    
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    try:
        with get_db() as db:
            user = db.merge(user)
            pats = db.execute(
                select(PersonalAccessToken)
                .where(PersonalAccessToken.user_id == user.id)
                .order_by(PersonalAccessToken.created_at.desc())
            ).scalars().all()
            
            return JSONResponse({
                "tokens": [
                    {
                        "id": pat.id,
                        "name": pat.name,
                        "prefix": pat.prefix,
                        "created_at": pat.created_at.isoformat(),
                        "last_used_at": pat.last_used_at.isoformat() if pat.last_used_at else None,
                        "is_active": pat.is_active
                    }
                    for pat in pats
                ]
            })
    
    except Exception as e:
        logger.error(f"Error listing PATs: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def revoke_pat(request: Request):
    """Revoke a Personal Access Token."""
    user = get_current_user_from_request(request)
    
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    pat_id = request.path_params.get("id")
    
    try:
        with get_db() as db:
            user = db.merge(user)
            pat = db.get(PersonalAccessToken, pat_id)
            
            if not pat or pat.user_id != user.id:
                return JSONResponse({"error": "Token not found"}, status_code=404)
            
            pat.revoked_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Revoked PAT {pat.name} for user {user.email}")
            
            return JSONResponse({
                "message": "Token revoked successfully",
                "id": pat.id,
                "revoked_at": pat.revoked_at.isoformat()
            })
    
    except Exception as e:
        logger.error(f"Error revoking PAT: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def save_meta_token(request: Request):
    """Save Meta access token for current user.
    
    Body:
        {
            "access_token": "...",
            "refresh_token": "...",  # Optional
            "expires_at": "2024-12-31T23:59:59",  # Optional ISO format
            "scopes": "ads_read,ads_management",  # Optional
            "account_id": "act_123456"  # Optional
        }
    """
    user = get_current_user_from_request(request)
    
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    try:
        body = await request.json()
        access_token = body.get("access_token")
        
        if not access_token:
            return JSONResponse({"error": "access_token is required"}, status_code=400)
        
        refresh_token = body.get("refresh_token")
        scopes = body.get("scopes")
        account_id = body.get("account_id")
        
        # Parse expires_at if provided
        expires_at = None
        if body.get("expires_at"):
            try:
                expires_at = datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))
            except:
                pass
        
        with get_db() as db:
            user = db.merge(user)
            
            # Check for existing token
            existing = db.execute(
                select(OAuthToken).where(
                    OAuthToken.user_id == user.id,
                    OAuthToken.provider == "meta"
                )
            ).scalar_one_or_none()
            
            if existing:
                # Update existing
                existing.access_token = access_token
                existing.refresh_token = refresh_token
                existing.expires_at = expires_at
                existing.scopes = scopes
                existing.account_id = account_id
                existing.updated_at = datetime.utcnow()
                token = existing
            else:
                # Create new
                token = OAuthToken(
                    user_id=user.id,
                    provider="meta",
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=expires_at,
                    scopes=scopes,
                    account_id=account_id
                )
                db.add(token)
            
            db.commit()
            db.refresh(token)
            
            logger.info(f"Saved Meta token for user {user.email}")
            
            return JSONResponse({
                "message": "Meta token saved successfully",
                "provider": "meta",
                "updated_at": token.updated_at.isoformat()
            })
    
    except Exception as e:
        logger.error(f"Error saving Meta token: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def whoami(request: Request):
    """Get current user info and connected providers."""
    user = get_current_user_from_request(request)
    
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    try:
        with get_db() as db:
            user = db.merge(user)
            
            # Get connected providers
            tokens = db.execute(
                select(OAuthToken).where(OAuthToken.user_id == user.id)
            ).scalars().all()
            
            providers = [
                {
                    "provider": token.provider,
                    "account_id": token.account_id,
                    "scopes": token.scopes,
                    "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                    "updated_at": token.updated_at.isoformat()
                }
                for token in tokens
            ]
            
            return JSONResponse({
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "providers": providers
            })
    
    except Exception as e:
        logger.error(f"Error in whoami: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


# Route definitions
routes = [
    Route("/health", health_check, methods=["GET"]),
    Route("/v1/users", create_user, methods=["POST"]),
    Route("/v1/pats", create_pat, methods=["POST"]),
    Route("/v1/pats", list_pats, methods=["GET"]),
    Route("/v1/pats/{id}", revoke_pat, methods=["DELETE"]),
    Route("/v1/meta/token", save_meta_token, methods=["POST"]),
    Route("/v1/me", whoami, methods=["GET"]),
]
