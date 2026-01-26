#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2가지 필수 조건 수집
- 투자받은 회사 (필수)
- 투자자 (필수)
- 제목 사전 필터링 → 본문 확인 → 2가지 있는 것만 저장
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

# 테스트 소스
TEST_SOURCES = [
    {
        'source_name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net/category/news/',
        'max_pages': 3
    },
    {
        'source_name': '비석세스',
        'url': 'https://besuccess.com/category/news/',
        'max_pages': 3
    }
]


def check_title_pattern(title):
    """
    제목 필터링 (1단계)

    필수: "투자" OR "유치" 포함

    Returns:
        bool: 제목에 "투자" 또는 "유치"가 있는가?
    """

    # 필수: "투자" 또는 "유치" 포함
    if not any(kw in title for kw in ['투자', '유치']):
        return False

    # 제외 키워드
    excluded = ['IR', 'M&A', '인수', '합병', '상장', 'IPO',
                '행사', '세미나', '채용', '인사', 'MOU', '협약']
    if any(kw in title for kw in excluded):
        return False

    return True


def collect_candidate_links(source_url):
    """투자 기사 후보 링크 수집"""

    print(f"  Collecting links from {source_url}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(source_url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"    [FAIL] HTTP {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        # 모든 링크 수집
        all_links = soup.find_all('a', href=True)

        candidates = []

        for link in all_links:
            title = link.get_text().strip()
            url = link['href']

            if not title or len(title) < 10:
                continue

            # 제목 패턴 체크
            if check_title_pattern(title):
                # 절대 URL 변환
                if not url.startswith('http'):
                    base_url = source_url.split('/category')[0]
                    if url.startswith('/'):
                        url = base_url + url
                    else:
                        url = base_url + '/' + url

                candidates.append({
                    'title': title,
                    'url': url
                })

        # 중복 제거
        seen_urls = set()
        unique_candidates = []
        for c in candidates:
            if c['url'] not in seen_urls:
                seen_urls.add(c['url'])
                unique_candidates.append(c)

        print(f"    [OK] Found {len(unique_candidates)} candidate articles")
        return unique_candidates

    except Exception as e:
        print(f"    [ERROR] {str(e)[:100]}")
        return []


def crawl_article_content(url):
    """기사 본문 크롤링"""

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 본문 선택자들 (여러 패턴 시도)
        content_selectors = [
            'div.entry-content',
            'article',
            'div.article-content',
            'div.content',
            'div.post-content'
        ]

        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text(separator='\n', strip=True)
                if len(content) > 200:  # 충분한 길이
                    return content

        return None

    except Exception as e:
        return None


def extract_company_and_investor(title, content):
    """
    Gemini로 회사+투자자 추출 (2가지 필수)

    Returns:
        dict or None
    """

    if not content:
        return None

    content_truncated = content[:3000]

    prompt = f"""
다음 투자 뉴스에서 정보를 추출하세요.

제목: {title}

본문:
{content_truncated}

추출 (JSON):
{{
    "company": "투자 받은 회사 이름",
    "investor": "투자자 이름",
    "amount": "투자 금액"
}}

CRITICAL:
- company와 investor는 반드시 모두 있어야 합니다
- 둘 중 하나라도 없으면 null로 표시하지 말고, 기사를 다시 읽어서 찾으세요
- 정말로 없으면 그때만 null

JSON만 응답하세요.
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
        return None


def test_collection():
    """2가지 필수 조건으로 수집 테스트"""

    print("="*60)
    print("Collection with 2 Requirements")
    print("="*60)
    print("Requirements:")
    print("  1. Company (투자받은 회사) - REQUIRED")
    print("  2. Investor (투자자) - REQUIRED")
    print("  3. Amount (투자금액) - OPTIONAL")
    print("="*60)

    all_results = []

    for source in TEST_SOURCES:
        print(f"\n{'='*60}")
        print(f"Source: {source['source_name']}")
        print(f"{'='*60}")

        # 1단계: 후보 링크 수집
        candidates = collect_candidate_links(source['url'])

        if not candidates:
            print(f"  [SKIP] No candidates")
            continue

        print(f"\n  Processing {len(candidates)} candidates...")

        # 2단계: 본문 크롤링 + 2가지 확인
        for idx, candidate in enumerate(candidates, 1):
            title = candidate['title']
            url = candidate['url']

            print(f"\n  [{idx}/{len(candidates)}] {title[:50]}...")

            # 본문 크롤링
            content = crawl_article_content(url)

            if not content:
                print(f"    [FAIL] Content crawling failed")
                continue

            print(f"    [OK] Content ({len(content)} chars)")

            # 회사+투자자 추출
            extracted = extract_company_and_investor(title, content)

            if not extracted:
                print(f"    [FAIL] Extraction failed")
                continue

            company = extracted.get('company')
            investor = extracted.get('investor')
            amount = extracted.get('amount')

            # 타입 변환 (list → string)
            if isinstance(investor, list):
                investor = ', '.join(investor) if investor else None
            if isinstance(company, list):
                company = ', '.join(company) if company else None
            if isinstance(amount, list):
                amount = ', '.join(amount) if amount else None

            # 2가지 필수 체크
            has_company = company and str(company).lower() not in ['null', 'n/a', 'none', '']
            has_investor = investor and str(investor).lower() not in ['null', 'n/a', 'none', '']
            has_amount = amount and str(amount).lower() not in ['null', 'n/a', 'none', '']

            # 필수 2가지
            has_required = has_company and has_investor

            print(f"    Company: {company if has_company else '[MISSING!]'}")
            print(f"    Investor: {investor if has_investor else '[MISSING!]'}")
            print(f"    Amount: {amount if has_amount else '[NONE]'}")
            print(f"    Result: {'[VALID!]' if has_required else '[INVALID - 2가지 필수 미충족]'}")

            # 2가지가 있는 것만 저장
            if has_required:
                all_results.append({
                    'source_name': source['source_name'],
                    'title': title,
                    'url': url,
                    'company': company,
                    'investor': investor,
                    'amount': amount if has_amount else None,
                    'has_amount': has_amount
                })

            time.sleep(2)

    # 최종 결과
    print(f"\n{'='*60}")
    print("Test Results")
    print(f"{'='*60}")

    total = len(all_results)
    with_amount = sum(1 for r in all_results if r['has_amount'])

    print(f"\n[Valid Articles (회사+투자자)]")
    print(f"  Total: {total}")
    print(f"  With amount: {with_amount} ({with_amount/total*100:.1f}%)")
    print(f"  Without amount: {total - with_amount}")

    # 결과 출력
    if all_results:
        print(f"\n{'='*60}")
        print(f"Valid Articles ({total})")
        print(f"{'='*60}")

        for idx, article in enumerate(all_results, 1):
            print(f"\n{idx}. [{article['source_name']}]")
            print(f"   {article['title'][:60]}...")
            print(f"   Company: {article['company']}")
            print(f"   Investor: {article['investor']}")
            print(f"   Amount: {article['amount'] if article['amount'] else 'N/A'}")
    else:
        print(f"\n[WARNING] No valid articles found!")

    # 추정
    if total > 0:
        print(f"\n{'='*60}")
        print("Estimation for Full Run")
        print(f"{'='*60}")

        print(f"\n현재 테스트 (2개 소스 × 3페이지):")
        print(f"  Valid: {total}개")

        print(f"\n전체 실행 시 (10개 소스 × 10페이지):")
        estimated = total * 16  # 5배 소스 × 3배 페이지 이상
        print(f"  예상: ~{estimated}개")

        if estimated >= 100:
            print(f"\n✅ 결론: 전체 실행 권장! 약 {estimated}개 예상")
        elif estimated >= 50:
            print(f"\n⚠️ 결론: 괜찮음. {estimated}개 예상")
        else:
            print(f"\n❌ 결론: 적음. {estimated}개만 예상")


if __name__ == '__main__':
    test_collection()
