#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 직접 연결로 number 칼럼 추가
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
    from psycopg2 import sql
except ImportError:
    print("\n❌ psycopg2가 설치되어 있지 않습니다.")
    print("설치: pip install psycopg2-binary")
    sys.exit(1)

# Supabase URL에서 PostgreSQL 연결 정보 추출
supabase_url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY")

# URL: https://arxrfetgaitkgiiqabap.supabase.co
project_id = supabase_url.split('//')[1].split('.')[0]

# PostgreSQL 연결 문자열
# Supabase는 db.xxxxx.supabase.co:5432 로 접속
conn_string = f"postgresql://postgres.{project_id}:{service_key}@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

print(f"\n📡 연결 중: {project_id}")

try:
    # PostgreSQL 연결
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    print("  ✅ 연결 성공")

    # 1. number 칼럼 추가
    print("\n1️⃣ number 칼럼 추가...")
    try:
        cursor.execute("ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;")
        conn.commit()
        print("  ✅ number 칼럼 추가 완료")
    except Exception as e:
        print(f"  ⚠️  {e}")
        conn.rollback()

    # 2. 번호 할당
    print("\n2️⃣ 번호 할당 중...")
    cursor.execute("""
        WITH numbered_deals AS (
            SELECT
                id,
                ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
            FROM deals
        )
        UPDATE deals
        SET number = numbered_deals.row_num
        FROM numbered_deals
        WHERE deals.id = numbered_deals.id;
    """)
    conn.commit()
    print("  ✅ 번호 할당 완료")

    # 3. 확인
    print("\n3️⃣ 확인 (처음 10개)")
    cursor.execute("""
        SELECT number, company_name
        FROM deals
        ORDER BY number
        LIMIT 10;
    """)

    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row[0]:3d}. {row[1]}")

    # 4. 통계
    cursor.execute("SELECT COUNT(*) FROM deals;")
    count = cursor.fetchone()[0]

    print("\n" + "=" * 80)
    print("✅ 완료!")
    print("=" * 80)
    print(f"\nDeal 테이블: {count}개")
    print(f"번호: 1 ~ {count}")

    # 연결 종료
    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ 오류: {e}")
    print("\n💡 Supabase 연결 정보가 올바른지 확인하세요.")
