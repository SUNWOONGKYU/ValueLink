#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최신 Deal들의 실제 뉴스 게재일 확인
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import requests
from bs4 import BeautifulSoup
import codecs
import time

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# 최신 20개 Deal 가져오기
result = supabase.table('deals').select('id,company_name,news_date,news_url').order('number').limit(20).execute()

print("=" * 80)
print("최신 20개 Deal의 실제 뉴스 게재일 확인")
print("=" * 80 + "\n")

mismatches = []

for i, deal in enumerate(result.data, 1):
    company = deal['company_name']
    db_date = deal['news_date']
    url = deal['news_url']

    if not url:
        print(f"{i:2d}. {company:25s} - URL 없음")
        continue

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 메타 태그 확인
            actual_date = None
            date_meta = soup.find('meta', {'property': 'article:published_time'})
            if date_meta:
                date_str = date_meta.get('content', '')
                actual_date = date_str.split('T')[0] if 'T' in date_str else date_str[:10]

            # time 태그 확인
            if not actual_date:
                time_tag = soup.find('time')
                if time_tag and time_tag.get('datetime'):
                    datetime_attr = time_tag.get('datetime')
                    actual_date = datetime_attr.split('T')[0] if 'T' in datetime_attr else datetime_attr[:10]

            if actual_date:
                if actual_date == db_date:
                    print(f"{i:2d}. ✓ {company:25s} {db_date}")
                else:
                    print(f"{i:2d}. ✗ {company:25s} DB={db_date}, 실제={actual_date}")
                    mismatches.append({
                        'id': deal['id'],
                        'company': company,
                        'db_date': db_date,
                        'actual_date': actual_date
                    })
            else:
                print(f"{i:2d}. ? {company:25s} 날짜 추출 실패")

        time.sleep(0.5)
    except Exception as e:
        print(f"{i:2d}. ✗ {company:25s} 오류: {str(e)[:30]}")

print("\n" + "=" * 80)
print(f"불일치: {len(mismatches)}개")
print("=" * 80)

if mismatches:
    print("\n수정이 필요한 Deal:")
    for item in mismatches:
        print(f"  - {item['company']}: {item['db_date']} → {item['actual_date']}")
