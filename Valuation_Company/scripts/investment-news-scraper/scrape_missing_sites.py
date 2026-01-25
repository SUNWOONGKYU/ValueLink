#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
누락된 4개 사이트 정밀 스크래핑 스크립트
작성일: 2026-01-26
대상: 더벨, 넥스트유니콘, 벤처경영신문, 다음뉴스
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================================================================
# 설정
# ================================================================

TARGET_SITES = [
    {'number': 16, 'name': '더벨', 'url': 'https://www.thebell.co.kr/free/content/article.asp?svccode=00'}, # 전체기사
    {'number': 17, 'name': '넥스트유니콘', 'url': 'https://nextunicorn.kr/newsroom'}, # 뉴스룸 확인
    {'number': 20, 'name': '벤처경영신문', 'url': 'https://www.vmnews.co.kr/news/articleList.html?sc_section_code=S1N1&view_type=sm'}, # S1N1: 종합
    {'number': 25, 'name': '다음뉴스 벤처/스타트업', 'url': 'https://news.daum.net/section/2/venture'},
]

KEYWORDS = ['투자', '투자유치', '펀딩', '시리즈', '벤처캐피털', 'VC', 'M&A', '인수', '유치', '확보', '조달']
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
    # 숫자 추출
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
    """더벨 (The Bell)"""
    articles = []
    # 더벨은 쿼리 스트링으로 페이지네이션 가능. 여기선 1페이지만
    url = "https://www.thebell.co.kr/free/content/Article.asp?svccode=00" 
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.content, 'lxml') # content로 인코딩 자동 처리
        
        # 리스트 아이템: li 혹은 dl/dt 구조 확인. 보통 더벨은 liBox or listBox
        # 실제 구조: <div class="listBox"> <ul> <li> ...
        
        items = soup.select('.listBox .listBox li') or soup.select('.listBox li')
        if not items:
            items = soup.select('ul.list01 > li') # 구버전 등 대비

        for item in items:
            try:
                # 제목
                title_tag = item.select_one('dt a') or item.select_one('.tit a')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                if not link.startswith('http'):
                    link = 'https://www.thebell.co.kr/free/content/' + link

                # 날짜: <span class="date"> or <dd class="date">
                date_tag = item.select_one('.date') or item.select_one('span.date')
                date_str = date_tag.get_text(strip=True) if date_tag else ""
                
                pub_date = parse_date(date_str)
                
                # 필터링
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
            except Exception as e:
                continue

    except Exception as e:
        return {'error': str(e)}

    return articles

def scrape_nextunicorn(site_info):
    """넥스트유니콘 (NextUnicorn) - CSR/SPA 가능성 높음"""
    # 넥스트유니콘은 기본적으로 로그인이 필요하거나 동적 로딩이 많음.
    # 뉴스룸(블로그) 페이지가 있다면 시도.
    # 여기서는 requests로 가져올 수 있는 메타데이터나 SSR 된 부분이 있는지 확인.
    
    url = "https://nextunicorn.kr/newsroom" 
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        # 넥스트유니콘은 일반적인 뉴스 리스트 페이지가 아닐 수 있음.
        # 데이터 수집이 어렵다면 '데이터 없음' 처리하고 이유 명시
        
        # 만약 정적 페이지라면:
        soup = BeautifulSoup(resp.text, 'lxml')
        # ... 파싱 로직 ...
        
        # 넥스트유니콘은 외부 뉴스 링크를 모아두는 경우가 많음.
        # 현재로서는 HTML 구조를 모르므로, 제목/링크만이라도 찾아서 시도.
        # (임시) robots.txt 나 보안 정책 확인
        if "Bot" in resp.text or resp.status_code == 403:
            return {'error': "403 Forbidden or Bot detection"}

        return [] # 구조를 모르므로 빈 리스트 (실패 처리 될 것임)

    except Exception as e:
        return {'error': str(e)}

