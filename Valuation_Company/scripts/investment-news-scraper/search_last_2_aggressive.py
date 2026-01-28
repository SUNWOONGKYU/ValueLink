#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마지막 2개 기업 공격적 검색
"""

import os
import sys
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

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 마지막 2개 기업
last_2_companies = {
    '디앤티테크솔루션': {
        '투자자': '리인인베스트먼트',
        '투자자2': 'L&S벤처캐피탈',
        '투자자3': '킹고투자파트너스',
        '주요사업': '산업 공정 자동화 솔루션',
        '변형': ['디앤티테크', '디앤티', 'DNT테크솔루션', 'DNT', 'D&T테크솔루션', 'D&T']
    },
    '엘리시전': {
        '투자자': '데일리파트너스-NH투자증권',
        '투자자2': '데일리파트너스',
        '투자자3': 'NH투자증권',
        '단계': '시리즈C',
        '금액': '50억',
        '주요사업': '유전자 치료제',
        '변형': ['엘리시전', 'Ellision', 'ellision', '엘리션', 'Elision']
    }
}

def search_naver_aggressive(company_name, company_info):
    """네이버 API - 공격적 검색"""

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    # 다양한 검색 쿼리
    all_variants = [company_name] + company_info.get('변형', [])
    investors = [company_info.get('투자자', ''), company_info.get('투자자2', ''), company_info.get('투자자3', '')]

    queries = []

    # 기업명 + 투자자
    for variant in all_variants:
        for investor in investors:
            if investor:
                queries.append(f"{variant} {investor}")
                queries.append(f"{variant} {investor} 투자")

    # 기업명 + 키워드
    for variant in all_variants:
        queries.extend([
            f"{variant} 투자유치",
            f"{variant} 투자",
            f"{variant} 펀딩",
            f"{variant} 시리즈",
            variant
        ])

    # 투자자 + 주요사업
    business = company_info.get('주요사업', '')
    if business:
        for investor in investors:
            if investor:
                queries.append(f"{investor} {business}")

    print(f"\n  🔍 {len(queries)}개 쿼리로 검색 중...")

    for query in queries[:50]:  # 최대 50개 쿼리
        params = {
            'query': query,
            'display': 100,
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

                    # 기업명 변형 중 하나라도 포함
                    found = False
                    for variant in all_variants:
                        if variant in title:
                            found = True
                            break

                    if not found:
                        continue

                    # 투자 키워드 확인
                    investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'VC', '캐피탈']
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
                        'wowtale.net': ('WOWTALE', 1),
                        'venturesquare.net': ('벤처스퀘어', 9),
                        'thebell.co.kr': ('더벨', 16),
                        'platum.kr': ('플래텀', 10),
                        'startuptoday.kr': ('스타트업투데이', 11),
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
                        'site_url': '',
                        'article_title': title,
                        'article_url': link,
                        'published_date': published_date
                    }, query

            time.sleep(0.1)

        except Exception as e:
            continue

    return None, None


def search_google_duckduckgo(company_name, company_info):
    """DuckDuckGo로 구글 검색"""

    all_variants = [company_name] + company_info.get('변형', [])
    investors = [company_info.get('투자자', ''), company_info.get('투자자2', ''), company_info.get('투자자3', '')]

    queries = []
    for variant in all_variants[:3]:
        for investor in investors:
            if investor:
                queries.append(f"{variant} {investor} 투자")

    for query in queries[:10]:
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            results = soup.find_all('a', class_='result__a')

            for result in results[:20]:
                href = result.get('href', '')
                text = result.get_text().strip()

                # 기업명 확인
                found = False
                for variant in all_variants:
                    if variant in text:
                        found = True
                        break

                if not found:
                    continue

                # 투자 키워드
                if not any(kw in text for kw in ['투자', '유치', '펀딩', '시리즈']):
                    continue

                # 뉴스 사이트
                news_domains = [
                    'wowtale.net', 'venturesquare.net', 'thebell.co.kr',
                    'platum.kr', 'startuptoday.kr', 'etnews.com',
                    'zdnet.co.kr', 'bloter.net', 'moneys.co.kr',
                    'etoday.co.kr', 'newstomato.com'
                ]

                if any(domain in href for domain in news_domains):
                    return {
                        'title': text,
                        'url': href,
                        'query': query
                    }

            time.sleep(1)

        except Exception as e:
            continue

    return None


def main():
    print("=" * 80)
    print("마지막 2개 기업 공격적 검색")
    print("=" * 80)

    found = 0
    not_found = []

    for idx, (company, info) in enumerate(last_2_companies.items(), 1):
        print(f"\n[{idx}/2] {company}")
        print(f"  투자자: {info['투자자']}")
        print(f"  주요사업: {info['주요사업']}")
        print(f"  검색 변형: {', '.join(info['변형'][:3])}...")

        # 네이버 검색
        print("\n  🔍 네이버 API 검색...")
        article, query = search_naver_aggressive(company, info)

        if not article:
            print("  ❌ 네이버에서 못 찾음")
            print("\n  🔍 DuckDuckGo 검색...")
            result = search_google_duckduckgo(company, info)

            if result:
                print(f"  ✅ 발견: {result['title'][:60]}...")
                print(f"  🔗 {result['url']}")

                # 사이트명 추출
                site_mapping = {
                    'wowtale.net': ('WOWTALE', 1),
                    'venturesquare.net': ('벤처스퀘어', 9),
                    'thebell.co.kr': ('더벨', 16),
                    'platum.kr': ('플래텀', 10),
                    'startuptoday.kr': ('스타트업투데이', 11),
                    'etnews.com': ('전자신문', 99),
                    'zdnet.co.kr': ('지디넷', 99),
                    'bloter.net': ('블로터', 22),
                    'moneys.co.kr': ('머니S', 99),
                    'etoday.co.kr': ('이투데이', 99),
                }

                site_name = "기타 뉴스"
                site_number = 99

                for domain, (name, num) in site_mapping.items():
                    if domain in result['url']:
                        site_name = name
                        site_number = num
                        break

                article = {
                    'site_number': site_number,
                    'site_name': site_name,
                    'site_url': '',
                    'article_title': result['title'],
                    'article_url': result['url'],
                    'published_date': datetime.now().strftime('%Y-%m-%d')
                }

        if article:
            print(f"  ✅ 발견: {article['article_title'][:60]}...")
            print(f"  🔎 검색어: {query if query else '구글 검색'}")
            print(f"  📰 [{article['site_name']}]")

            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if not existing.data:
                try:
                    supabase.table("investment_news_articles").insert(article).execute()
                    print(f"  💾 DB 저장 완료")
                    found += 1
                except Exception as e:
                    print(f"  ❌ DB 오류: {e}")
            else:
                print(f"  ⚠️  중복")
                found += 1
        else:
            print(f"  ❌ 최종 미발견")
            not_found.append(company)

        time.sleep(1)

    print(f"\n{'='*80}")
    print("검색 완료")
    print(f"{'='*80}")
    print(f"✅ 발견: {found}개")
    print(f"❌ 최종 미발견: {len(not_found)}개")

    if not_found:
        print(f"\n❌ 최종 미발견 기업:")
        for company in not_found:
            print(f"  - {company}")
    else:
        print(f"\n🎉 모든 기업 발견 완료!")

    # 최종 통계
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"\ninvestment_news_articles 테이블 총 레코드: {count_result.count}개")


if __name__ == '__main__':
    main()
