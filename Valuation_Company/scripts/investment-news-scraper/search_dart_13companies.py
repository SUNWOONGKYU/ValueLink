#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
금융감독원 DART에서 못 찾은 13개 기업 검색 (주로 M&A 건)
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

# DART API 키 (없으면 OpenDart 웹사이트에서 발급)
DART_API_KEY = os.getenv("DART_API_KEY", "")

# M&A 건 위주로 검색 (4개)
ma_companies = [
    "스튜디오에피소드",
    "한양로보틱스",
    "스카이인텔리전스",
    "하이파이브랩"
]

# 나머지 기업들도 검색
other_companies = [
    "애플에이아이",
    "디엔티테크솔루션",
    "엘리사젠",
    "오픈웨딩",
    "부스티스",
    "투모로우",
    "비바트로로보틱스",
    "덱사스튜디오",
    "소셜릭스코리아"
]


def search_dart(company_name):
    """DART Open API로 기업 검색"""

    if not DART_API_KEY:
        return None

    # DART 공시검색 API
    url = "https://opendart.fss.or.kr/api/list.json"

    params = {
        'crtfc_key': DART_API_KEY,
        'corp_name': company_name,
        'bgn_de': '20250101',  # 2025년 1월부터
        'pblntf_ty': 'A',  # 정기공시
        'page_no': 1,
        'page_count': 10
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data['status'] == '000':  # 정상
                items = data.get('list', [])

                for item in items:
                    # 투자, M&A 관련 공시
                    if any(kw in item['report_nm'] for kw in ['투자', '인수', '합병', 'M&A', '지분취득']):
                        return {
                            'title': item['report_nm'],
                            'url': f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}",
                            'date': item['rcept_dt']
                        }

        return None

    except Exception as e:
        return None


def search_dart_web(company_name):
    """DART 웹사이트 검색 (API 없을 때)"""

    # 간단한 웹 검색
    search_url = f"https://dart.fss.or.kr/dsab001/search.ax"

    # 실제로는 POST 요청이 필요하지만, 간단하게 구글 검색 활용
    google_query = f"site:dart.fss.or.kr {company_name} 투자"

    # 또는 네이버 검색으로 DART 공시 찾기
    naver_query = f"{company_name} DART 공시 투자"

    # 여기서는 간단하게 None 반환 (API가 더 정확)
    return None


def main():
    print("=" * 80)
    print("금융감독원 DART에서 못 찾은 13개 기업 검색")
    print("=" * 80)

    if not DART_API_KEY:
        print("\n⚠️  DART API 키가 없습니다.")
        print("   https://opendart.fss.or.kr/ 에서 API 키를 발급받으세요.")
        print("   .env 파일에 DART_API_KEY=your_key 추가\n")

    all_companies = ma_companies + other_companies

    found = 0
    not_found = []

    for idx, company in enumerate(all_companies, 1):
        is_ma = company in ma_companies
        print(f"\n[{idx:2d}/13] {company:25s} {'(M&A)' if is_ma else ''}")

        # DART 검색
        result = search_dart(company)

        if result:
            print(f"  ✅ DART 공시 발견: {result['title'][:50]}...")
            print(f"  📅 {result['date']}")
            print(f"  🔗 {result['url']}")

            # DB에 저장 시도
            article = {
                'site_number': 99,
                'site_name': 'DART 공시',
                'site_url': "",
                'article_title': result['title'],
                'article_url': result['url'],
                'published_date': result['date']
            }

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
                    print(f"  ❌ DB 저장 실패")
            else:
                print(f"  ⚠️  이미 DB에 있음")
        else:
            print(f"  ❌ DART에서 못 찾음")
            not_found.append(company)

        time.sleep(0.5)

    print(f"\n{'='*80}")
    print("DART 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 발견: {found}개")
    print(f"❌ 못 찾음: {len(not_found)}개")

    if not_found:
        print(f"\n❌ DART에서도 못 찾은 기업:")
        for company in not_found:
            print(f"  - {company}")


if __name__ == '__main__':
    main()
