#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엘리시전 변형 검색 (매우 공격적)
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
print("엘리시전 변형 검색 (매우 공격적)")
print("=" * 80)

# 엘리시전 정보
company_info = {
    'name': '엘리시전',
    'variants': [
        # 한글 변형
        '엘리시전', '엘리션', '엘리시젼', '엘리젼',
        # 영문 변형
        'Ellision', 'ellision', 'ELLISION',
        'Elision', 'elision', 'ELISION',
        'Ellisien', 'Elisien',
        # 조합
        '엘리시전 유전자', '엘리시전 치료제',
    ],
    'investors': [
        '데일리파트너스',
        'NH투자증권',
        '데일리파트너스-NH투자증권',
    ],
    'keywords': [
        '유전자 치료제',
        '유전자치료제',
        '시리즈C',
        '50억',
    ]
}

print(f"\n🔍 검색 변형: {len(company_info['variants'])}개")
for v in company_info['variants']:
    print(f"  - {v}")

def search_naver(query):
    """네이버 API 검색"""
    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    params = {
        'query': query,
        'display': 100,
        'sort': 'date'
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            items = response.json().get('items', [])
            return items
    except:
        pass

    return []

# 검색 실행
print("\n" + "=" * 80)
print("검색 시작")
print("=" * 80)

all_queries = []

# 변형 + 투자자
for variant in company_info['variants']:
    for investor in company_info['investors']:
        all_queries.append(f"{variant} {investor}")
        all_queries.append(f"{variant} {investor} 투자")

# 변형 + 키워드
for variant in company_info['variants']:
    for keyword in company_info['keywords']:
        all_queries.append(f"{variant} {keyword}")

# 변형 단독
for variant in company_info['variants']:
    all_queries.append(f"{variant} 투자유치")
    all_queries.append(f"{variant} 투자")
    all_queries.append(variant)

print(f"\n📊 총 {len(all_queries)}개 쿼리 검색")

found_articles = []

for idx, query in enumerate(all_queries, 1):
    if idx % 10 == 0:
        print(f"  진행: {idx}/{len(all_queries)}")

    items = search_naver(query)

    for item in items:
        title = item.get('title', '').replace('<b>', '').replace('</b>', '')
        link = item.get('originallink') or item.get('link')

        # 변형 중 하나라도 포함
        found = False
        for variant in company_info['variants']:
            if variant.lower() in title.lower():
                found = True
                break

        if not found:
            continue

        # 투자 키워드
        investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'VC', '치료제']
        if not any(kw in title for kw in investment_keywords):
            continue

        found_articles.append({
            'title': title,
            'url': link,
            'query': query
        })

    time.sleep(0.05)

# 중복 제거
unique_articles = []
seen_urls = set()

for article in found_articles:
    if article['url'] not in seen_urls:
        seen_urls.add(article['url'])
        unique_articles.append(article)

print(f"\n" + "=" * 80)
print(f"검색 결과: {len(unique_articles)}개 기사 발견")
print("=" * 80)

if unique_articles:
    for idx, article in enumerate(unique_articles[:10], 1):
        print(f"\n[{idx}] {article['title']}")
        print(f"  URL: {article['url']}")
        print(f"  검색어: {article['query']}")

    # 가장 관련성 높은 기사 선택
    print("\n" + "=" * 80)
    print("가장 관련성 높은 기사 저장")
    print("=" * 80)

    best_article = unique_articles[0]
    pub_date = datetime.now().strftime('%Y-%m-%d')

    # 사이트명 추출
    site_mapping = {
        'wowtale.net': ('WOWTALE', 1),
        'venturesquare.net': ('벤처스퀘어', 9),
        'thebell.co.kr': ('더벨', 16),
        'platum.kr': ('플래텀', 10),
        'startuptoday.kr': ('스타트업투데이', 11),
    }

    site_name = "네이버 뉴스"
    site_number = 99

    for domain, (name, num) in site_mapping.items():
        if domain in best_article['url']:
            site_name = name
            site_number = num
            break

    article_data = {
        'site_number': site_number,
        'site_name': site_name,
        'site_url': '',
        'article_title': best_article['title'],
        'article_url': best_article['url'],
        'published_date': pub_date
    }

    # 중복 확인
    existing = supabase.table("investment_news_articles")\
        .select("id")\
        .eq("article_url", article_data['article_url'])\
        .execute()

    if not existing.data:
        try:
            supabase.table("investment_news_articles").insert(article_data).execute()
            print(f"✅ DB 저장 완료")
            print(f"  제목: {best_article['title']}")
            print(f"  사이트: {site_name}")
        except Exception as e:
            print(f"❌ DB 오류: {e}")
    else:
        print(f"⚠️  중복 (이미 있음)")

else:
    print("\n❌ 기사를 찾지 못했습니다.")
    print("\n💡 제안:")
    print("  1. 회사명이 다를 수 있습니다 (영문명 확인 필요)")
    print("  2. 비공개 투자일 수 있습니다")
    print("  3. 최근 투자가 아닐 수 있습니다")
