#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 기사 선정 및 Deal 테이블 이동
- investment_news_articles에서 기사 선정
- Gemini API로 정보 추출
- deals 테이블에 저장
"""

import os
import json
import requests
import time
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
import google.generativeai as genai
from fetch_article_content import fetch_article_content
from search_company_info import enrich_company_info

# .env 로드
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Supabase 헤더
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# 사이트 랭킹 (점수가 낮을수록 우선)
SITE_RANKING = {
    9: 1,   # 벤처스퀘어
    11: 2,  # 스타트업투데이
    13: 3,  # 아웃스탠딩
    8: 4,   # 더브이씨
    12: 5,  # 스타트업엔
    22: 6,  # 블로터
    23: 7,  # 이코노미스트
    10: 8,  # 플래텀
    19: 9,  # AI타임스
    21: 10  # 뉴스톱
}

def calculate_article_score(article):
    """기사 점수 계산 (11점 만점)"""
    score = 0
    title = article.get('article_title', '')
    snippet = article.get('content_snippet', '') or ''
    content = f"{title} {snippet}"

    # 1. 투자금액 (3점)
    amount_keywords = ['억원', '억 원', '$', '달러', 'M', '만원', '규모']
    if any(kw in content for kw in amount_keywords):
        score += 3

    # 2. 투자자 (3점)
    investor_keywords = ['벤처스', '인베스트', '투자', '캐피탈', 'VC', '투자사']
    if any(kw in content for kw in investor_keywords):
        score += 3

    # 3. 투자단계 (2점)
    stage_keywords = ['시리즈', 'Series', '프리', 'Pre', '시드', 'Seed', '브릿지', 'Bridge']
    if any(kw in content for kw in stage_keywords):
        score += 2

    # 4. 업종 (1점)
    industry_keywords = ['AI', '인공지능', '헬스케어', '의료', '핀테크', '금융', '푸드', '이커머스', '커머스']
    if any(kw in content for kw in industry_keywords):
        score += 1

    # 5. 지역 (1점)
    location_keywords = ['판교', '강남', '서울', '부산', '대구', '본사', '위치']
    if any(kw in content for kw in location_keywords):
        score += 1

    # 6. 직원수 (1점)
    employee_keywords = ['직원', '임직원', '팀원', '명']
    if any(kw in content for kw in employee_keywords):
        score += 1

    return score

def select_best_article(articles):
    """같은 기업의 기사 중 최적의 기사 선정"""
    if len(articles) == 1:
        return articles[0]

    # 점수 계산
    for article in articles:
        article['score'] = calculate_article_score(article)
        snippet = article.get('content_snippet', '') or ''
        article['content_length'] = len(snippet)

    # 정렬: 점수 → 글자수 → 발행일 → 사이트랭킹
    # 점수 높을수록, 글자수 많을수록, 날짜 최신일수록, 사이트랭킹 낮을수록 우선
    articles.sort(key=lambda x: (
        -x['score'],                              # 내림차순
        -x['content_length'],                     # 내림차순
        x.get('published_date', ''),              # 오름차순 (ISO 형식이므로 최신이 뒤)
        SITE_RANKING.get(x['site_number'], 999)   # 오름차순
    ), reverse=False)

    # published_date는 문자열이므로 별도 처리
    articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)  # 최신 우선
    articles.sort(key=lambda x: SITE_RANKING.get(x['site_number'], 999))    # 랭킹 우선
    articles.sort(key=lambda x: x['content_length'], reverse=True)           # 글자수 우선
    articles.sort(key=lambda x: x['score'], reverse=True)                    # 점수 최우선

    return articles[0]

def extract_deal_info(article):
    """Gemini API로 Deal 정보 추출 (개선된 프롬프트 + 본문 크롤링)"""
    title = article.get('article_title', '')
    snippet = article.get('content_snippet', '') or ''
    url = article.get('article_url', '')

    # 본문이 없으면 크롤링 시도
    if not snippet and url:
        print(f"  [INFO] Fetching article content from URL...")
        snippet = fetch_article_content(url)
        if snippet:
            print(f"  [SUCCESS] Content fetched ({len(snippet)} chars)")
        else:
            print(f"  [WARNING] Failed to fetch content")

    # 개선된 프롬프트: 더 구체적이고 예시 포함
    prompt = f"""
당신은 한국 스타트업 투자 뉴스 분석 전문가입니다.
아래 뉴스 기사에서 투자 정보를 정확하게 추출하세요.

