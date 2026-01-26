#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스타트업투데이 기사 페이지 HTML 구조 확인
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

url = 'https://startuptoday.kr/news/articleView.html?idxno=52012'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)

print(f"HTTP Status: {response.status_code}\n")

soup = BeautifulSoup(response.content, 'html.parser')

# 모든 div 클래스 확인
print("All div classes that might contain article content:\n")

divs_with_class = soup.find_all('div', class_=True)
for div in divs_with_class:
    classes = ' '.join(div.get('class', []))
    text = div.get_text(strip=True)
    if len(text) > 100:  # 충분히 긴 텍스트만
        safe_print(f"Class: {classes}")
        safe_print(f"Text length: {len(text)}")
        safe_print(f"Preview: {text[:100]}...")
        print("-" * 60)

# 모든 div id 확인
print("\n\nAll div IDs that might contain article content:\n")

divs_with_id = soup.find_all('div', id=True)
for div in divs_with_id:
    div_id = div.get('id', '')
    text = div.get_text(strip=True)
    if len(text) > 100:
        safe_print(f"ID: {div_id}")
        safe_print(f"Text length: {len(text)}")
        safe_print(f"Preview: {text[:100]}...")
        print("-" * 60)
