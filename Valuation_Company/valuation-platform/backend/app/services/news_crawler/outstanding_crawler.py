"""
Outstanding News Crawler
아웃스탠딩 뉴스 크롤러
"""
import logging
from typing import List, Optional
from app.services.news_crawler.base_crawler import BaseCrawler, CrawledNews

logger = logging.getLogger(__name__)

class OutstandingCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(source_name="outstanding", base_url="https://outstanding.kr")

    async def get_search_results(self, keywords: List[str], max_pages: int = 1) -> List[str]:
        urls = []
        # 투자 섹션: https://outstanding.kr/category/investment
        target_url = f"{self.base_url}/category/investment"
        html = await self.fetch_page(target_url)
        if not html: return []
        
        soup = self.parse_html(html)
        items = soup.select("h2 a")
        for item in items:
            href = item.get("href")
            if href: urls.append(href)
        return list(set(urls))

    async def parse_article(self, url: str) -> Optional[CrawledNews]:
        html = await self.fetch_page(url)
        if not html: return None
        soup = self.parse_html(html)
        try:
            title = soup.select_one("h1").get_text(strip=True)
            content = soup.select_one("section.post-content").get_text(strip=True)
            if not self.is_investment_news(title, content): return None
            return CrawledNews(source="outstanding", source_url=url, title=title, content=content)
        except Exception: return None
