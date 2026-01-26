#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News 715개 전체 처리 (Gemini 2.5 Flash + Rate Limiting)
"""

import os
import time
import json
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Gemini 2.5 Flash 사용
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

def extract_deal_info(title, snippet):
    """
    Gemini로 딜 정보 추출
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

        result = json.loads(result_text)
        return result

    except Exception as e:
        print(f"  [ERROR] {str(e)[:100]}")
        return None


def process_all_google_news():
    """Google News 715개 전체 처리"""

    print("="*60)
    print("Processing All Google News Articles")
    print("="*60)

    # 1. Google News 기사 전체 조회
    articles_result = supabase.table('investment_news_articles').select('id, article_title, content_snippet, site_number').eq('site_number', 100).execute()

    all_articles = articles_result.data
    print(f"\nTotal Google News articles: {len(all_articles)}")
    print(f"Estimated time: {len(all_articles) * 6 / 60:.1f} minutes (6 sec per article)")
    print()

    # 2. 각 기사 처리
    results = {
        'total': len(all_articles),
        'success': 0,
        'failed': 0,
        'has_company_name': 0,
        'scores': []
    }

    start_time = time.time()

    for idx, article in enumerate(all_articles, 1):
        article_id = article['id']
        title = article['article_title']
        snippet = article.get('content_snippet')

        print(f"[{idx}/{len(all_articles)}] {title[:50]}...")

        # Gemini 정보 추출
        extracted = extract_deal_info(title, snippet)

        if extracted:
            results['success'] += 1

            # 기업명 체크
            if extracted.get('company_name'):
                results['has_company_name'] += 1

            # 점수 저장
            score = extracted.get('score', 0)
            results['scores'].append(score)

            # 데이터베이스 업데이트 (11점 점수 필드)
            update_data = {
                'score': score,
                'has_amount': bool(extracted.get('amount')),
                'has_investors': bool(extracted.get('investors')),
                'has_stage': bool(extracted.get('stage')),
                'has_industry': bool(extracted.get('industry')),
                'has_location': bool(extracted.get('location'))
            }

            try:
                supabase.table('investment_news_articles').update(update_data).eq('id', article_id).execute()
                print(f"  [OK] Score: {score}, Company: {extracted.get('company_name', 'N/A')}")
            except Exception as e:
                print(f"  [ERROR] DB update failed: {str(e)[:50]}")
        else:
            results['failed'] += 1
            print(f"  [FAIL] Extraction failed")

        # Rate limiting: 6초마다 1개 (분당 10개 제한)
        time.sleep(6)

        # 진행 상황 출력 (50개마다)
        if idx % 50 == 0:
            elapsed = time.time() - start_time
            remaining = (len(all_articles) - idx) * 6
            print(f"\n  Progress: {idx}/{len(all_articles)} ({idx/len(all_articles)*100:.1f}%)")
            print(f"  Elapsed: {elapsed/60:.1f} min, Remaining: {remaining/60:.1f} min")
            print(f"  Success: {results['success']}, Failed: {results['failed']}\n")

    # 3. 최종 결과
    elapsed_time = time.time() - start_time

    print("\n" + "="*60)
    print("Processing Results")
    print("="*60)

    print(f"\n[Overall]")
    print(f"  Total processed: {results['total']}")
    print(f"  Success: {results['success']} ({results['success']/results['total']*100:.1f}%)")
    print(f"  Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print(f"  Has company name: {results['has_company_name']} ({results['has_company_name']/results['success']*100:.1f}%)")
    print(f"  Processing time: {elapsed_time/60:.1f} minutes")

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


if __name__ == '__main__':
    process_all_google_news()
