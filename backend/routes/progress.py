"""
Progress tracking route.

POST /progress/complete-day
  - Requires Bearer JWT (Supabase auth)
  - Marks a day as complete for an injury assessment
  - Updates daily_progress, profiles streak/points, and points_log
  - Returns updated profile stats
"""

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from core.auth import get_current_user_id
from core.logger import get_logger
from db.supabase import get_supabase_client

logger = get_logger(__name__)

router = APIRouter(prefix="/progress", tags=["progress"])

POINTS_PER_DAY = 50  # Points awarded for completing a day


class CompleteDayRequest(BaseModel):
    injury_assessment_id: str = Field(..., description="The assessment this day belongs to")
    day_number: int = Field(..., ge=1, description="The day number completed (1-based)")
    pain_level: int | None = Field(None, ge=0, le=10, description="Current pain level 0-10")
    notes: str | None = Field(None, description="Optional notes")


class CompleteDayResponse(BaseModel):
    success: bool
    points_earned: int
    total_points: int
    current_streak: int
    longest_streak: int
    already_completed: bool


@router.post(
    "/complete-day",
    response_model=CompleteDayResponse,
    summary="Mark a rehab day as complete and update streak/points",
)
async def complete_day(
    body: CompleteDayRequest,
    user_id: str = Depends(get_current_user_id),
) -> CompleteDayResponse:
    """
    Mark a day as complete.

    1. Checks if already completed today (idempotent).
    2. Inserts into daily_progress.
    3. Updates profiles: total_points, current_streak, longest_streak, last_completed_date.
    4. Inserts into points_log.
    """
    client = get_supabase_client()
    today = datetime.date.today()

    # 1. Check if this day is already logged for this assessment
    existing = (
        client.table("daily_progress")
        .select("id")
        .eq("injury_assessment_id", body.injury_assessment_id)
        .eq("day_number", body.day_number)
        .maybe_single()
        .execute()
    )

    if existing and existing.data:
        # Already completed — return current profile stats without modifying
        profile_res = (
            client.table("profiles")
            .select("total_points, current_streak, longest_streak")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        profile = profile_res.data or {}
        return CompleteDayResponse(
            success=True,
            points_earned=0,
            total_points=profile.get("total_points", 0),
            current_streak=profile.get("current_streak", 0),
            longest_streak=profile.get("longest_streak", 0),
            already_completed=True,
        )

    # 2. Insert daily_progress
    client.table("daily_progress").insert({
        "injury_assessment_id": body.injury_assessment_id,
        "day_number": body.day_number,
        "pain_level": body.pain_level,
        "notes": body.notes or "",
    }).execute()

    # 3. Fetch current profile to compute new streak
    profile_res = (
        client.table("profiles")
        .select("total_points, current_streak, longest_streak, last_completed_date")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    profile = profile_res.data or {}

    current_points = profile.get("total_points", 0) or 0
    current_streak = profile.get("current_streak", 0) or 0
    longest_streak = profile.get("longest_streak", 0) or 0
    last_date_str = profile.get("last_completed_date")

    # Compute new streak
    new_streak = current_streak
    if last_date_str:
        try:
            last_date = datetime.date.fromisoformat(str(last_date_str))
            delta = (today - last_date).days
            if delta == 1:
                new_streak = current_streak + 1  # Consecutive day
            elif delta == 0:
                new_streak = current_streak  # Same day, no change
            else:
                new_streak = 1  # Streak broken, restart
        except (ValueError, TypeError):
            new_streak = 1
    else:
        new_streak = 1  # First ever completion

    new_longest = max(longest_streak, new_streak)
    new_points = current_points + POINTS_PER_DAY

    # 4. Update profile
    client.table("profiles").update({
        "total_points": new_points,
        "current_streak": new_streak,
        "longest_streak": new_longest,
        "last_completed_date": today.isoformat(),
    }).eq("id", user_id).execute()

    # 5. Log the points
    client.table("points_log").insert({
        "user_id": user_id,
        "points": POINTS_PER_DAY,
        "source": f"completed_day_{body.day_number}",
    }).execute()

    logger.info(
        "Day completed | user=%s assessment=%s day=%d streak=%d points=%d",
        user_id,
        body.injury_assessment_id,
        body.day_number,
        new_streak,
        new_points,
    )

    return CompleteDayResponse(
        success=True,
        points_earned=POINTS_PER_DAY,
        total_points=new_points,
        current_streak=new_streak,
        longest_streak=new_longest,
        already_completed=False,
    )


@router.get(
    "/completed-days/{injury_assessment_id}",
    summary="Get list of completed day numbers for an assessment",
)
async def get_completed_days(
    injury_assessment_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Return set of day numbers the user has completed."""
    client = get_supabase_client()

    result = (
        client.table("daily_progress")
        .select("day_number")
        .eq("injury_assessment_id", injury_assessment_id)
        .execute()
    )

    completed = [row["day_number"] for row in (result.data or [])]
    return {"completed_days": completed}
