from __future__ import annotations

from loguru import logger

from app.ai.client import TongyiClient
from app.ai.prompts import render_prompt


class ScriptWriter:
    """Generate narration scripts for short videos."""

    def __init__(self, client: TongyiClient | None = None) -> None:
        self.client = client or TongyiClient(model="qwen-plus")

    async def generate_script(
        self,
        outline: dict,
        duration_seconds: int = 75,
    ) -> dict:
        """Generate a timed narration script from an outline.

        Returns a dict with:
        - title: video title
        - segments: list of {text, overlay_text, duration_seconds, image_keywords}
        - total_duration_seconds: int
        """
        logger.info(f"[script_writer] Generating {duration_seconds}s script")

        import json
        outline_str = json.dumps(outline, ensure_ascii=False, indent=2)

        system_prompt, user_prompt = render_prompt(
            "script",
            outline=outline_str,
            duration=str(duration_seconds),
        )

        result = await self.client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5,
        )

        # Validate structure
        if "segments" not in result:
            raise ValueError("Script missing 'segments' field")

        # Build full text from segments
        full_text = "\n".join(seg.get("text", "") for seg in result["segments"])
        result["full_text"] = full_text

        logger.info(
            f"[script_writer] Generated script: {len(result['segments'])} segments, "
            f"~{result.get('total_duration_seconds', duration_seconds)}s"
        )
        return result

    async def generate_hashtags(
        self,
        title: str,
        summary: str,
        platform: str = "douyin",
    ) -> dict:
        """Generate platform-specific hashtags and captions.

        Returns a dict with:
        - title: post title
        - description: post description
        - hashtags: list of hashtag strings
        """
        logger.info(f"[script_writer] Generating hashtags for '{title}' on {platform}")

        system_prompt, user_prompt = render_prompt(
            "hashtags",
            title=title,
            summary=summary,
            platform=platform,
        )

        result = await self.client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5,
        )

        return result
