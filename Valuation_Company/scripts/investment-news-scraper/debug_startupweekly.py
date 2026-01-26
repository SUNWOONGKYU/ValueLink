#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스타트업위클리 디버깅
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

url = 'https://www.startupweekly.kr/'

print("="*60)
print("Debugging Startup Weekly")
print("="*60)
safe_print(f"URL: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"HTTP Status: {response.status_code}\n")

    if response.status_code != 200:
        print("[ERROR] Failed to fetch")

        # Try alternative URL
        alt_url = 'https://startupweekly.kr/'
        print(f"\nTrying alternative: {alt_url}")
        response = requests.get(alt_url, headers=headers, timeout=10)
        print(f"HTTP Status: {response.status_code}\n")

    soup = BeautifulSoup(response.content, 'html.parser')

    # 모든 링크 찾기
    links = soup.find_all('a', href=True)
    print(f"[All Links] Total: {len(links)}\n")

    # 투자 관련 링크
    investment_links = []
    for link in links:
        text = link.get_text().strip()
        if len(text) > 10 and any(kw in text for kw in ['투자', '유치', '시리즈', '펀딩']):
            investment_links.append({
                'text': text[:80],
                'href': link['href'][:100]
            })

    print(f"[Investment-related links] Found: {len(investment_links)}\n")

    if investment_links:
        print("First 10 investment articles:")
        for idx, link_data in enumerate(investment_links[:10], 1):
            safe_print(f"\n{idx}. {link_data['text']}")
            safe_print(f"   URL: {link_data['href']}")

        # 첫 번째 기사 본문 크롤링 테스트
        if investment_links:
            print(f"\n\n{'='*60}")
            print("Testing content crawling for first article")
            print("="*60)

            first_url = investment_links[0]['href']
            if not first_url.startswith('http'):
                first_url = 'https://www.startupweekly.kr' + first_url

            safe_print(f"Article URL: {first_url}\n")

            article_response = requests.get(first_url, headers=headers, timeout=10)
            print(f"HTTP Status: {article_response.status_code}\n")

            if article_response.status_code == 200:
                article_soup = BeautifulSoup(article_response.content, 'html.parser')

                # 다양한 본문 선택자 시도
                selectors = [
                    'div.article-body',
                    'div#article-view',
                    'div.entry-content',
                    'article',
                    'div.article-content',
                    'div.content',
                    'div.post-content',
                    'div#article-view-content-div'
                ]

                print("Trying different content selectors:")
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
    else:
        print("[INFO] No investment-related links found!")

except Exception as e:
    print(f"[ERROR] {str(e)}")
