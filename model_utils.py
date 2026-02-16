# ============================================================
# model_utils.py — MedGemma Model Loading & Inference
# RehabFlow AI — MedGemma Impact Challenge 2026
# ============================================================

import os
import torch
from PIL import Image
import warnings

warnings.filterwarnings("ignore")


def load_medgemma(force_cpu: bool = False):
    """
    Load MedGemma 1.5-4b-it with optimal settings.
    
    - GPU available → 4-bit quantization + flash_attention_2
    - CPU or force_cpu → float32, no quantization
    - Returns (processor, model) or (None, None) on failure
    """
    try:
        from transformers import AutoProcessor, AutoModelForImageTextToText
        from huggingface_hub import login
        from dotenv import load_dotenv

        load_dotenv()
        token = os.getenv("HF_TOKEN")
        if token and token != "your_token_here":
            login(token=token)
        
        model_id = "google/medgemma-1.5-4b-it"
        
        processor = AutoProcessor.from_pretrained(model_id)
        
        use_gpu = torch.cuda.is_available() and not force_cpu
        
        if use_gpu:
            model = AutoModelForImageTextToText.from_pretrained(
                model_id,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                load_in_4bit=True,
                attn_implementation="flash_attention_2",
            )
        else:
            model = AutoModelForImageTextToText.from_pretrained(
                model_id,
                device_map="cpu",
                torch_dtype=torch.float32,
            )
        
        return processor, model
    
    except Exception as e:
        print(f"[RehabFlow] ⚠ Model loading failed: {e}")
        print("[RehabFlow] ℹ Falling back to Demo Mode (no model).")
        return None, None


def run_medgemma(
    processor,
    model,
    prompt: str,
    image: Image.Image = None,
    max_tokens: int = 1200,
):
    """
    Run inference on MedGemma with optional image input.
    
    Returns the decoded text string.
    """
    if processor is None or model is None:
        return None  # Caller should use demo mode
    
    try:
        if image:
            inputs = processor(
                text=prompt, images=image, return_tensors="pt"
            ).to(model.device)
        else:
            inputs = processor(
                text=prompt, return_tensors="pt"
            ).to(model.device)
        
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.75,
                do_sample=True,
                top_p=0.9,
                pad_token_id=processor.tokenizer.pad_token_id,
            )
        
        decoded = processor.decode(outputs[0], skip_special_tokens=True)
        
        # Strip the input prompt from output if echoed
        if decoded.startswith(prompt):
            decoded = decoded[len(prompt):].strip()
        
        return decoded
    
    except Exception as e:
        print(f"[RehabFlow] ⚠ Inference error: {e}")
        return None
