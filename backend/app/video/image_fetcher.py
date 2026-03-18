from __future__ import annotations

import httpx
from loguru import logger

from app.config import get_settings


class ImageFetcher:
    """Fetch relevant images from stock photo APIs (Unsplash, Pexels)."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def close(self) -> None:
        await self._client.aclose()

    async def fetch_images(self, keywords: list[str], count: int = 3) -> list[str]:
        """Fetch image URLs for given keywords. Returns list of image URLs."""
        urls: list[str] = []

        # Try Unsplash first
        if self.settings.unsplash_access_key:
            try:
                unsplash_urls = await self._fetch_unsplash(keywords, count)
                urls.extend(unsplash_urls)
            except Exception as e:
                logger.warning(f"[image_fetcher] Unsplash failed: {e}")

        # Fall back to Pexels
        if len(urls) < count and self.settings.pexels_api_key:
            try:
                remaining = count - len(urls)
                pexels_urls = await self._fetch_pexels(keywords, remaining)
                urls.extend(pexels_urls)
            except Exception as e:
                logger.warning(f"[image_fetcher] Pexels failed: {e}")

        if not urls:
            logger.warning(f"[image_fetcher] No images found for keywords: {keywords}")

        return urls[:count]

    async def _fetch_unsplash(self, keywords: list[str], count: int) -> list[str]:
        query = " ".join(keywords)
        response = await self._client.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": count, "orientation": "portrait"},
            headers={"Authorization": f"Client-ID {self.settings.unsplash_access_key}"},
        )
        response.raise_for_status()
        data = response.json()
        return [r["urls"]["regular"] for r in data.get("results", [])]

    async def _fetch_pexels(self, keywords: list[str], count: int) -> list[str]:
        query = " ".join(keywords)
        response = await self._client.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": count, "orientation": "portrait"},
            headers={"Authorization": self.settings.pexels_api_key},
        )
        response.raise_for_status()
        data = response.json()
        return [p["src"]["large2x"] for p in data.get("photos", [])]

    async def download_image(self, url: str, save_path: str) -> str:
        """Download an image to local path. Returns the save path."""
        response = await self._client.get(url)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path

    async def __aenter__(self) -> ImageFetcher:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
