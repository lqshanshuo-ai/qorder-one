from __future__ import annotations

import json
from typing import Any

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    import dashscope
    from dashscope import Generation
    HAS_DASHSCOPE = True
except ImportError:
    HAS_DASHSCOPE = False

from app.config import get_settings


class TongyiClient:
    """Client for Tongyi Qianwen (DashScope) API."""

    def __init__(self, model: str = "qwen-plus") -> None:
        self.settings = get_settings()
        self.model = model
        if HAS_DASHSCOPE and self.settings.dashscope_api_key:
            dashscope.api_key = self.settings.dashscope_api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text using Tongyi Qianwen."""
        if not HAS_DASHSCOPE:
            raise RuntimeError("dashscope package not installed. Run: pip install dashscope")
        if not self.settings.dashscope_api_key:
            raise RuntimeError("DASHSCOPE_API_KEY not configured")

        logger.debug(f"[tongyi] Generating with model={self.model}, temp={temperature}")

        response = Generation.call(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            result_format="message",
        )

        if response.status_code != 200:
            error_msg = f"Tongyi API error: {response.code} - {response.message}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        content = response.output.choices[0].message.content
        logger.debug(f"[tongyi] Generated {len(content)} chars")
        return content

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Any:
        """Generate and parse JSON output from Tongyi Qianwen."""
        raw = await self.generate(system_prompt, user_prompt, temperature, max_tokens)

        # Extract JSON from markdown code blocks if present
        cleaned = raw.strip()
        if "```json" in cleaned:
            start = cleaned.index("```json") + 7
            end = cleaned.index("```", start)
            cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            start = cleaned.index("```") + 3
            end = cleaned.index("```", start)
            cleaned = cleaned[start:end].strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"[tongyi] Failed to parse JSON: {e}\nRaw output: {raw[:500]}")
            raise ValueError(f"AI returned invalid JSON: {e}") from e
