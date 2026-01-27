#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 스키마 업데이트 - employees 컬럼 삭제
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


def update_schema():
    """Deal 테이블에서 employees 컬럼 삭제"""

    print("=" * 60)
    print("Deal 테이블 스키마 업데이트")
    print("=" * 60)

    try:
        # Supabase REST API로는 DDL 실행 불가
        # SQL 파일을 Supabase 대시보드에서 직접 실행해야 함
        print("\n⚠️  주의: Supabase REST API로는 DDL(ALTER TABLE) 실행 불가")
        print("\n다음 단계를 따라 직접 실행하세요:")
        print("\n1. Supabase 대시보드 접속: https://supabase.com/dashboard")
        print("2. SQL Editor 클릭")
        print("3. 아래 SQL 실행:\n")

        print("-" * 60)
        print("ALTER TABLE deals DROP COLUMN IF EXISTS employees;")
        print("-" * 60)

        print("\n또는:")
        print("\n4. 파일 내용 복사: remove_employees_column.sql")
        print("5. SQL Editor에 붙여넣기")
        print("6. Run 클릭")

        print("\n" + "=" * 60)

        # 현재 테이블 구조 확인
        print("\n현재 Deal 테이블 샘플 데이터 확인:")
        result = supabase.table("deals").select("*").limit(1).execute()

        if result.data and len(result.data) > 0:
            sample = result.data[0]
            print("\n컬럼 목록:")
            for idx, key in enumerate(sample.keys(), 1):
                print(f"  {idx}. {key}")

            if 'employees' in sample:
                print("\n✅ employees 컬럼 존재 - 삭제 필요")
            else:
                print("\n✅ employees 컬럼 없음 - 이미 삭제됨")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n❌ 에러: {e}")


if __name__ == '__main__':
    update_schema()
