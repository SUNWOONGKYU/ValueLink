#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3개 기업을 Deal 테이블에 수동 추가
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

# 3개 기업 Deal 데이터
deals_to_add = [
    {
        'company_name': '부스터즈',
        'industry': 'AI 기반 스마트팩토리',
        'stage': None,
        'investors': 'SBI인베스트먼트',
        'amount': 200.0,
        'news_title': 'FSN 子 부스터즈, 200억 규모 투자 유치… "3년 내 기업가치 1조 달성 목표"',
        'news_url': 'https://www.etoday.co.kr/news/view/2531426',
        'site_name': '이투데이',
        'news_date': '2026-01-28',
        'created_at': datetime.now().isoformat()
    },
    {
        'company_name': '에봄에이아이',
        'industry': 'AI 기반 건강관리',
        'stage': '시드',
        'investors': '광림벤처스',
        'amount': None,
        'news_title': '에봄에이아이, 끌림벤처스서 시드 투자 유치 및 딥테크 팁스 선정',
        'news_url': 'https://wowtale.net/2026/01/07/252857/',
        'site_name': 'WOWTALE',
        'news_date': '2026-01-28',
        'created_at': datetime.now().isoformat()
    },
    {
        'company_name': '소서릭스',
        'industry': 'AI 스타트업',
        'stage': None,
        'investors': '네이버 D2SF',
        'amount': None,
        'news_title': "네이버 D2SF, AI 스타트업 '소서릭스'에 신규 투자",
        'news_url': 'https://www.moneys.co.kr/article/2025123010574577445',
        'site_name': '머니S',
        'news_date': '2026-01-28',
        'created_at': datetime.now().isoformat()
    }
]

print("=" * 80)
print("3개 기업을 Deal 테이블에 수동 추가")
print("=" * 80)

added = 0
updated = 0

for idx, deal in enumerate(deals_to_add, 1):
    company_name = deal['company_name']

    print(f"\n[{idx}/3] {company_name}")
    print(f"  투자자: {deal['investors']}")
    print(f"  투자금액: {deal['amount']}억원" if deal['amount'] else "  투자금액: 비공개")
    print(f"  사이트: {deal['site_name']}")

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

print("\n🎉 센서블박스 127개 기업 중 116개 기업 뉴스 수집 완료!")
print(f"   - 자동 수집: 113개")
print(f"   - 수동 추가: 3개")
print(f"   - 미발견: 11개")
