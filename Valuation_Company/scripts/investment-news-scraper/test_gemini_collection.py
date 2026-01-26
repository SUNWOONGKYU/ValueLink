#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 뉴스 수집 테스트
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Gemini 2.5-flash (최신 모델)
model = genai.GenerativeModel('gemini-2.5-flash')

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

prompt = f"""
다음 사이트에서 {yesterday} 날짜의 한국 기업 투자 유치 뉴스를 수집해주세요.

사이트:
1. 벤처스퀘어 - https://www.venturesquare.net
2. 플래텀 - https://platum.kr

수집 조건:
- 날짜: {yesterday}
- 한국 기업만 (일본, 외국 기업 제외)
- 투자 유치 관련 (투자, 유치, 시리즈 등)
- 각 사이트당 3-5개

JSON 형식:
[
  {{
    "site_name": "벤처스퀘어",
    "article_title": "기사 제목",
    "article_url": "실제 URL",
    "published_date": "{yesterday}"
  }}
]

JSON만 반환하세요.
"""

print('=' * 60)
print('Gemini 뉴스 수집 테스트')
print('=' * 60)
print(f'\n요청 날짜: {yesterday}')
print('Gemini에게 뉴스 수집 요청 중...\n')

try:
    response = model.generate_content(prompt)
    print(f'응답 길이: {len(response.text)} 문자')
    print(f'\n응답 내용:\n{response.text}\n')

    # JSON 파싱 시도
    text = response.text
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0].strip()
    elif '```' in text:
        text = text.split('```')[1].split('```')[0].strip()

    articles = json.loads(text)

    print('=' * 60)
    print(f'✅ JSON 파싱 성공: {len(articles)}건')
    print('=' * 60)

    for i, article in enumerate(articles, 1):
        print(f'\n[{i}] {article.get("article_title", "N/A")}')
        print(f'    Site: {article.get("site_name", "N/A")}')
        print(f'    URL: {article.get("article_url", "N/A")}')
        print(f'    Date: {article.get("published_date", "N/A")}')

except json.JSONDecodeError as e:
    print(f'\n❌ JSON 파싱 실패: {e}')
    print('Gemini가 JSON 형식으로 응답하지 않았습니다.')

except Exception as e:
    print(f'\n❌ 오류: {e}')
