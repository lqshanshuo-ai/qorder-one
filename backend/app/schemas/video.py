from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class VideoOut(BaseModel):
    id: str
    topic_id: str
    script_id: str
    file_path: str
    cover_image_path: str
    duration_seconds: int
    resolution: str
    file_size_mb: float
    status: str
    style_template: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PublishingOut(BaseModel):
    id: str
    video_id: str
    platform: str
    caption: str
    hashtags: list | None = None
    cover_image_path: str
    status: str
    published_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsIn(BaseModel):
    publishing_id: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    notes: str = ""


class AnalyticsOut(BaseModel):
    id: str
    publishing_id: str
    views: int
    likes: int
    comments: int
    shares: int
    engagement_rate: float
    recorded_at: datetime
    notes: str

    model_config = {"from_attributes": True}


class PipelineStatusOut(BaseModel):
    crawl_status: str
    topics_today: int
    confirmed_topics: int
    content_generated: int
    videos_generated: int
    last_crawl_time: datetime | None = None
