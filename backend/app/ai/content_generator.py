from __future__ import annotations

import json
from loguru import logger

from app.ai.client import TongyiClient
from app.ai.prompts import render_prompt, load_prompts
from app.crawlers.base import CrawledResult


class ContentGenerator:
    """High-level content generation orchestrating research, outline, and topic selection."""

    def __init__(self, client: TongyiClient | None = None) -> None:
        self.client = client or TongyiClient(model="qwen-plus")

    async def select_topics(
        self,
        crawled_items: list[dict],
        categories: list[str],
        max_topics: int = 8,
    ) -> list[dict]:
        """Use AI to select the best topics from crawled items.

        Returns list of dicts with: title, description, category, priority, reason
        """
        logger.info(f"[content_gen] Selecting topics from {len(crawled_items)} items")

        items_str = json.dumps(crawled_items[:50], ensure_ascii=False, indent=1)
        categories_str = ", ".join(categories)

        system_prompt, user_prompt = render_prompt(
            "topic_selection",
            crawled_items=items_str,
            categories=categories_str,
        )

        result = await self.client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5,
        )

        if isinstance(result, list):
            result = result[:max_topics]

        logger.info(f"[content_gen] Selected {len(result)} topics")
        return result
