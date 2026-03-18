from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Topic, TopicStatus
from app.schemas.topic import TopicOut, TopicCreate, TopicConfirmRequest

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("", response_model=list[TopicOut])
async def list_topics(
    status: str | None = None,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all topics with optional filtering."""
    query = select(Topic).order_by(Topic.created_at.desc())
    if status:
        query = query.where(Topic.status == TopicStatus(status))
    if category:
        query = query.where(Topic.category == category)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/candidates", response_model=list[TopicOut])
async def get_candidates(db: AsyncSession = Depends(get_db)):
    """Get today's candidate topics."""
    today = datetime.now().date()
    result = await db.execute(
        select(Topic).where(
            Topic.status == TopicStatus.CANDIDATE,
            Topic.created_at >= datetime.combine(today, datetime.min.time()),
        ).order_by(Topic.priority.desc())
    )
    return result.scalars().all()


@router.get("/{topic_id}", response_model=TopicOut)
async def get_topic(topic_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single topic by ID."""
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.post("", response_model=TopicOut)
async def create_topic(data: TopicCreate, db: AsyncSession = Depends(get_db)):
    """Create a manual topic."""
    topic = Topic(
        title=data.title,
        description=data.description,
        category=data.category,
        priority=data.priority,
        status=TopicStatus.CANDIDATE,
    )
    db.add(topic)
    await db.flush()
    return topic


@router.patch("/{topic_id}/confirm", response_model=TopicOut)
async def confirm_topic(topic_id: str, db: AsyncSession = Depends(get_db)):
    """Confirm a candidate topic for content generation."""
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if topic.status != TopicStatus.CANDIDATE:
        raise HTTPException(status_code=400, detail=f"Topic status is '{topic.status.value}', expected 'candidate'")

    topic.status = TopicStatus.CONFIRMED
    topic.confirmation_date = datetime.now()
    await db.flush()
    await db.refresh(topic)
    return topic


@router.patch("/{topic_id}/reject", response_model=TopicOut)
async def reject_topic(topic_id: str, db: AsyncSession = Depends(get_db)):
    """Reject a candidate topic."""
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic.status = TopicStatus.REJECTED
    await db.flush()
    await db.refresh(topic)
    return topic


@router.post("/confirm-batch", response_model=list[TopicOut])
async def confirm_batch(data: TopicConfirmRequest, db: AsyncSession = Depends(get_db)):
    """Confirm multiple topics at once."""
    confirmed: list[Topic] = []
    for topic_id in data.topic_ids:
        topic = await db.get(Topic, topic_id)
        if topic and topic.status == TopicStatus.CANDIDATE:
            topic.status = TopicStatus.CONFIRMED
            topic.confirmation_date = datetime.now()
            confirmed.append(topic)
    await db.flush()
    for topic in confirmed:
        await db.refresh(topic)
    return confirmed
