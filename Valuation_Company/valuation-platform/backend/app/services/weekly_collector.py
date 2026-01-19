"""
Weekly Collector Orchestrator (Supabase Version)
주간 투자 뉴스 수집 오케스트레이터

@task Investment Tracker
@description 뉴스 크롤링 → AI 파싱 → Supabase 저장
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.db.supabase_client import supabase_client
from app.services.news_crawler import CrawlerManager, CrawledNews

logger = logging.getLogger(__name__)


class WeeklyCollector:
    """
    주간 수집 오케스트레이터 (Supabase 버전)
    """

    def __init__(self):
        self.crawler_manager = CrawlerManager()
        self.collection_id: Optional[int] = None
        self.stats = {
            "news_crawled": 0,
            "news_saved": 0,
            "companies_found": 0,
            "new_companies": 0,
            "errors": []
        }

    async def run(
        self,
        sources: Optional[List[str]] = None,
        max_pages: int = 3
    ) -> Dict[str, Any]:
        """
        전체 수집 프로세스 실행
        """
        logger.info("Starting weekly collection process")

        try:
            # 1. 수집 작업 레코드 생성
            await self._create_collection_record()

            # 2. 뉴스 크롤링
            crawled_news = await self._crawl_news(sources, max_pages)
            self.stats["news_crawled"] = len(crawled_news)

            if not crawled_news:
                logger.warning("No news articles crawled")
                await self._complete_collection(success=True)
                return self.stats

            # 3. DB에 저장 (기업, 뉴스)
            await self._save_to_database(crawled_news)

            # 4. 수집 완료
            await self._complete_collection(success=True)
            logger.info(f"Weekly collection completed: {self.stats}")

        except Exception as e:
            logger.error(f"Weekly collection failed: {e}")
            self.stats["errors"].append(str(e))
            await self._complete_collection(success=False)
            raise

        return self.stats

    async def _create_collection_record(self) -> None:
        """수집 작업 레코드 생성"""
        now = datetime.utcnow()
        iso_calendar = now.isocalendar()

        result = await supabase_client.insert("weekly_collections", {
            "collection_date": now.isoformat(),
            "week_number": iso_calendar.week,
            "year": iso_calendar.year,
            "status": "in_progress",
            "started_at": now.isoformat()
        })

        if result and isinstance(result, dict) and "id" in result:
            self.collection_id = result["id"]
            logger.info(f"Created collection record: {self.collection_id}")
        else:
            logger.error(f"Failed to create collection record. Result: {result}")

    async def _complete_collection(self, success: bool) -> None:
        """수집 작업 완료 처리"""
        if self.collection_id:
            await supabase_client.update("weekly_collections", self.collection_id, {
                "status": "completed" if success else "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "total_news_collected": self.stats["news_crawled"],
                "new_companies_found": self.stats["new_companies"],
                "error_log": str(self.stats["errors"]) if self.stats["errors"] else None
            })

    async def _crawl_news(
        self,
        sources: Optional[List[str]],
        max_pages: int
    ) -> List[CrawledNews]:
        """뉴스 크롤링 단계"""
        logger.info(f"Starting news crawl from sources: {sources or 'all'}")

        news_list = await self.crawler_manager.crawl_all(
            sources=sources,
            max_pages=max_pages
        )

        # 이미 저장된 URL 필터링
        existing = await supabase_client.select("investment_news", columns="source_url")
        existing_urls = set(item.get("source_url") for item in existing) if existing else set()

        new_news = [
            news for news in news_list
            if news.source_url not in existing_urls
        ]

        logger.info(f"Crawled {len(news_list)} articles, {len(new_news)} are new")
        return new_news

    async def _save_to_database(
        self,
        news_list: List[CrawledNews]
    ) -> None:
        """DB에 저장"""
        logger.info(f"Saving {len(news_list)} news items to database")

        for news in news_list:
            try:
                # 기업명 추출 (제목에서 간단히 추출)
                company_name = self._extract_company_name(news.title)

                if company_name:
                    # 기업 조회 또는 생성
                    company_id = await self._get_or_create_company(
                        company_name,
                        news
                    )

                    # 뉴스 저장
                    await supabase_client.insert("investment_news", {
                        "company_id": company_id,
                        "title": news.title,
                        "content": news.content[:5000] if news.content else None,
                        "summary": news.content[:500] if news.content else None,
                        "source": news.source,
                        "source_url": news.source_url,
                        "published_date": news.published_at.isoformat() if news.published_at else None,
                        "collection_id": self.collection_id
                    })

                    self.stats["news_saved"] += 1
                else:
                    # 기업명 없이 뉴스만 저장
                    await supabase_client.insert("investment_news", {
                        "title": news.title,
                        "content": news.content[:5000] if news.content else None,
                        "source": news.source,
                        "source_url": news.source_url,
                        "published_date": news.published_at.isoformat() if news.published_at else None,
                        "collection_id": self.collection_id
                    })
                    self.stats["news_saved"] += 1

            except Exception as e:
                logger.error(f"Error saving news: {e}")
                self.stats["errors"].append(str(e))

    def _extract_company_name(self, title: str) -> Optional[str]:
        """제목에서 기업명 추출 (간단한 규칙 기반)"""
        import re

        # 패턴: '기업명', "기업명", 기업명(이) 투자
        patterns = [
            r"['\"]([^'\"]+)['\"]",  # 따옴표 안의 텍스트
            r"([가-힣A-Za-z0-9]+)\s*,?\s*(?:시리즈|시드|프리)",  # 기업명, 시리즈A
            r"([가-힣A-Za-z0-9]+)(?:이|가)\s+(?:\d+억|\d+조)",  # 기업명이 100억
        ]

        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                name = match.group(1).strip()
                if len(name) >= 2 and len(name) <= 20:
                    return name

        return None

    async def _get_or_create_company(
        self,
        company_name: str,
        news: CrawledNews
    ) -> int:
        """기업 조회 또는 생성"""
        # 기존 기업 조회
        existing = await supabase_client.select(
            "startup_companies",
            filters={"name_ko": company_name}
        )

        if existing:
            return existing[0]["id"]

        # 신규 기업 생성
        # 제목에서 투자 단계 추출
        stage = self._extract_stage(news.title)
        amount = self._extract_amount(news.title)

        result = await supabase_client.insert("startup_companies", {
            "name_ko": company_name,
            "investment_stage": stage,
            "total_funding_krw": amount
        })

        self.stats["new_companies"] += 1
        return result["id"] if isinstance(result, dict) else result[0]["id"]

    def _extract_stage(self, title: str) -> Optional[str]:
        """제목에서 투자 단계 추출"""
        title_lower = title.lower()

        if "시리즈c" in title_lower or "series c" in title_lower:
            return "series_c"
        elif "시리즈b" in title_lower or "series b" in title_lower:
            return "series_b"
        elif "시리즈a" in title_lower or "series a" in title_lower:
            return "series_a"
        elif "프리a" in title_lower or "pre-a" in title_lower or "프리 a" in title_lower:
            return "pre_a"
        elif "시드" in title_lower or "seed" in title_lower:
            return "seed"

        return None

    def _extract_amount(self, title: str) -> Optional[float]:
        """제목에서 투자 금액 추출"""
        import re

        # 패턴: 100억, 50억원, 1조
        match = re.search(r"(\d+(?:\.\d+)?)\s*(조|억)", title)
        if match:
            num = float(match.group(1))
            unit = match.group(2)

            if unit == "조":
                return num * 1_000_000_000_000
            elif unit == "억":
                return num * 100_000_000

        return None


async def run_weekly_collection(
    sources: Optional[List[str]] = None,
    max_pages: int = 3
) -> Dict[str, Any]:
    """
    주간 수집 실행 헬퍼 함수
    """
    collector = WeeklyCollector()
    return await collector.run(sources=sources, max_pages=max_pages)
