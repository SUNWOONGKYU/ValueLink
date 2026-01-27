#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 뉴스 검색으로 투자 뉴스 찾기
"""

import csv
import sys
import time
import requests
from bs4 import BeautifulSoup

def safe_print(text, end='\n'):
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


def naver_news_search(company_name):
    """네이버 뉴스 검색으로 투자 뉴스 찾기"""

    query = f"{company_name} 투자 유치"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        # 네이버 뉴스 검색
        url = f"https://search.naver.com/search.naver?where=news&query={query}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 뉴스 링크 찾기
            news_items = soup.select('a.news_tit')

            for item in news_items[:5]:  # 상위 5개
                title = item.get_text()
                link = item.get('href', '')

                # 투자 관련 키워드 확인
                if any(kw in title for kw in ['투자', '유치', '펀딩', '시리즈']):
                    # 소스명 추출
                    domain_map = {
                        'venturesquare': '벤처스퀘어',
                        'startuptoday': '스타트업투데이',
                        'platum': '플래텀',
                        'bloter': '블로터',
                        'besuccess': '비석세스',
                        'thevc': '더브이씨',
                        'outstanding': '아웃스탠딩',
                        'startupn': '스타트업엔',
                        'nextunicorn': '넥스트유니콘',
                        'economist': '이코노미스트',
                        'wowtale': 'WOWTALE',
                        'aitimes': 'AI타임스',
                        'newstap': '뉴스톱',
                        'etnews': '전자신문',
                        'zdnet': 'ZDNet',
                        'mk.co.kr': '매일경제',
                        'hankyung': '한국경제',
                        'chosun': '조선일보',
                        'joins': '중앙일보',
                        'donga': '동아일보',
                    }

                    source = '네이버 뉴스'
                    for domain, name in domain_map.items():
                        if domain in link.lower():
                            source = name
                            break

                    return link, source

    except Exception as e:
        pass

    return None, None


def main():
    if len(sys.argv) < 2:
        print("Usage: python naver_search.py <group_num>")
        sys.exit(1)

    group_num = int(sys.argv[1])
    input_file = f'not_found_group{group_num}.csv'
    output_file = f'naver_found_group{group_num}.csv'

    print("="*60)
    safe_print(f"그룹 {group_num} 네이버 뉴스 검색 시작")
    print("="*60)

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    safe_print(f"기업 수: {len(companies)}개\n")

    found_count = 0

    for idx, company in enumerate(companies, 1):
        company_name = company['기업명']

        safe_print(f"[G{group_num}:{idx}/{len(companies)}] {company_name}...", end=" ")

        news_url, source_name = naver_news_search(company_name)

        if news_url:
            company['뉴스URL'] = news_url
            company['뉴스소스'] = source_name
            found_count += 1
            safe_print(f"✅ [{source_name}]")
        else:
            company['뉴스URL'] = ''
            company['뉴스소스'] = ''
            safe_print("❌")

        time.sleep(0.5)  # 네이버 요청 제한 회피

    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=companies[0].keys())
        writer.writeheader()
        writer.writerows(companies)

    print("\n" + "="*60)
    safe_print(f"그룹 {group_num} 완료: {found_count}/{len(companies)} 발견")
    print("="*60)


if __name__ == '__main__':
    main()
