#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자자 정보가 없는 Deal의 투자자 찾기
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import codecs
from google import genai
from google.genai import types
import time
import json
import requests
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_investors_with_gemini(title, url):
    """Gemini로 뉴스에서 투자자 추출"""

    # 뉴스 본문 크롤링
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 본문 추출 (간단하게)
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])  # 처음 10개 문단
        else:
            content = ""
    except:
        content = ""

    prompt = f"""
다음 투자유치 뉴스에서 투자자를 찾아주세요:

제목: {title}
본문: {content[:1000]}

JSON 형식으로만 답변:
{{
    "investors": "투자자명 (콤마로 구분, 예: 알토스벤처스, 삼성벤처투자)"
}}

조건:
- 투자자가 여러 명이면 콤마로 구분
- 투자자가 없으면 null
- VC, 투자사, 액셀러레이터 등 투자한 회사/기관명만
"""

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=256,
                response_mime_type='application/json'
            )
        )

        if response and hasattr(response, 'text'):
            text = response.text.strip()
            result = json.loads(text)
            return result.get('investors')

        return None
    except Exception as e:
        print(f"  Gemini 오류: {str(e)[:50]}")
        return None

def fill_missing_investors():
    """투자자가 없는 Deal의 투자자 찾기"""

    # 투자자가 없는 Deal
    deals = supabase.table('deals').select('*').is_('investors', 'null').execute()

    print(f"📊 투자자 정보 없는 Deal: {len(deals.data)}개\n")

    updated = 0
    failed = 0

    for deal in deals.data:
        company = deal['company_name']
        number = deal['number']
        title = deal.get('news_title', '')
        url = deal.get('news_url', '')

        if not url:
            print(f"❌ #{number} {company}: URL 없음")
            failed += 1
            continue

        print(f"🔍 #{number} {company}... ", end='')

        investors = extract_investors_with_gemini(title, url)

        if investors:
            print(f"✅ {investors}")

            # 업데이트
            supabase.table('deals').update({
                'investors': investors
            }).eq('id', deal['id']).execute()

            updated += 1
        else:
            print("❌ 투자자 없음")
            failed += 1

        time.sleep(1)

    print(f"\n" + "="*80)
    print(f"✅ 업데이트: {updated}개")
    print(f"❌ 실패: {failed}개")
    print("="*80)

# 메인
print("=" * 80)
print("투자자 정보 채우기")
print("=" * 80 + "\n")

fill_missing_investors()

print("\n완료!")
