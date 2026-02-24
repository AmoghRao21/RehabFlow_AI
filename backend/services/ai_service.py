"""
AI service layer.

Orchestrates the clinical analysis flow:
  1. Gather all patient context from Supabase.
  2. Download injury images and encode them.
  3. Call the Modal BLIP + MedGemma endpoint for real AI analysis.
  4. Persist result in DB.
  5. Return the stored result.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, status

from core.config import get_settings
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

MODEL_VERSION = "blip:Salesforce/blip-image-captioning-large+medgemma:google/medgemma-4b-it"

# Timeout for the Modal endpoint — first call may cold-start the GPU
# container (loading BLIP ~1 GB + MedGemma ~8.5 GB), which can take 2-5 min.
MODAL_TIMEOUT = 300.0


# ── Modal endpoint call ─────────────────────────────────────────

async def _call_medgemma_endpoint(
    images_base64: list[str],
    text_complaint: str,
    pain_location: str,
    pain_level: int,
    patient_context: dict[str, Any],
) -> dict[str, Any]:
    """
    Call the Modal-hosted BLIP + MedGemma endpoint to generate
    a clinical analysis and rehabilitation plan.
    """
    settings = get_settings()
    endpoint_url = settings.medgemma_endpoint

    if not endpoint_url:
        raise ValueError(
            "MEDGEMMA_ENDPOINT is not configured. "
            "Deploy the Modal endpoint and set the URL in .env"
        )

    # The DEPLOYED Modal endpoint uses  image_base64: str   (single image)
    # The LOCAL/future code uses        images_base64: list[str]
    # Send both so either version works.
    payload = {
        "image_base64": images_base64[0] if images_base64 else "",
        "images_base64": images_base64,
        "text_complaint": text_complaint,
        "pain_location": pain_location,
        "pain_level": pain_level,
        "patient_context": patient_context,
    }

    try:
        async with httpx.AsyncClient(
            timeout=MODAL_TIMEOUT,
            follow_redirects=True,  # Modal returns 303 redirects for async results
        ) as client:
            response = await client.post(
                endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
    except httpx.ReadTimeout:
        logger.error(
            "MedGemma endpoint timed out after %.0f seconds (cold start?)",
            MODAL_TIMEOUT,
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                "AI analysis timed out. The GPU may be cold-starting. "
                "Please wait 1-2 minutes and try again."
            ),
        )

    if response.status_code != 200:
        logger.error(
            "MedGemma endpoint returned %d: %s",
            response.status_code,
            response.text[:500],
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI analysis service returned an error (HTTP {response.status_code})",
        )

    data = response.json()
    logger.info("Raw Modal response keys: %s", list(data.keys()) if isinstance(data, dict) else type(data))
    logger.info("Raw Modal response (truncated): %s", str(data)[:1000])
    return data


# ── Public entry point (signature unchanged) ────────────────────

async def run_clinical_analysis(
    injury_assessment_id: str,
    user_id: str,
) -> dict[str, Any]:
    """
    End-to-end clinical analysis pipeline.

    1. Validate ownership.
    2. Fetch patient context (baseline, conditions, injury, images).
    3. Call Modal BLIP + MedGemma endpoint for AI analysis.
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

    # Download images as base64
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

    # Build patient context dict for the endpoint
    patient_context: dict[str, Any] = {}
    if baseline:
        patient_context["occupation_type"] = baseline.get("occupation_type", "")
        patient_context["daily_sitting_hours"] = baseline.get("daily_sitting_hours", 0)
        patient_context["physical_work_level"] = baseline.get("physical_work_level", "")
    if condition_names:
        patient_context["medical_conditions"] = condition_names

    # ── 3. Call Modal endpoint ──────────────────────────────────
    logger.info(
        "Calling MedGemma endpoint | images=%d conditions=%s",
        len(raw_images),
        condition_names,
    )

    # ── Build text_complaint from actual DB columns ────────────
    # Frontend stores injury description in `pain_cause` (NOT `description`).
    # We enrich it with swelling/mobility info for better AI analysis.
    complaint_parts: list[str] = []

    pain_cause = (assessment.get("pain_cause") or "").strip()
    if pain_cause:
        complaint_parts.append(f"Cause: {pain_cause}")

    additional_notes = (assessment.get("additional_notes") or "").strip()
    if additional_notes and additional_notes != "Advanced assessment submission":
        complaint_parts.append(f"Notes: {additional_notes}")

    if assessment.get("visible_swelling"):
        complaint_parts.append("Visible swelling is present.")
    if assessment.get("mobility_restriction"):
        complaint_parts.append("Mobility is restricted.")

    pain_location = assessment.get("pain_location", "unspecified area")
    text_complaint = "; ".join(complaint_parts) if complaint_parts else f"Pain in {pain_location}"

    result = await _call_medgemma_endpoint(
        images_base64=raw_images,
        text_complaint=text_complaint,
        pain_location=pain_location,
        pain_level=assessment.get("pain_level", 5),
        patient_context=patient_context,
    )

    logger.info(
        "AI result | condition=%s confidence=%.2f",
        result.get("probable_condition", "N/A"),
        result.get("confidence_score", 0.0),
    )

    # Combine reasoning and rehab_plan into the reasoning field
    # (the DB schema has a single 'reasoning' column)
    full_reasoning = result.get("reasoning", "")
    rehab_plan = result.get("rehab_plan", "")
    if rehab_plan:
        full_reasoning += "\n\n## Rehabilitation Plan\n" + rehab_plan

    # Include image captions in reasoning if available
    captions = result.get("image_captions", [])
    if captions:
        caption_text = "\n".join(
            f"- Image {i+1}: {cap}" for i, cap in enumerate(captions)
        )
        full_reasoning = (
            f"## Visual Assessment\n{caption_text}\n\n{full_reasoning}"
        )

    # ── 4. Persist result ───────────────────────────────────────
    stored = await insert_clinical_analysis(
        injury_assessment_id=injury_assessment_id,
        probable_condition=result.get("probable_condition", "Assessment pending"),
        confidence_score=result.get("confidence_score", 0.0),
        reasoning=full_reasoning,
        model_version=MODEL_VERSION,
    )

    logger.info("Analysis persisted | id=%s", stored.get("id"))

    return stored
