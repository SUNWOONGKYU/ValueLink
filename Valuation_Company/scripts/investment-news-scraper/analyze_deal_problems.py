#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 데이터 품질 분석
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
print("Deal 테이블 데이터 품질 분석")
print("=" * 80)

# 전체 Deal 조회
deals = supabase.table("deals").select("*").order("number").execute()

print(f"\n총 Deal 수: {len(deals.data)}개")

# 1. 투자금액 누락
print("\n" + "=" * 80)
print("1️⃣ 투자금액 (amount) 누락 분석")
print("=" * 80)

empty_amount = [d for d in deals.data if not d.get('amount') or d.get('amount') in [0, None, '']]
print(f"\n투자금액 없음: {len(empty_amount)}개 / {len(deals.data)}개")

if empty_amount:
    print(f"\n상위 20개:")
    for deal in empty_amount[:20]:
        print(f"  {deal['number']:3d}. {deal['company_name']:20s} - amount={deal.get('amount')}")
        print(f"       URL: {deal.get('news_url', 'N/A')[:70]}")

# 2. 투자단계 누락
print("\n" + "=" * 80)
print("2️⃣ 투자단계 (stage) 누락 분석")
print("=" * 80)

empty_stage = [d for d in deals.data if not d.get('stage') or d.get('stage') in ['-', 'None', '']]
print(f"\n투자단계 없음: {len(empty_stage)}개 / {len(deals.data)}개")

if empty_stage:
    print(f"\n전체 목록:")
    for deal in empty_stage:
        print(f"  {deal['number']:3d}. {deal['company_name']:20s} - stage='{deal.get('stage')}'")
        print(f"       URL: {deal.get('news_url', 'N/A')[:70]}")

# 3. 투자자 누락
print("\n" + "=" * 80)
print("3️⃣ 투자자 (investors) 누락 분석")
print("=" * 80)

empty_investors = [d for d in deals.data if not d.get('investors') or d.get('investors') in ['-', '', 'N/A']]
print(f"\n투자자 없음: {len(empty_investors)}개 / {len(deals.data)}개")

if empty_investors:
    print(f"\n상위 10개:")
    for deal in empty_investors[:10]:
        print(f"  {deal['number']:3d}. {deal['company_name']:20s}")

# 4. 투자자 길이 분석 (두 줄 표시 관련)
print("\n" + "=" * 80)
print("4️⃣ 투자자 텍스트 길이 분석 (두 줄 표시 관련)")
print("=" * 80)

investors_with_text = [d for d in deals.data if d.get('investors') and d['investors'] not in ['-', '', 'N/A']]
print(f"\n투자자 정보 있음: {len(investors_with_text)}개")

# 길이별 분포
length_dist = {}
for deal in investors_with_text:
    inv_text = deal['investors']
    length = len(inv_text)

    if length < 30:
        key = "30자 미만"
    elif length < 60:
        key = "30-60자"
    elif length < 90:
        key = "60-90자"
    else:
        key = "90자 이상"

    length_dist[key] = length_dist.get(key, 0) + 1

print("\n투자자 텍스트 길이 분포:")
for key in ["30자 미만", "30-60자", "60-90자", "90자 이상"]:
    count = length_dist.get(key, 0)
    print(f"  {key}: {count}개")

# 긴 투자자 텍스트 샘플
print("\n긴 투자자 텍스트 샘플 (60자 이상):")
long_investors = [d for d in investors_with_text if len(d['investors']) >= 60]
for deal in long_investors[:5]:
    inv_text = deal['investors']
    print(f"  {deal['number']:3d}. {deal['company_name']:20s} ({len(inv_text)}자)")
    print(f"       \"{inv_text}\"")

# 5. 뉴스 날짜 분포 (통계 관련)
print("\n" + "=" * 80)
print("5️⃣ 뉴스 날짜 분포 (투자 통계 관련)")
print("=" * 80)

from collections import Counter
from datetime import datetime, timedelta

date_counter = Counter([d['news_date'] for d in deals.data if d.get('news_date')])

print(f"\n전체 날짜 종류: {len(date_counter)}개")
print(f"\n날짜별 분포 (상위 20개):")
for date, count in sorted(date_counter.items(), reverse=True)[:20]:
    print(f"  {date}: {count}개")

# 2026년 데이터만 확인
deals_2026 = [d for d in deals.data if d.get('news_date', '').startswith('2026')]
print(f"\n2026년 뉴스: {len(deals_2026)}개")

# 날짜 계산
today = datetime.now()
yesterday = today - timedelta(days=1)
week_ago = today - timedelta(days=7)

yesterday_str = yesterday.strftime('%Y-%m-%d')
week_ago_str = week_ago.strftime('%Y-%m-%d')
today_str = today.strftime('%Y-%m-%d')

print(f"\n날짜 기준:")
print(f"  오늘: {today_str}")
print(f"  어제: {yesterday_str}")
print(f"  7일 전: {week_ago_str}")

# 어제 투자
yesterday_deals = [d for d in deals.data if d.get('news_date') == yesterday_str]
print(f"\n어제 ({yesterday_str}) 투자: {len(yesterday_deals)}개")

# 지난주 (7일 전 ~ 어제)
last_week_deals = [d for d in deals.data if d.get('news_date') and week_ago_str <= d.get('news_date') < today_str]
print(f"지난주 ({week_ago_str} ~ {yesterday_str}): {len(last_week_deals)}개")

# 금년 누적
year_deals = [d for d in deals.data if d.get('news_date', '').startswith('2026')]
print(f"금년 누적 (2026-01-01 ~): {len(year_deals)}개")

print("\n" + "=" * 80)
print("분석 완료")
print("=" * 80)
