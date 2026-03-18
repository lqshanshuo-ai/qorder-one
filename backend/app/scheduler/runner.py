from __future__ import annotations

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from app.config import get_settings
from app.scheduler.jobs import daily_crawl_job, topic_push_job


_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


def setup_scheduler() -> AsyncIOScheduler:
    """Configure and return the scheduler with all jobs."""
    settings = get_settings()
    scheduler = get_scheduler()

    # Daily crawl job
    scheduler.add_job(
        daily_crawl_job,
        trigger=CronTrigger(hour=settings.crawl_cron_hour, minute=0),
        id="daily_crawl",
        name="Daily content crawling",
        replace_existing=True,
    )

    # Topic push job
    scheduler.add_job(
        topic_push_job,
        trigger=CronTrigger(hour=settings.topic_push_cron_hour, minute=0),
        id="topic_push",
        name="Morning topic push",
        replace_existing=True,
    )

    logger.info(
        f"[scheduler] Configured: crawl@{settings.crawl_cron_hour}:00, "
        f"push@{settings.topic_push_cron_hour}:00"
    )
    return scheduler


def start_scheduler() -> None:
    """Start the scheduler."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("[scheduler] Started")


def shutdown_scheduler() -> None:
    """Shutdown the scheduler."""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[scheduler] Shut down")
