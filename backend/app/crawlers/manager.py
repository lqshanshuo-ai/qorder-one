from __future__ import annotations

import asyncio
from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crawlers.base import BaseCrawler, CrawledResult
from app.crawlers.weibo import WeiboCrawler
from app.crawlers.zhihu import ZhihuCrawler
from app.crawlers.baidu import BaiduCrawler
from app.crawlers.scholar import ScholarCrawler
from app.models.crawl_data import CrawledItem


class CrawlerManager:
    """Orchestrate all crawlers, aggregate and deduplicate results."""

    def __init__(self) -> None:
        self._crawler_classes: list[type[BaseCrawler]] = [
            WeiboCrawler,
            ZhihuCrawler,
            BaiduCrawler,
            ScholarCrawler,
        ]

    async def run_all(self, db: AsyncSession) -> list[CrawledItem]:
        """Run all crawlers concurrently and save results to database."""
        logger.info("Starting crawl from all sources...")

        all_results: list[CrawledResult] = []

        # Run crawlers concurrently
        async def run_crawler(crawler_cls: type[BaseCrawler]) -> list[CrawledResult]:
            async with crawler_cls() as crawler:
                return await crawler.crawl()

        tasks = [run_crawler(cls) for cls in self._crawler_classes]
        results_per_source = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results_per_source:
            if isinstance(result, Exception):
                logger.error(f"Crawler failed: {result}")
                continue
            all_results.extend(result)

        # Deduplicate by title
        deduped = self._deduplicate(all_results)
        logger.info(f"Total crawled: {len(all_results)}, after dedup: {len(deduped)}")

        # Save to database
        saved_items = await self._save_to_db(db, deduped)
        return saved_items

    async def run_single(self, source: str, db: AsyncSession) -> list[CrawledItem]:
        """Run a single crawler by source name."""
        crawler_map = {cls.source_name: cls for cls in self._crawler_classes}
        crawler_cls = crawler_map.get(source)
        if not crawler_cls:
            raise ValueError(f"Unknown source: {source}. Available: {list(crawler_map.keys())}")

        async with crawler_cls() as crawler:
            results = await crawler.crawl()

        return await self._save_to_db(db, results)

    def _deduplicate(self, results: list[CrawledResult]) -> list[CrawledResult]:
        """Remove duplicate results by title similarity."""
        seen_titles: set[str] = set()
        deduped: list[CrawledResult] = []

        for item in results:
            normalized = item.title.strip().lower()
            if normalized not in seen_titles:
                seen_titles.add(normalized)
                deduped.append(item)

        return deduped

    async def _save_to_db(self, db: AsyncSession, results: list[CrawledResult]) -> list[CrawledItem]:
        """Persist crawled results to the database."""
        items: list[CrawledItem] = []
        today = datetime.now().date()

        for result in results:
            # Check if already exists today
            existing = await db.execute(
                select(CrawledItem).where(
                    CrawledItem.source == result.source,
                    CrawledItem.title == result.title,
                    CrawledItem.crawl_date >= datetime.combine(today, datetime.min.time()),
                )
            )
            if existing.scalar_one_or_none():
                continue

            item = CrawledItem(
                source=result.source,
                source_url=result.source_url,
                title=result.title,
                summary=result.summary,
                raw_data=result.raw_data,
                category_tags=result.category_tags,
                popularity_score=result.popularity_score,
            )
            db.add(item)
            items.append(item)

        await db.flush()
        logger.info(f"Saved {len(items)} new crawled items to database")
        return items

    @property
    def available_sources(self) -> list[str]:
        return [cls.source_name for cls in self._crawler_classes]
