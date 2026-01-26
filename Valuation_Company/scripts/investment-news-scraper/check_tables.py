#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase 테이블 목록 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

print("="*60)
print("Supabase 테이블 목록 확인")
print("="*60)

# information_schema에서 테이블 목록 조회
try:
    # RPC 호출로 테이블 목록 가져오기
    result = supabase.rpc('get_tables').execute()
    print(f"\n테이블 목록:")
    print(result)
except Exception as e:
    print(f"\n[방법 1 실패] {str(e)}")

# 직접 쿼리로 시도
try:
    # postgrest API로 테이블 메타데이터 확인
    result = supabase.table("pg_tables").select("tablename").eq("schemaname", "public").execute()
    print(f"\n\n[방법 2] pg_tables:")
    print(result)
except Exception as e:
    print(f"\n[방법 2 실패] {str(e)}")

# 일반적인 테이블명들 시도
print("\n\n테이블명 시도:")
test_names = ["Deal", "deal", "deals", "Deals", "투자딜", "investment_deals"]

for name in test_names:
    try:
        result = supabase.table(name).select("*").limit(1).execute()
        print(f"✅ '{name}' - 존재함! (레코드 수: {len(result.data)})")
        if result.data:
            print(f"   컬럼: {list(result.data[0].keys())}")
    except Exception as e:
        error_msg = str(e)
        if "Could not find" in error_msg:
            print(f"❌ '{name}' - 없음")
        else:
            print(f"⚠️ '{name}' - 에러: {error_msg[:50]}")

print("\n" + "="*60)
