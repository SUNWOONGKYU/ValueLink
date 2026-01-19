"""
VentureSquare Crawler
벤처스퀘어 크롤러

@task Investment Tracker
@description 벤처스퀘어에서 스타트업 투자 뉴스 수집
"""
import re
import logging
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

from app.services.news_crawler.base_crawler import BaseCrawler, CrawledNews

logger = logging.getLogger(__name__)


class VentureSquareCrawler(BaseCrawler):
    """
    벤처스퀘어 크롤러
    스타트업/벤처 전문 매체
    """

    def __init__(self):
        super().__init__(
            source_name="venturesquare",
            base_url="https://www.venturesquare.net"
        )

    async def get_search_results(
        self,
        keywords: List[str],
        max_pages: int = 3
    ) -> List[str]:
        """
        벤처스퀘어 뉴스에서 URL 추출

        Args:
            keywords: 검색 키워드 목록
            max_pages: 최대 페이지 수

        Returns:
            뉴스 URL 목록
        """
        urls = []

        # 뉴스 카테고리 페이지 크롤링
        for page in range(1, max_pages + 1):
            if page == 1:
                page_url = f"{self.base_url}/category/news-contents/news-trends/news/"
            else:
                page_url = f"{self.base_url}/category/news-contents/news-trends/news/page/{page}/"

            html = await self.fetch_page(page_url)
            if not html:
                continue

            soup = self.parse_html(html)

            # 기사 링크 추출 - 여러 셀렉터 시도
            selectors = [
                "article h2 a",
                "h2.entry-title a",
                ".post-title a",
                "article a[href*='venturesquare.net']"
            ]

            for selector in selectors:
                articles = soup.select(selector)
                if articles:
                    for article in articles:
                        href = article.get("href", "")
                        if href and "venturesquare.net" in href:
                            urls.append(href)
                    break

            logger.debug(f"Found {len(articles) if articles else 0} items from page {page}")

        # 키워드 검색 추가
        search_keywords = ["투자 유치", "시리즈A", "펀딩"]
        for keyword in search_keywords:
            search_url = f"{self.base_url}/?s={keyword.replace(' ', '+')}"
            html = await self.fetch_page(search_url)
            if html:
                soup = self.parse_html(html)
                for selector in selectors:
                    articles = soup.select(selector)
                    if articles:
                        for article in articles:
                            href = article.get("href", "")
                            if href and "venturesquare.net" in href:
                                urls.append(href)
                        break

        return list(set(urls))  # 중복 제거

    async def parse_article(self, url: str) -> Optional[CrawledNews]:
        """
        벤처스퀘어 기사 파싱

        Args:
            url: 뉴스 URL

        Returns:
            CrawledNews 객체 또는 None
        """
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # 제목 추출
            title_elem = soup.select_one("h1.entry-title") or soup.select_one("h1.post-title") or soup.select_one("h1")
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title:
                logger.warning(f"No title found for {url}")
                return None

            # 본문 추출
            content_elem = soup.select_one("div.entry-content") or soup.select_one("article .content")
            if content_elem:
                # 불필요한 요소 제거
                for tag in content_elem.select("script, style, iframe, .ad, .advertisement, .related-posts"):
                    tag.decompose()
                content = content_elem.get_text(separator="\n", strip=True)
            else:
                content = ""

            # 투자 관련 뉴스인지 확인
            if not self.is_investment_news(title, content):
                logger.debug(f"Skipping non-investment news: {title}")
                return None

            # 날짜 추출
            date_elem = soup.select_one("time.entry-date") or soup.select_one("span.date") or soup.select_one("time")
            published_at = None
            if date_elem:
                date_str = date_elem.get("datetime", "") or date_elem.get_text(strip=True)
                published_at = self._parse_date(date_str)

            # 작성자 추출
            author_elem = soup.select_one("span.author a") or soup.select_one(".author-name")
            author = author_elem.get_text(strip=True) if author_elem else "벤처스퀘어"

            return CrawledNews(
                source="venturesquare",
                source_url=url,
                title=title,
                content=content[:10000] if content else None,
                published_at=published_at,
                author=author,
                metadata={
                    "category": "investment"
                }
            )

        except Exception as e:
            logger.error(f"Error parsing VentureSquare article {url}: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        날짜 문자열 파싱

        Args:
            date_str: 날짜 문자열

        Returns:
            datetime 객체 또는 None
        """
        if not date_str:
            return None

        # ISO 형식 처리
        try:
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00").split("+")[0])
        except ValueError:
            pass

        # 한글 날짜 형식 처리
        patterns = [
            (r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", None),
            (r"(\d{4})\.(\d{1,2})\.(\d{1,2})", None),
            (r"(\d{4})-(\d{1,2})-(\d{1,2})", None),
        ]

        for pattern, _ in patterns:
            match = re.search(pattern, date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day))

        return None
