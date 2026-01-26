#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS 피드 수집 (4개 사이트)
- 벤처스퀘어, 아웃스탠딩, 플래텀, 비석세스
"""

import feedparser
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
import time

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# RSS 소스 정보
RSS_SOURCES = [
    {
        'source_number': 9,
        'source_name': '벤처스퀘어',
        'source_url': 'https://www.venturesquare.net',
        'rss_url': 'https://www.venturesquare.net/feed'
    },
    {
        'source_number': 13,
        'source_name': '아웃스탠딩',
        'source_url': 'https://outstanding.kr',
        'rss_url': 'https://outstanding.kr/feed'
    },
    {
        'source_number': 10,
        'source_name': '플래텀',
        'source_url': 'https://platum.kr',
        'rss_url': 'https://platum.kr/feed'
    },
    {
        'source_number': 14,
        'source_name': '비석세스',
        'source_url': 'https://besuccess.com',
        'rss_url': 'https://besuccess.com/feed'
    }
]

# 투자 관련 키워드
INVESTMENT_KEYWORDS = [
    '투자', '유치', '시리즈', '펀딩', 'funding', 'investment',
    'Series A', 'Series B', 'Series C', 'Pre-A', '시드', 'Seed',
    '억원', 'M', '조달', 'raised', 'rounds'
]

# 제외 키워드
EXCLUDED_KEYWORDS = [
    'IR', 'M&A', '인수', '합병', '상장', 'IPO', '행사', '세미나',
    '채용', '인사', '임원', '대표이사', '엔젤리그', '실홀딩스'
]


def collect_from_rss(source):
    """
    RSS 피드에서 기사 수집

    Args:
        source: 소스 정보 딕셔너리

    Returns:
        수집된 기사 리스트
    """
    print(f"\n[{source['source_name']}] Collecting RSS feed...")

    try:
        # RSS 파싱
        feed = feedparser.parse(source['rss_url'])

        if not feed.entries:
            print(f"  [WARN] No entries found in RSS feed")
            return []

        print(f"  [INFO] Found {len(feed.entries)} entries")

        articles = []

        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')

            # URL 검증
            if not link:
                continue

            # 투자 키워드 필터링
            has_investment_keyword = any(kw.lower() in title.lower() for kw in INVESTMENT_KEYWORDS)

            # 제외 키워드 체크
            has_excluded_keyword = any(kw in title for kw in EXCLUDED_KEYWORDS)

            # 투자 키워드가 있고, 제외 키워드가 없으면 수집
            if has_investment_keyword and not has_excluded_keyword:
                # 발행일 파싱
                published_date = None
                if 'published' in entry:
                    try:
                        from dateutil import parser
                        published_date = parser.parse(entry.published).isoformat()
                    except:
                        published_date = entry.published

                # 요약/스니펫
                content_snippet = None
                if 'summary' in entry:
                    content_snippet = entry.summary[:500]  # 최대 500자
                elif 'description' in entry:
                    content_snippet = entry.description[:500]

                article = {
                    'site_number': source['source_number'],
                    'site_name': source['source_name'],
                    'site_url': source['source_url'],
                    'article_title': title,
                    'article_url': link,
                    'published_date': published_date,
                    'content_snippet': content_snippet
                }

                articles.append(article)

        print(f"  [SUCCESS] Collected {len(articles)} investment-related articles")
        return articles

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return []


def save_to_database(articles):
    """
    수집된 기사를 데이터베이스에 저장

    Args:
        articles: 기사 리스트

    Returns:
        저장 성공/실패 개수
    """
    print(f"\n[DATABASE] Saving {len(articles)} articles...")

    saved = 0
    duplicated = 0
    failed = 0

    for article in articles:
        try:
            # 중복 체크 (article_url 기준)
            existing = supabase.table('investment_news_articles').select('id').eq('article_url', article['article_url']).execute()

            if existing.data:
                duplicated += 1
                print(f"  [SKIP] Duplicate: {article['article_title'][:50]}...")
                continue

            # 저장
            supabase.table('investment_news_articles').insert(article).execute()
            saved += 1
            print(f"  [SAVED] {article['site_name']}: {article['article_title'][:50]}...")

        except Exception as e:
            failed += 1
            print(f"  [ERROR] Failed to save: {str(e)[:100]}")

    print(f"\n[RESULT] Saved: {saved}, Duplicated: {duplicated}, Failed: {failed}")

    return saved, duplicated, failed


def update_last_collected(source_number):
    """
    마지막 수집 시간 업데이트

    Args:
        source_number: 소스 번호
    """
    try:
        supabase.table('investment_news_network_sources').update({
            'last_collected_at': datetime.now().isoformat()
        }).eq('source_number', source_number).execute()
    except Exception as e:
        print(f"  [WARN] Failed to update last_collected_at: {e}")


def main():
    """메인 실행"""
    print("="*60)
    print("RSS Feed Collection")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_articles = []

    # 각 소스에서 수집
    for source in RSS_SOURCES:
        articles = collect_from_rss(source)
        all_articles.extend(articles)

        # 마지막 수집 시간 업데이트
        if articles:
            update_last_collected(source['source_number'])

        # Rate limiting (1초 대기)
        time.sleep(1)

    # 데이터베이스 저장
    if all_articles:
        saved, duplicated, failed = save_to_database(all_articles)
    else:
        print("\n[WARN] No articles collected")
        saved, duplicated, failed = 0, 0, 0

    # 결과 요약
    print("\n" + "="*60)
    print("Collection Summary")
    print("="*60)
    print(f"Total collected: {len(all_articles)}")
    print(f"Saved: {saved}")
    print(f"Duplicated: {duplicated}")
    print(f"Failed: {failed}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return len(all_articles), saved, duplicated, failed


if __name__ == '__main__':
    main()
