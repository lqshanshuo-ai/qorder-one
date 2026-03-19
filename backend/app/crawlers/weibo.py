from __future__ import annotations

from bs4 import BeautifulSoup
from loguru import logger

from app.crawlers.base import BaseCrawler, CrawledResult


class WeiboCrawler(BaseCrawler):
    """Crawl Weibo hot search (trending topics)."""

    source_name = "weibo"

    # Weibo trending API endpoint
    TRENDING_URL = "https://weibo.com/ajax/side/hotSearch"

    async def crawl(self) -> list[CrawledResult]:
        results: list[CrawledResult] = []
        try:
            response = await self._fetch(self.TRENDING_URL)
            data = response.json()

            realtime = data.get("data", {}).get("realtime", [])
            for i, item in enumerate(realtime[:30]):
                title = item.get("word", "")
                if not title:
                    continue

                raw_num = item.get("raw_hot", item.get("num", 0))
                label_name = item.get("label_name", "")
                note = item.get("note", "")

                results.append(CrawledResult(
                    source="weibo",
                    source_url=f"https://s.weibo.com/weibo?q=%23{title}%23",
                    title=title,
                    summary=note or label_name,
                    raw_data=item,
                    category_tags=self._extract_tags(item),
                    popularity_score=self._calculate_score(raw_num, i),
                ))

            logger.info(f"[weibo] Crawled {len(results)} trending topics")
        except Exception as e:
            logger.error(f"[weibo] Crawl failed: {e}")
        return results

    def _extract_tags(self, item: dict) -> list[str]:
        tags = []
        if item.get("category"):
            tags.append(item["category"])
        if item.get("label_name"):
            tags.append(item["label_name"])
        return tags

    def _calculate_score(self, raw_num: int, rank: int) -> int:
        """Higher rank = higher score, adjusted by raw popularity."""
        rank_score = max(100 - rank * 3, 10)
        if raw_num > 1000000:
            rank_score += 30
        elif raw_num > 100000:
            rank_score += 15
        return min(rank_score, 100)
