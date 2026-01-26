#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11개 언론사 소스 27개 기사 품질 분석
- 투자받은 회사, 투자자, 투자금액 3가지 확인
"""

import os
import json
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
    except Exception as e:
        print(f"  [ERROR] {str(e)[:100]}")
        return None


def analyze_11sources():
    """11개 언론사 소스 품질 분석"""

    print("="*60)
    print("11 Sources Quality Analysis")
    print("="*60)

    # Google News 제외한 나머지 소스 조회
    result = supabase.table('investment_news_articles').select('*').neq('site_number', 100).execute()

    articles = result.data
    print(f"\nTotal articles from 11 sources: {len(articles)}")

    # 소스별 분포
    source_dist = {}
    for article in articles:
        site_num = article['site_number']
        site_name = article['site_name']
        if site_num not in source_dist:
            source_dist[site_num] = {'name': site_name, 'count': 0}
        source_dist[site_num]['count'] += 1

    print(f"\n[Source Distribution]")
    for site_num in sorted(source_dist.keys()):
        info = source_dist[site_num]
        print(f"  {site_num:3d}. {info['name']:20s}: {info['count']:2d} articles")

    # 각 기사 분석
    print(f"\n{'='*60}")
    print("Analyzing Each Article")
    print(f"{'='*60}")

    results = {
        'total': len(articles),
        'has_company': 0,
        'has_investor': 0,
        'has_amount': 0,
        'has_all_three': 0,
        'perfect_articles': []
    }

    for idx, article in enumerate(articles, 1):
        title = article['article_title']
        snippet = article.get('content_snippet')
        site_name = article['site_name']

        print(f"\n[{idx}/{len(articles)}] {site_name}")
        print(f"  {title[:60]}...")

        extracted = extract_core_info(title, snippet)

        if extracted:
            company = extracted.get('company')
            investor = extracted.get('investor')
            amount = extracted.get('amount')

            # null 체크
            has_company = company and company.lower() != 'null' and company != 'N/A'
            has_investor = investor and investor.lower() != 'null' and investor != 'N/A'
            has_amount = amount and amount.lower() != 'null' and amount != 'N/A'

            if has_company:
                results['has_company'] += 1
            if has_investor:
                results['has_investor'] += 1
            if has_amount:
                results['has_amount'] += 1

            if has_company and has_investor and has_amount:
                results['has_all_three'] += 1
                results['perfect_articles'].append({
                    'site_name': site_name,
                    'title': title,
                    'company': company,
                    'investor': investor,
                    'amount': amount,
                    'url': article['article_url']
                })

            print(f"  Company: {company if has_company else '[NONE]'}")
            print(f"  Investor: {investor if has_investor else '[NONE]'}")
            print(f"  Amount: {amount if has_amount else '[NONE]'}")
            print(f"  Result: {'[PERFECT]' if (has_company and has_investor and has_amount) else '[INCOMPLETE]'}")
        else:
            print(f"  [FAIL] Extraction failed")

        time.sleep(2)

    # 최종 결과
    print(f"\n{'='*60}")
    print("Results Summary")
    print(f"{'='*60}")

    print(f"\n[Overall]")
    print(f"  Total articles: {results['total']}")
    print(f"  Company extracted: {results['has_company']} ({results['has_company']/results['total']*100:.1f}%)")
    print(f"  Investor extracted: {results['has_investor']} ({results['has_investor']/results['total']*100:.1f}%)")
    print(f"  Amount extracted: {results['has_amount']} ({results['has_amount']/results['total']*100:.1f}%)")
    print(f"  ALL THREE: {results['has_all_three']} ({results['has_all_three']/results['total']*100:.1f}%)")

    # 완벽한 기사 출력
    if results['perfect_articles']:
        print(f"\n{'='*60}")
        print(f"Perfect Articles ({results['has_all_three']}개)")
        print(f"{'='*60}")

        for idx, article in enumerate(results['perfect_articles'], 1):
            print(f"\n{idx}. [{article['site_name']}]")
            print(f"   {article['title']}")
            print(f"   Company: {article['company']}")
            print(f"   Investor: {article['investor']}")
            print(f"   Amount: {article['amount']}")
            print(f"   URL: {article['url'][:80]}...")
    else:
        print(f"\n[WARNING] No perfect articles found!")

    # 비교
    print(f"\n{'='*60}")
    print("Comparison")
    print(f"{'='*60}")

    print(f"\n[Google News vs 11 Sources]")
    print(f"  Google News:")
    print(f"    - Total: 715 articles")
    print(f"    - Perfect (3 items): ~28 articles (4%)")
    print(f"\n  11 Sources:")
    print(f"    - Total: {results['total']} articles")
    print(f"    - Perfect (3 items): {results['has_all_three']} articles ({results['has_all_three']/results['total']*100:.1f}%)")

    # 결론
    print(f"\n{'='*60}")
    print("Conclusion")
    print(f"{'='*60}")

    google_rate = 4.0  # Google News 4%
    sources_rate = (results['has_all_three'] / results['total']) * 100

    print(f"\n완성도 높은 기사 비율:")
    print(f"  Google News: 4.0%")
    print(f"  11 Sources: {sources_rate:.1f}%")

    if sources_rate > google_rate * 2:
        print(f"\n=> 11 Sources가 Google News보다 2배 이상 우수!")
        print(f"   권장: 11 Sources 중심 + Google News 보완")
    elif sources_rate > google_rate:
        print(f"\n=> 11 Sources가 약간 우수")
        print(f"   권장: 11 Sources + Google News 병행")
    else:
        print(f"\n=> 비슷하거나 Google News가 우수")
        print(f"   권장: Google News 중심")

    # 최종 추정
    google_perfect = 28
    sources_perfect = results['has_all_three']
    total_perfect = google_perfect + sources_perfect

    print(f"\n[Final Estimate]")
    print(f"  Google News: ~28개")
    print(f"  11 Sources: {sources_perfect}개")
    print(f"  Total: 약 {total_perfect}개의 완성도 높은 Deal")


if __name__ == '__main__':
    analyze_11sources()
