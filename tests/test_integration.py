"""
Integration tests for Frontend ↔ Backend API connectivity.

These tests use the actual FastAPI app with mocked dependencies to verify
the full request/response cycle including:
  1. POST /ai/analyze/{id} — full analysis flow with proper CORS headers.
  2. GET /ai/analysis/{id} — fetching existing analysis.
  3. Error handling — 401, 403, 500 all return JSON with CORS headers.
  4. Auth header forwarding and JWT validation.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

ORIGIN = "http://localhost:3000"
FAKE_USER_ID = "c8af80eb-4896-4134-879e-c216e70b6aeb"


# ---------------------------------------------------------------------------
# App fixture with ALL dependencies mocked
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Return a fresh FastAPI app with mocked lifespan dependencies."""
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


def _make_valid_analysis_result(extra=None):
    """Build a mock result that satisfies ClinicalAnalysisResponse schema."""
    base = {
        "id": "result-1",
        "injury_assessment_id": "assessment-123",
        "probable_condition": "Anterior Cruciate Ligament (ACL) Sprain",
        "confidence_score": 0.82,
        "reasoning": "Based on the mechanism of injury...",
        "model_version": "blip+medgemma",
        "created_at": "2026-02-24T20:00:00+00:00",
    }
    if extra:
        base.update(extra)
    return base


# ---------------------------------------------------------------------------
# POST /ai/analyze/{id} — Full Analysis Flow
# ---------------------------------------------------------------------------

class TestAnalyzeEndpoint:

    @pytest.mark.asyncio
    async def test_analyze_returns_cors_headers(self, authed_app):
        """POST /ai/analyze should always include CORS headers."""
        mock_result = _make_valid_analysis_result()

        with patch("routes.ai.run_clinical_analysis", new_callable=AsyncMock, return_value=mock_result):
            transport = ASGITransport(app=authed_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/ai/analyze/assessment-123",
                    headers={
                        "Origin": ORIGIN,
                        "Authorization": "Bearer fake-token",
                    },
                )

        assert response.headers.get("access-control-allow-origin") == ORIGIN

    @pytest.mark.asyncio
    async def test_analyze_success_returns_result(self, authed_app):
        """POST /ai/analyze should return the analysis result on success."""
        mock_result = _make_valid_analysis_result()

        with patch("routes.ai.run_clinical_analysis", new_callable=AsyncMock, return_value=mock_result):
            transport = ASGITransport(app=authed_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/ai/analyze/assessment-123",
                    headers={
                        "Origin": ORIGIN,
                        "Authorization": "Bearer fake-token",
                    },
                )

        assert response.status_code == 200
        body = response.json()
        assert body["probable_condition"] == "Anterior Cruciate Ligament (ACL) Sprain"
        assert body["confidence_score"] == 0.82
        assert body["injury_assessment_id"] == "assessment-123"

    @pytest.mark.asyncio
    async def test_analyze_500_still_has_cors(self, authed_app):
        """If analysis crashes, 500 response must still have CORS headers."""
        with patch("routes.ai.run_clinical_analysis", new_callable=AsyncMock, side_effect=ValueError("boom")):
            transport = ASGITransport(app=authed_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/ai/analyze/assessment-123",
                    headers={
                        "Origin": ORIGIN,
                        "Authorization": "Bearer fake-token",
                    },
                )

        assert response.status_code == 500
        assert response.headers.get("access-control-allow-origin") == ORIGIN
        body = response.json()
        assert "detail" in body


# ---------------------------------------------------------------------------
# GET /ai/analysis/{id} — Fetch Existing Analysis
# ---------------------------------------------------------------------------

class TestGetAnalysisEndpoint:

    @pytest.mark.asyncio
    async def test_get_analysis_returns_data(self, authed_app):
        """GET /ai/analysis should return existing analysis."""
        analysis_data = _make_valid_analysis_result()

        with patch("routes.ai.fetch_clinical_analysis", new_callable=AsyncMock, return_value=analysis_data):
            transport = ASGITransport(app=authed_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/ai/analysis/assessment-123",
                    headers={
                        "Origin": ORIGIN,
                        "Authorization": "Bearer fake-token",
                    },
                )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == ORIGIN
        body = response.json()
        assert body["probable_condition"] == "Anterior Cruciate Ligament (ACL) Sprain"

    @pytest.mark.asyncio
    async def test_get_analysis_404_when_none(self, authed_app):
        """GET /ai/analysis should return 404 when no analysis exists."""
        with patch("routes.ai.fetch_clinical_analysis", new_callable=AsyncMock, return_value=None):
            transport = ASGITransport(app=authed_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/ai/analysis/assessment-123",
                    headers={
                        "Origin": ORIGIN,
                        "Authorization": "Bearer fake-token",
                    },
                )

        assert response.status_code == 404
        assert response.headers.get("access-control-allow-origin") == ORIGIN


# ---------------------------------------------------------------------------
# Auth — 401 on missing/invalid token
# ---------------------------------------------------------------------------

class TestAuthErrors:

    @pytest.mark.asyncio
    async def test_missing_auth_returns_401_with_cors(self, app):
        """Request without Authorization header should return 401/403 + CORS."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/ai/analyze/assessment-123",
                headers={"Origin": ORIGIN},
            )

        assert response.status_code in (401, 403)
        assert response.headers.get("access-control-allow-origin") == ORIGIN
