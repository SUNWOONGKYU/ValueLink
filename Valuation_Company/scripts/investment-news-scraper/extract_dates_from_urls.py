#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 URL에서 날짜 추출하여 Deal 테이블 업데이트
"""

import os
import sys
import re
from datetime import datetime
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

def extract_date_from_url(url):
    """URL에서 날짜 추출"""
    if not url:
        return None

    # 패턴 1: /2026/01/07/ 형식
    match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"

    # 패턴 2: ?date=2026-01-07 형식
    match = re.search(r'date=(\d{4}-\d{2}-\d{2})', url)
    if match:
        return match.group(1)

    # 패턴 3: /20260107/ 형식 (8자리 날짜)
    match = re.search(r'/(\d{8})(?:/|$)', url)
    if match:
        date_str = match.group(1)
        year = date_str[:4]
        if 2020 <= int(year) <= 2027:  # 유효 연도 체크
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    # 패턴 4: 20260109000127 형식 (날짜가 숫자 앞부분)
    match = re.search(r'/(\d{8})\d+', url)
    if match:
        date_str = match.group(1)
        year = date_str[:4]
        if 2020 <= int(year) <= 2027:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    # 패턴 5: 20251226500276 형식 (8자리 날짜 + 추가 숫자)
    match = re.search(r'(\d{8})\d{4,}', url)
    if match:
        date_str = match.group(1)
        year = date_str[:4]
        if 2020 <= int(year) <= 2027:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    # 패턴 6: articleView.html?idxno=1864 같은 경우 - 현재 날짜 사용 (최후의 수단)
    # 이 경우는 날짜를 알 수 없으므로 None 반환

    return None

print("=" * 80)
print("뉴스 URL에서 날짜 추출")
print("=" * 80)

# Deal 테이블 조회
deals = supabase.table("deals").select("*").execute()

update_count = 0
no_date_urls = []

for deal in deals.data:
    url = deal.get('news_url')
    if not url:
        continue

    # URL에서 날짜 추출
    extracted_date = extract_date_from_url(url)

    if extracted_date:
        current_date = deal.get('news_date')

        # 날짜가 다르면 업데이트
        if extracted_date != current_date:
            # Deal 테이블 업데이트
            supabase.table("deals")\
                .update({'news_date': extracted_date})\
                .eq("id", deal['id'])\
                .execute()

            # 뉴스 테이블도 업데이트
            supabase.table("investment_news_articles")\
                .update({'published_date': extracted_date})\
                .eq("article_url", url)\
                .execute()

            print(f"  ✅ {deal['number']:3d}. {deal['company_name']:20s}: {current_date} → {extracted_date}")
            update_count += 1
    else:
        no_date_urls.append({
            'number': deal['number'],
            'company': deal['company_name'],
            'url': url[:70] + '...' if len(url) > 70 else url
        })

print(f"\n총 {update_count}개 뉴스 날짜 업데이트 완료")

if no_date_urls:
    print(f"\n⚠️  URL에서 날짜 추출 안 됨 ({len(no_date_urls)}개):")
    for item in no_date_urls[:10]:
        print(f"  {item['number']:3d}. {item['company']}")
        print(f"       {item['url']}")

# 최종 통계
print("\n" + "=" * 80)
print("뉴스 게재일 분포 (업데이트 후)")
print("=" * 80)

deals_updated = supabase.table("deals").select("news_date").execute()
from collections import Counter
date_counter = Counter([d['news_date'] for d in deals_updated.data if d.get('news_date')])

for date, count in sorted(date_counter.items(), reverse=True)[:15]:
    print(f"  {date}: {count}개")
