#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 기사 본문 크롤링
"""

import requests
from bs4 import BeautifulSoup
import time

def fetch_article_content(url):
    """
    뉴스 기사 URL에서 본문 추출

    Args:
        url: 기사 URL

    Returns:
        본문 텍스트 또는 None
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # 사이트별 본문 추출 로직
        content = None

        # 벤처스퀘어
        if 'venturesquare.net' in url:
            article = soup.find('div', class_='entry-content')
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 스타트업투데이
        elif 'startuptoday.kr' in url:
            article = soup.find('div', {'id': 'article-view-content-div'})
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 아웃스탠딩
        elif 'outstanding.kr' in url:
            article = soup.find('div', class_='post-content')
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 더벨
        elif 'thebell.co.kr' in url:
            article = soup.find('div', {'id': 'article_body'})
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 더브이씨
        elif 'thevc.kr' in url:
            article = soup.find('div', class_='article-body')
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 스타트업엔
        elif 'startupn.kr' in url:
            article = soup.find('div', {'id': 'article-view-content-div'})
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 블로터
        elif 'bloter.net' in url:
            article = soup.find('div', class_='article-body')
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 이코노미스트
        elif 'economist.co.kr' in url:
            article = soup.find('div', {'id': 'articleBody'})
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 플래텀
        elif 'platum.kr' in url:
            article = soup.find('div', class_='entry-content')
            if article:
                content = article.get_text(strip=True, separator=' ')

        # AI타임스
        elif 'aitimes.com' in url:
            article = soup.find('div', {'id': 'article-view-content-div'})
            if article:
                content = article.get_text(strip=True, separator=' ')

        # 일반적인 방법 (article 태그)
        else:
            article = soup.find('article')
            if article:
                content = article.get_text(strip=True, separator=' ')
            else:
                # 가장 긴 div 찾기
                divs = soup.find_all('div')
                longest_div = max(divs, key=lambda x: len(x.get_text()), default=None)
                if longest_div:
                    content = longest_div.get_text(strip=True, separator=' ')

        # 본문 정리
        if content:
            # 길이 제한 (5000자)
            content = content[:5000]
            return content

        return None

    except Exception as e:
        print(f"[ERROR] Failed to fetch content from {url}: {e}")
        return None

def test_fetch():
    """테스트 함수"""
    test_urls = [
        'https://www.venturesquare.net/example',
        'https://startuptoday.kr/example'
    ]

    for url in test_urls:
        print(f"\nTesting: {url}")
        content = fetch_article_content(url)
        if content:
            print(f"Content length: {len(content)}")
            print(f"Preview: {content[:200]}...")
        else:
            print("Failed to fetch content")
        time.sleep(1)

if __name__ == '__main__':
    test_fetch()
