#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블에 number 칼럼 추가 (PostgreSQL 직접 연결)
"""

import os
import sys
from dotenv import load_dotenv

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

print("=" * 80)
print("Deal 테이블에 number 칼럼 추가 (PostgreSQL 직접 연결)")
print("=" * 80)

try:
    import psycopg2
except ImportError:
    print("\npsycopg2 설치 중...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "psycopg2-binary"])
    import psycopg2

# Supabase 정보
supabase_url = os.getenv("SUPABASE_URL")
db_password = os.getenv("DB_PASSWORD")

project_id = supabase_url.split('//')[1].split('.')[0]

print(f"\n📡 프로젝트 ID: {project_id}")
print(f"🔑 비밀번호: {'*' * len(db_password)}")

# 직접 연결
conn_string = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"

print("\n🔄 연결 중...")

try:
    conn = psycopg2.connect(conn_string, connect_timeout=15)
    print("  ✅ 연결 성공!")

    cursor = conn.cursor()

    # 1. number 칼럼 추가
    print("\n1️⃣ number 칼럼 추가...")
    try:
        cursor.execute("ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;")
        conn.commit()
        print("  ✅ 완료")
    except Exception as e:
        print(f"  ⚠️  {e}")
        conn.rollback()

    # 2. 번호 할당
    print("\n2️⃣ 번호 할당 (created_at 순서)...")
    try:
        cursor.execute("""
            WITH numbered_deals AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
                FROM deals
            )
            UPDATE deals SET number = numbered_deals.row_num
            FROM numbered_deals WHERE deals.id = numbered_deals.id;
        """)
        affected = cursor.rowcount
        conn.commit()
        print(f"  ✅ {affected}개 레코드 업데이트 완료")
    except Exception as e:
        print(f"  ❌ {e}")
        conn.rollback()

    # 3. 확인
    print("\n3️⃣ 확인 (처음 10개)")
    cursor.execute("SELECT number, company_name FROM deals ORDER BY number LIMIT 10;")

    for row in cursor.fetchall():
        print(f"  {row[0]:3d}. {row[1]}")

    # 4. 통계
    cursor.execute("SELECT COUNT(*), MIN(number), MAX(number) FROM deals;")
    count, min_num, max_num = cursor.fetchone()

    print("\n" + "=" * 80)
    print("✅ 완료!")
    print("=" * 80)
    print(f"\nDeal 테이블: {count}개")
    print(f"번호 범위: {min_num} ~ {max_num}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ 오류: {e}")
    print("\n연결 문자열:")
    print(f"  Host: db.{project_id}.supabase.co")
    print(f"  Port: 5432")
    print(f"  User: postgres")
    print(f"  Database: postgres")
