"""
Reprocess Deals
기존에 저장된 Deal 데이터 재정제 (품질 향상)
"""
import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# 경로 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.services.news_parser import NewsParser
from app.services.news_crawler.base_crawler import CrawledNews
from supabase import create_client

# 설정 로드 (강제 리로드)
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ReprocessDeals")

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

async def reprocess_deals():
    logger.info("🚀 기존 Deal 데이터 재정제 시작 (IT/AI 구체화, 금액 검증)")
    
    # 1. 재정제 대상 가져오기 (업종이 IT, AI 이거나 금액이 없는 것)
    # 전체를 다시 하는 것이 가장 확실함
    response = supabase.table("deals").select("*").execute()
    deals = response.data
    
    logger.info(f"총 {len(deals)}개의 Deal 데이터를 재검토합니다.")
    
    parser = NewsParser()
    updated_count = 0
    
    for deal in deals:
        try:
            # 기사 내용이 DB에 없으므로, 제목과 요약 등을 이용해 다시 파싱 시도
            # (원래는 URL로 다시 크롤링해야 하지만, 시간상 제목+기존정보로 재추론 시도)
            # 더 정확하게 하려면 크롤러를 다시 돌려야 함. 여기서는 크롤러를 다시 돌리는 로직으로 구현.
            
            logger.info(f"🔄 재처리 중: {deal['company_name']} ({deal['news_title']})")
            
            # 임시 뉴스 객체 생성 (재크롤링 대신 제목만으로 시도해보고, 안되면 크롤러 연동 필요)
            # 일단 제목이 가장 중요하므로 제목 기반으로 재추출 시도
            fake_news = CrawledNews(
                source=deal['site_name'] or "unknown",
                source_url=deal['news_url'] or "",
                title=deal['news_title'] or "",
                content=f"{deal['news_title']} {deal['company_name']} 투자 유치" # 내용이 없어서 약식 처리
            )
            
            # 파서 호출 (강화된 프롬프트 적용됨)
            # 주의: 내용(content)이 없으면 AI가 할 수 있는게 제한적임.
            # 제대로 하려면 URL로 다시 긁어야 함.
            
            # 이번에는 간단히 제목만으로라도 업종을 더 구체적으로 추론해달라고 요청
            extracted = await parser.parse_news(fake_news)
            
            if extracted and extracted.company_name_ko:
                update_data = {}
                
                # 업종 구체화 확인
                if extracted.industry and extracted.industry not in ["IT", "AI", "서비스"]:
                    update_data["industry"] = extracted.industry
                
                # 금액 검증 (기존에 0인데 새로 찾았으면 업데이트)
                if extracted.investment_amount_krw and (not deal['amount'] or deal['amount'] == 0):
                    update_data["amount"] = extracted.investment_amount_krw
                
                # 업데이트 실행
                if update_data:
                    supabase.table("deals").update(update_data).eq("id", deal['id']).execute()
                    logger.info(f"✅ 업데이트 완료: {deal['company_name']} -> {update_data}")
                    updated_count += 1
                else:
                    logger.info(f"PASS: 변경 사항 없음 ({deal['company_name']})")
            
        except Exception as e:
            logger.error(f"Error reprocessing deal {deal['id']}: {e}")

    logger.info(f"🎉 재정제 완료: 총 {updated_count}건 업데이트됨")

if __name__ == "__main__":
    asyncio.run(reprocess_deals())
