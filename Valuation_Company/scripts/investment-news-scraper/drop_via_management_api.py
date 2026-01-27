#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Management API로 SQL 실행
"""

import os
import sys
import requests
from dotenv import load_dotenv

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def drop_via_management_api():
    """Management API로 SQL 실행"""

    print("=" * 60)
    print("Supabase Management API로 employees 컬럼 삭제")
    print("=" * 60)

    project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

    # Supabase API에서 SQL을 직접 실행하는 방법 시도
    # PostgREST를 우회해서 직접 실행

    # 방법 1: pg_catalog를 통한 우회
    print("\n방법 1: pg_catalog 우회 시도...")

    # 실제로는 Supabase에서 DDL을 REST API로 직접 실행할 방법이 없음
    # 하지만 Python psycopg2로 다시 시도해보자

    try:
        import psycopg2

        # 여러 연결 방식 시도
        connection_strings = [
            # IPv4 직접 연결 시도
            f"postgresql://postgres:{DB_PASSWORD}@15.164.120.176:6543/postgres?options=project%3D{project_ref}",
            # Session mode pooler
            f"postgresql://postgres.{project_ref}:{DB_PASSWORD}@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres",
            # Transaction mode pooler
            f"postgresql://postgres.{project_ref}:{DB_PASSWORD}@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require",
        ]

        for i, conn_str in enumerate(connection_strings, 1):
            try:
                print(f"\n연결 시도 {i}...")
                conn = psycopg2.connect(conn_str)
                cursor = conn.cursor()

                # employees 컬럼 존재 확인
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'deals' AND column_name = 'employees'
                """)

                if cursor.fetchone():
                    print("✅ employees 컬럼 발견")
                    print("SQL 실행: ALTER TABLE deals DROP COLUMN employees;")

                    cursor.execute("ALTER TABLE deals DROP COLUMN employees;")
                    conn.commit()

                    print("✅✅✅ employees 컬럼 삭제 성공! ✅✅✅")
                    cursor.close()
                    conn.close()
                    return True
                else:
                    print("ℹ️  employees 컬럼이 이미 없습니다")
                    cursor.close()
                    conn.close()
                    return True

            except Exception as e:
                print(f"   연결 실패: {str(e)[:80]}")
                continue

        print("\n❌ 모든 연결 방식 실패")
        return False

    except ImportError:
        print("❌ psycopg2 없음")
        return False


if __name__ == '__main__':
    success = drop_via_management_api()
    if not success:
        print("\n" + "=" * 60)
        print("자동 실행 실패 - 수동 실행 필요")
        print("=" * 60)
        print("\nSupabase 대시보드에서 실행:")
        print("ALTER TABLE deals DROP COLUMN employees;")
        print("=" * 60)
    sys.exit(0 if success else 1)
