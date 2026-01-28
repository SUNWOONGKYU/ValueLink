#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
추가 언론사에서 못 찾은 3개 기업 검색
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

# 못 찾은 3개 기업
target_companies = {
    "부스티스": "SBI인베스트먼트",
    "애플에이아이": "광림벤처스",
    "소셜릭스코리아": "네이버 D2SF"
}

# 추가 언론사
ADDITIONAL_MEDIA = {
    "더벨": {
        "number": 16,
        "search_url": "https://www.thebell.co.kr/search/result.asp?search_key={}",
        "domain": "thebell.co.kr"
    },
    "블로터": {
        "number": 22,
        "search_url": "https://www.bloter.net/?s={}",
        "domain": "bloter.net"
    },
    "지디넷코리아": {
        "number": 99,
        "search_url": "https://zdnet.co.kr/search/?query={}",
        "domain": "zdnet.co.kr"
    },
    "전자신문": {
        "number": 99,
        "search_url": "https://www.etnews.com/search?kw={}",
        "domain": "etnews.com"
    },
    "이코노미스트": {
        "number": 23,
        "search_url": "https://economist.co.kr/?s={}",
        "domain": "economist.co.kr"
    },
    "AI타임스": {
        "number": 19,
        "search_url": "https://www.aitimes.com/search/search.html?kwd={}",
        "domain": "aitimes.com"
    }
}


def search_media_site(media_name, media_info, company_name, investor):
    """각 언론사 사이트 내 검색"""

    # 검색 쿼리
    queries = [
        f"{company_name} {investor} 투자",
        f"{company_name} 투자유치",
        f"{company_name} 펀딩"
    ]

    for query in queries:
        search_url = media_info['search_url'].format(quote(query))

        try:
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 모든 링크 검색
            links = soup.find_all('a', href=True)

            for link in links:
                href = link.get('href', '')
                text = link.get_text().strip()

                # 기업명 확인
                if company_name not in text:
                    continue

                # 투자 키워드 확인
                investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
                if not any(kw in text for kw in investment_keywords):
                    continue

                # 해당 언론사 도메인 확인
                if media_info['domain'] in href or href.startswith('/'):
                    # 절대 URL 변환
                    if href.startswith('/'):
                        base_url = f"https://{media_info['domain']}"
                        href = base_url + href

                    return {
                        'title': text,
                        'url': href,
                        'query': query
                    }

            time.sleep(0.5)

        except Exception as e:
            continue

    return None


def main():
    print("=" * 80)
    print("추가 언론사에서 못 찾은 3개 기업 검색")
    print("=" * 80)
    print(f"\n🎯 타겟: {', '.join(target_companies.keys())}\n")

    total_found = 0
    total_duplicate = 0
    found_companies = set()

    for company, investor in target_companies.items():
        print(f"\n{'='*80}")
        print(f"🔍 {company} (투자: {investor})")
        print(f"{'='*80}")

        for media_name, media_info in ADDITIONAL_MEDIA.items():
            print(f"\n  [{media_name}] 검색 중...", end=' ')

            result = search_media_site(media_name, media_info, company, investor)

            if result:
                print(f"\n  ✅ 발견!")
                print(f"     제목: {result['title'][:60]}...")
                print(f"     URL: {result['url']}")
                print(f"     검색어: {result['query']}")

                # DB 저장
                article = {
                    'site_number': media_info['number'],
                    'site_name': media_name,
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
                        print(f"     💾 DB 저장 완료")
                        total_found += 1
                        found_companies.add(company)
                        break  # 하나 찾으면 다음 기업으로
                    except:
                        print(f"     ❌ DB 오류")
                else:
                    print(f"     ⚠️  중복")
                    total_duplicate += 1
                    found_companies.add(company)
                    break
            else:
                print("못 찾음")

        time.sleep(1)

    print(f"\n{'='*80}")
    print("추가 언론사 검색 완료")
    print(f"{'='*80}")
    print(f"✅ 새로 발견: {total_found}개")
    print(f"⚠️  중복: {total_duplicate}개")
    print(f"{'='*80}")

    if found_companies:
        print(f"\n🎉 발견된 기업:")
        for company in found_companies:
            print(f"  ✅ {company}")

    not_found = set(target_companies.keys()) - found_companies
    if not_found:
        print(f"\n❌ 최종 미발견 기업 ({len(not_found)}개):")
        for company in not_found:
            print(f"  - {company}")
    else:
        print(f"\n🎉🎉🎉 모든 기업 발견 완료!")

    # 최종 통계
    count_result = supabase.table("investment_news_articles").select("id", count="exact").execute()
    print(f"\ninvestment_news_articles 테이블 총 레코드: {count_result.count}개")


if __name__ == '__main__':
    main()
