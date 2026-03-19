from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from app.database import get_db
from app.models import Video, VideoStatus, Script, Topic
from app.schemas.video import VideoOut
from app.video.generator import VideoGenerator

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("/generate/{script_id}")
async def generate_video(script_id: str, db: AsyncSession = Depends(get_db)):
    """Trigger video generation from a script."""
    script = await db.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    # Get content and topic
    from app.models import Content
    content = await db.get(Content, script.content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    topic = await db.get(Topic, content.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Create video record
    video = Video(
        topic_id=topic.id,
        script_id=script.id,
        status=VideoStatus.GENERATING,
    )
    db.add(video)
    await db.flush()

    # Generate video
    try:
        async with VideoGenerator() as gen:
            script_data = {
                "title": script.title,
                "segments": script.segments or [],
                "total_duration_seconds": script.total_duration_seconds,
            }
            result = await gen.generate(
                script_data=script_data,
                topic_title=topic.title,
                topic_category=topic.category,
            )

        video.file_path = result["video_path"]
        video.cover_image_path = result["cover_path"]
        video.duration_seconds = result["duration_seconds"]
        video.file_size_mb = result["file_size_mb"]
        video.status = VideoStatus.COMPLETED
        await db.flush()

    except Exception as e:
        video.status = VideoStatus.FAILED
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Video generation failed: {e}")

    return {
        "video_id": video.id,
        "status": video.status.value,
        "file_path": video.file_path,
        "cover_path": video.cover_image_path,
        "duration_seconds": video.duration_seconds,
    }


@router.get("", response_model=list[VideoOut])
async def list_videos(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all videos."""
    query = select(Video).order_by(Video.created_at.desc())
    if status:
        query = query.where(Video.status == VideoStatus(status))
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{video_id}", response_model=VideoOut)
async def get_video(video_id: str, db: AsyncSession = Depends(get_db)):
    """Get video details."""
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.get("/{video_id}/status")
async def get_video_status(video_id: str, db: AsyncSession = Depends(get_db)):
    """Check video generation status."""
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"video_id": video.id, "status": video.status.value}


@router.get("/{video_id}/download")
async def download_video(video_id: str, db: AsyncSession = Depends(get_db)):
    """Download a generated video file."""
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.status != VideoStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Video not ready")
    if not video.file_path:
        raise HTTPException(status_code=404, detail="Video file not found")

    import os
    if not os.path.exists(video.file_path):
        raise HTTPException(status_code=404, detail="Video file missing from disk")

    return FileResponse(
        video.file_path,
        media_type="video/mp4",
        filename=f"{video.id}.mp4",
    )
