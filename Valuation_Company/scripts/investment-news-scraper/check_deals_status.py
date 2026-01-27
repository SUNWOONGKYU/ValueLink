#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 상태 확인
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

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def check_deals():
    """Deal 테이블 상태 확인"""

    print("=" * 60)
    print("Deal 테이블 상태 확인")
    print("=" * 60)

    # 전체 레코드 수
    all_deals = supabase.table("deals").select("id").execute()
    print(f"\n전체 레코드 수: {len(all_deals.data)}개")

    # news_url이 있는 레코드 수
    with_url = supabase.table("deals").select("id").not_.is_("news_url", "null").execute()
    print(f"news_url 있음: {len(with_url.data)}개")

    # news_url이 NULL인 레코드 수
    without_url = supabase.table("deals").select("id").is_("news_url", "null").execute()
    print(f"news_url 없음: {len(without_url.data)}개")

    # news_url이 NULL인 레코드 샘플 (처음 10개)
    print("\n" + "=" * 60)
    print("news_url이 NULL인 레코드 샘플 (처음 10개)")
    print("=" * 60)

    sample = supabase.table("deals")\
        .select("id, company_name, news_url")\
        .is_("news_url", "null")\
        .limit(10)\
        .execute()

    for record in sample.data:
        print(f"ID: {record['id']}, 기업명: {record['company_name']}, URL: {record['news_url']}")

    # 중복 회사 확인
    print("\n" + "=" * 60)
    print("중복 회사 확인")
    print("=" * 60)

    all_companies = supabase.table("deals").select("company_name").execute()
    company_counts = {}
    for record in all_companies.data:
        name = record['company_name']
        company_counts[name] = company_counts.get(name, 0) + 1

    duplicates = {name: count for name, count in company_counts.items() if count > 1}

    if duplicates:
        print(f"중복 회사 수: {len(duplicates)}개")
        print("\n중복 회사 목록 (처음 10개):")
        for name, count in list(duplicates.items())[:10]:
            print(f"  - {name}: {count}개")

            # 해당 회사의 레코드 상세
            records = supabase.table("deals")\
                .select("id, company_name, news_url")\
                .eq("company_name", name)\
                .execute()

            for rec in records.data:
                url_status = "URL 있음" if rec.get('news_url') else "URL 없음"
                print(f"    ID {rec['id']}: {url_status}")
    else:
        print("중복 회사 없음")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    check_deals()
