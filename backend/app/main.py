from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.database import init_db
from app.scheduler.runner import setup_scheduler, start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    settings = get_settings()
    logger.info(f"Starting Content Creator Platform (env={settings.environment})")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Setup and start scheduler
    setup_scheduler()
    start_scheduler()
    logger.info("Scheduler started")

    yield

    # Shutdown
    shutdown_scheduler()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Content Creator Platform",
    description="Automated content creation pipeline for short video production",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
from app.api.crawl import router as crawl_router
from app.api.topics import router as topics_router
from app.api.content import router as content_router
from app.api.videos import router as videos_router
from app.api.analytics import router as analytics_router
from app.api.notifications import router as notifications_router

app.include_router(crawl_router)
app.include_router(topics_router)
app.include_router(content_router)
app.include_router(videos_router)
app.include_router(analytics_router)
app.include_router(notifications_router)


@app.get("/")
async def root():
    return {
        "name": "Content Creator Platform",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
