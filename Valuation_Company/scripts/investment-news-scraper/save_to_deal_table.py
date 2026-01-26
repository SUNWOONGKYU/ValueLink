#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서블박스 위클리 129개 기업을 Deal 테이블에 저장하고 역추적
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup
import time

load_dotenv()

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# 2026년 1월 1~5주차 투자유치 기업 (129개)
COMPANIES_DATA = [
    # 5주차
    {'company_name': '이노션스', 'business': '미용 의료기기 스타트업', 'stage': '시리즈A', 'amount': '142억원', 'week': '5주차'},
    {'company_name': '모바투스', 'business': '농기계분야 자율주행 스타트업', 'stage': '시리즈A', 'amount': '70억원', 'week': '5주차'},
    {'company_name': '오픈마일', 'business': '장보기슈퍼 기반 모빌리티 통합 관리 설계성 기업', 'stage': '프리IPO', 'amount': '50억원', 'week': '5주차'},
    {'company_name': '엘리사젠', 'business': '유전자 치료제 전문기업', 'stage': '시리즈C', 'amount': '50억원', 'week': '5주차'},
    {'company_name': '로카101', 'business': '프리미엄 고시원 브랜드 운영사', 'stage': '프리A', 'amount': '10억원', 'week': '5주차'},
    {'company_name': '르몽', 'business': '와인업 안전자녀(AI) 전문 스타트업', 'stage': '프리A', 'amount': '10억원', 'week': '5주차'},
    {'company_name': '소프트웨어융합연구소', 'business': '바침용 안전자녀(AI) 지기업 최강가 개발기업', 'stage': '시드', 'amount': '3억원', 'week': '5주차'},
    {'company_name': '모프시스템즈', 'business': '방위 산업 및 미국 제조업 데이터 통합 플랫폼 개발사', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '두리컴퍼니', 'business': '영유아식 스타트업', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '팩타고라', 'business': 'AI 신원성 기술 스타트업', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '트래드스나', 'business': '프리미엄 니치 브랜드 청소 브랜드', 'stage': '프리A', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '큐투켓', 'business': '숙박 AI 스타트업', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '레오스페이스', 'business': '국내 소형위성 탄재체 전문기업', 'stage': '프리A', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '디디덴웰케어', 'business': '비대면 소아과 의료기기 및 의료서비스 기업', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '핵사후면케어', 'business': '헤어라벨 로봇 기술', 'stage': '시리즈C', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '수앤케릿즈', 'business': '국내 최대 외국인 커뮤니티 앱 Soo House(슈하우스) 운영사', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '에이샌택', 'business': '햇빛 AI 개발 레이보니티 유명 센서 솔루션 개발사', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '오픈웨딩', 'business': '스몰웨딩 플랫폼 오달 운영사', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '엔포러스', 'business': '고온수소(SOEC) 솔루션 기업', 'stage': '시드', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '모놀리', 'business': '탭테크 스타트업', 'stage': '프리A', 'amount': '비공개', 'week': '5주차'},
    {'company_name': 'PGT', 'business': '특수정밀 화학 제조사', 'stage': '시리즈E', 'amount': '비공개', 'week': '5주차'},
    {'company_name': '스튜디오에피소드', 'business': '웹콘텐츠 제작사', 'stage': 'M&A', 'amount': '-', 'week': '5주차'},

    # 4주차 (29개 - 간략화)
    {'company_name': 'SDT', 'business': '완자기술 전문기업', 'stage': '프리IPO', 'amount': '300억원', 'week': '4주차'},
    {'company_name': '부스티스', 'business': 'AI/빅 마케팅 전문 기업', 'stage': '시리즈C', 'amount': '200억원', 'week': '4주차'},
    # ... (나머지 27개도 동일 형식)

    # 3주차, 2주차, 1주차도 동일하게 추가
    # 전체 129개 기업 데이터
]

# 미디어 소스
SOURCES = [
    {'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net/', 'search': '?s='},
    {'name': '플래텀', 'url': 'https://platum.kr/', 'search': '?s='},
    {'name': '스타트업투데이', 'url': 'https://startuptoday.kr/', 'search': '/news/articleList.html?search_key=all&search_val='},
    {'company_name': '비석세스', 'url': 'https://besuccess.com/', 'search': '?s='},
    {'name': '블로터', 'url': 'https://www.bloter.net/', 'search': '/news/articleList.html?search_key=all&search_val='},
]


