"""
RehabFlow AI — NLLB-200 Translation Endpoint (Modal)

Production-grade serverless translation using facebook/nllb-200-distilled-600M.
Deployed on Modal with T4 GPU, FP16 quantization, and warm container pooling.

Usage:
    modal deploy modal/endpoints/translate_endpoint.py
    modal serve modal/endpoints/translate_endpoint.py   # local dev
"""

import logging
from typing import Optional

import modal
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("rehabflow.translate")
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Modal App & Container Image
# ---------------------------------------------------------------------------
MODEL_ID = "facebook/nllb-200-distilled-600M"
MAX_INPUT_TOKENS = 512  # safe ceiling; NLLB supports 1024 but we leave headroom

app = modal.App("rehabflow-translate")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "sentencepiece",
    )
)

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: str = Field(..., description="NLLB BCP-47 code, e.g. eng_Latn")
    target_lang: str = Field(..., description="NLLB BCP-47 code, e.g. hin_Deva")


class TranslateResponse(BaseModel):
    translated_text: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# ---------------------------------------------------------------------------
# Translation Service (class-based for warm model caching)
# ---------------------------------------------------------------------------

@app.cls(
    image=image,
    gpu="T4",
    timeout=120,
    container_idle_timeout=300,
    allow_concurrent_inputs=4,
    retries=0,
)
class TranslationService:
    """
    Loads the NLLB-200 model once on container start via @modal.enter().
    All subsequent requests reuse the warm model — zero cold-load per request.
    """

    @modal.enter()
    def load_model(self):
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
        )
        self.model.eval()

        logger.info(
            "Model loaded: %s | device=%s | dtype=float16",
            MODEL_ID,
            self.device,
        )

    # ---- web endpoint ----

    @modal.web_endpoint(method="POST", docs=True)
    def translate(self, request: TranslateRequest) -> TranslateResponse:
        """
        Translate text between any two NLLB-200 supported languages.

        Language codes use NLLB BCP-47 format, e.g.:
            eng_Latn, hin_Deva, fra_Latn, deu_Latn, jpn_Jpan, zho_Hans, nld_Latn
        """
        import torch

        try:
            # Validate language codes exist in tokenizer vocab
            src_lang = request.source_lang
            tgt_lang = request.target_lang

            if src_lang not in self.tokenizer.additional_special_tokens:
                raise ValueError(f"Unsupported source language: {src_lang}")
            if tgt_lang not in self.tokenizer.additional_special_tokens:
                raise ValueError(f"Unsupported target language: {tgt_lang}")

            # Set source language for tokenizer
            self.tokenizer.src_lang = src_lang

            # Tokenize with truncation for safety
            inputs = self.tokenizer(
                request.text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=MAX_INPUT_TOKENS,
            ).to(self.device)

            # Resolve target language token ID
            tgt_lang_id = self.tokenizer.convert_tokens_to_ids(tgt_lang)

            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=tgt_lang_id,
                    max_new_tokens=MAX_INPUT_TOKENS,
                    num_beams=4,
                    early_stopping=True,
                )

            translated_text = self.tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )[0]

            return TranslateResponse(translated_text=translated_text)

        except ValueError as e:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=400,
                content=ErrorResponse(error="Bad Request", detail=str(e)).model_dump(),
            )
        except Exception as e:
            logger.exception("Translation failed")
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Internal Server Error",
                    detail="Translation generation failed. Please retry.",
                ).model_dump(),
            )
