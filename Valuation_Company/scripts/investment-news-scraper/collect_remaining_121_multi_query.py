#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
미수집 121개 기업 다중 쿼리 전략으로 재검색
"""

import os
import sys
import csv
import requests
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

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")


def extract_first_investor(investor_str):
    """투자자 문자열에서 첫 단어 추출"""
    if not investor_str or investor_str == '-':
        return ""

    # 공백, 하이픈, 쉼표로 분리하고 첫 단어 추출
    words = investor_str.replace('-', ' ').replace(',', ' ').split()
    if words:
        return words[0]
    return ""


def search_naver_multi_query(company_name, investor_str):
    """네이버 API - 여러 쿼리 조합으로 검색"""

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    # 투자자 첫 단어 추출
    first_investor = extract_first_investor(investor_str)

    # 여러 검색 쿼리 조합 (우선순위 순)
    queries = []

    if first_investor:
        queries.append(f"{company_name} {first_investor} 투자")
        queries.append(f"{company_name} {first_investor} 유치")
        queries.append(f"{company_name} {first_investor}")

    queries.extend([
        f"{company_name} 투자유치",
        f"{company_name} 시리즈",
        f"{company_name} 펀딩",
        f"{company_name} 라운드",
        f"{company_name} VC",
    ])

    # 각 쿼리 시도
    for query in queries:
        params = {
            'query': query,
            'display': 50,  # 최대한 많이
            'sort': 'date'
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                items = response.json().get('items', [])

                for item in items:
                    title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                    link = item.get('originallink') or item.get('link')
                    pub_date = item.get('pubDate', '')

                    # 기업명 정확히 포함
                    if company_name not in title:
                        continue

                    # 투자 키워드
                    investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'VC', '벤처캐피털']
                    if not any(kw in title for kw in investment_keywords):
                        continue

                    # 날짜 파싱
                    try:
                        dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                        published_date = dt.strftime('%Y-%m-%d')
                    except:
                        published_date = datetime.now().strftime('%Y-%m-%d')

                    # 사이트명
                    site_mapping = {
                        'venturesquare.net': ('벤처스퀘어', 9),
                        'wowtale.net': ('WOWTALE', 1),
                        'platum.kr': ('플래텀', 10),
                        'outstanding.kr': ('아웃스탠딩', 13),
                        'startuptoday.kr': ('스타트업투데이', 11),
                        'thebell.co.kr': ('더벨', 16),
                    }

                    site_name = "네이버 뉴스"
                    site_number = 99

                    for domain, (name, num) in site_mapping.items():
                        if domain in link:
                            site_name = name
                            site_number = num
                            break

                    return {
                        'site_number': site_number,
                        'site_name': site_name,
                        'site_url': "",
                        'article_title': title,
                        'article_url': link,
                        'published_date': published_date
                    }, query

            time.sleep(0.15)

        except Exception as e:
            continue

    return None, None


def main():
    print("=" * 80)
    print("미수집 121개 기업 다중 쿼리 전략 재검색")
    print("=" * 80)

    # CSV 읽기
    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = {row['기업명']: row for row in reader}

    # 미수집 기업 목록
    with open('final_not_found_126.txt', 'r', encoding='utf-8') as f:
        not_found = [line.strip() for line in f if line.strip()]

    print(f"\n미수집 기업: {len(not_found)}개\n")

    found = 0
    duplicate = 0
    still_not_found = []

    for idx, company in enumerate(not_found, 1):
        if company not in companies:
            print(f"[{idx:3d}/{len(not_found)}] {company:20s}... ❌ CSV에 없음")
            still_not_found.append(company)
            continue

        row = companies[company]
        investor = row['투자자']
        first_inv = extract_first_investor(investor)

        print(f"[{idx:3d}/{len(not_found)}] {company:20s} + {first_inv:15s}...", end=' ')

        # 다중 쿼리 검색
        article, matched_query = search_naver_multi_query(company, investor)

        if article and article['article_url']:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if not existing.data:
                try:
                    supabase.table("investment_news_articles").insert(article).execute()
                    print(f"✅ [{article['site_name']}] Query: {matched_query}")
                    found += 1
                except:
                    print(f"❌ DB 오류")
            else:
                print(f"⚠️ 중복")
                duplicate += 1
        else:
            print("❌ 못 찾음")
            still_not_found.append(company)

        time.sleep(0.2)

    print(f"\n{'='*80}")
    print("재검색 완료")
    print(f"{'='*80}")
    print(f"✅ 새로 발견: {found}개")
    print(f"⚠️ 중복: {duplicate}개")
    print(f"❌ 여전히 못 찾음: {len(still_not_found)}개")
    print(f"{'='*80}")

    # 최종 통계
    result = supabase.table("investment_news_articles").select("article_title").execute()

    all_companies = list(companies.keys())
    final_collected = set()
    for article in result.data:
        for comp in all_companies:
            if comp in article['article_title']:
                final_collected.add(comp)

    print(f"\n📊 126개 기업 최종:")
    print(f"  ✅ 뉴스 있음: {len(final_collected)}개 ({len(final_collected)*100//126}%)")
    print(f"  ❌ 뉴스 없음: {126-len(final_collected)}개")

    if still_not_found:
        with open('still_not_found_after_multi_query.txt', 'w', encoding='utf-8') as f:
            for company in still_not_found:
                f.write(f"{company}\n")
        print(f"\n⚠️ 여전히 못 찾은 기업: still_not_found_after_multi_query.txt ({len(still_not_found)}개)")

    print(f"\ninvestment_news_articles 테이블 총 레코드:")
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"  {count_result.count}개")


if __name__ == '__main__':
    main()
