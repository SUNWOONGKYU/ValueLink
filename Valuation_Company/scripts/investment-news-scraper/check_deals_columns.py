#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deals 테이블 컬럼명 확인
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
print("deals 테이블 컬럼명 확인")
print("="*60)

try:
    # deals 테이블에서 1개 레코드 가져오기
    result = supabase.table("deals").select("*").limit(1).execute()

    if result.data:
        print(f"\ndeals 테이블 컬럼 목록:")
        for col in result.data[0].keys():
            print(f"  - {col}")

        print(f"\n첫 번째 레코드:")
        for key, value in result.data[0].items():
            print(f"  {key}: {value}")
    else:
        print("\n[INFO] deals 테이블이 비어 있습니다.")
        print("빈 INSERT로 컬럼 구조 확인...")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")

print("\n" + "="*60)
