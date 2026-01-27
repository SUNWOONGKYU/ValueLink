#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
못 찾은 14개 기업 정확한 이름으로 최종 검색
"""

import os
import sys
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

# 정정된 기업명
corrected_companies = {
    "애플에이아이": "광림벤처스",
    "디엔티테크솔루션": "티진인베스트먼트",
    "엘리사젠": "데일리파트너스-NHF투자증권",
    "오픈웨딩": "월드플로라",
    "스튜디오에피소드": "캐리소프트",
    "부스티스": "SBI인베스트먼트",
    "투모로우": "SJ투자파트너스",
    "비바트로로보틱스": "카이스트홀딩스",
    "덱사스튜디오": "NC소프트",
    "한양로보틱스": "나우로보틱스",
    "소셜릭스코리아": "네이버 D2SF",
    "스카이인텔리전스": "SKAI월드와이드",
    "하이파이브랩": "DSRV",
}


def search_naver_news(company_name, investor_str):
    """네이버 API로 뉴스 검색"""

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    # 투자자 첫 단어 추출
    first_investor = investor_str.split()[0] if investor_str else ""

    # 여러 검색 쿼리 시도
    queries = []

    if first_investor:
        queries.append(f"{company_name} {first_investor}")
        queries.append(f"{company_name} {first_investor} 투자")

    queries.extend([
        f"{company_name} 투자유치",
        f"{company_name} 시리즈",
        f"{company_name} 펀딩",
    ])

    # 각 쿼리 시도
    for query in queries:
        params = {
            'query': query,
            'display': 30,
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
                    investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
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

            time.sleep(0.1)

        except Exception as e:
            continue

    return None, None


def main():
    print("=" * 80)
    print("못 찾은 14개 기업 정확한 이름으로 최종 검색")
    print("=" * 80)

    found = 0
    duplicate = 0
    not_found = []

    for idx, (company, investor) in enumerate(corrected_companies.items(), 1):
        print(f"[{idx:2d}/{len(corrected_companies)}] {company:25s} + {investor[:20]:20s}...", end=' ')

        # 네이버 검색
        article, matched_query = search_naver_news(company, investor)

        if article and article['article_url']:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if not existing.data:
                try:
                    supabase.table("investment_news_articles").insert(article).execute()
                    print(f"✅ [{article['site_name']}]")
                    found += 1
                except:
                    print(f"❌ DB 오류")
            else:
                print(f"⚠️ 중복")
                duplicate += 1
        else:
            print("❌ 못 찾음")
            not_found.append(company)

        time.sleep(0.12)

    print(f"\n{'='*80}")
    print("최종 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 새로 발견: {found}개")
    print(f"⚠️ 중복: {duplicate}개")
    print(f"❌ 여전히 못 찾음: {len(not_found)}개")
    print(f"{'='*80}")

    # 최종 통계
    print(f"\ninvestment_news_articles 테이블 총 레코드:")
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"  {count_result.count}개")

    if not_found:
        print(f"\n❌ 여전히 못 찾은 기업:")
        for company in not_found:
            print(f"  - {company}")


if __name__ == '__main__':
    main()
