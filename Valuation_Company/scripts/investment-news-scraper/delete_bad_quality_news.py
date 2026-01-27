#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
품질 불량 뉴스 삭제
- 더VC organizations URL (기업 프로필, 뉴스 아님)
- 404 에러 URL
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


def main():
    print("=" * 60)
    print("품질 불량 뉴스 삭제")
    print("=" * 60)

    # 1. 더VC organizations URL 삭제
    print("\n[1/2] 더VC organizations URL 삭제 중...")

    result = supabase.table("investment_news_articles")\
        .select("id,article_title,article_url")\
        .eq("site_name", "더브이씨")\
        .execute()

    thevc_count = 0
    for article in result.data:
        if '/organizations/' in article['article_url']:
            supabase.table("investment_news_articles")\
                .delete()\
                .eq("id", article['id'])\
                .execute()
            thevc_count += 1
            print(f"  ✅ 삭제: {article['article_title'][:40]}...")

    print(f"\n  → 더VC organizations: {thevc_count}개 삭제")

    # 2. 404 패턴 URL 삭제
    print("\n[2/2] 404 패턴 URL 삭제 중...")

    # 스타트업투데이 404 패턴 (idxno=51937 등)
    result = supabase.table("investment_news_articles")\
        .select("id,article_title,article_url")\
        .eq("site_name", "스타트업투데이")\
        .execute()

    startup_count = 0
    for article in result.data:
        # 404 확인된 idxno
        if 'idxno=51937' in article['article_url']:
            supabase.table("investment_news_articles")\
                .delete()\
                .eq("id", article['id'])\
                .execute()
            startup_count += 1
            print(f"  ✅ 삭제: {article['article_title'][:40]}...")

    print(f"\n  → 스타트업투데이 404: {startup_count}개 삭제")

    # 플래텀 404 패턴 (archives/241345)
    result = supabase.table("investment_news_articles")\
        .select("id,article_title,article_url")\
        .eq("site_name", "플래텀")\
        .execute()

    platum_count = 0
    for article in result.data:
        # 404 확인된 archives
        if 'archives/241345' in article['article_url']:
            supabase.table("investment_news_articles")\
                .delete()\
                .eq("id", article['id'])\
                .execute()
            platum_count += 1
            print(f"  ✅ 삭제: {article['article_title'][:40]}...")

    print(f"\n  → 플래텀 404: {platum_count}개 삭제")

    # 최종 통계
    print(f"\n{'='*60}")
    print("삭제 완료")
    print(f"{'='*60}")
    total_deleted = thevc_count + startup_count + platum_count
    print(f"✅ 총 {total_deleted}개 삭제")
    print(f"  - 더VC organizations: {thevc_count}개")
    print(f"  - 스타트업투데이 404: {startup_count}개")
    print(f"  - 플래텀 404: {platum_count}개")
    print(f"{'='*60}")

    # 남은 데이터 확인
    result = supabase.table("investment_news_articles")\
        .select("id", count="exact")\
        .execute()

    print(f"\n📊 남은 뉴스: {result.count}개")


if __name__ == '__main__':
    main()
