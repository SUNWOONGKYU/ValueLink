#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10개 소스 하나씩 순차 테스트
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

# 11개 소스 전체
ALL_SOURCES = [
    {
        'source_number': 9,
        'source_name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net/category/news/'
    },
    {
        'source_number': 10,
        'source_name': '플래텀',
        'url': 'https://platum.kr'
    },
    {
        'source_number': 11,
        'source_name': '스타트업투데이',
        'url': 'https://startuptoday.kr/news/articleList.html'
    },
    {
        'source_number': 12,
        'source_name': '스타트업엔',
        'url': 'https://startupn.kr/news/articleList.html'
    },
    {
        'source_number': 13,
        'source_name': '아웃스탠딩',
        'url': 'https://outstanding.kr/category/news/'
    },
    {
        'source_number': 14,
        'source_name': '비석세스',
        'url': 'https://besuccess.com/category/news/'
    },
    {
        'source_number': 19,
        'source_name': 'AI타임스',
        'url': 'https://www.aitimes.com/news/articleList.html'
    },
    {
        'source_number': 21,
        'source_name': '넥스트유니콘',
        'url': 'https://www.nextunicorn.kr/news/articleList.html'
    },
    {
        'source_number': 22,
        'source_name': '블로터',
        'url': 'https://www.bloter.net/news/articleList.html'
    },
    {
        'source_number': 23,
        'source_name': '이코노미스트',
        'url': 'https://www.economist.co.kr/news/articleList.html'
    },
    {
        'source_number': 24,
        'source_name': '와우테일',
        'url': 'https://www.wowtale.net/'
    }
]


def check_title(title):
    """제목 필터링: "투자" OR "유치" 필수"""

    if not any(kw in title for kw in ['투자', '유치']):
        return False

    excluded = ['IR', 'M&A', '인수', '합병', '상장', 'IPO',
                '행사', '세미나', '채용', '인사', 'MOU', '협약']
    if any(kw in title for kw in excluded):
        return False

    return True


def collect_links(url):
    """링크 수집"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        all_links = soup.find_all('a', href=True)

        candidates = []
        for link in all_links:
            title = link.get_text().strip()
            if len(title) < 10:
                continue

            if check_title(title):
                link_url = link['href']

                if not link_url.startswith('http'):
                    base = url.split('/category')[0] if '/category' in url else url.split('/news')[0] if '/news' in url else url.split('/archives')[0] if '/archives' in url else url
                    if link_url.startswith('/'):
                        link_url = base + link_url
                    elif link_url.startswith('?'):
                        link_url = base + link_url
                    else:
                        link_url = base + '/' + link_url

                candidates.append({
                    'title': title,
                    'url': link_url
                })

        # 중복 제거
        seen = set()
        unique = []
        for c in candidates:
            if c['url'] not in seen:
                seen.add(c['url'])
                unique.append(c)

        return unique

    except Exception as e:
        print(f"    [ERROR] {str(e)[:50]}")
        return []


def crawl_content(url):
    """본문 크롤링"""

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        selectors = [
            'div.article-body',           # 스타트업투데이, 스타트업엔, 넥스트유니콘, 블로터, 이코노미스트
            'div#article-view',           # 스타트업투데이 전체
            'div.entry-content',
            'article',
            'div.article-content',
            'div.content',
            'div.post-content',
            'div#article-view-content-div'
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                content = elem.get_text(separator='\n', strip=True)
                if len(content) > 200:
                    return content

        return None

    except Exception as e:
        return None


def extract_info(title, content):
    """회사 + 투자자 추출"""

    if not content:
        return None

    content_truncated = content[:3000]

    prompt = f"""
다음 투자 뉴스에서 정보를 추출하세요.

제목: {title}

본문:
{content_truncated}

JSON:
{{
    "company": "투자 받은 회사",
    "investor": "투자자",
    "amount": "투자 금액"
}}

company와 investor는 반드시 찾아야 합니다.
없으면 null.
JSON만 응답.
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


def safe_print(text):
    """인코딩 에러 방지를 위한 안전한 출력"""
    try:
        print(text)
    except UnicodeEncodeError:
        # cp949로 인코딩할 수 없는 문자를 ?로 대체
        print(text.encode('cp949', errors='replace').decode('cp949'))


