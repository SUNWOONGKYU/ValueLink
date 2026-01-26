#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2개 소스 테스트
- 벤처스퀘어, 비석세스
- 페이지네이션 5페이지만
- 본문 크롤링 + 3가지 정보 확인
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

# 테스트 소스 2개
TEST_SOURCES = [
    {
        'source_number': 9,
        'source_name': '벤처스퀘어',
        'base_url': 'https://www.venturesquare.net',
        'list_url_template': 'https://www.venturesquare.net/category/news/page/{page}/',
        'max_pages': 5,  # 테스트용 5페이지만
        'article_selector': 'article.post',
        'title_selector': 'h2.entry-title a',
        'link_selector': 'h2.entry-title a',
        'content_selector': 'div.entry-content'
    },
    {
        'source_number': 14,
        'source_name': '비석세스',
        'base_url': 'https://besuccess.com',
        'list_url_template': 'https://besuccess.com/category/news/page/{page}/',
        'max_pages': 5,
        'article_selector': 'article',
        'title_selector': 'h2 a',
        'link_selector': 'h2 a',
        'content_selector': 'div.entry-content'
    }
]

INVESTMENT_KEYWORDS = [
    '투자', '유치', '시리즈', '펀딩', 'funding', 'investment',
    'Series A', 'Series B', 'Series C', 'Pre-A', '시드', 'Seed',
    '억원', '조달', 'raised', 'rounds'
]

EXCLUDED_KEYWORDS = [
    'IR', 'M&A', '인수', '합병', '상장', 'IPO', '행사', '세미나',
    '채용', '인사', '임원', '대표이사', 'MOU', '협약'
]


def collect_article_urls(source):
    """기사 URL 수집"""

    print(f"\n[{source['source_name']}] Collecting article URLs...")

    all_urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for page in range(1, source['max_pages'] + 1):
        print(f"  Page {page}/{source['max_pages']}...", end=" ")

        try:
            list_url = source['list_url_template'].format(page=page)
            response = requests.get(list_url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"[FAIL] HTTP {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.select(source['article_selector'])

            page_urls = 0

            for article in articles:
                title_elem = article.select_one(source['title_selector'])
                if not title_elem:
                    continue

                title = title_elem.get_text().strip()

                # 투자 키워드 필터링
                has_investment = any(kw.lower() in title.lower() for kw in INVESTMENT_KEYWORDS)
                has_excluded = any(kw in title for kw in EXCLUDED_KEYWORDS)

                if not has_investment or has_excluded:
                    continue

                link_elem = article.select_one(source['link_selector'])
                if not link_elem or not link_elem.get('href'):
                    continue

                url = link_elem['href']

                if not url.startswith('http'):
                    if url.startswith('/'):
                        url = source['base_url'] + url
                    else:
                        url = source['base_url'] + '/' + url

                all_urls.append({
                    'title': title,
                    'url': url
                })
                page_urls += 1

            print(f"[OK] {page_urls} investment articles")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] {str(e)[:50]}")
            continue

    print(f"  [TOTAL] {len(all_urls)} URLs")
    return all_urls


def crawl_content(url, content_selector):
    """본문 크롤링"""

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        content_elem = soup.select_one(content_selector)

        if not content_elem:
            return None

        content = content_elem.get_text(separator='\n', strip=True)
        return content

    except Exception as e:
        return None


def extract_info(title, content):
    """Gemini로 3가지 핵심 정보 추출"""

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
    "company": "투자 받은 회사",
    "investor": "투자자",
    "amount": "투자 금액"
}}

정보가 없으면 null.
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