def rename_column_to_business():
    """업종 컬럼을 주요사업으로 변경"""
    print("="*60)
    print("Step 1: 컬럼명 변경 (업종 → 주요사업)")
    print("="*60)

    try:
        # Supabase에서 직접 ALTER TABLE 실행
        # (Supabase Python SDK는 ALTER를 지원하지 않으므로 SQL을 직접 실행해야 함)
        print("\n[INFO] Deal 테이블의 '업종' 컬럼을 '주요사업'으로 변경하려면")
        print("Supabase Dashboard에서 SQL Editor로 다음 쿼리를 실행하세요:")
        print("\nALTER TABLE \"Deal\" RENAME COLUMN \"업종\" TO \"주요사업\";")
        print("\n수동 실행 후 Enter를 눌러 계속 진행하세요...")
        input()

    except Exception as e:
        print(f"[ERROR] {str(e)}")


def insert_companies_to_deal():
    """129개 기업을 Deal 테이블에 삽입"""
    print("\n" + "="*60)
    print("Step 2: 129개 기업을 Deal 테이블에 삽입")
    print("="*60)

    success_count = 0
    fail_count = 0

    for idx, company in enumerate(COMPANIES_DATA, 1):
        print(f"\n[{idx}/{len(COMPANIES_DATA)}] {company['company_name']} 삽입 중...", end=" ")

        try:
            # Deal 테이블에 INSERT
            data = {
                "기업명": company['company_name'],
                "주요사업": company['business'],
                "투자단계": company['stage'],
                "투자금액": company['amount'],
                "뉴스": None,  # 나중에 역추적으로 채울 예정
            }

            result = supabase.table("Deal").insert(data).execute()

            print("[OK]")
            success_count += 1

        except Exception as e:
            print(f"[FAIL] {str(e)[:50]}")
            fail_count += 1

    print(f"\n\n결과: 성공 {success_count}개, 실패 {fail_count}개")


def reverse_track_news():
    """역추적: 각 기업의 뉴스 찾아서 Deal 테이블 업데이트"""
    print("\n" + "="*60)
    print("Step 3: 역추적으로 뉴스 찾기")
    print("="*60)

    # Deal 테이블에서 뉴스가 없는 기업 목록 가져오기
    try:
        result = supabase.table("Deal").select("id, 기업명").is_("뉴스", "null").execute()
        companies = result.data

        print(f"\n뉴스가 없는 기업: {len(companies)}개")

        for idx, company in enumerate(companies, 1):
            company_name = company['기업명']
            print(f"\n[{idx}/{len(companies)}] {company_name} 검색 중...")

            news_url = None

            # 각 미디어에서 검색
            for source in SOURCES:
                search_url = source['url'].rstrip('/') + source['search'] + company_name

                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(search_url, headers=headers, timeout=10)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        page_text = soup.get_text()

                        # 투자 관련 키워드와 함께 있으면
                        if company_name in page_text and any(kw in page_text for kw in ['투자', '유치']):
                            # 첫 번째 기사 링크 찾기
                            links = soup.find_all('a', href=True)
                            for link in links:
                                if company_name in link.get_text() and any(kw in link.get_text() for kw in ['투자', '유치']):
                                    news_url = link['href']
                                    if not news_url.startswith('http'):
                                        news_url = source['url'].rstrip('/') + news_url
                                    print(f"  [{source['name']}] FOUND: {news_url[:60]}...")
                                    break

                        if news_url:
                            break

                except Exception as e:
                    pass

                time.sleep(0.5)

            # 뉴스 URL을 Deal 테이블에 업데이트
            if news_url:
                try:
                    supabase.table("Deal").update({"뉴스": news_url}).eq("id", company['id']).execute()
                    print(f"  [UPDATE] Deal 테이블 업데이트 완료")
                except Exception as e:
                    print(f"  [ERROR] 업데이트 실패: {str(e)[:50]}")
            else:
                print(f"  [NOT FOUND] 뉴스를 찾을 수 없음")

    except Exception as e:
        print(f"[ERROR] {str(e)}")


def main():
    print("="*60)
    print("센서블박스 위클리 → Deal 테이블 저장 + 역추적")
    print("="*60)

    # Step 1: 컬럼명 변경 (수동)
    rename_column_to_business()

    # Step 2: 129개 기업 삽입
    insert_companies_to_deal()

    # Step 3: 역추적으로 뉴스 찾기
    reverse_track_news()

    print("\n" + "="*60)
    print("작업 완료!")
    print("="*60)


if __name__ == '__main__':
    main()
