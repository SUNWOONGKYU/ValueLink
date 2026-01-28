#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수동으로 찾은 3개 기업 기사 추가
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

# 수동으로 찾은 3개 기업 기사
manual_articles = [
    {
        'site_number': 99,
        'site_name': '이투데이',
        'site_url': '',
        'article_title': 'FSN 子 부스터즈, 200억 규모 투자 유치… "3년 내 기업가치 1조 달성 목표"',
        'article_url': 'https://www.etoday.co.kr/news/view/2531426',
        'published_date': datetime.now().strftime('%Y-%m-%d')
    },
    {
        'site_number': 1,
        'site_name': 'WOWTALE',
        'site_url': '',
        'article_title': '에봄에이아이, 끌림벤처스서 시드 투자 유치 및 딥테크 팁스 선정',
        'article_url': 'https://wowtale.net/2026/01/07/252857/',
        'published_date': datetime.now().strftime('%Y-%m-%d')
    },
    {
        'site_number': 99,
        'site_name': '머니S',
        'site_url': '',
        'article_title': "네이버 D2SF, AI 스타트업 '소서릭스'에 신규 투자",
        'article_url': 'https://www.moneys.co.kr/article/2025123010574577445',
        'published_date': datetime.now().strftime('%Y-%m-%d')
    }
]

print("=" * 80)
print("수동으로 찾은 3개 기업 기사 추가")
print("=" * 80)

added = 0
duplicate = 0

for idx, article in enumerate(manual_articles, 1):
    company_name = article['article_title'].split(',')[0].split(' ')[0]

    print(f"\n[{idx}/3] {article['article_title'][:60]}...")
    print(f"  URL: {article['article_url']}")
    print(f"  사이트: {article['site_name']}")

    # 중복 확인
    existing = supabase.table("investment_news_articles")\
        .select("id")\
        .eq("article_url", article['article_url'])\
        .execute()

    if not existing.data:
        try:
            supabase.table("investment_news_articles").insert(article).execute()
            print(f"  ✅ DB 저장 완료")
            added += 1
        except Exception as e:
            print(f"  ❌ DB 오류: {e}")
    else:
        print(f"  ⚠️  중복 (이미 존재)")
        duplicate += 1

print(f"\n{'='*80}")
print(f"✅ 새로 추가: {added}개")
print(f"⚠️  중복: {duplicate}개")
print(f"{'='*80}")

# 최종 통계
count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
print(f"\ninvestment_news_articles 테이블 총 레코드: {count_result.count}개")
