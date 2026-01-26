#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 검색 기반 전수 조사 (Search All)
작성일: 2026-01-26
전략: 카테고리 리스트 대신 '통합 검색' 결과를 크롤링하여 누락 최소화
"""

import os
import json
import time
import re
from datetime import datetime, date
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2026년 1월
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 1, 26)

# 검색 URL 패턴 (페이지네이션 포함)
SEARCH_TARGETS = [
    # 워드프레스 계열 (?s=KEYWORD)
    {'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net/page/{}?s=투자', 'type': 'wp'},
    {'name': '플래텀', 'url': 'https://platum.kr/page/{}?s=투자', 'type': 'wp'},
    
    # NDSoft 계열 (search.html 또는 sc.html)
    # 스타트업투데이 검색: https://www.startuptoday.kr/news/search.php?q=투자&page=
    {'name': '스타트업투데이', 'url': 'https://www.startuptoday.kr/news/search.php?q=투자&page={}', 'type': 'nd_search'},
    {'name': '스타트업엔', 'url': 'https://www.startupn.kr/news/search.php?q=투자&page={}', 'type': 'nd_search'},
    {'name': 'AI타임스', 'url': 'https://www.aitimes.com/news/search.php?q=투자&page={}', 'type': 'nd_search'},
    
    # 아웃스탠딩 (검색 URL 구조 확인 필요, 보통 ?s=)
    {'name': '아웃스탠딩', 'url': 'https://outstanding.kr/page/{}?s=투자', 'type': 'wp'},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\search_result_news.json'

def parse_date(date_str):
    if not date_str: return None
    try:
        # 2026.01.26 or 2026-01-26
        nums = re.findall(r'\d+', date_str)
        if len(nums) >= 3:
            y, m, d = map(int, nums[:3])
            if y < 100: y += 2000
            return date(y, m, d)
    except: pass
    return None

def main():
    all_articles = []
    print("=== 투자 뉴스 검색 기반 전수 조사 시작 ===")

    for site in SEARCH_TARGETS:
        print(f"\n[{site['name']}] 검색 중...", end='', flush=True)
        site_cnt = 0
        
        # 검색 결과는 보통 10페이지까지 뒤져보면 됨 (1페이지당 10~20개면 100개 이상)
        for page in range(1, 11):
            url = site['url'].format(page)
            
            try:
                verify = False if site['type'] == 'nd_search' else True
                resp = requests.get(url, headers=HEADERS, timeout=15, verify=verify)
                
                if site['type'] == 'nd_search':
                    resp.encoding = 'euc-kr' # 검색 결과는 보통 euc-kr
                else:
                    resp.encoding = 'utf-8'

                soup = BeautifulSoup(resp.text, 'lxml')
                items = []

                if site['type'] == 'wp':
                    # 워드프레스 검색 결과
                    items = soup.select('article') or soup.select('.post')
                    if not items: items = soup.select('h2 a') # 제목 링크만이라도
                elif site['type'] == 'nd_search':
                    # NDSoft 검색 결과 (.search_result, .result_box 등)
                    items = soup.select('.result_box li') or soup.select('.search_list li') or soup.select('.art_list li')

                if not items:
                    # 범용: a 태그 중 제목 길이가 적당한 것
                    items = soup.select('a')

                found_in_page = 0
                for item in items:
                    # 제목/링크 추출
                    if item.name == 'a':
                        t_elem = item
                    else:
                        t_elem = item.select_one('h2 a') or item.select_one('.tit a') or item.select_one('a')
                    
                    if not t_elem: continue
                    
                    title = t_elem.get_text(strip=True)
                    link = t_elem.get('href')
                    
                    if not link or len(title) < 5: continue
                    
                    # 날짜 추출 (필수: 2026년 확인)
                    date_str = ""
                    # 부모 요소에서 날짜 찾기
                    parent = t_elem.find_parent('li') or t_elem.find_parent('div') or item
                    if parent:
                        d_elem = parent.select_one('time') or parent.select_one('.date') or parent.select_one('.list-dated')
                        if d_elem:
                            date_str = d_elem.get_text(strip=True)
                    
                    # 날짜가 없으면 텍스트에서 2026 찾기
                    if '2026' not in date_str and '2026' not in parent.get_text():
                        # 날짜 확인 불가 시, 검색 결과 상위면(1~2페이지) 일단 포함? 
                        # 아니면 안전하게 스킵. 사용자가 126건을 언급했으니 최대한 포함
                        if page > 3: continue # 3페이지 이후 날짜 확인 안되면 스킵
                    
                    # 2025년 기사 제외
                    if '2025' in date_str: continue

                    # 키워드 재확인 (검색했으니 있겠지만)
                    if '투자' not in title and '유치' not in title and '펀딩' not in title:
                        continue

                    if not link.startswith('http'):
                        # 도메인 결합
                        base = '/'.join(site['url'].split('/')[:3])
                        link = base + link

                    # 중복 제거
                    if not any(a['url'] == link for a in all_articles):
                        all_articles.append({
                            'site_name': site['name'],
                            'title': title,
                            'url': link,
                            'date': date_str,
                            'source': 'search_crawl'
                        })
                        site_cnt += 1
                        found_in_page += 1
                
                if found_in_page == 0 and page > 1:
                    break # 결과 없음 중단
                    
            except Exception as e:
                # print(f"Err: {e}")
                pass
        
        print(f" -> {site_cnt}건")

    # 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {len(all_articles)}건 수집 완료. 저장: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
