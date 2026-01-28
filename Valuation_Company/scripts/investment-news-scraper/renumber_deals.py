#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 number를 최신순으로 재정렬
최신 투자가 1번
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

print("=" * 80)
print("Deal number 재정렬 (최신순)")
print("=" * 80 + "\n")

# Step 1: 모든 Deal을 news_date 역순으로 가져오기
deals = supabase.table('deals').select('*').order('news_date', desc=True).order('id', desc=True).execute()

print(f"총 Deal 수: {len(deals.data)}개\n")

# Step 2: 중복 방지를 위해 먼저 모든 number를 음수로 변경
print("Step 1: number를 임시 음수로 변경 중...\n")

for i, deal in enumerate(deals.data, 1):
    supabase.table('deals').update({
        'number': -i
    }).eq('id', deal['id']).execute()

print("✅ 임시 변경 완료\n")

# Step 3: 다시 양수로 변경 (최신 = 1)
print("Step 2: number를 최신순 양수로 변경 중...\n")

for new_number, deal in enumerate(deals.data, 1):
    old_number = deal['number']
    company = deal['company_name']
    news_date = deal.get('news_date', '-')

    print(f"  #{new_number:3d}: {company:30s} ({news_date})")

    # 업데이트
    supabase.table('deals').update({
        'number': new_number
    }).eq('id', deal['id']).execute()

print("\n✅ 완료!")
print(f"최신: #{1} / 가장 오래된: #{len(deals.data)}")
print("=" * 80)
