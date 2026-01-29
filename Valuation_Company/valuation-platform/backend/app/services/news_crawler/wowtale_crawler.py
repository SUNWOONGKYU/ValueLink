"""
Wowtale News Crawler
와우테일 뉴스 크롤러

@task Investment Tracker
@description 와우테일에서 스타트업 투자 뉴스 수집
"""
import logging
from typing import List, Optional
from app.services.news_crawler.base_crawler import BaseCrawler, CrawledNews

logger = logging.getLogger(__name__)


class WowtaleCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(
            source_name="wowtale",
            base_url="https://wowtale.net"
        )

    async def get_search_results(self, keywords: List[str], max_pages: int = 1) -> List[str]:
        urls = []
        # 와우테일은 '투자' 카테고리가 명확하므로 카테고리 페이지 직접 크롤링 권장
        # https://wowtale.net/category/investment/
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/category/investment/page/{page}/" if page > 1 else f"{self.base_url}/category/investment/"
            html = await self.fetch_page(url)
            if not html: continue
            
            soup = self.parse_html(html)
            # 기사 링크 추출 (와우테일 테마에 따라 셀렉터 조정 필요)
            items = soup.select("h2.entry-title a")
            for item in items:
                href = item.get("href")
                if href: urls.append(href)
        
        return list(set(urls))

    async def parse_article(self, url: str) -> Optional[CrawledNews]:
        html = await self.fetch_page(url)
        if not html: return None
        
        soup = self.parse_html(html)
        try:
            title = soup.select_one("h1.entry-title").get_text(strip=True)
            content_elem = soup.select_one("div.entry-content")
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # 투자 뉴스 검증
            if not self.is_investment_news(title, content):
                return None
                
            return CrawledNews(
                source="wowtale",
                source_url=url,
                title=title,
                content=content,
                published_at=None # 날짜 파싱 로직은 추후 보강
            )
        except Exception as e:
            logger.error(f"Error parsing Wowtale {url}: {e}")
            return None
