#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국 기업 투자 뉴스만 Deal 테이블로 이동
- 일본, 외국 기업 제외
- 투자사 목록 제외
- 실제 투자 뉴스만 선정
"""

import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# 제외할 키워드 (투자사 목록)
EXCLUDED_KEYWORDS = [
    '엔젤리그', '실홀딩스', '인베스트먼트', '캐피탈', '벤처스',
    'IR', '대표', 'M&A', '투자사', '파트너스'
]

# 외국 기업 키워드
FOREIGN_KEYWORDS = [
    '일본', 'Japan', '미국', 'USA', '중국', 'China',
    '글로벌', 'Global', '해외'
]


def is_korean_investment_news(title):
    """한국 기업 투자 뉴스인지 판단"""

    # 제외 키워드 체크
    for keyword in EXCLUDED_KEYWORDS:
        if keyword in title:
            return False

    # 외국 기업 키워드 체크
    for keyword in FOREIGN_KEYWORDS:
        if keyword in title:
            return False

    # 투자 관련 키워드가 있는지 확인
    investment_keywords = ['투자', '유치', '시리즈', '억원', '억', '만원']
    has_investment = any(kw in title for kw in investment_keywords)

    if not has_investment:
        return False

    return True


def extract_deal_info(title, url):
    """Gemini로 Deal 정보 추출"""

    prompt = f"""
다음 뉴스 제목에서 투자 정보를 JSON 형식으로 추출하세요.

**중요 규칙:**
1. **한국 기업만** 추출합니다
2. 일본 기업, 외국 기업, 투자사 목록은 제외합니다
3. 실제 투자를 받은 스타트업만 추출합니다

제목: "{title}"

추출 항목:
1. company_name: 투자받은 한국 기업명 (필수)
   - 일본 회사(카카오AI 등) → null
   - 외국 회사(GIGR 등) → null
   - 투자사 이름(엔젤리그, 87실홀딩스 등) → null
   - 명확한 한국 스타트업만 추출
2. ceo: 대표자명
3. industry: 업종
4. stage: 투자 단계 (시드/프리A/시리즈A/시리즈B 등)
5. investors: 투자자 (여러 명이면 쉼표 구분)
6. amount: 투자 금액 (억원 단위 숫자만, 예: 100)
7. location: 본사 위치 (서울, 판교 등)

**중요:** 한국 기업이 확실하지 않으면 company_name을 null로 반환하세요.

응답 (JSON만):
{{
    "company_name": "기업명 또는 null",
    "ceo": "대표자명",
    "industry": "업종",
    "stage": "투자단계",
    "investors": "투자자",
    "amount": 100,
    "location": "위치"
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # JSON 추출
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()

        data = json.loads(text)

        # company_name 필수
        if not data.get('company_name'):
            return None

        return data

    except Exception as e:
        print(f"  [ERROR] Extract failed: {e}")
        return None


def main():
    print("=" * 80)
    print("한국 기업 투자 뉴스 → Deal 테이블 이동")
    print("=" * 80)

    # investment_news_articles에서 모든 기사 가져오기
    url = f"{SUPABASE_URL}/rest/v1/investment_news_articles?select=*&order=published_date.desc"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch articles")
        return

    articles = response.json()
    print(f"\nTotal articles: {len(articles)}")

    # 필터링
    filtered_articles = []
    for article in articles:
        title = article['article_title']

        if is_korean_investment_news(title):
            filtered_articles.append(article)

    print(f"Filtered (한국 투자 뉴스): {len(filtered_articles)}")

    if len(filtered_articles) == 0:
        print("\n[WARNING] No Korean investment news found!")
        return

    # Deal 추출 및 저장
    success_count = 0
    skip_count = 0
    error_count = 0

    for i, article in enumerate(filtered_articles, 1):
        title = article['article_title']
        url = article['article_url']
        date = article['published_date']
        site = article['site_name']

        print(f"\n[{i}/{len(filtered_articles)}] {date}")
        print(f"  {title[:100]}")

        # Gemini 추출
        deal_info = extract_deal_info(title, url)

        if not deal_info:
            print(f"  [SKIP] 한국 기업 아니거나 정보 부족")
            skip_count += 1
            time.sleep(0.6)
            continue

        # Deal 데이터 구성
        deal_data = {
            'company_name': deal_info.get('company_name'),
            'ceo': deal_info.get('ceo'),
            'industry': deal_info.get('industry'),
            'stage': deal_info.get('stage'),
            'investors': deal_info.get('investors'),
            'amount': deal_info.get('amount'),
            'location': deal_info.get('location'),
            'news_title': title,
            'news_url': url,
            'news_date': date,
            'site_name': site
        }

        # 중복 체크 (같은 회사 + 같은 날짜)
        check_url = f"{SUPABASE_URL}/rest/v1/deals?select=id&company_name=eq.{deal_info['company_name']}&news_date=eq.{date}"
        check_response = requests.get(check_url, headers=headers)

        if check_response.ok and len(check_response.json()) > 0:
            print(f"  [SKIP] Duplicate: {deal_info['company_name']}")
            skip_count += 1
            time.sleep(0.6)
            continue

        # Deal 저장
        save_url = f"{SUPABASE_URL}/rest/v1/deals"
        save_response = requests.post(save_url, headers=headers, json=deal_data)

        if save_response.status_code in [200, 201]:
            amt = deal_info.get('amount', 'N/A')
            print(f"  [SAVED] {deal_info['company_name']} - {amt}억원")
            success_count += 1
        else:
            print(f"  [ERROR] Save failed: {save_response.text[:100]}")
            error_count += 1

        time.sleep(0.6)  # Rate limiting

    print("\n" + "=" * 80)
    print(f"Success: {success_count}")
    print(f"Skipped: {skip_count}")
    print(f"Errors: {error_count}")
    print("=" * 80)


if __name__ == '__main__':
    main()
