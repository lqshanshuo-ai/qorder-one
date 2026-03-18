from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class ContentOut(BaseModel):
    id: str
    topic_id: str
    research_summary: str
    outline: dict | None = None
    key_points: list | None = None
    target_audience: str
    tone: str
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ScriptOut(BaseModel):
    id: str
    content_id: str
    title: str
    full_text: str
    segments: list | None = None
    total_duration_seconds: int
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentGenerateRequest(BaseModel):
    duration_seconds: int = 75
