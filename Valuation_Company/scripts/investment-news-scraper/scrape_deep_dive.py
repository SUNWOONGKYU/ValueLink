#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
萨聖 新闻 深圳 スクレイピング (Deep Dive)
作成日: 2026-01-26
対象: 10個 サイトの 過去 10ページまで 収集
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
# 設定
# ================================================================

# 収集 対象 び ページネーション パターン
# {page}部分が ページ 番号で 置換えられる
TARGET_SITES = [
    {
        'number': 9, 
        'name': 'ベンチャスクエア',
        'url_pattern': 'https://www.venturesquare.net/category/news-contents/news-trends/news/page/{page}/',
        'type': 'wordpress'
    },
    {
        'number': 10, 
        'name': 'フレタム',
        'url_pattern': 'https://platum.kr/category/investment/page/{page}',
        'type': 'wordpress'
    },
    {
        'number': 11, 
        'name': 'スタルトアップトトゥデイ',
        'url_pattern': 'https://www.startuptoday.kr/news/articleList.html?page={page}&sc_section_code=S1N2&view_type=sm', # S1N2: 投資/ピープル
        'type': 'ndsoft'
    },
    {
        'number': 12, 
        'name': 'スタルトアップトエン',
        'url_pattern': 'https://www.startupn.kr/news/articleList.html?page={page}&sc_section_code=S1N2&view_type=sm', # S1N2: 投資
        'type': 'ndsoft'
    },
    {
        'number': 13, 
        'name': 'アウトスタンディング',
        'url_pattern': 'https://outstanding.kr/category/news/page/{page}',
        'type': 'wordpress_custom' 
    },
    {
        'number': 14, 
        'name': 'ビセクセス',
        'url_pattern': 'https://besuccess.com/category/investment/page/{page}/',
        'type': 'wordpress'
    },
    {
        'number': 19, 
        'name': 'AIタイムス',
        'url_pattern': 'https://www.aitimes.com/news/articleList.html?page={page}&sc_section_code=S1N1&view_type=sm',
        'type': 'ndsoft'
    },
    {
        'number': 21, 
        'name': 'ネクストユニコン',
        'url_pattern': 'https://nextunicorn.kr/newsroom', # 動的 ローディングで ページネーション 難しい. 1ページばか試行
        'type': 'dynamic'
    },
    {
        'number': 22, 
        'name': 'ブロター',
        'url_pattern': 'https://www.bloter.net/news/articleList.html?page={page}&sc_section_code=S1N1&view_type=sm',
        'type': 'ndsoft'
    },
    {
        'number': 23, 
        'name': 'イコノミスト',
        'url_pattern': 'https://economist.co.kr/section/1000?page={page}', # ガストパターン (確認 必要)
        'type': 'generic'
    }
]

KEYWORDS = ['投資', '収入', 'ファンディング', 'シリーズ', 'VC', '収負', 'M&A', 'エクシット']
MAX_PAGES = 10 # 深く 収集

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\deep_dive_data.json'

# ================================================================
# 関数
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
        print(f"    Error fetching {url}: {e}")
        return None

def parse_date(date_str):
    if not date_str: return date.today().isoformat()
    try:
        nums = re.findall(r'\d+', date_str)
        if len(nums) >= 3:
            y, m, d = map(int, nums[:3])
            if y < 100: y += 2000
            return date(y, m, d).isoformat()
    except: pass
    return date.today().isoformat()

# ================================================================
# サイト別 パーサ
# ================================================================

def parse_wordpress(soup, site_info):
    articles = []
    # 一般的 ワードプレス 構造
    items = soup.select('article') or soup.select('.post') or soup.select('.post-item')
    
    for item in items:
        try:
            t = item.select_one('h2 a') or item.select_one('h3 a') or item.select_one('.title a') or item.select_one('a')
            if not t: continue
            
            title = t.get_text(strip=True)
            link = t.get('href')
            
            d = item.select_one('time') or item.select_one('.date')
            d_str = d.get_text(strip=True) if d else ""
            
            if contains_keyword(title):
                articles.append({
                    'title': title,
                    'url': link,
                    'date': parse_date(d_str)
                })
        except: continue
    return articles

def parse_ndsoft(soup, site_info):
    articles = []
    # 国内 ユンロンサ 公通 ソルション (ND Soft) 構造
    # .list-block .list-titles a  OR .art_list_all .tit a
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
            
            if contains_keyword(title):
                articles.append({
                    'title': title,
                    'url': link,
                    'date': parse_date(d_str)
                })
        except: continue
    return articles

def parse_generic(soup, site_info):
    # 略用
    articles = []
    links = soup.select('a')
    seen = set()
    for link in links:
        try:
            title = link.get_text(strip=True)
            href = link.get('href')
            if not href or len(title) < 10: continue
            if href in seen: continue
            
            if contains_keyword(title):
                seen.add(href)
                if not href.startswith('http'):
                    base = '/'.join(site_info['url_pattern'].split('/')[:3])
                    href = base + href
                
                articles.append({
                    'title': title,
                    'url': href,
                    'date': date.today().isoformat()
                })
        except: continue
    return articles[:15] # ページ当 最大 15個 

# ================================================================
# メイン
# ================================================================

def main():
    all_data = []
    print(f"Starting Deep Dive Scraping (Max {MAX_PAGES} pages per site)...")
    
    for site in TARGET_SITES:
        site_name = site['name']
        site_type = site.get('type', 'generic')
        print(f"\n[{site_name}] Scraping...")
        
        site_articles = []
        
        # ネクストユニコン 例外 処理
        if site_name == 'ネクストユニコン':
            print("  Skipping NextUnicorn (Dynamic Loading)")
            continue

        for page in range(1, MAX_PAGES + 1):
            url = site['url_pattern'].format(page=page)
            print(f"  Page {page}: {url} ...", end='\r')
            
            encoding = 'euc-kr' if site_type == 'ndsoft' else 'utf-8'
            # ブロター 等 は utf-8でも いける. 自動 感知 匹かな へ、 おり 例外 処理.
            if site_name == 'ブロター': encoding = 'utf-8'
            
            soup = get_soup(url, encoding)
            if not soup: continue
            
            items = []
            if site_type == 'wordpress' or site_type == 'wordpress_custom':
                items = parse_wordpress(soup, site)
            elif site_type == 'ndsoft':
                items = parse_ndsoft(soup, site)
            else:
                items = parse_generic(soup, site)
            
            if items:
                for item in items:
                    # 中変 検查 (URL 基準)
                    if not any(d['article_url'] == item['url'] for d in site_articles):
                        site_articles.append({
                            'site_number': site['number'],
                            'site_name': site_name,
                            'site_url': '/'.join(url.split('/')[:3]),
                            'article_title': item['title'],
                            'article_url': item['url'],
                            'published_date': item['date'],
                            'content_snippet': "Deep Dive Collection"
                        })
            else:
                # アイテム が 無い 場合 は ページネーション 終了と 襲取 (唤ば 1ページ は 例外)
                if page > 1:
                    print(f"  Page {page}: No items. Stopping.")
                    break
            
            time.sleep(0.5) # 過部 防止 
        
        print(f"  -> Collected {len(site_articles)} articles.")
        all_data.extend(site_articles)

    # 保存
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal collected: {len(all_data)}")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
