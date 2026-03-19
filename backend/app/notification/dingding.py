from __future__ import annotations

import hashlib
import hmac
import base64
import time
import urllib.parse
from typing import Any

import httpx
from loguru import logger

from app.config import get_settings


class DingDingBot:
    """DingDing Robot webhook integration."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = httpx.AsyncClient(timeout=15.0)

    async def close(self) -> None:
        await self._client.aclose()

    def _sign(self) -> tuple[str, str]:
        """Generate HMAC-SHA256 signature for DingDing API."""
        timestamp = str(round(time.time() * 1000))
        secret = self.settings.dingding_secret
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def _build_url(self) -> str:
        """Build the full webhook URL with signature."""
        base_url = self.settings.dingding_webhook_url
        if self.settings.dingding_secret:
            timestamp, sign = self._sign()
            separator = "&" if "?" in base_url else "?"
            return f"{base_url}{separator}timestamp={timestamp}&sign={sign}"
        return base_url

    async def send_text(self, content: str, at_all: bool = False) -> dict:
        """Send a text message."""
        data = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {"isAtAll": at_all},
        }
        return await self._send(data)

    async def send_markdown(self, title: str, text: str, at_all: bool = False) -> dict:
        """Send a markdown message."""
        data = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {"isAtAll": at_all},
        }
        return await self._send(data)

    async def send_action_card(
        self,
        title: str,
        text: str,
        buttons: list[dict[str, str]] | None = None,
        single_title: str = "",
        single_url: str = "",
    ) -> dict:
        """Send an action card message."""
        action_card: dict[str, Any] = {"title": title, "text": text}
        if buttons:
            action_card["btns"] = buttons
            action_card["btnOrientation"] = "0"
        elif single_title and single_url:
            action_card["singleTitle"] = single_title
            action_card["singleURL"] = single_url

        data = {"msgtype": "actionCard", "actionCard": action_card}
        return await self._send(data)

    async def send_topic_list(self, topics: list[dict]) -> dict:
        """Send a formatted topic list for user confirmation.

        Args:
            topics: List of dicts with 'id', 'title', 'category', 'priority', 'description'
        """
        lines = ["## 📋 今日候选话题\n"]

        for i, topic in enumerate(topics, 1):
            category = topic.get("category", "")
            title = topic.get("title", "")
            priority = topic.get("priority", 5)
            description = topic.get("description", "")
            stars = "⭐" * min(priority // 2, 5)

            lines.append(f"**{i}. [{category}] {title}**")
            if description:
                lines.append(f"> {description[:80]}")
            lines.append(f"热度: {stars}\n")

        lines.append("---")
        lines.append("**回复编号确认话题，如: 1,3,5**")
        lines.append("**回复 \"全部\" 确认所有话题**")

        text = "\n".join(lines)
        return await self.send_markdown("今日候选话题", text)

    async def _send(self, data: dict) -> dict:
        """Send a message to DingDing."""
        if not self.settings.dingding_webhook_url:
            logger.warning("[dingding] Webhook URL not configured, skipping send")
            return {"errcode": -1, "errmsg": "webhook not configured"}

        url = self._build_url()
        try:
            response = await self._client.post(url, json=data)
            result = response.json()
            if result.get("errcode") != 0:
                logger.error(f"[dingding] Send failed: {result}")
            else:
                logger.info("[dingding] Message sent successfully")
            return result
        except Exception as e:
            logger.error(f"[dingding] Send error: {e}")
            return {"errcode": -1, "errmsg": str(e)}

    async def __aenter__(self) -> DingDingBot:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
