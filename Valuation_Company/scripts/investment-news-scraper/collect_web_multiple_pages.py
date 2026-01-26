#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 스크래핑 수집 - 여러 페이지 (1월 전체 수집)
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

# 웹 스크래핑 소스 정보 (페이지네이션 지원)
WEB_SOURCES = [
    {
        'source_number': 11,
        'source_name': '스타트업투데이',
        'base_url': 'https://startuptoday.kr',
        'page_url_template': 'https://startuptoday.kr/news/articleList.html?page={page}',
        'selector': 'article',
        'max_pages': 5  # 5페이지까지
    },
    {
        'source_number': 12,
        'source_name': '스타트업엔',
        'base_url': 'https://startupn.kr',
        'page_url_template': 'https://startupn.kr/news/articleList.html?page={page}',
        'selector': 'article',
        'max_pages': 5
    },
    {
        'source_number': 22,
        'source_name': '블로터',
        'base_url': 'https://www.bloter.net',
        'page_url_template': 'https://www.bloter.net/news/articleList.html?page={page}',
        'selector': 'article',
        'max_pages': 5
    },
    {
        'source_number': 19,
        'source_name': 'AI타임스',
        'base_url': 'https://www.aitimes.com',
        'page_url_template': 'https://www.aitimes.com/news/articleList.html?page={page}',
        'selector': 'article',
        'max_pages': 5
    }
]

INVESTMENT_KEYWORDS = [
    '투자', '유치', '시리즈', '펀딩', 'funding', 'investment',
    'Series A', 'Series B', 'Series C', 'Pre-A', '시드', 'Seed',
    '억원', 'M', '조달', 'raised', 'rounds'
]

EXCLUDED_KEYWORDS = [
    'IR', 'M&A', '인수', '합병', '상장', 'IPO', '행사', '세미나',
    '채용', '인사', '임원', '대표이사', '엔젤리그', '실홀딩스'
]


def collect_from_web_pages(source):
    """여러 페이지에서 기사 수집"""

    print(f"\n[{source['source_name']}] Collecting from multiple pages...")

    all_articles = []

    for page in range(1, source['max_pages'] + 1):
        print(f"  Page {page}/{source['max_pages']}...")

        try:
            # 페이지 URL 생성
            if 'page_url_template' in source:
                url = source['page_url_template'].format(page=page)
            else:
                url = source['base_url']

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"    [WARN] HTTP {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            elements = soup.select(source['selector'])

            page_articles = 0

            for elem in elements:
                # 제목 찾기
                title = None
                title_tag = elem.find(['h1', 'h2', 'h3', 'h4', '.title', '.headline'])
                if title_tag:
                    title = title_tag.get_text().strip()
                elif elem.name == 'a':
                    title = elem.get_text().strip()

                # URL 찾기
                link = None
                link_tag = elem.find('a')
                if link_tag and link_tag.get('href'):
                    link = link_tag['href']
                elif elem.name == 'a':
                    link = elem.get('href')

                if not title or not link:
                    continue

                # 절대 URL로 변환
                if link and not link.startswith('http'):
                    if link.startswith('/'):
                        link = source['base_url'] + link
                    else:
                        link = source['base_url'] + '/' + link

                # 투자 키워드 필터링
                has_investment = any(kw.lower() in title.lower() for kw in INVESTMENT_KEYWORDS)
                has_excluded = any(kw in title for kw in EXCLUDED_KEYWORDS)

                if has_investment and not has_excluded:
                    article = {
                        'site_number': source['source_number'],
                        'site_name': source['source_name'],
                        'site_url': source['base_url'],
                        'article_title': title,
                        'article_url': link,
                        'published_date': datetime.now().isoformat(),
                        'content_snippet': None
                    }

                    all_articles.append(article)
                    page_articles += 1

            print(f"    Found {page_articles} investment articles")

            # Rate limiting
            time.sleep(2)

        except Exception as e:
            print(f"    [ERROR] {str(e)[:100]}")
            continue

    print(f"  [TOTAL] {len(all_articles)} articles from {source['source_name']}")
    return all_articles


def save_to_database(articles):
    """데이터베이스에 저장"""

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

    print(f"\n[RESULT] Saved: {saved}, Duplicated: {duplicated}, Failed: {failed}")
    return saved, duplicated, failed


def main():
    """메인 실행"""

    print("="*60)
    print("Web Scraping - Multiple Pages Collection")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_articles = []

    # 각 소스에서 수집
    for source in WEB_SOURCES:
        articles = collect_from_web_pages(source)
        all_articles.extend(articles)

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


if __name__ == '__main__':
    main()
