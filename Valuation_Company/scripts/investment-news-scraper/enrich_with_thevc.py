#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TheVC로 239개 기사 추가 정보 보강
- 투자금액 포함 기사만 대상
- CEO, 설립일, 정식 명칭 추가
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai
import json

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')


def extract_company_name_from_title(title, snippet):
    """
    Gemini로 기사 제목/요약에서 기업명 추출
    """
    prompt = f"""
다음 투자 뉴스에서 투자를 받은 기업명만 추출하세요.

제목: {title}
요약: {snippet if snippet else 'N/A'}

기업명만 반환하세요 (JSON 형식):
{{"company_name": "기업명"}}

투자자명이 아닌 투자 받은 기업명입니다.
예: "알토스벤처스가 테크노바에 투자" → {{"company_name": "테크노바"}}
"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]

        result = json.loads(result_text)
        return result.get('company_name')
    except:
        return None


def search_company_on_thevc(company_name):
    """
    TheVC.kr에서 기업 정보 검색

    Returns:
        dict: {ceo, founded, official_name, url}
    """

    if not company_name:
        return None

    try:
        # TheVC 검색
        search_url = f"https://thevc.kr/s/{company_name}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 첫 번째 검색 결과 (회사) 클릭
        company_link = soup.select_one('a[href^="/company/"]')

        if not company_link:
            return None

        company_url = 'https://thevc.kr' + company_link['href']

        # 회사 상세 페이지 접근
        detail_response = requests.get(company_url, headers=headers, timeout=10)
        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

        # 정보 추출
        result = {
            'official_name': None,
            'ceo': None,
            'founded': None,
            'url': company_url,
            'source': 'thevc.kr'
        }

        # 회사 정식 명칭
        title_tag = detail_soup.select_one('h1')
        if title_tag:
            result['official_name'] = title_tag.get_text().strip()

        # CEO (대표)
        info_items = detail_soup.select('.info-item')
        for item in info_items:
            label = item.select_one('.label')
            value = item.select_one('.value')

            if label and value:
                label_text = label.get_text().strip()
                value_text = value.get_text().strip()

                if '대표' in label_text or 'CEO' in label_text:
                    result['ceo'] = value_text
                elif '설립' in label_text or 'Founded' in label_text:
                    result['founded'] = value_text

        return result

    except Exception as e:
        print(f"  [ERROR] TheVC search failed: {str(e)[:50]}")
        return None


def enrich_with_thevc():
    """TheVC로 239개 기사 보강"""

    print("="*60)
    print("Enriching with TheVC")
    print("="*60)

    # 투자금액 포함 기사만 조회 (has_amount = true)
    result = supabase.table('investment_news_articles').select('*').eq('site_number', 100).eq('has_amount', True).execute()

    articles = result.data
    print(f"\nTotal articles with amount: {len(articles)}")
    print(f"Estimated time: {len(articles) * 3 / 60:.1f} minutes (3 sec per article)")
    print()

    # 결과 추적
    results = {
        'total': len(articles),
        'success': 0,
        'failed': 0,
        'found_ceo': 0,
        'found_founded': 0,
        'found_official_name': 0
    }

    start_time = time.time()

    for idx, article in enumerate(articles, 1):
        article_id = article['id']
        title = article['article_title']
        snippet = article.get('content_snippet')

        print(f"[{idx}/{len(articles)}] {title[:50]}...")

        # 1. Gemini로 기업명 추출 (정확도 높이기)
        company_name = extract_company_name_from_title(title, snippet)

        if not company_name:
            results['failed'] += 1
            print(f"  [SKIP] No company name extracted")
            continue

        print(f"  Company: {company_name}")

        # 2. TheVC 검색
        thevc_info = search_company_on_thevc(company_name)

        if thevc_info:
            results['success'] += 1

            # 추출된 정보 카운트
            if thevc_info.get('ceo'):
                results['found_ceo'] += 1
            if thevc_info.get('founded'):
                results['found_founded'] += 1
            if thevc_info.get('official_name'):
                results['found_official_name'] += 1

            print(f"  [OK] CEO: {thevc_info.get('ceo', 'N/A')}, Founded: {thevc_info.get('founded', 'N/A')}")

            # 데이터베이스 업데이트 (임시로 content_snippet에 JSON 저장)
            # 나중에 별도 테이블로 분리 가능
            try:
                update_data = {
                    'content_snippet': json.dumps({
                        'original': snippet,
                        'thevc': thevc_info
                    }, ensure_ascii=False)
                }
                supabase.table('investment_news_articles').update(update_data).eq('id', article_id).execute()
            except Exception as e:
                print(f"  [ERROR] DB update failed: {str(e)[:50]}")
        else:
            results['failed'] += 1
            print(f"  [FAIL] Not found on TheVC")

        # Rate limiting
        time.sleep(3)

        # 진행 상황 (50개마다)
        if idx % 50 == 0:
            elapsed = time.time() - start_time
            remaining = (len(articles) - idx) * 3
            print(f"\n  Progress: {idx}/{len(articles)} ({idx/len(articles)*100:.1f}%)")
            print(f"  Elapsed: {elapsed/60:.1f} min, Remaining: {remaining/60:.1f} min")
            print(f"  Success: {results['success']}, Failed: {results['failed']}\n")

    # 최종 결과
    elapsed_time = time.time() - start_time

    print("\n" + "="*60)
    print("Enrichment Results")
    print("="*60)

    print(f"\n[Overall]")
    print(f"  Total processed: {results['total']}")
    print(f"  Success: {results['success']} ({results['success']/results['total']*100:.1f}%)")
    print(f"  Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print(f"  Processing time: {elapsed_time/60:.1f} minutes")

    print(f"\n[TheVC Data Found]")
    print(f"  Official name: {results['found_official_name']} ({results['found_official_name']/results['success']*100:.1f}% of success)")
    print(f"  CEO: {results['found_ceo']} ({results['found_ceo']/results['success']*100:.1f}% of success)")
    print(f"  Founded: {results['found_founded']} ({results['found_founded']/results['success']*100:.1f}% of success)")

    print(f"\n{'='*60}")
    print("Next Steps")
    print(f"{'='*60}")
    print(f"1. Naver API로 {results['success']}개 기사 추가 보강")
    print(f"2. 최종 Deal 테이블 생성")
    print(f"3. 점수 기반 중복 제거")


if __name__ == '__main__':
    enrich_with_thevc()
