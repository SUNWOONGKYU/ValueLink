#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자자 포트폴리오 검색 (데일리파트너스, NH투자증권)
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import time

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

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

print("=" * 80)
print("투자자 포트폴리오 검색")
print("=" * 80)

investors = [
    '데일리파트너스',
    'NH투자증권',
    '데일리파트너스-NH투자증권'
]

print("\n🔍 투자자:")
for inv in investors:
    print(f"  - {inv}")

def search_investor_portfolio(investor):
    """투자자가 투자한 회사 검색"""

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    queries = [
        f"{investor} 투자",
        f"{investor} 투자유치",
        f"{investor} 시리즈",
        f"{investor} 스타트업 투자",
    ]

    found_companies = []

    for query in queries:
        params = {
            'query': query,
            'display': 100,
            'sort': 'date'
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                items = response.json().get('items', [])

                for item in items:
                    title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                    link = item.get('originallink') or item.get('link')

                    # 투자 키워드 확인
                    investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
                    if not any(kw in title for kw in investment_keywords):
                        continue

                    found_companies.append({
                        'title': title,
                        'url': link,
                        'query': query
                    })

            time.sleep(0.1)

        except Exception as e:
            continue

    return found_companies

print("\n" + "=" * 80)
print("검색 결과")
print("=" * 80)

all_results = []

for investor in investors:
    print(f"\n🔍 {investor}")
    results = search_investor_portfolio(investor)

    if results:
        print(f"  ✅ {len(results)}개 기사 발견")

        # 상위 5개만 출력
        for idx, article in enumerate(results[:5], 1):
            print(f"\n  [{idx}] {article['title'][:70]}...")
            print(f"      URL: {article['url']}")

        all_results.extend(results)
    else:
        print(f"  ❌ 기사 없음")

# 중복 제거
unique_results = []
seen_urls = set()

for article in all_results:
    if article['url'] not in seen_urls:
        seen_urls.add(article['url'])
        unique_results.append(article)

print(f"\n{'='*80}")
print(f"총 {len(unique_results)}개 기사 발견 (중복 제거)")
print(f"{'='*80}")

print("\n💡 제안:")
print("  이 기사들 중에 '엘리시전'과 유사한 이름이 있는지 확인해보세요.")
print("  예: 엘리사젠, 엘리젠, 엘리시스 등")
