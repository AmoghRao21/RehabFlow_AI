"""
YouTube video search service.

Fetches the best embeddable video for a set of keywords using a composite
ranking strategy that weights:
  - relevance rank from the YouTube Search API   (30 %)
  - view count                                   (35 %)
  - like count                                   (25 %)
  - like-to-view ratio (engagement quality)      (10 %)

This means a highly-liked tutorial with millions of views beats a technically
"top-result" video that has poor engagement.
"""

from __future__ import annotations

import math
from typing import Any

import httpx

from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)

_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# How many candidates to pull from the Search API before scoring
_CANDIDATE_COUNT = 10


async def _search_candidates(
    client: httpx.AsyncClient,
    query: str,
    api_key: str,
    max_results: int = _CANDIDATE_COUNT,
) -> list[str]:
    """Return a list of video IDs ordered by YouTube's own relevance score."""
    params: dict[str, Any] = {
        "part": "snippet",
        "q": f"{query} -#shorts",
        "type": "video",
        "maxResults": max_results,
        "videoEmbeddable": "true",
        "videoSyndicated": "true",
        "videoDuration": "medium",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "order": "relevance",
        "key": api_key,
    }
    resp = await client.get(_SEARCH_URL, params=params, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    return [item["id"]["videoId"] for item in data.get("items", [])]


async def _fetch_statistics(
    client: httpx.AsyncClient,
    video_ids: list[str],
    api_key: str,
) -> dict[str, dict[str, int]]:
    """Return a mapping of videoId → {viewCount, likeCount}."""
    params: dict[str, Any] = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": api_key,
    }
    resp = await client.get(_VIDEOS_URL, params=params, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()

    result: dict[str, dict[str, int]] = {}
    for item in data.get("items", []):
        stats = item.get("statistics", {})
        result[item["id"]] = {
            "viewCount": int(stats.get("viewCount", 0)),
            "likeCount": int(stats.get("likeCount", 0)),
        }
    return result


def _log_scale(n: int) -> float:
    """Logarithmic normaliser so a 1 M-view video doesn't dwarf a 100 k one."""
    return math.log1p(n)


def _score_videos(
    video_ids: list[str],
    stats: dict[str, dict[str, int]],
) -> list[tuple[str, float]]:
    """
    Compute a composite score for each video and return
    [(video_id, score), ...] sorted best-first.

    Weights:
      relevance_rank   30 %  – position 0 is best
      view_count       35 %  – log-scaled, then min-max normalised
      like_count       25 %  – log-scaled, then min-max normalised
      like/view ratio  10 %  – engagement quality signal
    """
    n = len(video_ids)
    if n == 0:
        return []

    # Pre-compute log-scaled values
    log_views = [_log_scale(stats.get(vid, {}).get("viewCount", 0))
                 for vid in video_ids]
    log_likes = [_log_scale(stats.get(vid, {}).get("likeCount", 0))
                 for vid in video_ids]

    max_views = max(log_views) or 1.0
    max_likes = max(log_likes) or 1.0

    scored: list[tuple[str, float]] = []
    for rank, vid in enumerate(video_ids):
        relevance_score = 1.0 - (rank / n)  # 1.0 for rank-0 → 0.0 for last

        view_score = log_views[rank] / max_views
        like_score = log_likes[rank] / max_likes

        raw_views = stats.get(vid, {}).get("viewCount", 0)
        raw_likes = stats.get(vid, {}).get("likeCount", 0)
        ratio_score = (raw_likes / raw_views) if raw_views > 0 else 0.0
        # Cap ratio at 0.2 (20 % like rate is essentially perfect) then normalise
        ratio_score = min(ratio_score, 0.20) / 0.20

        composite = (
            0.30 * relevance_score
            + 0.35 * view_score
            + 0.25 * like_score
            + 0.10 * ratio_score
        )
        scored.append((vid, composite))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored


async def find_best_video(keywords: list[str]) -> str:
    """
    Given a list of keywords, return an embeddable YouTube URL for the best
    matching video, e.g. ``https://www.youtube.com/embed/<id>``.

    Raises ``httpx.HTTPStatusError`` on API errors.
    Raises ``ValueError`` when no embeddable video is found.
    """
    settings = get_settings()
    api_key = settings.youtube_api_key
    query = " ".join(keywords)

    logger.info("YouTube search | query=%r", query)

    async with httpx.AsyncClient() as client:
        video_ids = await _search_candidates(client, query, api_key)

        if not video_ids:
            raise ValueError(f"No YouTube results found for query: {query!r}")

        stats = await _fetch_statistics(client, video_ids, api_key)

    # videos.list only returns IDs that are publicly accessible (not deleted,
    # private, or region-blocked).  Drop any ID absent from the stats response
    # so we never return an unplayable embed URL.
    available_ids = [vid for vid in video_ids if vid in stats]

    if not available_ids:
        raise ValueError(
            f"No publicly accessible YouTube video found for query: {query!r}"
        )

    scored = _score_videos(available_ids, stats)

    best_id, best_score = scored[0]
    logger.info(
        "Best video | id=%s score=%.3f query=%r",
        best_id,
        best_score,
        query,
    )

    return f"https://www.youtube.com/embed/{best_id}"
