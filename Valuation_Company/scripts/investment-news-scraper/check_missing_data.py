#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블에서 비어있는 데이터 확인
"""

import os
import sys
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


def check_missing_data():
    """비어있는 데이터 확인"""

    print("=" * 70)
    print("Deal 테이블 빈 데이터 분석")
    print("=" * 70)

    # 모든 Deal 데이터 가져오기
    result = supabase.table("deals").select("*").execute()
    deals = result.data

    print(f"\n총 레코드 수: {len(deals)}개\n")

    # 필드별 빈 데이터 통계
    fields = [
        'company_name', 'ceo', 'industry', 'founded', 'location',
        'stage', 'investors', 'amount', 'total_funding',
        'news_url', 'news_title', 'news_date', 'site_name'
    ]

    print("=" * 70)
    print("필드별 빈 데이터 통계")
    print("=" * 70)
    print(f"{'필드명':<20} {'채워짐':<10} {'비어있음':<10} {'비율':<10}")
    print("-" * 70)

    missing_stats = {}

    for field in fields:
        filled = sum(1 for deal in deals if deal.get(field))
        empty = len(deals) - filled
        empty_pct = (empty / len(deals) * 100) if len(deals) > 0 else 0

        missing_stats[field] = {
            'filled': filled,
            'empty': empty,
            'empty_pct': empty_pct
        }

        print(f"{field:<20} {filled:<10} {empty:<10} {empty_pct:>6.1f}%")

    # 가장 많이 비어있는 필드
    print("\n" + "=" * 70)
    print("수집 우선순위 (비어있는 데이터 많은 순)")
    print("=" * 70)

    sorted_fields = sorted(missing_stats.items(), key=lambda x: x[1]['empty'], reverse=True)

    for idx, (field, stats) in enumerate(sorted_fields[:10], 1):
        if stats['empty'] > 0:
            print(f"{idx}. {field:<20} - {stats['empty']}개 ({stats['empty_pct']:.1f}%) 비어있음")

    # 샘플 레코드 (비어있는 데이터 많은 것)
    print("\n" + "=" * 70)
    print("샘플 레코드 (처음 5개)")
    print("=" * 70)

    for idx, deal in enumerate(deals[:5], 1):
        print(f"\n{idx}. {deal.get('company_name', '(이름없음)')}")
        print(f"   CEO: {deal.get('ceo') or '❌ 없음'}")
        print(f"   업종: {deal.get('industry') or '❌ 없음'}")
        print(f"   설립일: {deal.get('founded') or '❌ 없음'}")
        print(f"   지역: {deal.get('location') or '❌ 없음'}")
        print(f"   투자금액: {deal.get('amount') or '❌ 없음'}")
        print(f"   누적투자: {deal.get('total_funding') or '❌ 없음'}")
        print(f"   뉴스URL: {'✅ 있음' if deal.get('news_url') else '❌ 없음'}")

    print("\n" + "=" * 70)
    print("수집 계획")
    print("=" * 70)
    print("""
1. CEO, 설립일 → 네이버 검색 API 또는 기업정보 크롤링
2. 투자금액 → 뉴스 기사 본문에서 추출
3. 지역 → 기업정보 크롤링 또는 검색
4. 누적투자액 → 더VC, 크런치베이스 등

우선순위:
- 1순위: 투자금액 (뉴스 기사에서 추출 가능)
- 2순위: CEO, 설립일, 지역 (기업정보 크롤링)
- 3순위: 누적투자액 (외부 API)
""")

    print("=" * 70)


if __name__ == '__main__':
    check_missing_data()
