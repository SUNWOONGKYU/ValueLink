#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 미발견 5개 기업 재검색
"""

import os
import sys
import csv
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

GEMINI_CSV = 'sensible_companies_2026_01_GEMINI.csv'

# 미발견 5개 기업
missing_companies = [
    '뉴타입인더스트리즈',
    '덱사스튜디오',
    '디앤티테크솔루션',
    '엘리시전',
    '펩티르나테라퓨틱스'
]

print("=" * 80)
print("최종 미발견 5개 기업 재검색")
print("=" * 80)

# 1. Gemini CSV에서 투자자 정보 확인
company_info = {}
with open(GEMINI_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company_name = row['기업명']
        if company_name in missing_companies:
            company_info[company_name] = {
                '투자자': row.get('투자자', ''),
                '주요사업': row.get('주요사업', ''),
                '단계': row.get('단계', ''),
                '신규': row.get('신규', '')
            }

print("\n📋 미발견 5개 기업 정보:")
for company, info in company_info.items():
    print(f"\n{company}:")
    print(f"  투자자: {info['투자자']}")
    print(f"  주요사업: {info['주요사업']}")
    print(f"  단계: {info['단계']}")
    print(f"  신규: {info['신규']}")

# 2. 네이버 API로 검색
def search_naver(company_name, investor):
    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    # 검색 쿼리 여러 개 시도
    queries = [
        f"{company_name} {investor} 투자",
        f"{company_name} 투자유치",
        f"{company_name} 투자",
        company_name
    ]

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
                    pub_date = item.get('pubDate', '')

                    # 기업명 확인
                    if company_name not in title:
                        continue

                    # 투자 키워드 확인
                    investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
                    if any(kw in title for kw in investment_keywords):
                        # 날짜 파싱
                        try:
                            dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                            published_date = dt.strftime('%Y-%m-%d')
                        except:
                            published_date = datetime.now().strftime('%Y-%m-%d')

                        # 사이트명
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
                            if domain in link:
                                site_name = name
                                site_number = num
                                break

                        return {
                            'site_number': site_number,
                            'site_name': site_name,
                            'site_url': '',
                            'article_title': title,
                            'article_url': link,
                            'published_date': published_date
                        }, query

            time.sleep(0.1)

        except Exception as e:
            continue

    return None, None

# 3. 검색 실행
print("\n" + "=" * 80)
print("재검색 시작")
print("=" * 80)

found = 0
not_found = []

for idx, company in enumerate(missing_companies, 1):
    print(f"\n[{idx}/5] {company}")

    info = company_info.get(company, {})
    investor = info.get('투자자', '')

    article, query = search_naver(company, investor)

    if article:
        print(f"  ✅ 발견: {article['article_title'][:60]}...")
        print(f"  🔎 검색어: {query}")
        print(f"  📰 [{article['site_name']}]")

        # 중복 확인
        existing = supabase.table("investment_news_articles")\
            .select("id")\
            .eq("article_url", article['article_url'])\
            .execute()

        if not existing.data:
            try:
                supabase.table("investment_news_articles").insert(article).execute()
                print(f"  💾 DB 저장 완료")
                found += 1
            except Exception as e:
                print(f"  ❌ DB 오류: {e}")
        else:
            print(f"  ⚠️  중복")
            found += 1
    else:
        print(f"  ❌ 못 찾음")
        not_found.append(company)

    time.sleep(0.5)

print(f"\n{'='*80}")
print("재검색 완료")
print(f"{'='*80}")
print(f"✅ 발견: {found}개")
print(f"❌ 최종 미발견: {len(not_found)}개")

if not_found:
    print(f"\n❌ 최종 미발견 기업:")
    for company in not_found:
        print(f"  - {company}")

# 최종 통계
count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
print(f"\ninvestment_news_articles 테이블 총 레코드: {count_result.count}개")
