from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.health import router as health_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
