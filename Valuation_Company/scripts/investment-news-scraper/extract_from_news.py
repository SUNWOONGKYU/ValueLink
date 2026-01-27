#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 기사에서 투자금액 + 날짜 추출
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


def extract_amount_from_text(text):
    """텍스트에서 투자금액 추출"""

    # 패턴들
    patterns = [
        r'(\d+(?:\.\d+)?)\s*억\s*원',
        r'(\d+(?:\.\d+)?)\s*억',
        r'(\d+(?:,\d+)?)\s*억',
        r'(\d+)\s*조\s*(\d+)\s*억',
        r'(\d+)\s*조',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if '조' in pattern:
                if len(match.groups()) == 2:  # X조 Y억
                    jo = int(match.group(1))
                    eok = int(match.group(2))
                    return jo * 10000 + eok
                else:  # X조
                    return int(match.group(1)) * 10000
            else:
                amount_str = match.group(1).replace(',', '').replace('.', '')
                return int(float(match.group(1)))

    return None


def extract_date_from_html(soup, url):
    """HTML에서 날짜 추출"""

    # 메타 태그에서 추출
    meta_tags = [
        'article:published_time',
        'publishedDate',
        'datePublished',
        'pubdate',
    ]

    for tag in meta_tags:
        meta = soup.find('meta', property=tag) or soup.find('meta', attrs={'name': tag})
        if meta and meta.get('content'):
            try:
                date_str = meta.get('content')
                # ISO 형식 파싱
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime('%Y-%m-%d')
            except:
                pass

    # time 태그에서 추출
    time_tag = soup.find('time')
    if time_tag:
        datetime_attr = time_tag.get('datetime')
        if datetime_attr:
            try:
                date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                return date_obj.strftime('%Y-%m-%d')
            except:
                pass

    # URL에서 날짜 패턴 찾기 (YYYY/MM/DD 또는 YYYYMMDD)
    url_date_patterns = [
        r'/(\d{4})/(\d{2})/(\d{2})/',
        r'/(\d{8})/',
    ]

    for pattern in url_date_patterns:
        match = re.search(pattern, url)
        if match:
            if len(match.groups()) == 3:
                return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            else:
                date_str = match.group(1)
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    return None


def extract_from_news():
    """뉴스 기사에서 데이터 추출"""

    print("=" * 70)
    print("뉴스 기사에서 투자금액 + 날짜 추출")
    print("=" * 70)

    # amount가 없는 레코드 가져오기
    result = supabase.table("deals")\
        .select("id, company_name, news_url, news_title")\
        .is_("amount", "null")\
        .limit(50)\
        .execute()

    deals = result.data
    print(f"\n처리할 레코드: {len(deals)}개\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    success_count = 0
    fail_count = 0

    for idx, deal in enumerate(deals, 1):
        company_name = deal['company_name']
        news_url = deal.get('news_url')
        news_title = deal.get('news_title', '')

        print(f"[{idx}/{len(deals)}] {company_name}...", end=" ")

        if not news_url:
            print("❌ URL 없음")
            fail_count += 1
            continue

        try:
            # 뉴스 페이지 크롤링
            response = requests.get(news_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 본문 텍스트 추출
            article_text = soup.get_text()

            # 투자금액 추출 (제목에서 먼저 시도)
            amount = extract_amount_from_text(news_title)
            if not amount:
                amount = extract_amount_from_text(article_text)

            # 날짜 추출
            news_date = extract_date_from_html(soup, news_url)

            # DB 업데이트
            update_data = {}
            if amount:
                update_data['amount'] = amount
            if news_date:
                update_data['news_date'] = news_date

            if update_data:
                supabase.table("deals")\
                    .update(update_data)\
                    .eq("id", deal['id'])\
                    .execute()

                result_str = []
                if amount:
                    result_str.append(f"💰 {amount}억")
                if news_date:
                    result_str.append(f"📅 {news_date}")

                print(f"✅ {' '.join(result_str)}")
                success_count += 1
            else:
                print("⚠️ 정보 없음")
                fail_count += 1

            time.sleep(0.3)  # 크롤링 간격

        except Exception as e:
            print(f"❌ {str(e)[:30]}")
            fail_count += 1

    print("\n" + "=" * 70)
    print("추출 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    extract_from_news()
