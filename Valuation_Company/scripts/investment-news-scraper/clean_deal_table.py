#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 정리 - 센서블박스 기업만 남기기
"""

import os
import sys
import csv
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

GEMINI_CSV = 'sensible_companies_2026_01_GEMINI.csv'

print("=" * 80)
print("Deal 테이블 정리 - 센서블박스 기업만 남기기")
print("=" * 80)

# 1. 센서블박스 기업 로드
sensible_companies = set()
with open(GEMINI_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company_name = row['기업명']
        if company_name and company_name not in ['```', '```csv']:
            sensible_companies.add(company_name)

print(f"\n📋 센서블박스 기업: {len(sensible_companies)}개")

# 2. Deal 테이블 전체 조회
result = supabase.table("deals").select("*").execute()
all_deals = result.data

print(f"📊 현재 Deal 레코드: {len(all_deals)}개")

# 3. 삭제할 레코드 찾기
to_delete = []
sensible_deals = []
duplicate_ids = {}

for deal in all_deals:
    company_name = deal['company_name']
    deal_id = deal['id']

    if company_name in sensible_companies:
        # 센서블박스 기업
        if company_name in duplicate_ids:
            # 중복 - 최신 것만 남기고 삭제
            to_delete.append(deal_id)
            print(f"   ⚠️  중복 삭제: {company_name} (ID: {deal_id})")
        else:
            duplicate_ids[company_name] = deal_id
            sensible_deals.append(deal)
    else:
        # 센서블박스 외 기업 - 삭제
        to_delete.append(deal_id)

print(f"\n✅ 유지할 레코드: {len(sensible_deals)}개")
print(f"❌ 삭제할 레코드: {len(to_delete)}개")

# 4. 삭제 실행
if to_delete:
    print("\n🗑️  삭제 중...")
    for deal_id in to_delete:
        try:
            supabase.table("deals").delete().eq("id", deal_id).execute()
        except Exception as e:
            print(f"   ❌ 삭제 실패 (ID: {deal_id}): {e}")

    print(f"   ✅ {len(to_delete)}개 삭제 완료")

# 5. 최종 확인
final_result = supabase.table("deals").select("id", count="exact").execute()
print(f"\n📊 최종 Deal 레코드: {final_result.count}개")

# 6. 미발견 기업
deal_companies = set([deal['company_name'] for deal in sensible_deals])
missing = sensible_companies - deal_companies

print(f"\n❌ 미발견 기업: {len(missing)}개")
for idx, company in enumerate(sorted(missing), 1):
    print(f"   {idx:2d}. {company}")

print("\n✅ Deal 테이블 정리 완료!")
