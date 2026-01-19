"""
Naver News Crawler
네이버 뉴스 크롤러

@task Investment Tracker
@description 네이버 뉴스에서 스타트업 투자 뉴스 수집
"""
import re
import logging
from datetime import datetime
from typing import List, Optional
from urllib.parse import quote, urljoin

from app.services.news_crawler.base_crawler import BaseCrawler, CrawledNews

logger = logging.getLogger(__name__)


class NaverNewsCrawler(BaseCrawler):
    """
    네이버 뉴스 크롤러
    네이버 검색 API 대신 웹 크롤링 사용 (API 키 불필요)
    """

    def __init__(self):
        super().__init__(
            source_name="naver",
            base_url="https://search.naver.com/search.naver"
        )

    async def get_search_results(
        self,
        keywords: List[str],
        max_pages: int = 3
    ) -> List[str]:
        """
        네이버 뉴스 검색 결과에서 URL 추출

        Args:
            keywords: 검색 키워드 목록
            max_pages: 최대 페이지 수

        Returns:
            뉴스 URL 목록
        """
        urls = []

        for keyword in keywords:
            for page in range(1, max_pages + 1):
                start = (page - 1) * 10 + 1
                search_url = (
                    f"{self.base_url}?where=news&query={quote(keyword)}"
                    f"&sort=1&pd=4&start={start}"  # sort=1: 최신순, pd=4: 1주일
                )

                html = await self.fetch_page(search_url)
                if not html:
                    continue

                soup = self.parse_html(html)

                # 뉴스 링크 추출
                news_items = soup.select("a.news_tit")
                for item in news_items:
                    href = item.get("href", "")
                    if href and "news.naver.com" in href:
                        urls.append(href)

                logger.debug(f"Found {len(news_items)} items for '{keyword}' page {page}")

        return urls

    async def parse_article(self, url: str) -> Optional[CrawledNews]:
        """
        네이버 뉴스 기사 파싱

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
            title_elem = soup.select_one("h2#title_area span") or soup.select_one("h2.media_end_head_headline")
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title:
                logger.warning(f"No title found for {url}")
                return None

            # 본문 추출
            content_elem = soup.select_one("article#dic_area") or soup.select_one("div#newsct_article")
            content = content_elem.get_text(strip=True) if content_elem else ""

            # 투자 관련 뉴스인지 확인
            if not self.is_investment_news(title, content):
                logger.debug(f"Skipping non-investment news: {title}")
                return None

            # 날짜 추출
            date_elem = soup.select_one("span.media_end_head_info_datestamp_time")
            published_at = None
            if date_elem:
                date_str = date_elem.get("data-date-time", "") or date_elem.get_text(strip=True)
                published_at = self._parse_date(date_str)

            # 작성자 추출
            author_elem = soup.select_one("span.media_end_head_journalist_name") or soup.select_one("em.media_end_head_journalist_name")
            author = author_elem.get_text(strip=True) if author_elem else None

            return CrawledNews(
                source="naver",
                source_url=url,
                title=title,
                content=content[:10000] if content else None,  # 최대 10000자
                published_at=published_at,
                author=author,
                raw_html=html[:50000] if html else None  # 원본 HTML 저장 (선택)
            )

        except Exception as e:
            logger.error(f"Error parsing Naver article {url}: {e}")
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

        # 다양한 날짜 형식 처리
        patterns = [
            (r"(\d{4})\.(\d{2})\.(\d{2})\.\s*오전\s*(\d{1,2}):(\d{2})", "am"),
            (r"(\d{4})\.(\d{2})\.(\d{2})\.\s*오후\s*(\d{1,2}):(\d{2})", "pm"),
            (r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", "24h"),
            (r"(\d{4})\.(\d{2})\.(\d{2})", "date_only"),
        ]

        for pattern, time_type in patterns:
            match = re.search(pattern, date_str)
            if match:
                groups = match.groups()
                year, month, day = int(groups[0]), int(groups[1]), int(groups[2])

                if time_type == "date_only":
                    return datetime(year, month, day)

                hour, minute = int(groups[3]), int(groups[4])

                if time_type == "pm" and hour != 12:
                    hour += 12
                elif time_type == "am" and hour == 12:
                    hour = 0

                return datetime(year, month, day, hour, minute)

        return None
