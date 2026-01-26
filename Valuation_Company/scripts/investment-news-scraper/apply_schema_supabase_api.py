#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase REST API를 사용하여 스키마 적용
(PostgreSQL 직접 연결 대신)
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)


def apply_schema_via_api():
    """Supabase API로 스키마 적용"""
    print("="*60)
    print("Supabase Schema Setup (via API)")
    print("="*60)

    # SQL 파일 읽기
    print("\n[1/4] Reading schema file...")
    with open('DATABASE_SCHEMA.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    print("[SUCCESS] Schema file loaded!")

    # Supabase RPC로 실행
    print("\n[2/4] Executing SQL via Supabase API...")

    try:
        # SQL을 세미콜론으로 분리
        statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]

        print(f"[INFO] Total {len(statements)} SQL statements")

        # Supabase의 경우 RPC를 사용하거나, SQL Editor에서 직접 실행해야 함
        print("\n[INFO] Supabase API로는 CREATE TABLE을 직접 실행할 수 없습니다.")
        print("[INFO] SQL Editor에서 실행하거나, Migration 파일을 사용해야 합니다.")

        print("\n" + "="*60)
        print("Please use one of these methods:")
        print("="*60)
        print("\n1. Supabase SQL Editor (Recommended):")
        print("   https://supabase.com/dashboard/project/arxrfetgaitkgiiqabap/editor")
        print("   - Copy DATABASE_SCHEMA.sql content")
        print("   - Paste and Run")

        print("\n2. Supabase CLI:")
        print("   supabase db push")

        print("\n3. PostgreSQL Client:")
        print("   Use apply_schema.py with correct connection info")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")


if __name__ == '__main__':
    apply_schema_via_api()
