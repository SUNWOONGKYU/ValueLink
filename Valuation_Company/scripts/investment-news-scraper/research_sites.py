#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Top 10 사이트 크롤링 방법 연구
- RSS 피드 확인
- 웹 구조 분석
- 실제 수집 가능 여부 테스트
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import json

SITES = [
    {'number': 1, 'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net', 'rss': 'https://www.venturesquare.net/feed'},
    {'number': 2, 'name': '스타트업투데이', 'url': 'https://startuptoday.kr', 'rss': None},
    {'number': 3, 'name': '아웃스탠딩', 'url': 'https://outstanding.kr', 'rss': 'https://outstanding.kr/feed'},
    {'number': 4, 'name': '더벨', 'url': 'https://www.thebell.co.kr', 'rss': None},
    {'number': 5, 'name': '더브이씨', 'url': 'https://thevc.kr', 'rss': None},
    {'number': 6, 'name': '스타트업엔', 'url': 'https://startupn.kr', 'rss': None},
    {'number': 7, 'name': '블로터', 'url': 'https://www.bloter.net', 'rss': 'https://www.bloter.net/feed'},
    {'number': 8, 'name': '이코노미스트', 'url': 'https://www.economist.co.kr', 'rss': None},
    {'number': 9, 'name': '플래텀', 'url': 'https://platum.kr', 'rss': 'https://platum.kr/feed'},
    {'number': 10, 'name': 'AI타임스', 'url': 'https://www.aitimes.com', 'rss': None},
]

def test_rss_feed(site):
    """RSS 피드 테스트"""
    if not site['rss']:
        return {'success': False, 'method': 'RSS', 'reason': 'RSS 피드 없음'}

    try:
        print(f"  RSS 테스트 중: {site['rss']}")
        feed = feedparser.parse(site['rss'])

        if feed.entries:
            sample = feed.entries[0]
            return {
                'success': True,
                'method': 'RSS',
                'count': len(feed.entries),
                'sample_title': sample.get('title', 'N/A')[:60],
                'sample_link': sample.get('link', 'N/A'),
                'sample_date': sample.get('published', 'N/A'),
            }
        else:
            return {'success': False, 'method': 'RSS', 'reason': '피드가 비어있음'}

    except Exception as e:
        return {'success': False, 'method': 'RSS', 'reason': str(e)}


def test_web_scraping(site):
    """웹 스크래핑 테스트"""
    try:
        print(f"  웹 스크래핑 테스트 중: {site['url']}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(site['url'], headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 다양한 선택자 시도
            selectors = [
                'article',
                '.article',
                '.post',
                '.news-item',
                '.entry',
                'h2 a',
                'h3 a',
                '.title a'
            ]

            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    return {
                        'success': True,
                        'method': 'Web Scraping',
                        'selector': selector,
                        'count': len(elements),
                        'sample': str(elements[0])[:100] if elements else 'N/A'
                    }

            return {
                'success': False,
                'method': 'Web Scraping',
                'reason': '적절한 선택자를 찾지 못함'
            }
        else:
            return {
                'success': False,
                'method': 'Web Scraping',
                'reason': f'HTTP {response.status_code}'
            }

    except Exception as e:
        return {
            'success': False,
            'method': 'Web Scraping',
            'reason': str(e)
        }


def research_all_sites():
    """모든 사이트 연구"""

    print("=" * 80)
    print("Top 10 투자 뉴스 사이트 크롤링 방법 연구")
    print("=" * 80)

    results = []

    for site in SITES:
        print(f"\n[{site['number']}] {site['name']} ({site['url']})")
        print("-" * 80)

        # RSS 테스트
        rss_result = test_rss_feed(site)

        if rss_result['success']:
            print(f"  [OK] RSS feed available!")
            print(f"     - Count: {rss_result['count']}")
            print(f"     - Sample: {rss_result['sample_title']}")
            results.append({
                'site': site['name'],
                'method': 'RSS',
                'status': 'SUCCESS',
                'details': rss_result
            })
        else:
            print(f"  [FAIL] RSS feed failed: {rss_result['reason']}")

            # 웹 스크래핑 테스트
            web_result = test_web_scraping(site)

            if web_result['success']:
                print(f"  [OK] Web scraping available!")
                print(f"     - Selector: {web_result['selector']}")
                print(f"     - Count: {web_result['count']}")
                results.append({
                    'site': site['name'],
                    'method': 'Web Scraping',
                    'status': 'SUCCESS',
                    'details': web_result
                })
            else:
                print(f"  [FAIL] Web scraping failed: {web_result['reason']}")
                results.append({
                    'site': site['name'],
                    'method': 'None',
                    'status': 'FAILED',
                    'details': web_result
                })

    # 결과 요약
    print("\n" + "=" * 80)
    print("연구 결과 요약")
    print("=" * 80)

    rss_sites = [r for r in results if r['method'] == 'RSS']
    web_sites = [r for r in results if r['method'] == 'Web Scraping']
    failed_sites = [r for r in results if r['status'] == 'FAILED']

    print(f"\n[RSS AVAILABLE] {len(rss_sites)} sites")
    for r in rss_sites:
        print(f"   - {r['site']}")

    print(f"\n[WEB SCRAPING AVAILABLE] {len(web_sites)} sites")
    for r in web_sites:
        print(f"   - {r['site']} (selector: {r['details'].get('selector', 'N/A')})")

    print(f"\n[FAILED] {len(failed_sites)} sites")
    for r in failed_sites:
        print(f"   - {r['site']}: {r['details'].get('reason', 'N/A')}")

    # JSON으로 저장
    with open('site_research_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVED] site_research_results.json")


if __name__ == '__main__':
    research_all_sites()
