#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블에서 employees 컬럼 삭제 (PostgreSQL 직접 연결)
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

SUPABASE_URL = os.getenv("SUPABASE_URL")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def drop_employees_column():
    """employees 컬럼 삭제"""

    print("=" * 60)
    print("Deal 테이블 employees 컬럼 삭제")
    print("=" * 60)

    try:
        import psycopg2

        # Project reference 추출
        project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

        # Supabase 직접 연결 (Direct connection, not pooler)
        # 형식: postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres
        conn_string = f"postgresql://postgres:{DB_PASSWORD}@db.{project_ref}.supabase.co:5432/postgres"

        print(f"\n데이터베이스 연결 중...")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # employees 컬럼 존재 확인
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'deals' AND column_name = 'employees'
        """)

        if cursor.fetchone():
            print("✅ employees 컬럼 발견")
            print("\nSQL 실행 중: ALTER TABLE deals DROP COLUMN employees;")

            # 컬럼 삭제
            cursor.execute("ALTER TABLE deals DROP COLUMN employees;")
            conn.commit()

            print("✅ employees 컬럼 삭제 완료!")
        else:
            print("ℹ️  employees 컬럼이 이미 삭제되었거나 존재하지 않습니다.")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        return True

    except ImportError:
        print("❌ psycopg2 라이브러리를 찾을 수 없습니다.")
        print("   설치: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        print(f"\n에러 상세: {type(e).__name__}")
        return False


if __name__ == '__main__':
    success = drop_employees_column()
    sys.exit(0 if success else 1)
