#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엘리시젠 추가
"""

import os
import sys
from datetime import datetime
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
print("엘리시젠 추가")
print("=" * 80)

# 1. investment_news_articles에 기사 추가
article_data = {
    'site_number': 99,
    'site_name': '금융경제플러스',
    'site_url': '',
    'article_title': '엘리시젠, AAV 유전자치료제...정책자금·민간자본이 동시에 선택',
    'article_url': 'https://www.kndaily.co.kr/news/articleView.html?idxno=308684',
    'published_date': datetime.now().strftime('%Y-%m-%d')
}

print("\n1️⃣ investment_news_articles에 기사 추가...")

# 중복 확인
existing = supabase.table("investment_news_articles")\
    .select("id")\
    .eq("article_url", article_data['article_url'])\
    .execute()

if not existing.data:
    try:
        supabase.table("investment_news_articles").insert(article_data).execute()
        print("  ✅ 기사 추가 완료")
    except Exception as e:
        print(f"  ❌ 오류: {e}")
else:
    print("  ⚠️  이미 있음")

# 2. Deal 테이블에 추가
print("\n2️⃣ Deal 테이블에 추가...")

deal_data = {
    'company_name': '엘리시젠',
    'industry': 'AAV 유전자치료제',
    'stage': '시리즈C',
    'investors': '데일리파트너스, NH투자증권',
    'amount': 50.0,
    'news_title': article_data['article_title'],
    'news_url': article_data['article_url'],
    'site_name': article_data['site_name'],
    'news_date': article_data['published_date'],
    'created_at': datetime.now().isoformat()
}

# 중복 확인
existing = supabase.table("deals")\
    .select("id")\
    .eq("company_name", "엘리시젠")\
    .execute()

if not existing.data:
    try:
        supabase.table("deals").insert(deal_data).execute()
        print("  ✅ Deal 추가 완료")
    except Exception as e:
        print(f"  ❌ 오류: {e}")
else:
    print("  ⚠️  이미 있음")

# 3. 번호 재할당
print("\n3️⃣ 전체 Deal 번호 재할당...")

all_deals = supabase.table("deals").select("id").order("created_at").execute()

for idx, deal in enumerate(all_deals.data, 1):
    supabase.table("deals").update({'number': idx}).eq("id", deal['id']).execute()

print(f"  ✅ {len(all_deals.data)}개 번호 재할당 완료")

# 4. 최종 통계
print("\n" + "=" * 80)
print("최종 결과")
print("=" * 80)

count_result = supabase.table("deals").select("id", count="exact").execute()
articles_count = supabase.table("investment_news_articles").select("id", count="exact").execute()

print(f"\n✅ Deal 테이블: {count_result.count}개")
print(f"✅ investment_news_articles: {articles_count.count}개")

print("\n🎉 센서블박스(124개) 완료!")
print(f"   커버리지: {count_result.count}/124 = {count_result.count/124*100:.1f}%")

# 엘리시젠 확인
result = supabase.table("deals").select("number, company_name, investors, amount").eq("company_name", "엘리시젠").execute()

if result.data:
    deal = result.data[0]
    print(f"\n✅ 엘리시젠 추가 확인:")
    print(f"   번호: {deal['number']}")
    print(f"   투자자: {deal['investors']}")
    print(f"   금액: {deal['amount']}억원")
