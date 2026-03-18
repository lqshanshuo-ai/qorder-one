from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.pipeline.orchestrator import PipelineOrchestrator
from app.notification.handler import NotificationHandler


async def daily_crawl_job() -> None:
    """Scheduled job: run all crawlers daily."""
    logger.info("[scheduler] Running daily crawl job")
    try:
        async with async_session_factory() as db:
            pipeline = PipelineOrchestrator()
            items = await pipeline.run_crawl(db)
            await db.commit()
            logger.info(f"[scheduler] Daily crawl complete: {len(items)} items")
    except Exception as e:
        logger.error(f"[scheduler] Daily crawl failed: {e}")
        handler = NotificationHandler()
        await handler.notify_error("daily_crawl", str(e))
        await handler.close()


async def topic_push_job() -> None:
    """Scheduled job: select and push candidate topics."""
    logger.info("[scheduler] Running topic push job")
    try:
        async with async_session_factory() as db:
            pipeline = PipelineOrchestrator()
            topics = await pipeline.run_topic_selection(db)
            await db.commit()

            if topics:
                handler = NotificationHandler()
                topic_dicts = [
                    {
                        "id": t.id,
                        "title": t.title,
                        "category": t.category,
                        "priority": t.priority,
                        "description": t.description,
                    }
                    for t in topics
                ]
                await handler.push_topics(topic_dicts)
                await handler.close()
                logger.info(f"[scheduler] Pushed {len(topics)} candidate topics")
            else:
                logger.warning("[scheduler] No topics to push")
    except Exception as e:
        logger.error(f"[scheduler] Topic push failed: {e}")
