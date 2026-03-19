from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Content, Script, Topic, TopicStatus
from app.schemas.content import ContentOut, ScriptOut, ContentGenerateRequest
from app.pipeline.orchestrator import PipelineOrchestrator

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/generate/{topic_id}")
async def generate_content(
    topic_id: str,
    request: ContentGenerateRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Trigger content generation (research + outline + script) for a confirmed topic."""
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if topic.status not in (TopicStatus.CONFIRMED, TopicStatus.CANDIDATE):
        raise HTTPException(
            status_code=400,
            detail=f"Topic status is '{topic.status.value}', must be 'confirmed' or 'candidate'",
        )

    duration = request.duration_seconds if request else 75
    pipeline = PipelineOrchestrator()
    result = await pipeline.run_content_generation(db, topic_id, duration)
    return result


@router.get("/{content_id}", response_model=ContentOut)
async def get_content(content_id: str, db: AsyncSession = Depends(get_db)):
    """Get generated content by ID."""
    content = await db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.get("/{content_id}/script", response_model=ScriptOut)
async def get_script(content_id: str, db: AsyncSession = Depends(get_db)):
    """Get the script for a content item."""
    result = await db.execute(
        select(Script).where(Script.content_id == content_id).order_by(Script.version.desc())
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script
