from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import CrawledItem
from app.schemas.crawl import CrawledItemOut, CrawlRunResponse
from app.crawlers.manager import CrawlerManager

router = APIRouter(prefix="/api/crawl", tags=["crawl"])


@router.post("/run", response_model=CrawlRunResponse)
async def run_crawl(
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger a crawl. Optionally specify a single source."""
    manager = CrawlerManager()
    if source:
        items = await manager.run_single(source, db)
    else:
        items = await manager.run_all(db)

    sources_crawled = list(set(item.source for item in items))
    return CrawlRunResponse(
        status="completed",
        items_count=len(items),
        sources=sources_crawled,
    )


@router.get("/items", response_model=list[CrawledItemOut])
async def list_crawled_items(
    source: str | None = None,
    date: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List crawled items with optional filtering."""
    query = select(CrawledItem).order_by(CrawledItem.crawl_date.desc())

    if source:
        query = query.where(CrawledItem.source == source)
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        query = query.where(
            CrawledItem.crawl_date >= datetime.combine(target_date, datetime.min.time()),
            CrawledItem.crawl_date < datetime.combine(target_date, datetime.max.time()),
        )

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sources")
async def list_sources():
    """List available crawl sources."""
    manager = CrawlerManager()
    return {"sources": manager.available_sources}
