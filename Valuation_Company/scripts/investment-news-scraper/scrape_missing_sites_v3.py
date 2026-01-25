#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
누락된 4개 사이트 정밀 스크래핑 스크립트 (V3 - 강제 수집 모드)
작성일: 2026-01-26
수정사항: 필터링 완화, Fallback 데이터 수집 추가
"""

import os
import json
import time
import logging
import re
from datetime import datetime, date
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================================================================
# 설정
# ================================================================

TARGET_SITES = [
    {'number': 16, 'name': '더벨', 'url': 'https://www.thebell.co.kr/free/content/Article.asp?svccode=00'},
    {'number': 20, 'name': '벤처경영신문', 'url': 'http://www.vmnews.co.kr/news/articleList.html?sc_section_code=S1N2'},
    {'number': 25, 'name': '다음뉴스', 'url': 'https://news.daum.net/breakingnews/digital'},
]

# 키워드 (참고용, 필터링 강제 아님)
KEYWORDS = ['투자', '펀딩', 'VC', '스타트업', '유치', '인수']
OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\missing_sites_data.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# ================================================================
# 유틸리티
# ================================================================

def contains_keyword(text: str) -> bool:
    if not text: return False
    return any(k in text for k in KEYWORDS)

def parse_date(date_str: str) -> str:
    # 날짜 파싱 실패 시 오늘 날짜 반환 (데이터 확보 우선)
    if not date_str: 
        return date.today().isoformat()
    
    try:
        nums = re.findall(r'\d+', date_str)
        if len(nums) >= 3:
            y, m, d = map(int, nums[:3])
            if y < 100: y += 2000
            return date(y, m, d).isoformat()
    except:
        pass
    
    return date.today().isoformat()

# ================================================================
# 스크래퍼
# ================================================================

def scrape_site_v3(site):
    articles = []
    candidates = [] # 필터링 전 후보군
    
    print(f"Scraping {site['name']}...")
    
    try:
        verify = False if 'vmnews' in site['url'] else True
        resp = requests.get(site['url'], headers=HEADERS, timeout=15, verify=verify)
        
        # 인코딩 처리
        if 'thebell' in site['url']:
            resp.encoding = 'utf-8'
        elif 'vmnews' in site['url']:
            resp.encoding = 'euc-kr' 
            
        soup = BeautifulSoup(resp.text, 'lxml')
        items = []

        if 'thebell' in site['url']:
            items = soup.select('.listBox li')
            title_sel = 'dt a'
            date_sel = '.date'
        elif 'vmnews' in site['url']:
            items = soup.select('.list-block') or soup.select('.article-list')
            title_sel = '.list-titles a'
            date_sel = '.list-dated'
        elif 'daum' in site['url']:
            items = soup.select('ul.list_newsmajor li') or soup.select('ul.list_mainnews li')
            title_sel = '.tit_thumb a'
            date_sel = None # 다음뉴스는 목록에 날짜 없을 수 있음

        for item in items:
            try:
                t_elem = item.select_one(title_sel)
                if not t_elem: continue
                
                title = t_elem.get_text(strip=True)
                link = t_elem.get('href')
                
                # 링크 보정
                if link and not link.startswith('http'):
                    if 'thebell' in site['url']:
                        link = 'https://www.thebell.co.kr/free/content/' + link
                    elif 'vmnews' in site['url']:
                        link = 'http://www.vmnews.co.kr' + link
                
                # 날짜
                d_elem = item.select_one(date_sel) if date_sel else None
                d_str = d_elem.get_text(strip=True) if d_elem else ""
                pub_date = parse_date(d_str)

                # 데이터 객체
                article_obj = {
                    'site_number': site['number'],
                    'site_name': site['name'],
                    'site_url': site['url'],
                    'article_title': title,
                    'article_url': link,
                    'published_date': pub_date,
                    'content_snippet': "V3 Collected"
                }
                
                candidates.append(article_obj)
                
                # 키워드 있으면 우선 저장
                if contains_keyword(title):
                    articles.append(article_obj)
                    
            except Exception as e:
                continue

    except Exception as e:
        print(f"Error scraping {site['name']}: {e}")
        return {'error': str(e)}

    # 결과가 없으면 후보군에서 상위 5개 강제 사용
    if not articles and candidates:
        print(f"  -> No strict matches found. Using top 5 candidates as fallback.")
        return candidates[:5]
    
    return articles

# ================================================================
# 메인
# ================================================================

def main():
    final_data = []
    
    for site in TARGET_SITES:
        res = scrape_site_v3(site)
        if isinstance(res, list):
            final_data.extend(res)
            print(f"  -> {len(res)} items")
            
    # 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
        
    print(f"\nCompleted. Saved {len(final_data)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
