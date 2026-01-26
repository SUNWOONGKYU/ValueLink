#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
벤처스퀘어 단독 테스트
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

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

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
                    base = url.split('/category')[0] if '/category' in url else url
                    if link_url.startswith('/'):
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
            'div.article-body',
            'div#article-view',
            'div.entry-content',
            'article',
            'div.article-content',
            'div.content',
            'div.post-content'
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


url = 'https://www.venturesquare.net/category/news/'

print("="*60)
print("Testing Venturesquare ONLY")
print("="*60)
safe_print(f"URL: {url}\n")

# 1. 링크 수집
print("  [1/3] Collecting links...", end=" ")
candidates = collect_links(url)
print(f"[OK] {len(candidates)} candidates")

if not candidates:
    print("  [RESULT] No candidates found")
else:
    # 2. 본문 크롤링 + 추출
    print(f"\n  [2/3] Processing articles...\n")

    valid_articles = []

    for idx, candidate in enumerate(candidates[:10], 1):
        title = candidate['title']
        article_url = candidate['url']

        safe_print(f"    [{idx}/{min(len(candidates), 10)}] {title[:40]}...")

        # 본문
        content = crawl_content(article_url)
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

        safe_print(f"        Company: {company if has_company else '[MISSING]'}")
        safe_print(f"        Investor: {investor if has_investor else '[MISSING]'}")
        safe_print(f"        Amount: {amount if has_amount else '[NONE]'}")
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

    if valid_articles:
        print(f"\n{'='*60}")
        print(f"Valid Articles ({len(valid_articles)})")
        print(f"{'='*60}")
        for idx, article in enumerate(valid_articles, 1):
            safe_print(f"\n{idx}. {article['title'][:60]}...")
            safe_print(f"   Company: {article['company']}")
            safe_print(f"   Investor: {article['investor']}")
            safe_print(f"   Amount: {article['amount'] if article['amount'] else 'N/A'}")
