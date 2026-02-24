"""
Tests for Supabase service — null safety on maybe_single() calls.

Verifies that:
  1. validate_assessment_ownership raises 403 when response is None.
  2. fetch_baseline_profile returns None when no data found.
  3. fetch_clinical_analysis returns None when no data found.
  4. Normal cases still work when data IS present.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_supabase_response(data):
    """Create a mock Supabase response with a .data attribute."""
    response = MagicMock()
    response.data = data
    return response


def _mock_supabase_chain(mock_client, data, chain_style="validate"):
    """
    Build a fluent mock chain matching supabase-py's builder pattern.

    chain_style:
        "validate" -> table().select().eq().eq().maybe_single().execute()
        "baseline" -> table().select().eq().maybe_single().execute()
        "clinical" -> table().select().eq().order().maybe_single().execute()
    """
    table = mock_client.table.return_value
    select = table.select.return_value
    eq1 = select.eq.return_value

    if chain_style == "validate":
        eq2 = eq1.eq.return_value
        eq2.maybe_single.return_value.execute.return_value = data
    elif chain_style == "baseline":
        eq1.maybe_single.return_value.execute.return_value = data
    elif chain_style == "clinical":
        order = eq1.order.return_value
        order.maybe_single.return_value.execute.return_value = data


# ---------------------------------------------------------------------------
# validate_assessment_ownership
# ---------------------------------------------------------------------------

class TestValidateAssessmentOwnership:

    @pytest.mark.asyncio
    async def test_raises_403_when_no_rows(self):
        """Should raise HTTPException 403 when assessment not found."""
        mock_client = MagicMock()
        _mock_supabase_chain(mock_client, None, "validate")

        with patch("services.supabase_service.get_supabase_client", return_value=mock_client):
            from services.supabase_service import validate_assessment_ownership
            with pytest.raises(HTTPException) as exc_info:
                await validate_assessment_ownership("bad-id", "bad-user")
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_raises_403_when_response_data_is_none(self):
        """Should raise 403 when response exists but data is None (no row matched)."""
        mock_client = MagicMock()
        _mock_supabase_chain(mock_client, _make_supabase_response(None), "validate")

        with patch("services.supabase_service.get_supabase_client", return_value=mock_client):
            from services.supabase_service import validate_assessment_ownership
            with pytest.raises(HTTPException) as exc_info:
                await validate_assessment_ownership("bad-id", "bad-user")
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_data_when_found(self, sample_assessment):
        """Should return the assessment dict when found."""
        mock_client = MagicMock()
        _mock_supabase_chain(mock_client, _make_supabase_response(sample_assessment), "validate")

        with patch("services.supabase_service.get_supabase_client", return_value=mock_client):
            from services.supabase_service import validate_assessment_ownership
            result = await validate_assessment_ownership(
                sample_assessment["id"],
                sample_assessment["user_id"],
            )
            assert result == sample_assessment
            assert result["pain_location"] == "right_knee"


# ---------------------------------------------------------------------------
# fetch_baseline_profile
# ---------------------------------------------------------------------------

class TestFetchBaselineProfile:

    @pytest.mark.asyncio
    async def test_returns_none_when_no_baseline(self):
        """Should return None when no baseline profile exists (not crash)."""
        mock_client = MagicMock()
        _mock_supabase_chain(mock_client, None, "baseline")

        with patch("services.supabase_service.get_supabase_client", return_value=mock_client):
            from services.supabase_service import fetch_baseline_profile
            result = await fetch_baseline_profile("user-with-no-profile")
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_data_when_found(self, sample_baseline_profile):
        """Should return baseline data when found."""
        mock_client = MagicMock()
        _mock_supabase_chain(mock_client, _make_supabase_response(sample_baseline_profile), "baseline")

        with patch("services.supabase_service.get_supabase_client", return_value=mock_client):
            from services.supabase_service import fetch_baseline_profile
            result = await fetch_baseline_profile(sample_baseline_profile["user_id"])
            assert result["occupation_type"] == "office_worker"


# ---------------------------------------------------------------------------
# fetch_clinical_analysis
# ---------------------------------------------------------------------------

class TestFetchClinicalAnalysis:

    @pytest.mark.asyncio
    async def test_returns_none_when_no_analysis(self):
        """Should return None when no AI analysis exists for an assessment."""
        mock_client = MagicMock()
        _mock_supabase_chain(mock_client, None, "clinical")

        with patch("services.supabase_service.get_supabase_client", return_value=mock_client):
            from services.supabase_service import fetch_clinical_analysis
            result = await fetch_clinical_analysis("assessment-without-analysis")
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_response_data_is_none(self):
        """Should not crash when response exists but data is None."""
        mock_client = MagicMock()
        _mock_supabase_chain(mock_client, _make_supabase_response(None), "clinical")

        with patch("services.supabase_service.get_supabase_client", return_value=mock_client):
            from services.supabase_service import fetch_clinical_analysis
            result = await fetch_clinical_analysis("assessment-id")
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_data_when_analysis_exists(self):
        """Should return analysis data when it exists."""
        analysis_data = {
            "id": "analysis-1",
            "injury_assessment_id": "assessment-1",
            "probable_condition": "ACL Sprain",
            "confidence_score": 0.85,
            "reasoning": "Based on...",
        }
        mock_client = MagicMock()
        _mock_supabase_chain(mock_client, _make_supabase_response(analysis_data), "clinical")

        with patch("services.supabase_service.get_supabase_client", return_value=mock_client):
            from services.supabase_service import fetch_clinical_analysis
            result = await fetch_clinical_analysis("assessment-1")
            assert result["probable_condition"] == "ACL Sprain"
