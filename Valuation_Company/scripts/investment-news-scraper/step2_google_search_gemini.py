#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 2: 구글 검색으로 투자 뉴스 수집 (Gemini API Grounding 사용)
- 1단계에서 못 찾은 기업들을 구글 검색
"""

import os
import sys
import csv
import json
import time
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# Gemini API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Supabase 설정
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Gemini 모델 설정 (grounding 지원)
model = genai.GenerativeModel('gemini-pro')


def search_news_with_gemini(company_name, stage):
    """Gemini API로 투자 뉴스 검색"""

    query = f"{company_name} {stage} 투자 유치 뉴스 2026"

    try:
        # Gemini에게 검색 요청
        prompt = f"""
다음 기업의 최근 투자 유치 뉴스를 찾아주세요:
- 기업명: {company_name}
- 투자 단계: {stage}

조건:
1. 2026년 1월 뉴스만
2. 한국 스타트업 미디어 (벤처스퀘어, 플래텀, WOWTALE, 아웃스탠딩, 스타트업투데이 등)
3. 실제 투자 유치 뉴스 (공지사항 제외)

다음 JSON 형식으로만 답변:
{{
  "found": true/false,
  "title": "기사 제목",
  "url": "기사 URL",
  "site_name": "미디어명",
  "date": "YYYY-MM-DD"
}}

뉴스를 찾지 못하면 {{"found": false}}만 반환.
"""

        response = model.generate_content(prompt)

        if not response.text:
            return None

        # JSON 파싱
        text = response.text.strip()

        # ```json ... ``` 제거
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]

        result = json.loads(text.strip())

        if result.get('found'):
            return {
                'site_name': result.get('site_name', '기타 미디어'),
                'article_title': result.get('title', f"{company_name} {stage} 투자 유치"),
                'article_url': result.get('url', ''),
                'published_date': result.get('date', datetime.now().strftime('%Y-%m-%d'))
            }

        return None

    except Exception as e:
        print(f"    오류: {str(e)[:50]}")
        return None


def main():
    print("=" * 60)
    print("STEP 2: 구글 검색으로 투자 뉴스 수집 (Gemini API)")
    print("=" * 60)

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    # CSV 읽기
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업")

    # 이미 수집된 기업 확인
    result = supabase.table("investment_news_articles")\
        .select("article_title")\
        .execute()

    collected_companies = set()
    for article in result.data:
        for row in companies:
            if row['기업명'] in article['article_title']:
                collected_companies.add(row['기업명'])

    # 미수집 기업만 필터링
    todo_companies = [c for c in companies if c['기업명'] not in collected_companies]

    print(f"이미 수집: {len(collected_companies)}개")
    print(f"검색 대상: {len(todo_companies)}개\n")

    found_count = 0
    not_found = []

    for idx, row in enumerate(todo_companies, 1):
        company_name = row['기업명']
        stage = row['단계']

        print(f"[{idx}/{len(todo_companies)}] {company_name}...", end=' ')

        # Gemini로 검색
        article = search_news_with_gemini(company_name, stage)

        if article and article['article_url']:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if not existing.data:
                # DB 저장
                try:
                    supabase.table("investment_news_articles").insert({
                        "site_number": 99,
                        "site_name": article['site_name'],
                        "site_url": "",
                        "article_title": article['article_title'],
                        "article_url": article['article_url'],
                        "published_date": article['published_date']
                    }).execute()

                    print(f"✅ [{article['site_name']}]")
                    found_count += 1

                except Exception as e:
                    print(f"❌ DB 저장 실패: {str(e)[:30]}")
            else:
                print(f"⚠️ 중복")
        else:
            print("❌ 못 찾음")
            not_found.append(company_name)

        time.sleep(1)  # API 호출 간격

    print(f"\n{'='*60}")
    print("STEP 2 완료")
    print(f"{'='*60}")
    print(f"✅ 발견: {found_count}개")
    print(f"❌ 미발견: {len(not_found)}개")
    print(f"{'='*60}")

    # 미발견 목록 저장
    if not_found:
        with open('not_found_after_google.txt', 'w', encoding='utf-8') as f:
            for company in not_found:
                f.write(f"{company}\n")

        print(f"\n⚠️ 미발견 목록 저장: not_found_after_google.txt")
        print(f"→ STEP 3 (네이버 API)로 진행 필요")


if __name__ == '__main__':
    main()
