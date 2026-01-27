#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
92개 미발견 기업 전부 찾기 - Google + Gemini
"""

import csv
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Gemini API 키 확인
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def safe_print(text, end='\n'):
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


def gemini_find_url(company_name, links):
    """Gemini REST API로 투자 뉴스 URL 찾기"""

    if not links:
        return None

    prompt = f"""다음 URL 목록에서 "{company_name}" 기업의 투자 유치 뉴스 기사 URL을 찾아주세요.

URL 목록:
{chr(10).join(links[:10])}

조건:
- 투자, 유치, 펀딩, 시리즈 관련 기사
- 한국어 뉴스 사이트
- 실제 기사 URL (목록 페이지 제외)

형식: URL만 반환 (설명 없이)
없으면: NONE"""

    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        response = requests.post(
            f"{url}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()

            if text and text != 'NONE' and text.startswith('http'):
                return text

    except Exception as e:
        pass

    return None


def google_search(company_name, stage=""):
    """Google 검색으로 투자 뉴스 찾기"""

    queries = [
        f"{company_name} 투자 유치",
        f"{company_name} {stage} 투자",
        f"{company_name} 펀딩",
        f'"{company_name}" 투자',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for query in queries:
        try:
            search_url = f"https://www.google.com/search?q={query}&hl=ko"
            response = requests.get(search_url, headers=headers, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # 검색 결과 링크 추출
                links = []
                for g in soup.find_all('div', class_='g'):
                    for a in g.find_all('a'):
                        href = a.get('href', '')
                        if href.startswith('http') and 'google' not in href:
                            links.append(href)

                if links:
                    # Gemini로 분석
                    url = gemini_find_url(company_name, links)
                    if url:
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

                        source = 'Google 검색'
                        for domain, name in domain_map.items():
                            if domain in url.lower():
                                source = name
                                break

                        return url, source

            time.sleep(0.3)  # 빠른 검색

        except Exception as e:
            continue

    return None, None


def main():
    if len(sys.argv) < 2:
        print("Usage: python final_search.py <group_num>")
        sys.exit(1)

    group_num = int(sys.argv[1])
    input_file = f'not_found_group{group_num}.csv'
    output_file = f'found_group{group_num}.csv'

    print("="*60)
    safe_print(f"그룹 {group_num} 검색 시작 (Google + Gemini)")
    print("="*60)

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    safe_print(f"기업 수: {len(companies)}개\n")

    found_count = 0

    for idx, company in enumerate(companies, 1):
        company_name = company['기업명']
        stage = company.get('단계', '')

        safe_print(f"[G{group_num}:{idx}/{len(companies)}] {company_name}...", end=" ")

        news_url, source_name = google_search(company_name, stage)

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
    safe_print(f"그룹 {group_num} 완료: {found_count}/{len(companies)} 발견")
    print("="*60)


if __name__ == '__main__':
    main()
