from __future__ import annotations

from bs4 import BeautifulSoup
from loguru import logger

from app.crawlers.base import BaseCrawler, CrawledResult


class ZhihuCrawler(BaseCrawler):
    """Crawl Zhihu hot topics."""

    source_name = "zhihu"

    HOT_URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=30"

    async def crawl(self) -> list[CrawledResult]:
        results: list[CrawledResult] = []
        try:
            response = await self._fetch(
                self.HOT_URL,
                headers={
                    "Accept": "application/json",
                    "Referer": "https://www.zhihu.com/hot",
                },
            )
            data = response.json()

            for i, item in enumerate(data.get("data", [])):
                target = item.get("target", {})
                title = target.get("title", "")
                if not title:
                    continue

                excerpt = target.get("excerpt", "")
                detail_text = item.get("detail_text", "")
                url = target.get("url", "").replace("api.zhihu.com/questions", "www.zhihu.com/question")

                results.append(CrawledResult(
                    source="zhihu",
                    source_url=url,
                    title=title,
                    summary=excerpt[:500] if excerpt else detail_text,
                    raw_data={"target": target, "detail_text": detail_text},
                    category_tags=self._extract_tags(target),
                    popularity_score=self._calculate_score(item, i),
                ))

            logger.info(f"[zhihu] Crawled {len(results)} hot topics")
        except Exception as e:
            logger.error(f"[zhihu] Crawl failed: {e}")
        return results

    def _extract_tags(self, target: dict) -> list[str]:
        tags = []
        for topic in target.get("bound_topic_ids", []):
            tags.append(str(topic))
        return tags

    def _calculate_score(self, item: dict, rank: int) -> int:
        detail = item.get("detail_text", "")
        score = max(100 - rank * 3, 10)
        # Parse heat value from detail text like "2345 万热度"
        if "万" in detail:
            try:
                num = float(detail.replace("万热度", "").strip())
                if num > 1000:
                    score += 30
                elif num > 100:
                    score += 15
            except (ValueError, TypeError):
                pass
        return min(score, 100)
