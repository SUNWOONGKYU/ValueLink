#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News 기사 품질 테스트
- 50개 샘플 추출
- Gemini로 정보 추출 시도
- 성공률 측정
"""

import os
import random
import requests
import time
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def extract_deal_info(title, snippet, url):
    """
    Gemini로 딜 정보 추출

    Returns:
        dict with 11 fields
    """

    prompt = f"""
다음 투자 뉴스 기사에서 정보를 추출하세요.

제목: {title}
요약: {snippet if snippet else 'N/A'}
URL: {url}

추출할 정보 (JSON 형식으로 응답):
{{
    "company_name": "기업명 (필수)",
    "amount": "투자금액 (예: 100억원, $10M)",
    "investors": "투자자 (여러 명이면 쉼표로 구분)",
    "stage": "투자단계 (시리즈A, Pre-A, Seed 등)",
    "industry": "업종/분야",
    "location": "지역/본사위치",
    "employees": "직원수",
    "ceo": "대표이사",
    "founded": "설립일",
    "description": "기업 설명 (한 줄)",
    "confidence": "추출 신뢰도 (1-10)"
}}

정보가 없으면 null로 표시하세요.
반드시 JSON만 응답하세요.
"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # JSON 파싱 시도
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]

        import json
        result = json.loads(result_text)
        return result

    except Exception as e:
        print(f"  [ERROR] Gemini extraction failed: {str(e)[:100]}")
        return None


def test_url_redirect(google_url):
    """
    Google News 리디렉션 URL → 실제 URL 변환 시도
    """

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(google_url, headers=headers, timeout=10, allow_redirects=True)

        final_url = response.url

        # Google URL이 아니면 성공
        if 'news.google.com' not in final_url:
            return final_url
        else:
            return None

    except Exception as e:
        return None


def test_google_news_quality():
    """Google News 기사 품질 테스트"""

    print("="*60)
    print("Google News Quality Test")
    print("="*60)

    # 1. Google News 기사 전체 조회
    articles_result = supabase.table('investment_news_articles').select('*').eq('site_number', 100).execute()

    all_articles = articles_result.data
    print(f"\nTotal Google News articles: {len(all_articles)}")

    # 2. 랜덤 샘플 50개 추출
    sample_size = min(50, len(all_articles))
    sample_articles = random.sample(all_articles, sample_size)

    print(f"Testing {sample_size} random samples...\n")

    # 3. 각 샘플 테스트
    results = {
        'total': sample_size,
        'extraction_success': 0,
        'url_redirect_success': 0,
        'field_success': {
            'company_name': 0,
            'amount': 0,
            'investors': 0,
            'stage': 0,
            'industry': 0,
            'location': 0,
            'employees': 0,
            'ceo': 0,
            'founded': 0,
            'description': 0
        },
        'high_confidence': 0,  # confidence >= 7
        'samples': []
    }

    for idx, article in enumerate(sample_articles, 1):
        print(f"\n[{idx}/{sample_size}] {article['article_title'][:50]}...")

        # URL 리디렉션 테스트
        real_url = test_url_redirect(article['article_url'])
        if real_url:
            results['url_redirect_success'] += 1
            print(f"  [OK] URL redirect success")
            print(f"     Real URL: {real_url[:80]}...")
        else:
            print(f"  [FAIL] URL redirect failed (stays at Google)")

        # Gemini 정보 추출 테스트
        extracted = extract_deal_info(
            article['article_title'],
            article.get('content_snippet'),
            real_url if real_url else article['article_url']
        )

        if extracted:
            results['extraction_success'] += 1

            # 각 필드 성공 여부
            for field in results['field_success'].keys():
                if extracted.get(field) and extracted[field] != 'null':
                    results['field_success'][field] += 1

            # 신뢰도 체크
            confidence = extracted.get('confidence', 0)
            if isinstance(confidence, (int, float)) and confidence >= 7:
                results['high_confidence'] += 1

            # 샘플 저장 (처음 5개만)
            if len(results['samples']) < 5:
                results['samples'].append({
                    'title': article['article_title'][:60],
                    'extracted': extracted,
                    'real_url': real_url[:80] if real_url else None
                })

            print(f"  [OK] Extraction success (confidence: {confidence})")
        else:
            print(f"  [FAIL] Extraction failed")

        # Rate limiting
        time.sleep(2)

    # 4. 결과 리포트
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)

    print(f"\n[Overall]")
    print(f"  Total samples: {results['total']}")
    print(f"  URL redirect success: {results['url_redirect_success']} ({results['url_redirect_success']/results['total']*100:.1f}%)")
    print(f"  Extraction success: {results['extraction_success']} ({results['extraction_success']/results['total']*100:.1f}%)")
    print(f"  High confidence (>=7): {results['high_confidence']} ({results['high_confidence']/results['total']*100:.1f}%)")

    print(f"\n[Field Extraction Success Rate]")
    for field, count in results['field_success'].items():
        rate = count / results['extraction_success'] * 100 if results['extraction_success'] > 0 else 0
        print(f"  {field:15s}: {count:2d}/{results['extraction_success']} ({rate:5.1f}%)")

    print(f"\n[Sample Extractions (first 5)]")
    for idx, sample in enumerate(results['samples'], 1):
        print(f"\n{idx}. {sample['title']}...")
        print(f"   Company: {sample['extracted'].get('company_name', 'N/A')}")
        print(f"   Amount: {sample['extracted'].get('amount', 'N/A')}")
        print(f"   Investors: {sample['extracted'].get('investors', 'N/A')}")
        print(f"   Stage: {sample['extracted'].get('stage', 'N/A')}")
        print(f"   Confidence: {sample['extracted'].get('confidence', 'N/A')}")
        if sample['real_url']:
            print(f"   Real URL: {sample['real_url']}...")

    # 5. 결론
    print("\n" + "="*60)
    print("Conclusion")
    print("="*60)

    url_rate = results['url_redirect_success'] / results['total'] * 100
    extract_rate = results['extraction_success'] / results['total'] * 100
    company_rate = results['field_success']['company_name'] / results['extraction_success'] * 100 if results['extraction_success'] > 0 else 0

    print(f"\n1. URL 리디렉션: {url_rate:.1f}% 성공")
    if url_rate < 50:
        print("   [FAIL] 절반 이상이 Google URL에 갇혀있음")
    else:
        print("   [OK] 대부분 실제 URL 획득 가능")

    print(f"\n2. 정보 추출: {extract_rate:.1f}% 성공")
    if extract_rate < 70:
        print("   [FAIL] 추출 성공률이 낮음")
    else:
        print("   [OK] 추출 성공률 양호")

    print(f"\n3. 기업명 추출: {company_rate:.1f}% 성공")
    if company_rate < 80:
        print("   [FAIL] 기업명(필수 정보) 추출률 낮음")
    else:
        print("   [OK] 기업명 추출 성공률 우수")

    print(f"\n4. 권장 사항:")
    if url_rate >= 50 and extract_rate >= 70 and company_rate >= 80:
        print("   [RECOMMEND] Google News 중심 + 11개 소스 보완 추천")
    elif extract_rate >= 50:
        print("   [WARNING] Google News 사용 가능, 단 품질 체크 필수")
    else:
        print("   [RECOMMEND] 11개 직접 소스 유지 추천")


if __name__ == '__main__':
    test_google_news_quality()
