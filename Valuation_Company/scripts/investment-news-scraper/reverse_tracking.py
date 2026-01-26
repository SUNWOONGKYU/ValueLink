#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
역추적: 센서블박스 위클리 투자 기업 목록으로 어느 미디어가 커버했는지 확인
"""

import requests
from bs4 import BeautifulSoup
import time

def safe_print(text, end='\n'):
    """인코딩 에러 방지"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)

# 센서블박스 위클리 2026년 1월 5주차 투자 기업 목록
COMPANIES = [
    '이노션스',
    '모바투스',
    '오픈마일',
    '엘리사젠',
    '로카101',
    '르몽',
    '소프트웨어융합연구소',
    '모프시스템즈',
    '두리컴퍼니',
    '팩타고라',
    '트래드스나',
    '큐투켓',
    '레오스페이스',
    '디디덴웰케어',
    '핵사후면케어',
    '수앤케릿즈',
    '에이샌택',
    '오픈웨딩',
    '엔포러스',
    '모놀리',
    'PGT',
    '스튜디오에피소드'
]

# 테스트할 미디어 소스
SOURCES = [
    {
        'name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net/',
        'search_param': '?s='
    },
    {
        'name': '플래텀',
        'url': 'https://platum.kr/',
        'search_param': '?s='
    },
    {
        'name': '스타트업투데이',
        'url': 'https://startuptoday.kr/',
        'search_param': '/news/articleList.html?search_key=all&search_val='
    },
    {
        'name': '스타트업엔',
        'url': 'https://startupn.kr/',
        'search_param': '/news/articleList.html?search_key=all&search_val='
    },
    {
        'name': '비석세스',
        'url': 'https://besuccess.com/',
        'search_param': '?s='
    },
    {
        'name': '블로터',
        'url': 'https://www.bloter.net/',
        'search_param': '/news/articleList.html?search_key=all&search_val='
    },
    {
        'name': '아웃스탠딩',
        'url': 'https://outstanding.kr/',
        'search_param': '?s='
    },
    {
        'name': '넥스트유니콘',
        'url': 'https://www.nextunicorn.kr/',
        'search_param': '/news/articleList.html?search_key=all&search_val='
    },
    {
        'name': '이코노미스트',
        'url': 'https://www.economist.co.kr/',
        'search_param': '/news/articleList.html?search_key=all&search_val='
    },
    {
        'name': 'AI타임스',
        'url': 'https://www.aitimes.com/',
        'search_param': '/news/articleList.html?search_key=all&search_val='
    },
    {
        'name': '와우테일',
        'url': 'https://www.wowtale.net/',
        'search_param': '?s='
    }
]

def search_company_in_source(source, company_name):
    """특정 미디어에서 기업명 검색"""

    search_url = source['url'].rstrip('/') + source['search_param'] + company_name

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.content, 'html.parser')

        # 페이지 텍스트에 기업명이 있는지 확인
        page_text = soup.get_text()

        # 투자 관련 키워드와 함께 나오는지 확인
        if company_name in page_text:
            # 투자 관련 키워드도 같이 있는지 확인
            if any(kw in page_text for kw in ['투자', '유치', '시리즈', '펀딩']):
                return True

        return False

    except Exception as e:
        return False


def main():
    """역추적 실행"""

    print("="*60)
    print("Reverse Tracking: 센서블박스 위클리 투자 기업")
    print("="*60)
    print(f"기업 수: {len(COMPANIES)}개")
    print(f"미디어 수: {len(SOURCES)}개")
    print("="*60)

    # 각 미디어별 커버 현황
    coverage = {source['name']: [] for source in SOURCES}

    for idx, company in enumerate(COMPANIES, 1):
        safe_print(f"\n[{idx}/{len(COMPANIES)}] {company} 검색 중...")

        for source in SOURCES:
            safe_print(f"  - {source['name']}...", end=" ")

            found = search_company_in_source(source, company)

            if found:
                print("[FOUND]")
                coverage[source['name']].append(company)
            else:
                print("[NOT FOUND]")

            time.sleep(1)  # 서버 부하 방지

    # 결과 집계
    print(f"\n\n{'='*60}")
    print("COVERAGE RESULTS")
    print(f"{'='*60}\n")

    # 커버율 순으로 정렬
    sorted_coverage = sorted(coverage.items(), key=lambda x: len(x[1]), reverse=True)

    for rank, (source_name, companies) in enumerate(sorted_coverage, 1):
        coverage_rate = len(companies) / len(COMPANIES) * 100
        safe_print(f"{rank}. {source_name}: {len(companies)}개 ({coverage_rate:.1f}%)")

        if companies:
            safe_print(f"   커버 기업: {', '.join(companies[:5])}")
            if len(companies) > 5:
                safe_print(f"            외 {len(companies)-5}개")

    # 상위 5개 추천
    print(f"\n{'='*60}")
    print("RECOMMENDED TOP 5 SOURCES")
    print(f"{'='*60}\n")

    for rank, (source_name, companies) in enumerate(sorted_coverage[:5], 1):
        coverage_rate = len(companies) / len(COMPANIES) * 100
        safe_print(f"{rank}. {source_name}: {len(companies)}/{len(COMPANIES)}개 ({coverage_rate:.1f}%)")

    print(f"\n{'='*60}")
    print("이 5개 소스로 자동 수집을 진행하시겠습니까?")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
