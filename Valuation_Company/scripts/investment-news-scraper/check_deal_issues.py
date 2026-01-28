#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 문제 확인
1. 투자단계 빈 것들
2. 뉴스 게재 시간 vs DB 저장 시간
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
print("Deal 테이블 문제 확인")
print("=" * 80)

# 전체 Deal 조회
deals = supabase.table("deals").select("*").order("number").execute()

print(f"\n총 Deal 수: {len(deals.data)}개")

# 1. 투자단계 빈 것들
empty_stage = [d for d in deals.data if not d.get('stage') or d.get('stage') == '-']
print(f"\n1️⃣ 투자단계 비어있음: {len(empty_stage)}개")
if empty_stage:
    for deal in empty_stage[:10]:
        print(f"  - {deal['number']}. {deal['company_name']}: stage='{deal.get('stage')}'")
    if len(empty_stage) > 10:
        print(f"  ... 외 {len(empty_stage)-10}개")

# 2. 뉴스 게재일 vs 생성일 비교
print(f"\n2️⃣ 뉴스 게재일 확인:")
today_str = "2026-01-28"
today_news = [d for d in deals.data if d.get('news_date') == today_str]
print(f"  - 2026-01-28 뉴스: {len(today_news)}개")

if today_news:
    print(f"\n  샘플 (처음 5개):")
    for deal in today_news[:5]:
        print(f"    {deal['number']}. {deal['company_name']}")
        print(f"       news_date: {deal.get('news_date')}")
        print(f"       created_at: {deal.get('created_at')}")
        print(f"       news_url: {deal.get('news_url', 'N/A')[:60]}...")

# 3. 뉴스 테이블에서 실제 발행일 확인
print(f"\n3️⃣ 뉴스 테이블에서 실제 발행일 확인:")
for deal in today_news[:3]:
    if deal.get('news_url'):
        # 뉴스 테이블에서 해당 URL 찾기
        articles = supabase.table("investment_news_articles")\
            .select("published_date, article_url")\
            .eq("article_url", deal['news_url'])\
            .execute()

        if articles.data:
            actual_date = articles.data[0]['published_date']
            print(f"  {deal['company_name']}:")
            print(f"    Deal 테이블 news_date: {deal.get('news_date')}")
            print(f"    뉴스 테이블 published_date: {actual_date}")
            if actual_date != deal.get('news_date'):
                print(f"    ❌ 불일치!")
        else:
            print(f"  {deal['company_name']}: 뉴스 테이블에 없음")

print("\n" + "=" * 80)
print("확인 완료")
print("=" * 80)
