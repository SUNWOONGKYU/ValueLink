#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google 검색 + Gemini 분석으로 투자 뉴스 URL 찾기
모든 기업의 뉴스를 100% 찾을 때까지 실행
"""

import csv
import os
import time
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def safe_print(text, end='\n'):
    """인코딩 에러 방지"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


def google_search(company_name, investment_stage=""):
    """Google 검색으로 투자 뉴스 찾기"""

    # 여러 검색 쿼리 시도
    queries = [
        f"{company_name} 투자 유치",
        f"{company_name} {investment_stage} 투자",
        f"{company_name} 펀딩",
        f"{company_name} 시리즈",
        f'"{company_name}" 투자',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for query in queries:
        try:
            # Google 검색
            search_url = f"https://www.google.com/search?q={query}&hl=ko"
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # 검색 결과에서 링크 추출
                links = []
                for g in soup.find_all('div', class_='g'):
                    anchors = g.find_all('a')
                    for a in anchors:
                        href = a.get('href', '')
                        if href.startswith('http') and 'google' not in href:
                            links.append(href)

                if links:
                    # Gemini로 관련 뉴스 URL 찾기
                    prompt = f"""
아래 검색 결과 URL 중에서 "{company_name}" 기업의 투자 유치 뉴스 기사 URL을 찾아주세요.

검색된 URL:
{chr(10).join(links[:10])}

다음 조건을 만족하는 URL 1개만 반환:
1. 투자 유치, 펀딩, 시리즈 관련 기사
2. 한국어 뉴스 사이트 (벤처스퀘어, 스타트업투데이, 플래텀, 블로터 등)
3. 실제 기사 URL (검색 페이지나 목록 페이지 제외)

형식: URL만 반환 (설명 없이)
없으면: NONE
"""

                    result = model.generate_content(prompt)
                    url = result.text.strip()

                    if url and url != 'NONE' and url.startswith('http'):
                        # 소스명 추출
                        if 'venturesquare' in url:
                            source = '벤처스퀘어'
                        elif 'startuptoday' in url:
                            source = '스타트업투데이'
                        elif 'platum' in url:
                            source = '플래텀'
                        elif 'bloter' in url:
                            source = '블로터'
                        elif 'besuccess' in url:
                            source = '비석세스'
                        elif 'thevc' in url:
                            source = '더브이씨'
                        elif 'outstanding' in url:
                            source = '아웃스탠딩'
                        elif 'startupn' in url:
                            source = '스타트업엔'
                        elif 'nextunicorn' in url:
                            source = '넥스트유니콘'
                        elif 'economist' in url:
                            source = '이코노미스트'
                        elif 'wowtale' in url:
                            source = 'WOWTALE'
                        elif 'aitimes' in url:
                            source = 'AI타임스'
                        elif 'newstap' in url:
                            source = '뉴스톱'
                        elif 'etnews' in url:
                            source = '전자신문'
                        elif 'zdnet' in url:
                            source = 'ZDNet Korea'
                        else:
                            source = 'Google 검색'

                        return url, source

            time.sleep(2)  # Google 요청 제한 회피

        except Exception as e:
            safe_print(f"  [에러: {str(e)[:30]}]")
            continue

    return None, None


def search_all_companies():
    """모든 미발견 기업 검색"""

    input_csv = 'sensible_companies_2026_01_with_news.csv'
    output_csv = 'sensible_companies_2026_01_complete.csv'

    print("="*60)
    print("Google 검색 + Gemini 분석으로 100% 발견")
    print("="*60)

    # CSV 읽기
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    # 미발견 기업만 추출
    not_found = [c for c in companies if not c.get('뉴스URL') or c.get('뉴스URL') == '']

    safe_print(f"\n미발견 기업: {len(not_found)}개")
    safe_print(f"Google + Gemini로 재검색 시작\n")
    print("="*60)

    found_count = 0
    still_not_found = 0

    for idx, company in enumerate(not_found, 1):
        company_name = company['기업명']
        stage = company.get('단계', '')

        safe_print(f"\n[{idx}/{len(not_found)}] {company_name} 검색 중...", end=" ")

        news_url, source_name = google_search(company_name, stage)

        if news_url:
            # 원본 companies 리스트에서 찾아서 업데이트
            for c in companies:
                if c['기업명'] == company_name:
                    c['뉴스URL'] = news_url
                    c['뉴스소스'] = source_name
                    break

            found_count += 1
            safe_print(f"✅ [{source_name}] FOUND")
        else:
            still_not_found += 1
            safe_print("❌ NOT FOUND")

    # 결과 CSV 저장
    fieldnames = [key for key in companies[0].keys() if key is not None]

    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(companies)

    # 최종 결과
    total_found = len([c for c in companies if c.get('뉴스URL')])

    print("\n\n" + "="*60)
    print("최종 결과")
    print("="*60)
    print(f"전체 기업: {len(companies)}개")
    print(f"총 발견: {total_found}개 ({total_found/len(companies)*100:.1f}%)")
    print(f"이번 라운드 발견: {found_count}개")
    print(f"여전히 미발견: {still_not_found}개")
    safe_print(f"\n결과 파일: {output_csv}")
    print("="*60)


if __name__ == '__main__':
    search_all_companies()
