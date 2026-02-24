"""
AI analysis route.

POST /ai/analyze/{injury_assessment_id}
  - Requires Bearer JWT (Supabase auth)
  - Runs full clinical analysis pipeline
  - Returns the persisted analysis result

GET /ai/analysis/{injury_assessment_id}
  - Requires Bearer JWT (Supabase auth)
  - Returns existing analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth import get_current_user_id
from core.logger import get_logger
from services.ai_service import run_clinical_analysis
from services.supabase_service import fetch_clinical_analysis

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

    try:
        result = await run_clinical_analysis(
            injury_assessment_id=injury_assessment_id,
            user_id=user_id,
        )
    except HTTPException:
        raise  # Let FastAPI handle HTTPExceptions normally
    except Exception as exc:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {exc}",
        )

    return ClinicalAnalysisResponse(**result)


@router.get(
    "/analysis/{injury_assessment_id}",
    response_model=ClinicalAnalysisResponse,
    summary="Get existing AI analysis",
)
async def get_analysis(
    injury_assessment_id: str,
    user_id: str = Depends(get_current_user_id),
) -> ClinicalAnalysisResponse:
    """
    Fetch the existing clinical analysis for the given assessment.
    """
    result = await fetch_clinical_analysis(injury_assessment_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis found for this assessment",
        )

    return ClinicalAnalysisResponse(**result)