【기사 정보】
제목: {title}
내용: {snippet if snippet else '(본문 없음)'}

【추출 규칙】
1. company_name: 투자를 받은 기업명 (투자자가 아님!)
   - 예: "카카오가 A기업에 투자" → "A기업" (카카오 아님)
   - 따옴표 안의 기업명 우선
   - 쉼표 앞 단어 확인

2. ceo: 대표자 이름
   - "대표 홍길동", "CEO 김철수" 형태
   - 영문/한글 모두 가능

3. founded: 설립일 (YYYY-MM-DD 형식)
   - "2020년 설립" → "2020-01-01"
   - 월/일 정보 없으면 01-01 사용

4. industry: 업종 (한 단어로)
   - AI, 헬스케어, 핀테크, 푸드테크, 이커머스, SaaS 등
   - 가장 대표적인 업종 1개만

5. stage: 투자 단계
   - 시드, 프리A, 시리즈A, 시리즈B, 시리즈C 등
   - "Pre-A" → "프리A"로 통일

6. investors: 투자자 (쉼표로 구분)
   - 예: "알토스벤처스, 삼성벤처투자"
   - 리드 투자자 먼저
   - VC/투자사만 (개인 투자자 제외)

7. amount: 투자 금액 (숫자만, 단위: 억원)
   - **중요**: 반드시 억원 단위로 변환!
   - "100억원" → 100
   - "50억 규모" → 50
   - "1조원" → 10000 (1조 = 10000억)
   - "$10M" (1000만 달러) → 130 (환율 1300원: 10M * 1300 / 1억)
   - "$100M" (1억 달러) → 1300
   - "65억 달러" → 84500 (65 * 1300)
   - 일반적 범위: 1 ~ 10000 (1억 ~ 1조)

8. total_funding: 누적 투자액 (억원)
   - "누적 200억" → 200
   - 정보 없으면 null

9. location: 본사 지역
   - 서울, 경기, 판교, 강남, 부산 등
   - 시/구 단위까지만

10. employees: 직원수 (숫자만)
    - "50명" → 50
    - "약 100명" → 100

【출력 형식】
반드시 아래 JSON 형식만 출력하세요. 다른 텍스트 없이 JSON만!

{{
  "company_name": "기업명 또는 null",
  "ceo": "대표자명 또는 null",
  "founded": "YYYY-MM-DD 또는 null",
  "industry": "업종 또는 null",
  "stage": "투자단계 또는 null",
  "investors": "투자자1, 투자자2 또는 null",
  "amount": 숫자 또는 null,
  "total_funding": 숫자 또는 null,
  "location": "지역 또는 null",
  "employees": 숫자 또는 null
}}

지금 시작하세요:
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            result = response.text.strip()

            # JSON 파싱
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            result = result.strip()

            deal_info = json.loads(result)
            time.sleep(0.5)  # Rate limiting
            return deal_info
        except Exception as e:
            if '429' in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4초
                print(f"[WARNING] Rate limit, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[ERROR] Gemini API error: {e}")
                return None

def validate_and_fix_amount(amount):
    """투자 금액 검증 및 수정"""
    if not amount or amount is None:
        return None

    try:
        amount = float(amount)

        # 비정상적으로 큰 금액 (100조 이상) - 단위 오류로 추정
        if amount > 1000000:  # 100조
            # 10000으로 나누기 (억 단위 오류)
            amount = amount / 10000
            print(f"  [FIX] Amount too large, divided by 10000: {amount}")

        # 비정상적으로 작은 금액 (1000만원 이하)
        if amount < 0.1:
            return None

        # 일반적인 투자 금액 범위: 1억 ~ 10조
        if 0.1 <= amount <= 100000:
            return amount
        else:
            print(f"  [WARNING] Unusual amount: {amount}억원")
            return amount

    except (ValueError, TypeError):
        return None

