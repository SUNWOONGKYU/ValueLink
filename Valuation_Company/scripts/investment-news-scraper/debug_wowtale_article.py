#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WOWTALE 실제 투자 뉴스 기사 테스트
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

# 실제 투자 뉴스 기사
url = 'https://wowtale.net/2026/01/26/253799/'  # 딥실버웨어 투자 유치

print("="*60)
print("Testing WOWTALE Investment News Article")
print("="*60)
safe_print(f"URL: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)
print(f"HTTP Status: {response.status_code}\n")

soup = BeautifulSoup(response.content, 'html.parser')

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
    'div#articleBody',
    'div.post_content'
]

print("Trying different content selectors:")
for selector in selectors:
    elem = soup.select_one(selector)
    if elem:
        content = elem.get_text(separator='\n', strip=True)
        print(f"\nOK {selector}: Found {len(content)} chars")
        if len(content) > 200:
            safe_print(f"   Preview: {content[:200]}...")
            print(f"\n*** This selector works! ***")
            break
        else:
            safe_print(f"   Too short: {content[:100]}")
    else:
        print(f"X {selector}: Not found")

# 모든 div 클래스 확인 (긴 텍스트만)
print("\n\n" + "="*60)
print("All div classes with content > 500 chars:")
print("="*60)

divs = soup.find_all('div', class_=True)
for div in divs:
    classes = ' '.join(div.get('class', []))
    text = div.get_text(strip=True)
    if len(text) > 500:
        safe_print(f"\nClass: {classes}")
        safe_print(f"Length: {len(text)}")
        safe_print(f"Preview: {text[:150]}...")
        print("-" * 60)
