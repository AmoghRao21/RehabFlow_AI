# 📝 RehabFlow AI — Challenge Writeup Notes

## Problem Statement

Musculoskeletal conditions affect **1.7 billion people** globally (WHO, 2019). Access to physiotherapy is limited by cost, geography, and wait times. Many patients receive generic exercise handouts that don't account for their specific pain levels, functional limitations, or recovery trajectory.

**RehabFlow AI** addresses this gap by providing personalized, AI-generated home rehabilitation plans that adapt to each patient's progress — accessible offline, on any device with a browser.

---

## Approach

### Model Selection
- **MedGemma 1.5-4b-it** — Google's medical-domain multimodal LLM
- 4-bit quantization via bitsandbytes for consumer GPU compatibility
- Multimodal: accepts clinical images alongside text symptoms

### Prompt Engineering
- Safety-first system prompts with **red-flag screening** (cauda equina, fracture signs, etc.)
- Structured output format: Patient Overview → 14-Day Plan → Progression Rules → Safety → Tracking
- Conservative exercise selection: bodyweight/household items only
- Pain-guided progression: regress if pain increases, progress only when pain ≤3/10

### Architecture
- **Gradio 5.12** web interface — 3-tab design (Create, Progress, My Plans)
- **Offline-first** — all inference runs locally, plans stored as JSON
- **Demo Mode** — 4 expert-crafted clinical plans when model unavailable
- **PDF Export** — professional medical report via fpdf2
- **Voice Input** — Whisper tiny for progress note transcription

---

## Impact

### Who Benefits
1. **Patients** in rural/underserved areas without local physiotherapy
2. **Post-surgical patients** needing structured home exercise programs
3. **Elderly patients** with chronic conditions (OA, back pain) managing at home
4. **Clinicians** who can use it as a starting template to customize

### Safety Approach
- Every plan includes mandatory disclaimer
- Red-flag screening in every prompt
- Progressive overload principles with built-in regression criteria
- Prominent UI warnings against unsupervised use

### Limitations (Honest Assessment)
- AI cannot perform physical examination
- Image analysis is observational, not diagnostic
- Plans are educational starting points, not clinical prescriptions
- Requires clinical validation before any real-world deployment

---

## Technical Highlights

| Feature | Implementation |
|---------|---------------|
| Model | MedGemma 1.5-4b-it via `AutoModelForImageTextToText` |
| Quantization | 4-bit (bitsandbytes) + flash_attention_2 |
| CPU Fallback | float32, no quantization, demo plans |
| UI | Gradio Blocks, custom CSS, responsive |
| Persistence | JSON files in `plans/` directory |
| Export | Professional PDF via fpdf2 |
| Voice | Whisper tiny (optional) |

---

## Future Work
- Clinical validation with physiotherapy professionals
- Multi-language support for global accessibility
- Wearable sensor integration (accelerometer data for ROM tracking)
- Telemedicine integration (share plans with remote therapist)
- Longitudinal outcome tracking with visualization

---

## References
- WHO Global Burden of Disease — Musculoskeletal Conditions (2019)
- MedGemma Model Card: https://huggingface.co/google/medgemma-1.5-4b-it
- Exercise prescription guidelines: ACSM, NICE CKS
