"""
YouTube video search route.

GET /youtube/video?keywords=python&keywords=tutorial
  - Public endpoint (no auth required)
  - Returns the embeddable URL of the best matching YouTube video

POST /youtube/video
  - Same logic but accepts a JSON body { "keywords": ["python", "tutorial"] }
  - Useful for complex/longer keyword lists
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from core.logger import get_logger
from services.youtube_service import find_best_video

logger = get_logger(__name__)

router = APIRouter(prefix="/youtube", tags=["youtube"])


# ─── Response schema ──────────────────────────────────────────────────────────


class VideoEmbedResponse(BaseModel):
    embed_url: str = Field(
        ...,
        description="Embeddable YouTube URL, e.g. https://www.youtube.com/embed/<id>",
        examples=["https://www.youtube.com/embed/kqtD5dpn9C8"],
    )
    query: str = Field(...,
                       description="The joined keyword query that was searched")


# ─── Request body (POST) ──────────────────────────────────────────────────────


class VideoSearchRequest(BaseModel):
    keywords: list[str] = Field(
        ...,
        min_length=1,
        description="List of search keywords, e.g. ['physical therapy', 'shoulder']",
        examples=[["physical therapy", "shoulder exercise"]],
    )


# ─── Routes ──────────────────────────────────────────────────────────────────


@router.get(
    "/video",
    response_model=VideoEmbedResponse,
    summary="Find the best embeddable YouTube video for given keywords (GET)",
)
async def get_video(
    keywords: list[str] = Query(
        ...,
        description="One or more keywords. Pass the parameter multiple times: "
                    "?keywords=rehab&keywords=knee",
    ),
) -> VideoEmbedResponse:
    return await _resolve(keywords)


@router.post(
    "/video",
    response_model=VideoEmbedResponse,
    summary="Find the best embeddable YouTube video for given keywords (POST)",
)
async def post_video(body: VideoSearchRequest) -> VideoEmbedResponse:
    return await _resolve(body.keywords)


# ─── Shared helper ────────────────────────────────────────────────────────────


async def _resolve(keywords: list[str]) -> VideoEmbedResponse:
    query = " ".join(k.strip() for k in keywords if k.strip())
    if not query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one non-empty keyword is required.",
        )

    try:
        embed_url = await find_best_video(keywords)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("YouTube API error | query=%r", query)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"YouTube API error: {exc}",
        ) from exc

    return VideoEmbedResponse(embed_url=embed_url, query=query)
