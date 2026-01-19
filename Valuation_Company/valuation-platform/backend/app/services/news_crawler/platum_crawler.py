"""
Platum Crawler
플래텀 (전문 스타트업 매체) 크롤러

@task Investment Tracker
@description 플래텀에서 스타트업 투자 뉴스 수집
"""
import re
import logging
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

from app.services.news_crawler.base_crawler import BaseCrawler, CrawledNews

logger = logging.getLogger(__name__)


class PlatumCrawler(BaseCrawler):
    """
    플래텀 크롤러
    스타트업 전문 매체로 투자 뉴스 품질이 높음
    """

    def __init__(self):
        super().__init__(
            source_name="platum",
            base_url="https://platum.kr"
        )

    async def get_search_results(
        self,
        keywords: List[str],
        max_pages: int = 3
    ) -> List[str]:
        """
        플래텀 투자 관련 뉴스 URL 추출

        Args:
            keywords: 검색 키워드 목록
            max_pages: 최대 페이지 수

        Returns:
            뉴스 URL 목록
        """
        urls = []

        # 투자 관련 키워드로 검색
        search_keywords = [
            "투자 유치",
            "시리즈A",
            "시리즈B",
            "시드 투자",
            "펀딩"
        ]

        for keyword in search_keywords:
            for page in range(1, max_pages + 1):
                if page == 1:
                    search_url = f"{self.base_url}/?s={keyword.replace(' ', '+')}"
                else:
                    search_url = f"{self.base_url}/page/{page}/?s={keyword.replace(' ', '+')}"

                html = await self.fetch_page(search_url)
                if not html:
                    continue

                soup = self.parse_html(html)

                # 다양한 셀렉터 시도
                selectors = [
                    "article.post h2.entry-title a",
                    "h2.entry-title a",
                    "article a[href*='/archives/']",
                    ".post-title a",
                    "a.article-link"
                ]

                for selector in selectors:
                    articles = soup.select(selector)
                    if articles:
                        for article in articles:
                            href = article.get("href", "")
                            if href and "/archives/" in href:
                                urls.append(href)
                        break

                logger.debug(f"Found items for '{keyword}' page {page}")

        return urls

    async def parse_article(self, url: str) -> Optional[CrawledNews]:
        """
        플래텀 기사 파싱

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
            title_elem = soup.select_one("h1.entry-title") or soup.select_one("header.entry-header h1")
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title:
                logger.warning(f"No title found for {url}")
                return None

            # 본문 추출
            content_elem = soup.select_one("div.entry-content")
            if content_elem:
                # 불필요한 요소 제거
                for tag in content_elem.select("script, style, iframe, .ad, .advertisement"):
                    tag.decompose()
                content = content_elem.get_text(separator="\n", strip=True)
            else:
                content = ""

            # 투자 관련 뉴스인지 확인 (플래텀은 대부분 관련 뉴스이지만 필터링)
            if not self.is_investment_news(title, content):
                logger.debug(f"Skipping non-investment news: {title}")
                return None

            # 날짜 추출
            date_elem = soup.select_one("time.entry-date") or soup.select_one("span.posted-on time")
            published_at = None
            if date_elem:
                date_str = date_elem.get("datetime", "") or date_elem.get_text(strip=True)
                published_at = self._parse_date(date_str)

            # 작성자 추출
            author_elem = soup.select_one("span.author a") or soup.select_one("a.author-name")
            author = author_elem.get_text(strip=True) if author_elem else "플래텀"

            return CrawledNews(
                source="platum",
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
            logger.error(f"Error parsing Platum article {url}: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        날짜 문자열 파싱

        Args:
            date_str: 날짜 문자열 (ISO 형식 또는 한글)

        Returns:
            datetime 객체 또는 None
        """
        if not date_str:
            return None

        # ISO 형식 처리 (datetime 속성)
        try:
            # 2024-01-15T09:00:00+09:00 형식
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00").split("+")[0])
        except ValueError:
            pass

        # 한글 날짜 형식 처리
        patterns = [
            (r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", "%Y-%m-%d"),
            (r"(\d{4})\.(\d{1,2})\.(\d{1,2})", "%Y-%m-%d"),
            (r"(\d{4})-(\d{1,2})-(\d{1,2})", "%Y-%m-%d"),
        ]

        for pattern, _ in patterns:
            match = re.search(pattern, date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day))

        return None
