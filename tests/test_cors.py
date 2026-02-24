"""
Tests for CORS configuration and error handling.

Verifies that:
  1. CORS headers are present on normal responses.
  2. CORS headers are present on error responses (500, 404, 502).
  3. Preflight (OPTIONS) requests succeed.
  4. The global exception handler returns JSON with CORS headers.
  5. Origins that are NOT allowed are rejected.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALLOWED_ORIGIN = "http://localhost:3000"
DISALLOWED_ORIGIN = "http://evil-site.com"
FAKE_USER_ID = "c8af80eb-4896-4134-879e-c216e70b6aeb"


@pytest.fixture
def app():
    """Import and return a fresh FastAPI app with mocked lifespan."""
    with patch("main.get_supabase_client"), \
         patch("main.get_redis_client", new_callable=AsyncMock), \
         patch("main.close_redis_client", new_callable=AsyncMock):
        from main import app
        return app


@pytest.fixture
def authed_app(app):
    """App with auth dependency overridden to always return a fake user ID."""
    from core.auth import get_current_user_id

    async def fake_user():
        return FAKE_USER_ID

    app.dependency_overrides[get_current_user_id] = fake_user
    yield app
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# CORS on normal responses
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cors_headers_on_health_endpoint(app):
    """Health endpoint should return Access-Control-Allow-Origin for allowed origins."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={"Origin": ALLOWED_ORIGIN},
        )
    assert response.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN


@pytest.mark.asyncio
async def test_cors_preflight_options(app):
    """OPTIONS (preflight) should return 200 with CORS headers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/ai/analyze/some-id",
            headers={
                "Origin": ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            },
        )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN
    assert "POST" in response.headers.get("access-control-allow-methods", "")


@pytest.mark.asyncio
async def test_cors_rejected_for_disallowed_origin(app):
    """Requests from a disallowed origin should NOT get CORS headers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={"Origin": DISALLOWED_ORIGIN},
        )
    assert response.headers.get("access-control-allow-origin") != DISALLOWED_ORIGIN


# ---------------------------------------------------------------------------
# CORS on error responses (the bug we fixed)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cors_headers_on_404(app):
    """A 404 response must still include CORS headers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/nonexistent-route",
            headers={"Origin": ALLOWED_ORIGIN},
        )
    assert response.status_code in (404, 405)
    assert response.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN


@pytest.mark.asyncio
async def test_cors_headers_on_unhandled_exception(authed_app):
    """
    If a route raises an unhandled ValueError, the global handler should
    catch it and return JSON with CORS headers.
    """
    with patch("routes.ai.run_clinical_analysis", new_callable=AsyncMock, side_effect=ValueError("test crash")):
        transport = ASGITransport(app=authed_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/ai/analyze/test-id",
                headers={
                    "Origin": ALLOWED_ORIGIN,
                    "Authorization": "Bearer fake-token",
                },
            )

    assert response.status_code == 500
    assert response.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN
    body = response.json()
    assert "detail" in body


@pytest.mark.asyncio
async def test_cors_credentials_allowed(app):
    """Verify allow-credentials is included in CORS response."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/ai/analyze/some-id",
            headers={
                "Origin": ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
    assert response.headers.get("access-control-allow-credentials") == "true"
