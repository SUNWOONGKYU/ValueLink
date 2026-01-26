#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLANCE MEDIA 디버깅
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
    'https://www.glancemedia.co.kr/',
    'https://glancemedia.co.kr/',
    'https://www.glancemedia.kr/',
    'https://glancemedia.kr/',
    'https://www.glance.co.kr/',
    'https://glance.co.kr/'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for url in urls_to_try:
    print("="*60)
    print("Trying GLANCE MEDIA")
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
                print("*** FOUND! This URL works! ***")
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
                    if first_url.startswith('/'):
                        first_url = base_url + first_url
                    else:
                        first_url = base_url + '/' + first_url

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
                        'div#article-view-content-div',
                        'div.article_view',
                        'div.news_body',
                        'div#articleBody'
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

                    if not found:
                        print("\n[WARNING] Could not find suitable content selector")
                        print("\nShowing all div classes with content > 500 chars:")

                        divs = article_soup.find_all('div', class_=True)
                        for div in divs[:5]:
                            classes = ' '.join(div.get('class', []))
                            text = div.get_text(strip=True)
                            if len(text) > 500:
                                safe_print(f"\nClass: {classes}")
                                safe_print(f"Length: {len(text)}")
                                safe_print(f"Preview: {text[:150]}...")

                print(f"\n*** SUCCESS! Add this to sources list ***")
                print(f"URL: {url}")
                break  # 성공하면 루프 종료

            else:
                print("[INFO] No investment-related links found with this URL")
                if len(links) > 0:
                    print("\nShowing first 5 article links:")
                    count = 0
                    for link in links:
                        text = link.get_text().strip()
                        if len(text) > 10:
                            count += 1
                            safe_print(f"\n{count}. {text[:60]}")
                            safe_print(f"   {link['href'][:80]}")
                            if count >= 5:
                                break

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Connection failed: {str(e)[:100]}")

    print("\n")