def insert_to_deals(article, deal_info):
    """deals 테이블에 삽입"""
    # null 값을 None으로 변환
    for key in deal_info:
        if deal_info[key] == 'null' or deal_info[key] == '':
            deal_info[key] = None

    # 금액 검증
    deal_info['amount'] = validate_and_fix_amount(deal_info.get('amount'))
    deal_info['total_funding'] = validate_and_fix_amount(deal_info.get('total_funding'))

    deal_data = {
        'company_name': deal_info.get('company_name'),
        'ceo': deal_info.get('ceo'),  # 새 필드
        'founded': deal_info.get('founded'),  # 새 필드
        'industry': deal_info.get('industry'),
        'stage': deal_info.get('stage'),
        'investors': deal_info.get('investors'),
        'amount': deal_info.get('amount'),
        'total_funding': deal_info.get('total_funding'),  # 새 필드
        'location': deal_info.get('location'),
        'employees': deal_info.get('employees'),
        'news_title': article.get('article_title'),
        'news_url': article.get('article_url'),
        'news_date': article.get('published_date'),
        'site_name': article.get('site_name')
    }

    url = f"{SUPABASE_URL}/rest/v1/deals"
    response = requests.post(url, headers=headers, json=deal_data)

    if response.status_code in [200, 201]:
        print(f"[SUCCESS] Deal saved: {deal_info.get('company_name')}")
        return True
    else:
        print(f"[ERROR] Failed to save deal: {response.text}")
        return False

def main():
    print("=" * 60)
    print("Investment News Article Selection & Deal Table Migration")
    print("=" * 60)

    # 1. investment_news_articles에서 모든 기사 가져오기
    url = f"{SUPABASE_URL}/rest/v1/investment_news_articles?select=*"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch articles: {response.text}")
        return

    articles = response.json()
    print(f"[INFO] Total {len(articles)} articles fetched")

    # 2. 기업명 기준으로 그룹핑 (Gemini로 기업명 추출)
    print("\n[INFO] Extracting company names...")
    company_groups = defaultdict(list)

    for idx, article in enumerate(articles):
        # 간단한 프롬프트로 기업명만 추출
        title = article.get('article_title', '')
        if not title:
            continue

        prompt = f"다음 기사 제목에서 투자받은 기업명만 추출하세요. 기업명만 출력하세요 (추가 설명 없이).\n\n제목: {title}"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                company_name = response.text.strip()

                # 디버그 출력 (처음 10개)
                if idx < 10:
                    print(f"  [DEBUG {idx+1}] Title: {title[:50]}")
                    print(f"  [DEBUG {idx+1}] Gemini: '{company_name}'")

                # 다양한 "없음" 케이스 필터링
                skip_keywords = ['없음', 'None', '기업명 없음', '알 수 없음', 'N/A', '미상', '불명']
                if company_name and not any(skip in company_name for skip in skip_keywords):
                    company_groups[company_name].append(article)
                    if idx < 10:
                        print(f"  [DEBUG {idx+1}] ✅ Added: {company_name}")

                time.sleep(0.6)  # Rate limiting
                break  # 성공하면 루프 종료
            except Exception as e:
                if '429' in str(e) and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"[WARNING] Rate limit hit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    if idx < 10:
                        print(f"  [DEBUG {idx+1}] ERROR: {str(e)[:100]}")
                    break

        # 진행 상황 표시 (10개마다)
        if (idx + 1) % 10 == 0:
            print(f"  Progress: {idx + 1}/{len(articles)} articles processed")

    print(f"[SUCCESS] {len(company_groups)} companies grouped")

    # 3. 각 기업별 최적 기사 선정
    print("\n[INFO] Selecting best articles...")
    selected_articles = []

    for company_name, articles_list in company_groups.items():
        best_article = select_best_article(articles_list)
        best_article['extracted_company_name'] = company_name
        selected_articles.append(best_article)

        if len(articles_list) > 1:
            print(f"  {company_name}: {len(articles_list)} articles -> selected (score: {best_article['score']})")

    print(f"[SUCCESS] Total {len(selected_articles)} articles selected")

    # 4. Deal 정보 추출 및 저장
    print("\n[INFO] Saving to deals table...")
    success_count = 0

    for article in selected_articles:
        title = article.get('article_title', 'Unknown')
        print(f"\n[PROCESSING] {title[:50]}...")

        # Gemini로 정보 추출
        deal_info = extract_deal_info(article)

        if deal_info:
            # 추가 정보 검색으로 보강 (선택적)
            company_name = deal_info.get('company_name')
            if company_name and company_name not in ['없음', 'None', '-']:
                deal_info = enrich_company_info(company_name, deal_info)

            # deals 테이블에 삽입
            if insert_to_deals(article, deal_info):
                success_count += 1

    print("\n" + "=" * 60)
    print(f"[COMPLETE] {success_count}/{len(selected_articles)} deals saved successfully")
    print("=" * 60)

if __name__ == '__main__':
    main()
