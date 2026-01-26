#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
날짜별 뉴스 수집 (1월 1일 ~ 오늘)
- Naver 뉴스 검색 API 사용
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import requests
from datetime import datetime, timedelta
import time

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

# 투자 관련 검색 키워드
SEARCH_KEYWORDS = [
    '스타트업 투자 유치',
    '시리즈A 투자',
    '시리즈B 투자',
    '벤처투자',
    '스타트업 펀딩',
]

# 제외 키워드
EXCLUDED_KEYWORDS = [
    'IR', 'M&A', '인수', '합병', '상장', 'IPO', '행사', '세미나',
    '채용', '인사', '임원', '대표이사'
]


def search_naver_news_by_date(keyword, target_date):
    """
    Naver 뉴스 검색 API - 특정 날짜

    Args:
        keyword: 검색 키워드
        target_date: 검색 날짜 (datetime.date)

    Returns:
        기사 리스트
    """

    # 날짜 범위 (해당 날짜 00:00 ~ 23:59)
    date_str = target_date.strftime('%Y.%m.%d')

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    params = {
        'query': f'{keyword} {date_str}',
        'display': 100,  # 최대 100개
        'sort': 'date'
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        else:
            print(f"  [ERROR] Naver API HTTP {response.status_code}")
            return []

    except Exception as e:
        print(f"  [ERROR] {str(e)[:100]}")
        return []


def collect_by_date(start_date, end_date):
    """
    날짜 범위로 수집

    Args:
        start_date: 시작일 (datetime.date)
        end_date: 종료일 (datetime.date)
    """

    print("="*60)
    print("Date-by-Date News Collection")
    print("="*60)
    print(f"Period: {start_date} ~ {end_date}")
    print()

    current_date = start_date
    total_collected = 0
    total_saved = 0

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"\n{'='*60}")
        print(f"Date: {date_str}")
        print(f"{'='*60}")

        day_articles = []

        # 각 키워드로 검색
        for keyword in SEARCH_KEYWORDS:
            print(f"\n[{keyword}]")
            items = search_naver_news_by_date(keyword, current_date)

            print(f"  Found {len(items)} results")

            for item in items:
                title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                link = item.get('link', '')
                pub_date = item.get('pubDate', '')
                description = item.get('description', '').replace('<b>', '').replace('</b>', '')

                # 제외 키워드 체크
                has_excluded = any(kw in title for kw in EXCLUDED_KEYWORDS)

                if not has_excluded and link:
                    article = {
                        'site_number': 99,  # Naver 뉴스
                        'site_name': 'Naver 뉴스',
                        'site_url': 'https://news.naver.com',
                        'article_title': title,
                        'article_url': link,
                        'published_date': pub_date,
                        'content_snippet': description[:500]
                    }

                    day_articles.append(article)

            # Rate limiting
            time.sleep(0.1)

        # 중복 제거 (URL 기준)
        seen_urls = set()
        unique_articles = []
        for article in day_articles:
            if article['article_url'] not in seen_urls:
                seen_urls.add(article['article_url'])
                unique_articles.append(article)

        print(f"\n[RESULT] {date_str}: {len(unique_articles)} unique articles")

        # 데이터베이스 저장
        saved = 0
        duplicated = 0

        for article in unique_articles:
            try:
                # 중복 체크
                existing = supabase.table('investment_news_articles').select('id').eq('article_url', article['article_url']).execute()

                if existing.data:
                    duplicated += 1
                    continue

                # 저장
                supabase.table('investment_news_articles').insert(article).execute()
                saved += 1

            except Exception as e:
                print(f"  [ERROR] Failed to save: {str(e)[:200]}")

        print(f"  Saved: {saved}, Duplicated: {duplicated}")

        total_collected += len(unique_articles)
        total_saved += saved

        # 다음 날로
        current_date += timedelta(days=1)

        # Rate limiting
        time.sleep(1)

    print(f"\n{'='*60}")
    print("Final Summary")
    print(f"{'='*60}")
    print(f"Total collected: {total_collected}")
    print(f"Total saved: {total_saved}")
    print(f"{'='*60}")


def main():
    """메인 실행"""

    # 1월 1일부터 오늘까지
    start_date = datetime(2026, 1, 1).date()
    end_date = datetime.now().date()

    collect_by_date(start_date, end_date)


if __name__ == '__main__':
    main()
