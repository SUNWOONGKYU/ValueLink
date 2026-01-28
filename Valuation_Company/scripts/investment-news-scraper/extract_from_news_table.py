#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 테이블(investment_news_articles)에서 투자금액, 투자단계 추출하여 Deal 테이블 업데이트
"""

import os
import sys
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

def extract_amount_from_title(title):
    """제목에서 투자금액 추출 (억원 단위)"""
    # 패턴들 (우선순위 순서)
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*억\s*원', 1),  # 100억원
        (r'(\d+(?:\.\d+)?)\s*억', 1),      # 100억
        (r'(\d+)\s*조', 10000),             # 1조 = 10000억
        (r'\$\s*(\d+(?:\.\d+)?)\s*M', 13), # $10M = 130억
        (r'(\d+)만\s*달러', 0.0013),       # 100만달러 = 13억
    ]

    for pattern, multiplier in patterns:
        match = re.search(pattern, title)
        if match:
            amount = float(match.group(1)) * multiplier
            return round(amount, 1)

    return None

def extract_stage_from_title(title):
    """제목에서 투자단계 추출"""
    stages = [
        ('시리즈C', ['시리즈C', 'Series C']),
        ('시리즈B', ['시리즈B', 'Series B']),
        ('시리즈A', ['시리즈A', 'Series A']),
        ('프리A', ['프리A', 'Pre-A', 'PreA']),
        ('시드', ['시드', 'Seed']),
        ('브릿지', ['브릿지', 'Bridge']),
    ]

    for stage_name, keywords in stages:
        for keyword in keywords:
            if keyword in title:
                return stage_name

    return None

print("=" * 80)
print("뉴스 테이블에서 투자금액, 투자단계 추출")
print("=" * 80)

# Deal 테이블 조회
deals = supabase.table("deals").select("*").order("number").execute()

print(f"\n총 Deal: {len(deals.data)}개")

amount_updated = 0
stage_updated = 0

for deal in deals.data:
    company = deal['company_name']
    news_url = deal.get('news_url')

    if not news_url:
        continue

    # 뉴스 테이블에서 해당 기사 찾기
    articles = supabase.table("investment_news_articles")\
        .select("article_title")\
        .eq("article_url", news_url)\
        .execute()

    if not articles.data:
        continue

    title = articles.data[0]['article_title']

    updates = {}

    # 투자금액 추출
    if not deal.get('amount') or deal.get('amount') == 0:
        amount = extract_amount_from_title(title)
        if amount:
            updates['amount'] = amount
            print(f"  {deal['number']:3d}. {company:20s} - amount: {amount}억원")
            amount_updated += 1

    # 투자단계 추출
    if not deal.get('stage') or deal.get('stage') in ['-', 'None']:
        stage = extract_stage_from_title(title)
        if stage:
            updates['stage'] = stage
            print(f"  {deal['number']:3d}. {company:20s} - stage: {stage}")
            stage_updated += 1

    # 업데이트
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

# 최종 통계
deals_final = supabase.table("deals").select("*").execute()

empty_amount = len([d for d in deals_final.data if not d.get('amount') or d.get('amount') == 0])
empty_stage = len([d for d in deals_final.data if not d.get('stage') or d.get('stage') in ['-', 'None']])

print(f"\n📊 업데이트 후:")
print(f"  투자금액 없음: {empty_amount}개 (이전: 85개)")
print(f"  투자단계 없음: {empty_stage}개 (이전: 4개)")
