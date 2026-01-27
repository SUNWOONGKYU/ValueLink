#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
잘못된 뉴스 URL 찾기 (빠른 버전)
- 제목에 공지/행사 키워드 포함 URL만 찾기
"""

import os
import sys
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


def find_wrong_urls():
    """잘못된 URL 찾기"""

    print("=" * 70)
    print("잘못된 뉴스 URL 찾기")
    print("=" * 70)

    # 모든 Deal 가져오기
    result = supabase.table("deals")\
        .select("id, company_name, news_url, news_title")\
        .execute()

    deals = result.data
    print(f"\n총 레코드: {len(deals)}개\n")

    # 잘못된 키워드
    wrong_keywords = ['공지', '초대', '데모데이', '안내', '프로그램', '행사']

    wrong_urls = []

    for deal in deals:
        news_title = deal.get('news_title', '')
        news_url = deal.get('news_url', '')

        # 제목에 잘못된 키워드 포함 여부
        for keyword in wrong_keywords:
            if keyword in news_title:
                wrong_urls.append({
                    'id': deal['id'],
                    'company_name': deal['company_name'],
                    'news_title': news_title,
                    'news_url': news_url
                })
                break

    print(f"❌ 잘못된 URL: {len(wrong_urls)}개\n")

    if wrong_urls:
        print("=" * 70)
        print("잘못된 URL 목록")
        print("=" * 70)
        for idx, item in enumerate(wrong_urls[:20], 1):
            print(f"\n{idx}. {item['company_name']}")
            print(f"   제목: {item['news_title']}")
            print(f"   URL: {item['news_url'][:80]}")

        print("\n" + "=" * 70)
        print(f"총 {len(wrong_urls)}개의 잘못된 URL 발견")
        print("=" * 70)
    else:
        print("✅ 모든 URL이 정상입니다.")


if __name__ == '__main__':
    find_wrong_urls()
