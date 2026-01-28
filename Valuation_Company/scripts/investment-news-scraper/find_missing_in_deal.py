#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서블박스에는 있지만 Deal 테이블에는 없는 기업 찾기
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
print("센서블박스 vs Deal 테이블 비교")
print("=" * 80)

# 1. 센서블박스 기업 로드
sensible_companies = []
with open(GEMINI_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company_name = row['기업명']
        if company_name and company_name not in ['```', '```csv', '기업명']:
            sensible_companies.append(company_name)

# 중복 제거
sensible_set = set(sensible_companies)
print(f"\n📋 센서블박스 유효 기업: {len(sensible_set)}개")

if len(sensible_companies) != len(sensible_set):
    duplicates = [c for c in sensible_set if sensible_companies.count(c) > 1]
    print(f"   ⚠️  중복 발견: {duplicates}")

# 2. Deal 테이블 기업 로드
result = supabase.table("deals").select("company_name").execute()
deal_companies = set([deal['company_name'] for deal in result.data])

print(f"📊 Deal 테이블 기업: {len(deal_companies)}개")

# 3. 비교
missing_in_deal = sensible_set - deal_companies
found_in_deal = sensible_set & deal_companies

print(f"✅ Deal에 있는 센서블박스 기업: {len(found_in_deal)}개")
print(f"❌ Deal에 없는 센서블박스 기업: {len(missing_in_deal)}개")

if missing_in_deal:
    print("\n" + "=" * 80)
    print("Deal 테이블에 없는 센서블박스 기업 (상세)")
    print("=" * 80)

    # CSV에서 상세 정보 가져오기
    with open(GEMINI_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_name = row['기업명']
            if company_name in missing_in_deal:
                print(f"\n{company_name}:")
                print(f"  투자자: {row.get('투자자', '')}")
                print(f"  주요사업: {row.get('주요사업', '')}")
                print(f"  단계: {row.get('단계', '')}")
                print(f"  신규: {row.get('신규', '')}")

# 4. Deal에는 있지만 센서블박스에는 없는 기업
extra_in_deal = deal_companies - sensible_set

if extra_in_deal:
    print("\n" + "=" * 80)
    print("Deal에는 있지만 센서블박스에는 없는 기업")
    print("=" * 80)
    for company in sorted(extra_in_deal):
        print(f"  - {company}")
