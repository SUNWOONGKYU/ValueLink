#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 industry 컬럼을 main_business로 변경
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
print("Deal 테이블 컬럼명 변경: industry → main_business")
print("="*60)

try:
    # Supabase Python 클라이언트는 DDL을 직접 실행할 수 없음
    # RPC 함수나 SQL Editor 사용 필요
    print("\n⚠️  컬럼명 변경은 Supabase SQL Editor에서 실행해주세요:")
    print("\n--- SQL 쿼리 ---")
    print("ALTER TABLE deals")
    print("RENAME COLUMN industry TO main_business;")
    print("\nCOMMENT ON COLUMN deals.main_business IS '기업의 주요 사업 (이전: 업종/industry)';")
    print("--- SQL 쿼리 끝 ---")

    print("\n✅ SQL 파일 위치:")
    print("   scripts/investment-news-scraper/alter_industry_to_main_business.sql")

except Exception as e:
    print(f"\n❌ 에러: {str(e)}")

print("\n" + "="*60)
