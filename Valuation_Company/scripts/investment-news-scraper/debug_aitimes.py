#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI타임스 디버깅
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

url = 'https://www.aitimes.com/news/articleList.html'

print("="*60)
print("Debugging AI Times")
print("="*60)
safe_print(f"URL: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)

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
            'href': link['href'][:80]
        })

print(f"[Investment-related links] Found: {len(investment_links)}")
if investment_links:
    for idx, link_data in enumerate(investment_links[:10], 1):
        safe_print(f"\n{idx}. {link_data['text']}")
        safe_print(f"   URL: {link_data['href']}")
else:
    print("\n[INFO] No investment-related links found!")
    print("\nShowing first 10 article links:")

    article_count = 0
    for link in links:
        text = link.get_text().strip()
        href = link['href']
        if len(text) > 10 and 'articleView' in href:
            article_count += 1
            safe_print(f"\n{article_count}. {text[:60]}")
            safe_print(f"   URL: {href[:80]}")

            if article_count >= 10:
                break
