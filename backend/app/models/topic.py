from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TopicStatus(str, enum.Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    source_item_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("crawled_items.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[TopicStatus] = mapped_column(
        SAEnum(TopicStatus), default=TopicStatus.CANDIDATE, index=True
    )
    reason: Mapped[str] = mapped_column(Text, default="")
    confirmation_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    contents: Mapped[list["Content"]] = relationship(back_populates="topic", lazy="selectin")


# Avoid circular import - Content imported at module level
from app.models.content import Content  # noqa: E402
