#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service Role Key를 사용해서 126개 기업 뉴스 URL 업데이트
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

# Service Role Key로 Supabase 클라이언트 생성
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # Service Role Key 사용
)


def update_news_urls():
    """126개 기업의 뉴스 URL 업데이트 (Service Role Key 사용)"""

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    print("=" * 60)
    print("126개 기업 뉴스 URL 업데이트 (Service Role Key)")
    print("=" * 60)

    success_count = 0
    fail_count = 0
    skip_count = 0
    success_companies = []
    fail_companies = []

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
            # news_url이 NULL인 레코드만 UPDATE
            result = supabase.table("deals")\
                .update({
                    "news_url": news_url,
                    "site_name": site_name,
                    "news_title": f"{company_name} 투자 유치"
                })\
                .eq("company_name", company_name)\
                .is_("news_url", "null")\
                .execute()

            if result.data and len(result.data) > 0:
                success_count += 1
                success_companies.append(company_name)
                print(f"[{idx}/{len(companies)}] {company_name} - 성공 ✅")
            else:
                fail_count += 1
                fail_companies.append((company_name, "레코드 없음 또는 URL 존재"))
                print(f"[{idx}/{len(companies)}] {company_name} - 실패 (URL 이미 있음)")

        except Exception as e:
            error_msg = str(e)
            fail_count += 1
            fail_companies.append((company_name, error_msg[:50]))
            print(f"[{idx}/{len(companies)}] {company_name} - 에러: {error_msg[:60]}")

    # 결과 요약
    print("\n" + "=" * 60)
    print("업데이트 완료")
    print("=" * 60)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"⏭️  건너뜀: {skip_count}개")
    print("=" * 60)

    if success_companies:
        print(f"\n✅ 성공한 기업 (처음 20개):")
        for name in success_companies[:20]:
            print(f"  - {name}")
        if len(success_companies) > 20:
            print(f"  ... 외 {len(success_companies) - 20}개")

    if fail_companies:
        print(f"\n❌ 실패한 기업:")
        for name, reason in fail_companies[:10]:
            print(f"  - {name}: {reason}")
        if len(fail_companies) > 10:
            print(f"  ... 외 {len(fail_companies) - 10}개")

    print("\n" + "=" * 60)

    # 최종 검증
    print("\n최종 검증 중...")
    final_check = supabase.table("deals").select("id").is_("news_url", "null").execute()
    print(f"남은 NULL URL 레코드: {len(final_check.data)}개")
    print("=" * 60)


if __name__ == '__main__':
    update_news_urls()
