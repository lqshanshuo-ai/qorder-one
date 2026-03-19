from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import (
    Publishing, Analytics, Platform, PublishStatus,
    Video, VideoStatus, Topic, TopicStatus, CrawledItem,
)
from app.schemas.video import AnalyticsIn, AnalyticsOut, PublishingOut, PipelineStatusOut
from app.pipeline.orchestrator import PipelineOrchestrator

router = APIRouter(prefix="/api", tags=["analytics"])


@router.post("/analytics/record", response_model=AnalyticsOut)
async def record_analytics(data: AnalyticsIn, db: AsyncSession = Depends(get_db)):
    """Record performance analytics for a published video."""
    pub = await db.get(Publishing, data.publishing_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publishing record not found")

    total_interactions = data.views + data.likes + data.comments + data.shares
    engagement_rate = (data.likes + data.comments + data.shares) / data.views if data.views > 0 else 0.0

    analytics = Analytics(
        publishing_id=data.publishing_id,
        views=data.views,
        likes=data.likes,
        comments=data.comments,
        shares=data.shares,
        engagement_rate=round(engagement_rate, 4),
        notes=data.notes,
    )
    db.add(analytics)
    await db.flush()
    return analytics


@router.get("/analytics/summary")
async def analytics_summary(db: AsyncSession = Depends(get_db)):
    """Get overall analytics summary."""
    result = await db.execute(
        select(
            func.sum(Analytics.views).label("total_views"),
            func.sum(Analytics.likes).label("total_likes"),
            func.sum(Analytics.comments).label("total_comments"),
            func.sum(Analytics.shares).label("total_shares"),
            func.avg(Analytics.engagement_rate).label("avg_engagement"),
            func.count(Analytics.id).label("total_records"),
        )
    )
    row = result.one()
    return {
        "total_views": row.total_views or 0,
        "total_likes": row.total_likes or 0,
        "total_comments": row.total_comments or 0,
        "total_shares": row.total_shares or 0,
        "avg_engagement_rate": round(float(row.avg_engagement or 0), 4),
        "total_records": row.total_records or 0,
    }


@router.get("/analytics/{publishing_id}", response_model=list[AnalyticsOut])
async def get_analytics(publishing_id: str, db: AsyncSession = Depends(get_db)):
    """Get analytics records for a specific publishing."""
    result = await db.execute(
        select(Analytics).where(Analytics.publishing_id == publishing_id)
        .order_by(Analytics.recorded_at.desc())
    )
    return result.scalars().all()


@router.post("/publishing/prepare/{video_id}", response_model=list[PublishingOut])
async def prepare_publishing(
    video_id: str,
    platforms: list[str] | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Prepare publishing metadata for a video."""
    pipeline = PipelineOrchestrator()
    publishings = await pipeline.run_publish_prep(db, video_id, platforms)
    return publishings


@router.get("/publishing", response_model=list[PublishingOut])
async def list_publishings(
    platform: str | None = None,
    status: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List publishing records."""
    query = select(Publishing).order_by(Publishing.created_at.desc())
    if platform:
        query = query.where(Publishing.platform == Platform(platform))
    if status:
        query = query.where(Publishing.status == PublishStatus(status))
    query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/pipeline/status", response_model=PipelineStatusOut)
async def pipeline_status(db: AsyncSession = Depends(get_db)):
    """Get current pipeline status."""
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())

    # Count today's items
    topics_result = await db.execute(
        select(func.count(Topic.id)).where(Topic.created_at >= today_start)
    )
    confirmed_result = await db.execute(
        select(func.count(Topic.id)).where(
            Topic.status == TopicStatus.CONFIRMED,
            Topic.created_at >= today_start,
        )
    )
    content_result = await db.execute(
        select(func.count(Topic.id)).where(
            Topic.status == TopicStatus.COMPLETED,
            Topic.created_at >= today_start,
        )
    )
    videos_result = await db.execute(
        select(func.count(Video.id)).where(
            Video.status == VideoStatus.COMPLETED,
            Video.created_at >= today_start,
        )
    )
    last_crawl_result = await db.execute(
        select(CrawledItem.crawl_date).order_by(CrawledItem.crawl_date.desc()).limit(1)
    )
    last_crawl = last_crawl_result.scalar_one_or_none()

    return PipelineStatusOut(
        crawl_status="idle",
        topics_today=topics_result.scalar() or 0,
        confirmed_topics=confirmed_result.scalar() or 0,
        content_generated=content_result.scalar() or 0,
        videos_generated=videos_result.scalar() or 0,
        last_crawl_time=last_crawl,
    )


@router.post("/pipeline/run")
async def run_full_pipeline(db: AsyncSession = Depends(get_db)):
    """Run the full pipeline: crawl -> select -> push."""
    pipeline = PipelineOrchestrator()
    items = await pipeline.run_crawl(db)
    topics = await pipeline.run_topic_selection(db)

    return {
        "crawled_items": len(items),
        "candidate_topics": len(topics),
        "topics": [{"id": t.id, "title": t.title, "category": t.category} for t in topics],
    }
