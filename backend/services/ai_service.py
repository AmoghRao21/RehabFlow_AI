"""
AI service layer.

Orchestrates the clinical analysis flow:
  1. Gather all patient context from Supabase.
  2. Download injury images and encode them.
  3. Generate clinical analysis (currently mock / deterministic).
  4. Persist result in DB.
  5. Return the stored result.

NOTE: The Modal call is temporarily replaced with deterministic mock
logic for local development and testing.  Restore the real Modal
integration when the inference endpoint is ready.
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger
from services.supabase_service import (
    download_image_as_base64,
    fetch_baseline_profile,
    fetch_injury_images,
    fetch_medical_conditions,
    insert_clinical_analysis,
    validate_assessment_ownership,
)

logger = get_logger(__name__)

MODEL_VERSION = "mock-deterministic-v1"


# ── Mock inference ──────────────────────────────────────────────

def _mock_analyze(
    assessment: dict[str, Any],
    baseline: dict[str, Any] | None,
    condition_names: list[str],
    image_count: int,
) -> dict[str, Any]:
    """
    Deterministic mock that replaces the Modal endpoint.

    Returns a structured result based on pain_location, pain_level,
    swelling, mobility restriction, and lifestyle context.
    """
    pain_location: str = assessment.get("pain_location", "unknown")
    pain_level: int = assessment.get("pain_level", 5)
    swelling: bool = assessment.get("visible_swelling", False)
    mobility: bool = assessment.get("mobility_restriction", False)

    # ── Condition & confidence by location ──────────────────────
    if pain_location == "knee":
        probable_condition = "Possible ligament strain"
        confidence_score = 0.82
    elif pain_location == "shoulder":
        probable_condition = "Possible rotator cuff inflammation"
        confidence_score = 0.79
    else:
        probable_condition = "Soft tissue injury suspected"
        confidence_score = 0.65

    # ── Build reasoning paragraph ───────────────────────────────
    parts: list[str] = [
        f"The patient reports pain in the {pain_location.replace('_', ' ')} region "
        f"with a self-reported intensity of {pain_level}/10.",
    ]

    if swelling:
        parts.append("Visible swelling is present, suggesting an active inflammatory response.")
    else:
        parts.append("No visible swelling was reported.")

    if mobility:
        parts.append(
            "The patient indicates restricted mobility, which may point to "
            "structural involvement or significant soft-tissue compromise."
        )
    else:
        parts.append("Mobility appears to be within a functional range.")

    if baseline:
        occupation = baseline.get("occupation_type", "unspecified")
        sitting = baseline.get("daily_sitting_hours", 0)
        work_level = baseline.get("physical_work_level", "unknown")
        parts.append(
            f"Lifestyle context: occupation is '{occupation}', "
            f"approximately {sitting} hours of daily sitting, "
            f"and a '{work_level}' physical-work level."
        )

    if condition_names:
        parts.append(
            f"Relevant medical history includes: {', '.join(condition_names)}. "
            "These conditions have been factored into the assessment."
        )

    if image_count > 0:
        parts.append(
            f"{image_count} injury image(s) were provided and reviewed as part of this analysis."
        )

    reasoning = " ".join(parts)

    return {
        "probable_condition": probable_condition,
        "confidence_score": confidence_score,
        "reasoning": reasoning,
    }


# ── Public entry point (signature unchanged) ────────────────────

async def run_clinical_analysis(
    injury_assessment_id: str,
    user_id: str,
) -> dict[str, Any]:
    """
    End-to-end clinical analysis pipeline.

    1. Validate ownership.
    2. Fetch patient context (baseline, conditions, injury, images).
    3. Run mock analysis (replaces Modal call).
    4. Persist result in ``ai_clinical_analysis``.
    5. Return the stored row.
    """

    # ── 1. Ownership ────────────────────────────────────────────
    assessment = await validate_assessment_ownership(injury_assessment_id, user_id)
    logger.info(
        "Starting clinical analysis | assessment=%s user=%s",
        injury_assessment_id,
        user_id,
    )

    # ── 2. Gather context ───────────────────────────────────────
    baseline = await fetch_baseline_profile(user_id)
    conditions = await fetch_medical_conditions(user_id)
    image_rows = await fetch_injury_images(injury_assessment_id)

    # Download images (kept so the flow is fully exercised)
    raw_images: list[str] = []
    for row in image_rows:
        b64 = await download_image_as_base64(row["image_url"])
        raw_images.append(b64)

    # Flatten condition names
    condition_names: list[str] = []
    for c in conditions:
        mc = c.get("medical_conditions")
        if mc and isinstance(mc, dict):
            condition_names.append(mc.get("name", "Unknown"))

    # ── 3. Mock analysis (replaces Modal call) ──────────────────
    result = _mock_analyze(
        assessment=assessment,
        baseline=baseline,
        condition_names=condition_names,
        image_count=len(raw_images),
    )

    logger.info(
        "Mock AI result | condition=%s confidence=%.2f",
        result["probable_condition"],
        result["confidence_score"],
    )

    # ── 4. Persist result ───────────────────────────────────────
    stored = await insert_clinical_analysis(
        injury_assessment_id=injury_assessment_id,
        probable_condition=result["probable_condition"],
        confidence_score=result["confidence_score"],
        reasoning=result["reasoning"],
        model_version=MODEL_VERSION,
    )

    logger.info("Analysis persisted | id=%s", stored.get("id"))

    return stored
