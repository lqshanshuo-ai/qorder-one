from app.crawlers.base import BaseCrawler, CrawledResult
from app.crawlers.manager import CrawlerManager
from app.crawlers.weibo import WeiboCrawler
from app.crawlers.zhihu import ZhihuCrawler
from app.crawlers.baidu import BaiduCrawler
from app.crawlers.scholar import ScholarCrawler

__all__ = [
    "BaseCrawler",
    "CrawledResult",
    "CrawlerManager",
    "WeiboCrawler",
    "ZhihuCrawler",
    "BaiduCrawler",
    "ScholarCrawler",
]
