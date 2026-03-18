from __future__ import annotations

import enum
import json
from datetime import datetime
from pathlib import Path

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Topic, TopicStatus, Content, Script, Video, VideoStatus, Publishing, Platform
from app.ai.client import TongyiClient
from app.ai.researcher import Researcher
from app.ai.script_writer import ScriptWriter
from app.ai.content_generator import ContentGenerator
from app.crawlers.manager import CrawlerManager


class PipelineStep(str, enum.Enum):
    CRAWL = "crawl"
    SELECT_TOPICS = "select_topics"
    RESEARCH = "research"
    OUTLINE = "outline"
    SCRIPT = "script"
    VIDEO = "video"
    PUBLISH_PREP = "publish_prep"


class PipelineOrchestrator:
    """Orchestrate the full content creation pipeline."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = TongyiClient(model="qwen-plus")
        self.researcher = Researcher(self.client)
        self.script_writer = ScriptWriter(self.client)
        self.content_generator = ContentGenerator(self.client)
        self.crawler_manager = CrawlerManager()

    async def run_crawl(self, db: AsyncSession) -> list[dict]:
        """Step 1: Run all crawlers."""
        logger.info("[pipeline] Step: CRAWL")
        items = await self.crawler_manager.run_all(db)
        return [{"id": item.id, "title": item.title, "source": item.source} for item in items]

    async def run_topic_selection(self, db: AsyncSession) -> list[Topic]:
        """Step 2: Select candidate topics from today's crawled data."""
        logger.info("[pipeline] Step: SELECT_TOPICS")

        # Load today's crawled items
        from app.models.crawl_data import CrawledItem
        today = datetime.now().date()
        result = await db.execute(
            select(CrawledItem).where(
                CrawledItem.crawl_date >= datetime.combine(today, datetime.min.time()),
                CrawledItem.processed == False,
            ).order_by(CrawledItem.popularity_score.desc())
        )
        crawled_items = result.scalars().all()

        if not crawled_items:
            logger.warning("[pipeline] No crawled items found for today")
            return []

        # Prepare data for AI selection
        items_for_ai = [
            {
                "title": item.title,
                "summary": item.summary[:200],
                "source": item.source,
                "popularity_score": item.popularity_score,
                "tags": item.category_tags or [],
            }
            for item in crawled_items[:50]
        ]

        # Load category config
        import yaml
        categories_path = self.settings.config_dir / "topic_categories.yaml"
        categories = []
        if categories_path.exists():
            with open(categories_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                categories = [c["display_name"] for c in config.get("categories", []) if c.get("enabled")]

        # Use AI to select topics
        selected = await self.content_generator.select_topics(items_for_ai, categories)

        # Save as candidate topics
        topics: list[Topic] = []
        for item in selected:
            topic = Topic(
                title=item.get("title", ""),
                description=item.get("description", ""),
                category=item.get("category", "general"),
                priority=item.get("priority", 5),
                status=TopicStatus.CANDIDATE,
                reason=item.get("reason", ""),
            )
            db.add(topic)
            topics.append(topic)

        await db.flush()
        # Mark crawled items as processed
        for ci in crawled_items:
            ci.processed = True
        await db.flush()

        logger.info(f"[pipeline] Selected {len(topics)} candidate topics")
        return topics

    async def run_content_generation(self, db: AsyncSession, topic_id: str, duration_seconds: int = 75) -> dict:
        """Steps 3-5: Research, outline, and script generation for a confirmed topic."""
        logger.info(f"[pipeline] Running content generation for topic {topic_id}")

        # Get topic
        topic = await db.get(Topic, topic_id)
        if not topic:
            raise ValueError(f"Topic {topic_id} not found")

        topic.status = TopicStatus.IN_PROGRESS
        await db.flush()

        # Step 3: Research
        logger.info(f"[pipeline] Step: RESEARCH for '{topic.title}'")
        research_summary = await self.researcher.research_topic(
            topic_title=topic.title,
            topic_description=topic.description,
            topic_category=topic.category,
        )

        # Step 4: Outline
        logger.info(f"[pipeline] Step: OUTLINE for '{topic.title}'")
        outline = await self.researcher.generate_outline(research_summary)

        # Save content
        content = Content(
            topic_id=topic_id,
            research_summary=research_summary,
            outline=outline,
            key_points=[s.get("key_point", "") for s in outline.get("sections", [])],
        )
        db.add(content)
        await db.flush()

        # Step 5: Script
        logger.info(f"[pipeline] Step: SCRIPT for '{topic.title}'")
        script_data = await self.script_writer.generate_script(outline, duration_seconds)

        script = Script(
            content_id=content.id,
            title=script_data.get("title", topic.title),
            full_text=script_data.get("full_text", ""),
            segments=script_data.get("segments", []),
            total_duration_seconds=script_data.get("total_duration_seconds", duration_seconds),
        )
        db.add(script)
        await db.flush()

        logger.info(f"[pipeline] Content generation complete for '{topic.title}'")
        return {
            "topic_id": topic_id,
            "content_id": content.id,
            "script_id": script.id,
            "title": script.title,
            "segments_count": len(script.segments or []),
            "duration": script.total_duration_seconds,
        }

    async def run_publish_prep(
        self,
        db: AsyncSession,
        video_id: str,
        platforms: list[str] | None = None,
    ) -> list[Publishing]:
        """Step 7: Prepare publishing metadata for each platform."""
        if platforms is None:
            platforms = ["douyin", "xiaohongshu"]

        video = await db.get(Video, video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")

        topic = await db.get(Topic, video.topic_id)
        script = await db.get(Script, video.script_id)

        publishings: list[Publishing] = []
        for platform_name in platforms:
            platform = Platform(platform_name)

            # Generate platform-specific metadata
            hashtag_data = await self.script_writer.generate_hashtags(
                title=script.title if script else topic.title,
                summary=script.full_text[:300] if script else topic.description,
                platform=platform_name,
            )

            # Create output directory
            date_str = datetime.now().strftime("%Y-%m-%d")
            safe_title = "".join(c for c in topic.title[:30] if c.isalnum() or c in " _-").strip()
            output_dir = self.settings.output_path / date_str / safe_title / platform_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save metadata
            metadata = {
                "platform": platform_name,
                "title": hashtag_data.get("title", topic.title),
                "description": hashtag_data.get("description", ""),
                "hashtags": hashtag_data.get("hashtags", []),
                "video_path": video.file_path,
                "cover_image_path": video.cover_image_path,
                "script_text": script.full_text if script else "",
            }
            metadata_path = output_dir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # Save script text
            if script:
                script_path = output_dir / "script.txt"
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(f"标题：{script.title}\n\n")
                    f.write(f"时长：{script.total_duration_seconds}秒\n\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(script.full_text)

            pub = Publishing(
                video_id=video_id,
                platform=platform,
                caption=hashtag_data.get("description", ""),
                hashtags=hashtag_data.get("hashtags", []),
                cover_image_path=video.cover_image_path,
                metadata_path=str(metadata_path),
            )
            db.add(pub)
            publishings.append(pub)

        await db.flush()
        logger.info(f"[pipeline] Publish prep done for {len(publishings)} platforms")
        return publishings
