#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 뉴스로 표시된 항목의 실제 언론사명 추출
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import requests
from bs4 import BeautifulSoup
import codecs
import time
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def extract_site_name_from_url(url):
    """URL에서 실제 언론사명 추출"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 1. og:site_name 메타 태그
            og_site = soup.find('meta', {'property': 'og:site_name'})
            if og_site and og_site.get('content'):
                return og_site.get('content').strip()

            # 2. publisher 메타 태그
            publisher = soup.find('meta', {'name': 'publisher'})
            if publisher and publisher.get('content'):
                return publisher.get('content').strip()

            # 3. author 메타 태그
            author = soup.find('meta', {'name': 'author'})
            if author and author.get('content'):
                return author.get('content').strip()

            # 4. title에서 추출 (마지막 대안)
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text
                # "기사제목 - 언론사" 패턴
                if ' - ' in title:
                    parts = title.split(' - ')
                    if len(parts) >= 2:
                        return parts[-1].strip()

            # 5. 도메인 기반 매핑
            domain = urlparse(url).netloc
            domain_map = {
                'mt.co.kr': '머니투데이',
                'joongang.co.kr': '중앙일보',
                'fashionbiz.co.kr': '패션비즈',
                'hellot.net': '헬로티',
                'socialvalue.kr': '소셜밸류',
                'news2day.co.kr': '뉴스투데이',
                'press9.kr': '프레스나인',
                'knpnews.com': '경남일보',
                '1conomynews.co.kr': '원코노미뉴스'
            }

            for key, value in domain_map.items():
                if key in domain:
                    return value

            return None

    except Exception as e:
        print(f"    오류: {str(e)[:50]}")
        return None

def fix_naver_news_sites():
    """네이버 뉴스 항목 수정"""

    # 네이버 뉴스로 표시된 Deal 가져오기
    result = supabase.table('deals').select('id,company_name,site_name,news_url').eq('site_name', '네이버 뉴스').execute()

    print(f"네이버 뉴스로 표시된 항목: {len(result.data)}개\n")
    print("=" * 80)

    updated = 0
    failed = 0

    for i, deal in enumerate(result.data, 1):
        company = deal['company_name']
        url = deal['news_url']

        print(f"{i:2d}. {company:25s} ", end='')

        if not url:
            print("❌ URL 없음")
            failed += 1
            continue

        # 실제 언론사명 추출
        real_site = extract_site_name_from_url(url)

        if real_site:
            print(f"✅ {real_site}")

            # DB 업데이트
            supabase.table('deals').update({
                'site_name': real_site
            }).eq('id', deal['id']).execute()

            updated += 1
        else:
            print("❌ 언론사 추출 실패")
            failed += 1

        time.sleep(0.5)

    print("\n" + "=" * 80)
    print(f"✅ 업데이트: {updated}개")
    print(f"❌ 실패: {failed}개")
    print("=" * 80)

# 메인
print("=" * 80)
print("네이버 뉴스 → 실제 언론사명 변환")
print("=" * 80 + "\n")

fix_naver_news_sites()

print("\n완료!")
