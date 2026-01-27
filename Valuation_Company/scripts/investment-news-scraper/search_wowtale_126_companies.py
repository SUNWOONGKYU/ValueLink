#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WOWTALE 사이트 내 검색 - 126개 기업명으로 직접 검색
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
from urllib.parse import quote

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


def search_wowtale(company_name):
    """WOWTALE 사이트 내 검색"""

    # WOWTALE 검색 URL (일반적인 WordPress 검색 패턴)
    search_url = f"https://wowtale.net/?s={quote(company_name)}"

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 검색 결과에서 기사 링크 추출
        # WordPress 일반 패턴: article, post, entry 등의 클래스
        articles = []

        # 방법 1: article 태그
        for article in soup.find_all('article'):
            title_tag = article.find('h2')
            if not title_tag:
                title_tag = article.find('h3')
            if not title_tag:
                continue

            link_tag = title_tag.find('a', href=True)
            if not link_tag:
                link_tag = article.find('a', href=True)
            if not link_tag:
                continue

            title = title_tag.get_text().strip()
            url = link_tag.get('href')

            # 투자 키워드 확인
            investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
            if any(kw in title for kw in investment_keywords):
                articles.append({'title': title, 'url': url})

        # 방법 2: 일반 링크에서 2026/01 포함 + 기업명 포함
        if not articles:
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().strip()

                if company_name in text and '/202' in href and 'wowtale.net' in href:
                    investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
                    if any(kw in text for kw in investment_keywords):
                        articles.append({'title': text, 'url': href})

        # 첫 번째 결과 반환
        if articles:
            return articles[0]

        return None

    except Exception as e:
        return None


def extract_article_date(url):
    """기사 날짜 추출"""

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

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

        return published_date

    except:
        return datetime.now().strftime('%Y-%m-%d')


def main():
    print("=" * 80)
    print("WOWTALE 사이트 내 검색 - 126개 기업명")
    print("=" * 80)

    # CSV 읽기
    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업\n")

    found = 0
    duplicate = 0
    not_found = []

    for idx, row in enumerate(companies, 1):
        company = row['기업명']

        print(f"[{idx:3d}/{len(companies)}] {company:20s}...", end=' ')

        # WOWTALE 검색
        result = search_wowtale(company)

        if result:
            url = result['url']
            title = result['title']

            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", url)\
                .execute()

            if not existing.data:
                # 날짜 추출
                published_date = extract_article_date(url)

                article = {
                    'site_number': 1,
                    'site_name': 'WOWTALE',
                    'site_url': "",
                    'article_title': title,
                    'article_url': url,
                    'published_date': published_date
                }

                try:
                    supabase.table("investment_news_articles").insert(article).execute()
                    print(f"✅ {title[:40]}...")
                    found += 1
                except Exception as e:
                    print(f"❌ DB 오류: {e}")
            else:
                print(f"⚠️ 중복")
                duplicate += 1
        else:
            print("❌ 못 찾음")
            not_found.append(company)

        time.sleep(1)  # 요청 간격

    print(f"\n{'='*80}")
    print("WOWTALE 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 새로 발견: {found}개")
    print(f"⚠️ 중복: {duplicate}개")
    print(f"❌ 못 찾음: {len(not_found)}개")
    print(f"{'='*80}")

    # 최종 통계
    result = supabase.table("investment_news_articles").select("article_title").execute()

    final_collected = set()
    for article in result.data:
        for row in companies:
            if row['기업명'] in article['article_title']:
                final_collected.add(row['기업명'])

    print(f"\n📊 126개 기업 최종:")
    print(f"  ✅ 뉴스 있음: {len(final_collected)}개 ({len(final_collected)*100//126}%)")
    print(f"  ❌ 뉴스 없음: {126-len(final_collected)}개")

    if not_found:
        with open('wowtale_not_found.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")
        print(f"\n⚠️ WOWTALE에서 못 찾은 기업: wowtale_not_found.txt ({len(not_found)}개)")

    print(f"\ninvestment_news_articles 테이블 총 레코드:")
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"  {count_result.count}개")


if __name__ == '__main__':
    main()
