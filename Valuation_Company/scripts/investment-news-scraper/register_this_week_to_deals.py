#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이번 주 수집된 투자 뉴스를 Deal 테이블에 등록
회사당 점수가 가장 높은 뉴스 하나만 선택
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
from collections import defaultdict

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_deal_info_with_gemini(title, url):
    """Gemini로 뉴스에서 Deal 정보 추출"""
    prompt = f"""
다음 투자유치 뉴스에서 정보를 추출해주세요:

제목: {title}

JSON 형식으로만 답변:
{{
    "company_name": "회사명",
    "industry": "업종 (AI/헬스케어/핀테크 등)",
    "stage": "투자단계 (시드/프리A/시리즈A 등)",
    "investors": "투자자 (콤마로 구분)",
    "amount": "투자금액 (억원 숫자만)",
    "location": "지역",
    "employees": "직원수 (숫자만)"
}}

조건:
- 정보 없으면 null
- amount는 억원 단위 숫자만 (50억 → 50)
- employees는 숫자만
- 투자유치 뉴스가 아니면 company_name을 null로
"""

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=512,
                response_mime_type='application/json'
            )
        )

        if response and hasattr(response, 'text'):
            text = response.text.strip()
            result = json.loads(text)
            return result

        return None
    except Exception as e:
        return None

def calculate_score(info):
    """기사 점수 계산 (11점 만점)"""
    score = 0

    if info.get('amount'):
        score += 3
    if info.get('investors'):
        score += 3
    if info.get('stage'):
        score += 2
    if info.get('industry'):
        score += 1
    if info.get('location'):
        score += 1
    if info.get('employees'):
        score += 1

    return score

def register_to_deals():
    """이번 주 뉴스를 Deal 테이블에 등록"""

    # Step 1: 이번 주 뉴스 가져오기
    articles = supabase.table('investment_news_articles')\
        .select('*')\
        .or_('published_date.eq.2026-01-27,published_date.eq.2026-01-28')\
        .order('published_date', desc=True)\
        .execute()

    print(f"📊 이번 주 뉴스: {len(articles.data)}개\n")
    print("Step 1: Gemini로 회사명 및 정보 추출 중...\n")

    # Step 2: 각 뉴스에서 정보 추출
    news_with_info = []

    for i, article in enumerate(articles.data, 1):
        title = article['article_title']

        print(f"[{i}/{len(articles.data)}] {title[:50]}... ", end='')

        info = extract_deal_info_with_gemini(title, article['article_url'])

        if info and info.get('company_name'):
            score = calculate_score(info)
            news_with_info.append({
                'article': article,
                'info': info,
                'score': score
            })
            print(f"✅ {info['company_name']} (점수: {score})")
        else:
            print("❌ 회사명 없음")

        time.sleep(0.8)

    print(f"\n✅ 총 {len(news_with_info)}개 회사 발견\n")

    # Step 3: 회사별로 그룹핑하고 최고 점수 선택
    print("Step 2: 회사별 최고 점수 뉴스 선택...\n")

    company_best = {}

    for news in news_with_info:
        company = news['info']['company_name']
        score = news['score']

        if company not in company_best or score > company_best[company]['score']:
            company_best[company] = news

    print(f"✅ 유일한 회사: {len(company_best)}개\n")

    # Step 4: Deal 테이블 중복 체크
    print("Step 3: Deal 테이블에 등록...\n")

    existing_deals = supabase.table('deals').select('company_name').execute()
    existing_companies = {deal['company_name'] for deal in existing_deals.data}

    last_deal = supabase.table('deals').select('number').order('number', desc=True).limit(1).execute()
    next_number = last_deal.data[0]['number'] + 1 if last_deal.data else 1

    registered = 0
    skipped_duplicate = 0

    for company, news in sorted(company_best.items()):
        article = news['article']
        info = news['info']
        score = news['score']

        print(f"🔍 {company} (점수: {score})... ", end='')

        # 중복 체크
        if company in existing_companies:
            print("⚠️  이미 존재")
            skipped_duplicate += 1
            continue

        # Deal 테이블에 등록
        try:
            supabase.table('deals').insert({
                'number': next_number,
                'company_name': company,
                'industry': info.get('industry'),
                'stage': info.get('stage'),
                'investors': info.get('investors'),
                'amount': info.get('amount'),
                'location': info.get('location'),
                'news_title': article['article_title'],
                'news_url': article['article_url'],
                'news_date': article['published_date'],
                'site_name': article['site_name'],
            }).execute()

            print(f"✅ 등록 (#{next_number})")

            existing_companies.add(company)
            next_number += 1
            registered += 1

        except Exception as e:
            print(f"❌ 오류: {str(e)[:40]}")

    print(f"\n" + "="*80)
    print(f"📊 결과:")
    print(f"  - 이번 주 뉴스: {len(articles.data)}개")
    print(f"  - 투자 회사 발견: {len(news_with_info)}개")
    print(f"  - 유일한 회사: {len(company_best)}개")
    print(f"  - 신규 등록: {registered}개")
    print(f"  - 이미 존재: {skipped_duplicate}개")
    print(f"  - 총 Deal 수: {next_number - 1}개")
    print("="*80)

# 메인
print("=" * 80)
print("이번 주 투자 뉴스 → Deal 테이블 등록 (회사당 최고 점수 1개)")
print("=" * 80 + "\n")

register_to_deals()

print("\n완료!")
