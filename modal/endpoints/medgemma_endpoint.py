"""
RehabFlow AI — BLIP + MedGemma Clinical Analysis Endpoint (Modal)

Two-stage pipeline:
  1. BLIP-large captions the injury image(s) → text description
  2. MedGemma-4B receives caption + patient text → structured rehab plan

Deployed on Modal with T4 GPU (16 GB), FP16 precision, warm container pooling.

Usage:
    modal deploy modal/endpoints/medgemma_endpoint.py
    modal serve modal/endpoints/medgemma_endpoint.py   # local dev
"""

import base64
import io
import json
import logging
from typing import Optional

import modal
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("rehabflow.medgemma")
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Modal App & Container Image
# ---------------------------------------------------------------------------
BLIP_MODEL_ID = "Salesforce/blip-image-captioning-large"
MEDGEMMA_MODEL_ID = "google/medgemma-4b-it"

app = modal.App("rehabflow-medgemma")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "Pillow",
        "sentencepiece",
        "protobuf",
        "fastapi[standard]",
    )
)

# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    """Full analysis request: image(s) + text complaint + patient context."""
    images_base64: list[str] = Field(
        default_factory=list,
        description="Base64-encoded injury images (JPEG/PNG, no data-URI prefix)",
    )
    text_complaint: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Patient's text description of their injury/pain",
    )
    pain_location: str = Field(default="", description="e.g. knee, shoulder, back")
    pain_level: int = Field(default=5, ge=1, le=10)
    patient_context: dict = Field(
        default_factory=dict,
        description="Optional context: baseline profile, medical conditions, etc.",
    )


class CaptionRequest(BaseModel):
    """Debug endpoint: caption a single image."""
    image_base64: str = Field(
        ..., description="Base64-encoded image (no data-URI prefix)"
    )


class AnalyzeResponse(BaseModel):
    probable_condition: str
    confidence_score: float
    reasoning: str
    rehab_plan: str
    image_captions: list[str] = Field(default_factory=list)
    model_version: str


class CaptionResponse(BaseModel):
    caption: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# ---------------------------------------------------------------------------
# Clinical Analysis Service
# ---------------------------------------------------------------------------

