#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
특정 그룹의 기업들 Google 검색
"""

import sys
import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Gemini 설정
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def safe_print(text, end='\n'):
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


def google_search(company_name, investment_stage=""):
    """Google 검색으로 투자 뉴스 찾기"""

    queries = [
        f"{company_name} 투자 유치",
        f"{company_name} {investment_stage} 투자",
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

                links = []
                for g in soup.find_all('div', class_='g'):
                    anchors = g.find_all('a')
                    for a in anchors:
                        href = a.get('href', '')
                        if href.startswith('http') and 'google' not in href:
                            links.append(href)

                if links:
                    prompt = f"""
아래 URL 중 "{company_name}" 기업의 투자 유치 뉴스 URL 1개만 반환:

{chr(10).join(links[:10])}

조건: 투자/펀딩/시리즈 관련 한국어 뉴스
형식: URL만 (설명 없이)
없으면: NONE
"""

                    response = client.models.generate_content(
                        model='gemini-2.0-flash-exp',
                        contents=prompt
                    )
                    url = response.text.strip()

                    if url and url != 'NONE' and url.startswith('http'):
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
                            'zdnet': 'ZDNet Korea',
                            'mk.co.kr': '매일경제',
                            'hankyung.com': '한국경제',
                            'chosun.com': '조선일보',
                            'joins.com': '중앙일보',
                        }

                        source = 'Google 검색'
                        for domain, name in domain_map.items():
                            if domain in url:
                                source = name
                                break

                        return url, source

            time.sleep(0.5)

        except Exception as e:
            continue

    return None, None


def search_group(group_num):
    """특정 그룹 검색"""

    input_file = f'not_found_group{group_num}.csv'
    output_file = f'found_group{group_num}.csv'

    print("="*60)
    safe_print(f"그룹 {group_num} 검색 시작")
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
    if len(sys.argv) < 2:
        print("Usage: python search_group.py <group_number>")
        sys.exit(1)

    group_num = int(sys.argv[1])
    search_group(group_num)
