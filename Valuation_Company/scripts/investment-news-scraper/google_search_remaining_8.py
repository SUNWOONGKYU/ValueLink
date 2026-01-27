#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
구글 검색으로 남은 8개 기업 뉴스 찾기
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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 남은 8개 기업
remaining_companies = {
    "애플에이아이": "광림벤처스",
    "스튜디오에피소드": "케리소프트",
    "부스티스": "SBI인베스트먼트",
    "비바트로로보틱스": "카이스트홀딩스",
    "덱사스튜디오": "NC소프트",
    "한양로보틱스": "나우로보틱스",
    "소셜릭스코리아": "네이버",
    "스카이인텔리전스": "SKAI월드와이드"
}


def google_search_via_duckduckgo(company_name, investor):
    """DuckDuckGo HTML 검색으로 구글 결과 가져오기"""

    # 여러 검색 쿼리 시도
    queries = [
        f"{company_name} {investor} 투자유치",
        f"{company_name} {investor} 투자",
        f"{company_name} 투자 뉴스",
        f"{company_name} 시리즈 투자",
        f"{company_name} 펀딩",
    ]

    for query in queries:
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # DuckDuckGo 검색 결과
            results = soup.find_all('a', class_='result__a')

            for result in results[:10]:  # 상위 10개
                href = result.get('href', '')
                title = result.get_text().strip()

                # 기업명 확인
                if company_name not in title:
                    continue

                # 투자 키워드 확인
                if not any(kw in title for kw in ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']):
                    continue

                # 뉴스 사이트만
                news_domains = [
                    'venturesquare.net', 'wowtale.net', 'platum.kr',
                    'outstanding.kr', 'startuptoday.kr', 'thebell.co.kr',
                    'zdnet.co.kr', 'etnews.com', 'bloter.net',
                    'techcrunch.com', 'venturebeat.com'
                ]

                if any(domain in href for domain in news_domains):
                    # DuckDuckGo redirect URL 처리
                    if 'duckduckgo.com/l/' in href:
                        # 실제 URL 추출 시도
                        try:
                            redirect_response = requests.get(f"https:{href}", allow_redirects=True, timeout=5)
                            actual_url = redirect_response.url
                        except:
                            actual_url = href
                    else:
                        actual_url = href

                    return {
                        'title': title,
                        'url': actual_url,
                        'query': query
                    }

            time.sleep(1)

        except Exception as e:
            continue

    return None


def google_search_direct(company_name, investor):
    """구글 직접 검색 (간단한 scraping)"""

    query = f"{company_name} {investor} 투자유치 뉴스"
    url = f"https://www.google.com/search?q={quote(query)}&num=20"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 구글 검색 결과 링크
        links = soup.find_all('a')

        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()

            # /url?q= 패턴
            if '/url?q=' in href:
                # 실제 URL 추출
                start = href.find('/url?q=') + 7
                end = href.find('&', start)
                if end == -1:
                    actual_url = href[start:]
                else:
                    actual_url = href[start:end]

                # 기업명 확인
                if company_name not in text:
                    continue

                # 투자 키워드
                if not any(kw in text for kw in ['투자', '유치', '펀딩', '시리즈']):
                    continue

                # 뉴스 사이트만
                news_domains = [
                    'venturesquare.net', 'wowtale.net', 'platum.kr',
                    'outstanding.kr', 'startuptoday.kr', 'thebell.co.kr',
                    'zdnet.co.kr', 'etnews.com', 'bloter.net'
                ]

                if any(domain in actual_url for domain in news_domains):
                    return {
                        'title': text,
                        'url': actual_url,
                        'query': query
                    }

    except Exception as e:
        pass

    return None


def main():
    print("=" * 80)
    print("구글 검색으로 남은 8개 기업 재탐색")
    print("=" * 80)

    found = 0
    duplicate = 0
    not_found = []

    for idx, (company, investor) in enumerate(remaining_companies.items(), 1):
        print(f"\n[{idx}/8] {company:25s} + {investor}")

        # DuckDuckGo 검색 시도
        print(f"  🔍 DuckDuckGo 검색 중...", end=' ')
        result = google_search_via_duckduckgo(company, investor)

        # DuckDuckGo 실패 시 구글 직접 검색
        if not result:
            print("실패")
            print(f"  🔍 구글 직접 검색 중...", end=' ')
            result = google_search_direct(company, investor)

        if result:
            print(f"\n  ✅ 발견: {result['title'][:60]}...")
            print(f"  🔗 {result['url']}")
            print(f"  🔎 검색어: {result['query']}")

            # 사이트명 추출
            site_mapping = {
                'venturesquare.net': ('벤처스퀘어', 9),
                'wowtale.net': ('WOWTALE', 1),
                'platum.kr': ('플래텀', 10),
                'outstanding.kr': ('아웃스탠딩', 13),
                'startuptoday.kr': ('스타트업투데이', 11),
                'thebell.co.kr': ('더벨', 16),
                'zdnet.co.kr': ('지디넷', 99),
                'etnews.com': ('전자신문', 99),
                'bloter.net': ('블로터', 22),
            }

            site_name = "구글 검색"
            site_number = 99

            for domain, (name, num) in site_mapping.items():
                if domain in result['url']:
                    site_name = name
                    site_number = num
                    break

            # DB 저장
            article = {
                'site_number': site_number,
                'site_name': site_name,
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
                except Exception as e:
                    print(f"  ❌ DB 오류: {e}")
            else:
                print(f"  ⚠️  중복")
                duplicate += 1
        else:
            print("실패")
            print(f"  ❌ 못 찾음")
            not_found.append(company)

        time.sleep(2)  # 검색 간격

    print(f"\n{'='*80}")
    print("구글 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 새로 발견: {found}개")
    print(f"⚠️ 중복: {duplicate}개")
    print(f"❌ 여전히 못 찾음: {len(not_found)}개")
    print(f"{'='*80}")

    # 최종 통계
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"\ninvestment_news_articles 테이블 총 레코드: {count_result.count}개")

    if not_found:
        print(f"\n❌ 최종 미발견 기업 ({len(not_found)}개):")
        for company in not_found:
            print(f"  - {company}")


if __name__ == '__main__':
    main()
