"""
JWT authentication dependency for FastAPI routes.

Supabase signs user access tokens with ES256 (ECDSA).  The public key is
fetched from the project's JWKS endpoint and cached by PyJWKClient.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import jwt
from jwt import PyJWKClient

from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)

_bearer_scheme = HTTPBearer()

# Supabase JWKS endpoint — public keys used to verify ES256 access tokens.
_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    """Lazy-init and cache a single PyJWKClient instance."""
    global _jwks_client
    if _jwks_client is None:
        settings = get_settings()
        jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
        logger.info("JWKS client initialised → %s", jwks_url)
    return _jwks_client


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """
    Decode and validate the Supabase JWT from the Authorization header.

    Returns the authenticated user's UUID string and also stores it on
    ``request.state.user_id`` for convenient access in route handlers.
    """
    token = credentials.credentials

    try:
        # Resolve the signing key from JWKS using the token's "kid" header
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        logger.warning("JWT has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        logger.warning("JWT validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as exc:
        logger.error("Unexpected auth error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    if user_id is None:
        logger.warning("JWT payload missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain a valid user identity",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.user_id = user_id
    return user_id
