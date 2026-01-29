"""
Crawler Manager
모든 크롤러를 조율하는 매니저

@task Investment Tracker
@description 뉴스 크롤러들을 통합 관리
"""
import asyncio
import logging
from typing import List, Dict, Optional, Type
from datetime import datetime

from app.services.news_crawler.base_crawler import BaseCrawler, CrawledNews
from app.services.news_crawler.naver_crawler import NaverNewsCrawler
from app.services.news_crawler.platum_crawler import PlatumCrawler
from app.services.news_crawler.venturesquare_crawler import VentureSquareCrawler
from app.services.news_crawler.wowtale_crawler import WowtaleCrawler
from app.services.news_crawler.startuptoday_crawler import StartupTodayCrawler
from app.services.news_crawler.outstanding_crawler import OutstandingCrawler

logger = logging.getLogger(__name__)


class CrawlerManager:
    """
    크롤러 매니저
    여러 크롤러를 동시에 실행하고 결과를 통합
    """

    # 사용 가능한 크롤러 목록
    AVAILABLE_CRAWLERS: Dict[str, Type[BaseCrawler]] = {
        "platum": PlatumCrawler,
        "venturesquare": VentureSquareCrawler,
        "naver": NaverNewsCrawler,
        "wowtale": WowtaleCrawler,
        "startuptoday": StartupTodayCrawler,
        "outstanding": OutstandingCrawler,
    }

    def __init__(self):
        self.results: List[CrawledNews] = []
        self.errors: List[Dict] = []
        self.stats: Dict[str, int] = {}

    async def crawl_all(
        self,
        sources: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        max_pages: int = 3
    ) -> List[CrawledNews]:
        """
        모든 소스에서 뉴스 수집

        Args:
            sources: 수집할 소스 목록 (None이면 전체)
            keywords: 검색 키워드 목록
            max_pages: 최대 페이지 수

        Returns:
            수집된 뉴스 목록
        """
        if sources is None:
            sources = list(self.AVAILABLE_CRAWLERS.keys())

        if keywords is None:
            keywords = [
                "스타트업 투자 유치",
                "시드 투자",
                "시리즈A",
                "프리A 투자"
            ]

        self.results = []
        self.errors = []
        self.stats = {source: 0 for source in sources}

        logger.info(f"Starting crawl from sources: {sources}")
        start_time = datetime.utcnow()

        # 각 소스별로 크롤링 실행
        tasks = []
        for source in sources:
            if source in self.AVAILABLE_CRAWLERS:
                tasks.append(self._crawl_source(source, keywords, max_pages))
            else:
                logger.warning(f"Unknown source: {source}")

        # 병렬 실행
        await asyncio.gather(*tasks, return_exceptions=True)

        # 중복 제거 (URL 기준)
        unique_results = self._deduplicate_results()

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Crawl completed in {elapsed:.2f}s. "
            f"Total: {len(unique_results)} unique articles. "
            f"Stats: {self.stats}"
        )

        return unique_results

    async def _crawl_source(
        self,
        source: str,
        keywords: List[str],
        max_pages: int
    ) -> None:
        """
        단일 소스에서 크롤링

        Args:
            source: 소스 이름
            keywords: 검색 키워드
            max_pages: 최대 페이지 수
        """
        crawler_class = self.AVAILABLE_CRAWLERS[source]

        try:
            async with crawler_class() as crawler:
                articles = await crawler.crawl(keywords, max_pages)
                self.results.extend(articles)
                self.stats[source] = len(articles)
                logger.info(f"Crawled {len(articles)} articles from {source}")

        except Exception as e:
            error_info = {
                "source": source,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.errors.append(error_info)
            logger.error(f"Error crawling {source}: {e}")

    def _deduplicate_results(self) -> List[CrawledNews]:
        """
        URL 기준으로 중복 제거

        Returns:
            중복 제거된 뉴스 목록
        """
        seen_urls = set()
        unique = []

        for article in self.results:
            if article.source_url not in seen_urls:
                seen_urls.add(article.source_url)
                unique.append(article)

        logger.debug(f"Deduplicated: {len(self.results)} -> {len(unique)}")
        return unique

    async def crawl_source(
        self,
        source: str,
        keywords: Optional[List[str]] = None,
        max_pages: int = 3
    ) -> List[CrawledNews]:
        """
        단일 소스에서만 수집

        Args:
            source: 소스 이름
            keywords: 검색 키워드
            max_pages: 최대 페이지 수

        Returns:
            수집된 뉴스 목록
        """
        return await self.crawl_all(
            sources=[source],
            keywords=keywords,
            max_pages=max_pages
        )

    def get_stats(self) -> Dict:
        """
        수집 통계 반환

        Returns:
            통계 정보
        """
        return {
            "total_articles": len(self.results),
            "by_source": self.stats,
            "errors": len(self.errors),
            "error_details": self.errors
        }