def test_sources():
    """2개 소스 테스트"""

    print("="*60)
    print("Testing 2 Sources")
    print("="*60)
    print("Sources: 벤처스퀘어, 비석세스")
    print("Pages: 5 per source")
    print("Process: URL수집 → 본문크롤링 → 3가지정보추출")
    print("="*60)

    all_results = []

    for source in TEST_SOURCES:
        print(f"\n{'='*60}")
        print(f"Source: {source['source_name']}")
        print(f"{'='*60}")

        # 1단계: URL 수집
        urls = collect_article_urls(source)

        if not urls:
            print(f"  [SKIP] No URLs found")
            continue

        # 2단계: 본문 크롤링 + 정보 추출
        print(f"\n  Processing {len(urls)} articles...")

        for idx, url_data in enumerate(urls, 1):
            title = url_data['title']
            url = url_data['url']

            print(f"\n  [{idx}/{len(urls)}] {title[:50]}...")

            # 본문 크롤링
            content = crawl_content(url, source['content_selector'])

            if not content:
                print(f"    [FAIL] Content crawling failed")
                continue

            print(f"    [OK] Content ({len(content)} chars)")

            # 정보 추출
            extracted = extract_info(title, content)

            if not extracted:
                print(f"    [FAIL] Extraction failed")
                continue

            company = extracted.get('company')
            investor = extracted.get('investor')
            amount = extracted.get('amount')

            # 3가지 체크
            has_company = company and company.lower() not in ['null', 'n/a']
            has_investor = investor and investor.lower() not in ['null', 'n/a']
            has_amount = amount and amount.lower() not in ['null', 'n/a']

            has_all_three = has_company and has_investor and has_amount

            print(f"    Company: {company if has_company else '[NONE]'}")
            print(f"    Investor: {investor if has_investor else '[NONE]'}")
            print(f"    Amount: {amount if has_amount else '[NONE]'}")
            print(f"    Result: {'[PERFECT!]' if has_all_three else '[INCOMPLETE]'}")

            # 결과 저장
            all_results.append({
                'source_name': source['source_name'],
                'title': title,
                'url': url,
                'company': company,
                'investor': investor,
                'amount': amount,
                'has_all_three': has_all_three
            })

            time.sleep(2)  # Rate limiting

    # 최종 결과
    print(f"\n{'='*60}")
    print("Test Results")
    print(f"{'='*60}")

    total = len(all_results)
    perfect = sum(1 for r in all_results if r['has_all_three'])

    print(f"\n[Overall]")
    print(f"  Total processed: {total}")
    print(f"  Perfect (3 items): {perfect} ({perfect/total*100:.1f}%)")

    # 완벽한 기사
    perfect_articles = [r for r in all_results if r['has_all_three']]

    if perfect_articles:
        print(f"\n{'='*60}")
        print(f"Perfect Articles ({len(perfect_articles)})")
        print(f"{'='*60}")

        for idx, article in enumerate(perfect_articles, 1):
            print(f"\n{idx}. [{article['source_name']}]")
            print(f"   {article['title'][:60]}...")
            print(f"   Company: {article['company']}")
            print(f"   Investor: {article['investor']}")
            print(f"   Amount: {article['amount']}")
    else:
        print(f"\n[WARNING] No perfect articles found!")

    # 추정
    print(f"\n{'='*60}")
    print("Estimation for Full Run")
    print(f"{'='*60}")

    if total > 0:
        rate = perfect / total

        print(f"\n현재 테스트 (2개 소스 × 5페이지):")
        print(f"  처리: {total}개")
        print(f"  완벽: {perfect}개 ({rate*100:.1f}%)")

        print(f"\n전체 실행 시 (10개 소스 × 10페이지):")
        estimated_total = total * 10  # 10개 소스 × 2배 페이지
        estimated_perfect = int(estimated_total * rate)
        print(f"  예상 처리: ~{estimated_total}개")
        print(f"  예상 완벽: ~{estimated_perfect}개")

        if estimated_perfect >= 100:
            print(f"\n✅ 결론: 전체 실행 권장! 약 {estimated_perfect}개의 완성도 높은 Deal 예상")
        elif estimated_perfect >= 50:
            print(f"\n⚠️ 결론: 괜찮은 수준. {estimated_perfect}개 예상")
        else:
            print(f"\n❌ 결론: 낮은 수준. {estimated_perfect}개만 예상. 전략 재검토 필요")


if __name__ == '__main__':
    test_sources()
