#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플래텀 수정 - UTF-8 인코딩 처리
"""

import requests
from bs4 import BeautifulSoup

url = 'https://platum.kr/archives/category/startup/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("="*60)
print("Platum - Fixed with UTF-8")
print("="*60)

response = requests.get(url, headers=headers, timeout=10)

# UTF-8로 디코딩
response.encoding = 'utf-8'

print(f"Status: {response.status_code}")
print(f"Encoding: {response.encoding}\n")

soup = BeautifulSoup(response.content, 'html.parser')

# 모든 링크
all_links = soup.find_all('a', href=True)

print(f"Total links: {len(all_links)}\n")

# 투자/유치 포함 링크
investment_links = []

for link in all_links:
    # UTF-8로 제대로 읽기
    text = link.get_text().strip()

    if len(text) < 10:
        continue

    # 투자 또는 유치
    if '투자' in text or '유치' in text:
        investment_links.append({
            'text': text,
            'href': link['href']
        })

print(f"Investment links: {len(investment_links)}\n")

if investment_links:
    print("First 10:")
    for idx, link_data in enumerate(investment_links[:10], 1):
        try:
            print(f"\n{idx}. {link_data['text'][:60]}")
            print(f"   {link_data['href'][:80]}")
        except:
            print(f"\n{idx}. [encoding error]")
            print(f"   {link_data['href'][:80]}")
else:
    print("[ERROR] Still no investment links!")
    print("\nAll text links (first 10):")

    count = 0
    for link in all_links:
        text = link.get_text().strip()
        if len(text) > 10:
            count += 1
            try:
                print(f"\n{count}. {text[:60]}")
                print(f"   {link['href'][:80]}")
            except:
                print(f"\n{count}. [encoding error]")
                print(f"   {link['href'][:80]}")

            if count >= 10:
                break
