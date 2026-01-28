#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블에 number 칼럼 추가 (직접 연결)
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
print("Deal 테이블에 number 칼럼 추가")
print("=" * 80)

try:
    import psycopg2
except ImportError:
    print("\n설치 중: pip install psycopg2-binary")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

# Supabase 정보
supabase_url = os.getenv("SUPABASE_URL")
project_id = supabase_url.split('//')[1].split('.')[0]

print(f"\n🔍 프로젝트 ID: {project_id}")
print("\n⚠️  PostgreSQL 비밀번호 필요")
print("Supabase Dashboard → Settings → Database → Database Password")

# 비밀번호 입력 받기
db_password = input("\n비밀번호 입력: ").strip()

if not db_password:
    print("❌ 비밀번호가 필요합니다.")
    sys.exit(1)

# 여러 연결 방식 시도
connection_attempts = [
    {
        'name': '직접 연결 (5432)',
        'conn_string': f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"
    },
    {
        'name': 'Pooler 연결 (6543)',
        'conn_string': f"postgresql://postgres.{project_id}:{db_password}@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"
    },
    {
        'name': 'IPv4 Pooler (6543)',
        'conn_string': f"postgresql://postgres.{project_id}:{db_password}@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
    }
]

conn = None

for attempt in connection_attempts:
    print(f"\n🔄 시도: {attempt['name']}")
    try:
        conn = psycopg2.connect(attempt['conn_string'], connect_timeout=10)
        print(f"  ✅ 연결 성공!")
        break
    except Exception as e:
        print(f"  ❌ 실패: {str(e)[:100]}")

if not conn:
    print("\n❌ 모든 연결 시도 실패")
    print("\n💡 대안: Supabase 대시보드에서 직접 실행")
    print("   SQL Editor → 아래 SQL 복사 & 실행:")
    print("""
ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;

WITH numbered_deals AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
    FROM deals
)
UPDATE deals SET number = numbered_deals.row_num
FROM numbered_deals WHERE deals.id = numbered_deals.id;
    """)
    sys.exit(1)

# 연결 성공 - SQL 실행
cursor = conn.cursor()

print("\n1️⃣ number 칼럼 추가...")
try:
    cursor.execute("ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;")
    conn.commit()
    print("  ✅ 완료")
except Exception as e:
    print(f"  ⚠️  {e}")
    conn.rollback()

print("\n2️⃣ 번호 할당...")
try:
    cursor.execute("""
        WITH numbered_deals AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
            FROM deals
        )
        UPDATE deals SET number = numbered_deals.row_num
        FROM numbered_deals WHERE deals.id = numbered_deals.id;
    """)
    conn.commit()
    print("  ✅ 완료")
except Exception as e:
    print(f"  ❌ {e}")
    conn.rollback()

print("\n3️⃣ 확인 (처음 10개)")
cursor.execute("SELECT number, company_name FROM deals ORDER BY number LIMIT 10;")
for row in cursor.fetchall():
    print(f"  {row[0]:3d}. {row[1]}")

cursor.execute("SELECT COUNT(*) FROM deals;")
count = cursor.fetchone()[0]

print("\n" + "=" * 80)
print("✅ 완료!")
print("=" * 80)
print(f"\nDeal 테이블: {count}개")
print(f"번호: 1 ~ {count}")

cursor.close()
conn.close()
