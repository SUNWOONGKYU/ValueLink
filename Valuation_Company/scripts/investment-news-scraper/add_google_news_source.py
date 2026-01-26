#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News 소스 추가
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def add_google_news_source():
    """Google News 소스 추가"""

    google_news_source = {
        'rank': 13,
        'category': 'News RSS',
        'source_number': 100,
        'source_name': 'Google News',
        'source_url': 'https://news.google.com',
        'collection_method': 'RSS',
        'rss_url': 'https://news.google.com/rss/search',
        'is_active': True,
        'expected_daily_count': 100
    }

    try:
        # 기존에 있는지 확인
        existing = supabase.table('investment_news_network_sources').select('id').eq('source_number', 100).execute()

        if existing.data:
            print("[INFO] Google News source already exists")
            return

        # 추가
        result = supabase.table('investment_news_network_sources').insert(google_news_source).execute()
        print("[SUCCESS] Google News source added")
        print(f"  ID: {result.data[0]['id']}")
        print(f"  Source Number: {result.data[0]['source_number']}")
        print(f"  Source Name: {result.data[0]['source_name']}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == '__main__':
    add_google_news_source()
