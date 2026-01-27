#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensible Box 기업들의 실제 투자 뉴스 수집
"""

import os
import sys
import csv
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import time

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

# 뉴스 사이트 목록
NEWS_SITES = {
    'WOWTALE': 'https://www.wowtale.net',
    '벤처스퀘어': 'https://www.venturesquare.net',
    '아웃스탠딩': 'https://outstanding.kr',
    '더브이씨': 'https://thevc.kr',
    '스타트업투데이': 'https://www.startuptoday.kr'
}


def search_company_news(company_name, stage):
    """기업명으로 투자 뉴스 검색 (Google)"""

    query = f"{company_name} {stage} 투자 유치 site:wowtale.net OR site:venturesquare.net OR site:outstanding.kr OR site:thevc.kr OR site:startuptoday.kr"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        # Google 검색
        from urllib.parse import quote
        encoded_query = quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 검색 결과에서 첫 번째 링크 찾기
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/url?q=' in href and '&sa=U&' in href:
                match = re.search(r'/url\?q=([^&]+)', href)
                if match:
                    news_url = match.group(1)
                    # 뉴스 사이트인지 확인
                    for site_url in NEWS_SITES.values():
                        if site_url in news_url:
                            return news_url

        return None

    except Exception as e:
        return None


def main():
    print("=" * 70)
    print("Sensible Box 기업 투자 뉴스 수집")
    print("=" * 70)

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 기업 처리 예정\n")

    success_count = 0
    fail_count = 0

    for idx, row in enumerate(companies, 1):
        company_name = row['기업명']
        stage = row['단계']

        print(f"[{idx}/{len(companies)}] {company_name}...", end=' ')

        # 뉴스 URL 검색
        news_url = search_company_news(company_name, stage)

        if news_url:
            print(f"✅ {news_url[:60]}...")
            success_count += 1

            # Deal 테이블 업데이트
            try:
                supabase.table("deals").update({
                    "news_url": news_url
                }).eq("company_name", company_name).execute()
            except Exception as e:
                print(f"  ❌ DB 업데이트 실패: {str(e)[:50]}")

        else:
            print(f"⚠️ 못 찾음")
            fail_count += 1

        time.sleep(1)  # Google 검색 간격

        # 10개마다 좀 더 대기
        if idx % 10 == 0:
            time.sleep(3)

    print("\n" + "=" * 70)
    print("뉴스 수집 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    main()
