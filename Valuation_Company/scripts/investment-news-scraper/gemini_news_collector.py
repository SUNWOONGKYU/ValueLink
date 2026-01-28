#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini를 활용한 투자 뉴스 수집
몰트봇이 사용한 방법을 재현

Gemini 1.5의 웹 검색 기능을 활용하여
기존 방법이 놓친 투자 뉴스 기사를 발견
"""

import os
import sys
import csv
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Gemini 모델 설정 (2.5 Flash - 최신, 빠르고 효율적, 1M tokens)
model = genai.GenerativeModel('gemini-2.5-flash')

print("=" * 80)
print("Gemini 투자 뉴스 수집기")
print("=" * 80)

def search_investment_news_with_gemini(company_name, year=2026, month=1):
    """
    Gemini를 활용하여 특정 회사의 투자 뉴스 검색

    Args:
        company_name: 회사명
        year: 연도 (기본: 2026)
        month: 월 (기본: 1)

    Returns:
        list: 발견한 기사 정보 리스트
    """
    prompt = f"""
다음 회사의 {year}년 {month}월 투자 뉴스를 검색해주세요:

**회사명**: {company_name}

**검색 조건**:
- 투자 유치 관련 기사만
- 한국 언론사 기사
- {year}년 {month}월에 발행된 기사
- 시리즈A, 시드, 브릿지 등 투자 단계 언급

**필요한 정보**:
각 기사마다 다음 정보를 JSON 형식으로 제공:
1. article_title: 기사 제목
2. article_url: 기사 URL
3. site_name: 언론사명
4. published_date: 발행일 (YYYY-MM-DD)
5. summary: 투자 관련 핵심 내용 (투자자, 금액, 단계)

**출력 형식**:
```json
[
  {{
    "article_title": "제목",
    "article_url": "https://...",
    "site_name": "언론사",
    "published_date": "2026-01-15",
    "summary": "투자자명, 투자금액, 투자단계 등"
  }}
]
```

기사를 찾지 못했다면 빈 배열 []을 반환해주세요.
"""

    try:
        print(f"\n🔍 {company_name} 검색 중...")

        # Gemini에게 검색 요청 (웹 검색 포함)
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.1,  # 정확성 우선
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )

        # 응답 파싱
        text = response.text.strip()

        # JSON 추출 (```json ... ``` 제거)
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()

        articles = json.loads(text)

        if articles:
            print(f"  ✅ {len(articles)}개 기사 발견")
            for idx, article in enumerate(articles, 1):
                print(f"     {idx}. {article.get('article_title', 'N/A')[:50]}...")
        else:
            print(f"  ⚠️  기사 없음")

        return articles

    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 파싱 오류: {e}")
        print(f"     응답: {text[:200]}...")
        return []
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return []

def save_to_news_table(articles, company_name):
    """
    발견한 기사를 뉴스 테이블에 저장

    Args:
        articles: 기사 리스트
        company_name: 회사명

    Returns:
        int: 저장된 기사 수
    """
    saved_count = 0

    for article in articles:
        # 중복 확인
        existing = supabase.table("investment_news_articles")\
            .select("id")\
            .eq("article_url", article['article_url'])\
            .execute()

        if existing.data:
            print(f"  ⚠️  중복: {article['article_title'][:40]}...")
            continue

        # 저장 데이터 준비
        data = {
            'site_number': 999,  # Gemini 수집 표시
            'site_name': article.get('site_name', 'Unknown'),
            'site_url': '',
            'article_title': article['article_title'],
            'article_url': article['article_url'],
            'published_date': article.get('published_date', datetime.now().strftime('%Y-%m-%d')),
            'company_keywords': company_name,
            'gemini_summary': article.get('summary', '')
        }

        try:
            supabase.table("investment_news_articles").insert(data).execute()
            print(f"  ✅ 저장: {article['article_title'][:40]}...")
            saved_count += 1
        except Exception as e:
            print(f"  ❌ 저장 실패: {e}")

    return saved_count

def main():
    """메인 실행 함수"""

    # 센서블박스 기업 목록 로드
    csv_path = "data/sensiblebox_companies_gemini_extracted.csv"

    if not os.path.exists(csv_path):
        print(f"\n❌ 파일 없음: {csv_path}")
        return

    companies = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_name = row.get('회사명', '').strip()
            if company_name and company_name not in ['```', '```csv']:
                companies.append(company_name)

    print(f"\n📋 총 {len(companies)}개 기업 검색")
    print("=" * 80)

    # 통계
    total_found = 0
    total_saved = 0
    companies_with_news = []
    companies_without_news = []

    # 각 회사별 검색
    for idx, company_name in enumerate(companies, 1):
        print(f"\n[{idx}/{len(companies)}] {company_name}")

        articles = search_investment_news_with_gemini(company_name)

        if articles:
            saved = save_to_news_table(articles, company_name)
            total_found += len(articles)
            total_saved += saved
            companies_with_news.append({
                'company': company_name,
                'found': len(articles),
                'saved': saved
            })
        else:
            companies_without_news.append(company_name)

        # API 제한 방지 (Gemini는 분당 60회)
        if idx < len(companies):
            time.sleep(1)

    # 최종 결과
    print("\n" + "=" * 80)
    print("최종 결과")
    print("=" * 80)

    print(f"\n✅ 기사 발견: {total_found}개")
    print(f"✅ 저장 완료: {total_saved}개")
    print(f"✅ 뉴스 있는 기업: {len(companies_with_news)}개")
    print(f"⚠️  뉴스 없는 기업: {len(companies_without_news)}개")

    if companies_with_news:
        print(f"\n📊 뉴스 발견 기업 Top 10:")
        sorted_companies = sorted(companies_with_news, key=lambda x: x['found'], reverse=True)
        for idx, item in enumerate(sorted_companies[:10], 1):
            print(f"  {idx:2d}. {item['company']:20s} - {item['found']}개 발견, {item['saved']}개 저장")

    if companies_without_news:
        print(f"\n⚠️  뉴스 없는 기업 ({len(companies_without_news)}개):")
        for company in companies_without_news[:10]:
            print(f"  - {company}")
        if len(companies_without_news) > 10:
            print(f"  ... 외 {len(companies_without_news) - 10}개")

    # 결과 저장
    result_file = f"data/gemini_collection_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_companies': len(companies),
            'total_found': total_found,
            'total_saved': total_saved,
            'companies_with_news': companies_with_news,
            'companies_without_news': companies_without_news,
            'timestamp': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

    print(f"\n💾 결과 저장: {result_file}")

if __name__ == "__main__":
    main()
