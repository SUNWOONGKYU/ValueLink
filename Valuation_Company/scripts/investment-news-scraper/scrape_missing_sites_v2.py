#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
누락된 4개 사이트 정밀 스크래핑 스크립트 (V2)
작성일: 2026-01-26
수정사항: URL 수정, 인코딩 처리 개선
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ================================================================
# 설정
# ================================================================

# URL 수정됨
TARGET_SITES = [
    # 더벨: 대소문자 주의 (Article.asp)
    {'number': 16, 'name': '더벨', 'url': 'https://www.thebell.co.kr/free/content/Article.asp?svccode=00'},
    # 넥스트유니콘: 여전히 어려울 수 있음
    {'number': 17, 'name': '넥스트유니콘', 'url': 'https://nextunicorn.kr/newsroom'},
    # 벤처경영신문: HTTP로 변경 (HTTPS 인증서 문제 회피 목적 포함), URL 파라미터 확인
    {'number': 20, 'name': '벤처경영신문', 'url': 'http://www.vmnews.co.kr/news/articleList.html?sc_section_code=S1N2'},
    # 다음뉴스: IT > 스타트업 섹션으로 변경 시도 (존재하지 않으면 IT 전체)
    # 다음 뉴스는 URL이 자주 바뀜. 'IT' 섹션의 최신 기사 수집 후 필터링이 안전.
    {'number': 25, 'name': '다음뉴스', 'url': 'https://news.daum.net/breakingnews/digital'}, 
]

KEYWORDS = ['투자', '투자유치', '펀딩', '시리즈', '벤처캐피털', 'VC', 'M&A', '인수', '스타트업']
START_DATE = date(2026, 1, 1)
END_DATE = date.today()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\missing_sites_data.json'

# ================================================================
# 유틸리티
# ================================================================

def contains_keyword(text: str) -> bool:
    if not text: return False
    return any(k in text for k in KEYWORDS)

def parse_date(date_str: str) -> Optional[date]:
    if not date_str: return None
    nums = re.findall(r'\d+', date_str)
    if len(nums) >= 3:
        y, m, d = map(int, nums[:3])
        if y < 100: y += 2000
        try:
            return date(y, m, d)
        except:
            return None
    return None

def is_valid_date(d: date) -> bool:
    return START_DATE <= d <= END_DATE

# ================================================================
# 사이트별 스크래퍼
# ================================================================

def scrape_thebell(site_info):
    articles = []
    url = site_info['url']
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8' # UTF-8 강제 (디버깅 결과 반영)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # 더벨 리스트 구조: <div class="listBox"> <ul> <li> ...
        # 제목: <dt> <a href="...">
        items = soup.select('.listBox li')
        
        for item in items:
            try:
                title_tag = item.select_one('dt a')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                if not link.startswith('http'):
                    link = 'https://www.thebell.co.kr/free/content/' + link
                    
                date_tag = item.select_one('.date')
                date_str = date_tag.get_text(strip=True) if date_tag else ""
                
                pub_date = parse_date(date_str)
                
                if contains_keyword(title) and pub_date and is_valid_date(pub_date):
                    articles.append({
                        'site_number': site_info['number'],
                        'site_name': site_info['name'],
                        'site_url': 'https://www.thebell.co.kr',
                        'article_title': title,
                        'article_url': link,
                        'published_date': pub_date.isoformat(),
                        'content_snippet': None
                    })
            except: continue
    except Exception as e:
        return {'error': str(e)}
    return articles

def scrape_vmnews(site_info):
    articles = []
    url = site_info['url']
    try:
        # SSL verify=False, HTTP 시도
        resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        # 인코딩 자동 감지 맡기거나 EUC-KR 시도
        # 벤처경영신문은 보통 EUC-KR 사용 가능성 높음
        if 'charset=euc-kr' in resp.text.lower() or resp.encoding == 'ISO-8859-1':
            resp.encoding = 'euc-kr'
            
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # 구조 재확인 필요하지만, 일반적인 신문사 솔루션 구조(nd-soft 등) 추정
        # .list-block .list-titles a
        items = soup.select('.list-block') or soup.select('.article-list')
        
        for item in items:
            try:
                title_tag = item.select_one('.list-titles a') or item.select_one('.tit a')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                if not link.startswith('http'):
                    link = 'http://www.vmnews.co.kr' + link # HTTP
                
                date_tag = item.select_one('.list-dated') or item.select_one('.date')
                date_str = date_tag.get_text(strip=True) if date_tag else ""
                
                pub_date = parse_date(date_str)
                
                if contains_keyword(title) and pub_date and is_valid_date(pub_date):
                    articles.append({
                        'site_number': site_info['number'],
                        'site_name': site_info['name'],
                        'site_url': 'http://www.vmnews.co.kr',
                        'article_title': title,
                        'article_url': link,
                        'published_date': pub_date.isoformat(),
                        'content_snippet': None
                    })
            except: continue
    except Exception as e:
        return {'error': str(e)}
    return articles

def scrape_daum_digital(site_info):
    articles = []
    url = site_info['url'] # IT/Digital Breaking News
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # 다음 뉴스 목록 (최신)
        # <ul class="list_newsmajor"> <li> ...
        # <strong class="tit_thumb"> <a href="...">
        items = soup.select('ul.list_newsmajor li') or soup.select('ul.list_mainnews li')
        
        for item in items:
            try:
                title_tag = item.select_one('.tit_thumb a') or item.select_one('.link_txt')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                
                # 날짜 정보가 목록에 없을 수 있음 -> 오늘 날짜로 가정 (Breaking News이므로)
                # 키워드 필터링 필수
                if contains_keyword(title):
                    articles.append({
                        'site_number': site_info['number'],
                        'site_name': site_info['name'],
                        'site_url': 'https://news.daum.net',
                        'article_title': title,
                        'article_url': link,
                        'published_date': date.today().isoformat(),
                        'content_snippet': None
                    })
            except: continue
    except Exception as e:
        return {'error': str(e)}
    return articles

# ================================================================
# 메인
# ================================================================

def main():
    results = []
    failures = []

    print("=== 정밀 스크래핑 시작 (V2) ===")

    for site in TARGET_SITES:
        print(f"Target: {site['name']} ({site['url']})")
        res = []
        
        if site['name'] == '더벨':
            res = scrape_thebell(site)
        elif site['name'] == '벤처경영신문':
            res = scrape_vmnews(site)
        elif site['name'] == '다음뉴스':
            res = scrape_daum_digital(site)
        else:
            # 넥스트유니콘 등 스킵
            failures.append({'site': site['name'], 'reason': 'Skipped (Not implemented/Difficult)'})
            continue

        if isinstance(res, dict) and 'error' in res:
            failures.append({'site': site['name'], 'reason': res['error']})
            print(f"  -> Error: {res['error']}")
        elif isinstance(res, list):
            if not res:
                failures.append({'site': site['name'], 'reason': '0 items found (Check Keywords/Date)'})
                print(f"  -> 0 items found")
            else:
                results.extend(res)
                print(f"  -> {len(res)} items collected")

    # 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(results)} items to {OUTPUT_FILE}")
    
    if failures:
        print("\n=== Failures ===")
        for f in failures:
            print(f"- {f['site']}: {f['reason']}")

if __name__ == "__main__":
    main()
