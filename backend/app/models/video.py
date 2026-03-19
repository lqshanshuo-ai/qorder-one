from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    topic_id: Mapped[str] = mapped_column(String(36), ForeignKey("topics.id"), index=True)
    script_id: Mapped[str] = mapped_column(String(36), ForeignKey("scripts.id"))
    file_path: Mapped[str] = mapped_column(String(1024), default="")
    cover_image_path: Mapped[str] = mapped_column(String(1024), default="")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    resolution: Mapped[str] = mapped_column(String(20), default="1080x1920")
    file_size_mb: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[VideoStatus] = mapped_column(
        SAEnum(VideoStatus), default=VideoStatus.PENDING, index=True
    )
    style_template: Mapped[str] = mapped_column(String(100), default="text_montage")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
