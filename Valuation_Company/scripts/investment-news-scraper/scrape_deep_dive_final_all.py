#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 통합 수집 (Final Real)
작성일: 2026-01-26
대상: 10개 사이트
기간: 2026-01-01 ~ 2026-01-26 (오늘까지 포함)
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

# 설정
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 1, 26) # 오늘까지

TARGET_SITES = [
    # 워드프레스 계열
    {'name': '벤처스퀘어', 'url_pattern': 'https://www.venturesquare.net/category/news-contents/news-trends/news/page/{}', 'type': 'wordpress'},
    {'name': '플래텀', 'url_pattern': 'https://platum.kr/category/investment/page/{}', 'type': 'wordpress'},
    {'name': '아웃스탠딩', 'url_pattern': 'https://outstanding.kr/category/news/page/{}', 'type': 'wordpress'},
    {'name': '비석세스', 'url_pattern': 'https://besuccess.com/category/investment/page/{}/', 'type': 'wordpress'},
    
    # NDSoft 계열 (국내 언론사)
    {'name': '스타트업투데이', 'url_pattern': 'https://www.startuptoday.kr/news/articleList.html?page={}&sc_section_code=S1N2&view_type=sm', 'type': 'ndsoft'},
    {'name': '스타트업엔', 'url_pattern': 'https://www.startupn.kr/news/articleList.html?page={}&sc_section_code=S1N2&view_type=sm', 'type': 'ndsoft'},
    {'name': 'AI타임스', 'url_pattern': 'https://www.aitimes.com/news/articleList.html?page={}&sc_section_code=S1N1&view_type=sm', 'type': 'ndsoft'},
    {'name': '블로터', 'url_pattern': 'https://www.bloter.net/news/articleList.html?page={}&sc_section_code=S1N1&view_type=sm', 'type': 'ndsoft'},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\deep_dive_final.json'

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

def main():
    all_articles = []
    print(f"통합 수집 시작: {START_DATE} ~ {END_DATE}")

    for site in TARGET_SITES:
        print(f"[{site['name']}] 수집 중...", end='', flush=True)
        site_cnt = 0
        
        for page in range(1, 6): # 사이트당 5페이지까지만 (충분함)
            url = site['url_pattern'].format(page)
            
            try:
                verify = False if site['type'] == 'ndsoft' else True
                resp = requests.get(url, headers=HEADERS, timeout=10, verify=verify)
                
                # 인코딩 처리
                if site['type'] == 'ndsoft':
                    resp.encoding = 'euc-kr' # NDSoft는 보통 euc-kr
                else:
                    resp.encoding = 'utf-8'

                soup = BeautifulSoup(resp.text, 'lxml')
                
                # 선택자 분기
                items = []
                if site['type'] == 'wordpress':
                    items = soup.select('article h2 a') or soup.select('.post-title a') or soup.select('h2 a')
                elif site['type'] == 'ndsoft':
                    items = soup.select('.list-titles a') or soup.select('.tit a')
                
                # 2차 시도 (범용)
                if not items:
                    items = soup.select('a')

                found_in_page = 0
                for item in items:
                    title = item.get_text(strip=True)
                    link = item.get('href')
                    
                    if not link or len(title) < 5: continue
                    
                    # 키워드 체크
                    if any(k in title for k in ['투자', '유치', '펀딩', '시리즈']):
                        # 날짜 체크 (있으면)
                        # 목록에서 날짜 추출 시도
                        parent = item.find_parent('li') or item.find_parent('div')
                        d_str = ""
                        if parent:
                            # 다양한 날짜 클래스 시도
                            d_elem = parent.select_one('time') or parent.select_one('.date') or parent.select_one('.list-dated')
                            if d_elem:
                                d_str = d_elem.get_text(strip=True) or d_elem.get('datetime')
                        
                        # 2026년 기사만 (혹은 날짜 없으면 일단 포함)
                        pub_date = parse_date(d_str)
                        is_2026 = False
                        
                        if pub_date:
                            if START_DATE <= pub_date <= END_DATE:
                                is_2026 = True
                        elif '2026' in d_str or not d_str: # 날짜 문자열에 2026 있거나, 날짜를 못 찾았으면(안전하게) 포함
                            is_2026 = True
                            
                        if is_2026:
                            if not link.startswith('http'):
                                base_domain = '/'.join(site['url_pattern'].split('/')[:3])
                                link = base_domain + link

                            # 중복 제거
                            if not any(a['url'] == link for a in all_articles):
                                all_articles.append({
                                    'site_name': site['name'],
                                    'title': title,
                                    'url': link,
                                    'date': d_str if d_str else "Unknown",
                                    'fetched_at': datetime.now().isoformat()
                                })
                                site_cnt += 1
                                found_in_page += 1
                
                if found_in_page == 0 and page > 2:
                    break # 2페이지 연속 없으면 중단
                    
            except Exception as e:
                # print(f"Error: {e}")
                continue
                
        print(f" -> {site_cnt}건")

    # 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {len(all_articles)}건 수집 완료. 저장: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
