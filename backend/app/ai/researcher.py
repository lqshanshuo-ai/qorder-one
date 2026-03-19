from __future__ import annotations

from loguru import logger

from app.ai.client import TongyiClient
from app.ai.prompts import render_prompt


class Researcher:
    """Deep research synthesis on a topic using AI."""

    def __init__(self, client: TongyiClient | None = None) -> None:
        self.client = client or TongyiClient(model="qwen-plus")

    async def research_topic(
        self,
        topic_title: str,
        topic_description: str,
        topic_category: str,
    ) -> str:
        """Perform deep research on a topic and return a comprehensive summary."""
        logger.info(f"[researcher] Researching: {topic_title}")

        system_prompt, user_prompt = render_prompt(
            "research",
            topic_title=topic_title,
            topic_description=topic_description,
            topic_category=topic_category,
        )

        result = await self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4096,
        )

        logger.info(f"[researcher] Generated {len(result)} chars of research for '{topic_title}'")
        return result

    async def generate_outline(self, research_summary: str) -> dict:
        """Generate a structured content outline from research."""
        logger.info("[researcher] Generating content outline")

        system_prompt, user_prompt = render_prompt(
            "outline",
            research_summary=research_summary,
        )

        result = await self.client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5,
        )

        return result
