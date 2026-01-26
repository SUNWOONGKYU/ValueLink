#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 수집 + 보강 스크립트
1. RSS + 웹 스크래핑 수집
2. Gemini로 점수 계산 및 Deal 정보 추출
3. TheVC로 보강
4. Naver API로 보강
5. deals 테이블 저장
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import re
from collections import defaultdict

# 다른 스크립트 import
from collect_rss import main as collect_rss_main
from collect_web import main as collect_web_main
from search_thevc import enrich_deal_with_thevc
from search_company_info import search_company_info_naver

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Gemini API 설정
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')


def calculate_article_score_with_gemini(article):
    """
    Gemini로 기사 점수 계산 (11점 만점)

    Args:
        article: 기사 정보

    Returns:
        점수 정보 딕셔너리
    """
    print(f"\n[SCORE] Calculating for: {article['article_title'][:50]}...")

    prompt = f"""
다음 투자 뉴스 기사를 분석하고 점수를 계산하세요.

기사 제목: {article['article_title']}
기사 요약: {article.get('content_snippet', 'N/A')}

점수 기준 (11점 만점):
1. 투자금액 명시 (3점): "100억원", "$10M" 등
2. 투자자 명시 (3점): "알토스벤처스", "삼성벤처" 등
3. 투자단계 명시 (2점): "시리즈A", "프리A", "시드" 등
4. 업종 명시 (1점): "AI", "헬스케어", "핀테크" 등
5. 지역 명시 (1점): "서울", "판교", "강남" 등
6. 직원수 명시 (1점): "직원 50명", "팀원 20명" 등

JSON 형식으로 답변:
{{
    "has_amount": true/false,
    "has_investors": true/false,
    "has_stage": true/false,
    "has_industry": true/false,
    "has_location": true/false,
    "has_employees": true/false,
    "total_score": 0-11
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # JSON 추출
        import json
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            score_data = json.loads(json_match.group())
            print(f"  [SUCCESS] Score: {score_data['total_score']}/11")
            return score_data
        else:
            print(f"  [WARN] No JSON found in response")
            return None

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return None


def extract_deal_info_with_gemini(article):
    """
    Gemini로 Deal 정보 추출

    Args:
        article: 기사 정보

    Returns:
        Deal 정보 딕셔너리
    """
    print(f"\n[EXTRACT] Deal info from: {article['article_title'][:50]}...")

    prompt = f"""
다음 투자 뉴스 기사에서 투자 정보를 추출하세요.

기사 제목: {article['article_title']}
기사 요약: {article.get('content_snippet', 'N/A')}

추출할 정보:
1. company_name (필수): 투자받은 기업명
2. ceo: 대표자명
3. founded: 설립일 (YYYY-MM-DD 형식)
4. industry: 업종 (예: AI, 헬스케어)
5. location: 위치 (예: 서울, 판교)
6. employees: 직원수 (숫자만)
7. investors: 투자자 (여러 명이면 콤마로 구분)
8. amount: 투자금액 (원문 그대로)
9. stage: 투자단계 (예: 시리즈A, 프리A, 시드)

