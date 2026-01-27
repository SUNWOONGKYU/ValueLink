#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 2: 구글 검색으로 투자 뉴스 수집 (직접 스크래핑)
"""

import os
import sys
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
import re
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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

# 타겟 미디어 도메인
TARGET_SITES = [
    'wowtale.net',
    'venturesquare.net',
    'outstanding.kr',
    'platum.kr',
    'startuptoday.kr',
    'thebell.co.kr',
    'bloter.net',
    'zdnet.co.kr',
    'aitimes.com'
]

# 사이트명 매핑
SITE_NAME_MAP = {
    'wowtale.net': ('WOWTALE', 1),
    'venturesquare.net': ('벤처스퀘어', 9),
    'outstanding.kr': ('아웃스탠딩', 13),
    'platum.kr': ('플래텀', 10),
    'startuptoday.kr': ('스타트업투데이', 11),
    'thebell.co.kr': ('더벨', 16),
    'bloter.net': ('블로터', 22),
    'zdnet.co.kr': ('지디넷코리아', 15),
    'aitimes.com': ('AI타임스', 19)
}


def google_search(company_name, stage):
    """구글 검색으로 투자 뉴스 찾기"""

    # 검색 쿼리
    query = f"{company_name} {stage} 투자 유치 2026"

    # 사이트 필터 추가
    site_filter = " OR ".join([f"site:{site}" for site in TARGET_SITES])
    full_query = f"{query} ({site_filter})"

    search_url = f"https://www.google.com/search?q={quote(full_query)}&tbm=nws"

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 검색 결과 링크 찾기
        links = soup.find_all('a')

        for link in links:
            href = link.get('href', '')

            # /url?q= 패턴 추출
            if '/url?q=' in href:
                # 실제 URL 추출
                match = re.search(r'/url\?q=([^&]+)', href)
                if not match:
                    continue

                url = match.group(1)

                # 타겟 사이트인지 확인
                is_target = False
                site_name = None
                site_number = 99

                for domain in TARGET_SITES:
                    if domain in url:
                        is_target = True
                        if domain in SITE_NAME_MAP:
                            site_name, site_number = SITE_NAME_MAP[domain]
                        else:
                            site_name = domain
                        break

                if not is_target:
                    continue

                # 제목 추출
                title_elem = link.find_parent('div')
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                else:
                    title_text = link.get_text(strip=True)

                # 기업명 확인
                if company_name not in title_text:
                    continue

                return {
                    'site_number': site_number,
                    'site_name': site_name,
                    'site_url': f"https://{domain}",
                    'article_title': title_text[:200] if len(title_text) > 200 else title_text,
                    'article_url': url,
                    'published_date': datetime.now().strftime('%Y-%m-%d')
                }

        return None

    except Exception as e:
        return None


def main():
    print("=" * 60)
    print("STEP 2: 구글 검색으로 투자 뉴스 수집")
    print("=" * 60)

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    # CSV 읽기
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업")

    # 이미 수집된 기업 확인
    result = supabase.table("investment_news_articles")\
        .select("article_title")\
        .execute()

    collected_companies = set()
    for article in result.data:
        for row in companies:
            if row['기업명'] in article['article_title']:
                collected_companies.add(row['기업명'])

    # 미수집 기업만 필터링
    todo_companies = [c for c in companies if c['기업명'] not in collected_companies]

    print(f"이미 수집: {len(collected_companies)}개")
    print(f"검색 대상: {len(todo_companies)}개\n")

    found_count = 0
    not_found = []

    for idx, row in enumerate(todo_companies, 1):
        company_name = row['기업명']
        stage = row['단계']

        print(f"[{idx}/{len(todo_companies)}] {company_name}...", end=' ')

        # 구글 검색
        article = google_search(company_name, stage)

        if article and article['article_url']:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if not existing.data:
                # DB 저장
                try:
                    supabase.table("investment_news_articles").insert(article).execute()
                    print(f"✅ [{article['site_name']}]")
                    found_count += 1

                except Exception as e:
                    print(f"❌ DB 저장 실패")
            else:
                print(f"⚠️ 중복")
        else:
            print("❌ 못 찾음")
            not_found.append(company_name)

        time.sleep(2)  # 구글 차단 방지 (중요!)

    print(f"\n{'='*60}")
    print("STEP 2 완료")
    print(f"{'='*60}")
    print(f"✅ 발견: {found_count}개")
    print(f"❌ 미발견: {len(not_found)}개")
    print(f"{'='*60}")

    # 미발견 목록 저장
    if not_found:
        with open('not_found_after_google.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")

        print(f"\n⚠️ 미발견 목록 저장: not_found_after_google.txt")
        print(f"→ STEP 3 (네이버 API)로 진행 필요")


if __name__ == '__main__':
    main()
