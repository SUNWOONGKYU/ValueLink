#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 중복 확인 및 정리
"""

import os
import sys
import csv
from dotenv import load_dotenv
from supabase import create_client, Client
from collections import Counter

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
print("Deal 테이블 분석")
print("=" * 80)

# 1. Deal 테이블 전체 조회
result = supabase.table("deals").select("*").execute()
all_deals = result.data

print(f"\n📊 Deal 테이블 총 레코드: {len(all_deals)}개")

# 2. 기업명별 카운트
company_counts = Counter([deal['company_name'] for deal in all_deals])

# 3. 중복 확인
duplicates = {name: count for name, count in company_counts.items() if count > 1}

if duplicates:
    print(f"\n⚠️  중복 발견: {len(duplicates)}개 기업")
    for company, count in sorted(duplicates.items(), key=lambda x: -x[1])[:10]:
        print(f"   {company:30s}: {count}개")
else:
    print("\n✅ 중복 없음")

# 4. 센서블박스 127개 기업과 비교
GEMINI_CSV = 'sensible_companies_2026_01_GEMINI.csv'

sensible_companies = set()
with open(GEMINI_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sensible_companies.add(row['기업명'])

print(f"\n📋 센서블박스 기업: {len(sensible_companies)}개")

# Deal에 있는 센서블박스 기업
deal_companies = set([deal['company_name'] for deal in all_deals])
sensible_in_deal = sensible_companies & deal_companies

print(f"✅ Deal에 있는 센서블박스 기업: {len(sensible_in_deal)}개")

# 5. 미발견 기업
missing = sensible_companies - deal_companies
print(f"\n❌ 미발견 기업: {len(missing)}개")
for idx, company in enumerate(sorted(missing), 1):
    print(f"   {idx:2d}. {company}")

# 6. 센서블박스가 아닌 기업 (기존 데이터)
non_sensible = deal_companies - sensible_companies
print(f"\n🔍 센서블박스 외 기업: {len(non_sensible)}개")
if len(non_sensible) <= 20:
    for company in sorted(non_sensible):
        print(f"   - {company}")
