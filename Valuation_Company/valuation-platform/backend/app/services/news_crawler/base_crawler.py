"""
Base Crawler Abstract Class
All news crawlers inherit from this class

@task Investment Tracker
@description 뉴스 크롤러 추상 기반 클래스
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class CrawledNews:
    """크롤링된 뉴스 데이터"""
    source: str
    source_url: str
    title: str
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    raw_html: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseCrawler(ABC):
    """
    뉴스 크롤러 추상 기반 클래스
    모든 크롤러는 이 클래스를 상속받아야 함
    """

    # 기본 HTTP 헤더 - 브라우저처럼 보이도록 설정
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(
        self,
        source_name: str,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.source_name = source_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.client = httpx.AsyncClient(
            headers=self.DEFAULT_HEADERS,
            timeout=self.timeout,
            follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.client:
            await self.client.aclose()

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        페이지 HTML 가져오기

        Args:
            url: 요청할 URL

        Returns:
            HTML 문자열 또는 None (실패 시)
        """
        if not self.client:
            raise RuntimeError("Crawler must be used as async context manager")

        for attempt in range(self.max_retries):
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error {e.response.status_code} for {url}, attempt {attempt + 1}")
            except httpx.RequestError as e:
                logger.warning(f"Request error for {url}: {e}, attempt {attempt + 1}")

            if attempt < self.max_retries - 1:
                import asyncio
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """HTML을 BeautifulSoup 객체로 파싱"""
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    async def get_search_results(
        self,
        keywords: List[str],
        max_pages: int = 3
    ) -> List[str]:
        """
        검색 결과에서 뉴스 URL 목록 가져오기

        Args:
            keywords: 검색 키워드 목록
            max_pages: 최대 페이지 수

        Returns:
            뉴스 URL 목록
        """
        pass

    @abstractmethod
    async def parse_article(self, url: str) -> Optional[CrawledNews]:
        """
        개별 뉴스 기사 파싱

        Args:
            url: 뉴스 URL

        Returns:
            CrawledNews 객체 또는 None (실패 시)
        """
        pass

    async def crawl(
        self,
        keywords: List[str] = None,
        max_pages: int = 3
    ) -> List[CrawledNews]:
        """
        뉴스 크롤링 실행

        Args:
            keywords: 검색 키워드 (기본값: 투자 관련 키워드)
            max_pages: 최대 페이지 수

        Returns:
            크롤링된 뉴스 목록
        """
        if keywords is None:
            keywords = [
                "스타트업 투자 유치",
                "시드 투자",
                "시리즈A 투자",
                "프리A 투자"
            ]

        logger.info(f"Starting crawl from {self.source_name} with keywords: {keywords}")

        # 검색 결과에서 URL 수집
        urls = await self.get_search_results(keywords, max_pages)
        logger.info(f"Found {len(urls)} article URLs from {self.source_name}")

        # 중복 제거
        urls = list(set(urls))

        # 각 기사 파싱 (요청 간격 추가)
        import asyncio
        results: List[CrawledNews] = []
        for i, url in enumerate(urls):
            try:
                article = await self.parse_article(url)
                if article:
                    results.append(article)
                # 요청 사이에 딜레이 (서버 부하 방지)
                if i < len(urls) - 1:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error parsing article {url}: {e}")

        logger.info(f"Successfully crawled {len(results)} articles from {self.source_name}")
        return results

    def is_investment_news(self, title: str, content: str = "") -> bool:
        """
        투자 관련 뉴스인지 확인

        Args:
            title: 뉴스 제목
            content: 뉴스 내용

        Returns:
            투자 관련 여부
        """
        investment_keywords = [
            "투자", "유치", "시드", "시리즈", "프리A", "엔젤",
            "펀딩", "밸류에이션", "VC", "벤처캐피탈",
            "인베스트", "투자자", "리드투자"
        ]

        text = f"{title} {content}".lower()
        return any(keyword in text for keyword in investment_keywords)
