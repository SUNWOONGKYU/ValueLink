#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gemini 2.5 Flash로 남은 2개 회사 뉴스 찾기"""
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from supabase import create_client
import codecs
import json
import time

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# news_title이 없는 Deal
deals = supabase.table("deals").select("*").is_("news_title", "null").execute()

print(f"Gemini 2.5 Flash로 뉴스 찾기: {len(deals.data)}개\n")

for deal in deals.data:
    company = deal['company_name']
    print(f"{company} 검색 중...")
    
    prompt = f"""
다음 회사의 2025-2026년 투자유치 뉴스를 찾아주세요:

회사명: {company}

다음 정보를 JSON 형식으로 출력:
{{
    "title": "뉴스 제목",
    "url": "뉴스 URL",
    "date": "YYYY-MM-DD",
    "media": "언론사명"
}}

조건:
- 실제 투자유치 뉴스만 (기업정보 페이지 제외)
- 가장 최신 뉴스
- THE VC 포트폴리오 제외
"""
    
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            
            # JSON 추출
            if "```json" in text:
                json_start = text.find("```json") + 7
                json_end = text.rfind("```")
                if json_end > json_start:
                    text = text[json_start:json_end].strip()
            
            result = json.loads(text)
            
            print(f"  ✅ 제목: {result.get('title')}")
            print(f"     URL: {result.get('url')}")
            print(f"     날짜: {result.get('date')}")
            print(f"     언론: {result.get('media')}")
            
            supabase.table("deals").update({
                'news_title': result.get('title'),
                'news_url': result.get('url'),
                'news_date': result.get('date'),
                'site_name': result.get('media')
            }).eq("id", deal['id']).execute()
            
        else:
            print(f"  ❌ Gemini 응답 없음")
    
    except Exception as e:
        print(f"  ❌ 오류: {str(e)[:50]}")
    
    time.sleep(2)
    print()

print("완료")