@app.cls(
    image=image,
    gpu="T4",
    timeout=180,
    scaledown_window=300,
    retries=0,
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
@modal.concurrent(max_inputs=2)
class ClinicalAnalysisService:
    """
    Loads BLIP (captioning) and MedGemma-4B (reasoning) once on container
    start via @modal.enter().  All subsequent requests reuse the warm models.

    Total VRAM: ~1 GB (BLIP) + ~8.5 GB (MedGemma BF16) ≈ 9.5 GB on a 16 GB T4.
    """

    @modal.enter()
    def load_models(self):
        import torch
        from transformers import (
            AutoModelForCausalLM,
            AutoProcessor,
            AutoTokenizer,
            BlipForConditionalGeneration,
            BlipProcessor,
        )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # ── Load BLIP (image captioning) ─────────────────────────
        logger.info("Loading BLIP model: %s", BLIP_MODEL_ID)
        self.blip_processor = BlipProcessor.from_pretrained(BLIP_MODEL_ID)
        self.blip_model = BlipForConditionalGeneration.from_pretrained(
            BLIP_MODEL_ID,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
        )
        self.blip_model.eval()
        logger.info("BLIP loaded | device=%s", self.device)

        # ── Load MedGemma-4B (clinical reasoning) ────────────────
        logger.info("Loading MedGemma model: %s", MEDGEMMA_MODEL_ID)
        self.medgemma_tokenizer = AutoTokenizer.from_pretrained(MEDGEMMA_MODEL_ID)
        self.medgemma_model = AutoModelForCausalLM.from_pretrained(
            MEDGEMMA_MODEL_ID,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            low_cpu_mem_usage=True,
        )
        self.medgemma_model.eval()
        logger.info("MedGemma loaded | device=%s", self.device)

    # ── Internal helpers ─────────────────────────────────────────

    def _caption_image(self, image_b64: str) -> str:
        """Run BLIP captioning on a single base64-encoded image."""
        import torch
        from PIL import Image

        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        inputs = self.blip_processor(images=image, return_tensors="pt").to(
            self.device, torch.float16
        )

        with torch.no_grad():
            generated_ids = self.blip_model.generate(
                **inputs,
                max_new_tokens=100,
                num_beams=4,
                early_stopping=True,
            )

        caption = self.blip_processor.decode(
            generated_ids[0], skip_special_tokens=True
        )
        return caption.strip()

    def _build_medgemma_prompt(
        self,
        captions: list[str],
        text_complaint: str,
        pain_location: str,
        pain_level: int,
        patient_context: dict,
    ) -> str:
        """Build a structured prompt for MedGemma clinical reasoning."""

        # Build image description section
        image_section = ""
        if captions:
            image_descriptions = "\n".join(
                f"  - Image {i+1}: {cap}" for i, cap in enumerate(captions)
            )
            image_section = f"""
## Visual Assessment (from injury images)
{image_descriptions}
"""

        # Build patient context section
        context_section = ""
        if patient_context:
            context_parts = []
            if patient_context.get("occupation_type"):
                context_parts.append(f"- Occupation: {patient_context['occupation_type']}")
            if patient_context.get("daily_sitting_hours"):
                context_parts.append(f"- Daily sitting hours: {patient_context['daily_sitting_hours']}")
            if patient_context.get("physical_work_level"):
                context_parts.append(f"- Physical work level: {patient_context['physical_work_level']}")
            if patient_context.get("medical_conditions"):
                conditions = ", ".join(patient_context["medical_conditions"])
                context_parts.append(f"- Pre-existing conditions: {conditions}")
            if context_parts:
                context_section = "\n## Patient Context\n" + "\n".join(context_parts) + "\n"

        prompt = f"""You are a rehabilitation specialist AI assistant. Based on the following patient information, provide a comprehensive rehabilitation assessment and plan.

## Patient Complaint
- Location: {pain_location if pain_location else 'Not specified'}
- Pain level: {pain_level}/10
- Description: {text_complaint}
{image_section}{context_section}
## Instructions
Provide your response in the following structured format:

**Probable Condition:** [Your assessment of the most likely condition]

**Confidence:** [A score from 0.0 to 1.0]

**Clinical Reasoning:** [Detailed explanation of your assessment, incorporating the visual findings from the images and the patient's reported symptoms]

**Rehabilitation Plan:**
1. **Phase 1 — Acute (Days 1-7):** [Immediate steps, rest/ice/compression/elevation, pain management]
2. **Phase 2 — Recovery (Weeks 2-4):** [Gentle exercises, stretching, mobility work]
3. **Phase 3 — Strengthening (Weeks 4-8):** [Progressive strengthening, functional exercises]
4. **Precautions:** [What to avoid, when to seek medical attention]
5. **Home Exercises:** [Specific exercises with sets/reps/duration]

Be thorough, evidence-based, and always recommend consulting a healthcare professional for proper diagnosis."""

        return prompt

    def _run_medgemma(self, prompt: str) -> str:
        """Generate clinical analysis using MedGemma."""
        import torch

        # Use the chat template format for MedGemma
        messages = [
            {"role": "user", "content": prompt},
        ]

        input_text = self.medgemma_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.medgemma_tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.medgemma_model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.4,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.1,
            )

        # Decode only the newly generated tokens
        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        response = self.medgemma_tokenizer.decode(
            generated_tokens, skip_special_tokens=True
        )
        return response.strip()

    def _parse_medgemma_response(self, response: str) -> dict:
        """Extract structured fields from MedGemma's text response."""
        probable_condition = ""
        confidence_score = 0.7
        reasoning = ""
        rehab_plan = ""

        lines = response.split("\n")
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()

            if "probable condition" in line_lower:
                probable_condition = line.split(":", 1)[-1].strip().strip("*")
                current_section = None
            elif "confidence" in line_lower and ("0." in line or "1.0" in line):
                try:
                    # Extract the float value
                    import re
                    match = re.search(r"(0\.\d+|1\.0)", line)
                    if match:
                        confidence_score = float(match.group(1))
                except (ValueError, IndexError):
                    pass
                current_section = None
            elif "clinical reasoning" in line_lower:
                current_section = "reasoning"
            elif "rehabilitation plan" in line_lower:
                current_section = "rehab_plan"
            else:
                if current_section == "reasoning":
                    reasoning += line + "\n"
                elif current_section == "rehab_plan":
                    rehab_plan += line + "\n"

        return {
            "probable_condition": probable_condition or "Assessment pending further review",
            "confidence_score": confidence_score,
            "reasoning": reasoning.strip() or response,
            "rehab_plan": rehab_plan.strip() or response,
        }

    # ── Web endpoints ────────────────────────────────────────────

    @modal.fastapi_endpoint(method="POST", docs=True)
    def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """
        Full clinical analysis pipeline:
          1. Caption each injury image with BLIP
          2. Build structured prompt with captions + patient text
          3. Generate rehab plan with MedGemma
        """
        try:
            # Step 1: Caption images
            captions = []
            for i, img_b64 in enumerate(request.images_base64):
                logger.info("Captioning image %d/%d", i + 1, len(request.images_base64))
                caption = self._caption_image(img_b64)
                captions.append(caption)
                logger.info("Caption %d: %s", i + 1, caption)

            # Step 2: Build prompt
            prompt = self._build_medgemma_prompt(
                captions=captions,
                text_complaint=request.text_complaint,
                pain_location=request.pain_location,
                pain_level=request.pain_level,
                patient_context=request.patient_context,
            )

            # Step 3: Generate with MedGemma
            logger.info("Running MedGemma inference...")
            raw_response = self._run_medgemma(prompt)
            logger.info("MedGemma response length: %d chars", len(raw_response))

            # Step 4: Parse structured response
            parsed = self._parse_medgemma_response(raw_response)

            return AnalyzeResponse(
                probable_condition=parsed["probable_condition"],
                confidence_score=parsed["confidence_score"],
                reasoning=parsed["reasoning"],
                rehab_plan=parsed["rehab_plan"],
                image_captions=captions,
                model_version=f"blip:{BLIP_MODEL_ID}+medgemma:{MEDGEMMA_MODEL_ID}",
            )

        except Exception as e:
            logger.exception("Analysis failed")
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Internal Server Error",
                    detail="Clinical analysis generation failed. Please retry.",
                ).model_dump(),
            )

    @modal.fastapi_endpoint(method="POST", docs=True)
    def caption(self, request: CaptionRequest) -> CaptionResponse:
        """
        Debug endpoint: generate a BLIP caption for a single image.
        Useful for testing image quality and caption accuracy.
        """
        try:
            caption = self._caption_image(request.image_base64)
            return CaptionResponse(caption=caption)
        except Exception as e:
            logger.exception("Captioning failed")
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Internal Server Error",
                    detail="Image captioning failed. Please retry.",
                ).model_dump(),
            )
