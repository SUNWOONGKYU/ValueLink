"""
Weekly Collector Orchestrator (Supabase Version)
주간 투자 뉴스 수집 오케스트레이터

@task Investment Tracker
@description 뉴스 크롤링 → Gemini AI 파싱 → Supabase 저장
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.db.supabase_client import supabase_client
from app.services.news_crawler import CrawlerManager, CrawledNews
from app.services.news_parser import NewsParser

logger = logging.getLogger(__name__)


class WeeklyCollector:
    """
    주간 수집 오케스트레이터 (Supabase 버전)
    """

    def __init__(self, use_ai_parser: bool = True):
        self.crawler_manager = CrawlerManager()
        self.news_parser = NewsParser() if use_ai_parser else None
        self.use_ai_parser = use_ai_parser
        self.collection_id: Optional[int] = None
        self.stats = {
            "news_crawled": 0,
            "news_parsed_by_ai": 0,
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
        """DB에 저장 (Gemini AI 파싱 사용)"""
        logger.info(f"Saving {len(news_list)} news items to database")

        for news in news_list:
            try:
                extracted = None
                company_name = None

                # Gemini AI로 데이터 추출 시도
                if self.use_ai_parser and self.news_parser:
                    try:
                        extracted = await self.news_parser.parse_news(news)
                        if extracted and extracted.company_name_ko:
                            company_name = extracted.company_name_ko
                            self.stats["news_parsed_by_ai"] += 1
                            logger.info(f"AI parsed: {company_name} ({extracted.industry}, {extracted.investment_amount_krw}억원)")
                    except Exception as ai_error:
                        logger.warning(f"AI parsing failed for '{news.title}': {ai_error}")

                # AI 파싱 실패 시 regex fallback
                if not company_name:
                    company_name = self._extract_company_name(news.title)

                if company_name:
                    # 기업 조회 또는 생성 (AI 추출 데이터 활용)
                    company_id = await self._get_or_create_company_with_ai(
                        company_name,
                        news,
                        extracted
                    )

                    # 뉴스 저장 (AI 요약 포함)
                    import json as json_module
                    ai_data = None
                    if extracted:
                        ai_data = json_module.dumps({
                            "confidence": extracted.confidence_score,
                            "industry": extracted.industry,
                            "amount_krw": extracted.investment_amount_krw,
                            "stage": extracted.investment_stage,
                            "lead_investor": extracted.lead_investor,
                            "investors": extracted.investors
                        }, ensure_ascii=False)

                    await supabase_client.insert("investment_news", {
                        "company_id": company_id,
                        "title": news.title,
                        "content": news.content[:5000] if news.content else None,
                        "summary": extracted.summary if extracted else (news.content[:500] if news.content else None),
                        "source": news.source,
                        "source_url": news.source_url,
                        "published_date": news.published_at.isoformat() if news.published_at else None,
                        "collection_id": self.collection_id,
                        "ai_extracted_data": ai_data
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
        """기업 조회 또는 생성 (레거시 - regex 기반)"""
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

    async def _get_or_create_company_with_ai(
        self,
        company_name: str,
        news: CrawledNews,
        extracted: Optional[Any] = None
    ) -> int:
        """기업 조회 또는 생성 (AI 추출 데이터 활용)"""
        from app.services.news_parser import ExtractedInvestmentData

        # 기존 기업 조회
        existing = await supabase_client.select(
            "startup_companies",
            filters={"name_ko": company_name}
        )

        if existing:
            company_id = existing[0]["id"]

            # AI 데이터가 있으면 기존 정보 업데이트
            if extracted and isinstance(extracted, ExtractedInvestmentData):
                update_data = {}

                if extracted.industry and not existing[0].get("industry"):
                    update_data["industry"] = extracted.industry
                if extracted.company_name_en and not existing[0].get("name_en"):
                    update_data["name_en"] = extracted.company_name_en

                if update_data:
                    await supabase_client.update("startup_companies", company_id, update_data)

            return company_id

        # 신규 기업 생성
        company_data = {"name_ko": company_name}

        if extracted and isinstance(extracted, ExtractedInvestmentData):
            # AI 추출 데이터 사용
            if extracted.company_name_en:
                company_data["name_en"] = extracted.company_name_en
            if extracted.industry:
                company_data["industry"] = extracted.industry
            if extracted.sub_industry:
                company_data["sub_industry"] = extracted.sub_industry
            if extracted.investment_stage:
                company_data["investment_stage"] = extracted.investment_stage
            if extracted.investment_amount_krw:
                company_data["total_funding_krw"] = extracted.investment_amount_krw * 100_000_000  # 억원 → 원
            if extracted.valuation_post_krw:
                company_data["latest_valuation_krw"] = extracted.valuation_post_krw * 100_000_000
        else:
            # Fallback: regex 추출
            company_data["investment_stage"] = self._extract_stage(news.title)
            amount = self._extract_amount(news.title)
            if amount:
                company_data["total_funding_krw"] = amount

        result = await supabase_client.insert("startup_companies", company_data)

        self.stats["new_companies"] += 1
        company_id = result["id"] if isinstance(result, dict) else result[0]["id"]

        # 투자 라운드 정보 저장 (AI 데이터가 있는 경우)
        if extracted and isinstance(extracted, ExtractedInvestmentData) and extracted.investment_amount_krw:
            await self._save_investment_round(company_id, extracted, news)

        return company_id

    async def _save_investment_round(
        self,
        company_id: int,
        extracted: Any,
        news: CrawledNews
    ) -> None:
        """투자 라운드 정보 저장"""
        from app.services.news_parser import ExtractedInvestmentData

        if not isinstance(extracted, ExtractedInvestmentData):
            return

        try:
            round_data = {
                "company_id": company_id,
                "round_name": extracted.investment_stage or "unknown",
                "amount_krw": int(extracted.investment_amount_krw * 100_000_000) if extracted.investment_amount_krw else None,
                "announced_date": news.published_at.isoformat() if news.published_at else datetime.utcnow().isoformat(),
                "source_url": news.source_url,
            }

            if extracted.valuation_post_krw:
                round_data["valuation_krw"] = int(extracted.valuation_post_krw * 100_000_000)
            if extracted.lead_investor:
                round_data["lead_investor"] = extracted.lead_investor
            if extracted.investors:
                # co_investors는 배열 형태
                co_investors = [inv.get("name", "") for inv in extracted.investors if inv.get("name")]
                round_data["co_investors"] = co_investors

            await supabase_client.insert("investment_rounds", round_data)
            logger.info(f"Saved investment round for company {company_id}: {extracted.investment_stage} {extracted.investment_amount_krw}억원")

        except Exception as e:
            logger.warning(f"Failed to save investment round: {e}")

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
