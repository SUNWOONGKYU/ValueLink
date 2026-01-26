#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
페이지 구조 디버깅
"""

import requests
from bs4 import BeautifulSoup

def debug_page(url, name):
    """페이지 구조 확인"""

    print(f"\n{'='*60}")
    print(f"Debugging: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        print(f"HTTP Status: {response.status_code}")

        if response.status_code != 200:
            print("[ERROR] Failed to fetch")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. article 태그 찾기
        articles = soup.find_all('article')
        print(f"\n[article 태그] Found: {len(articles)}")

        if articles:
            article = articles[0]
            print(f"  First article HTML (200 chars):")
            print(f"  {str(article)[:200]}...")

            # 제목 찾기 시도
            titles = article.find_all(['h1', 'h2', 'h3', 'h4'])
            print(f"\n  [Titles in first article]")
            for t in titles[:3]:
                print(f"    {t.name}: {t.get_text().strip()[:60]}...")

        # 2. 모든 링크 찾기
        links = soup.find_all('a', href=True)
        print(f"\n[Links] Total: {len(links)}")

        # 투자 키워드 포함 링크
        investment_links = []
        for link in links:
            text = link.get_text().strip()
            if any(kw in text for kw in ['투자', '유치', '시리즈', '펀딩']):
                investment_links.append({
                    'text': text[:60],
                    'href': link['href'][:60]
                })

        print(f"\n[Investment-related links] Found: {len(investment_links)}")
        for idx, link in enumerate(investment_links[:5], 1):
            print(f"  {idx}. {link['text']}...")
            print(f"     URL: {link['href']}...")

    except Exception as e:
        print(f"[ERROR] {str(e)}")

# 테스트 URL
debug_page('https://www.venturesquare.net/category/news/', '벤처스퀘어')
debug_page('https://besuccess.com/category/news/', '비석세스')
