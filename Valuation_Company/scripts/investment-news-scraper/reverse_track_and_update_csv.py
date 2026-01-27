#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
역추적: 129개 기업의 뉴스 URL을 찾아서 CSV에 추가
"""

import csv
import requests
from bs4 import BeautifulSoup
import time

def safe_print(text, end='\n'):
    """인코딩 에러 방지"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


# 전체 11개 미디어 소스
SOURCES = [
    {'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net/', 'search': '?s='},
    {'name': '더브이씨', 'url': 'https://thevc.kr/', 'search': '?s='},
    {'name': '스타트업투데이', 'url': 'https://startuptoday.kr/', 'search': '/news/articleList.html?search_key=all&search_val='},
    {'name': '비석세스', 'url': 'https://besuccess.com/', 'search': '?s='},
    {'name': '아웃스탠딩', 'url': 'https://outstanding.kr/', 'search': '?s='},
    {'name': '스타트업엔', 'url': 'https://startupn.kr/', 'search': '/news/articleList.html?search_key=all&search_val='},
    {'name': '플래텀', 'url': 'https://platum.kr/', 'search': '?s='},
    {'name': '넥스트유니콘', 'url': 'https://www.nextunicorn.kr/', 'search': '/news/articleList.html?search_key=all&search_val='},
    {'name': '블로터', 'url': 'https://www.bloter.net/', 'search': '/news/articleList.html?search_key=all&search_val='},
    {'name': '이코노미스트', 'url': 'https://www.economist.co.kr/', 'search': '/news/articleList.html?search_key=all&search_val='},
    {'name': 'WOWTALE', 'url': 'https://www.wowtale.net/', 'search': '?s='},
]


def search_news_for_company(company_name):
    """기업명으로 뉴스 검색"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for source in SOURCES:
        search_url = source['url'].rstrip('/') + source['search'] + company_name

        try:
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text()

                # 투자 관련 키워드와 함께 있으면
                if company_name in page_text and any(kw in page_text for kw in ['투자', '유치', '시리즈', '펀딩']):
                    # 첫 번째 기사 링크 찾기
                    links = soup.find_all('a', href=True)
                    for link in links:
                        link_text = link.get_text()
                        # 기업명과 투자 키워드가 함께 있는 링크
                        if company_name in link_text and any(kw in link_text for kw in ['투자', '유치', '시리즈', '펀딩']):
                            news_url = link['href']
                            if not news_url.startswith('http'):
                                news_url = source['url'].rstrip('/') + news_url

                            safe_print(f"[{source['name']}] FOUND")
                            return news_url, source['name']

        except Exception as e:
            pass

        time.sleep(0.5)

    return None, None


def reverse_track_all():
    """전체 기업 역추적"""

    input_csv = 'sensible_companies_2026_01.csv'
    output_csv = 'sensible_companies_2026_01_with_news.csv'

    print("="*60)
    print("역추적: 129개 기업의 뉴스 URL 찾기")
    print("="*60)
    safe_print(f"\n입력: {input_csv}")
    safe_print(f"출력: {output_csv}\n")
    print("="*60)

    # CSV 읽기
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    # None 키 제거 (CSV 읽기 시 발생할 수 있는 문제)
    for company in companies:
        if None in company:
            del company[None]

    safe_print(f"\n총 기업 수: {len(companies)}개\n")

    # 뉴스 URL과 소스 컬럼 추가
    found_count = 0
    not_found_count = 0

    # 모든 회사에 빈 컬럼 먼저 추가 (fieldnames 문제 방지)
    for company in companies:
        company['뉴스URL'] = ''
        company['뉴스소스'] = ''

    for idx, company in enumerate(companies, 1):
        company_name = company['기업명']
        safe_print(f"\n[{idx}/{len(companies)}] {company_name} 검색 중...", end=" ")

        news_url, source_name = search_news_for_company(company_name)

        if news_url:
            company['뉴스URL'] = news_url
            company['뉴스소스'] = source_name
            found_count += 1
            print(f"[{source_name}] FOUND")
        else:
            print("[NOT FOUND]")
            not_found_count += 1

        time.sleep(1)  # 서버 부하 방지

    # 결과 CSV 저장
    # None 키 제거하고 fieldnames 생성
    fieldnames = [key for key in companies[0].keys() if key is not None]

    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(companies)

    # 결과 요약
    print("\n\n" + "="*60)
    print("역추적 완료")
    print("="*60)
    print(f"뉴스 발견: {found_count}개 ({found_count/len(companies)*100:.1f}%)")
    print(f"뉴스 없음: {not_found_count}개 ({not_found_count/len(companies)*100:.1f}%)")
    safe_print(f"\n결과 파일: {output_csv}")

    # 소스별 통계
    source_stats = {}
    for company in companies:
        source = company.get('뉴스소스', '')
        if source:
            source_stats[source] = source_stats.get(source, 0) + 1

    if source_stats:
        print("\n소스별 통계:")
        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            safe_print(f"  {source}: {count}개")

    print("\n" + "="*60)


if __name__ == '__main__':
    reverse_track_all()
