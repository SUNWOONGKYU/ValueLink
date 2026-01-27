#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 API로 126개 기업 투자 뉴스 수집
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


def search_naver_news(company_name, stage):
    """네이버 API로 뉴스 검색"""

    query = f"{company_name} {stage} 투자 유치"
    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    params = {
        'query': query,
        'display': 10,  # 최대 10개
        'sort': 'date'  # 최신순
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            return []
    except Exception as e:
        return []


def main():
    print("=" * 70)
    print("네이버 API로 투자 뉴스 수집")
    print("=" * 70)

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업 검색 예정\n")

    total_found = 0
    total_saved = 0

    for idx, row in enumerate(companies, 1):
        company_name = row['기업명']
        stage = row['단계']

        print(f"[{idx}/{len(companies)}] {company_name}...", end=' ')

        # 네이버 뉴스 검색
        articles = search_naver_news(company_name, stage)

        if articles:
            print(f"✅ {len(articles)}건 발견", end=' ')

            saved_count = 0
            for article in articles:
                title = article.get('title', '').replace('<b>', '').replace('</b>', '')
                link = article.get('originallink') or article.get('link')
                pub_date = article.get('pubDate', '')

                # pubDate 형식: "Tue, 27 Jan 2026 14:30:00 +0900"
                # → "2026-01-27" 형식으로 변환
                try:
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                    published_date = dt.strftime('%Y-%m-%d')
                except:
                    published_date = None

                # 중복 확인
                existing = supabase.table("investment_news_articles")\
                    .select("id")\
                    .eq("article_url", link)\
                    .execute()

                if not existing.data:
                    # DB 저장
                    try:
                        supabase.table("investment_news_articles").insert({
                            "article_title": title,
                            "article_url": link,
                            "site_name": "Naver News",
                            "published_date": published_date,
                            "company_name": company_name
                        }).execute()
                        saved_count += 1
                    except:
                        pass

            print(f"→ {saved_count}건 저장")
            total_found += len(articles)
            total_saved += saved_count

        else:
            print(f"⚠️ 못 찾음")

        time.sleep(0.1)  # API 호출 간격

    print("\n" + "=" * 70)
    print("네이버 뉴스 수집 완료")
    print("=" * 70)
    print(f"✅ 발견: {total_found}건")
    print(f"✅ 저장: {total_saved}건")
    print("=" * 70)


if __name__ == '__main__':
    main()
