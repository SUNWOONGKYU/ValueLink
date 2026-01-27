#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5개 언론사 사이트 내 검색 - 126개 기업명
WOWTALE, 벤처스퀘어, 아웃스탠딩, 플래텀, 스타트업투데이
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

# 5개 언론사 정보
SITES = {
    'WOWTALE': {
        'number': 1,
        'search_url': 'https://wowtale.net/?s={}',
        'domain': 'wowtale.net'
    },
    '벤처스퀘어': {
        'number': 9,
        'search_url': 'https://www.venturesquare.net/?s={}',
        'domain': 'venturesquare.net'
    },
    '아웃스탠딩': {
        'number': 13,
        'search_url': 'https://outstanding.kr/?s={}',
        'domain': 'outstanding.kr'
    },
    '플래텀': {
        'number': 10,
        'search_url': 'https://platum.kr/?s={}',
        'domain': 'platum.kr'
    },
    '스타트업투데이': {
        'number': 11,
        'search_url': 'https://www.startuptoday.kr/?s={}',
        'domain': 'startuptoday.kr'
    }
}


def search_site(site_name, site_info, company_name):
    """특정 사이트에서 기업명 검색"""

    search_url = site_info['search_url'].format(quote(company_name))

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 검색 결과에서 기사 링크 추출
        articles = []

        # WordPress 일반 패턴: article 태그
        for article in soup.find_all('article'):
            title_tag = article.find('h2')
            if not title_tag:
                title_tag = article.find('h3')
            if not title_tag:
                title_tag = article.find('h1')
            if not title_tag:
                continue

            link_tag = title_tag.find('a', href=True)
            if not link_tag:
                link_tag = article.find('a', href=True)
            if not link_tag:
                continue

            title = title_tag.get_text().strip()
            url = link_tag.get('href')

            # 공지사항 제외
            if '[공지]' in title or '공지사항' in title or '이벤트' in title:
                continue

            # 투자 키워드 확인
            investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
            if any(kw in title for kw in investment_keywords):
                # 기업명 확인
                if company_name in title:
                    articles.append({'title': title, 'url': url})

        # 일반 링크에서도 검색 (article 태그가 없는 경우)
        if not articles:
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().strip()

                # 공지사항 제외
                if '[공지]' in text or '공지사항' in text or '이벤트' in text:
                    continue

                if company_name in text and site_info['domain'] in href:
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
        date_tag = soup.find('time')
        if not date_tag:
            date_tag = soup.find('span', class_=['date', 'entry-date', 'published'])

        published_date = datetime.now().strftime('%Y-%m-%d')
        if date_tag:
            try:
                datetime_attr = date_tag.get('datetime')
                if datetime_attr:
                    dt = datetime.strptime(datetime_attr.split('T')[0], '%Y-%m-%d')
                    published_date = dt.strftime('%Y-%m-%d')
                else:
                    date_text = date_tag.get_text().strip()
                    # YYYY-MM-DD 또는 YYYY.MM.DD 형식 추출
                    import re
                    match = re.search(r'(\d{4})[.-](\d{2})[.-](\d{2})', date_text)
                    if match:
                        published_date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            except:
                pass

        return published_date

    except:
        return datetime.now().strftime('%Y-%m-%d')


def main():
    print("=" * 80)
    print("5개 언론사 사이트 내 검색 - 126개 기업명")
    print("=" * 80)

    # CSV 읽기
    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업\n")

    found_by_site = {site: 0 for site in SITES.keys()}
    total_found = 0
    total_duplicate = 0
    not_found = []

    for idx, row in enumerate(companies, 1):
        company = row['기업명']

        print(f"[{idx:3d}/{len(companies)}] {company:20s}...", end=' ')

        found_this_company = False

        # 5개 사이트에서 순서대로 검색
        for site_name, site_info in SITES.items():
            result = search_site(site_name, site_info, company)

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
                        'site_number': site_info['number'],
                        'site_name': site_name,
                        'site_url': "",
                        'article_title': title,
                        'article_url': url,
                        'published_date': published_date
                    }

                    try:
                        supabase.table("investment_news_articles").insert(article).execute()
                        print(f"✅ [{site_name}] {title[:30]}...")
                        found_by_site[site_name] += 1
                        total_found += 1
                        found_this_company = True
                        break  # 하나 찾으면 다음 기업으로
                    except Exception as e:
                        pass
                else:
                    print(f"⚠️ [{site_name}] 중복")
                    total_duplicate += 1
                    found_this_company = True
                    break

            time.sleep(0.5)  # 사이트당 대기

        if not found_this_company:
            print("❌ 모든 사이트에서 못 찾음")
            not_found.append(company)

        time.sleep(1)  # 기업당 대기

    print(f"\n{'='*80}")
    print("5개 언론사 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 새로 발견: {total_found}개")
    for site, count in found_by_site.items():
        if count > 0:
            print(f"   - {site}: {count}개")
    print(f"⚠️ 중복: {total_duplicate}개")
    print(f"❌ 못 찾음: {len(not_found)}개")
    print(f"{'='*80}")

    # 최종 통계
    result = supabase.table("investment_news_articles").select("article_title").execute()

    final_collected = set()
    for article in result.data:
        for comp in companies:
            if comp['기업명'] in article['article_title']:
                final_collected.add(comp['기업명'])

    print(f"\n📊 126개 기업 최종:")
    print(f"  ✅ 뉴스 있음: {len(final_collected)}개 ({len(final_collected)*100//126}%)")
    print(f"  ❌ 뉴스 없음: {126-len(final_collected)}개")

    if not_found:
        with open('all_5sites_not_found.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")
        print(f"\n⚠️ 5개 사이트에서 못 찾은 기업: all_5sites_not_found.txt ({len(not_found)}개)")

    print(f"\ninvestment_news_articles 테이블 총 레코드:")
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"  {count_result.count}개")


if __name__ == '__main__':
    main()
