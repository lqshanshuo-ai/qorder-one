from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class TopicOut(BaseModel):
    id: str
    title: str
    description: str
    category: str
    priority: int
    status: str
    reason: str = ""
    source_item_id: str | None = None
    confirmation_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TopicCreate(BaseModel):
    title: str
    description: str = ""
    category: str
    priority: int = Field(default=5, ge=1, le=10)


class TopicConfirmRequest(BaseModel):
    topic_ids: list[str] = Field(..., description="List of topic IDs to confirm")
