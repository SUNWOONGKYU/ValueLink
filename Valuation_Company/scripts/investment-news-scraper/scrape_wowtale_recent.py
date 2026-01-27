#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WOWTALE 최신 뉴스 수집 (2026년 1월)
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import time
import re

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

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

INVESTMENT_KEYWORDS = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'VC']


def get_wowtale_recent_urls():
    """WOWTALE 메인 페이지에서 2026년 1월 URL 수집"""

    url = 'https://wowtale.net'

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a', href=True)

        recent_urls = set()
        for link in links:
            href = link.get('href', '')
            if '/2026/01/' in href and 'wowtale.net' in href:
                recent_urls.add(href)

        return list(recent_urls)

    except Exception as e:
        print(f"메인 페이지 오류: {str(e)[:50]}")
        return []


def crawl_article(url):
    """기사 내용 크롤링"""

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 제목 추출
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.get_text(strip=True) if title_elem else ""

        # 공지사항 제외
        if '[공지]' in title or '공지' in title[:10]:
            return None

        # 투자 키워드 확인
        if not any(kw in title for kw in INVESTMENT_KEYWORDS):
            return None

        # 날짜 추출 (URL에서)
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            published_date = f"{year}-{month}-{day}"
        else:
            published_date = datetime.now().strftime('%Y-%m-%d')

        return {
            'site_number': 1,
            'site_name': 'WOWTALE',
            'site_url': 'https://wowtale.net',
            'article_title': title,
            'article_url': url,
            'published_date': published_date
        }

    except Exception as e:
        return None


def main():
    print("=" * 60)
    print("WOWTALE 최신 뉴스 수집 (2026년 1월)")
    print("=" * 60)

    # 2026년 1월 URL 수집
    print("\n[1/2] 2026년 1월 URL 수집 중...")
    urls = get_wowtale_recent_urls()
    print(f"  → {len(urls)}개 URL 발견")

    # 각 URL 크롤링
    print("\n[2/2] 기사 크롤링 중...")

    saved_count = 0
    duplicate_count = 0
    skip_count = 0

    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] {url[:50]}...", end=' ')

        article = crawl_article(url)

        if not article:
            print("❌ 공지사항 or 투자뉴스 아님")
            skip_count += 1
            continue

        # 중복 확인
        existing = supabase.table("investment_news_articles")\
            .select("id")\
            .eq("article_url", article['article_url'])\
            .execute()

        if existing.data:
            print("⚠️ 중복")
            duplicate_count += 1
        else:
            # DB 저장
            try:
                supabase.table("investment_news_articles").insert(article).execute()
                print(f"✅ {article['article_title'][:40]}...")
                saved_count += 1
            except Exception as e:
                print(f"❌ DB 오류")

        time.sleep(0.2)

    print(f"\n{'='*60}")
    print("WOWTALE 수집 완료")
    print(f"{'='*60}")
    print(f"✅ 저장: {saved_count}개")
    print(f"⚠️ 중복: {duplicate_count}개")
    print(f"❌ 제외: {skip_count}개")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
