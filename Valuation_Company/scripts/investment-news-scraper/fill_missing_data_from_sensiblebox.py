#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서블박스 CSV에서 누락된 투자금액, 투자단계 채우기
"""

import os
import sys
import csv
import re
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
print("센서블박스 CSV에서 누락 데이터 채우기")
print("=" * 80)

# 센서블박스 CSV 로드
csv_path = "sensible_companies_2026_01_GEMINI.csv"

sensible_data = {}

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company = row.get('기업명', '').strip()
        if not company or company in ['```', '```csv', '기업명']:
            continue

        # 투자금액 추출 (신규 컬럼)
        amount_str = row.get('신규', '').strip()
        amount = None
        if amount_str and amount_str not in ['', '-', 'N/A', '비공개']:
            # 숫자 추출 (300.0억 -> 300.0)
            match = re.search(r'(\d+(?:\.\d+)?)', amount_str)
            if match:
                amount = float(match.group(1))

        # 투자단계 (단계 컬럼)
        stage = row.get('단계', '').strip()
        if stage in ['', '-', 'N/A']:
            stage = None

        # 투자자
        investors = row.get('투자자', '').strip()
        if investors in ['', '-', 'N/A']:
            investors = None

        sensible_data[company] = {
            'amount': amount,
            'stage': stage,
            'investors': investors
        }

print(f"\n센서블박스 데이터 로드: {len(sensible_data)}개 회사")

# Deal 테이블 조회
deals = supabase.table("deals").select("*").order("number").execute()

print(f"Deal 테이블: {len(deals.data)}개")

# 업데이트
amount_updated = 0
stage_updated = 0
investors_updated = 0

print("\n" + "=" * 80)
print("업데이트 중...")
print("=" * 80)

for deal in deals.data:
    company = deal['company_name']

    if company not in sensible_data:
        continue

    sensible = sensible_data[company]
    updates = {}

    # 투자금액 업데이트
    if (not deal.get('amount') or deal.get('amount') == 0) and sensible['amount']:
        updates['amount'] = sensible['amount']
        print(f"  {deal['number']:3d}. {company:20s} - amount: {sensible['amount']}억원")
        amount_updated += 1

    # 투자단계 업데이트
    if (not deal.get('stage') or deal.get('stage') in ['-', 'None']) and sensible['stage']:
        updates['stage'] = sensible['stage']
        print(f"  {deal['number']:3d}. {company:20s} - stage: {sensible['stage']}")
        stage_updated += 1

    # 투자자 업데이트 (비어있거나 '-'일 때만)
    if (not deal.get('investors') or deal.get('investors') == '-') and sensible['investors']:
        updates['investors'] = sensible['investors']
        print(f"  {deal['number']:3d}. {company:20s} - investors: {sensible['investors'][:50]}...")
        investors_updated += 1

    # 업데이트 실행
    if updates:
        supabase.table("deals")\
            .update(updates)\
            .eq("id", deal['id'])\
            .execute()

print("\n" + "=" * 80)
print("최종 결과")
print("=" * 80)

print(f"\n✅ 투자금액 업데이트: {amount_updated}개")
print(f"✅ 투자단계 업데이트: {stage_updated}개")
print(f"✅ 투자자 업데이트: {investors_updated}개")

# 최종 통계
deals_final = supabase.table("deals").select("*").execute()

empty_amount = len([d for d in deals_final.data if not d.get('amount') or d.get('amount') == 0])
empty_stage = len([d for d in deals_final.data if not d.get('stage') or d.get('stage') in ['-', 'None']])

print(f"\n📊 업데이트 후 통계:")
print(f"  투자금액 없음: {empty_amount}개 (이전: 85개)")
print(f"  투자단계 없음: {empty_stage}개 (이전: 4개)")
