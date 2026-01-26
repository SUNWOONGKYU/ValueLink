#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sitemap.xml을 활용한 전체 기사 URL 수집
- RSS 제한 우회
- 1월 전체 기간 기사 수집 가능
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time

# 10개 소스 Sitemap URL
SOURCES_SITEMAP = [
    {
        'source_number': 9,
        'source_name': '벤처스퀘어',
        'sitemap_url': 'https://www.venturesquare.net/sitemap.xml',
        'base_url': 'https://www.venturesquare.net'
    },
    {
        'source_number': 10,
        'source_name': '플래텀',
        'sitemap_url': 'https://platum.kr/sitemap.xml',
        'base_url': 'https://platum.kr'
    },
    {
        'source_number': 13,
        'source_name': '아웃스탠딩',
        'sitemap_url': 'https://outstanding.kr/sitemap.xml',
        'base_url': 'https://outstanding.kr'
    },
    {
        'source_number': 14,
        'source_name': '비석세스',
        'sitemap_url': 'https://besuccess.com/sitemap.xml',
        'base_url': 'https://besuccess.com'
    },
    {
        'source_number': 11,
        'source_name': '스타트업투데이',
        'sitemap_url': 'https://startuptoday.kr/sitemap.xml',
        'base_url': 'https://startuptoday.kr'
    },
    {
        'source_number': 12,
        'source_name': '스타트업엔',
        'sitemap_url': 'https://startupn.kr/sitemap.xml',
        'base_url': 'https://startupn.kr'
    },
    {
        'source_number': 19,
        'source_name': 'AI타임스',
        'sitemap_url': 'https://www.aitimes.com/sitemap.xml',
        'base_url': 'https://www.aitimes.com'
    },
    {
        'source_number': 21,
        'source_name': '넥스트유니콘',
        'sitemap_url': 'https://www.nextunicorn.kr/sitemap.xml',
        'base_url': 'https://www.nextunicorn.kr'
    },
    {
        'source_number': 22,
        'source_name': '블로터',
        'sitemap_url': 'https://www.bloter.net/sitemap.xml',
        'base_url': 'https://www.bloter.net'
    },
    {
        'source_number': 23,
        'source_name': '이코노미스트',
        'sitemap_url': 'https://www.economist.co.kr/sitemap.xml',
        'base_url': 'https://www.economist.co.kr'
    }
]


def parse_sitemap(sitemap_url, start_date, end_date):
    """
    Sitemap.xml 파싱하여 기간 내 URL 추출

    Args:
        sitemap_url: Sitemap URL
        start_date: 시작일 (datetime.date)
        end_date: 종료일 (datetime.date)

    Returns:
        list of {'url': ..., 'lastmod': ...}
    """

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(sitemap_url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"  [ERROR] HTTP {response.status_code}")
            return []

        # XML 파싱
        root = ET.fromstring(response.content)

        # Namespace 처리
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = []

        # 1단계: sitemap index인지 확인 (sitemap의 sitemap)
        sitemaps = root.findall('.//ns:sitemap', namespace)

        if sitemaps:
            # Sitemap index - 각 sitemap을 재귀적으로 파싱
            print(f"  [INFO] Found {len(sitemaps)} sub-sitemaps")

            for sitemap_elem in sitemaps:
                loc = sitemap_elem.find('ns:loc', namespace)
                if loc is not None:
                    sub_sitemap_url = loc.text
                    # 재귀 호출
                    sub_urls = parse_sitemap(sub_sitemap_url, start_date, end_date)
                    urls.extend(sub_urls)
                    time.sleep(0.5)

            return urls

        # 2단계: 일반 sitemap - URL 추출
        url_entries = root.findall('.//ns:url', namespace)

        for url_elem in url_entries:
            loc = url_elem.find('ns:loc', namespace)
            lastmod = url_elem.find('ns:lastmod', namespace)

            if loc is None:
                continue

            url = loc.text

            # 날짜 필터링
            if lastmod is not None:
                lastmod_text = lastmod.text

                # ISO 8601 형식 파싱 (2026-01-15 또는 2026-01-15T10:30:00+00:00)
                try:
                    if 'T' in lastmod_text:
                        lastmod_date = datetime.fromisoformat(lastmod_text.replace('Z', '+00:00')).date()
                    else:
                        lastmod_date = datetime.strptime(lastmod_text, '%Y-%m-%d').date()

                    # 기간 체크
                    if lastmod_date < start_date or lastmod_date > end_date:
                        continue

                except Exception as e:
                    # 날짜 파싱 실패 시 포함
                    pass

            urls.append({
                'url': url,
                'lastmod': lastmod.text if lastmod is not None else None
            })

        return urls

    except Exception as e:
        print(f"  [ERROR] Sitemap parsing failed: {str(e)[:100]}")
        return []


def collect_urls_from_all_sitemaps():
    """모든 소스의 Sitemap에서 1월 기사 URL 수집"""

    print("="*60)
    print("Collecting from Sitemaps (1월 전체)")
    print("="*60)

    # 1월 1일 ~ 오늘
    start_date = datetime(2026, 1, 1).date()
    end_date = datetime.now().date()

    print(f"\nPeriod: {start_date} ~ {end_date}")
    print(f"Sources: {len(SOURCES_SITEMAP)}")
    print()

    all_results = {}

    for source in SOURCES_SITEMAP:
        print(f"\n[{source['source_name']}]")
        print(f"  Sitemap: {source['sitemap_url']}")

        urls = parse_sitemap(source['sitemap_url'], start_date, end_date)

        print(f"  Found {len(urls)} URLs in Jan 2026")

        all_results[source['source_name']] = {
            'source_number': source['source_number'],
            'urls': urls,
            'count': len(urls)
        }

        time.sleep(1)

    # 결과 요약
    print(f"\n{'='*60}")
    print("Results Summary")
    print(f"{'='*60}")

    total_urls = sum(r['count'] for r in all_results.values())

    print(f"\n[Total URLs: {total_urls}]")

    for source_name, result in all_results.items():
        print(f"  {source_name:20s}: {result['count']:4d} URLs")

    # 샘플 출력
    print(f"\n{'='*60}")
    print("Sample URLs (first 10)")
    print(f"{'='*60}")

    sample_count = 0
    for source_name, result in all_results.items():
        if result['urls']:
            for url_data in result['urls'][:2]:
                sample_count += 1
                print(f"\n{sample_count}. [{source_name}]")
                print(f"   URL: {url_data['url'][:80]}...")
                print(f"   Date: {url_data.get('lastmod', 'N/A')}")

                if sample_count >= 10:
                    break

        if sample_count >= 10:
            break

    return all_results


if __name__ == '__main__':
    results = collect_urls_from_all_sitemaps()

    print(f"\n{'='*60}")
    print("Next Steps")
    print(f"{'='*60}")
    print("\n1. 이제 이 URL들을 크롤링하여 본문 수집")
    print("2. Gemini로 3가지 정보 추출")
    print("3. 3가지 모두 있는 것만 저장")
    print(f"\n예상: {sum(r['count'] for r in results.values())}개 URL에서")
    print("      완성도 높은 기사 100-200개 수집 가능")
