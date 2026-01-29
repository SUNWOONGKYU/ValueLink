#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주요사업 정보가 없는 Deal의 업종 추출
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import requests
from bs4 import BeautifulSoup
import codecs
from google import genai
from google.genai import types
import time
import json

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_industry_with_gemini(title, url):
    """Gemini로 뉴스에서 주요사업/업종 추출"""

    # 뉴스 본문 크롤링
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 본문 추출
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs[:15]])  # 처음 15개 문단
        else:
            content = ""
    except:
        content = ""

    prompt = f"""
다음 투자유치 뉴스에서 회사의 주요사업/업종을 간단히 답변해주세요:

제목: {title}
본문: {content[:1500]}

회사의 주요사업을 2-3단어로 간결하게 답변하세요.
예시: "AI 기반 헬스케어", "이커머스 플랫폼", "핀테크", "푸드테크", "모빌리티"

업종만 답변하고 다른 설명은 하지 마세요.
"""

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=64
            )
        )

        if response and hasattr(response, 'text'):
            text = response.text.strip()

            # 빈 응답이나 불필요한 텍스트 제거
            if not text or len(text) < 2:
                return None

            # 불필요한 문구 제거
            unwanted = ['Here is', 'JSON', 'requested', ':', '{', '}', '"']
            for word in unwanted:
                if word in text and len(text) > 20:
                    return None

            # 텍스트 정제 (앞뒤 따옴표, 공백 제거)
            text = text.strip('"\'').strip()

            return text if len(text) > 1 and len(text) < 50 else None

        return None
    except Exception as e:
        # API 오류 시 제목에서 키워드 추출 시도
        keywords = ['AI', '헬스케어', '핀테크', '이커머스', '푸드테크', '커머스', 'SaaS', 'B2B', 'B2C']
        for keyword in keywords:
            if keyword in title or keyword in content:
                return keyword

        return None

def fill_missing_industry():
    """주요사업이 없는 Deal의 업종 찾기"""

    # 주요사업이 없는 Deal
    deals = supabase.table('deals').select('*').or_('industry.is.null,industry.eq.-').execute()

    print(f"📊 주요사업 정보 없는 Deal: {len(deals.data)}개\n")

    updated = 0
    failed = 0

    for deal in deals.data:
        company = deal['company_name']
        number = deal.get('number', '-')
        title = deal.get('news_title', '')
        url = deal.get('news_url', '')

        if not url:
            print(f"❌ #{number} {company}: URL 없음")
            failed += 1
            continue

        print(f"🔍 #{number} {company}... ", end='')

        industry = extract_industry_with_gemini(title, url)

        if industry:
            print(f"✅ {industry}")

            # 업데이트
            supabase.table('deals').update({
                'industry': industry
            }).eq('id', deal['id']).execute()

            updated += 1
        else:
            print("❌ 업종 추출 실패")
            failed += 1

        time.sleep(1)

    print(f"\n" + "="*80)
    print(f"✅ 업데이트: {updated}개")
    print(f"❌ 실패: {failed}개")
    print("="*80)

# 메인
print("=" * 80)
print("주요사업 정보 채우기")
print("=" * 80 + "\n")

fill_missing_industry()

print("\n완료!")
