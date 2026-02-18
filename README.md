# RehabFlow AI

Production-grade AI-powered rehabilitation planning system.

## Architecture

Frontend: Next.js 15
Backend: FastAPI
Database: Supabase
Cache: Upstash Redis
AI: Modal (MedGemma, Whisper, BLIP2, NLLB)

## Local Development (Docker)

Clone repository:

git clone <repo-url>
cd rehabflow-ai

Copy environment file:

cp .env.example .env

Fill required environment variables.

Run system:

docker compose up --build

Backend runs on:
http://localhost:8000

Frontend runs on:
http://localhost:3000

## Health Check

http://localhost:8000/health

## Production Deployment

Backend: Railway
Frontend: Vercel
AI: Modal
Database: Supabase
Cache: Upstash Redis
