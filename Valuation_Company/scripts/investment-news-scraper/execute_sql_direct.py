#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase에 직접 SQL 실행 (REST API 사용)
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

def execute_sql():
    """SQL 직접 실행"""

    print("=" * 60)
    print("Deal 테이블 employees 컬럼 삭제 실행")
    print("=" * 60)

    # Supabase Management API로 SQL 실행
    # Project Reference 추출
    project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

    sql = "ALTER TABLE deals DROP COLUMN IF EXISTS employees;"

    print(f"\n실행할 SQL:")
    print(f"  {sql}\n")

    # Supabase Database API 사용
    db_url = f"https://{project_ref}.supabase.co/rest/v1/rpc/exec_sql"

    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }

    # exec_sql RPC 함수가 없을 수 있으므로 대신 직접 HTTP API 사용
    # 또는 supabase-py 라이브러리의 execute_sql 사용

    try:
        # Python으로 직접 PostgreSQL 연결 시도
        import psycopg2

        # Connection string 생성
        conn_string = f"postgresql://postgres:{SUPABASE_SERVICE_KEY}@db.{project_ref}.supabase.co:5432/postgres"

        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        cursor.execute(sql)
        conn.commit()

        print("✅ SQL 실행 성공!")
        print("   employees 컬럼이 삭제되었습니다.")

        cursor.close()
        conn.close()

    except ImportError:
        print("❌ psycopg2 라이브러리 없음")
        print("   설치: pip install psycopg2-binary")
        print("\n대안: Supabase 대시보드에서 수동 실행")
        return False
    except Exception as e:
        print(f"❌ SQL 실행 실패: {e}")
        print("\n대안: Supabase 대시보드에서 수동 실행")
        return False

    print("\n" + "=" * 60)
    return True


if __name__ == '__main__':
    execute_sql()