def test_one_source(source, source_num, total_sources):
    """1개 소스 테스트"""

    print(f"\n{'='*60}")
    print(f"[{source_num}/{total_sources}] {source['source_name']}")
    print(f"{'='*60}")
    print(f"URL: {source['url']}")

    # 1. 링크 수집
    print(f"\n  [1/3] Collecting links...", end=" ")
    candidates = collect_links(source['url'])
    print(f"[OK] {len(candidates)} candidates")

    if not candidates:
        print(f"  [RESULT] No candidates found")
        return {
            'source_name': source['source_name'],
            'candidates': 0,
            'valid': 0,
            'articles': []
        }

    # 2. 본문 크롤링 + 추출
    print(f"\n  [2/3] Processing articles...")

    valid_articles = []

    for idx, candidate in enumerate(candidates[:10], 1):  # 최대 10개만
        title = candidate['title']
        url = candidate['url']

        safe_print(f"\n    [{idx}/{min(len(candidates), 10)}] {title[:40]}...")

        # 본문
        content = crawl_content(url)
        if not content:
            print(f"        [FAIL] Content")
            continue

        print(f"        [OK] Content ({len(content)} chars)")

        # 추출
        extracted = extract_info(title, content)
        if not extracted:
            print(f"        [FAIL] Extraction")
            continue

        company = extracted.get('company')
        investor = extracted.get('investor')
        amount = extracted.get('amount')

        # 리스트 → 문자열
        if isinstance(investor, list):
            investor = ', '.join(investor) if investor else None
        if isinstance(company, list):
            company = ', '.join(company) if company else None
        if isinstance(amount, list):
            amount = ', '.join(amount) if amount else None

        # 필수 체크
        has_company = company and str(company).lower() not in ['null', 'n/a', 'none', '']
        has_investor = investor and str(investor).lower() not in ['null', 'n/a', 'none', '']
        has_amount = amount and str(amount).lower() not in ['null', 'n/a', 'none', '']

        is_valid = has_company and has_investor

        print(f"        Company: {company if has_company else '[MISSING]'}")
        print(f"        Investor: {investor if has_investor else '[MISSING]'}")
        print(f"        Amount: {amount if has_amount else '[NONE]'}")
        print(f"        => {'[VALID]' if is_valid else '[INVALID]'}")

        if is_valid:
            valid_articles.append({
                'title': title,
                'company': company,
                'investor': investor,
                'amount': amount if has_amount else None
            })

        time.sleep(2)

    # 3. 결과
    print(f"\n  [3/3] Results")
    print(f"    Candidates: {len(candidates)}")
    print(f"    Processed: {min(len(candidates), 10)}")
    print(f"    Valid: {len(valid_articles)}")

    return {
        'source_name': source['source_name'],
        'candidates': len(candidates),
        'valid': len(valid_articles),
        'articles': valid_articles
    }


def main():
    """11개 소스 순차 테스트"""

    total_sources = len(ALL_SOURCES)

    print("="*60)
    print(f"Testing {total_sources} Sources Sequentially")
    print("="*60)
    print("Criteria:")
    print("  1. Title: '투자' OR '유치'")
    print("  2. Body: Company + Investor (both required)")
    print("="*60)

    all_results = []

    for idx, source in enumerate(ALL_SOURCES, 1):
        result = test_one_source(source, idx, total_sources)
        all_results.append(result)

        # 중간 요약
        print(f"\n>>> {source['source_name']}: {result['valid']}개 유효")

        time.sleep(3)  # 소스 간 대기

    # 전체 요약
    print(f"\n\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")

    total_valid = sum(r['valid'] for r in all_results)

    print(f"\n[Overall]")
    print(f"  Total valid: {total_valid}")

    print(f"\n[By Source]")
    for r in all_results:
        print(f"  {r['source_name']:20s}: {r['valid']:2d} valid")

    # 상위 5개 기사
    print(f"\n[Top Articles (first 5)]")
    count = 0
    for r in all_results:
        for article in r['articles']:
            count += 1
            print(f"\n{count}. [{r['source_name']}]")
            print(f"   {article['title'][:60]}...")
            print(f"   Company: {article['company']}")
            print(f"   Investor: {article['investor']}")

            if count >= 5:
                break
        if count >= 5:
            break


if __name__ == '__main__':
    main()
