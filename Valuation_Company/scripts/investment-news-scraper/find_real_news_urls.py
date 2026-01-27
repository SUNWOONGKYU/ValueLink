#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
각 기업의 실제 투자 뉴스 URL 찾기 (Google 검색)
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from supabase import create_client, Client
import time
from urllib.parse import quote

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


def search_news_url(company_name, stage):
    """Google 검색으로 실제 뉴스 URL 찾기"""

    # 검색 쿼리
    query = f"{company_name} {stage} 투자 유치"
    encoded_query = quote(query)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        # Google 검색
        url = f"https://www.google.com/search?q={encoded_query}&tbm=nws"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 검색 결과에서 첫 번째 뉴스 링크 찾기
        # Google 뉴스 검색 결과는 <a> 태그에 있음
        links = soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            # /url?q= 형식의 링크 찾기
            if '/url?q=' in href:
                # 실제 URL 추출
                match = re.search(r'/url\?q=([^&]+)', href)
                if match:
                    real_url = match.group(1)
                    # 뉴스 사이트인지 확인
                    if any(site in real_url for site in ['wowtale.net', 'venturesquare.net', 'outstanding.kr', 'platum.kr', 'startuptoday.kr', 'thevc.kr']):
                        return real_url

        return None

    except Exception as e:
        return None


def main():
    print("=" * 70)
    print("실제 투자 뉴스 URL 찾기")
    print("=" * 70)

    # Deal 테이블에서 모든 레코드 가져오기
    result = supabase.table("deals").select("id,company_name,stage,news_url").execute()
    deals = result.data

    print(f"\n총 {len(deals)}개 레코드 처리 예정\n")

    success_count = 0
    fail_count = 0

    for idx, deal in enumerate(deals, 1):
        company_name = deal['company_name']
        stage = deal.get('stage', '')
        old_url = deal.get('news_url', '')

        # 이미 유효한 URL이면 건너뛰기
        if old_url and 'wowtale.net/2025/09/22/247395' not in old_url:
            print(f"[{idx}/{len(deals)}] {company_name}: URL 유효 (건너뛰기)")
            success_count += 1
            continue

        print(f"[{idx}/{len(deals)}] {company_name}...", end=' ')

        # 실제 뉴스 URL 검색
        new_url = search_news_url(company_name, stage)

        if new_url:
            # DB 업데이트
            try:
                supabase.table("deals").update({
                    "news_url": new_url
                }).eq("id", deal['id']).execute()

                print(f"✅ {new_url[:50]}...")
                success_count += 1
            except Exception as e:
                print(f"❌ DB 업데이트 실패")
                fail_count += 1
        else:
            print(f"⚠️ URL 못 찾음")
            fail_count += 1

        time.sleep(2)  # Google 검색 간격 (너무 빠르면 차단될 수 있음)

    print("\n" + "=" * 70)
    print("실제 뉴스 URL 찾기 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    main()
