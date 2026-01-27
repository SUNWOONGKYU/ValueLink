#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단일 레코드 UPDATE 테스트
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


def test_update():
    """단일 레코드 UPDATE 테스트"""

    company_name = "이노션스"

    print("=" * 60)
    print(f"'{company_name}' 레코드 조회 및 UPDATE 테스트")
    print("=" * 60)

    # 1. 해당 회사의 모든 레코드 조회
    print(f"\n1. '{company_name}' 레코드 조회:")
    records = supabase.table("deals")\
        .select("id, company_name, news_url, site_name")\
        .eq("company_name", company_name)\
        .execute()

    print(f"총 {len(records.data)}개 레코드:")
    for rec in records.data:
        url_text = rec.get('news_url') or "NULL"
        print(f"  ID: {rec['id']}, URL: {url_text}")

    # 2. URL이 NULL인 레코드만 조회 (여러 방법 테스트)
    print(f"\n2. URL이 NULL인 레코드 조회 테스트:")

    # 방법 1: .is_()
    print("  방법 1: .is_('news_url', 'null')")
    try:
        result1 = supabase.table("deals")\
            .select("id, company_name, news_url")\
            .eq("company_name", company_name)\
            .is_("news_url", "null")\
            .execute()
        print(f"    결과: {len(result1.data)}개")
    except Exception as e:
        print(f"    에러: {e}")

    # 방법 2: .eq(None)
    print("  방법 2: .eq('news_url', None)")
    try:
        result2 = supabase.table("deals")\
            .select("id, company_name, news_url")\
            .eq("company_name", company_name)\
            .eq("news_url", None)\
            .execute()
        print(f"    결과: {len(result2.data)}개")
    except Exception as e:
        print(f"    에러: {e}")

    # 방법 3: filter
    print("  방법 3: .filter('news_url', 'is', None)")
    try:
        result3 = supabase.table("deals")\
            .select("id, company_name, news_url")\
            .eq("company_name", company_name)\
            .filter("news_url", "is", None)\
            .execute()
        print(f"    결과: {len(result3.data)}개")
    except Exception as e:
        print(f"    에러: {e}")

    # 3. ID 125 레코드 직접 UPDATE (URL이 없는 것으로 확인됨)
    print(f"\n3. ID 125 레코드 직접 UPDATE 테스트:")
    test_url = "https://wowtale.net/test/url"
    test_site = "WOWTALE"

    try:
        update_result = supabase.table("deals")\
            .update({
                "news_url": test_url,
                "site_name": test_site,
                "news_title": f"{company_name} 투자 유치"
            })\
            .eq("id", 125)\
            .execute()

        if update_result.data:
            print(f"  성공! 업데이트된 레코드 수: {len(update_result.data)}")
            print(f"  업데이트된 레코드: {update_result.data[0]}")
        else:
            print(f"  실패: 업데이트된 레코드 없음")

    except Exception as e:
        print(f"  에러: {e}")

    # 4. 업데이트 후 재조회
    print(f"\n4. 업데이트 후 '{company_name}' 레코드 재조회:")
    final_records = supabase.table("deals")\
        .select("id, company_name, news_url, site_name")\
        .eq("company_name", company_name)\
        .execute()

    for rec in final_records.data:
        url_text = rec.get('news_url') or "NULL"
        site_text = rec.get('site_name') or "NULL"
        print(f"  ID: {rec['id']}, URL: {url_text[:50]}..., Site: {site_text}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    test_update()
