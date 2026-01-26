#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
핵심 3가지 정보 분석
1. 투자받은 회사 이름
2. 투자회사 이름 (투자자)
3. 투자금액
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')


def extract_core_info(title, snippet):
    """
    기사에서 핵심 3가지 정보 추출
    - 투자받은 회사
    - 투자자
    - 투자금액
    """

    prompt = f"""
다음 투자 뉴스에서 정보를 추출하세요.

제목: {title}
요약: {snippet if snippet else 'N/A'}

다음 정보만 추출하세요 (JSON):
{{
    "company": "투자 받은 회사 이름",
    "investor": "투자자 이름 (여러 명이면 쉼표로 구분)",
    "amount": "투자 금액"
}}

정보가 없으면 null로 표시하세요.
반드시 JSON만 응답하세요.
"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]

        result = json.loads(result_text)
        return result
    except:
        return None


def analyze_core_data():
    """핵심 3가지 정보 분석"""

    print("="*60)
    print("Core Data Analysis (Company, Investor, Amount)")
    print("="*60)

    # Google News 715개 조회
    result = supabase.table('investment_news_articles').select('*').eq('site_number', 100).execute()

    articles = result.data
    print(f"\nTotal Google News articles: {len(articles)}")

    # 현재 데이터베이스 필드 기준 분석
    print(f"\n{'='*60}")
    print("Current Database Fields")
    print(f"{'='*60}")

    has_amount = [a for a in articles if a.get('has_amount')]
    has_investors = [a for a in articles if a.get('has_investors')]

    # 3가지 모두 있는 기사 (데이터베이스 필드 기준)
    has_all_three = [
        a for a in articles
        if a.get('has_amount') and a.get('has_investors')
    ]

    print(f"\n1. 투자금액 포함: {len(has_amount)}개 ({len(has_amount)/len(articles)*100:.1f}%)")
    print(f"2. 투자자 포함: {len(has_investors)}개 ({len(has_investors)/len(articles)*100:.1f}%)")
    print(f"3. 둘 다 포함: {len(has_all_three)}개 ({len(has_all_three)/len(articles)*100:.1f}%)")

    # 샘플 확인 (둘 다 포함된 기사 10개)
    print(f"\n{'='*60}")
    print("Sample: Articles with Both Amount & Investor (10개)")
    print(f"{'='*60}")

    for idx, article in enumerate(has_all_three[:10], 1):
        print(f"\n{idx}. {article['article_title'][:60]}...")
        print(f"   Score: {article.get('score', 0)}")
        print(f"   URL: {article['article_url'][:80]}...")

    # Gemini로 재확인 (샘플 50개)
    print(f"\n{'='*60}")
    print("Re-verification with Gemini (50개 샘플)")
    print(f"{'='*60}")

    import random
    sample_size = min(50, len(articles))
    sample_articles = random.sample(articles, sample_size)

    verification_results = {
        'total': sample_size,
        'has_company': 0,
        'has_investor': 0,
        'has_amount': 0,
        'has_all_three': 0
    }

    all_three_samples = []

    for idx, article in enumerate(sample_articles, 1):
        print(f"\n[{idx}/{sample_size}] {article['article_title'][:50]}...")

        extracted = extract_core_info(article['article_title'], article.get('content_snippet'))

        if extracted:
            company = extracted.get('company')
            investor = extracted.get('investor')
            amount = extracted.get('amount')

            if company and company != 'null':
                verification_results['has_company'] += 1
            if investor and investor != 'null':
                verification_results['has_investor'] += 1
            if amount and amount != 'null':
                verification_results['has_amount'] += 1

            if company and investor and amount and \
               company != 'null' and investor != 'null' and amount != 'null':
                verification_results['has_all_three'] += 1
                all_three_samples.append({
                    'title': article['article_title'],
                    'company': company,
                    'investor': investor,
                    'amount': amount
                })

            print(f"  Company: {company if company else 'N/A'}")
            print(f"  Investor: {investor if investor else 'N/A'}")
            print(f"  Amount: {amount if amount else 'N/A'}")
        else:
            print(f"  [FAIL] Extraction failed")

        import time
        time.sleep(2)

    # 재확인 결과
    print(f"\n{'='*60}")
    print("Re-verification Results")
    print(f"{'='*60}")

    print(f"\n[Sample of {sample_size} articles]")
    print(f"  회사명 추출: {verification_results['has_company']}개 ({verification_results['has_company']/sample_size*100:.1f}%)")
    print(f"  투자자 추출: {verification_results['has_investor']}개 ({verification_results['has_investor']/sample_size*100:.1f}%)")
    print(f"  투자금액 추출: {verification_results['has_amount']}개 ({verification_results['has_amount']/sample_size*100:.1f}%)")
    print(f"  3가지 모두: {verification_results['has_all_three']}개 ({verification_results['has_all_three']/sample_size*100:.1f}%)")

    # 전체 추정
    estimated_all_three = int((verification_results['has_all_three'] / sample_size) * len(articles))
    print(f"\n[Estimated for all 715 articles]")
    print(f"  3가지 모두 포함 추정: 약 {estimated_all_three}개")

    # 3가지 모두 있는 샘플 출력
    if all_three_samples:
        print(f"\n{'='*60}")
        print("Perfect Samples (3가지 모두 포함)")
        print(f"{'='*60}")

        for idx, sample in enumerate(all_three_samples[:5], 1):
            print(f"\n{idx}. {sample['title'][:60]}...")
            print(f"   회사: {sample['company']}")
            print(f"   투자자: {sample['investor']}")
            print(f"   금액: {sample['amount']}")

    # 결론
    print(f"\n{'='*60}")
    print("Conclusion")
    print(f"{'='*60}")

    print(f"\n데이터베이스 필드 기준:")
    print(f"  - 투자금액 + 투자자: {len(has_all_three)}개")

    print(f"\nGemini 재확인 기준 (50개 샘플):")
    print(f"  - 3가지 모두: {verification_results['has_all_three']}개 ({verification_results['has_all_three']/sample_size*100:.1f}%)")
    print(f"  - 전체 추정: 약 {estimated_all_three}개")

    if estimated_all_three >= 100:
        print(f"\n✅ 결론: 약 {estimated_all_three}개의 완성도 높은 Deal 생성 가능")
    elif estimated_all_three >= 50:
        print(f"\n⚠️ 결론: 약 {estimated_all_three}개 - 보통 수준")
    else:
        print(f"\n❌ 결론: 약 {estimated_all_three}개 - 적음, 추가 보강 필요")


if __name__ == '__main__':
    analyze_core_data()
