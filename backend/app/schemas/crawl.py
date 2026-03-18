from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class CrawledItemOut(BaseModel):
    id: str
    source: str
    source_url: str
    title: str
    summary: str
    category_tags: list[str] | None = None
    popularity_score: int
    crawl_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class CrawlRunResponse(BaseModel):
    status: str
    items_count: int
    sources: list[str]
