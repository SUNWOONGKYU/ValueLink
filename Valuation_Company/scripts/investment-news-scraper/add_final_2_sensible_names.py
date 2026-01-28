#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
부스터스, 소서릭스코리아를 올바른 이름으로 추가
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 80)
print("부스터스, 소서릭스코리아 추가")
print("=" * 80)

# 2개 기업 Deal 데이터
deals_to_add = [
    {
        'company_name': '부스터스',
        'industry': 'AI기반 마케팅 전문 기업',
        'stage': '시리즈 C',
        'investors': 'SBI인베스트먼트',
        'amount': 200.0,
        'news_title': 'FSN 子 부스터즈, 200억 규모 투자 유치… "3년 내 기업가치 1조 달성 목표"',
        'news_url': 'https://www.etoday.co.kr/news/view/2531426',
        'site_name': '이투데이',
        'news_date': '2026-01-28',
        'created_at': datetime.now().isoformat()
    },
    {
        'company_name': '소서릭스코리아',
        'industry': '자율형 스마트홈 기술개발 스타트업',
        'stage': '시리즈 A',
        'investors': '네이버 D2SF',
        'amount': None,
        'news_title': "네이버 D2SF, AI 스타트업 '소서릭스'에 신규 투자",
        'news_url': 'https://www.moneys.co.kr/article/2025123010574577445',
        'site_name': '머니S',
        'news_date': '2026-01-28',
        'created_at': datetime.now().isoformat()
    }
]

added = 0
updated = 0

for idx, deal in enumerate(deals_to_add, 1):
    company_name = deal['company_name']

    print(f"\n[{idx}/2] {company_name}")
    print(f"  투자자: {deal['investors']}")
    print(f"  투자금액: {deal['amount']}억원" if deal['amount'] else "  투자금액: 비공개")

    # 중복 확인
    existing = supabase.table("deals")\
        .select("id")\
        .eq("company_name", company_name)\
        .execute()

    if not existing.data:
        try:
            supabase.table("deals").insert(deal).execute()
            print(f"  ✅ 신규 추가 완료")
            added += 1
        except Exception as e:
            print(f"  ❌ DB 오류: {e}")
    else:
        try:
            supabase.table("deals")\
                .update(deal)\
                .eq("company_name", company_name)\
                .execute()
            print(f"  ✅ 업데이트 완료")
            updated += 1
        except Exception as e:
            print(f"  ❌ DB 오류: {e}")

print(f"\n{'='*80}")
print(f"✅ 신규 추가: {added}개")
print(f"✅ 업데이트: {updated}개")
print(f"{'='*80}")

# 최종 통계
count_result = supabase.table("deals").select("id", count="exact").execute()
print(f"\nDeals 테이블 총 레코드: {count_result.count}개")
print(f"센서블박스 커버리지: {count_result.count}/124 = {count_result.count/124*100:.1f}%")

print("\n❌ 최종 미발견 기업: 2개")
print("  1. 디앤티테크솔루션")
print("  2. 엘리시전")
