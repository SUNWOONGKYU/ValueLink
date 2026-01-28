#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 스키마 확인
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
print("Deal 테이블 스키마 확인")
print("=" * 80)

# 기존 데이터 조회 (1개만)
result = supabase.table("deals").select("*").limit(1).execute()

if result.data:
    print("\n📊 Deal 테이블 컬럼 목록:")
    for key in result.data[0].keys():
        print(f"  - {key}")

    print(f"\n샘플 데이터:")
    for key, value in result.data[0].items():
        print(f"  {key}: {value}")
else:
    print("\n⚠️ Deal 테이블이 비어있습니다.")
    print("테이블 정의를 확인할 수 없습니다.")
