#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아웃스탠딩 디버깅
"""

import requests
from bs4 import BeautifulSoup

def safe_print(text):
    """인코딩 에러 방지"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'))

# 투자 기사 하나 선택
url = 'https://outstanding.kr/gotomarket20250108/'

print("="*60)
print("Debugging Outstanding")
print("="*60)
safe_print(f"URL: {url}\n")

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
    if len(text) > 100:
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
