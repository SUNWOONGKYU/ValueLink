#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
126개 기업 완전 수집 (기업명 + 투자자 + 단계 활용)
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


def search_with_multiple_queries(company_name, investors, stage):
    """여러 조합으로 검색"""

    # 투자자 첫 단어 추출
    first_investor = ""
    if investors and investors != '-':
        first_investor = investors.split()[0].split('-')[0].split(',')[0]

    # 검색 쿼리 조합 (우선순위대로)
    queries = [
        f"{company_name} {first_investor} 투자",  # 기업명 + 투자자
        f"{company_name} {stage} 투자",  # 기업명 + 단계
        f"{company_name} 투자유치",  # 기업명만
        f"{company_name} 펀딩",
    ]

    for query in queries:
        url = "https://openapi.naver.com/v1/search/news.json"

        headers = {
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        }

        params = {
            'query': query,
            'display': 30,
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

                    # 투자 키워드
                    investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
                    if not any(kw in title for kw in investment_keywords):
                        continue

                    # 날짜 파싱
                    try:
                        dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                        published_date = dt.strftime('%Y-%m-%d')
                    except:
                        published_date = datetime.now().strftime('%Y-%m-%d')

                    # 사이트명
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
    print("126개 기업 완전 수집 (전체 정보 활용)")
    print("=" * 60)

    # 126개 기업 CSV 읽기
    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 126개 기업\n")

    # 이미 수집된 기업 확인
    result = supabase.table("investment_news_articles")\
        .select("article_title")\
        .execute()

    collected = set()
    for article in result.data:
        for row in companies:
            if row['기업명'] in article['article_title']:
                collected.add(row['기업명'])

    # 미수집 기업
    todo = [c for c in companies if c['기업명'] not in collected]

    print(f"이미 수집: {len(collected)}개")
    print(f"미수집: {len(todo)}개\n")

    found = 0
    not_found = []

    for idx, row in enumerate(todo, 1):
        company = row['기업명']
        investors = row['투자자']
        stage = row['단계']

        print(f"[{idx}/{len(todo)}] {company} ({investors[:20]}...)...", end=' ')

        # 여러 검색 쿼리로 시도
        article = search_with_multiple_queries(company, investors, stage)

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
    print("수집 완료")
    print(f"{'='*60}")
    print(f"✅ 이번에 발견: {found}개")
    print(f"❌ 못 찾음: {len(not_found)}개")
    print(f"{'='*60}")

    # 최종 통계
    result = supabase.table("investment_news_articles")\
        .select("article_title")\
        .execute()

    final_collected = set()
    for article in result.data:
        for row in companies:
            if row['기업명'] in article['article_title']:
                final_collected.add(row['기업명'])

    print(f"\n📊 126개 기업 최종 현황:")
    print(f"  ✅ 수집 완료: {len(final_collected)}개 ({len(final_collected)*100//126}%)")
    print(f"  ❌ 미수집: {126-len(final_collected)}개")

    if not_found:
        with open('final_126_not_found.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")
        print(f"\n⚠️ 못 찾은 기업: final_126_not_found.txt ({len(not_found)}개)")


if __name__ == '__main__':
    main()
