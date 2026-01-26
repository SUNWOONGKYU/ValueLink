#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 11개 소스 수집
- 페이지네이션 (10-20페이지)
- 본문 크롤링
- Gemini로 본문에서 정보 추출
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
import json
import google.generativeai as genai

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

# 개선된 소스 정보 (10개 - TheVC 제외)
IMPROVED_SOURCES = [
    {
        'source_number': 9,
        'source_name': '벤처스퀘어',
        'base_url': 'https://www.venturesquare.net',
        'list_url_template': 'https://www.venturesquare.net/category/news/page/{page}/',
        'max_pages': 10,
        'article_selector': 'article.post',
        'title_selector': 'h2.entry-title a',
        'link_selector': 'h2.entry-title a',
        'content_selector': 'div.entry-content'
    },
    {
        'source_number': 10,
        'source_name': '플래텀',
        'base_url': 'https://platum.kr',
        'list_url_template': 'https://platum.kr/archives/category/startup/page/{page}',
        'max_pages': 10,
        'article_selector': 'article',
        'title_selector': 'h2.entry-title a',
        'link_selector': 'h2.entry-title a',
        'content_selector': 'div.entry-content'
    },
    {
        'source_number': 11,
        'source_name': '스타트업투데이',
        'base_url': 'https://startuptoday.kr',
        'list_url_template': 'https://startuptoday.kr/news/articleList.html?page={page}',
        'max_pages': 10,
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles a',
        'link_selector': 'h4.titles a',
        'content_selector': 'article'
    },
    {
        'source_number': 12,
        'source_name': '스타트업엔',
        'base_url': 'https://startupn.kr',
        'list_url_template': 'https://startupn.kr/news/articleList.html?page={page}',
        'max_pages': 10,
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles a',
        'link_selector': 'h4.titles a',
        'content_selector': 'article'
    },
    {
        'source_number': 13,
        'source_name': '아웃스탠딩',
        'base_url': 'https://outstanding.kr',
        'list_url_template': 'https://outstanding.kr/category/news/page/{page}/',
        'max_pages': 10,
        'article_selector': 'article',
        'title_selector': 'h2.entry-title a',
        'link_selector': 'h2.entry-title a',
        'content_selector': 'div.entry-content'
    },
    {
        'source_number': 14,
        'source_name': '비석세스',
        'base_url': 'https://besuccess.com',
        'list_url_template': 'https://besuccess.com/category/news/page/{page}/',
        'max_pages': 10,
        'article_selector': 'article',
        'title_selector': 'h2 a',
        'link_selector': 'h2 a',
        'content_selector': 'div.entry-content'
    },
    {
        'source_number': 19,
        'source_name': 'AI타임스',
        'base_url': 'https://www.aitimes.com',
        'list_url_template': 'https://www.aitimes.com/news/articleList.html?page={page}',
        'max_pages': 10,
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles a',
        'link_selector': 'h4.titles a',
        'content_selector': 'article'
    },
    {
        'source_number': 21,
        'source_name': '넥스트유니콘',
        'base_url': 'https://www.nextunicorn.kr',
        'list_url_template': 'https://www.nextunicorn.kr/news/articleList.html?page={page}',
        'max_pages': 10,
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles a',
        'link_selector': 'h4.titles a',
        'content_selector': 'article'
    },
    {
        'source_number': 22,
        'source_name': '블로터',
        'base_url': 'https://www.bloter.net',
        'list_url_template': 'https://www.bloter.net/news/articleList.html?page={page}',
        'max_pages': 10,
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles a',
        'link_selector': 'h4.titles a',
        'content_selector': 'article'
    },
    {
        'source_number': 23,
        'source_name': '이코노미스트',
        'base_url': 'https://www.economist.co.kr',
        'list_url_template': 'https://www.economist.co.kr/news/articleList.html?page={page}',
        'max_pages': 10,
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles a',
        'link_selector': 'h4.titles a',
        'content_selector': 'article'
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
    """
    소스별로 여러 페이지의 기사 URL 수집
    """
    print(f"\n[{source['source_name']}] Collecting article URLs...")

    all_urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for page in range(1, source['max_pages'] + 1):
        print(f"  Page {page}/{source['max_pages']}...")

        try:
            list_url = source['list_url_template'].format(page=page)
            response = requests.get(list_url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"    [WARN] HTTP {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.select(source['article_selector'])

            page_urls = 0

            for article in articles:
                # 제목 찾기
                title_elem = article.select_one(source['title_selector'])
                if not title_elem:
                    continue

                title = title_elem.get_text().strip()

                # 투자 키워드 체크
                has_investment = any(kw.lower() in title.lower() for kw in INVESTMENT_KEYWORDS)
                has_excluded = any(kw in title for kw in EXCLUDED_KEYWORDS)

                if not has_investment or has_excluded:
                    continue

                # URL 찾기
                link_elem = article.select_one(source['link_selector'])
                if not link_elem or not link_elem.get('href'):
                    continue

                url = link_elem['href']

                # 절대 URL 변환
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

            print(f"    Found {page_urls} investment articles")
            time.sleep(1)

        except Exception as e:
            print(f"    [ERROR] {str(e)[:100]}")
            continue

    print(f"  [TOTAL] {len(all_urls)} URLs from {source['source_name']}")
    return all_urls


def crawl_article_content(url, content_selector):
    """
    기사 본문 크롤링
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 본문 추출
        content_elem = soup.select_one(content_selector)
        if not content_elem:
            return None

        # 텍스트만 추출
        content = content_elem.get_text(separator='\n', strip=True)

        return content

    except Exception as e:
        return None


def extract_info_from_content(title, content):
    """
    Gemini로 본문에서 정보 추출
    """
    if not content:
        return None

    # 본문이 너무 길면 앞부분만 (토큰 제한)
    content_truncated = content[:3000]

    prompt = f"""
다음 투자 뉴스 기사에서 정보를 추출하세요.

제목: {title}

본문:
{content_truncated}

추출할 정보 (JSON):
{{
    "company": "투자 받은 회사 이름",
    "investor": "투자자 (여러 명이면 쉼표로 구분)",
    "amount": "투자 금액",
    "stage": "투자 단계",
    "industry": "업종",
    "score": "11점 만점 점수 (금액 3, 투자자 3, 단계 2, 업종 1, 지역 1, 직원수 1)"
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
        print(f"    [ERROR] Gemini extraction: {str(e)[:50]}")
        return None


def main():
    """메인 실행"""

    print("="*60)
    print("Improved 10 Sources Collection")
    print("="*60)
    print("Strategy:")
    print("  1. Pagination (10 pages per source)")
    print("  2. Full article content crawling")
    print("  3. Gemini extraction from full content")
    print("="*60)

    all_results = []

    for source in IMPROVED_SOURCES:
        print(f"\n{'='*60}")
        print(f"Source: {source['source_name']}")
        print(f"{'='*60}")

        # 1단계: URL 수집
        article_urls = collect_article_urls(source)

        if not article_urls:
            print(f"  [SKIP] No articles found")
            continue

        # 2단계: 본문 크롤링 + 정보 추출
        print(f"\n  Crawling & extracting {len(article_urls)} articles...")

        for idx, article_data in enumerate(article_urls, 1):
            title = article_data['title']
            url = article_data['url']

            print(f"\n  [{idx}/{len(article_urls)}] {title[:50]}...")

            # 본문 크롤링
            content = crawl_article_content(url, source['content_selector'])

            if not content:
                print(f"    [FAIL] Content crawling failed")
                continue

            print(f"    [OK] Content crawled ({len(content)} chars)")

            # Gemini 정보 추출
            extracted = extract_info_from_content(title, content)

            if not extracted:
                print(f"    [FAIL] Extraction failed")
                continue

            company = extracted.get('company')
            investor = extracted.get('investor')
            amount = extracted.get('amount')
            score = extracted.get('score', 0)

            # 3가지 체크
            has_company = company and company.lower() != 'null'
            has_investor = investor and investor.lower() != 'null'
            has_amount = amount and amount.lower() != 'null'

            has_all_three = has_company and has_investor and has_amount

            print(f"    Company: {company if has_company else '[NONE]'}")
            print(f"    Investor: {investor if has_investor else '[NONE]'}")
            print(f"    Amount: {amount if has_amount else '[NONE]'}")
            print(f"    Score: {score}")
            print(f"    Result: {'[PERFECT]' if has_all_three else '[INCOMPLETE]'}")

            # 결과 저장
            all_results.append({
                'source_number': source['source_number'],
                'source_name': source['source_name'],
                'title': title,
                'url': url,
                'content': content[:500],  # 일부만
                'company': company,
                'investor': investor,
                'amount': amount,
                'stage': extracted.get('stage'),
                'industry': extracted.get('industry'),
                'score': score,
                'has_all_three': has_all_three
            })

            time.sleep(3)  # Rate limiting

            # 진행 중 저장 (10개마다)
            if len(all_results) % 10 == 0:
                print(f"\n  [CHECKPOINT] {len(all_results)} articles processed")

    # 최종 결과
    print(f"\n{'='*60}")
    print("Final Results")
    print(f"{'='*60}")

    total = len(all_results)
    perfect = sum(1 for r in all_results if r['has_all_three'])

    print(f"\n[Overall]")
    print(f"  Total collected: {total}")
    print(f"  Perfect (3 items): {perfect} ({perfect/total*100:.1f}%)")

    # 완벽한 기사 출력
    perfect_articles = [r for r in all_results if r['has_all_three']]

    if perfect_articles:
        print(f"\n{'='*60}")
        print(f"Perfect Articles ({len(perfect_articles)})")
        print(f"{'='*60}")

        for idx, article in enumerate(perfect_articles[:10], 1):
            print(f"\n{idx}. [{article['source_name']}]")
            print(f"   {article['title']}")
            print(f"   Company: {article['company']}")
            print(f"   Investor: {article['investor']}")
            print(f"   Amount: {article['amount']}")
            print(f"   Score: {article['score']}")

    # 데이터베이스 저장
    print(f"\n{'='*60}")
    print("Saving to Database")
    print(f"{'='*60}")

    # TODO: 데이터베이스 저장 로직


if __name__ == '__main__':
    main()
