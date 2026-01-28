#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모든 Deal의 실제 뉴스 제목과 날짜 재수집"""
import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client
import codecs
import time

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def extract_date_and_title(html_content, url):
    """HTML에서 날짜와 제목 추출"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. 날짜 추출
    date = None
    date_patterns = [
        ('meta', {'property': 'article:published_time'}),
        ('meta', {'name': 'pubdate'}),
        ('meta', {'property': 'og:published_time'}),
        ('meta', {'itemprop': 'datePublished'}),
        ('time', {'datetime': True}),
    ]
    
    for tag_name, attrs in date_patterns:
        if tag_name == 'time':
            time_tags = soup.find_all('time')
            for time_tag in time_tags:
                datetime_attr = time_tag.get('datetime')
                if datetime_attr:
                    match = re.search(r'(\d{4}-\d{2}-\d{2})', datetime_attr)
                    if match:
                        date = match.group(1)
                        break
        else:
            tag = soup.find(tag_name, attrs)
            if tag and tag.get('content'):
                match = re.search(r'(\d{4}-\d{2}-\d{2})', tag.get('content'))
                if match:
                    date = match.group(1)
                    break
        if date:
            break
    
    # 2. 제목 추출
    title = None
    title_patterns = [
        ('meta', {'property': 'og:title'}),
        ('meta', {'name': 'title'}),
        ('meta', {'property': 'twitter:title'}),
        ('title', {}),
        ('h1', {'class': re.compile('title|headline|article', re.I)}),
    ]
    
    for tag_name, attrs in title_patterns:
        if tag_name == 'title':
            tag = soup.find('title')
            if tag:
                title = tag.get_text().strip()
                # "| 사이트명" 제거
                title = re.split(r'\s*[|\-]\s*(벤처스퀘어|WOWTALE|플래텀|더벨|전자신문|동아일보|조선비즈|블로터)', title)[0].strip()
                break
        elif tag_name == 'h1':
            tag = soup.find('h1', attrs)
            if tag:
                title = tag.get_text().strip()
                break
        else:
            tag = soup.find(tag_name, attrs)
            if tag and tag.get('content'):
                title = tag.get('content').strip()
                break
    
    return date, title

def crawl_news(url):
    """뉴스 페이지 크롤링"""
    # DuckDuckGo 리다이렉트 처리
    if 'duckduckgo.com' in url:
        match = re.search(r'uddg=([^&]+)', url)
        if match:
            import urllib.parse
            url = urllib.parse.unquote(match.group(1))
    
    # URL이 //로 시작하면 https: 추가
    if url.startswith('//'):
        url = 'https:' + url
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        return extract_date_and_title(response.content, url)
    except Exception as e:
        return None, None

print("=" * 80)
print("모든 Deal의 뉴스 날짜와 제목 재수집")
print("=" * 80)

# 모든 Deal 조회
deals = supabase.table("deals").select("*").order("number").execute()

print(f"\n총 {len(deals.data)}개 Deal 처리 시작\n")

updated = 0
failed = 0

for idx, deal in enumerate(deals.data, 1):
    company = deal['company_name']
    url = deal.get('news_url')
    
    if not url:
        print(f"[{idx}/{len(deals.data)}] {company}: URL 없음 - 건너뛰기")
        continue
    
    print(f"[{idx}/{len(deals.data)}] {company} 크롤링 중...")
    
    date, title = crawl_news(url)
    
    updates = {}
    if date:
        updates['news_date'] = date
        print(f"  날짜: {date}")
    
    if title:
        updates['news_title'] = title
        print(f"  제목: {title[:50]}...")
    
    if updates:
        supabase.table("deals").update(updates).eq("id", deal['id']).execute()
        updated += 1
    else:
        print(f"  ⚠️  추출 실패")
        failed += 1
    
    time.sleep(0.5)  # 서버 부하 방지

print("\n" + "=" * 80)
print("최종 결과")
print("=" * 80)
print(f"\n✅ 업데이트: {updated}개")
print(f"❌ 실패: {failed}개")
