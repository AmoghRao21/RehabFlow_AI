import hashlib
import hmac
import secrets
from typing import Optional

from fastapi import HTTPException, Request, status

from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)


def verify_api_key(request: Request, expected_key: Optional[str] = None) -> bool:
    """Verify that the request contains a valid API key in the Authorization header."""
    auth_header: Optional[str] = request.headers.get("Authorization")
    if auth_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization scheme",
        )

    key = expected_key or get_settings().supabase_anon_key
    if not hmac.compare_digest(token, key):
        logger.warning("Unauthorized request from %s", request.client.host if request.client else "unknown")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return True


def generate_secret(length: int = 32) -> str:
    """Generate a cryptographically secure random secret."""
    return secrets.token_urlsafe(length)


def hash_value(value: str) -> str:
    """Return a SHA-256 hex digest of the given value."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
