#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glance Media (Startup Weekly) 디버깅
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

# 가능한 페이지들
urls_to_try = [
    'http://glance.media/',
    'http://glance.media/news',
    'http://glance.media/archive',
    'http://glance.media/articles',
    'http://glance.media/posts',
    'http://startupweekly.kr/',
    'http://www.startupweekly.kr/'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for url in urls_to_try:
    print("="*60)
    print("Trying URL")
    print("="*60)
    safe_print(f"URL: {url}\n")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"HTTP Status: {response.status_code}\n")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 페이지 타이틀
            title = soup.find('title')
            if title:
                safe_print(f"Page Title: {title.get_text()}")

            # 모든 링크 찾기
            links = soup.find_all('a', href=True)
            print(f"[All Links] Total: {len(links)}\n")

            if len(links) > 10:  # 충분한 링크가 있으면
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
                    print("*** FOUND! This URL has investment articles! ***")
                    print("\nFirst 10 investment articles:")
                    for idx, link_data in enumerate(investment_links[:10], 1):
                        safe_print(f"\n{idx}. {link_data['text']}")
                        safe_print(f"   URL: {link_data['href']}")
                    break

    except Exception as e:
        print(f"[ERROR] {str(e)[:100]}")

    print("\n")

print("\n" + "="*60)
print("Conclusion")
print("="*60)
print("\nGlance Media operates Startup Weekly as a NEWSLETTER service.")
print("They send weekly emails, not a traditional news website.")
print("Articles are delivered via email, not hosted on a web archive.")
print("\nThis is NOT suitable for web scraping.")
