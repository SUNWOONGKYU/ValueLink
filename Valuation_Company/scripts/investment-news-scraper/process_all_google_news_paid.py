#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News 715개 전체 처리 (유료 플랜 - Rate Limiting 없음)
- Model: gemini-2.5-flash
- RPM: 2,000 (매우 빠름)
- 예상 시간: 1-2분
"""

import os
import time
import json
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Gemini 2.5 Flash (유료 플랜)
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

def extract_deal_info(article_id, title, snippet):
    """
    Gemini로 딜 정보 추출

    Returns:
        dict: {article_id, extracted_data, score}
    """

    prompt = f"""
다음 투자 뉴스 기사에서 정보를 추출하세요.

제목: {title}
요약: {snippet if snippet else 'N/A'}

추출할 정보 (JSON 형식으로 응답):
{{
    "company_name": "기업명 (필수)",
    "amount": "투자금액 (예: 100억원, $10M)",
    "investors": "투자자 (여러 명이면 쉼표로 구분)",
    "stage": "투자단계 (시리즈A, Pre-A, Seed 등)",
    "industry": "업종/분야",
    "location": "지역/본사위치",
    "employees": "직원수",
    "score": "11점 만점 점수 (투자금액 3점, 투자자 3점, 단계 2점, 업종 1점, 지역 1점, 직원수 1점)"
}}

정보가 없으면 null로 표시하세요.
반드시 JSON만 응답하세요.
"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # JSON 파싱
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]

        extracted = json.loads(result_text)

        return {
            'article_id': article_id,
            'success': True,
            'extracted': extracted,
            'score': extracted.get('score', 0)
        }

    except Exception as e:
        return {
            'article_id': article_id,
            'success': False,
            'error': str(e)[:100]
        }


def update_article_score(article_id, extracted):
    """데이터베이스 점수 업데이트"""

    update_data = {
        'score': extracted.get('score', 0),
        'has_amount': bool(extracted.get('amount')),
        'has_investors': bool(extracted.get('investors')),
        'has_stage': bool(extracted.get('stage')),
        'has_industry': bool(extracted.get('industry')),
        'has_location': bool(extracted.get('location')),
        'has_employees': bool(extracted.get('employees'))
    }

    try:
        supabase.table('investment_news_articles').update(update_data).eq('id', article_id).execute()
        return True
    except Exception as e:
        print(f"  [ERROR] DB update failed for article {article_id}: {str(e)[:50]}")
        return False


def process_all_google_news_parallel():
    """Google News 715개 병렬 처리 (유료 플랜)"""

    print("="*60)
    print("Processing All Google News Articles (Paid Plan)")
    print("="*60)

    # 1. Google News 기사 전체 조회
    articles_result = supabase.table('investment_news_articles').select('id, article_title, content_snippet').eq('site_number', 100).execute()

    all_articles = articles_result.data
    print(f"\nTotal Google News articles: {len(all_articles)}")
    print(f"Using: gemini-2.5-flash (2,000 RPM)")
    print(f"Estimated time: 1-2 minutes")
    print()

    # 2. 병렬 처리 (ThreadPoolExecutor)
    results = {
        'total': len(all_articles),
        'success': 0,
        'failed': 0,
        'has_company_name': 0,
        'scores': [],
        'failed_ids': []
    }

    start_time = time.time()

    # 최대 50개씩 병렬 처리 (안전하게)
    with ThreadPoolExecutor(max_workers=50) as executor:
        # Submit all tasks
        futures = {
            executor.submit(
                extract_deal_info,
                article['id'],
                article['article_title'],
                article.get('content_snippet')
            ): article for article in all_articles
        }

        # Process results as they complete
        for idx, future in enumerate(as_completed(futures), 1):
            result = future.result()

            if result['success']:
                results['success'] += 1
                extracted = result['extracted']

                # 기업명 체크
                if extracted.get('company_name'):
                    results['has_company_name'] += 1

                # 점수 저장
                score = result['score']
                results['scores'].append(score)

                # DB 업데이트
                update_article_score(result['article_id'], extracted)

                company = extracted.get('company_name', 'N/A')
                if company and company != 'N/A':
                    company_display = company[:30]
                else:
                    company_display = 'N/A'
                print(f"[{idx}/{len(all_articles)}] [OK] Score: {score}, Company: {company_display}")
            else:
                results['failed'] += 1
                results['failed_ids'].append(result['article_id'])
                print(f"[{idx}/{len(all_articles)}] [FAIL] {result.get('error', 'Unknown error')}")

            # 진행 상황 (100개마다)
            if idx % 100 == 0:
                elapsed = time.time() - start_time
                print(f"\n  Progress: {idx}/{len(all_articles)} ({idx/len(all_articles)*100:.1f}%)")
                print(f"  Elapsed: {elapsed:.1f} sec, Success: {results['success']}, Failed: {results['failed']}\n")

    # 3. 최종 결과
    elapsed_time = time.time() - start_time

    print("\n" + "="*60)
    print("Processing Results")
    print("="*60)

    print(f"\n[Overall]")
    print(f"  Total processed: {results['total']}")
    print(f"  Success: {results['success']} ({results['success']/results['total']*100:.1f}%)")
    print(f"  Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print(f"  Has company name: {results['has_company_name']} ({results['has_company_name']/results['success']*100:.1f}% of success)")
    print(f"  Processing time: {elapsed_time:.1f} seconds ({elapsed_time/60:.2f} minutes)")

    if results['scores']:
        avg_score = sum(results['scores']) / len(results['scores'])
        print(f"\n[Scores]")
        print(f"  Average score: {avg_score:.2f} / 11")
        print(f"  Max score: {max(results['scores'])}")
        print(f"  Min score: {min(results['scores'])}")

        # 점수 분포
        score_dist = {}
        for s in results['scores']:
            score_dist[s] = score_dist.get(s, 0) + 1

        print(f"\n[Score Distribution]")
        for score in sorted(score_dist.keys(), reverse=True):
            count = score_dist[score]
            print(f"  {score:2d}점: {count:3d}개 ({count/len(results['scores'])*100:5.1f}%)")

    # 실패한 기사 ID
    if results['failed_ids']:
        print(f"\n[Failed Article IDs (first 10)]")
        for fail_id in results['failed_ids'][:10]:
            print(f"  {fail_id}")

    # 비용 추정
    total_tokens = results['success'] * 600  # 평균 600 토큰
    cost = total_tokens / 1_000_000 * 0.075
    print(f"\n[Cost Estimate]")
    print(f"  Total tokens: ~{total_tokens:,}")
    print(f"  Estimated cost: ${cost:.4f} (약 {cost * 1350:.0f}원)")


if __name__ == '__main__':
    process_all_google_news_parallel()
