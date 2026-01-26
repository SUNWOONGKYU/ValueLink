#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News RSS로 대량 수집
- 날짜 범위 지정 가능
- 검색 키워드별 100개씩
"""

import feedparser
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
import time
from urllib.parse import quote

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# 투자 관련 검색 키워드 (더 많이)
SEARCH_KEYWORDS = [
    '스타트업 투자',
    '벤처투자',
    '시리즈A',
    'Series A',
    '시리즈B',
    'Series B',
    '시드투자',
    '프리A',
    '스타트업 펀딩',
    '벤처캐피탈',
    '투자유치',
    '스케일업 투자',
    '테크 스타트업 투자',
    'AI 스타트업 투자',
]

# 제외 키워드
EXCLUDED_KEYWORDS = [
    'IR', 'M&A', '인수', '합병', '상장', 'IPO', '행사', '세미나',
    '채용', '인사', '임원', '대표이사', 'MOU', '협약'
]


def collect_google_news(keyword, start_date, end_date):
    """
    Google News RSS로 수집

    Args:
        keyword: 검색 키워드
        start_date: 시작일
        end_date: 종료일

    Returns:
        기사 리스트
    """

    articles = []

    # Google News RSS URL
    # when:7d = 최근 7일
    # when:1m = 최근 1개월
    base_url = "https://news.google.com/rss/search"

    # 한국어로 검색 + 날짜 범위
    query = f'{keyword} after:{start_date} before:{end_date}'
    encoded_query = quote(query)

    url = f"{base_url}?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

    try:
        print(f"  [{keyword}] Fetching Google News RSS...")
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"    No results")
            return []

        print(f"    Found {len(feed.entries)} entries")

        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')
            pub_date = entry.get('published', '')
            summary = entry.get('summary', '')

            # 제외 키워드 체크
            has_excluded = any(kw in title for kw in EXCLUDED_KEYWORDS)

            if not has_excluded and link:
                article = {
                    'site_number': 100,  # Google News
                    'site_name': 'Google News',
                    'site_url': 'https://news.google.com',
                    'article_title': title,
                    'article_url': link,
                    'published_date': pub_date,
                    'content_snippet': summary[:500] if summary else None
                }

                articles.append(article)

    except Exception as e:
        print(f"    [ERROR] {str(e)[:100]}")

    return articles


def collect_all_google_news(start_date_str, end_date_str):
    """전체 Google News 수집"""

    print("="*60)
    print("Google News Collection")
    print("="*60)
    print(f"Period: {start_date_str} ~ {end_date_str}")
    print(f"Keywords: {len(SEARCH_KEYWORDS)}")
    print()

    all_articles = []

    for keyword in SEARCH_KEYWORDS:
        articles = collect_google_news(keyword, start_date_str, end_date_str)
        all_articles.extend(articles)

        # Rate limiting
        time.sleep(1)

    # 중복 제거 (URL 기준)
    seen_urls = set()
    unique_articles = []

    for article in all_articles:
        if article['article_url'] not in seen_urls:
            seen_urls.add(article['article_url'])
            unique_articles.append(article)

    print(f"\n{'='*60}")
    print(f"Total collected: {len(all_articles)}")
    print(f"Unique: {len(unique_articles)}")
    print(f"{'='*60}")

    return unique_articles


def save_to_database(articles):
    """데이터베이스 저장"""

    print(f"\n[DATABASE] Saving {len(articles)} articles...")

    saved = 0
    duplicated = 0
    failed = 0

    for article in articles:
        try:
            # 중복 체크
            existing = supabase.table('investment_news_articles').select('id').eq('article_url', article['article_url']).execute()

            if existing.data:
                duplicated += 1
                continue

            # 저장
            supabase.table('investment_news_articles').insert(article).execute()
            saved += 1

            if saved % 10 == 0:
                print(f"  Saved {saved}...")

        except Exception as e:
            failed += 1
            if failed <= 5:  # 처음 5개 에러만 출력
                print(f"  [ERROR] {str(e)[:200]}")

    print(f"\n[RESULT] Saved: {saved}, Duplicated: {duplicated}, Failed: {failed}")
    return saved, duplicated, failed


def main():
    """메인 실행"""

    # 1월 1일부터 오늘까지
    start_date = "2026-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    # Google News 수집
    articles = collect_all_google_news(start_date, end_date)

    # 데이터베이스 저장
    if articles:
        save_to_database(articles)
    else:
        print("\n[WARN] No articles collected")


if __name__ == '__main__':
    main()
