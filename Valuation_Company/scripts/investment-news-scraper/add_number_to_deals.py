#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블에 번호 칼럼 추가 (1번부터)
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
    os.getenv("SUPABASE_SERVICE_KEY"))

print("=" * 80)
print("Deal 테이블에 번호 칼럼 추가")
print("=" * 80)

# 1. 모든 Deal 조회 (created_at 순서로 정렬)
print("\n📊 Deal 테이블 조회 중...")
result = supabase.table("deals").select("*").order("created_at").execute()
deals = result.data

print(f"  ✅ {len(deals)}개 레코드 발견")

# 2. 번호 할당 (1번부터)
print("\n🔢 번호 할당 중...")

for idx, deal in enumerate(deals, 1):
    deal_id = deal['id']

    try:
        # number 필드 업데이트
        supabase.table("deals")\
            .update({'number': idx})\
            .eq("id", deal_id)\
            .execute()

        if idx % 10 == 0:
            print(f"  진행: {idx}/{len(deals)}")

    except Exception as e:
        print(f"  ❌ ID {deal_id} 업데이트 실패: {e}")

print(f"  ✅ {len(deals)}개 레코드 번호 할당 완료")

# 3. 확인
print("\n📋 번호 할당 확인 (처음 10개)")
result = supabase.table("deals").select("number, company_name").order("number").limit(10).execute()

for deal in result.data:
    print(f"  {deal['number']:3d}. {deal['company_name']}")

print("\n" + "=" * 80)
print("✅ 완료!")
print("=" * 80)

# 최종 통계
count_result = supabase.table("deals").select("id", count="exact").execute()
print(f"\nDeal 테이블 총 레코드: {count_result.count}개")
print(f"번호: 1 ~ {count_result.count}")
