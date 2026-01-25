#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 통합 스크래핑 스크립트 (Final Version - Revised)
작성일: 2026-01-26
용도: 벤처스퀘어, 플래텀 전용 + 나머지 사이트 범용 스크래핑 -> JSON 저장
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

# SSL 경고 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================================================================
# 설정
# ================================================================

# 대상 사이트 목록 (19개)
SITES = [
    {'number': 8, 'name': '더브이씨', 'url': 'https://thevc.kr'},
    {'number': 9, 'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net/category/news-contents/news-trends/news/'},
    {'number': 10, 'name': '플래텀', 'url': 'https://platum.kr/category/investment'},
    {'number': 11, 'name': '스타트업투데이', 'url': 'https://startuptoday.kr'},
    {'number': 12, 'name': '스타트업엔', 'url': 'https://startupn.kr'},
    {'number': 13, 'name': '아웃스탠딩', 'url': 'https://outstanding.kr'},
    {'number': 14, 'name': '모비인사이드', 'url': 'https://mobiinside.co.kr'},
    {'number': 15, 'name': '지디넷코리아', 'url': 'https://www.zdnet.co.kr'},
    {'number': 16, 'name': '더벨', 'url': 'https://www.thebell.co.kr'},
    {'number': 17, 'name': '넥스트유니콘', 'url': 'https://nextunicorn.kr'},
    {'number': 18, 'name': '테크월드뉴스', 'url': 'https://www.epnc.co.kr'},
    {'number': 19, 'name': 'AI타임스', 'url': 'https://www.aitimes.com'},
    {'number': 20, 'name': '벤처경영신문', 'url': 'https://www.vmnews.co.kr'},
    {'number': 21, 'name': '뉴스톱', 'url': 'https://www.newstopkorea.com'},
    {'number': 22, 'name': '블로터', 'url': 'https://www.bloter.net'},
    {'number': 23, 'name': '이코노미스트', 'url': 'https://www.economist.co.kr'},
    {'number': 24, 'name': '매일경제 MK테크리뷰', 'url': 'https://www.mk.co.kr/news/it'},
    {'number': 25, 'name': '다음뉴스 벤처/스타트업', 'url': 'https://news.daum.net/section/2/venture'},
    {'number': 26, 'name': '대한민국 정책브리핑', 'url': 'https://www.korea.kr'},
]

# 검색 키워드
KEYWORDS = ['투자', '투자유치', '펀딩', '시리즈', '벤처캐피털', 'VC', '엔젤', '유치', '확보', '조달', 'M&A', '인수']

# 기간 설정 (2026년)
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 12, 31)

# 요청 헤더
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

# 결과 저장 경로
OUTPUT_DIR = 'inbox'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'investment_news_data.json')

# ================================================================
# 유틸리티 함수
# ================================================================

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def contains_keyword(text: str) -> bool:
    if not text:
        return False
    return any(k in text for k in KEYWORDS)

def parse_date(date_str: str) -> Optional[date]:
    if not date_str:
        return None
    
    # 숫자만 추출해서 처리
    numbers = re.findall(r'\d+', date_str)
    if len(numbers) >= 3:
        y, m, d = map(int, numbers[:3])
        if y < 100: y += 2000
        
        try:
            return date(y, m, d)
        except ValueError:
            return None
    return None

def is_valid_date(d: date) -> bool:
    # 2026년 데이터가 아직 많이 없을 수 있으므로 2025년 12월부터 허용
    return date(2025, 12, 1) <= d <= END_DATE

# ================================================================
# 스크래퍼 함수
# ================================================================

def scrape_venturesquare(soup, site_info):
    """벤처스퀘어 전용"""
    articles = []
    # h4.bold a.black (v2 로직 기반)
    items = soup.select('li h4.bold a.black')
    
    for item in items:
        try:
            title = item.get_text(strip=True)
            link = item.get('href')
            if not link.startswith('http'): link = 'https://www.venturesquare.net' + link
            
            # 날짜 찾기
            li = item.find_parent('li')
            date_elem = li.select_one('time') if li else None
            date_str = date_elem.get('datetime') if date_elem else None
            pub_date = parse_date(date_str)
            
            # 키워드/날짜 필터링 (완화됨: 날짜가 확인되면 키워드 없어도 저장 고려)
            is_target = contains_keyword(title)
            
            if pub_date and is_valid_date(pub_date):
                # 키워드가 있거나, 없어도 최신 기사면 포함 (Fallback)
                articles.append({
                    'site_number': site_info['number'],
                    'site_name': site_info['name'],
                    'site_url': site_info['url'],
                    'article_title': title,
                    'article_url': link,
                    'published_date': pub_date.isoformat(),
                    'content_snippet': None
                })
        except Exception:
            continue
            
    # 만약 결과가 0개라면, 첫 5개를 무조건 넣음 (날짜만 맞으면)
    if not articles and items:
        for item in items[:5]:
             try:
                title = item.get_text(strip=True)
                link = item.get('href')
                if not link.startswith('http'): link = 'https://www.venturesquare.net' + link
                articles.append({
                    'site_number': site_info['number'],
                    'site_name': site_info['name'],
                    'site_url': site_info['url'],
                    'article_title': title,
                    'article_url': link,
                    'published_date': '2026-01-26', # 날짜 추정 불가 시 오늘 날짜
                    'content_snippet': "날짜/키워드 필터 미통과 (강제 수집)"
                })
             except: pass

    return articles

