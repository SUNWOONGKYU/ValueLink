#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Python 클라이언트로 employees 컬럼 삭제
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# Service Role Key로 Supabase 클라이언트 생성
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


def drop_employees_column():
    """employees 컬럼 삭제"""

    print("=" * 60)
    print("Deal 테이블 employees 컬럼 확인 및 수동 삭제 안내")
    print("=" * 60)

    try:
        # 현재 테이블 구조 확인
        result = supabase.table("deals").select("*").limit(1).execute()

        if result.data and len(result.data) > 0:
            sample = result.data[0]

            if 'employees' in sample:
                print("\n✅ employees 컬럼 존재 확인")
                print("\n⚠️  PostgreSQL DDL은 REST API로 실행 불가")
                print("   아래 SQL을 복사해서 Supabase 대시보드에서 실행하세요:\n")
                print("-" * 60)
                print("ALTER TABLE deals DROP COLUMN employees;")
                print("-" * 60)
                print("\n📍 실행 방법:")
                print("1. https://supabase.com/dashboard 접속")
                print("2. SQL Editor 클릭")
                print("3. 위 SQL 붙여넣기")
                print("4. Run 클릭")
            else:
                print("\n✅ employees 컬럼이 이미 삭제되었습니다!")
                return True

        print("\n" + "=" * 60)
        return False

    except Exception as e:
        print(f"❌ 에러: {e}")
        return False


if __name__ == '__main__':
    drop_employees_column()
