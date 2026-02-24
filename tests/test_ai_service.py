"""
Tests for the AI service layer — field mapping, Modal endpoint call, and error handling.

Verifies that:
  1. `pain_cause` is correctly mapped to `text_complaint` (not the nonexistent `description`).
  2. Empty/null `pain_cause` falls back to a sensible default.
  3. `visible_swelling` and `mobility_restriction` are included in the complaint.
  4. `patient_context` is correctly built from baseline profile and conditions.
  5. Modal endpoint errors raise HTTPException (not RuntimeError).
  6. The payload sent to Modal matches the AnalyzeRequest schema.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Field mapping tests (the critical bug we fixed)
# ---------------------------------------------------------------------------

class TestTextComplaintMapping:
    """Verify that the backend correctly maps DB fields to Modal's text_complaint."""

    @pytest.mark.asyncio
    async def test_pain_cause_mapped_to_text_complaint(
        self, sample_assessment, sample_baseline_profile,
        sample_medical_conditions, sample_modal_response,
    ):
        """pain_cause should appear in the text_complaint sent to Modal."""
        captured_payload = {}

        async def mock_call_endpoint(**kwargs):
            captured_payload.update(kwargs)
            return sample_modal_response

        with patch("services.ai_service.validate_assessment_ownership", new_callable=AsyncMock, return_value=sample_assessment), \
             patch("services.ai_service.fetch_baseline_profile", new_callable=AsyncMock, return_value=sample_baseline_profile), \
             patch("services.ai_service.fetch_medical_conditions", new_callable=AsyncMock, return_value=sample_medical_conditions), \
             patch("services.ai_service.fetch_injury_images", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service._call_medgemma_endpoint", side_effect=mock_call_endpoint), \
             patch("services.ai_service.insert_clinical_analysis", new_callable=AsyncMock, return_value={"id": "test-id", **sample_modal_response}):

            from services.ai_service import run_clinical_analysis
            await run_clinical_analysis("test-assessment-id", "test-user-id")

        # The actual pain_cause text should be in the complaint
        text_complaint = captured_payload.get("text_complaint", "")
        assert "Sports injury while playing football" in text_complaint
        assert "twisted knee during tackle" in text_complaint

    @pytest.mark.asyncio
    async def test_description_field_not_used(
        self, sample_assessment, sample_baseline_profile,
        sample_medical_conditions, sample_modal_response,
    ):
        """
        The old code used assessment.get('description') which doesn't exist.
        Verify that even if 'description' is present, 'pain_cause' takes priority.
        """
        assessment_with_description = {**sample_assessment, "description": "This should NOT be used"}
        captured_payload = {}

        async def mock_call_endpoint(**kwargs):
            captured_payload.update(kwargs)
            return sample_modal_response

        with patch("services.ai_service.validate_assessment_ownership", new_callable=AsyncMock, return_value=assessment_with_description), \
             patch("services.ai_service.fetch_baseline_profile", new_callable=AsyncMock, return_value=sample_baseline_profile), \
             patch("services.ai_service.fetch_medical_conditions", new_callable=AsyncMock, return_value=sample_medical_conditions), \
             patch("services.ai_service.fetch_injury_images", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service._call_medgemma_endpoint", side_effect=mock_call_endpoint), \
             patch("services.ai_service.insert_clinical_analysis", new_callable=AsyncMock, return_value={"id": "test-id", **sample_modal_response}):

            from services.ai_service import run_clinical_analysis
            await run_clinical_analysis("test-assessment-id", "test-user-id")

        text_complaint = captured_payload.get("text_complaint", "")
        # pain_cause is primary source, not 'description'
        assert "Sports injury while playing football" in text_complaint
        assert "This should NOT be used" not in text_complaint

    @pytest.mark.asyncio
    async def test_null_pain_cause_falls_back_to_location(
        self, sample_assessment_minimal, sample_baseline_profile,
        sample_medical_conditions, sample_modal_response,
    ):
        """When pain_cause is null, fall back to 'Pain in {location}'."""
        captured_payload = {}

        async def mock_call_endpoint(**kwargs):
            captured_payload.update(kwargs)
            return sample_modal_response

        with patch("services.ai_service.validate_assessment_ownership", new_callable=AsyncMock, return_value=sample_assessment_minimal), \
             patch("services.ai_service.fetch_baseline_profile", new_callable=AsyncMock, return_value=sample_baseline_profile), \
             patch("services.ai_service.fetch_medical_conditions", new_callable=AsyncMock, return_value=sample_medical_conditions), \
             patch("services.ai_service.fetch_injury_images", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service._call_medgemma_endpoint", side_effect=mock_call_endpoint), \
             patch("services.ai_service.insert_clinical_analysis", new_callable=AsyncMock, return_value={"id": "test-id", **sample_modal_response}):

            from services.ai_service import run_clinical_analysis
            await run_clinical_analysis("test-assessment-id", "test-user-id")

        text_complaint = captured_payload.get("text_complaint", "")
        assert "Pain in lower_back" in text_complaint
        # Must not be empty (Modal requires min_length=1)
        assert len(text_complaint) >= 1

    @pytest.mark.asyncio
    async def test_text_complaint_never_empty(
        self, sample_modal_response,
    ):
        """text_complaint must NEVER be empty regardless of input."""
        empty_assessment = {
            "id": "test",
            "user_id": "test",
            "pain_location": "",
            "pain_level": 5,
            "pain_cause": "",
            "visible_swelling": False,
            "mobility_restriction": False,
            "additional_notes": "",
        }
        captured_payload = {}

        async def mock_call_endpoint(**kwargs):
            captured_payload.update(kwargs)
            return sample_modal_response

        with patch("services.ai_service.validate_assessment_ownership", new_callable=AsyncMock, return_value=empty_assessment), \
             patch("services.ai_service.fetch_baseline_profile", new_callable=AsyncMock, return_value=None), \
             patch("services.ai_service.fetch_medical_conditions", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service.fetch_injury_images", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service._call_medgemma_endpoint", side_effect=mock_call_endpoint), \
             patch("services.ai_service.insert_clinical_analysis", new_callable=AsyncMock, return_value={"id": "test-id", **sample_modal_response}):

            from services.ai_service import run_clinical_analysis
            await run_clinical_analysis("test-assessment-id", "test-user-id")

        text_complaint = captured_payload.get("text_complaint", "")
        assert len(text_complaint) >= 1, "text_complaint must never be empty"

    @pytest.mark.asyncio
    async def test_swelling_and_mobility_included(
        self, sample_assessment, sample_baseline_profile,
        sample_medical_conditions, sample_modal_response,
    ):
        """visible_swelling and mobility_restriction should be in the complaint."""
        captured_payload = {}

        async def mock_call_endpoint(**kwargs):
            captured_payload.update(kwargs)
            return sample_modal_response

        with patch("services.ai_service.validate_assessment_ownership", new_callable=AsyncMock, return_value=sample_assessment), \
             patch("services.ai_service.fetch_baseline_profile", new_callable=AsyncMock, return_value=sample_baseline_profile), \
             patch("services.ai_service.fetch_medical_conditions", new_callable=AsyncMock, return_value=sample_medical_conditions), \
             patch("services.ai_service.fetch_injury_images", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service._call_medgemma_endpoint", side_effect=mock_call_endpoint), \
             patch("services.ai_service.insert_clinical_analysis", new_callable=AsyncMock, return_value={"id": "test-id", **sample_modal_response}):

            from services.ai_service import run_clinical_analysis
            await run_clinical_analysis("test-assessment-id", "test-user-id")

        text_complaint = captured_payload.get("text_complaint", "")
        assert "swelling" in text_complaint.lower()
        assert "mobility" in text_complaint.lower()


# ---------------------------------------------------------------------------
# Patient context mapping tests
# ---------------------------------------------------------------------------

class TestPatientContextMapping:
    """Verify patient_context is built correctly from baseline + conditions."""

    @pytest.mark.asyncio
    async def test_patient_context_includes_baseline(
        self, sample_assessment, sample_baseline_profile,
        sample_medical_conditions, sample_modal_response,
    ):
        """patient_context should include baseline profile fields."""
        captured_payload = {}

        async def mock_call_endpoint(**kwargs):
            captured_payload.update(kwargs)
            return sample_modal_response

        with patch("services.ai_service.validate_assessment_ownership", new_callable=AsyncMock, return_value=sample_assessment), \
             patch("services.ai_service.fetch_baseline_profile", new_callable=AsyncMock, return_value=sample_baseline_profile), \
             patch("services.ai_service.fetch_medical_conditions", new_callable=AsyncMock, return_value=sample_medical_conditions), \
             patch("services.ai_service.fetch_injury_images", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service._call_medgemma_endpoint", side_effect=mock_call_endpoint), \
             patch("services.ai_service.insert_clinical_analysis", new_callable=AsyncMock, return_value={"id": "test-id", **sample_modal_response}):

            from services.ai_service import run_clinical_analysis
            await run_clinical_analysis("test-assessment-id", "test-user-id")

        ctx = captured_payload.get("patient_context", {})
        assert ctx.get("occupation_type") == "office_worker"
        assert ctx.get("daily_sitting_hours") == 8
        assert ctx.get("physical_work_level") == "sedentary"

    @pytest.mark.asyncio
    async def test_patient_context_includes_conditions(
        self, sample_assessment, sample_baseline_profile,
        sample_medical_conditions, sample_modal_response,
    ):
        """patient_context should include medical condition names."""
        captured_payload = {}

        async def mock_call_endpoint(**kwargs):
            captured_payload.update(kwargs)
            return sample_modal_response

        with patch("services.ai_service.validate_assessment_ownership", new_callable=AsyncMock, return_value=sample_assessment), \
             patch("services.ai_service.fetch_baseline_profile", new_callable=AsyncMock, return_value=sample_baseline_profile), \
             patch("services.ai_service.fetch_medical_conditions", new_callable=AsyncMock, return_value=sample_medical_conditions), \
             patch("services.ai_service.fetch_injury_images", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service._call_medgemma_endpoint", side_effect=mock_call_endpoint), \
             patch("services.ai_service.insert_clinical_analysis", new_callable=AsyncMock, return_value={"id": "test-id", **sample_modal_response}):

            from services.ai_service import run_clinical_analysis
            await run_clinical_analysis("test-assessment-id", "test-user-id")

        ctx = captured_payload.get("patient_context", {})
        conditions = ctx.get("medical_conditions", [])
        assert "Hypertension" in conditions
        assert "Asthma" in conditions

    @pytest.mark.asyncio
    async def test_patient_context_empty_when_no_baseline(
        self, sample_assessment, sample_modal_response,
    ):
        """patient_context should be empty dict when no baseline exists."""
        captured_payload = {}

        async def mock_call_endpoint(**kwargs):
            captured_payload.update(kwargs)
            return sample_modal_response

        with patch("services.ai_service.validate_assessment_ownership", new_callable=AsyncMock, return_value=sample_assessment), \
             patch("services.ai_service.fetch_baseline_profile", new_callable=AsyncMock, return_value=None), \
             patch("services.ai_service.fetch_medical_conditions", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service.fetch_injury_images", new_callable=AsyncMock, return_value=[]), \
             patch("services.ai_service._call_medgemma_endpoint", side_effect=mock_call_endpoint), \
             patch("services.ai_service.insert_clinical_analysis", new_callable=AsyncMock, return_value={"id": "test-id", **sample_modal_response}):

            from services.ai_service import run_clinical_analysis
            await run_clinical_analysis("test-assessment-id", "test-user-id")

        ctx = captured_payload.get("patient_context", {})
        assert "occupation_type" not in ctx
        assert "medical_conditions" not in ctx


# ---------------------------------------------------------------------------
# Modal endpoint call tests
# ---------------------------------------------------------------------------

class TestModalEndpointCall:
    """Verify the HTTP call to the Modal endpoint is correct."""

    @pytest.mark.asyncio
    async def test_modal_url_has_no_path_suffix(self):
        """The Modal URL should be used directly — no /analyze appended."""
        import httpx

        with patch("services.ai_service.httpx.AsyncClient") as MockClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "probable_condition": "Test",
                "confidence_score": 0.8,
                "reasoning": "Test reasoning",
                "rehab_plan": "Test plan",
                "image_captions": [],
                "model_version": "test",
            }

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client_instance

            from services.ai_service import _call_medgemma_endpoint
            await _call_medgemma_endpoint(
                images_base64=[],
                text_complaint="test complaint",
                pain_location="knee",
                pain_level=5,
                patient_context={},
            )

            # Verify the URL used — should be the endpoint directly, NOT with /analyze
            call_args = mock_client_instance.post.call_args
            url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
            assert url == "https://test-modal-endpoint.modal.run"
            assert "/analyze" not in url

    @pytest.mark.asyncio
    async def test_modal_error_raises_http_exception(self):
        """Non-200 from Modal should raise HTTPException, not RuntimeError."""
        from fastapi import HTTPException

        with patch("services.ai_service.httpx.AsyncClient") as MockClient:
            mock_response = MagicMock()
            mock_response.status_code = 422
            mock_response.text = '{"detail":"Validation error"}'

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client_instance

            from services.ai_service import _call_medgemma_endpoint
            with pytest.raises(HTTPException) as exc_info:
                await _call_medgemma_endpoint(
                    images_base64=[],
                    text_complaint="test",
                    pain_location="knee",
                    pain_level=5,
                    patient_context={},
                )

            assert exc_info.value.status_code == 502
            assert "422" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_modal_payload_matches_schema(self):
        """The payload sent to Modal should match AnalyzeRequest schema fields."""
        with patch("services.ai_service.httpx.AsyncClient") as MockClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "probable_condition": "Test",
                "confidence_score": 0.8,
                "reasoning": "Test",
                "rehab_plan": "Test",
                "image_captions": [],
                "model_version": "test",
            }

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client_instance

            from services.ai_service import _call_medgemma_endpoint
            await _call_medgemma_endpoint(
                images_base64=["base64data"],
                text_complaint="knee pain after running",
                pain_location="right_knee",
                pain_level=7,
                patient_context={"occupation_type": "office_worker"},
            )

            call_args = mock_client_instance.post.call_args
            payload = call_args[1].get("json", {})

            # Validate all required AnalyzeRequest fields are present
            assert "images_base64" in payload
            assert "text_complaint" in payload
            assert "pain_location" in payload
            assert "pain_level" in payload
            assert "patient_context" in payload

            # Validate values
            assert payload["images_base64"] == ["base64data"]
            assert payload["text_complaint"] == "knee pain after running"
            assert payload["pain_location"] == "right_knee"
            assert payload["pain_level"] == 7
            assert payload["patient_context"] == {"occupation_type": "office_worker"}
