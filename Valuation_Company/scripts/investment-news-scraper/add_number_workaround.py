#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
number 칼럼 없이 Deal 번호 확인 - remarks 필드 활용
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

print("=" * 80)
print("Deal 테이블 번호 매기기")
print("=" * 80)

# 방법: remarks 필드에 번호 저장
print("\n💡 방법: remarks 필드에 '[번호]' 형태로 저장")

# 1. 모든 Deal 조회 (created_at 순)
print("\n📊 Deal 테이블 조회 중...")
result = supabase.table("deals").select("*").order("created_at").execute()
deals = result.data

print(f"  ✅ {len(deals)}개 레코드 발견")

# 2. remarks 필드에 번호 저장
print("\n🔢 번호 매기는 중...")

for idx, deal in enumerate(deals, 1):
    deal_id = deal['id']
    current_remarks = deal.get('remarks', '') or ''

    # 기존 remarks에 번호 추가
    new_remarks = f"[{idx}] " + current_remarks if current_remarks else f"[{idx}]"

    try:
        supabase.table("deals")\
            .update({'remarks': new_remarks})\
            .eq("id", deal_id)\
            .execute()

        if idx % 20 == 0:
            print(f"  진행: {idx}/{len(deals)}")
    except Exception as e:
        print(f"  ❌ ID {deal_id} 실패: {e}")

print(f"  ✅ {len(deals)}개 번호 매기기 완료")

# 3. 확인
print("\n📋 확인 (처음 10개)")
result = supabase.table("deals")\
    .select("company_name, remarks")\
    .order("created_at")\
    .limit(10)\
    .execute()

for deal in result.data:
    remarks = deal['remarks'] or ''
    print(f"  {remarks:6s} {deal['company_name']}")

print("\n" + "=" * 80)
print("✅ 완료!")
print("=" * 80)
print(f"\nDeal 테이블: {len(deals)}개")
print(f"번호: [1] ~ [{len(deals)}]")
print("\n💡 remarks 필드에 [번호] 형태로 저장되었습니다.")
