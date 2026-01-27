#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 URL에서 실제 발행일시 추출
"""

import os
import sys
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


def extract_news_data(url):
    """뉴스 URL에서 제목과 발행일시 추출"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 제목 추출
        title = None
        # 1. og:title meta 태그
        og_title = soup.find('meta', property='og:title')
        if og_title:
            title = og_title.get('content')
        # 2. title 태그
        elif soup.title:
            title = soup.title.get_text()
        # 3. h1 태그
        elif soup.h1:
            title = soup.h1.get_text()

        # 발행일시 추출
        published_datetime = None

        # 1. meta 태그에서 찾기 (가장 정확)
        meta_time = soup.find('meta', property='article:published_time')
        if meta_time and meta_time.get('content'):
            published_datetime = meta_time['content']

        # 2. time 태그에서 찾기
        if not published_datetime:
            time_tag = soup.find('time')
            if time_tag:
                datetime_attr = time_tag.get('datetime')
                if datetime_attr:
                    published_datetime = datetime_attr
                else:
                    # time 태그 내용에서 추출
                    time_text = time_tag.get_text()
                    if time_text:
                        published_datetime = parse_korean_datetime(time_text)

        # 3. 날짜 패턴 찾기 (한국어 형식)
        if not published_datetime:
            text = soup.get_text()

            # "2026-01-27 14:30" 형식
            pattern1 = re.search(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})', text)
            if pattern1:
                published_datetime = f"{pattern1.group(1)}-{pattern1.group(2)}-{pattern1.group(3)}T{pattern1.group(4)}:{pattern1.group(5)}:00"

            # "2026.01.27 14:30" 형식
            if not published_datetime:
                pattern2 = re.search(r'(\d{4})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})', text)
                if pattern2:
                    published_datetime = f"{pattern2.group(1)}-{pattern2.group(2)}-{pattern2.group(3)}T{pattern2.group(4)}:{pattern2.group(5)}:00"

        return title, published_datetime

    except Exception as e:
        print(f"  크롤링 실패: {str(e)[:50]}")
        return None, None


def parse_korean_datetime(text):
    """한국어 날짜/시간 파싱"""

    # "2026년 1월 27일 오후 2:30" 형식
    pattern = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*(오전|오후)?\s*(\d{1,2}):(\d{2})', text)
    if pattern:
        year = pattern.group(1)
        month = pattern.group(2).zfill(2)
        day = pattern.group(3).zfill(2)
        ampm = pattern.group(4)
        hour = int(pattern.group(5))
        minute = pattern.group(6)

        if ampm == '오후' and hour < 12:
            hour += 12
        elif ampm == '오전' and hour == 12:
            hour = 0

        return f"{year}-{month}-{day}T{hour:02d}:{minute}:00"

    return None


def main():
    print("=" * 70)
    print("뉴스 URL에서 발행일시 추출")
    print("=" * 70)

    # Deal 테이블에서 모든 레코드 가져오기
    result = supabase.table("deals").select("id,company_name,news_url").execute()
    deals = result.data

    print(f"\n총 {len(deals)}개 레코드 처리 예정\n")

    success_count = 0
    fail_count = 0

    for idx, deal in enumerate(deals, 1):
        company_name = deal['company_name']
        news_url = deal.get('news_url')

        if not news_url:
            print(f"[{idx}/{len(deals)}] {company_name}: URL 없음")
            fail_count += 1
            continue

        print(f"[{idx}/{len(deals)}] {company_name}...", end=' ')

        # 발행일시 추출
        published_datetime = extract_datetime_from_url(news_url)

        if published_datetime:
            # ISO 8601 형식으로 변환
            try:
                dt = datetime.fromisoformat(published_datetime.replace('Z', '+00:00'))
                news_date = dt.strftime('%Y-%m-%d')

                # DB 업데이트
                supabase.table("deals").update({
                    "news_date": news_date
                }).eq("id", deal['id']).execute()

                print(f"✅ {news_date}")
                success_count += 1

            except Exception as e:
                print(f"❌ 날짜 파싱 실패: {str(e)[:30]}")
                fail_count += 1
        else:
            print(f"⚠️ 날짜 추출 실패")
            fail_count += 1

        time.sleep(0.3)  # 크롤링 간격

    print("\n" + "=" * 70)
    print("발행일시 추출 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    main()
