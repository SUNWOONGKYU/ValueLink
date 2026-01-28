#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5개 언론사 깊이 탐색 - 아카이브, 카테고리, 태그별 수집
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import time
from urllib.parse import urljoin

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

# 못 찾은 3개 기업
target_companies = ["부스티스", "애플에이아이", "소셜릭스코리아"]

# 5개 언론사 심층 탐색 URL
MEDIA_SOURCES = {
    "WOWTALE": {
        "name": "WOWTALE",
        "number": 1,
        "urls": [
            "https://wowtale.net/category/investment/",
            "https://wowtale.net/2026/01/",
            "https://wowtale.net/2025/12/",
            "https://wowtale.net/2025/11/",
        ]
    },
    "벤처스퀘어": {
        "name": "벤처스퀘어",
        "number": 9,
        "urls": [
            "https://www.venturesquare.net/category/news/investment",
            "https://www.venturesquare.net/category/startup",
            "https://www.venturesquare.net/page/2/",
            "https://www.venturesquare.net/page/3/",
            "https://www.venturesquare.net/page/4/",
        ]
    },
    "더벨": {
        "name": "더벨",
        "number": 16,
        "urls": [
            "https://www.thebell.co.kr/free/content/NewsList.asp?svccode=00&trustkey=00",
            "https://www.thebell.co.kr/free/content/NewsList.asp?page=2",
            "https://www.thebell.co.kr/free/content/NewsList.asp?page=3",
        ]
    },
    "플래텀": {
        "name": "플래텀",
        "number": 10,
        "urls": [
            "https://platum.kr/archives/category/startup-story/investment",
            "https://platum.kr/archives/category/startup-story",
            "https://platum.kr/page/2/",
            "https://platum.kr/page/3/",
        ]
    },
    "스타트업투데이": {
        "name": "스타트업투데이",
        "number": 11,
        "urls": [
            "https://www.startuptoday.kr/news/articleList.html?sc_section_code=S1N1",
            "https://www.startuptoday.kr/news/articleList.html?sc_section_code=S1N2",
            "https://www.startuptoday.kr/news/articleList.html?page=2",
            "https://www.startuptoday.kr/news/articleList.html?page=3",
        ]
    }
}


def extract_articles_from_page(url, media_name):
    """페이지에서 모든 기사 링크 추출"""

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []

        # 모든 링크 추출
        links = soup.find_all('a', href=True)

        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()

            # 절대 URL 변환
            if href.startswith('/'):
                base_url = '/'.join(url.split('/')[:3])
                href = urljoin(base_url, href)

            # 기사 URL 패턴 확인
            is_article = False

            if media_name == "WOWTALE" and '/2025/' in href or '/2026/' in href:
                is_article = True
            elif media_name == "벤처스퀘어" and 'venturesquare.net' in href and len(href.split('/')) > 3:
                is_article = True
            elif media_name == "아웃스탠딩" and 'outstanding.kr' in href and href.count('/') >= 3:
                is_article = True
            elif media_name == "플래텀" and 'platum.kr/archives/' in href:
                is_article = True
            elif media_name == "스타트업투데이" and 'articleView.html' in href:
                is_article = True

            if is_article and text:
                # 3개 기업 중 하나라도 포함?
                for company in target_companies:
                    if company in text:
                        # 투자 키워드 확인
                        investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'M&A', '인수']
                        if any(kw in text for kw in investment_keywords):
                            articles.append({
                                'title': text,
                                'url': href,
                                'company': company
                            })
                            break

        return articles

    except Exception as e:
        print(f"    오류: {e}")
        return []


def main():
    print("=" * 80)
    print("5개 언론사 심층 탐색 - 아카이브, 카테고리, 페이지별")
    print("=" * 80)
    print(f"\n🎯 타겟: {', '.join(target_companies)}\n")

    total_found = 0
    total_duplicate = 0
    all_found_companies = set()

    for media_name, media_info in MEDIA_SOURCES.items():
        print(f"\n{'='*80}")
        print(f"📰 {media_name} 탐색 중...")
        print(f"{'='*80}")

        media_found = 0
        media_duplicate = 0

        for idx, url in enumerate(media_info['urls'], 1):
            print(f"\n[{idx}/{len(media_info['urls'])}] {url}")
            print(f"  🔍 크롤링 중...", end=' ')

            articles = extract_articles_from_page(url, media_name)

            print(f"{len(articles)}개 기사 발견")

            for article in articles:
                print(f"  ✅ [{article['company']}] {article['title'][:50]}...")

                # DB 저장
                article_data = {
                    'site_number': media_info['number'],
                    'site_name': media_info['name'],
                    'site_url': "",
                    'article_title': article['title'],
                    'article_url': article['url'],
                    'published_date': datetime.now().strftime('%Y-%m-%d')
                }

                # 중복 확인
                existing = supabase.table("investment_news_articles")\
                    .select("id")\
                    .eq("article_url", article_data['article_url'])\
                    .execute()

                if not existing.data:
                    try:
                        supabase.table("investment_news_articles").insert(article_data).execute()
                        print(f"     💾 저장 완료")
                        media_found += 1
                        total_found += 1
                        all_found_companies.add(article['company'])
                    except:
                        print(f"     ❌ DB 오류")
                else:
                    print(f"     ⚠️  중복")
                    media_duplicate += 1
                    total_duplicate += 1

            time.sleep(1)

        print(f"\n{media_name} 결과:")
        print(f"  ✅ 새로 발견: {media_found}개")
        print(f"  ⚠️  중복: {media_duplicate}개")

    print(f"\n{'='*80}")
    print("5개 언론사 심층 탐색 완료")
    print(f"{'='*80}")
    print(f"✅ 총 새로 발견: {total_found}개")
    print(f"⚠️  총 중복: {total_duplicate}개")
    print(f"{'='*80}")

    if all_found_companies:
        print(f"\n🎉 발견된 기업:")
        for company in all_found_companies:
            print(f"  ✅ {company}")

    not_found = set(target_companies) - all_found_companies
    if not_found:
        print(f"\n❌ 여전히 못 찾은 기업:")
        for company in not_found:
            print(f"  - {company}")

    # 최종 통계
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"\ninvestment_news_articles 테이블 총 레코드: {count_result.count}개")


if __name__ == '__main__':
    main()
