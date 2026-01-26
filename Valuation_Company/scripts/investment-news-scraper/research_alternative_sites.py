#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
더벨 대체 사이트 후보 연구
"""

import requests
import feedparser
from bs4 import BeautifulSoup

# 대체 후보 사이트들
CANDIDATE_SITES = [
    {'name': '넥스트유니콘', 'url': 'https://www.nextunicorn.kr', 'rss': None},
    {'name': '비석세스', 'url': 'https://besuccess.com', 'rss': 'https://besuccess.com/feed'},
    {'name': '더스쿠프', 'url': 'https://www.thescoop.co.kr', 'rss': None},
    {'name': '한경 스타트업', 'url': 'https://www.hankyung.com/economy/startup', 'rss': None},
    {'name': '매경 스타트업', 'url': 'https://www.mk.co.kr/news/it/', 'rss': None},
    {'name': '디지털데일리', 'url': 'https://www.ddaily.co.kr', 'rss': None},
    {'name': 'ZDNet Korea', 'url': 'https://zdnet.co.kr', 'rss': None},
    {'name': '뉴스핌', 'url': 'https://www.newspim.com', 'rss': None},
    {'name': 'IT조선', 'url': 'https://it.chosun.com', 'rss': None},
    {'name': '디지털타임스', 'url': 'https://www.dt.co.kr', 'rss': None},
]


def test_site(site):
    """사이트 테스트"""
    print(f"\n{site['name']} ({site['url']})")
    print("-" * 60)

    result = {'name': site['name'], 'url': site['url']}

    # RSS 테스트
    if site['rss']:
        try:
            feed = feedparser.parse(site['rss'])
            if feed.entries:
                result['rss'] = 'OK'
                result['rss_count'] = len(feed.entries)
                result['rss_sample'] = feed.entries[0].title[:60] if feed.entries else 'N/A'
                print(f"  [RSS OK] {len(feed.entries)} entries")
                print(f"  Sample: {result['rss_sample']}")
            else:
                result['rss'] = 'EMPTY'
                print(f"  [RSS EMPTY]")
        except Exception as e:
            result['rss'] = 'FAIL'
            print(f"  [RSS FAIL] {str(e)[:50]}")
    else:
        result['rss'] = 'N/A'

    # 웹 접속 테스트
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(site['url'], headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 투자 관련 키워드 검색
            text = soup.get_text()
            investment_keywords = ['투자', '유치', '시리즈', '펀딩', '스타트업']
            keyword_counts = sum(text.count(kw) for kw in investment_keywords)

            result['web_access'] = 'OK'
            result['keyword_count'] = keyword_counts

            # 기사 요소 찾기
            selectors = ['article', '.article', '.news-item', 'h2 a', 'h3 a']
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    result['selector'] = selector
                    result['element_count'] = len(elements)
                    break

            print(f"  [WEB OK] Keywords: {keyword_counts}, Selector: {result.get('selector', 'N/A')}")
        else:
            result['web_access'] = f'HTTP {response.status_code}'
            print(f"  [WEB FAIL] {response.status_code}")

    except Exception as e:
        result['web_access'] = 'FAIL'
        print(f"  [WEB FAIL] {str(e)[:50]}")

    return result


def main():
    print("=" * 80)
    print("더벨 대체 사이트 후보 연구")
    print("=" * 80)

    results = []

    for site in CANDIDATE_SITES:
        result = test_site(site)
        results.append(result)

    # 결과 정리
    print("\n" + "=" * 80)
    print("연구 결과")
    print("=" * 80)

    # RSS 가능한 사이트
    rss_sites = [r for r in results if r.get('rss') == 'OK']
    print(f"\n[RSS AVAILABLE] {len(rss_sites)} sites")
    for r in rss_sites:
        print(f"  - {r['name']}: {r['rss_count']} entries")

    # 웹 스크래핑 가능한 사이트
    web_sites = [r for r in results if r.get('web_access') == 'OK' and r.get('selector')]
    print(f"\n[WEB SCRAPING POSSIBLE] {len(web_sites)} sites")
    for r in web_sites:
        print(f"  - {r['name']}: {r.get('selector', 'N/A')} ({r.get('element_count', 0)} elements)")
        print(f"    Keywords: {r.get('keyword_count', 0)}")

    # 추천 순위
    print(f"\n[RECOMMENDATION]")
    # RSS 있는 사이트 우선
    for r in rss_sites:
        print(f"  1. {r['name']} (RSS available)")

    # 투자 키워드 많은 사이트
    web_sorted = sorted(web_sites, key=lambda x: x.get('keyword_count', 0), reverse=True)
    for r in web_sorted[:3]:
        print(f"  2. {r['name']} (Keywords: {r.get('keyword_count', 0)})")


if __name__ == '__main__':
    main()
