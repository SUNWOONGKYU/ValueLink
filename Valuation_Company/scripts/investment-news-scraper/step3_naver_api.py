#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 3: 네이버 API로 투자 뉴스 수집
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
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            items = response.json().get('items', [])

            # 투자 관련 키워드 필터링
            investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']

            for item in items:
                title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                link = item.get('originallink') or item.get('link')
                pub_date = item.get('pubDate', '')

                # 기업명 확인
                if company_name not in title:
                    continue

                # 투자 키워드 확인
                if not any(kw in title for kw in investment_keywords):
                    continue

                # 날짜 파싱: "Tue, 27 Jan 2026 14:30:00 +0900" → "2026-01-27"
                try:
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                    published_date = dt.strftime('%Y-%m-%d')
                except:
                    published_date = datetime.now().strftime('%Y-%m-%d')

                # 사이트명 추출
                site_name = "네이버 뉴스"
                if 'venturesquare.net' in link:
                    site_name = "벤처스퀘어"
                    site_number = 9
                elif 'wowtale.net' in link:
                    site_name = "WOWTALE"
                    site_number = 1
                elif 'platum.kr' in link:
                    site_name = "플래텀"
                    site_number = 10
                elif 'outstanding.kr' in link:
                    site_name = "아웃스탠딩"
                    site_number = 13
                elif 'startuptoday.kr' in link:
                    site_name = "스타트업투데이"
                    site_number = 11
                elif 'thebell.co.kr' in link:
                    site_name = "더벨"
                    site_number = 16
                else:
                    site_number = 99

                return {
                    'site_number': site_number,
                    'site_name': site_name,
                    'site_url': "",
                    'article_title': title,
                    'article_url': link,
                    'published_date': published_date
                }

            return None

        else:
            return None

    except Exception as e:
        return None


def main():
    print("=" * 60)
    print("STEP 3: 네이버 API로 투자 뉴스 수집")
    print("=" * 60)

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    # CSV 읽기
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업")

    # 이미 수집된 기업 확인
    result = supabase.table("investment_news_articles")\
        .select("article_title")\
        .execute()

    collected_companies = set()
    for article in result.data:
        for row in companies:
            if row['기업명'] in article['article_title']:
                collected_companies.add(row['기업명'])

    # 미수집 기업만 필터링
    todo_companies = [c for c in companies if c['기업명'] not in collected_companies]

    print(f"이미 수집: {len(collected_companies)}개")
    print(f"검색 대상: {len(todo_companies)}개\n")

    found_count = 0
    not_found = []

    for idx, row in enumerate(todo_companies, 1):
        company_name = row['기업명']
        stage = row['단계']

        print(f"[{idx}/{len(todo_companies)}] {company_name}...", end=' ')

        # 네이버 뉴스 검색
        article = search_naver_news(company_name, stage)

        if article and article['article_url']:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if not existing.data:
                # DB 저장
                try:
                    supabase.table("investment_news_articles").insert(article).execute()
                    print(f"✅ [{article['site_name']}]")
                    found_count += 1

                except Exception as e:
                    print(f"❌ DB 저장 실패")
            else:
                print(f"⚠️ 중복")
        else:
            print("❌ 못 찾음")
            not_found.append(company_name)

        time.sleep(0.1)  # API 호출 간격

    print(f"\n{'='*60}")
    print("STEP 3 완료")
    print(f"{'='*60}")
    print(f"✅ 발견: {found_count}개")
    print(f"❌ 미발견: {len(not_found)}개")
    print(f"{'='*60}")

    # 최종 통계
    result = supabase.table("investment_news_articles")\
        .select("id", count="exact")\
        .execute()

    print(f"\n📊 투자 뉴스 테이블 총 레코드: {result.count}개")

    # 미발견 목록 저장
    if not_found:
        with open('final_not_found.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")

        print(f"\n⚠️ 최종 미발견 목록 저장: final_not_found.txt")
        print(f"   총 {len(not_found)}개 기업")


if __name__ == '__main__':
    main()
