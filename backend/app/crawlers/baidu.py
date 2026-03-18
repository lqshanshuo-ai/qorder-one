from __future__ import annotations

from bs4 import BeautifulSoup
from loguru import logger

from app.crawlers.base import BaseCrawler, CrawledResult


class BaiduCrawler(BaseCrawler):
    """Crawl Baidu hot search rankings."""

    source_name = "baidu"

    HOT_URL = "https://top.baidu.com/board?tab=realtime"

    async def crawl(self) -> list[CrawledResult]:
        results: list[CrawledResult] = []
        try:
            # Try the JSON API first
            api_results = await self._crawl_api()
            if api_results:
                return api_results

            # Fallback to HTML scraping
            response = await self._fetch(self.HOT_URL)
            soup = BeautifulSoup(response.text, "lxml")

            items = soup.select("div.category-wrap_iQLoo")
            for i, item in enumerate(items[:30]):
                title_el = item.select_one("div.c-single-text-ellipsis")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                desc_el = item.select_one("div.hot-desc_1m_jR")
                summary = desc_el.get_text(strip=True) if desc_el else ""
                hot_index_el = item.select_one("div.hot-index_1Bl1a")
                hot_index = int(hot_index_el.get_text(strip=True)) if hot_index_el else 0

                results.append(CrawledResult(
                    source="baidu",
                    source_url=f"https://www.baidu.com/s?wd={title}",
                    title=title,
                    summary=summary,
                    raw_data={"hot_index": hot_index, "rank": i + 1},
                    category_tags=[],
                    popularity_score=self._calculate_score(hot_index, i),
                ))

            logger.info(f"[baidu] Crawled {len(results)} hot search items")
        except Exception as e:
            logger.error(f"[baidu] Crawl failed: {e}")
        return results

    async def _crawl_api(self) -> list[CrawledResult]:
        """Try Baidu hot search JSON API."""
        results: list[CrawledResult] = []
        try:
            api_url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
            response = await self._fetch(api_url)
            data = response.json()

            cards = data.get("data", {}).get("cards", [])
            if not cards:
                return []

            content = cards[0].get("content", [])
            for i, item in enumerate(content[:30]):
                title = item.get("word", item.get("query", ""))
                if not title:
                    continue

                desc = item.get("desc", "")
                hot_score = int(item.get("hotScore", 0))
                url = item.get("url", f"https://www.baidu.com/s?wd={title}")

                results.append(CrawledResult(
                    source="baidu",
                    source_url=url,
                    title=title,
                    summary=desc,
                    raw_data=item,
                    category_tags=self._extract_tags(item),
                    popularity_score=self._calculate_score(hot_score, i),
                ))

            logger.info(f"[baidu] API crawled {len(results)} items")
        except Exception:
            return []
        return results

    def _extract_tags(self, item: dict) -> list[str]:
        tags = []
        if item.get("tag"):
            tags.append(item["tag"])
        return tags

    def _calculate_score(self, hot_index: int, rank: int) -> int:
        score = max(100 - rank * 3, 10)
        if hot_index > 5000000:
            score += 30
        elif hot_index > 1000000:
            score += 15
        return min(score, 100)
