#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini로 2026-01-28 뉴스 날짜 빠르게 수정
"""

import os
import sys
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# Gemini 클라이언트
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 80)
print("Gemini - 2026-01-28 뉴스 날짜 빠른 수정")
print("=" * 80)

# 2026-01-28 뉴스 조회
deals = supabase.table("deals")\
    .select("*")\
    .eq("news_date", "2026-01-28")\
    .execute()

print(f"\n처리할 Deal: {len(deals.data)}개\n")

update_count = 0

for idx, deal in enumerate(deals.data, 1):
    company = deal['company_name']
    url = deal.get('news_url', '')

    print(f"[{idx}/{len(deals.data)}] {company}")
    print(f"  URL: {url[:70]}...")

    # 간단한 프롬프트
    prompt = f"이 뉴스 기사의 정확한 발행일(게재일)을 찾아주세요. YYYY-MM-DD 형식으로만 답변해주세요: {url}"

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=128,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        if response and hasattr(response, 'text'):
            text = response.text.strip()

            # 날짜 패턴 찾기
            date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', text)
            if date_match:
                extracted_date = date_match.group(1).replace('/', '-')

                print(f"  ✅ {extracted_date}")

                # 업데이트
                supabase.table("deals")\
                    .update({'news_date': extracted_date})\
                    .eq("id", deal['id'])\
                    .execute()

                supabase.table("investment_news_articles")\
                    .update({'published_date': extracted_date})\
                    .eq("article_url", url)\
                    .execute()

                update_count += 1
            else:
                print(f"  ⚠️  날짜 못 찾음: {text[:50]}")
        else:
            print(f"  ⚠️  응답 없음")

    except Exception as e:
        print(f"  ❌ 오류: {str(e)[:50]}")

    time.sleep(1)

print("\n" + "=" * 80)
print(f"✅ {update_count}/{len(deals.data)}개 수정 완료")
print("=" * 80)
