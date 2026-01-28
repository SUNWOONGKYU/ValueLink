#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 시도: number 칼럼 추가
"""

import os
import sys
from dotenv import load_dotenv
from urllib.parse import quote_plus

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

try:
    import psycopg2
    print("✅ psycopg2 로드됨")
except ImportError:
    print("psycopg2 설치 중...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "psycopg2-binary"])
    import psycopg2
    print("✅ psycopg2 설치 완료")

print("=" * 80)
print("Deal 테이블에 number 칼럼 추가 - 최종 시도")
print("=" * 80)

# 환경 변수
supabase_url = os.getenv("SUPABASE_URL")
db_password = os.getenv("DB_PASSWORD")

project_id = supabase_url.split('//')[1].split('.')[0]

print(f"\n📡 프로젝트 ID: {project_id}")
print(f"🔑 비밀번호 길이: {len(db_password)}자")

# URL 인코딩된 비밀번호
encoded_password = quote_plus(db_password)

# 여러 호스트 시도
hosts = [
    f"db.{project_id}.supabase.co",
    f"{project_id}.supabase.co",
    f"aws-0-ap-northeast-2.pooler.supabase.com"
]

ports = [5432, 6543]

conn = None

for host in hosts:
    for port in ports:
        print(f"\n🔄 시도: {host}:{port}")

        conn_strings = [
            f"postgresql://postgres:{encoded_password}@{host}:{port}/postgres",
            f"host={host} port={port} dbname=postgres user=postgres password={db_password}",
        ]

        for idx, conn_str in enumerate(conn_strings, 1):
            try:
                print(f"  방법 {idx}...", end=' ')
                conn = psycopg2.connect(conn_str, connect_timeout=10)
                print("✅ 성공!")
                break
            except Exception as e:
                error_msg = str(e)
                if 'Name or service not known' in error_msg:
                    print("❌ 호스트 없음")
                elif 'Tenant or user not found' in error_msg:
                    print("❌ 인증 실패")
                elif 'Connection refused' in error_msg:
                    print("❌ 연결 거부")
                else:
                    print(f"❌ {error_msg[:50]}")

        if conn:
            break

    if conn:
        print(f"\n✅ 연결 성공: {host}:{port}")
        break

if not conn:
    print("\n" + "=" * 80)
    print("❌ 모든 연결 시도 실패")
    print("=" * 80)

    print("\n📋 Supabase Dashboard에서 직접 실행 필요:")
    print(f"   URL: https://supabase.com/dashboard/project/{project_id}/editor")
    print("\n   SQL Editor에서 다음 실행:")

    sql = """ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;

WITH numbered_deals AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
    FROM deals
)
UPDATE deals SET number = numbered_deals.row_num
FROM numbered_deals WHERE deals.id = numbered_deals.id;

SELECT number, company_name FROM deals ORDER BY number LIMIT 5;"""

    print("\n" + "-" * 80)
    print(sql)
    print("-" * 80)

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
print(f"\nDeal 테이블: {count}개")
print(f"번호: 1 ~ {count}")

cursor.close()
conn.close()
