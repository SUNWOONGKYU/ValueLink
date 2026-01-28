#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Grounding (웹 검색) 테스트
Google Search를 활용한 최신 뉴스 검색
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerativeModel, types

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("=" * 80)
print("Gemini Grounding (웹 검색) 테스트")
print("=" * 80)

def search_with_grounding(company_name):
    """Google Search Grounding을 활용한 검색"""

    # Grounding 설정
    model = GenerativeModel(
        'gemini-2.5-flash',
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )

    prompt = f"""
인터넷에서 다음 한국 스타트업의 최신 투자 유치 뉴스를 검색해주세요:

**회사명**: {company_name}

**검색 조건**:
- 투자 유치 관련 기사 (시리즈A, 시드, 브릿지 등)
- 2025년 12월 ~ 2026년 1월 사이 발행된 기사
- 한국 언론사 기사 (벤처스퀘어, WOWTALE, 더벨, 플래텀, 이투데이 등)
- 실제 투자 금액이나 투자자가 명시된 기사 우선

**출력 형식**:
각 기사마다 다음 정보를 JSON 배열로:
```json
[
  {{
    "article_title": "기사 제목",
    "article_url": "기사 URL",
    "site_name": "언론사명",
    "published_date": "YYYY-MM-DD",
    "summary": "투자자, 금액, 단계 등 핵심 내용"
  }}
]
```

기사를 찾지 못했으면 `[]` 반환.
"""

    try:
        print(f"\n🔍 {company_name} 검색 중 (웹 검색 활성화)...")

        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.1,
                'top_p': 0.8,
                'max_output_tokens': 4096,  # 더 긴 응답
            }
        )

        text = response.text.strip()

        print(f"\n  📝 Gemini 응답 (전체):")
        print(f"  {text}")
        print()

        # JSON 추출
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()

        articles = json.loads(text)
        return articles

    except Exception as e:
        print(f"  ❌ 오류: {e}")
        print(f"  응답: {text[:500] if 'text' in locals() else 'N/A'}")
        return []

def main():
    """테스트 실행"""

    # 몰트봇이 발견한 회사 1개로만 테스트
    test_companies = ["부스터즈", "엘리시젠"]

    for company_name in test_companies:
        print(f"\n{'='*80}")
        print(f"테스트: {company_name}")
        print('='*80)

        articles = search_with_grounding(company_name)

        if articles:
            print(f"\n✅ {len(articles)}개 기사 발견!")
            for idx, article in enumerate(articles, 1):
                print(f"\n  [{idx}]")
                print(f"  제목: {article.get('article_title', 'N/A')}")
                print(f"  URL: {article.get('article_url', 'N/A')}")
                print(f"  언론사: {article.get('site_name', 'N/A')}")
                print(f"  발행일: {article.get('published_date', 'N/A')}")
                print(f"  요약: {article.get('summary', 'N/A')}")
        else:
            print(f"\n❌ 기사 없음")

    print(f"\n{'='*80}")
    print("테스트 완료")
    print('='*80)

if __name__ == "__main__":
    main()
