from __future__ import annotations

import re
from loguru import logger

from app.notification.dingding import DingDingBot


class NotificationHandler:
    """Handle DingDing notifications and parse user responses."""

    def __init__(self) -> None:
        self.bot = DingDingBot()

    async def push_topics(self, topics: list[dict]) -> dict:
        """Push candidate topics to user via DingDing."""
        return await self.bot.send_topic_list(topics)

    async def notify_content_ready(self, title: str, video_path: str) -> dict:
        """Notify user that content is ready for publishing."""
        text = (
            f"## ✅ 内容已生成\n\n"
            f"**话题**: {title}\n\n"
            f"**视频路径**: `{video_path}`\n\n"
            f"请查看output目录获取完整内容包"
        )
        return await self.bot.send_markdown("内容已生成", text)

    async def notify_error(self, step: str, error: str) -> dict:
        """Notify user of a pipeline error."""
        text = f"## ❌ 流程异常\n\n**步骤**: {step}\n\n**错误**: {error}"
        return await self.bot.send_markdown("流程异常", text)

    def parse_confirmation(self, message: str, total_topics: int) -> list[int]:
        """Parse user's topic confirmation reply.

        Args:
            message: User's reply text (e.g., "1,3,5" or "全部")
            total_topics: Total number of candidate topics

        Returns:
            List of confirmed topic indices (0-based)
        """
        text = message.strip()

        # Confirm all
        if text in ("全部", "all", "ALL", "所有"):
            return list(range(total_topics))

        # Parse comma-separated numbers
        indices: list[int] = []
        parts = re.split(r"[,，\s]+", text)
        for part in parts:
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1  # Convert to 0-based
                if 0 <= idx < total_topics:
                    indices.append(idx)
                else:
                    logger.warning(f"[handler] Invalid topic number: {part}")

        return sorted(set(indices))

    async def close(self) -> None:
        await self.bot.close()