JSON 형식으로 답변 (값이 없으면 null):
{{
    "company_name": "기업명",
    "ceo": "대표자명",
    "founded": "YYYY-MM-DD",
    "industry": "업종",
    "location": "위치",
    "employees": 50,
    "investors": "투자자1, 투자자2",
    "amount": "투자금액",
    "stage": "투자단계"
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # JSON 추출
        import json
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            deal_data = json.loads(json_match.group())
            print(f"  [SUCCESS] Company: {deal_data.get('company_name')}")
            return deal_data
        else:
            print(f"  [WARN] No JSON found in response")
            return None

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return None


def select_best_articles():
    """
    기업별 최고 점수 기사 선정

    Returns:
        선정된 기사 ID 리스트
    """
    print("\n" + "="*60)
    print("Selecting best articles per company...")
    print("="*60)

    # 어제 수집된 기사만 대상
    yesterday = (datetime.now() - timedelta(days=1)).date()

    # 아직 선정되지 않은 한국 기업 기사
    result = supabase.table('investment_news_articles').select('*').eq('is_selected', False).eq('is_korean_company', True).gte('created_at', yesterday.isoformat()).execute()

    articles = result.data

    if not articles:
        print("No articles to process")
        return []

    print(f"Found {len(articles)} articles to process")

    # Gemini로 점수 계산
    for article in articles:
        score_data = calculate_article_score_with_gemini(article)

        if score_data:
            # 점수 업데이트
            supabase.table('investment_news_articles').update({
                'score': score_data['total_score'],
                'has_amount': score_data['has_amount'],
                'has_investors': score_data['has_investors'],
                'has_stage': score_data['has_stage'],
                'has_industry': score_data['has_industry'],
                'has_location': score_data['has_location'],
                'has_employees': score_data['has_employees']
            }).eq('id', article['id']).execute()

            article['score'] = score_data['total_score']

        # Rate limiting
        time.sleep(0.6)

    # 기업별 그룹화
    companies = defaultdict(list)

    for article in articles:
        # Gemini로 기업명 추출 (간단한 프롬프트)
        deal_data = extract_deal_info_with_gemini(article)

        if deal_data and deal_data.get('company_name'):
            company_name = deal_data['company_name']
            article['company_name'] = company_name
            companies[company_name].append(article)

        time.sleep(0.6)

    # 기업별 최고 점수 선정
    selected_ids = []

    for company_name, company_articles in companies.items():
        # 점수순 정렬 (동점 시: 글자수 → 날짜)
        sorted_articles = sorted(
            company_articles,
            key=lambda x: (
                x.get('score', 0),
                len(x.get('article_title', '')),
                x.get('published_date', '')
            ),
            reverse=True
        )

        best_article = sorted_articles[0]
        selected_ids.append(best_article['id'])

        # is_selected 업데이트
        supabase.table('investment_news_articles').update({
            'is_selected': True,
            'selected_at': datetime.now().isoformat()
        }).eq('id', best_article['id']).execute()

        print(f"  [SELECTED] {company_name}: Score {best_article.get('score', 0)}/11")

    print(f"\n[RESULT] Selected {len(selected_ids)} articles")
    return selected_ids


def process_selected_articles(article_ids):
    """
    선정된 기사를 처리하여 deals 테이블에 저장

    Args:
        article_ids: 선정된 기사 ID 리스트
    """
    print("\n" + "="*60)
    print("Processing selected articles...")
    print("="*60)

    for article_id in article_ids:
        # 기사 조회
        result = supabase.table('investment_news_articles').select('*').eq('id', article_id).execute()

        if not result.data:
            continue

        article = result.data[0]

        print(f"\n[PROCESS] Article ID {article_id}: {article['article_title'][:50]}...")

        # Step 1: Gemini로 Deal 정보 추출
        deal_data = extract_deal_info_with_gemini(article)

        if not deal_data or not deal_data.get('company_name'):
            print(f"  [SKIP] No company name found")
            continue

        # Step 2: TheVC로 보강
        enriched_deal = enrich_deal_with_thevc(deal_data)

        # Step 3: Naver API로 부족한 정보 보강 (선택적)
        if not enriched_deal.get('ceo') or not enriched_deal.get('founded'):
            print(f"  [NAVER] Searching for missing info...")
            naver_info = search_company_info_naver(enriched_deal['company_name'])

            if naver_info:
                if not enriched_deal.get('ceo'):
                    enriched_deal['ceo'] = naver_info.get('ceo')
                if not enriched_deal.get('founded'):
                    enriched_deal['founded'] = naver_info.get('founded')
                if not enriched_deal.get('location'):
                    enriched_deal['location'] = naver_info.get('location')

        # Step 4: deals 테이블에 저장
        deal_record = {
            'article_id': article_id,
            'news_title': article['article_title'],
            'news_url': article['article_url'],
            'news_date': article['published_date'],
            'site_name': article['source_name'],
            'article_score': article.get('score', 0),

            'company_name': enriched_deal['company_name'],
            'ceo': enriched_deal.get('ceo'),
            'founded': enriched_deal.get('founded'),
            'industry': enriched_deal.get('industry'),
            'location': enriched_deal.get('location'),
            'employees': enriched_deal.get('employees'),
            'description': enriched_deal.get('description'),

            'investors': enriched_deal.get('investors'),
            'amount': enriched_deal.get('amount'),
            'stage': enriched_deal.get('stage'),

            'gemini_extracted': True,
            'thevc_enriched': bool(enriched_deal.get('source') == 'thevc.kr'),
            'naver_enriched': bool(naver_info) if not enriched_deal.get('ceo') else False
        }

        try:
            supabase.table('deals').insert(deal_record).execute()
            print(f"  [SAVED] Deal for {enriched_deal['company_name']}")
        except Exception as e:
            print(f"  [ERROR] Failed to save deal: {str(e)[:100]}")

        # Rate limiting
        time.sleep(1)


def main():
    """메인 실행"""
    print("="*60)
    print("Investment News Collection & Enrichment")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: RSS 수집
    print("\n[STEP 1/5] Collecting RSS feeds...")
    rss_collected, rss_saved, _, _ = collect_rss_main()

    # Step 2: 웹 스크래핑
    print("\n[STEP 2/5] Web scraping...")
    web_collected, web_saved, _, _ = collect_web_main()

    total_collected = rss_collected + web_collected
    total_saved = rss_saved + web_saved

    print(f"\n[COLLECTION] Total: {total_collected}, Saved: {total_saved}")

    if total_saved == 0:
        print("\n[DONE] No new articles to process")
        return

    # Step 3: 기업별 최고 점수 선정
    print("\n[STEP 3/5] Selecting best articles...")
    selected_ids = select_best_articles()

    if not selected_ids:
        print("\n[DONE] No articles selected")
        return

    # Step 4: Deal 정보 추출 및 보강
    print("\n[STEP 4/5] Extracting and enriching deal info...")
    process_selected_articles(selected_ids)

    # Step 5: 결과 요약
    print("\n" + "="*60)
    print("Final Summary")
    print("="*60)
    print(f"Total collected: {total_collected}")
    print(f"New articles saved: {total_saved}")
    print(f"Deals created: {len(selected_ids)}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
