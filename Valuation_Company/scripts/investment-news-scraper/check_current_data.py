#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 데이터베이스 상태 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def check_current_data():
    """현재 데이터 확인"""

    print("="*60)
    print("Current Database Status")
    print("="*60)

    # 전체 기사 수
    result = supabase.table('investment_news_articles').select('id', count='exact').execute()
    total_count = result.count if hasattr(result, 'count') else len(result.data)

    print(f"\n[TOTAL] {total_count} articles")

    # 소스별 통계
    sources_result = supabase.table('investment_news_articles').select('site_number, site_name').execute()

    source_counts = {}
    for article in sources_result.data:
        site_num = article['site_number']
        site_name = article['site_name']

        if site_num not in source_counts:
            source_counts[site_num] = {'name': site_name, 'count': 0}
        source_counts[site_num]['count'] += 1

    print(f"\n[By Source]")
    for site_num in sorted(source_counts.keys()):
        info = source_counts[site_num]
        print(f"  {site_num:3d}. {info['name']:20s}: {info['count']:3d} articles")

    # Google News URL 샘플 확인
    print(f"\n{'='*60}")
    print("Google News URL Samples (first 5)")
    print(f"{'='*60}")

    google_articles = supabase.table('investment_news_articles').select('article_title, article_url').eq('site_number', 100).limit(5).execute()

    for idx, article in enumerate(google_articles.data, 1):
        title = article['article_title'][:50]
        url = article['article_url'][:80]
        print(f"\n{idx}. {title}...")
        print(f"   URL: {url}...")

if __name__ == '__main__':
    check_current_data()
