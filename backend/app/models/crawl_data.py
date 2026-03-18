from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class CrawledItem(Base):
    __tablename__ = "crawled_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String(50), index=True)  # weibo, zhihu, baidu, arxiv, scholar
    source_url: Mapped[str] = mapped_column(String(1024), default="")
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text, default="")
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    crawl_date: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    category_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)  # list of strings
    popularity_score: Mapped[int] = mapped_column(Integer, default=0)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
