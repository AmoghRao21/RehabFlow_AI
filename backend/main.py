from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.health import router as health_router
from routes.ai import router as ai_router
from routes.youtube import router as youtube_router
from core.config import get_settings
from core.logger import get_logger
from db.redis import close_redis_client, get_redis_client
from db.supabase import get_supabase_client

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(
        "Starting RehabFlow AI backend | environment=%s",
        settings.environment,
    )

    # Initialize connections
    get_supabase_client()
    await get_redis_client()
    logger.info("All service connections established")

    yield

    # Graceful shutdown
    await close_redis_client()
    logger.info("RehabFlow AI backend shut down cleanly")


app = FastAPI(
    title="RehabFlow AI",
    description="Production backend for the RehabFlow AI medical rehabilitation platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware order matters: CORS must wrap auth so preflight works correctly
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://rehabflow-frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global catch-all handler — ensures unhandled exceptions still get CORS headers.
# Without this, a RuntimeError or other non-HTTPException would bypass the CORS
# middleware and the browser would show a CORS error instead of the actual error.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {type(exc).__name__}"},
    )


app.include_router(health_router)
app.include_router(ai_router)
app.include_router(youtube_router)

