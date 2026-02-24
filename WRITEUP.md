# RehabFlow AI

### Project Name
**RehabFlow AI** — Multilingual, AI-Powered Rehabilitation Planning from Injury Images

---

### Your Team

| Name | Specialty | Role |
|------|-----------|------|
| *[Team Member 1]* | Machine Learning / Backend | AI pipeline design (BLIP + MedGemma), Modal GPU deployment, FastAPI backend |
| *[Team Member 2]* | Frontend / UX | Next.js 15 interface, multilingual i18n (8 languages), responsive assessment flow |
| *[Team Member 3]* | Data Engineering / Infra | Supabase schema design, Docker orchestration, CI/CD, Redis caching |

> ⚠️ **Replace the placeholder names above with your actual team members.**

---

### Problem Statement

**Rehabilitation is inaccessible for billions.** Over 2.4 billion people worldwide live with conditions that benefit from rehabilitation (WHO, 2024), yet access to qualified physiotherapists is severely limited — particularly in low-resource, rural, and non-English-speaking regions. Patients are often discharged from emergency rooms with generic "rest and ice" advice and no structured recovery plan. This gap leads to chronic pain, re-injury, lost productivity, and preventable disability.

**RehabFlow AI bridges this gap** by providing personalized, evidence-based rehabilitation plans generated from injury photographs and patient-reported symptoms — delivered instantly, in the patient's own language, with curated exercise videos. Our target users are:

- **Patients in underserved regions** who lack access to rehabilitation specialists
- **Primary care clinics** that need to triage and discharge patients with actionable recovery plans
- **Athletes and workers** recovering from musculoskeletal injuries who need structured guidance between clinic visits

**Impact Potential:** By automating the first-pass clinical assessment and plan generation, RehabFlow AI can reduce time-to-treatment from weeks (waiting for a specialist appointment) to minutes, while ensuring plans account for the patient's complete medical history, lifestyle, and pre-existing conditions.

---

### Overall Solution

RehabFlow AI is built around a **two-stage HAI-DEF model pipeline** running on serverless GPU infrastructure:

#### Stage 1 — Visual Understanding (BLIP-Large)
Injury images uploaded by the patient are processed by **Salesforce BLIP-Large** (`blip-image-captioning-large`) to generate detailed textual descriptions of visible injuries, swelling, bruising, and anatomical context. This converts unstructured visual data into structured input consumable by a language model.

#### Stage 2 — Clinical Reasoning (Google MedGemma-4B-IT)
The BLIP captions are combined with the patient's text complaint, pain location, pain level (1-10), baseline health profile (occupation, sitting hours, physical activity level), and pre-existing medical conditions into a structured clinical prompt. **Google MedGemma-4B-IT** — a medically fine-tuned Gemma model from HAI-DEF — then generates:

- **Probable Condition** with confidence score
- **Clinical Reasoning** incorporating visual and textual evidence
- **Phased Rehabilitation Plan:** Acute (Days 1-7) → Recovery (Weeks 2-4) → Strengthening (Weeks 4-8)
- **Precautions and Home Exercises** with specific sets/reps/duration

#### Stage 3 — Multilingual Access (NLLB-200)
The entire plan is translated into the patient's preferred language using **Meta NLLB-200-distilled-600M**, supporting 8 languages at launch: English, Hindi, French, German, Arabic, Japanese, Dutch, and Chinese. This ensures non-English-speaking patients receive plans they can actually follow.

#### Contextual Exercise Videos
For each recommended exercise, the system queries the **YouTube Data API v3** with a composite ranking algorithm (30% relevance + 35% views + 25% likes + 10% engagement ratio) to surface the best embeddable tutorial video — so patients can see exactly how to perform their exercises.

```
┌─────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│ Injury Photo │───▶│  BLIP-Large  │───▶│  MedGemma-4B-IT  │───▶│  NLLB-200    │
│ + Symptoms   │    │  (Captioning)│    │  (Clinical Plan) │    │ (Translation)│
└─────────────┘    └──────────────┘    └──────────────────┘    └──────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │ YouTube Exercise  │
                                    │ Video Matching    │
                                    └──────────────────┘
```

---

### Technical Details

#### Architecture Overview

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15 + TypeScript | Responsive UI with 5-step assessment wizard, rehab plan viewer, gamification dashboard |
| **Backend API** | FastAPI (Python) | REST API with JWT auth, request orchestration, data persistence |
| **AI Inference** | Modal (T4 GPU, 16 GB) | Serverless GPU for BLIP + MedGemma + NLLB-200, warm container pooling for low latency |
| **Database** | Supabase (PostgreSQL 15) | 16-table schema with Row-Level Security, handles profiles, assessments, plans, exercises, progress tracking |
| **Caching** | Upstash Redis | Session and response caching for sub-second repeated queries |
| **Auth** | Supabase Auth (ES256 JWT) | Secure user authentication with JWKS-based token verification |
| **Storage** | Supabase Storage | Private, encrypted injury image storage |
| **Containerization** | Docker Compose | Three-service orchestration (backend + frontend + Redis) |
| **Deployment** | Railway + Vercel + Modal | Backend on Railway, frontend on Vercel, AI on Modal — fully serverless |
| **i18n** | next-intl | Full internationalization across 8 languages |

#### Product Feasibility

**The system is fully functional and deployed.** Key production-readiness features:

1. **End-to-end pipeline in ~15 seconds:** Image upload → BLIP caption → MedGemma reasoning → plan display, all on a single T4 GPU with warm container pooling (zero cold-start after first inference).

2. **Data safety:** Row-Level Security on all 16 tables ensures patients can only access their own data. AI analysis results are only written by the service-role backend — never directly by client code. Images are stored in private Supabase Storage buckets.

3. **Clinical context awareness:** The system doesn't just look at the injury image — it factors in occupation type, daily sitting hours, physical work level, pre-existing conditions (diabetes, arthritis, hypertension, etc.), and lifestyle habits to generate truly personalized plans.

4. **5-Step Assessment Workflow:**
   - Step 1: Pain location & severity (11 body regions, 0-10 scale)
   - Step 2: Medical history & pre-existing conditions
   - Step 3: Lifestyle profile (occupation, activity level, habits)
   - Step 4: Injury image upload (multiple images supported)
   - Step 5: Review & submit for AI analysis

5. **Gamification layer:** Points, streaks, and progress tracking encourage patient adherence to their rehabilitation plan — a critical factor in recovery outcomes.

6. **Scalability:** Modal's serverless GPU auto-scales from zero to handle burst traffic. No GPU sits idle (and billing) when there are no requests. The `scaledown_window=300` configuration means containers stay warm for 5 minutes after the last request, balancing cost and latency.

#### Links

- **Video (≤3 min):** *[INSERT VIDEO LINK]*
- **Public Code Repository:** *[INSERT GITHUB LINK]*
- **Live Demo:** *[INSERT DEMO LINK IF AVAILABLE]*
- **HAI-DEF Model:** [MedGemma-4B-IT on Hugging Face](https://huggingface.co/google/medgemma-4b-it)

---

*RehabFlow AI — making rehabilitation accessible to everyone, everywhere, in every language.*
