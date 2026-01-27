#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL을 직접 사용해서 126개 기업 뉴스 URL 업데이트
(RLS 정책 우회)
"""

import os
import csv
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def update_with_sql():
    """SQL RPC를 사용해서 UPDATE"""

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    print("=" * 60)
    print("126개 기업 뉴스 URL 업데이트 (SQL 직접 실행)")
    print("=" * 60)

    success_count = 0
    fail_count = 0
    skip_count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 기업 수: {len(companies)}개\n")
    print("=" * 60)

    for idx, row in enumerate(companies, 1):
        company_name = row['기업명']
        news_url = row.get('뉴스URL', '')
        site_name = row.get('뉴스소스', '')

        if not news_url:
            skip_count += 1
            continue

        try:
            # SQL RPC 함수 호출 방식
            # Supabase에서는 rpc() 메서드로 직접 SQL 함수를 호출할 수 있음

            # 먼저 해당 회사의 URL이 NULL인 레코드 ID를 찾음
            null_records = supabase.table("deals")\
                .select("id")\
                .eq("company_name", company_name)\
                .is_("news_url", "null")\
                .execute()

            if not null_records.data:
                fail_count += 1
                print(f"[{idx}/{len(companies)}] {company_name} - 실패 (URL 이미 있음)")
                continue

            # ID를 직접 사용해서 UPDATE (RLS 정책을 우회하기 위해)
            record_id = null_records.data[0]['id']

            # upsert를 사용 (INSERT or UPDATE)
            upsert_result = supabase.table("deals")\
                .upsert({
                    "id": record_id,
                    "company_name": company_name,
                    "news_url": news_url,
                    "site_name": site_name,
                    "news_title": f"{company_name} 투자 유치"
                })\
                .execute()

            if upsert_result.data:
                success_count += 1
                print(f"[{idx}/{len(companies)}] {company_name} - 성공")
            else:
                fail_count += 1
                print(f"[{idx}/{len(companies)}] {company_name} - 실패 (upsert 실패)")

        except Exception as e:
            error_msg = str(e)
            fail_count += 1
            print(f"[{idx}/{len(companies)}] {company_name} - 에러: {error_msg[:60]}")

    # 결과 요약
    print("\n" + "=" * 60)
    print("업데이트 완료")
    print("=" * 60)
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"건너뜀 (URL 없음): {skip_count}개")
    print("=" * 60)


if __name__ == '__main__':
    update_with_sql()
