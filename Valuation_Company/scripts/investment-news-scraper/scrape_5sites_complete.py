#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5개 언론사 완전 수집 (메인 페이지 크롤링)
- WOWTALE, 벤처스퀘어, 아웃스탠딩, 플래텀, 스타트업투데이
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

# 5개 언론사 설정
SITES = [
    {
        'number': 1,
        'name': 'WOWTALE',
        'url': 'https://wowtale.net',
        'main_url': 'https://wowtale.net',
        'url_pattern': '/2026/01/'
    },
    {
        'number': 9,
        'name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net',
        'main_url': 'https://www.venturesquare.net',
        'url_pattern': 'venturesquare.net'
    },
    {
        'number': 13,
        'name': '아웃스탠딩',
        'url': 'https://outstanding.kr',
        'main_url': 'https://outstanding.kr',
        'url_pattern': 'outstanding.kr'
    },
    {
        'number': 10,
        'name': '플래텀',
        'url': 'https://platum.kr',
        'main_url': 'https://platum.kr',
        'url_pattern': 'platum.kr'
    },
    {
        'number': 11,
        'name': '스타트업투데이',
        'url': 'https://www.startuptoday.kr',
        'main_url': 'https://www.startuptoday.kr/news/articleList.html',
        'url_pattern': 'startuptoday.kr'
    }
]


def get_recent_urls(site):
    """메인 페이지에서 최신 URL 수집"""

    try:
        response = requests.get(site['main_url'], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a', href=True)

        recent_urls = set()
        for link in links:
            href = link.get('href', '')

            # 절대 URL로 변환
            if href.startswith('/'):
                href = site['url'] + href
            elif not href.startswith('http'):
                href = site['url'] + '/' + href

            # 사이트 URL 패턴 확인
            if site['url_pattern'] in href:
                # WOWTALE은 2026년 1월만
                if site['name'] == 'WOWTALE':
                    if '/2026/01/' in href:
                        recent_urls.add(href)
                else:
                    recent_urls.add(href)

        return list(recent_urls)[:50]  # 최대 50개

    except Exception as e:
        return []


def crawl_article(url, site):
    """기사 내용 크롤링"""

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 제목 추출
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.get_text(strip=True) if title_elem else ""

        # 제목이 너무 짧으면 제외
        if len(title) < 10:
            return None

        # 공지사항 제외
        if '[공지]' in title or '공지' in title[:10]:
            return None

        # 투자 키워드 확인
        if not any(kw in title for kw in INVESTMENT_KEYWORDS):
            return None

        # 날짜 추출
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            published_date = f"{year}-{month}-{day}"
        else:
            published_date = datetime.now().strftime('%Y-%m-%d')

        return {
            'site_number': site['number'],
            'site_name': site['name'],
            'site_url': site['url'],
            'article_title': title,
            'article_url': url,
            'published_date': published_date
        }

    except Exception as e:
        return None


def scrape_site(site):
    """사이트별 수집"""

    print(f"\n{'='*60}")
    print(f"📰 {site['name']} 수집 중...")
    print(f"{'='*60}")

    # URL 수집
    urls = get_recent_urls(site)
    print(f"  → {len(urls)}개 URL 발견")

    if not urls:
        print(f"  ❌ URL 수집 실패")
        return 0, 0, 0

    saved = 0
    duplicate = 0
    skip = 0

    for idx, url in enumerate(urls, 1):
        article = crawl_article(url, site)

        if not article:
            skip += 1
            continue

        # 중복 확인
        existing = supabase.table("investment_news_articles")\
            .select("id")\
            .eq("article_url", article['article_url'])\
            .execute()

        if existing.data:
            duplicate += 1
        else:
            # DB 저장
            try:
                supabase.table("investment_news_articles").insert(article).execute()
                print(f"  [{idx}/{len(urls)}] ✅ {article['article_title'][:50]}...")
                saved += 1
            except:
                pass

        time.sleep(0.1)

    print(f"\n  결과: ✅ {saved}개 저장, ⚠️ {duplicate}개 중복, ❌ {skip}개 제외")

    return saved, duplicate, skip


def main():
    print("=" * 60)
    print("5개 언론사 완전 수집")
    print("=" * 60)

    total_saved = 0
    total_duplicate = 0
    total_skip = 0

    for site in SITES:
        saved, duplicate, skip = scrape_site(site)
        total_saved += saved
        total_duplicate += duplicate
        total_skip += skip

    print(f"\n{'='*60}")
    print("전체 수집 완료")
    print(f"{'='*60}")
    print(f"✅ 총 저장: {total_saved}개")
    print(f"⚠️ 총 중복: {total_duplicate}개")
    print(f"❌ 총 제외: {total_skip}개")
    print(f"{'='*60}")

    # 최종 레코드 수 확인
    result = supabase.table("investment_news_articles")\
        .select("id", count="exact")\
        .execute()

    print(f"\n📊 investment_news_articles 테이블: {result.count}개 레코드")


if __name__ == '__main__':
    main()
