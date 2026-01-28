#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pooler로 연결 시도
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

try:
    import psycopg2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "psycopg2-binary"])
    import psycopg2

print("=" * 80)
print("Deal 테이블에 number 칼럼 추가")
print("=" * 80)

supabase_url = os.getenv("SUPABASE_URL")
db_password = os.getenv("DB_PASSWORD")
project_id = supabase_url.split('//')[1].split('.')[0]

# 여러 연결 방식 시도
connections = [
    {
        'name': 'Pooler (Transaction Mode)',
        'conn': f"postgresql://postgres.{project_id}:[{db_password}]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"
    },
    {
        'name': 'Pooler (Session Mode)',
        'conn': f"postgresql://postgres.{project_id}:[{db_password}]@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres"
    },
    {
        'name': 'Pooler (postgres)',
        'conn': f"postgresql://postgres:[{db_password}]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
    },
]

print(f"\n📡 프로젝트: {project_id}")

conn = None

for idx, config in enumerate(connections, 1):
    print(f"\n[{idx}/{len(connections)}] {config['name']}")
    print(f"  연결 중...", end=' ')

    try:
        conn = psycopg2.connect(config['conn'], connect_timeout=10)
        print("✅ 성공!")
        break
    except Exception as e:
        print(f"❌ {str(e)[:80]}")

if not conn:
    print("\n" + "=" * 80)
    print("❌ 모든 연결 시도 실패")
    print("=" * 80)
    print("\n💡 Supabase Dashboard에서 직접 SQL 실행이 필요합니다:")
    print("   1. https://supabase.com/dashboard 접속")
    print("   2. SQL Editor 클릭")
    print("   3. 다음 SQL 실행:")
    print("""
ALTER TABLE deals ADD COLUMN number INTEGER;

WITH numbered_deals AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
    FROM deals
)
UPDATE deals SET number = numbered_deals.row_num
FROM numbered_deals WHERE deals.id = numbered_deals.id;
    """)
    sys.exit(1)

# 연결 성공!
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
    print(f"  ✅ {cursor.rowcount}개 업데이트")
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
print(f"\nDeal 테이블: {count}개 (번호: 1 ~ {count})")

cursor.close()
conn.close()
