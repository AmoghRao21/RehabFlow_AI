from typing import Optional

from supabase import Client, create_client

from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)

_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Return a singleton Supabase client authenticated with the service key."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
        logger.info("Supabase client initialized for %s", settings.supabase_url)
    return _client
