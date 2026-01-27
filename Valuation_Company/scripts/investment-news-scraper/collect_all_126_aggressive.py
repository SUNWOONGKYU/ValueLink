#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
126개 기업 전부 수집 (공격적 검색 - 기업명만)
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


def search_naver_aggressive(company_name):
    """네이버 API - 기업명만으로 검색 (투자 관련)"""

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    # 기업명만으로 검색
    params = {
        'query': company_name,
        'display': 50,  # 최대한 많이
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

                # 기업명 정확히 포함
                if company_name not in title:
                    continue

                # 투자 키워드
                investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'VC', '벤처캐피털']
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

        return None

    except Exception as e:
        return None


def main():
    print("=" * 60)
    print("126개 기업 전부 수집 (공격적 검색)")
    print("=" * 60)

    # CSV 읽기
    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업\n")

    found = 0
    duplicate = 0
    not_found = []

    for idx, row in enumerate(companies, 1):
        company = row['기업명']

        print(f"[{idx}/{len(companies)}] {company}...", end=' ')

        # 네이버 검색
        article = search_naver_aggressive(company)

        if article and article['article_url']:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if not existing.data:
                try:
                    supabase.table("investment_news_articles").insert(article).execute()
                    print(f"✅ [{article['site_name']}] {article['article_title'][:40]}...")
                    found += 1
                except:
                    print(f"❌ DB 오류")
            else:
                print(f"⚠️ 중복")
                duplicate += 1
        else:
            print("❌ 못 찾음")
            not_found.append(company)

        time.sleep(0.12)

    print(f"\n{'='*60}")
    print("수집 완료")
    print(f"{'='*60}")
    print(f"✅ 새로 발견: {found}개")
    print(f"⚠️ 중복: {duplicate}개")
    print(f"❌ 못 찾음: {len(not_found)}개")
    print(f"{'='*60}")

    # 최종 통계
    result = supabase.table("investment_news_articles").select("article_title").execute()

    final_collected = set()
    for article in result.data:
        for row in companies:
            if row['기업명'] in article['article_title']:
                final_collected.add(row['기업명'])

    print(f"\n📊 126개 기업 최종:")
    print(f"  ✅ 뉴스 있음: {len(final_collected)}개 ({len(final_collected)*100//126}%)")
    print(f"  ❌ 뉴스 없음: {126-len(final_collected)}개")

    if not_found:
        with open('final_not_found_126.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")


if __name__ == '__main__':
    main()
