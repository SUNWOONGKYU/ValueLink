#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WOWTALE 깊이 탐색 - 검색 + 아카이브 + 카테고리
"""

import os
import sys
import csv
import requests
from bs4 import BeautifulSoup
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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def get_wowtale_archive_urls():
    """WOWTALE 최근 여러 달 아카이브 URL 수집"""

    # 2026년 1월, 2025년 12월, 11월, 10월 탐색
    months = [
        '2026/01/',
        '2025/12/',
        '2025/11/',
        '2025/10/',
    ]

    all_urls = set()

    for month in months:
        print(f"\n📅 {month} 탐색 중...")

        # 메인 페이지 탐색
        url = 'https://wowtale.net'
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if month in href and 'wowtale.net' in href:
                    all_urls.add(href)
                    print(f"  ✅ {href}")

        except Exception as e:
            print(f"  ❌ {month} 탐색 실패: {e}")

        time.sleep(1)

    # 카테고리 페이지 탐색 (투자, 스타트업 등)
    category_keywords = ['투자', '유치', '펀딩', '시리즈', '스타트업']

    print(f"\n📂 카테고리 페이지 탐색 중...")
    url = 'https://wowtale.net'
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()

            # 투자 관련 카테고리 링크
            if any(kw in text for kw in category_keywords):
                if 'wowtale.net' in href and '/202' in href:
                    all_urls.add(href)
                    print(f"  ✅ {href} ({text})")

    except Exception as e:
        print(f"  ❌ 카테고리 탐색 실패: {e}")

    return list(all_urls)


def extract_article_data(url):
    """WOWTALE 기사 데이터 추출"""

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 제목 추출
        title_tag = soup.find('h1', class_='entry-title')
        if not title_tag:
            title_tag = soup.find('h1')
        if not title_tag:
            title_tag = soup.find('title')

        title = title_tag.get_text().strip() if title_tag else ""

        # 투자 키워드 확인
        investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
        if not any(kw in title for kw in investment_keywords):
            return None

        # 날짜 추출
        date_tag = soup.find('time', class_='entry-date')
        if not date_tag:
            date_tag = soup.find('time')

        published_date = datetime.now().strftime('%Y-%m-%d')
        if date_tag:
            try:
                datetime_attr = date_tag.get('datetime')
                if datetime_attr:
                    dt = datetime.strptime(datetime_attr.split('T')[0], '%Y-%m-%d')
                    published_date = dt.strftime('%Y-%m-%d')
            except:
                pass

        return {
            'site_number': 1,
            'site_name': 'WOWTALE',
            'site_url': "",
            'article_title': title,
            'article_url': url,
            'published_date': published_date
        }

    except Exception as e:
        return None


def main():
    print("=" * 80)
    print("WOWTALE 깊이 탐색 (검색 + 아카이브 + 카테고리)")
    print("=" * 80)

    # WOWTALE 아카이브 URL 수집
    urls = get_wowtale_archive_urls()

    print(f"\n총 발견 URL: {len(urls)}개\n")

    found = 0
    duplicate = 0
    no_investment = 0

    for idx, url in enumerate(urls, 1):
        print(f"[{idx:3d}/{len(urls)}] {url[:60]}...", end=' ')

        # 기사 데이터 추출
        article = extract_article_data(url)

        if not article:
            print("❌ 투자 뉴스 아님")
            no_investment += 1
            continue

        # 중복 확인
        existing = supabase.table("investment_news_articles")\
            .select("id")\
            .eq("article_url", article['article_url'])\
            .execute()

        if not existing.data:
            try:
                supabase.table("investment_news_articles").insert(article).execute()
                print(f"✅ {article['article_title'][:40]}...")
                found += 1
            except Exception as e:
                print(f"❌ DB 오류: {e}")
        else:
            print(f"⚠️ 중복")
            duplicate += 1

        time.sleep(0.5)

    print(f"\n{'='*80}")
    print("WOWTALE 탐색 완료")
    print(f"{'='*80}")
    print(f"✅ 새로 발견: {found}개")
    print(f"⚠️ 중복: {duplicate}개")
    print(f"❌ 투자 뉴스 아님: {no_investment}개")
    print(f"{'='*80}")

    # 최종 통계
    print(f"\ninvestment_news_articles 테이블 총 레코드:")
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"  {count_result.count}개")


if __name__ == '__main__':
    main()