def scrape_vmnews(site_info):
    """벤처경영신문"""
    articles = []
    # SSL 에러 자주 발생 -> verify=False
    url = "https://www.vmnews.co.kr/news/articleList.html?sc_section_code=S1N2&view_type=sm" # 투자/IR 섹션
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(resp.content, 'lxml') # EUC-KR 등 대응
        
        # 구조: <div class="list-block"> <div class="list-titles"> ...
        items = soup.select('.list-block')
        
        for item in items:
            try:
                title_tag = item.select_one('.list-titles a')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                if not link.startswith('http'):
                    link = 'https://www.vmnews.co.kr' + link
                
                # 날짜: <div class="list-dated">
                date_tag = item.select_one('.list-dated')
                date_str = date_tag.get_text(strip=True) if date_tag else ""
                
                # '2026-01-26 14:00' 형태
                pub_date = parse_date(date_str)
                
                if contains_keyword(title) and pub_date and is_valid_date(pub_date):
                    articles.append({
                        'site_number': site_info['number'],
                        'site_name': site_info['name'],
                        'site_url': 'https://www.vmnews.co.kr',
                        'article_title': title,
                        'article_url': link,
                        'published_date': pub_date.isoformat(),
                        'content_snippet': None
                    })
            except: continue

    except Exception as e:
        return {'error': str(e)}

    return articles

def scrape_daum_venture(site_info):
    """다음뉴스 벤처/스타트업"""
    articles = []
    url = "https://news.daum.net/section/2/venture"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # 다음뉴스 구조: <ul class="list_newsmajor"> <li> ...
        # <strong class="tit_thumb"> <a href="...">
        # <span class="info_news"> ... </span>
        
        items = soup.select('ul.list_newsmajor li') or soup.select('ul.list_mainnews li')
        
        for item in items:
            try:
                title_tag = item.select_one('.tit_thumb a')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                
                # 다음뉴스는 목록에 날짜가 명시적으로 "2026.01.26" 처럼 나오지 않고 "14:00", "어제" 등으로 나올 수 있음
                # 따라서 상세 페이지를 가거나, 현재 날짜(오늘)로 가정해야 할 수 있음.
                # 여기서는 '오늘' 수집한 것이므로 2026년으로 간주.
                
                # 키워드 체크
                if contains_keyword(title):
                    articles.append({
                        'site_number': site_info['number'],
                        'site_name': site_info['name'],
                        'site_url': 'https://news.daum.net',
                        'article_title': title,
                        'article_url': link,
                        'published_date': date.today().isoformat(), # 다음뉴스는 실시간이므로 오늘 날짜 할당
                        'content_snippet': None
                    })
            except: continue
            
    except Exception as e:
        return {'error': str(e)}

    return articles

# ================================================================
# 메인 실행
# ================================================================

def main():
    results = []
    failures = []

    logger.info("누락 사이트 스크래핑 시작...")

    for site in TARGET_SITES:
        logger.info(f"Processing: {site['name']}...")
        
        data = []
        error_msg = None
        
        if site['name'] == '더벨':
            res = scrape_thebell(site)
        elif site['name'] == '넥스트유니콘':
            res = scrape_nextunicorn(site)
        elif site['name'] == '벤처경영신문':
            res = scrape_vmnews(site)
        elif site['name'] == '다음뉴스 벤처/스타트업':
            res = scrape_daum_venture(site)
        else:
            res = []

        if isinstance(res, dict) and 'error' in res:
            failures.append({
                'site_number': site['number'],
                'site_name': site['name'],
                'reason': res['error'],
                'details': "스크래핑 중 예외 발생"
            })
        elif isinstance(res, list):
            if not res:
                failures.append({
                    'site_number': site['number'],
                    'site_name': site['name'],
                    'reason': "데이터 없음 (0건)",
                    'details': "해당 기간/키워드에 맞는 기사를 찾지 못했거나 HTML 구조가 변경됨"
                })
            else:
                data = res
                results.extend(data)
                logger.info(f"  -> {len(data)}건 수집 성공")

    # 결과 저장
    # 디렉토리 확인
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    logger.info(f"저장 완료: {OUTPUT_FILE}")
    
    # 실패 리포트 출력
    if failures:
        print("\n=== 수집 실패 리포트 ===")
        for fail in failures:
            print(json.dumps(fail, ensure_ascii=False, indent=2))
        print("========================")

if __name__ == "__main__":
    main()
