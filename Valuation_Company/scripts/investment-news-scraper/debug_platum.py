#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플래텀 페이지 직접 확인
"""

import requests
from bs4 import BeautifulSoup

def debug_platum():
    """플래텀 페이지 분석"""

    url = 'https://platum.kr/archives/category/startup/'

    print("="*60)
    print("Debugging Platum")
    print("="*60)
    print(f"URL: {url}\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"HTTP Status: {response.status_code}\n")

        if response.status_code != 200:
            print("[ERROR] Failed to fetch")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. 모든 링크
        all_links = soup.find_all('a', href=True)
        print(f"[All Links] Total: {len(all_links)}\n")

        # 2. 텍스트가 있는 링크
        text_links = []
        for link in all_links:
            text = link.get_text().strip()
            if len(text) > 10:
                text_links.append({
                    'text': text,
                    'href': link['href']
                })

        print(f"[Links with text (>10 chars)] Total: {len(text_links)}\n")

        # 3. "투자" 또는 "유치" 포함 링크
        investment_links = []
        for link_data in text_links:
            text = link_data['text']
            if '투자' in text or '유치' in text:
                investment_links.append(link_data)

        print(f"[Investment Links (투자/유치)] Total: {len(investment_links)}\n")

        if investment_links:
            print("First 10 investment links:")
            for idx, link_data in enumerate(investment_links[:10], 1):
                print(f"\n{idx}. {link_data['text'][:60]}")
                print(f"   URL: {link_data['href'][:80]}")
        else:
            print("[WARNING] NO investment links found!\n")
            print("Sample of all text links (first 10):")
            for idx, link_data in enumerate(text_links[:10], 1):
                print(f"\n{idx}. {link_data['text'][:60]}")
                print(f"   URL: {link_data['href'][:80]}")

        # 4. article 태그 확인
        articles = soup.find_all('article')
        print(f"\n\n[Articles] Found: {len(articles)}")

        if articles:
            print("\nFirst article structure:")
            print(str(articles[0])[:500])

    except Exception as e:
        print(f"[ERROR] {str(e)}")


if __name__ == '__main__':
    debug_platum()
