"""
Daily Investment News Automation
매일 아침 6시 실행되는 투자 뉴스 자동화 시스템

@process 뉴스 수집 -> AI 정제 -> DB 저장 -> 리포트 발송
"""
import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.services.news_crawler.crawler_manager import CrawlerManager
from app.services.news_parser import NewsParser
from app.services.investment_automation.enricher import DataEnricher
from app.services.investment_automation.reporter import DailyReporter
from supabase import create_client
from dotenv import load_dotenv

# 설정 로드
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DailyAutomation")

# Supabase 클라이언트
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

async def run_daily_automation():
    logger.info("=" * 60)
    logger.info("🚀 매일 아침 투자 뉴스 자동화 프로세스 시작")
    logger.info("=" * 60)

    # 1. 뉴스 수집 (전날 뉴스 타겟)
    manager = CrawlerManager()
    keywords = ["투자 유치", "스타트업 투자", "시리즈A", "시드 투자"]
    
    logger.info("1️⃣ 뉴스 수집 단계 시작...")
    yesterday_obj = datetime.now() - timedelta(days=1)
    yesterday = yesterday_obj.strftime("%Y-%m-%d")
    
    news_list = await manager.crawl_all(keywords=keywords, max_pages=3)
    logger.info(f"✅ 총 {len(news_list)}건의 뉴스 기사 수집 완료")

    if not news_list:
        logger.info("새로운 뉴스가 없습니다. 종료합니다.")
        return

    # 2. AI 데이터 정제 및 DB 저장
    parser = NewsParser()
    enricher = DataEnricher()
    logger.info("2️⃣ AI 데이터 정제 및 DB 저장 단계 시작...")
    logger.info(f"Connecting to Supabase: {os.getenv('SUPABASE_URL')}") # URL 확인용 로그
    
    new_deals = [] # 리스트 초기화
    saved_count = 0
    skipped_count = 0
    
    for news in news_list:
        try:
            # 1차 중복 체크 (URL 기준)
            existing_url = supabase.table("deals").select("id").eq("news_url", news.source_url).execute()
            if existing_url.data:
                logger.info(f"⏭️ [SKIP] 이미 등록된 뉴스 URL: {news.source_url}")
                skipped_count += 1
                continue

            # Gemini AI로 데이터 추출
            extracted = await parser.parse_news(news)
            if not extracted or not extracted.company_name_ko:
                continue

            # 2차 중복 체크 (기업명 + 투자금액 + 투자단계 정밀 비교)
            # 같은 기업이 '같은 단계'에서 '비슷한 금액'을 받았다면 중복으로 간주
            # (단계가 다르거나 금액이 다르면 추가/후속 투자로 인정)
            recent_deals = supabase.table("deals").select("id, amount, stage")\
                .eq("company_name", extracted.company_name_ko)\
                .gte("created_at", (datetime.now() - timedelta(days=60)).isoformat())\
                .execute()
            
            is_duplicate = False
            if recent_deals.data:
                for deal in recent_deals.data:
                    db_amount = deal.get('amount') or 0
                    new_amount = extracted.investment_amount_krw or 0
                    db_stage = deal.get('stage') or "unknown"
                    new_stage = extracted.investment_stage or "unknown"

                    # 1. 단계가 같고
                    # 2. 금액이 없거나(비공개), 금액이 거의 일치하면(오차 10% 이내) -> 중복
                    if db_stage == new_stage:
                        if db_amount == 0 or new_amount == 0: # 금액 불명확 시 단계만으로 중복 의심
                             is_duplicate = True
                             break
                        
                        # 금액 비교 (10% 오차 허용)
                        if abs(db_amount - new_amount) < (db_amount * 0.1):
                            is_duplicate = True
                            break
            
            if is_duplicate:
                logger.info(f"⏭️ [SKIP] 이미 등록된 투자 건 (동일 단계/금액): {extracted.company_name_ko}")
                skipped_count += 1
                continue

            # 3️⃣ 데이터 보강 (Enrichment)
            if not extracted.industry or extracted.industry in ["IT", "AI"]:
                logger.info(f"🔍 {extracted.company_name_ko} 정보 보강 중...")
                enriched_data = await enricher.enrich_company_info(extracted.company_name_ko)
                # 보강 로직은 추후 고도화

            # 데이터 구성
            deal_data = {
                "company_name": extracted.company_name_ko,
                "industry": extracted.industry,
                "stage": extracted.investment_stage,
                "amount": extracted.investment_amount_krw,
                "investors": ", ".join([inv.get("name", "") for inv in extracted.investors]) if extracted.investors else extracted.lead_investor,
                "news_title": news.title,
                "news_url": news.source_url,
                "news_date": yesterday,
                "site_name": news.source
            }

            # DB 저장
            supabase.table("deals").insert(deal_data).execute()
            new_deals.append(deal_data)
            logger.info(f"✅ [저장 완료] {extracted.company_name_ko} ({extracted.investment_amount_krw}억원)")

        except Exception as e:
            logger.error(f"❌ 처리 중 오류 발생 ({news.source_url}): {e}")

    logger.info(f"📊 최종 결과: {len(new_deals)}건의 새로운 Deal 등록 완료")

    # 4. 데일리 리포트 발송
    if new_deals:
        logger.info("4️⃣ 데일리 리포트 발송 단계 시작...")
        reporter = DailyReporter()
        target_emails = [os.getenv("REPORT_RECEIVER_EMAIL", os.getenv("SMTP_USER"))]
        reporter.send_report(new_deals, target_emails)

    logger.info("=" * 60)
    logger.info("🎉 매일 아침 자동화 프로세스 완료")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_daily_automation())
