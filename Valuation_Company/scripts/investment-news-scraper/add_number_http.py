#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP 직접 요청으로 number 칼럼 추가
"""

import os
import sys
import requests
from dotenv import load_dotenv

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

print("=" * 80)
print("Deal 테이블에 number 칼럼 추가 (HTTP)")
print("=" * 80)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

headers = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json'
}

# Supabase Management API 시도
print("\n🔍 Supabase Management API 시도...")

project_id = SUPABASE_URL.split('//')[1].split('.')[0]

# SQL 실행 엔드포인트 (Management API)
management_url = f"https://api.supabase.com/v1/projects/{project_id}/database/query"

sql = """
ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;

WITH numbered_deals AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
    FROM deals
)
UPDATE deals SET number = numbered_deals.row_num
FROM numbered_deals WHERE deals.id = numbered_deals.id;
"""

try:
    response = requests.post(
        management_url,
        headers={
            'Authorization': f'Bearer {SERVICE_KEY}',
            'Content-Type': 'application/json'
        },
        json={'query': sql},
        timeout=30
    )

    print(f"  응답 코드: {response.status_code}")

    if response.status_code in [200, 201]:
        print("  ✅ 성공!")
        print(response.json())
    else:
        print(f"  ❌ 실패: {response.text}")

except Exception as e:
    print(f"  ❌ 오류: {e}")

# 대안: pgAdmin URL 통해 실행 (EdgeDB)
print("\n🔍 PostgREST Query 시도...")

# PostgREST에서는 DDL을 직접 실행할 수 없으므로...
# Python client로 우회

from supabase import create_client

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

print("\n💡 Python client로 번호 할당 시도")
print("  (number 칼럼이 이미 있다고 가정)")

try:
    # 모든 Deal 조회
    result = supabase.table("deals").select("id").order("created_at").limit(1).execute()

    if result.data:
        test_id = result.data[0]['id']

        # 테스트: number 칼럼 업데이트
        supabase.table("deals").update({'number': 1}).eq("id", test_id).execute()

        print("  ✅ number 칼럼이 존재합니다!")

        # 전체 번호 할당
        print("\n🔢 번호 할당 중...")

        all_deals = supabase.table("deals").select("id").order("created_at").execute()

        for idx, deal in enumerate(all_deals.data, 1):
            supabase.table("deals").update({'number': idx}).eq("id", deal['id']).execute()

            if idx % 20 == 0:
                print(f"  진행: {idx}/{len(all_deals.data)}")

        print(f"  ✅ {len(all_deals.data)}개 번호 할당 완료")

        # 확인
        result = supabase.table("deals").select("number, company_name").order("number").limit(10).execute()
        print("\n📋 확인 (처음 10개)")
        for deal in result.data:
            print(f"  {deal['number']:3d}. {deal['company_name']}")

except Exception as e:
    print(f"  ❌ number 칼럼이 없습니다: {e}")
    print("\n" + "=" * 80)
    print("💡 해결 방법:")
    print("=" * 80)
    print("\n1. Supabase Dashboard 접속")
    print("   → https://supabase.com/dashboard/project/" + project_id)
    print("\n2. SQL Editor 클릭")
    print("\n3. 다음 SQL 실행:")
    print("""
ALTER TABLE deals ADD COLUMN number INTEGER;

WITH numbered_deals AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
    FROM deals
)
UPDATE deals SET number = numbered_deals.row_num
FROM numbered_deals WHERE deals.id = numbered_deals.id;
    """)
    print("\n4. 실행 후 제게 '완료'라고 알려주세요!")
