#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
못 찾은 6개 기업 최종 검색 (다양한 검색어 조합)
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

# 못 찾은 6개 기업 - 다양한 검색어 변형
companies_variants = {
    "부스티스": ["부스티스", "Boostis", "부스트이에스", "심리발달 검진"],
    "애플에이아이": ["애플에이아이", "애플AI", "Apple AI"],
    "스튜디오에피소드": ["스튜디오에피소드", "Studio Episode", "스튜디오 에피소드"],
    "비바트로로보틱스": ["비바트로로보틱스", "Vivatro Robotics", "비바트로"],
    "소셜릭스코리아": ["소셜릭스코리아", "Socialix Korea", "소셜릭스"],
    "스카이인텔리전스": ["스카이인텔리전스", "SKY Intelligence", "스카이 인텔리전스"]
}


def search_naver_variants(company_name, variants):
    """네이버 API - 여러 변형 검색어로 검색"""

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }

    # 모든 변형 시도
    for variant in variants:
        # 여러 검색 쿼리
        queries = [
            f"{variant} 투자유치",
            f"{variant} 투자",
            f"{variant} 시리즈",
            f"{variant} 펀딩",
            f"{variant} VC",
            variant
        ]

        for query in queries:
            params = {
                'query': query,
                'display': 50,
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

                        # 원래 기업명이나 변형 중 하나라도 포함
                        found = False
                        for v in variants:
                            if v in title:
                                found = True
                                break

                        if not found:
                            continue

                        # 투자 키워드
                        investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'VC', 'M&A', '인수']
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
                        }, variant, query

                time.sleep(0.1)

            except Exception as e:
                continue

    return None, None, None


def main():
    print("=" * 80)
    print("못 찾은 6개 기업 최종 검색 (다양한 검색어 변형)")
    print("=" * 80)

    found = 0
    duplicate = 0
    not_found = []

    for idx, (company, variants) in enumerate(companies_variants.items(), 1):
        print(f"\n[{idx}/6] {company:25s}")
        print(f"     변형: {', '.join(variants)}")

        # 변형 검색
        article, matched_variant, matched_query = search_naver_variants(company, variants)

        if article and article['article_url']:
            print(f"  ✅ 발견: {article['article_title'][:60]}...")
            print(f"  🔎 검색어: {matched_variant} - {matched_query}")
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
                except:
                    print(f"  ❌ DB 오류")
            else:
                print(f"  ⚠️  중복")
                duplicate += 1
        else:
            print(f"  ❌ 못 찾음")
            not_found.append(company)

        time.sleep(0.5)

    print(f"\n{'='*80}")
    print("최종 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 새로 발견: {found}개")
    print(f"⚠️ 중복: {duplicate}개")
    print(f"❌ 최종 미발견: {len(not_found)}개")
    print(f"{'='*80}")

    # 최종 통계
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"\ninvestment_news_articles 테이블 총 레코드: {count_result.count}개")

    if not_found:
        print(f"\n❌ 최종 미발견 기업 ({len(not_found)}개):")
        for company in not_found:
            print(f"  - {company}")
    else:
        print(f"\n🎉 모든 기업 수집 완료!")


if __name__ == '__main__':
    main()
