#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
벤처스퀘어 현재 상태 디버깅
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

url = 'https://www.venturesquare.net/category/news/'

print("="*60)
print("Debugging Venturesquare NOW")
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
    if len(text) > 10:
        # 투자/유치 키워드 확인
        if any(kw in text for kw in ['투자', '유치', '시리즈', '펀딩']):
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
else:
    print("[WARNING] No investment links found!")
    print("\nShowing first 20 article titles:")
    count = 0
    for link in links:
        text = link.get_text().strip()
        if len(text) > 10:
            count += 1
            safe_print(f"\n{count}. {text[:60]}")
            safe_print(f"   {link['href'][:80]}")
            if count >= 20:
                break
