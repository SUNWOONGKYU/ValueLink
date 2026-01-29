"""
StartupToday News Crawler
스타트업투데이 뉴스 크롤러
"""
import logging
from typing import List, Optional
from app.services.news_crawler.base_crawler import BaseCrawler, CrawledNews

logger = logging.getLogger(__name__)

class StartupTodayCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(source_name="startuptoday", base_url="https://www.startuptoday.kr")

    async def get_search_results(self, keywords: List[str], max_pages: int = 1) -> List[str]:
        urls = []
        # 투자/M&A 섹션: https://www.startuptoday.kr/news/articleList.html?sc_section_code=S1N2&view_type=sm
        target_url = f"{self.base_url}/news/articleList.html?sc_section_code=S1N2"
        html = await self.fetch_page(target_url)
        if not html: return []
        
        soup = self.parse_html(html)
        items = soup.select("h4.titles a")
        for item in items:
            href = item.get("href")
            if href: urls.append(self.base_url + href if href.startswith("/") else href)
        return list(set(urls))

    async def parse_article(self, url: str) -> Optional[CrawledNews]:
        html = await self.fetch_page(url)
        if not html: return None
        soup = self.parse_html(html)
        try:
            title = soup.select_one("h3.heading").get_text(strip=True)
            content = soup.select_one("article#article-view-content-div").get_text(strip=True)
            if not self.is_investment_news(title, content): return None
            return CrawledNews(source="startuptoday", source_url=url, title=title, content=content)
        except Exception: return None
