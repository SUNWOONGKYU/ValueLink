#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
미수집 기업 재수집 (제미나 정확한 기업명 사용)
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


def search_naver_news_broad(company_name):
    """네이버 API로 뉴스 검색 (넓은 검색어)"""

    # 단계 없이 기업명만으로 검색
    queries = [
        f"{company_name} 투자",
        f"{company_name} 투자유치",
        f"{company_name} 펀딩",
        f"{company_name} 시리즈"
    ]

    for query in queries:
        url = "https://openapi.naver.com/v1/search/news.json"

        headers = {
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        }

        params = {
            'query': query,
            'display': 20,  # 더 많이
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

                    # 기업명 확인 (정확히 포함되어야 함)
                    if company_name not in title:
                        continue

                    # 투자 관련 키워드
                    investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
                    if not any(kw in title for kw in investment_keywords):
                        continue

                    # 날짜 파싱
                    try:
                        dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                        published_date = dt.strftime('%Y-%m-%d')
                    except:
                        published_date = datetime.now().strftime('%Y-%m-%d')

                    # 사이트명 추출
                    site_mapping = {
                        'venturesquare.net': ('벤처스퀘어', 9),
                        'wowtale.net': ('WOWTALE', 1),
                        'platum.kr': ('플래텀', 10),
                        'outstanding.kr': ('아웃스탠딩', 13),
                        'startuptoday.kr': ('스타트업투데이', 11),
                        'thebell.co.kr': ('더벨', 16),
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
                        'site_url': "",
                        'article_title': title,
                        'article_url': link,
                        'published_date': published_date
                    }

            time.sleep(0.1)

        except Exception as e:
            continue

    return None


def main():
    print("=" * 60)
    print("미수집 기업 재수집 (제미나 정확한 이름)")
    print("=" * 60)

    # 제미나 92개 기업 (정확한 이름)
    with open('final_found_urls.csv', 'r', encoding='utf-8') as f:
        gemini_companies = {r['기업명']: r for r in csv.DictReader(f)}

    print(f"\n제미나 기업: {len(gemini_companies)}개")

    # 이미 수집된 기업 확인
    result = supabase.table("investment_news_articles")\
        .select("article_title")\
        .execute()

    collected = set()
    for article in result.data:
        for company in gemini_companies.keys():
            if company in article['article_title']:
                collected.add(company)

    # 미수집 기업
    todo = [c for c in gemini_companies.keys() if c not in collected]

    print(f"이미 수집: {len(collected)}개")
    print(f"미수집: {len(todo)}개\n")

    found = 0
    not_found = []

    for idx, company in enumerate(todo, 1):
        print(f"[{idx}/{len(todo)}] {company}...", end=' ')

        # 네이버 검색 (넓은 검색어)
        article = search_naver_news_broad(company)

        if article and article['article_url']:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if not existing.data:
                try:
                    supabase.table("investment_news_articles").insert(article).execute()
                    print(f"✅ [{article['site_name']}]")
                    found += 1
                except:
                    print(f"❌ DB 오류")
            else:
                print(f"⚠️ 중복")
        else:
            print("❌ 못 찾음")
            not_found.append(company)

        time.sleep(0.15)

    print(f"\n{'='*60}")
    print("재수집 완료")
    print(f"{'='*60}")
    print(f"✅ 발견: {found}개")
    print(f"❌ 미발견: {len(not_found)}개")
    print(f"{'='*60}")

    # 최종 통계
    result = supabase.table("investment_news_articles")\
        .select("article_title")\
        .execute()

    final_collected = set()
    for article in result.data:
        for company in gemini_companies.keys():
            if company in article['article_title']:
                final_collected.add(company)

    print(f"\n📊 제미나 92개 기업 중:")
    print(f"  ✅ 수집 완료: {len(final_collected)}개 ({len(final_collected)*100//92}%)")
    print(f"  ❌ 미수집: {92-len(final_collected)}개")

    if not_found:
        with open('still_not_found.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")
        print(f"\n⚠️ 여전히 못 찾은 기업: still_not_found.txt")


if __name__ == '__main__':
    main()
