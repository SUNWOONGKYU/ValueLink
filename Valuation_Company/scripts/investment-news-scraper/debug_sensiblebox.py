#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서블박스 디버깅
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

# 여러 가능한 URL 시도
urls_to_try = [
    'https://www.sensiblebox.kr/',
    'https://sensiblebox.kr/',
    'https://www.sensiblebox.co.kr/',
    'https://sensiblebox.co.kr/'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for url in urls_to_try:
    print("="*60)
    print("Trying Sensiblebox")
    print("="*60)
    safe_print(f"URL: {url}\n")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"HTTP Status: {response.status_code}\n")

        if response.status_code == 200:
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
                print("FOUND! This URL works!")
                print("\nFirst 10 investment articles:")
                for idx, link_data in enumerate(investment_links[:10], 1):
                    safe_print(f"\n{idx}. {link_data['text']}")
                    safe_print(f"   URL: {link_data['href']}")

                # 첫 번째 기사 본문 크롤링 테스트
                print(f"\n\n{'='*60}")
                print("Testing content crawling for first article")
                print("="*60)

                first_url = investment_links[0]['href']
                if not first_url.startswith('http'):
                    base_url = url.rstrip('/')
                    first_url = base_url + first_url

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
                    found = False
                    for selector in selectors:
                        elem = article_soup.select_one(selector)
                        if elem:
                            content = elem.get_text(separator='\n', strip=True)
                            if len(content) > 200:
                                print(f"\nOK {selector}: Found {len(content)} chars")
                                safe_print(f"   Preview: {content[:200]}...")
                                found = True
                                break
                            else:
                                print(f"OK {selector}: Found but too short ({len(content)} chars)")
                        else:
                            print(f"X {selector}: Not found")

                    if not found:
                        print("\n[WARNING] Could not find suitable content selector")

                break  # 성공하면 루프 종료
            else:
                print("[INFO] No investment-related links found with this URL")

    except Exception as e:
        print(f"[ERROR] {str(e)}")

    print("\n")
