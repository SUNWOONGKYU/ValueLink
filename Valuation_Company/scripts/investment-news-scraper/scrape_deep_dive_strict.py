#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 정밀 재수집 (Deep Dive V2)
작성일: 2026-01-26
대상: 10개 사이트
기간: 2026-01-01 ~ 2026-01-25
조건: 키워드(투자, 유치) 포함
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

# 수집 대상
TARGET_SITES = [
    {'number': 9, 'name': '벤처스퀘어', 'url_pattern': 'https://www.venturesquare.net/category/news-contents/news-trends/news/page/{page}/', 'type': 'wordpress'},
    {'number': 10, 'name': '플래텀', 'url_pattern': 'https://platum.kr/category/investment/page/{page}', 'type': 'wordpress'},
    {'number': 11, 'name': '스타트업투데이', 'url_pattern': 'https://www.startuptoday.kr/news/articleList.html?page={page}&sc_section_code=S1N2&view_type=sm', 'type': 'ndsoft'},
    {'number': 12, 'name': '스타트업엔', 'url_pattern': 'https://www.startupn.kr/news/articleList.html?page={page}&sc_section_code=S1N2&view_type=sm', 'type': 'ndsoft'},
    {'number': 13, 'name': '아웃스탠딩', 'url_pattern': 'https://outstanding.kr/category/news/page/{page}', 'type': 'wordpress_custom'},
    {'number': 14, 'name': '비석세스', 'url_pattern': 'https://besuccess.com/category/investment/page/{page}/', 'type': 'wordpress'},
    {'number': 19, 'name': 'AI타임스', 'url_pattern': 'https://www.aitimes.com/news/articleList.html?page={page}&sc_section_code=S1N1&view_type=sm', 'type': 'ndsoft'},
    {'number': 21, 'name': '넥스트유니콘', 'url_pattern': 'https://nextunicorn.kr/newsroom', 'type': 'dynamic'}, # 스킵 예상
    {'number': 22, 'name': '블로터', 'url_pattern': 'https://www.bloter.net/news/articleList.html?page={page}&sc_section_code=S1N1&view_type=sm', 'type': 'ndsoft'},
    {'number': 23, 'name': '이코노미스트', 'url_pattern': 'https://economist.co.kr/section/1000?page={page}', 'type': 'generic'}
]

# 필수 키워드 (적어도 하나는 포함되어야 함)
KEYWORDS = ['투자', '유치', '펀딩', '시리즈', 'VC', '인수', 'M&A']

# 기간 설정 (엄격)
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 1, 25)

MAX_PAGES = 10 # 10페이지까지 조회

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\deep_dive_v2.json'

# ================================================================
# 함수
# ================================================================

def contains_keyword(text):
    if not text: return False
    return any(k in text for k in KEYWORDS)

def get_soup(url, encoding='utf-8'):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        resp.encoding = encoding
        return BeautifulSoup(resp.text, 'lxml')
    except Exception as e:
        # print(f"    Error fetching {url}: {e}")
        return None

def parse_date(date_str):
    if not date_str: return None
    try:
        nums = re.findall(r'\d+', date_str)
        if len(nums) >= 3:
            y, m, d = map(int, nums[:3])
            if y < 100: y += 2000
            return date(y, m, d)
    except: pass
    return None

def is_target_date(d):
    if not d: return False
    return START_DATE <= d <= END_DATE

# ================================================================
# 파서
# ================================================================

def parse_wordpress(soup, site_info):
    articles = []
    items = soup.select('article') or soup.select('.post') or soup.select('.post-item')
    for item in items:
        try:
            t = item.select_one('h2 a') or item.select_one('h3 a') or item.select_one('.title a') or item.select_one('a')
            if not t: continue
            title = t.get_text(strip=True)
            link = t.get('href')
            
            d = item.select_one('time') or item.select_one('.date')
            d_str = d.get_text(strip=True) if d else ""
            pub_date = parse_date(d_str)
            
            if contains_keyword(title) and is_target_date(pub_date):
                articles.append({'title': title, 'url': link, 'date': pub_date.isoformat()})
        except: continue
    return articles

def parse_ndsoft(soup, site_info):
    articles = []
    items = soup.select('.list-block') or soup.select('.article-list') or soup.select('ul.art_list_all li') or soup.select('.list_box')
    for item in items:
        try:
            t = item.select_one('.list-titles a') or item.select_one('.tit a') or item.select_one('a.tit')
            if not t: continue
            title = t.get_text(strip=True)
            link = t.get('href')
            if link and not link.startswith('http'):
                base = '/'.join(site_info['url_pattern'].split('/')[:3])
                link = base + link
            
            d = item.select_one('.list-dated') or item.select_one('.date')
            d_str = d.get_text(strip=True) if d else ""
            pub_date = parse_date(d_str)
            
            if contains_keyword(title) and is_target_date(pub_date):
                articles.append({'title': title, 'url': link, 'date': pub_date.isoformat()})
        except: continue
    return articles

def parse_generic(soup, site_info):
    articles = []
    links = soup.select('a')
    seen = set()
    for link in links:
        try:
            title = link.get_text(strip=True)
            href = link.get('href')
            if not href or len(title) < 10 or href in seen: continue
            
            if contains_keyword(title):
                seen.add(href)
                if not href.startswith('http'):
                    base = '/'.join(site_info['url_pattern'].split('/')[:3])
                    href = base + href
                
                # 날짜 추정 불가 시 일단 수집하되, 나중에 필터링될 수 있음.
                # 여기서는 '2026' 텍스트가 근처에 있으면 수집
                parent_text = link.parent.get_text()
                pub_date = parse_date(parent_text)
                
                if is_target_date(pub_date):
                     articles.append({'title': title, 'url': href, 'date': pub_date.isoformat()})
        except: continue
    return articles[:15]

# ================================================================
# 메인
# ================================================================

def main():
    all_data = []
    print(f"Deep Dive Scraping: {START_DATE} ~ {END_DATE}")
    
    for site in TARGET_SITES:
        site_name = site['name']
        print(f"Checking {site_name}...", end='', flush=True)
        
        if site_name == '넥스트유니콘':
            print(" Skipped (Dynamic)")
            continue
            
        site_cnt = 0
        for page in range(1, MAX_PAGES + 1):
            url = site['url_pattern'].format(page=page)
            encoding = 'euc-kr' if site['type'] == 'ndsoft' else 'utf-8'
            if site_name == '블로터': encoding = 'utf-8'
            
            soup = get_soup(url, encoding)
            if not soup: continue
            
            items = []
            if site['type'] == 'wordpress' or site['type'] == 'wordpress_custom':
                items = parse_wordpress(soup, site)
            elif site['type'] == 'ndsoft':
                items = parse_ndsoft(soup, site)
            else:
                items = parse_generic(soup, site)
                
            if items:
                for item in items:
                    if not any(d['article_url'] == item['url'] for d in all_data):
                        all_data.append({
                            'site_number': site['number'],
                            'site_name': site_name,
                            'site_url': site['url_pattern'].split('?')[0],
                            'article_title': item['title'],
                            'article_url': item['url'],
                            'published_date': item['date'],
                            'content_snippet': None
                        })
                        site_cnt += 1
            else:
                if page > 2: break # 2페이지까지 없으면 중단
                
        print(f" Found {site_cnt} items")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal: {len(all_data)} items saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
