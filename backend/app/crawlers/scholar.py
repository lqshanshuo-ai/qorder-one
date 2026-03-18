from __future__ import annotations

import re
from datetime import datetime, timedelta

from loguru import logger

from app.crawlers.base import BaseCrawler, CrawledResult


class ScholarCrawler(BaseCrawler):
    """Crawl academic papers from arXiv."""

    source_name = "scholar"

    # arXiv API for recent papers in relevant categories
    ARXIV_API = "http://export.arxiv.org/api/query"

    # Categories of interest
    CATEGORIES = [
        "cs.AI",   # Artificial Intelligence
        "cs.CL",   # Computation and Language (NLP)
        "cs.CV",   # Computer Vision
        "cs.LG",   # Machine Learning
        "econ.GN",  # General Economics
    ]

    async def crawl(self) -> list[CrawledResult]:
        results: list[CrawledResult] = []

        for category in self.CATEGORIES:
            try:
                items = await self._crawl_category(category)
                results.extend(items)
            except Exception as e:
                logger.error(f"[scholar] Failed to crawl {category}: {e}")

        logger.info(f"[scholar] Crawled {len(results)} papers total")
        return results

    async def _crawl_category(self, category: str) -> list[CrawledResult]:
        items: list[CrawledResult] = []
        params = {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": 10,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        response = await self._fetch(self.ARXIV_API, params=params)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml-xml")

        entries = soup.find_all("entry")
        for i, entry in enumerate(entries):
            title = entry.find("title")
            summary_el = entry.find("summary")
            link = entry.find("id")
            published = entry.find("published")

            if not title:
                continue

            title_text = re.sub(r"\s+", " ", title.get_text(strip=True))
            summary_text = re.sub(r"\s+", " ", summary_el.get_text(strip=True)) if summary_el else ""
            url = link.get_text(strip=True) if link else ""

            # Extract authors
            authors = [a.find("name").get_text(strip=True) for a in entry.find_all("author") if a.find("name")]

            items.append(CrawledResult(
                source="arxiv",
                source_url=url,
                title=title_text,
                summary=summary_text[:500],
                raw_data={
                    "category": category,
                    "authors": authors[:5],
                    "published": published.get_text(strip=True) if published else "",
                },
                category_tags=[category, "academic"],
                popularity_score=self._calculate_score(category, i),
            ))

        return items

    def _calculate_score(self, category: str, rank: int) -> int:
        base = 60
        # AI-related papers get a boost
        if category in ("cs.AI", "cs.LG", "cs.CL"):
            base = 70
        return max(base - rank * 2, 20)
