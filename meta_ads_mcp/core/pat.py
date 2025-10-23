"""Personal Access Token (PAT) utilities."""

import secrets
import base64
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from .utils import logger

# Password hasher for PAT verification
ph = PasswordHasher()

def generate_pat() -> tuple[str, str, str]:
    """Generate a new Personal Access Token.
    
    Returns:
        tuple: (full_token, prefix, token_hash)
            - full_token: The complete token to return to user (show once)
            - prefix: First 8 chars for lookup/display
            - token_hash: Argon2 hash to store in database
    """
    # Generate 32 random bytes
    random_bytes = secrets.token_bytes(32)
    
    # Encode as base64url (URL-safe, no padding)
    token_part = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
    
    # Create full token with prefix
    full_token = f"pat_{token_part}"
    
    # Extract prefix (first 8 chars including 'pat_')
    prefix = full_token[:8]
    
    # Hash the full token for storage
    token_hash = ph.hash(full_token)
    
    logger.debug(f"Generated PAT with prefix: {prefix}")
    
    return full_token, prefix, token_hash


def verify_pat(raw_token: str, token_hash: str) -> bool:
    """Verify a PAT against its stored hash.
    
    Supports both Argon2 (backend-generated) and SHA256 (frontend-generated) hashes.
    
    Args:
        raw_token: The raw token from the user
        token_hash: The stored hash (Argon2 or SHA256)
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Try Argon2 first (starts with $argon2)
        if token_hash.startswith('$argon2'):
            ph.verify(token_hash, raw_token)
            return True
        else:
            # Try SHA256 (hex string, 64 characters)
            import hashlib
            computed_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            return computed_hash == token_hash
    except VerifyMismatchError:
        return False
    except Exception as e:
        logger.error(f"Error verifying PAT: {e}")
        return False


def extract_prefix(token: str) -> str:
    """Extract the prefix from a token for lookup.
    
    Args:
        token: Full token string
    
    Returns:
        str: First 12 characters (prefix) to match frontend storage
    """
    return token[:12] if len(token) >= 12 else token
