#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 본문 크롤링하여 투자금액, 투자단계, 투자자 추출
"""

import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
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

def extract_from_content(html_content):
    """본문에서 투자금액, 투자단계, 투자자 추출"""

    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()

    # 1. 투자금액 추출
    amount = None
    amount_patterns = [
        r'(\d+(?:\.\d+)?)\s*조\s*원?',      # 1조원
        r'(\d+)\s*조',                        # 1조
        r'(\d+(?:\.\d+)?)\s*억\s*원?',      # 100억원
        r'(\d+)\s*억',                        # 100억
        r'\$\s*(\d+(?:\.\d+)?)\s*[Mm]',     # $10M
    ]

    for pattern in amount_patterns:
        matches = re.findall(pattern, text)
        if matches:
            value = float(matches[0])
            if '조' in pattern:
                amount = value * 10000  # 조 -> 억
            elif '$' in pattern or 'M' in pattern or 'm' in pattern:
                amount = value * 13  # M$ -> 억
            else:
                amount = value
            break

    # 2. 투자단계 추출
    stage = None
    stage_patterns = [
        ('시리즈C', ['시리즈C', 'Series C', '시리즈 C']),
        ('시리즈B', ['시리즈B', 'Series B', '시리즈 B']),
        ('시리즈A', ['시리즈A', 'Series A', '시리즈 A']),
        ('프리A', ['프리A', 'Pre-A', 'PreA', 'Pre A']),
        ('시드', ['시드', 'Seed', '시드라운드']),
        ('브릿지', ['브릿지', 'Bridge']),
    ]

    for stage_name, keywords in stage_patterns:
        for keyword in keywords:
            if keyword in text:
                stage = stage_name
                break
        if stage:
            break

    # 3. 투자자 추출 (주요 키워드)
    investors = []
    investor_keywords = [
        '벤처투자', '인베스트먼트', '파트너스', '캐피탈',
        'VC', 'Partners', 'Investment', 'Ventures'
    ]

    # 간단한 투자자 추출 (회사명 + 키워드)
    for keyword in investor_keywords:
        pattern = r'([가-힣A-Za-z]+(?:벤처투자|인베스트먼트|파트너스|캐피탈|벤처스))'
        matches = re.findall(pattern, text)
        investors.extend(matches[:5])  # 최대 5개

    investors_str = ', '.join(set(investors[:5])) if investors else None

    return amount, stage, investors_str

def crawl_news_content(url):
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        return extract_from_content(response.content)

    except Exception as e:
        return None, None, None

print("=" * 80)
print("뉴스 본문 크롤링하여 투자금액, 투자단계 추출")
print("=" * 80)

# 투자금액 없는 Deal 조회
deals = supabase.table("deals")\
    .select("*")\
    .is_("amount", "null")\
    .order("number")\
    .execute()

print(f"\n처리할 Deal: {len(deals.data)}개")

amount_updated = 0
stage_updated = 0
investors_updated = 0

for idx, deal in enumerate(deals.data, 1):
    company = deal['company_name']
    url = deal.get('news_url')

    if not url:
        continue

    print(f"\n[{idx}/{len(deals.data)}] {deal['number']:3d}. {company}")
    print(f"  URL: {url[:70]}...")

    amount, stage, investors = crawl_news_content(url)

    updates = {}

    if amount:
        updates['amount'] = round(amount, 1)
        print(f"  ✅ 금액: {round(amount, 1)}억원")
        amount_updated += 1

    if stage and (not deal.get('stage') or deal.get('stage') in ['-', 'None']):
        updates['stage'] = stage
        print(f"  ✅ 단계: {stage}")
        stage_updated += 1

    if investors and (not deal.get('investors') or deal.get('investors') == '-'):
        updates['investors'] = investors
        print(f"  ✅ 투자자: {investors[:50]}...")
        investors_updated += 1

    if not updates:
        print(f"  ⚠️  추출 실패")

    # 업데이트 실행
    if updates:
        supabase.table("deals")\
            .update(updates)\
            .eq("id", deal['id'])\
            .execute()

print("\n" + "=" * 80)
print("최종 결과")
print("=" * 80)

print(f"\n✅ 투자금액 업데이트: {amount_updated}개")
print(f"✅ 투자단계 업데이트: {stage_updated}개")
print(f"✅ 투자자 업데이트: {investors_updated}개")

# 최종 통계
deals_final = supabase.table("deals").select("*").execute()

empty_amount = len([d for d in deals_final.data if not d.get('amount') or d.get('amount') == 0])
empty_stage = len([d for d in deals_final.data if not d.get('stage') or d.get('stage') in ['-', 'None']])

print(f"\n📊 최종 통계:")
print(f"  투자금액 없음: {empty_amount}개 (이전: 73개)")
print(f"  투자단계 없음: {empty_stage}개 (이전: 3개)")
