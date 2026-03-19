from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database import get_db
from app.models import Topic, TopicStatus
from app.notification.handler import NotificationHandler
from app.notification.dingding import DingDingBot

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/send-topics")
async def send_topics(db: AsyncSession = Depends(get_db)):
    """Manually trigger sending candidate topics to DingDing."""
    from datetime import datetime

    today = datetime.now().date()
    result = await db.execute(
        select(Topic).where(
            Topic.status == TopicStatus.CANDIDATE,
            Topic.created_at >= datetime.combine(today, datetime.min.time()),
        ).order_by(Topic.priority.desc())
    )
    topics = result.scalars().all()

    if not topics:
        return {"status": "no_topics", "message": "No candidate topics found for today"}

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
    send_result = await handler.push_topics(topic_dicts)
    await handler.close()

    return {
        "status": "sent",
        "topics_count": len(topics),
        "dingding_response": send_result,
    }


@router.post("/callback")
async def dingding_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle DingDing callback for topic confirmation.

    DingDing sends user replies to this endpoint.
    Expected payload includes 'text' with the user's message.
    """
    try:
        body = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    # Extract message text from DingDing callback format
    text = body.get("text", {}).get("content", "").strip()
    if not text:
        return {"status": "ignored", "message": "No text content"}

    logger.info(f"[callback] Received DingDing reply: {text}")

    # Get today's candidate topics
    from datetime import datetime
    today = datetime.now().date()
    result = await db.execute(
        select(Topic).where(
            Topic.status == TopicStatus.CANDIDATE,
            Topic.created_at >= datetime.combine(today, datetime.min.time()),
        ).order_by(Topic.priority.desc())
    )
    candidates = list(result.scalars().all())

    if not candidates:
        return {"status": "no_candidates", "message": "No candidate topics to confirm"}

    # Parse confirmation
    handler = NotificationHandler()
    indices = handler.parse_confirmation(text, len(candidates))
    await handler.close()

    if not indices:
        return {"status": "no_match", "message": f"Could not parse confirmation from: {text}"}

    # Confirm selected topics
    confirmed_titles = []
    for idx in indices:
        topic = candidates[idx]
        topic.status = TopicStatus.CONFIRMED
        topic.confirmation_date = datetime.now()
        confirmed_titles.append(topic.title)

    await db.flush()

    logger.info(f"[callback] Confirmed {len(confirmed_titles)} topics: {confirmed_titles}")
    return {
        "status": "confirmed",
        "confirmed_count": len(confirmed_titles),
        "confirmed_topics": confirmed_titles,
    }
