#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 뉴스 페이지 크롤링해서 날짜 추출
"""

import os
import sys
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

def extract_date_from_html(html_content, url):
    """HTML에서 날짜 추출"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. 메타 태그에서 찾기
    meta_patterns = [
        ('meta', {'property': 'article:published_time'}),
        ('meta', {'name': 'pubdate'}),
        ('meta', {'name': 'published_time'}),
        ('meta', {'property': 'og:published_time'}),
        ('meta', {'name': 'date'}),
        ('meta', {'itemprop': 'datePublished'}),
    ]

    for tag_name, attrs in meta_patterns:
        tag = soup.find(tag_name, attrs)
        if tag and tag.get('content'):
            content = tag.get('content')
            # ISO 8601 형식 (2026-01-15T12:00:00)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
            if date_match:
                return date_match.group(1), f"메타 태그 ({attrs})"

    # 2. time 태그에서 찾기
    time_tags = soup.find_all('time')
    for time_tag in time_tags:
        datetime_attr = time_tag.get('datetime')
        if datetime_attr:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', datetime_attr)
            if date_match:
                return date_match.group(1), "time 태그 datetime"

        text = time_tag.get_text()
        date_match = re.search(r'(\d{4})[.-](\d{2})[.-](\d{2})', text)
        if date_match:
            return f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}", "time 태그 텍스트"

    # 3. class/id가 'date', 'time', 'published' 포함하는 요소
    date_elements = soup.find_all(class_=re.compile(r'(date|time|publish|byline)', re.I))
    date_elements += soup.find_all(id=re.compile(r'(date|time|publish)', re.I))

    for elem in date_elements:
        text = elem.get_text()
        # YYYY-MM-DD, YYYY.MM.DD, YYYY/MM/DD
        date_match = re.search(r'(\d{4})[.-/](\d{2})[.-/](\d{2})', text)
        if date_match:
            return f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}", f"요소 class/id ({elem.get('class')})"

        # 2026년 1월 15일
        date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', text)
        if date_match:
            year = date_match.group(1)
            month = date_match.group(2).zfill(2)
            day = date_match.group(3).zfill(2)
            return f"{year}-{month}-{day}", "한글 날짜 형식"

    # 4. 본문에서 날짜 패턴 찾기 (최후의 수단)
    text = soup.get_text()

    # YYYY-MM-DD 패턴
    date_matches = re.findall(r'(202[0-9]-\d{2}-\d{2})', text)
    if date_matches:
        # 가장 최근 날짜 (2020~2029)
        valid_dates = [d for d in date_matches if 2020 <= int(d[:4]) <= 2029]
        if valid_dates:
            return valid_dates[0], "본문 텍스트"

    return None, "날짜 없음"

def crawl_and_extract_date(url):
    """URL 크롤링하여 날짜 추출"""

    # DuckDuckGo 리다이렉트 처리
    if 'duckduckgo.com' in url:
        # uddg 파라미터에서 실제 URL 추출
        match = re.search(r'uddg=([^&]+)', url)
        if match:
            import urllib.parse
            url = urllib.parse.unquote(match.group(1))
            print(f"    리다이렉트: {url[:70]}...")

    # URL이 //로 시작하면 https: 추가
    if url.startswith('//'):
        url = 'https:' + url

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()

        # 인코딩 설정
        response.encoding = response.apparent_encoding

        date, source = extract_date_from_html(response.content, url)
        return date, source

    except Exception as e:
        return None, f"크롤링 실패: {str(e)[:50]}"

print("=" * 80)
print("뉴스 페이지 크롤링하여 날짜 추출")
print("=" * 80)

# 2026-01-28 뉴스 조회
deals = supabase.table("deals")\
    .select("*")\
    .eq("news_date", "2026-01-28")\
    .execute()

print(f"\n처리할 Deal: {len(deals.data)}개\n")

update_count = 0

for idx, deal in enumerate(deals.data, 1):
    company = deal['company_name']
    url = deal.get('news_url', '')

    print(f"[{idx}/{len(deals.data)}] {company}")
    print(f"  URL: {url[:70]}...")

    date, source = crawl_and_extract_date(url)

    if date:
        print(f"  ✅ {date} (출처: {source})")

        # 업데이트
        supabase.table("deals")\
            .update({'news_date': date})\
            .eq("id", deal['id'])\
            .execute()

        supabase.table("investment_news_articles")\
            .update({'published_date': date})\
            .eq("article_url", deal['news_url'])\
            .execute()

        update_count += 1
    else:
        print(f"  ⚠️  {source}")

print("\n" + "=" * 80)
print(f"✅ {update_count}/{len(deals.data)}개 수정 완료")
print("=" * 80)

# 최종 통계
deals_updated = supabase.table("deals").select("news_date").execute()
from collections import Counter
date_counter = Counter([d['news_date'] for d in deals_updated.data if d.get('news_date')])

print(f"\n📊 뉴스 게재일 분포 (상위 15개):")
for date, count in sorted(date_counter.items(), reverse=True)[:15]:
    print(f"  {date}: {count}개")

print(f"\n2026-01-28 남은 개수: {date_counter.get('2026-01-28', 0)}개")
