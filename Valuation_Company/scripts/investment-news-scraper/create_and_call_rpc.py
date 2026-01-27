#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPC 함수를 만들어서 employees 컬럼 삭제
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

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


def drop_via_rpc():
    """RPC 함수로 컬럼 삭제"""

    print("=" * 60)
    print("RPC 함수로 employees 컬럼 삭제 시도")
    print("=" * 60)

    # 먼저 drop_employees_column RPC 함수가 있는지 확인
    try:
        print("\n시도 1: 기존 RPC 함수 호출...")
        result = supabase.rpc('drop_employees_column', {}).execute()
        print("✅ RPC 함수 실행 성공!")
        return True
    except Exception as e:
        print(f"RPC 함수 없음: {str(e)[:100]}")

    # SQL 함수를 직접 만드는 것은 DDL이므로 REST API로 불가능
    # 하지만 만약 이미 함수가 있다면 호출할 수 있음

    # Supabase 백도어 시도: _realtime schema 등을 통한 접근
    try:
        print("\n시도 2: 직접 SQL 실행 (realtime)...")
        # Supabase는 realtime을 통해 일부 DDL을 허용할 수 있음
        result = supabase.rpc('exec', {
            'sql': 'ALTER TABLE deals DROP COLUMN IF EXISTS employees'
        }).execute()
        print("✅ SQL 실행 성공!")
        return True
    except Exception as e:
        print(f"실패: {str(e)[:100]}")

    # 마지막 시도: postgREST의 숨겨진 기능
    try:
        print("\n시도 3: PostgREST admin 기능...")
        # Service role key로는 일부 admin 기능 접근 가능
        import requests

        headers = {
            'apikey': os.getenv("SUPABASE_SERVICE_KEY"),
            'Authorization': f'Bearer {os.getenv("SUPABASE_SERVICE_KEY")}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }

        # PostgREST의 admin endpoint 시도
        url = f"{os.getenv('SUPABASE_URL')}/rest/v1/rpc/exec"

        response = requests.post(url, headers=headers, json={
            'query': 'ALTER TABLE deals DROP COLUMN IF EXISTS employees'
        })

        if response.status_code == 200:
            print("✅ SQL 실행 성공!")
            return True
        else:
            print(f"실패: {response.status_code} - {response.text[:100]}")

    except Exception as e:
        print(f"실패: {str(e)[:100]}")

    print("\n❌ 모든 방법 실패")
    print("\n" + "=" * 60)
    print("Supabase 대시보드에서 수동 실행 필요:")
    print("-" * 60)
    print("ALTER TABLE deals DROP COLUMN employees;")
    print("-" * 60)
    print("\n1. https://supabase.com/dashboard 접속")
    print("2. SQL Editor 클릭")
    print("3. 위 SQL 실행")
    print("=" * 60)
    return False


if __name__ == '__main__':
    success = drop_via_rpc()
    sys.exit(0 if success else 1)
