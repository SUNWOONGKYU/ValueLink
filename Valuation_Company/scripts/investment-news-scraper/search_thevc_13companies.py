#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theVC.kr에서 못 찾은 13개 기업 검색
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

# 못 찾은 13개 기업
missing_companies = [
    "애플에이아이",
    "디엔티테크솔루션",
    "엘리사젠",
    "오픈웨딩",
    "스튜디오에피소드",
    "부스티스",
    "투모로우",
    "비바트로로보틱스",
    "덱사스튜디오",
    "한양로보틱스",
    "소셜릭스코리아",
    "스카이인텔리전스",
    "하이파이브랩"
]


def search_thevc(company_name):
    """theVC.kr에서 기업 검색"""

    # theVC 검색 URL
    search_url = f"https://thevc.kr/search?q={company_name}"

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 검색 결과에서 기업 링크 찾기
        # theVC 구조: 기업명 링크가 있으면 해당 페이지로
        links = soup.find_all('a', href=True)

        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()

            # 기업 페이지 링크 찾기
            if '/organizations/' in href and company_name in text:
                org_url = f"https://thevc.kr{href}" if href.startswith('/') else href
                return org_url

        return None

    except Exception as e:
        print(f"    오류: {e}")
        return None


def get_investment_info_from_thevc(org_url):
    """theVC 기업 페이지에서 투자 정보 추출"""

    try:
        response = requests.get(org_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # theVC 페이지 구조 분석 후 투자 정보 추출
        # (실제 구조에 맞게 수정 필요)

        # 최근 투자 뉴스 링크 찾기
        news_links = soup.find_all('a', href=True)

        for link in news_links:
            href = link.get('href', '')
            text = link.get_text().strip()

            # 투자 관련 키워드
            if any(kw in text for kw in ['투자', '유치', '펀딩', '시리즈', 'Series']):
                # 외부 뉴스 링크면 반환
                if href.startswith('http') and 'thevc.kr' not in href:
                    return {
                        'url': href,
                        'title': text
                    }

        return None

    except Exception as e:
        return None


def main():
    print("=" * 80)
    print("theVC.kr에서 못 찾은 13개 기업 검색")
    print("=" * 80)

    found = 0
    not_found = []

    for idx, company in enumerate(missing_companies, 1):
        print(f"\n[{idx:2d}/13] {company:25s}")

        # theVC 검색
        org_url = search_thevc(company)

        if org_url:
            print(f"  ✅ theVC 페이지 발견: {org_url}")

            # 투자 정보 추출
            investment_info = get_investment_info_from_thevc(org_url)

            if investment_info:
                print(f"  📰 뉴스 발견: {investment_info['title'][:50]}...")
                print(f"  🔗 {investment_info['url']}")

                # DB에 저장 시도
                article = {
                    'site_number': 99,
                    'site_name': 'theVC 검색',
                    'site_url': "",
                    'article_title': investment_info['title'],
                    'article_url': investment_info['url'],
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
                print(f"  ❌ 투자 뉴스 못 찾음")
                not_found.append(company)
        else:
            print(f"  ❌ theVC에서 못 찾음")
            not_found.append(company)

        time.sleep(1)

    print(f"\n{'='*80}")
    print("theVC 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 발견: {found}개")
    print(f"❌ 못 찾음: {len(not_found)}개")

    if not_found:
        print(f"\n❌ theVC에서도 못 찾은 기업:")
        for company in not_found:
            print(f"  - {company}")


if __name__ == '__main__':
    main()
