#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 Deal 이동 스크립트 (한국 기업만)
"""

import os
import json
import requests
import time
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

def extract_deal_info(article_title):
    """Gemini로 Deal 정보 추출 (한국 기업만)"""

    prompt = f"""
다음 뉴스 제목에서 투자 정보를 JSON 형식으로 추출하세요.

**중요: 한국 기업만 추출합니다. 일본, 미국 등 외국 기업은 제외합니다.**

제목: "{article_title}"

규칙:
1. company_name: 한국 기업 이름 (필수)
   - 일본 기업, 외국 기업이면 null 반환
   - "카카오AI" (일본 회사) → null
   - "GIGR" (글로벌 회사) → null
2. industry: 업종
3. stage: 투자 단계 (시드, 시리즈A, 시리즈B 등)
4. investors: 투자자 (여러 명이면 쉼표로 구분)
5. amount: 투자 금액 (숫자만, 단위 제외)

응답 형식 (JSON만):
{{
    "company_name": "기업명 또는 null",
    "industry": "업종",
    "stage": "투자단계",
    "investors": "투자자1, 투자자2",
    "amount": 100
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

        # 한국 기업인지 확인
        if not data.get('company_name'):
            print(f"  [SKIP] 한국 기업 아님: {article_title}")
            return None

        return data

    except Exception as e:
        print(f"  [ERROR] 추출 실패: {e}")
        return None


def main():
    print("Quick Move to Deals - 한국 기업만")
    print("=" * 60)

    # 최근 50개 기사 가져오기
    url = f"{SUPABASE_URL}/rest/v1/investment_news_articles?select=*&order=published_date.desc&limit=50"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch articles")
        return

    articles = response.json()
    print(f"Total articles: {len(articles)}")

    success_count = 0
    skip_count = 0

    for article in articles:
        title = article['article_title']
        url = article['article_url']
        date = article['published_date']
        site = article['site_name']

        print(f"\n[{date}] {title[:80]}")

        # Gemini로 정보 추출
        deal_info = extract_deal_info(title)

        if not deal_info:
            skip_count += 1
            time.sleep(0.6)
            continue

        # Deal 테이블에 저장
        deal_data = {
            'company_name': deal_info.get('company_name'),
            'industry': deal_info.get('industry'),
            'stage': deal_info.get('stage'),
            'investors': deal_info.get('investors'),
            'amount': deal_info.get('amount'),
            'news_title': title,
            'news_url': url,
            'news_date': date,
            'site_name': site
        }

        # 중복 확인
        check_url = f"{SUPABASE_URL}/rest/v1/deals?select=id&company_name=eq.{deal_info['company_name']}&news_date=eq.{date}"
        check_response = requests.get(check_url, headers=headers)

        if check_response.ok and len(check_response.json()) > 0:
            print(f"  [SKIP] Already exists")
            skip_count += 1
            time.sleep(0.6)
            continue

        # 저장
        save_url = f"{SUPABASE_URL}/rest/v1/deals"
        save_response = requests.post(save_url, headers=headers, json=deal_data)

        if save_response.status_code in [200, 201]:
            print(f"  [SAVED] {deal_info['company_name']} - {deal_info.get('amount', 'N/A')}억원")
            success_count += 1
        else:
            print(f"  [ERROR] Save failed: {save_response.text}")

        time.sleep(0.6)  # Rate limiting

    print("\n" + "=" * 60)
    print(f"Success: {success_count}")
    print(f"Skipped: {skip_count}")
    print("=" * 60)


if __name__ == '__main__':
    main()
