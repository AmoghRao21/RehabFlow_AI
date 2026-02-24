"""
Shared test fixtures for the RehabFlow AI backend test suite.

These fixtures mock external dependencies (Supabase, Redis, env vars)
so tests run in isolation without network or DB access.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure the backend package is importable from the tests/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


# ---------------------------------------------------------------------------
# Environment variables — set BEFORE any settings import
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Inject required env vars so Settings() doesn't crash."""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-jwt-secret")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("MEDGEMMA_ENDPOINT", "https://test-modal-endpoint.modal.run")
    monkeypatch.setenv("ENVIRONMENT", "test")

    # Clear the lru_cache so Settings picks up new env vars each test
    from core.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Supabase client mock
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_supabase_client():
    """Return a MagicMock that mimics the Supabase Python client."""
    client = MagicMock()
    return client


# ---------------------------------------------------------------------------
# Sample assessment data (mirrors the real DB row from injury_assessments)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_assessment():
    """A realistic injury_assessments row as returned by Supabase."""
    return {
        "id": "dcf757ee-61ba-4bf9-91d9-1e0f66c2fdb9",
        "user_id": "c8af80eb-4896-4134-879e-c216e70b6aeb",
        "pain_location": "right_knee",
        "pain_level": 7,
        "pain_cause": "Sports injury while playing football — twisted knee during tackle",
        "pain_started_at": "2026-02-20T00:00:00+00:00",
        "visible_swelling": True,
        "mobility_restriction": True,
        "additional_notes": "Advanced assessment submission",
        "created_at": "2026-02-24T20:00:00+00:00",
    }


@pytest.fixture
def sample_assessment_minimal():
    """Assessment row with optional fields empty/null."""
    return {
        "id": "aaaa1111-2222-3333-4444-555566667777",
        "user_id": "c8af80eb-4896-4134-879e-c216e70b6aeb",
        "pain_location": "lower_back",
        "pain_level": 3,
        "pain_cause": None,
        "pain_started_at": "2026-02-22T00:00:00+00:00",
        "visible_swelling": False,
        "mobility_restriction": False,
        "additional_notes": None,
        "created_at": "2026-02-24T21:00:00+00:00",
    }


@pytest.fixture
def sample_baseline_profile():
    """A realistic baseline_profiles row."""
    return {
        "user_id": "c8af80eb-4896-4134-879e-c216e70b6aeb",
        "occupation_type": "office_worker",
        "daily_sitting_hours": 8,
        "physical_work_level": "sedentary",
        "gym_frequency": "never",
        "alcohol_usage": "rarely",
        "smoking_usage": "never",
        "drug_usage": "never",
    }


@pytest.fixture
def sample_medical_conditions():
    """Medical conditions rows with joined names."""
    return [
        {"condition_id": "1", "medical_conditions": {"name": "Hypertension", "description": "High blood pressure"}},
        {"condition_id": "2", "medical_conditions": {"name": "Asthma", "description": "Respiratory condition"}},
    ]


@pytest.fixture
def sample_modal_response():
    """A realistic response from the Modal MedGemma endpoint."""
    return {
        "probable_condition": "Anterior Cruciate Ligament (ACL) Sprain",
        "confidence_score": 0.82,
        "reasoning": "Based on the mechanism of injury (twisting during tackle), visible swelling...",
        "rehab_plan": "Phase 1: Rest, ice, compression...\nPhase 2: Gentle mobility...",
        "image_captions": ["a close up photo of a swollen knee joint"],
        "model_version": "blip:Salesforce/blip-image-captioning-large+medgemma:google/medgemma-4b-it",
    }
