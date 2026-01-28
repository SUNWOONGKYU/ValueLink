#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""전체 Deal 테이블의 news_date를 실제 뉴스 URL에서 재확인 및 수정"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import codecs
import requests
from bs4 import BeautifulSoup
import time

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def extract_real_date(url):
    """뉴스 URL에서 실제 발행일 추출"""
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 날짜 추출 시도
        date_patterns = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'pubdate'}),
            ('meta', {'property': 'article:published'}),
            ('meta', {'name': 'date'}),
            ('time', {'datetime': True}),
        ]

        for tag_name, attrs in date_patterns:
            tag = soup.find(tag_name, attrs)
            if tag:
                date_str = tag.get('content') or tag.get('datetime')
                if date_str:
                    # ISO 날짜만 추출 (YYYY-MM-DD)
                    if 'T' in date_str:
                        return date_str.split('T')[0]
                    else:
                        return date_str[:10]

        return None
    except Exception as e:
        print(f"  크롤링 오류: {str(e)[:50]}")
        return None

# 전체 딜 조회
deals = supabase.table("deals").select("*").execute()

print(f"전체 딜 수: {len(deals.data)}개\n")

updated = 0
failed = 0

for deal in deals.data:
    company = deal['company_name']
    current_date = deal.get('news_date')
    url = deal.get('news_url')

    if not url:
        print(f"⚠️  {company}: URL 없음")
        continue

    print(f"{company}: ", end='')

    real_date = extract_real_date(url)

    if real_date:
        if real_date != current_date:
            print(f"수정 필요! DB={current_date} → 실제={real_date}")
            supabase.table("deals").update({'news_date': real_date}).eq("id", deal['id']).execute()
            updated += 1
        else:
            print(f"✅ 일치 ({current_date})")
    else:
        print(f"❌ 추출 실패 (현재: {current_date})")
        failed += 1

    time.sleep(0.5)  # 서버 부하 방지

print(f"\n완료!")
print(f"수정: {updated}개")
print(f"실패: {failed}개")
print(f"정상: {len(deals.data) - updated - failed}개")
