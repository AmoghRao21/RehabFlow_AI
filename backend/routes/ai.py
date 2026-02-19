"""
AI analysis route.

POST /ai/analyze/{injury_assessment_id}
  - Requires Bearer JWT (Supabase auth)
  - Runs full clinical analysis pipeline
  - Returns the persisted analysis result
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.auth import get_current_user_id
from core.logger import get_logger
from services.ai_service import run_clinical_analysis

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


class ClinicalAnalysisResponse(BaseModel):
    id: str
    injury_assessment_id: str
    probable_condition: str | None
    confidence_score: float | None
    reasoning: str | None
    model_version: str | None
    created_at: str | None


@router.post(
    "/analyze/{injury_assessment_id}",
    response_model=ClinicalAnalysisResponse,
    summary="Run AI clinical analysis on an injury assessment",
)
async def analyze_injury(
    injury_assessment_id: str,
    user_id: str = Depends(get_current_user_id),
) -> ClinicalAnalysisResponse:
    """
    Trigger a full clinical analysis for the given injury assessment.

    The endpoint:
    1. Validates that the assessment belongs to the authenticated user.
    2. Fetches all patient context (baseline, conditions, images).
    3. Sends data to the Modal AI inference endpoint.
    4. Persists the result in ``ai_clinical_analysis``.
    5. Returns the stored analysis.
    """
    logger.info(
        "Analyze request | assessment=%s user=%s",
        injury_assessment_id,
        user_id,
    )

    result = await run_clinical_analysis(
        injury_assessment_id=injury_assessment_id,
        user_id=user_id,
    )

    return ClinicalAnalysisResponse(**result)
