from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class CrawledResult:
    """Normalized result from any crawler."""
    source: str
    source_url: str
    title: str
    summary: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)
    category_tags: list[str] = field(default_factory=list)
    popularity_score: int = 0


class BaseCrawler(abc.ABC):
    """Abstract base class for all crawlers."""

    source_name: str = "unknown"

    def __init__(self, timeout: float = 30.0, proxy: str | None = None):
        transport = httpx.AsyncHTTPTransport(retries=2)
        self._client = httpx.AsyncClient(
            timeout=timeout,
            transport=transport,
            proxy=proxy,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
            follow_redirects=True,
        )

    async def close(self) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _fetch(self, url: str, **kwargs: Any) -> httpx.Response:
        """Fetch URL with retry logic."""
        logger.debug(f"[{self.source_name}] Fetching {url}")
        response = await self._client.get(url, **kwargs)
        response.raise_for_status()
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _post(self, url: str, **kwargs: Any) -> httpx.Response:
        """POST request with retry logic."""
        logger.debug(f"[{self.source_name}] POST {url}")
        response = await self._client.post(url, **kwargs)
        response.raise_for_status()
        return response

    @abc.abstractmethod
    async def crawl(self) -> list[CrawledResult]:
        """Crawl the source and return normalized results."""
        ...

    async def __aenter__(self) -> BaseCrawler:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
