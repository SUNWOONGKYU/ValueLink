#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 스크래퍼 - 최적화된 5개 미디어
"""

import csv
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


def safe_print(text, end='\n'):
    """인코딩 에러 방지 출력"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


# 최적화된 5개 뉴스 미디어 (11개 → 5개)
MEDIA_SITES = [
    {
        'name': 'WOWTALE',
        'search_url': 'https://www.wowtale.net/?s={keyword}',
        'link_selector': 'h2 a, h3 a',
        'priority': 1,  # 메인 소스 (76% 커버)
    },
    {
        'name': '벤처스퀘어',
        'search_url': 'https://www.venturesquare.net/?s={keyword}',
        'link_selector': 'h2.entry-title a, h3.entry-title a, a.post-title',
        'priority': 2,  # 서브 소스 (21% 커버)
    },
    {
        'name': '스타트업투데이',
        'search_url': 'https://www.startuptoday.kr/news/articleList.html?sc_area=A&view_type=sm&sc_word={keyword}',
        'link_selector': 'div.list-titles a, h4.titles a',
        'priority': 3,  # 틈새 소스 (2% 커버)
    },
    {
        'name': '아웃스탠딩',
        'search_url': 'https://outstanding.kr/?s={keyword}',
        'link_selector': 'h2 a, h3 a, a.article-link',
        'priority': 4,  # 심층 분석, 확장용
    },
    {
        'name': '플래텀',
        'search_url': 'https://platum.kr/?s={keyword}',
        'link_selector': 'h2.entry-title a, div.post-title a',
        'priority': 5,  # 해외 뉴스, 확장용
    },
]


def search_in_media(company_name):
    """
    5개 미디어에서 투자 뉴스 검색

    우선순위:
    1. WOWTALE (메인, 76% 커버)
    2. 벤처스퀘어 (서브, 21% 커버)
    3. 스타트업투데이 (틈새, 2% 커버)
    4. 아웃스탠딩 (확장)
    5. 플래텀 (확장)
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/',
    }

    keyword = quote(company_name)

    # 우선순위 순서로 검색
    for site in sorted(MEDIA_SITES, key=lambda x: x['priority']):
        try:
            search_url = site['search_url'].format(keyword=keyword)

            response = requests.get(search_url, headers=headers, timeout=8)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # 검색 결과 링크 찾기
                for selector in site['link_selector'].split(','):
                    links = soup.select(selector.strip())

                    for link in links[:5]:  # 상위 5개만
                        title = link.get_text(strip=True)
                        url = link.get('href', '')

                        # 투자 관련 키워드 확인
                        investment_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드']
                        if any(kw in title for kw in investment_keywords):
                            # 상대 경로면 절대 경로로 변환
                            if url.startswith('/'):
                                base_url = site['search_url'].split('?')[0].rsplit('/', 1)[0]
                                url = base_url + url

                            if url.startswith('http'):
                                return url, site['name']

            time.sleep(0.2)  # 사이트 부하 방지

        except Exception as e:
            continue

    return None, None


def scrape_companies(input_file, output_file):
    """기업 목록에서 뉴스 URL 수집"""

    print("=" * 70)
    print("투자 뉴스 스크래퍼 (5개 미디어)")
    print("=" * 70)

    # 소스 목록 출력
    print("\n📰 검색 소스:")
    for idx, site in enumerate(sorted(MEDIA_SITES, key=lambda x: x['priority']), 1):
        print(f"  {idx}. {site['name']}")

    print("\n" + "=" * 70)

    # CSV 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    total = len(companies)
    safe_print(f"\n총 기업 수: {total}개\n")

    found_count = 0
    results = []

    for idx, company in enumerate(companies, 1):
        company_name = company['기업명']

        safe_print(f"[{idx}/{total}] {company_name}...", end=" ")

        news_url, source_name = search_in_media(company_name)

        if news_url:
            company['뉴스URL'] = news_url
            company['뉴스소스'] = source_name
            found_count += 1
            safe_print(f"✅ [{source_name}]")
        else:
            company['뉴스URL'] = ''
            company['뉴스소스'] = ''
            safe_print("❌")

        results.append(company)

    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    # 통계
    print("\n" + "=" * 70)
    print("수집 완료")
    print("=" * 70)
    print(f"✅ 발견: {found_count}개")
    print(f"❌ 미발견: {total - found_count}개")
    print(f"📊 성공률: {found_count * 100 / total:.1f}%")

    # 소스별 통계
    source_stats = {}
    for company in results:
        source = company.get('뉴스소스', '')
        if source:
            source_stats[source] = source_stats.get(source, 0) + 1

    if source_stats:
        print("\n📰 소스별 발견 수:")
        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {source}: {count}개 ({count * 100 / found_count:.1f}%)")

    print("=" * 70)


def main():
    """메인 함수"""

    if len(sys.argv) < 3:
        print("사용법: python news_scraper_5sources.py <입력파일> <출력파일>")
        print("\n예시:")
        print("  python news_scraper_5sources.py companies.csv results.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        scrape_companies(input_file, output_file)
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
