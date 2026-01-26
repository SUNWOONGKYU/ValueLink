#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 스크래핑 수집 (6개 사이트)
- 스타트업투데이, 스타트업엔, 블로터, 이코노미스트, AI타임스, 넥스트유니콘
"""

import requests
from bs4 import BeautifulSoup
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

# 웹 스크래핑 소스 정보
WEB_SOURCES = [
    {
        'source_number': 11,
        'source_name': '스타트업투데이',
        'source_url': 'https://startuptoday.kr',
        'selector': 'article'
    },
    {
        'source_number': 12,
        'source_name': '스타트업엔',
        'source_url': 'https://startupn.kr',
        'selector': 'article'
    },
    {
        'source_number': 22,
        'source_name': '블로터',
        'source_url': 'https://www.bloter.net',
        'selector': 'article'
    },
    {
        'source_number': 23,
        'source_name': '이코노미스트',
        'source_url': 'https://www.economist.co.kr',
        'selector': 'h2 a'
    },
    {
        'source_number': 19,
        'source_name': 'AI타임스',
        'source_url': 'https://www.aitimes.com',
        'selector': 'article'
    },
    {
        'source_number': 21,
        'source_name': '넥스트유니콘',
        'source_url': 'https://www.nextunicorn.kr',
        'selector': 'article'
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


def collect_from_web(source):
    """
    웹사이트에서 기사 스크래핑

    Args:
        source: 소스 정보 딕셔너리

    Returns:
        수집된 기사 리스트
    """
    print(f"\n[{source['source_name']}] Scraping website...")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(source['source_url'], headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"  [ERROR] HTTP {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        # 선택자로 요소 찾기
        elements = soup.select(source['selector'])

        if not elements:
            print(f"  [WARN] No elements found with selector: {source['selector']}")
            return []

        print(f"  [INFO] Found {len(elements)} elements")

        articles = []

        for elem in elements:
            # 제목 찾기
            title = None
            title_tag = elem.find(['h1', 'h2', 'h3', 'h4', '.title', '.headline'])
            if title_tag:
                title = title_tag.get_text().strip()
            elif elem.name == 'a':  # 이코노미스트처럼 a 태그 자체가 선택된 경우
                title = elem.get_text().strip()

            # URL 찾기
            link = None
            link_tag = elem.find('a')
            if link_tag and link_tag.get('href'):
                link = link_tag['href']
            elif elem.name == 'a':  # a 태그 자체인 경우
                link = elem.get('href')

            # 제목, URL 둘 다 없으면 스킵
            if not title or not link:
                continue

            # 절대 URL로 변환
            if link and not link.startswith('http'):
                if link.startswith('/'):
                    link = source['source_url'] + link
                else:
                    link = source['source_url'] + '/' + link

            # 투자 키워드 필터링
            has_investment_keyword = any(kw.lower() in title.lower() for kw in INVESTMENT_KEYWORDS)

            # 제외 키워드 체크
            has_excluded_keyword = any(kw in title for kw in EXCLUDED_KEYWORDS)

            # 투자 키워드가 있고, 제외 키워드가 없으면 수집
            if has_investment_keyword and not has_excluded_keyword:
                # 요약/스니펫 (article인 경우 p 태그 찾기)
                content_snippet = None
                if elem.name == 'article':
                    p_tag = elem.find('p')
                    if p_tag:
                        content_snippet = p_tag.get_text().strip()[:500]

                article = {
                    'site_number': source['source_number'],
                    'site_name': source['source_name'],
                    'site_url': source['source_url'],
                    'article_title': title,
                    'article_url': link,
                    'published_date': datetime.now().isoformat(),  # 웹 스크래핑은 수집 시간 사용
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
    print("Web Scraping Collection")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_articles = []

    # 각 소스에서 수집
    for source in WEB_SOURCES:
        articles = collect_from_web(source)
        all_articles.extend(articles)

        # 마지막 수집 시간 업데이트
        if articles:
            update_last_collected(source['source_number'])

        # Rate limiting (2초 대기)
        time.sleep(2)

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
