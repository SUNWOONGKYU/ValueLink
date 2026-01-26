#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini가 수집한 투자 뉴스 데이터를 Supabase에 업로드
"""

import json
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드 (상위 폴더의 .env 파일)
env_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'investment-news-scraper', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] .env file not found or missing SUPABASE_URL/SUPABASE_KEY")
    print(f"Looking for .env at: {env_path}")
    exit(1)

def upload_articles():
    """JSON 파일의 기사들을 Supabase에 업로드"""

    # JSON 파일 읽기
    with open('investment_news_data.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)

    print(f"[INFO] Total {len(articles)} articles to upload...")
    print("-" * 60)

    success_count = 0
    duplicate_count = 0
    error_count = 0

    for idx, article in enumerate(articles, 1):
        try:
            # Supabase REST API로 저장
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/investment_news_articles",
                headers={
                    'apikey': SUPABASE_KEY,
                    'Authorization': f'Bearer {SUPABASE_KEY}',
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                json=article
            )

            if response.status_code == 201:
                success_count += 1
                print(f"[OK] [{idx}/{len(articles)}] {article['site_name']}: {article.get('article_title', 'NO TITLE')[:50]}...")
            elif response.status_code == 409:
                duplicate_count += 1
                print(f"[DUP] [{idx}/{len(articles)}] Duplicate: {article.get('article_title', 'NO TITLE')[:50]}...")
            else:
                error_count += 1
                print(f"[ERR] [{idx}/{len(articles)}] Failed ({response.status_code}): {article.get('article_title', 'NO TITLE')[:50]}...")

        except Exception as e:
            error_count += 1
            print(f"[ERR] [{idx}/{len(articles)}] Error: {str(e)[:50]}...")

    print("-" * 60)
    print(f"\n[RESULT] Upload Summary:")
    print(f"  Success: {success_count}")
    print(f"  Duplicate: {duplicate_count}")
    print(f"  Failed: {error_count}")
    print(f"  Total: {len(articles)}")

if __name__ == '__main__':
    upload_articles()
