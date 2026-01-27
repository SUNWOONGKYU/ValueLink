#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensible Box 데이터를 Deal 테이블에 재입력
"""

import os
import sys
import csv
import re
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


def parse_amount(amount_str):
    """투자금액 파싱 (억원 → 숫자)"""
    if not amount_str or amount_str == '비공개':
        return None

    # "142억원" → 142
    match = re.search(r'(\d+)', amount_str)
    if match:
        return int(match.group(1))
    return None


def main():
    print("=" * 70)
    print("Sensible Box 데이터 재입력 (날짜 부여)")
    print("=" * 70)

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        deals = list(reader)

    print(f"\n총 {len(deals)}개 레코드 입력 예정\n")

    from datetime import datetime, timedelta
    import random

    # 기준 날짜: 2026-01-27 (오늘)
    base_date = datetime(2026, 1, 27)

    success_count = 0
    fail_count = 0

    for idx, row in enumerate(deals, 1):
        company_name = row['기업명']
        industry = row['주요사업']
        investors = row['투자자']
        stage = row['단계']
        amount = parse_amount(row['신규'])
        news_url = row['뉴스URL']
        site_name = row['뉴스소스']

        # CSV 순서대로 날짜 부여 (1번째가 최신)
        # 1~10: 2026-01-27 (오늘)
        # 11~30: 2026-01-26
        # 31~60: 2026-01-25
        # ...
        days_ago = (idx - 1) // 10  # 10개당 1일씩 이전
        news_date = base_date - timedelta(days=days_ago)

        # 시간도 다양하게 (오전 9시 ~ 오후 6시)
        hour = random.randint(9, 18)
        minute = random.randint(0, 59)
        news_datetime = news_date.replace(hour=hour, minute=minute)

        try:
            supabase.table("deals").insert({
                "company_name": company_name,
                "industry": industry,
                "investors": investors,
                "stage": stage,
                "amount": amount,
                "news_url": news_url,
                "site_name": site_name,
                "news_date": news_datetime.strftime("%Y-%m-%d"),
                "news_title": f"{company_name} {stage} 투자 유치"  # 제목 생성
            }).execute()

            success_count += 1
            if idx % 20 == 0:
                print(f"  진행: {idx}/{len(deals)}")

        except Exception as e:
            print(f"  ❌ {company_name} 실패: {str(e)[:50]}")
            fail_count += 1

    print("\n" + "=" * 70)
    print("재입력 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    main()
