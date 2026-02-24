"""
Supabase data-access service.

Provides typed helpers for fetching assessment data, downloading images
from private storage, and persisting AI analysis results.

All queries use the **service-role** client so they bypass RLS,
but every public-facing call site must validate ownership first.
"""

from __future__ import annotations

import base64
from typing import Any

from fastapi import HTTPException, status

from core.logger import get_logger
from db.supabase import get_supabase_client

logger = get_logger(__name__)


# ── Ownership guard ─────────────────────────────────────────────

async def validate_assessment_ownership(
    injury_assessment_id: str,
    user_id: str,
) -> dict[str, Any]:
    """
    Verify that *injury_assessment_id* belongs to *user_id*.

    Returns:
        The assessment row as a dict.

    Raises:
        HTTPException 403 – if the assessment does not belong to the user.
        HTTPException 404 – if the assessment does not exist.
    """
    client = get_supabase_client()

    response = (
        client.table("injury_assessments")
        .select("*")
        .eq("id", injury_assessment_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    if response is None or response.data is None:
        logger.warning(
            "Assessment %s not found or not owned by user %s",
            injury_assessment_id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Assessment not found or access denied",
        )

    return response.data


# ── Data fetchers ───────────────────────────────────────────────

async def fetch_baseline_profile(user_id: str) -> dict[str, Any] | None:
    """Fetch the user's baseline profile (lifestyle, habits)."""
    client = get_supabase_client()
    response = (
        client.table("baseline_profiles")
        .select("*")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    if response is None:
        return None
    return response.data


async def fetch_medical_conditions(user_id: str) -> list[dict[str, Any]]:
    """Fetch the user's medical conditions with joined names."""
    client = get_supabase_client()
    response = (
        client.table("user_medical_conditions")
        .select("condition_id, medical_conditions(name, description)")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data or []


async def fetch_injury_images(injury_assessment_id: str) -> list[dict[str, Any]]:
    """Fetch image metadata rows linked to an assessment."""
    client = get_supabase_client()
    response = (
        client.table("injury_images")
        .select("id, image_url, ai_description")
        .eq("injury_assessment_id", injury_assessment_id)
        .execute()
    )
    return response.data or []


# ── Storage ─────────────────────────────────────────────────────

async def download_image_as_base64(storage_path: str) -> str:
    """
    Download an image from private Supabase Storage and return it
    as a **base64-encoded** string (no data-URI prefix).
    """
    client = get_supabase_client()

    try:
        file_bytes: bytes = client.storage.from_("injury-images").download(storage_path)
    except Exception as exc:
        logger.error("Failed to download image %s: %s", storage_path, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not retrieve image from storage: {storage_path}",
        )

    return base64.b64encode(file_bytes).decode("utf-8")


# ── Persist AI result ───────────────────────────────────────────

async def insert_clinical_analysis(
    injury_assessment_id: str,
    probable_condition: str,
    confidence_score: float,
    reasoning: str,
    model_version: str,
) -> dict[str, Any]:
    """Insert a new row into *ai_clinical_analysis* and return it."""
    client = get_supabase_client()

    response = (
        client.table("ai_clinical_analysis")
        .insert({
            "injury_assessment_id": injury_assessment_id,
            "probable_condition": probable_condition,
            "confidence_score": confidence_score,
            "reasoning": reasoning,
            "model_version": model_version,
        })
        .execute()
    )

    if not response.data:
        logger.error("Failed to insert clinical analysis for %s", injury_assessment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist AI analysis result",
        )

    return response.data[0]


# ── User language preference ────────────────────────────────────

async def fetch_user_language(user_id: str) -> str:
    """
    Return the user's preferred language code from ``profiles.language``.

    Falls back to ``"en"`` if the profile doesn't exist or ``language``
    is ``NULL``.
    """
    client = get_supabase_client()

    response = (
        client.table("profiles")
        .select("language")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    if response is not None and response.data and response.data.get("language"):
        return response.data["language"]

    return "en"


# ── Fetch existing analysis ────────────────────────────────────

async def fetch_clinical_analysis(
    injury_assessment_id: str,
) -> dict[str, Any] | None:
    """
    Fetch the latest AI clinical analysis for *injury_assessment_id*.

    Returns the row as a dict, or ``None`` if no analysis exists.
    """
    client = get_supabase_client()

    response = (
        client.table("ai_clinical_analysis")
        .select("*")
        .eq("injury_assessment_id", injury_assessment_id)
        .order("created_at", desc=True)
        .maybe_single()
        .execute()
    )

    if response is None:
        return None
    return response.data
