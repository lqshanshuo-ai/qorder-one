from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Content(Base):
    __tablename__ = "contents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    topic_id: Mapped[str] = mapped_column(String(36), ForeignKey("topics.id"), index=True)
    research_summary: Mapped[str] = mapped_column(Text, default="")
    outline: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    key_points: Mapped[list | None] = mapped_column(JSON, nullable=True)
    target_audience: Mapped[str] = mapped_column(String(200), default="general")
    tone: Mapped[str] = mapped_column(String(100), default="informative")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    topic: Mapped["Topic"] = relationship(back_populates="contents")
    scripts: Mapped[list["Script"]] = relationship(back_populates="content", lazy="selectin")


class Script(Base):
    __tablename__ = "scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id: Mapped[str] = mapped_column(String(36), ForeignKey("contents.id"), index=True)
    full_text: Mapped[str] = mapped_column(Text, default="")
    segments: Mapped[list | None] = mapped_column(JSON, nullable=True)
    total_duration_seconds: Mapped[int] = mapped_column(Integer, default=75)
    title: Mapped[str] = mapped_column(String(500), default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    content: Mapped["Content"] = relationship(back_populates="scripts")


from app.models.topic import Topic  # noqa: E402
