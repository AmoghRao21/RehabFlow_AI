# RehabFlow AI

Production-grade AI-powered rehabilitation planning system using MedGemma and BLIP for clinical analysis.

## Architecture

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| Database | Supabase (PostgreSQL + Auth) |
| Cache | Redis |
| AI | Modal (BLIP image captioning + MedGemma-4B clinical reasoning) |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Modal account (for AI endpoints)
- Supabase project
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for running tests)

### 1. Clone & Configure

```bash
git clone https://github.com/SayedZahur786/RehabFlow_AI.git
cd RehabFlow_AI
cp .env.example .env
```

Fill in all required environment variables in `.env`.

### 2. Deploy the Modal AI Endpoint

```bash
pip install modal
modal setup          # One-time auth
modal deploy modal/endpoints/medgemma_endpoint.py
```

Copy the **analyze** endpoint URL (not the caption URL) to `MEDGEMMA_ENDPOINT` in `.env`.

### 3. Run with Docker

```bash
docker compose -f infrastructure/docker/docker-compose.yml up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| Health Check | http://localhost:8000/health |

### 4. Use the App

1. Sign up / Log in at http://localhost:3000
2. Complete the injury assessment (5 steps)
3. View your dashboard and click **"Analyze with AI"**
4. View the full rehabilitation plan

> **Note:** The first AI analysis may take 2-5 minutes (GPU cold start). Subsequent requests take ~30-60 seconds.

## Testing

Install test dependencies and run the test suite:

```bash
pip install -r tests/requirements-test.txt
python -m pytest tests/ -v
```

### Test Coverage

| File | Tests | Coverage |
|---|---|---|
| `test_cors.py` | 7 | CORS headers on success, errors, preflight, credentials |
| `test_ai_service.py` | 11 | Field mapping, Modal payload, fallback logic, error handling |
| `test_supabase_service.py` | 8 | Null safety on `maybe_single()`, ownership validation |
| `test_integration.py` | 6 | Full API request/response cycle, auth, CORS on errors |

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anonymous key |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `SUPABASE_JWT_SECRET` | JWT secret for token validation |
| `REDIS_URL` | Redis connection URL |
| `MEDGEMMA_ENDPOINT` | Modal **analyze** endpoint URL |
| `HUGGINGFACE_API_KEY` | HuggingFace token (for model access) |

## Project Structure

```
RehabFlow_AI/
├── backend/              # FastAPI backend
│   ├── core/             # Config, auth, logging
│   ├── routes/           # API route handlers
│   └── services/         # Business logic (AI, Supabase)
├── frontend/             # Next.js 15 frontend
│   └── app/[locale]/     # i18n pages (dashboard, assessment, rehab-plan)
├── modal/                # Modal AI endpoints
│   └── endpoints/        # BLIP + MedGemma pipeline
├── infrastructure/       # Docker configs
│   └── docker/           # Dockerfiles + docker-compose.yml
└── tests/                # Pytest test suite
    ├── conftest.py       # Shared fixtures
    ├── test_cors.py      # CORS configuration tests
    ├── test_ai_service.py       # AI service unit tests
    ├── test_supabase_service.py # Supabase null-safety tests
    └── test_integration.py      # End-to-end API tests
```

## Production Deployment

| Service | Platform |
|---|---|
| Backend | Railway |
| Frontend | Vercel |
| AI | Modal |
| Database | Supabase |
| Cache | Upstash Redis |
