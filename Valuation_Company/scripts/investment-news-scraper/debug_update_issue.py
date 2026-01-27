#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UPDATE 실패 원인 디버깅
"""

import os
import sys
import json
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


def debug_update():
    """UPDATE 실패 원인 디버깅"""

    print("=" * 60)
    print("UPDATE 실패 원인 디버깅")
    print("=" * 60)

    company_name = "이노션스"
    test_id = 125

    # 1. ID 125 레코드 상세 조회
    print(f"\n1. ID {test_id} 레코드 상세:")
    record = supabase.table("deals")\
        .select("*")\
        .eq("id", test_id)\
        .execute()

    if record.data:
        print(json.dumps(record.data[0], indent=2, ensure_ascii=False))
    else:
        print("  레코드 없음")

    # 2. UPDATE 실행 및 결과 상세 확인
    print(f"\n2. ID {test_id} UPDATE 테스트:")
    test_url = "https://wowtale.net/test"
    test_site = "WOWTALE"
    test_title = f"{company_name} 투자 유치"

    try:
        update_result = supabase.table("deals")\
            .update({
                "news_url": test_url,
                "site_name": test_site,
                "news_title": test_title
            })\
            .eq("id", test_id)\
            .execute()

        print(f"  update_result.data: {update_result.data}")
        print(f"  update_result.count: {update_result.count if hasattr(update_result, 'count') else 'N/A'}")

        if update_result.data:
            print(f"  성공! {len(update_result.data)}개 레코드 업데이트됨")
        else:
            print(f"  실패: data가 비어있음")
            print(f"  전체 응답: {update_result}")

    except Exception as e:
        print(f"  에러 발생: {type(e).__name__}")
        print(f"  에러 메시지: {e}")

    # 3. company_name + NULL 조건으로 UPDATE 테스트
    print(f"\n3. company_name + NULL 조건 UPDATE 테스트:")
    try:
        update_result2 = supabase.table("deals")\
            .update({
                "news_url": test_url,
                "site_name": test_site,
                "news_title": test_title
            })\
            .eq("company_name", company_name)\
            .is_("news_url", "null")\
            .execute()

        print(f"  결과: {len(update_result2.data) if update_result2.data else 0}개 업데이트")
        if update_result2.data:
            print(f"  업데이트된 레코드:")
            for rec in update_result2.data:
                print(f"    ID: {rec['id']}, URL: {rec.get('news_url', 'NULL')}")
        else:
            print(f"  data가 비어있음")
            print(f"  전체 응답: {update_result2}")

    except Exception as e:
        print(f"  에러: {e}")

    # 4. 최종 상태 확인
    print(f"\n4. 최종 '{company_name}' 레코드 상태:")
    final = supabase.table("deals")\
        .select("id, company_name, news_url, site_name")\
        .eq("company_name", company_name)\
        .execute()

    for rec in final.data:
        url_text = rec.get('news_url') or "NULL"
        site_text = rec.get('site_name') or "NULL"
        print(f"  ID: {rec['id']}, URL: {url_text[:60]}, Site: {site_text}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    debug_update()
