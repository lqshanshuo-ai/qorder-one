from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Float, DateTime, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Platform(str, enum.Enum):
    DOUYIN = "douyin"
    XIAOHONGSHU = "xiaohongshu"


class PublishStatus(str, enum.Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"


class Publishing(Base):
    __tablename__ = "publishings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(String(36), ForeignKey("videos.id"), index=True)
    platform: Mapped[Platform] = mapped_column(SAEnum(Platform))
    caption: Mapped[str] = mapped_column(Text, default="")
    hashtags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    cover_image_path: Mapped[str] = mapped_column(String(1024), default="")
    metadata_path: Mapped[str] = mapped_column(String(1024), default="")
    status: Mapped[PublishStatus] = mapped_column(
        SAEnum(PublishStatus), default=PublishStatus.PENDING, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Analytics(Base):
    __tablename__ = "analytics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    publishing_id: Mapped[str] = mapped_column(String(36), ForeignKey("publishings.id"), index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    notes: Mapped[str] = mapped_column(Text, default="")
