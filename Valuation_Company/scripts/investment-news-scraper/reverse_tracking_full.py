#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
역추적 FULL: 센서블박스 위클리 2026년 1월 1~5주차 전체 129개 기업
"""

import requests
from bs4 import BeautifulSoup
import time
import json

def safe_print(text, end='\n'):
    """인코딩 에러 방지"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)

# 2026년 1월 1~5주차 전체 투자유치 기업 (129개)
COMPANIES = {
    '5주차': ['이노션스', '모바투스', '오픈마일', '엘리사젠', '로카101', '르몽',
             '소프트웨어융합연구소', '모프시스템즈', '두리컴퍼니', '팩타고라', '트래드스나',
             '큐투켓', '레오스페이스', '디디덴웰케어', '핵사후면케어', '수앤케릿즈',
             '에이샌택', '오픈웨딩', '엔포러스', '모놀리', 'PGT', '스튜디오에피소드'],

    '4주차': ['SDT', '부스티스', '에이디에스', '컨트로펙스', '신소재프레제조', '콕스케어넷',
             '데이터얼라이언스', '브라이트닉스이미징', '스마트아크', '구하다', '미스쿨',
             '에스와이유', '투모로우', '비바트로로보틱스', '웨이크', '슬러토즈', '플로라유지',
             '이원테이블', '옐바', '아워스팟', '포미큰', '디나미스월', '덱산스튜디오', '원',
             'Legion Health', '타이디비', '아이씨피', '한양로보틱스'],

    '3주차': ['크래온유니티', '엔라이트', '아이디어스투실리콘', '한국던난님', '그레이스',
             '망고부스트', 'RXC', 'SML메디트리', '에나이어', '워드로인즈', '오믹스AI',
             '아이슬', '팝업스튜디오', '팸', '리보다스', '큐슬루션즈', '엠피지오웰니스',
             '업맥당', '세상을바꾸는사람들', '랭인큐브', '열다컴퍼니', '애플에이아이',
             '요양의정석', '커버사먼', '애이뉴프로덕션', '어피닛', '매머드커퍼'],

    '2주차': ['라이드플러스', '어니스티', '아롤바이오', '팡세', '주미당', '로블루션',
             '공감오픈텐트', '엠바스', '바이오점', '신군', '소셜스크리야', '메디카네티',
             '로보에테크놀로지', '엘케이벤처스', '더틀티', '심일리티', '내일테크놀로지'],

    '1주차': ['어미닛', '인디그레이션', '인포유금융서비스', '메이사', '배다베로', '블루포인트',
             '하이마루캠퍼니', '디엔텐터크솔루션', '뉴리챗', '도대솔루션', '알엑스비아이오',
             '소담스탑', '프로스앤코', '나루빅큐리티', '파이토스올', '캔디슬리트',
             '드래프터임', '슬러라이즈', '뉴타임인더스트리즈', '에즈위에이크',
             '팰리트노티리퓨먼스', '에스티리테일', '홍시공', 'CSP', '엑스닷츠', '해피컵',
             '반야AI', '페리오너어', '무인의연구소', '하이파이널', '스카이인텔리전스']
}

# 전체 기업 리스트
ALL_COMPANIES = []
for week, companies in COMPANIES.items():
    ALL_COMPANIES.extend(companies)

# 테스트할 미디어 소스
SOURCES = [
    {'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net/', 'search': '?s='},
    {'name': '플래텀', 'url': 'https://platum.kr/', 'search': '?s='},
    {'name': '스타트업투데이', 'url': 'https://startuptoday.kr/', 'search': '/news/articleList.html?search_key=all&search_val='},
    {'name': '비석세스', 'url': 'https://besuccess.com/', 'search': '?s='},
    {'name': '블로터', 'url': 'https://www.bloter.net/', 'search': '/news/articleList.html?search_key=all&search_val='},
]

def search_company(source, company_name):
    """특정 미디어에서 기업명 검색"""
    search_url = source['url'].rstrip('/') + source['search'] + company_name

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text()

        # 기업명과 투자 관련 키워드가 함께 있는지
        if company_name in page_text and any(kw in page_text for kw in ['투자', '유치', '시리즈', '펀딩']):
            return True

        return False

    except Exception as e:
        return False


def main():
    """역추적 실행"""

    print("="*60)
    print("Reverse Tracking FULL: 1~5주차 전체 129개 기업")
    print("="*60)
    print(f"총 기업 수: {len(ALL_COMPANIES)}개")
    print(f"테스트 미디어: {len(SOURCES)}개")
    print("="*60)

    # 각 미디어별 커버 현황
    coverage = {source['name']: [] for source in SOURCES}

    for idx, company in enumerate(ALL_COMPANIES, 1):
        safe_print(f"\n[{idx}/{len(ALL_COMPANIES)}] {company} 검색 중...")

        for source in SOURCES:
            safe_print(f"  - {source['name']}...", end=" ")

            found = search_company(source, company)

            if found:
                print("[FOUND]")
                coverage[source['name']].append(company)
            else:
                print("[NOT FOUND]")

            time.sleep(0.5)  # 서버 부하 방지

    # 결과 집계
    print(f"\n\n{'='*60}")
    print("COVERAGE RESULTS")
    print(f"{'='*60}\n")

    # 커버율 순으로 정렬
    sorted_coverage = sorted(coverage.items(), key=lambda x: len(x[1]), reverse=True)

    for rank, (source_name, companies) in enumerate(sorted_coverage, 1):
        coverage_rate = len(companies) / len(ALL_COMPANIES) * 100
        safe_print(f"{rank}. {source_name}: {len(companies)}/{len(ALL_COMPANIES)}개 ({coverage_rate:.1f}%)")

        if companies:
            safe_print(f"   커버 기업 (처음 10개): {', '.join(companies[:10])}")
            if len(companies) > 10:
                safe_print(f"                        외 {len(companies)-10}개")

    # 상위 5개 추천
    print(f"\n{'='*60}")
    print("RECOMMENDED TOP 5 SOURCES")
    print(f"{'='*60}\n")

    for rank, (source_name, companies) in enumerate(sorted_coverage[:5], 1):
        coverage_rate = len(companies) / len(ALL_COMPANIES) * 100
        safe_print(f"{rank}위. {source_name}: {len(companies)}개 커버 ({coverage_rate:.1f}%)")

    # 결과 JSON으로 저장
    result_file = 'reverse_tracking_result.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(coverage, f, ensure_ascii=False, indent=2)

    print(f"\n\n결과 저장: {result_file}")
    print(f"\n{'='*60}")
    print("이 5개 소스로 자동 수집을 진행하시겠습니까?")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