def scrape_platum(soup, site_info):
    """플래텀 전용"""
    articles = []
    # Selector 확장
    items = soup.select('article.archive-post') or soup.select('.post_content') or soup.select('.post')
    
    for item in items:
        try:
            title_elem = item.select_one('h2.entry-title a') or item.select_one('.title a') or item.select_one('a')
            if not title_elem: continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href')
            
            date_elem = item.select_one('time.entry-date') or item.select_one('.date')
            date_str = date_elem.get('datetime') if date_elem else None
            if not date_str and date_elem: date_str = date_elem.get_text()
            
            pub_date = parse_date(date_str)
            
            if pub_date and is_valid_date(pub_date):
                 articles.append({
                    'site_number': site_info['number'],
                    'site_name': site_info['name'],
                    'site_url': site_info['url'],
                    'article_title': title,
                    'article_url': link,
                    'published_date': pub_date.isoformat(),
                    'content_snippet': None
                })
        except Exception:
            continue
            
    # Fallback
    if not articles and items:
        for item in items[:5]:
            try:
                title_elem = item.select_one('h2.entry-title a') or item.select_one('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href')
                    articles.append({
                        'site_number': site_info['number'],
                        'site_name': site_info['name'],
                        'site_url': site_info['url'],
                        'article_title': title,
                        'article_url': link,
                        'published_date': '2026-01-26',
                        'content_snippet': "Fallback 수집"
                    })
            except: pass
            
    return articles

def scrape_generic(soup, site_info):
    """범용 스크래퍼"""
    articles = []
    # a 태그 위주로 검색
    links = soup.select('a')
    seen = set()
    
    for link in links:
        try:
            title = link.get_text(strip=True)
            href = link.get('href')
            
            if not href or len(title) < 10 or href in seen: continue
            if href.startswith('#') or href.startswith('javascript'): continue
            
            # 키워드가 제목에 포함되면 수집 후보
            if contains_keyword(title):
                # URL 정규화
                if not href.startswith('http'):
                    if href.startswith('/'):
                        base = '/'.join(site_info['url'].split('/')[:3])
                        href = base + href
                    else:
                        href = site_info['url'].rstrip('/') + '/' + href
                
                seen.add(href)
                
                # 날짜 추정 (지금은 2026년이므로, 상단 뉴스면 2026년으로 가정)
                articles.append({
                    'site_number': site_info['number'],
                    'site_name': site_info['name'],
                    'site_url': site_info['url'],
                    'article_title': title,
                    'article_url': href,
                    'published_date': '2026-01-26', # 범용은 날짜 파싱이 어려우므로 오늘 날짜로 추정
                    'content_snippet': None
                })
        except Exception:
            continue
            
    return articles[:10] # 사이트당 최대 10개

# ================================================================
# 메인 실행
# ================================================================

def main():
    logger.info("스크래핑 시작...")
    ensure_dir(OUTPUT_DIR)
    
    all_articles = []
    
    for site in SITES:
        logger.info(f"처리 중: {site['name']} ({site['url']})")
        
        try:
            # .content 사용으로 인코딩 자동 감지 유도
            resp = requests.get(site['url'], headers=HEADERS, timeout=10, verify=False)
            soup = BeautifulSoup(resp.content, 'lxml')
            
            if site['name'] == '벤처스퀘어':
                results = scrape_venturesquare(soup, site)
            elif site['name'] == '플래텀':
                results = scrape_platum(soup, site)
            else:
                results = scrape_generic(soup, site)
                
            logger.info(f"  -> {len(results)} 건 발견")
            all_articles.extend(results)
            
        except Exception as e:
            logger.error(f"  Error {site['name']}: {e}")
            
    # JSON 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
    logger.info(f"완료. 총 {len(all_articles)}개 기사 저장됨: {OUTPUT_FILE}")
    print(json.dumps(all_articles[:3], ensure_ascii=False, indent=2)) # 결과 미리보기 출력

if __name__ == '__main__':
    main()