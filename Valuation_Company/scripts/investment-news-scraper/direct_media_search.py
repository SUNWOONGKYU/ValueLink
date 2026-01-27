#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11개 미디어 사이트를 직접 검색해서 뉴스 찾기
"""

import csv
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def safe_print(text, end='\n'):
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


# 11개 미디어 사이트 직접 검색
MEDIA_SITES = [
    {
        'name': '벤처스퀘어',
        'search_url': 'https://www.venturesquare.net/?s={keyword}',
        'link_selector': 'h2.entry-title a, h3.entry-title a, a.post-title',
    },
    {
        'name': '스타트업투데이',
        'search_url': 'https://www.startuptoday.kr/news/articleList.html?sc_area=A&view_type=sm&sc_word={keyword}',
        'link_selector': 'div.list-titles a, h4.titles a',
    },
    {
        'name': '더브이씨',
        'search_url': 'https://thevc.kr/?s={keyword}',
        'link_selector': 'h2.entry-title a, a.article-title',
    },
    {
        'name': '비석세스',
        'search_url': 'https://besuccess.com/?s={keyword}',
        'link_selector': 'h2.entry-title a, h3 a',
    },
    {
        'name': '아웃스탠딩',
        'search_url': 'https://outstanding.kr/?s={keyword}',
        'link_selector': 'h2 a, h3 a, a.article-link',
    },
    {
        'name': '플래텀',
        'search_url': 'https://platum.kr/?s={keyword}',
        'link_selector': 'h2.entry-title a, div.post-title a',
    },
    {
        'name': '블로터',
        'search_url': 'https://www.bloter.net/news/articleList.html?sc_area=A&view_type=sm&sc_word={keyword}',
        'link_selector': 'div.list-titles a, h4.titles a',
    },
    {
        'name': '스타트업엔',
        'search_url': 'https://www.startupn.kr/news/articleList.html?sc_area=A&view_type=sm&sc_word={keyword}',
        'link_selector': 'div.list-titles a, h4.titles a',
    },
    {
        'name': 'WOWTALE',
        'search_url': 'https://www.wowtale.net/?s={keyword}',
        'link_selector': 'h2 a, h3 a',
    },
    {
        'name': '넥스트유니콘',
        'search_url': 'https://www.nextunicorn.kr/news/articleList.html?sc_area=A&view_type=sm&sc_word={keyword}',
        'link_selector': 'div.list-titles a, h4.titles a',
    },
    {
        'name': '이코노미스트',
        'search_url': 'https://www.economist.co.kr/news/articleList.html?sc_area=A&view_type=sm&sc_word={keyword}',
        'link_selector': 'div.list-titles a, h4.titles a',
    },
]


def search_in_media(company_name):
    """11개 미디어에서 직접 검색"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/',
    }

    keyword = quote(company_name)

    for site in MEDIA_SITES:
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
                        if any(kw in title for kw in ['투자', '유치', '펀딩', '시리즈']):
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python direct_media_search.py <group_num>")
        sys.exit(1)

    group_num = int(sys.argv[1])
    input_file = f'not_found_group{group_num}.csv'
    output_file = f'direct_found_group{group_num}.csv'

    print("="*60)
    safe_print(f"그룹 {group_num} - 11개 미디어 직접 검색")
    print("="*60)

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    safe_print(f"기업 수: {len(companies)}개\n")

    found_count = 0

    for idx, company in enumerate(companies, 1):
        company_name = company['기업명']

        safe_print(f"[G{group_num}:{idx}/{len(companies)}] {company_name}...", end=" ")

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

    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=companies[0].keys())
        writer.writeheader()
        writer.writerows(companies)

    print("\n" + "="*60)
    safe_print(f"그룹 {group_num} 완료: {found_count}/{len(companies)} 발견 ({found_count*100//len(companies)}%)")
    print("="*60)


if __name__ == '__main__':
    main()
