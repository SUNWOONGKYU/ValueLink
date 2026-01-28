#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase SQL 실행
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

print("=" * 80)
print("Deal 테이블에 number 칼럼 추가 (SQL 실행)")
print("=" * 80)

# SQL 스크립트
sql_script = """
-- Deal 테이블에 number 칼럼 추가
ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;
"""

print("\n1️⃣ number 칼럼 추가...")

try:
    # SQL 실행 (RPC 사용)
    result = supabase.rpc('exec_sql', {'query': sql_script}).execute()
    print("  ✅ number 칼럼 추가 완료")
except Exception as e:
    print(f"  ⚠️  에러 (이미 있을 수 있음): {e}")

# 2. 번호 할당 (Python으로)
print("\n2️⃣ 번호 할당 중...")

# 모든 Deal 조회 (created_at 순서로)
result = supabase.table("deals").select("id").order("created_at").execute()
deals = result.data

print(f"  📊 {len(deals)}개 레코드 발견")

# 번호 할당
for idx, deal in enumerate(deals, 1):
    try:
        supabase.table("deals")\
            .update({'number': idx})\
            .eq("id", deal['id'])\
            .execute()

        if idx % 20 == 0:
            print(f"  진행: {idx}/{len(deals)}")
    except Exception as e:
        print(f"  ❌ ID {deal['id']} 실패: {e}")

print(f"  ✅ {len(deals)}개 번호 할당 완료")

# 3. 확인
print("\n3️⃣ 확인 (처음 10개)")

result = supabase.table("deals")\
    .select("number, company_name")\
    .order("number")\
    .limit(10)\
    .execute()

for deal in result.data:
    print(f"  {deal['number']:3d}. {deal['company_name']}")

print("\n" + "=" * 80)
print("✅ 완료!")
print("=" * 80)

# 최종 통계
count_result = supabase.table("deals").select("id", count="exact").execute()
print(f"\nDeal 테이블: {count_result.count}개")
print(f"번호: 1 ~ {count_result.count}")
