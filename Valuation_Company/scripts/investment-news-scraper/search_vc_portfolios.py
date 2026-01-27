#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주요 VC 포트폴리오에서 못 찾은 13개 기업 검색
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 못 찾은 13개 기업과 투자자
missing_companies = {
    "애플에이아이": "광림벤처스",
    "디엔티테크솔루션": "티진인베스트먼트",
    "엘리사젠": "데일리파트너스",
    "오픈웨딩": "월드플로라",
    "스튜디오에피소드": "캐리소프트",
    "부스티스": "SBI인베스트먼트",
    "투모로우": "SJ투자파트너스",
    "비바트로로보틱스": "카이스트홀딩스",
    "덱사스튜디오": "NC소프트",
    "한양로보틱스": "나우로보틱스",
    "소셜릭스코리아": "네이버",
    "스카이인텔리전스": "SKAI월드와이드",
    "하이파이브랩": "DSRV"
}

# 주요 VC 포트폴리오 URL
VC_PORTFOLIOS = {
    "알토스벤처스": "https://www.altos.vc/portfolio",
    "블루포인트파트너스": "https://bluepoint.vc/portfolio",
    "스톤브릿지벤처스": "https://www.stonebridge.vc/portfolio",
    "KB인베스트먼트": "https://www.kbi.co.kr/portfolio",
    "본엔젤스": "https://www.bonangels.net/portfolio",
}


def search_google_for_vc_portfolio(company_name, vc_name):
    """구글 검색으로 VC 포트폴리오 페이지 찾기"""

    query = f"{company_name} {vc_name} 투자 포트폴리오"

    # Google Custom Search API 사용 (있다면)
    # 또는 간단하게 DuckDuckGo HTML 검색

    search_url = f"https://html.duckduckgo.com/html/?q={query}"

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # DuckDuckGo 검색 결과 링크
        results = soup.find_all('a', class_='result__a')

        for result in results[:5]:  # 상위 5개만
            href = result.get('href', '')
            title = result.get_text().strip()

            # 투자 관련 키워드 확인
            if any(kw in title for kw in ['투자', '유치', '펀딩', 'portfolio']):
                # thevc, 뉴스 사이트 링크만
                if any(domain in href for domain in ['thevc.kr', 'venturesquare', 'platum', 'wowtale', 'outstanding']):
                    return {
                        'url': href,
                        'title': title
                    }

        return None

    except Exception as e:
        return None


def main():
    print("=" * 80)
    print("VC 포트폴리오에서 못 찾은 13개 기업 검색")
    print("=" * 80)

    found = 0
    not_found = []

    for idx, (company, vc) in enumerate(missing_companies.items(), 1):
        print(f"\n[{idx:2d}/13] {company:25s} (투자: {vc})")

        # 구글 검색으로 VC 포트폴리오 찾기
        result = search_google_for_vc_portfolio(company, vc)

        if result:
            print(f"  ✅ 발견: {result['title'][:50]}...")
            print(f"  🔗 {result['url']}")

            # DB에 저장 시도
            article = {
                'site_number': 99,
                'site_name': 'VC 포트폴리오',
                'site_url': "",
                'article_title': result['title'],
                'article_url': result['url'],
                'published_date': datetime.now().strftime('%Y-%m-%d')
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
            print(f"  ❌ 못 찾음")
            not_found.append(company)

        time.sleep(2)  # 검색 간격

    print(f"\n{'='*80}")
    print("VC 포트폴리오 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 발견: {found}개")
    print(f"❌ 못 찾음: {len(not_found)}개")

    if not_found:
        print(f"\n❌ VC 포트폴리오에서도 못 찾은 기업:")
        for company in not_found:
            print(f"  - {company}")


if __name__ == '__main__':
    main()
