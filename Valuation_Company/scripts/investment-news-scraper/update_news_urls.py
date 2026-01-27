#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
126개 기업의 뉴스 URL 업데이트
"""

import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def safe_print(text, end='\n'):
    """인코딩 에러 방지"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


def update_news_urls():
    """126개 기업의 뉴스 URL 업데이트"""

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    print("="*60)
    print("126개 기업 뉴스 URL 업데이트")
    print("="*60)
    safe_print(f"\nCSV 파일: {csv_file}\n")

    success_count = 0
    fail_count = 0
    skip_count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    safe_print(f"총 기업 수: {len(companies)}개\n")
    safe_print("="*60 + "\n")

    for idx, row in enumerate(companies, 1):
        company_name = row['기업명']
        news_url = row.get('뉴스URL', '')
        site_name = row.get('뉴스소스', '')

        if not news_url:
            skip_count += 1
            continue

        safe_print(f"[{idx}/{len(companies)}] {company_name}...", end=" ")

        try:
            # UPDATE (기업명으로 찾아서 + 뉴스 URL이 없는 것만)
            result = supabase.table("deals")\
                .update({
                    "news_url": news_url,
                    "site_name": site_name,
                    "news_title": f"{company_name} {row.get('신규', '')} 투자 유치"
                })\
                .eq("company_name", company_name)\
                .is_("news_url", "null")\
                .execute()

            if result.data:
                print("✅")
                success_count += 1
            else:
                print("⚠️ 없음")
                fail_count += 1

        except Exception as e:
            error_msg = str(e)
            safe_print(f"❌ {error_msg[:30]}")
            fail_count += 1

    # 결과 요약
    print("\n" + "="*60)
    print("업데이트 완료")
    print("="*60)
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"건너뜀 (URL 없음): {skip_count}개")
    print("="*60)


if __name__ == '__main__':
    update_news_urls()
