#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 1: 5개 언론사에서 126개 기업 투자 뉴스 검색
- WOWTALE, 벤처스퀘어, 아웃스탠딩, 플래텀, 스타트업투데이
"""

import os
import sys
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

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

# 5개 언론사 설정
SITES = [
    {
        'number': 1,
        'name': 'WOWTALE',
        'url': 'https://wowtale.net',
        'search_url': 'https://wowtale.net/?s={keyword}',
        'selectors': {
            'article': 'article, div.post',
            'title': 'h2 a, h3 a, .entry-title a',
            'link': 'h2 a, h3 a, .entry-title a'
        }
    },
    {
        'number': 9,
        'name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net',
        'search_url': 'https://www.venturesquare.net/?s={keyword}',
        'selectors': {
            'article': 'li, article',
            'title': 'h4.bold a.black, h2 a, h3 a',
            'link': 'h4.bold a.black, h2 a, h3 a'
        }
    },
    {
        'number': 13,
        'name': '아웃스탠딩',
        'url': 'https://outstanding.kr',
        'search_url': 'https://outstanding.kr/?s={keyword}',
        'selectors': {
            'article': 'article, div.post-item',
            'title': 'h2 a, h3 a',
            'link': 'h2 a, h3 a'
        }
    },
    {
        'number': 10,
        'name': '플래텀',
        'url': 'https://platum.kr',
        'search_url': 'https://platum.kr/?s={keyword}',
        'selectors': {
            'article': 'article, div.post',
            'title': 'h2.entry-title a, h3 a',
            'link': 'h2.entry-title a, h3 a'
        }
    },
    {
        'number': 11,
        'name': '스타트업투데이',
        'url': 'https://www.startuptoday.kr',
        'search_url': 'https://www.startuptoday.kr/news/articleList.html?sc_area=A&view_type=sm&sc_word={keyword}',
        'selectors': {
            'article': 'div.list-block, article',
            'title': 'div.list-titles a, h4.titles a',
            'link': 'div.list-titles a, h4.titles a'
        }
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9',
}

INVESTMENT_KEYWORDS = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']


def search_company_in_site(company_name, site):
    """언론사 사이트에서 기업명 검색"""

    keyword = quote(f"{company_name} 투자")
    search_url = site['search_url'].format(keyword=keyword)

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = soup.select(site['selectors']['article'])

        for article in articles[:10]:  # 상위 10개만
            try:
                link_elem = article.select_one(site['selectors']['link'])
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                url = link_elem.get('href', '')

                # 기업명 확인
                if company_name not in title:
                    continue

                # 투자 키워드 확인
                if not any(kw in title for kw in INVESTMENT_KEYWORDS):
                    continue

                # URL 정규화
                if url.startswith('/'):
                    url = site['url'] + url
                elif not url.startswith('http'):
                    url = site['url'] + '/' + url

                return {
                    'site_number': site['number'],
                    'site_name': site['name'],
                    'site_url': site['url'],
                    'article_title': title,
                    'article_url': url,
                    'published_date': datetime.now().strftime('%Y-%m-%d')
                }

            except Exception:
                continue

        return None

    except Exception:
        return None


def main():
    print("=" * 60)
    print("STEP 1: 5개 언론사에서 126개 기업 투자 뉴스 검색")
    print("=" * 60)

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    # CSV 읽기
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업")
    print(f"검색 언론사: {len(SITES)}개\n")

    found_count = 0
    not_found = []

    for idx, row in enumerate(companies, 1):
        company_name = row['기업명']

        print(f"[{idx}/{len(companies)}] {company_name}...", end=' ')

        # 5개 언론사 순회
        article_found = False

        for site in SITES:
            article = search_company_in_site(company_name, site)

            if article:
                # 중복 확인
                existing = supabase.table("investment_news_articles")\
                    .select("id")\
                    .eq("article_url", article['article_url'])\
                    .execute()

                if not existing.data:
                    # DB 저장
                    try:
                        supabase.table("investment_news_articles").insert(article).execute()
                        print(f"✅ [{site['name']}]")
                        found_count += 1
                        article_found = True
                        break
                    except Exception as e:
                        print(f"❌ DB 저장 실패: {str(e)[:30]}")
                else:
                    print(f"⚠️ 중복 [{site['name']}]")
                    article_found = True
                    break

            time.sleep(0.1)  # 사이트 부하 방지 (0.3→0.1초로 단축)

        if not article_found:
            print("❌ 못 찾음")
            not_found.append(company_name)

    print(f"\n{'='*60}")
    print("STEP 1 완료")
    print(f"{'='*60}")
    print(f"✅ 발견: {found_count}개 ({found_count*100/len(companies):.1f}%)")
    print(f"❌ 미발견: {len(not_found)}개")
    print(f"{'='*60}")

    # 미발견 목록 저장
    if not_found:
        with open('not_found_companies.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")

        print(f"\n⚠️ 미발견 목록 저장: not_found_companies.txt")
        print(f"→ STEP 2 (구글 검색)로 진행 필요")


if __name__ == '__main__':
    main()
