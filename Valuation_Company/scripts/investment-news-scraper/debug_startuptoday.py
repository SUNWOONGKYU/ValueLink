#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스타트업투데이 디버깅
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

def debug_startuptoday():
    """스타트업투데이 페이지 분석"""

    url = 'https://startuptoday.kr/news/articleList.html'

    print("="*60)
    print("Debugging StartupToday")
    print("="*60)
    print(f"URL: {url}\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"HTTP Status: {response.status_code}\n")

        if response.status_code != 200:
            print("[ERROR] Failed to fetch")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. 모든 링크 찾기
        links = soup.find_all('a', href=True)
        print(f"[All Links] Total: {len(links)}\n")

        # 2. "투자" 또는 "유치" 포함 링크
        investment_links = []
        for link in links:
            text = link.get_text().strip()
            if any(kw in text for kw in ['투자', '유치', '시리즈', '펀딩']):
                investment_links.append({
                    'text': text[:80],
                    'href': link['href'][:80]
                })

        print(f"[Investment-related links] Found: {len(investment_links)}")
        if investment_links:
            for idx, link_data in enumerate(investment_links[:10], 1):
                safe_print(f"\n{idx}. {link_data['text']}")
                safe_print(f"   URL: {link_data['href']}")

        # 3. 첫 번째 투자 기사의 본문 크롤링 시도 (articleView만)
        article_links = [link for link in investment_links if 'articleView' in link['href']]

        if article_links:
            print(f"\n\n{'='*60}")
            print("Testing content crawling for first article")
            print("="*60)

            first_url = article_links[0]['href']
            if not first_url.startswith('http'):
                first_url = 'https://startuptoday.kr' + first_url

            safe_print(f"Article URL: {first_url}\n")

            article_response = requests.get(first_url, headers=headers, timeout=10)
            print(f"HTTP Status: {article_response.status_code}")

            if article_response.status_code == 200:
                article_soup = BeautifulSoup(article_response.content, 'html.parser')

                # 다양한 본문 선택자 시도
                selectors = [
                    'div.entry-content',
                    'article',
                    'div.article-content',
                    'div.content',
                    'div.post-content',
                    'div#article-view-content-div',
                    'div.article_view',
                    'div.news_body',
                    'div#articleBody'
                ]

                print("\nTrying different content selectors:")
                for selector in selectors:
                    elem = article_soup.select_one(selector)
                    if elem:
                        content = elem.get_text(separator='\n', strip=True)
                        print(f"\nOK {selector}: Found {len(content)} chars")
                        if len(content) > 200:
                            safe_print(f"   Preview: {content[:200]}...")
                            break
                    else:
                        print(f"X {selector}: Not found")

                # article 태그 확인
                articles = article_soup.find_all('article')
                print(f"\n\n[article tags] Found: {len(articles)}")
                if articles:
                    print(f"First article HTML (500 chars):")
                    safe_print(str(articles[0])[:500])

    except Exception as e:
        print(f"[ERROR] {str(e)}")


if __name__ == '__main__':
    debug_startuptoday()
