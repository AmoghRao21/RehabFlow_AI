"""
Supabase client wrapper for authentication and storage operations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from supabase import Client, create_client

from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AuthResult:
    """Simple auth result wrapper for UI usage."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class SupabaseClient:
    """Handles Supabase authentication and admin access."""

    def __init__(self, url: str, anon_key: str, service_role_key: str | None = None) -> None:
        if not url or not anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY are required")

        self.client: Client = create_client(url, anon_key)
        self.admin_client: Optional[Client] = None
        if service_role_key:
            self.admin_client = create_client(url, service_role_key)

        logger.info("Supabase client initialized")

    @classmethod
    def from_config(cls) -> "SupabaseClient":
        return cls(
            Config.SUPABASE_URL,
            Config.SUPABASE_ANON_KEY,
            Config.SUPABASE_SERVICE_ROLE_KEY,
        )

    def sign_up(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> AuthResult:
        try:
            result = self.client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": metadata or {}},
                }
            )
            return AuthResult(True, "Sign up successful", {"user": result.user, "session": result.session})
        except Exception as exc:
            logger.error("Sign up failed: %s", exc, exc_info=True)
            return AuthResult(False, f"Sign up failed: {exc}")

    def sign_in(self, email: str, password: str) -> AuthResult:
        try:
            result = self.client.auth.sign_in_with_password(
                {"email": email, "password": password})
            return AuthResult(True, "Sign in successful", {"user": result.user, "session": result.session})
        except Exception as exc:
            logger.error("Sign in failed: %s", exc, exc_info=True)
            return AuthResult(False, f"Sign in failed: {exc}")

    def sign_out(self) -> AuthResult:
        try:
            self.client.auth.sign_out()
            return AuthResult(True, "Sign out successful")
        except Exception as exc:
            logger.error("Sign out failed: %s", exc, exc_info=True)
            return AuthResult(False, f"Sign out failed: {exc}")

    def reset_password(self, email: str) -> AuthResult:
        try:
            self.client.auth.reset_password_email(email)
            return AuthResult(True, "Password reset email sent")
        except Exception as exc:
            logger.error("Reset password failed: %s", exc, exc_info=True)
            return AuthResult(False, f"Reset password failed: {exc}")

    def get_current_user(self) -> AuthResult:
        try:
            session = self.client.auth.get_session()
            user = session.user if session else None
            if not user:
                return AuthResult(False, "No active user")
            return AuthResult(True, "Current user retrieved", {"user": user})
        except Exception as exc:
            logger.error("Get current user failed: %s", exc, exc_info=True)
            return AuthResult(False, f"Get current user failed: {exc}")


_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Lazily initialize the Supabase client to avoid import-time failures."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient.from_config()
    return _supabase_client
