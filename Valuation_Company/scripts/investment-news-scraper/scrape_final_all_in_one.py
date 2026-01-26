#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 최종 통합 수집기 (Final All-in-One)
작성일: 2026-01-26
목표: 10개 사이트 '저인망식' 수집 + 인코딩 완벽 대응
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

# ================================================================
# 설정
# ================================================================

# 정확한 URL 패턴 (페이지네이션 포함)
TARGET_SITES = [
    {'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net/category/news-contents/news-trends/news/page/{}', 'encoding': 'utf-8'},
    {'name': '플래텀', 'url': 'https://platum.kr/category/investment/page/{}', 'encoding': 'utf-8'},
    {'name': '아웃스탠딩', 'url': 'https://outstanding.kr/category/news/page/{}', 'encoding': 'utf-8'},
    {'name': '비석세스', 'url': 'https://besuccess.com/category/investment/page/{}/', 'encoding': 'utf-8'},
    # NDSoft 계열 (euc-kr 필수)
    {'name': '스타트업투데이', 'url': 'https://www.startuptoday.kr/news/articleList.html?page={}&sc_section_code=S1N2&view_type=sm', 'encoding': 'euc-kr'},
    {'name': '스타트업엔', 'url': 'https://www.startupn.kr/news/articleList.html?page={}&sc_section_code=S1N2&view_type=sm', 'encoding': 'euc-kr'},
    {'name': 'AI타임스', 'url': 'https://www.aitimes.com/news/articleList.html?page={}&sc_section_code=S1N1&view_type=sm', 'encoding': 'euc-kr'},
    {'name': '블로터', 'url': 'https://www.bloter.net/news/articleList.html?page={}&sc_section_code=S1N1&view_type=sm', 'encoding': 'utf-8'}, # 블로터는 utf-8일 수 있음
    {'name': '이코노미스트', 'url': 'https://economist.co.kr/section/1000?page={}', 'encoding': 'utf-8'},
]

KEYWORDS = ['투자', '유치', '펀딩', '시리즈', 'VC', '인수', 'M&A']
MAX_PAGES = 5 # 사이트당 5페이지 (충분함)
OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\final_collected_news.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# ================================================================
# 함수
# ================================================================

def parse_date_simple(text):
    """텍스트에서 날짜 패턴(2026-XX-XX) 추출"""
    if not text: return None
    # 2026.01.26 or 2026-01-26 or 2026년
    if '2026' in text:
        return '2026-01-XX' # 상세 날짜는 나중에
    return None

def main():
    all_articles = []
    print("=== 최종 통합 수집 시작 (저인망 모드) ===")

    for site in TARGET_SITES:
        print(f"\n[{site['name']}] 수집 시작...", end='', flush=True)
        site_cnt = 0
        
        for page in range(1, MAX_PAGES + 1):
            url = site['url'].format(page)
            # print(f"  Page {page}...", end='\r')
            
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
                resp.encoding = site['encoding'] # 강제 인코딩 적용
                
                soup = BeautifulSoup(resp.text, 'lxml')
                
                # 저인망 수집: 페이지 내 모든 a 태그 검사
                links = soup.select('a')
                
                # 중복 방지용
                seen_in_page = set()
                
                for link in links:
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    
                    if not href or len(title) < 5: continue
                    if href in seen_in_page: continue
                    
                    # 키워드 필터
                    is_target = any(k in title for k in KEYWORDS)
                    
                    if is_target:
                        # 날짜 체크 (링크의 부모/조부모 텍스트에서 2026 찾기)
                        # 간단하게: '2026'이 페이지 텍스트 어딘가에 있고, 이 링크가 기사 링크 같으면 수집
                        # 더 정밀하게: 링크 주위 텍스트 검색
                        parent_text = link.parent.get_text() + " " + (link.parent.parent.get_text() if link.parent.parent else "")
                        
                        # 2026년 기사인지, 혹은 날짜가 없으면(최신순이므로) 일단 포함
                        if '2026' in parent_text or '시간 전' in parent_text or '분 전' in parent_text:
                            # URL 보정
                            if not href.startswith('http'):
                                if href.startswith('/'):
                                    base = '/'.join(site['url'].split('/')[:3])
                                    href = base + href
                                else:
                                    # 상대경로 처리가 복잡하므로 일단 패스하거나 단순 결합
                                    continue 

                            # 전역 중복 체크
                            if not any(a['url'] == href for a in all_articles):
                                all_articles.append({
                                    'site_name': site['name'],
                                    'title': title,
                                    'url': href,
                                    'date_snippet': parse_date_simple(parent_text) or 'Unknown',
                                    'collected_at': datetime.now().isoformat()
                                })
                                site_cnt += 1
                                seen_in_page.add(href)
                
            except Exception as e:
                # print(f"Err: {e}")
                pass
        
        print(f" -> {site_cnt}건 확보")

    # 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"\n==========================================")
    print(f"총 {len(all_articles)}건의 기사를 수집하여 저장했습니다.")
    print(f"파일 위치: {OUTPUT_FILE}")
    print(f"==========================================")

if __name__ == "__main__":
    main()
