#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 데이터 정리 - 부적합한 기사 삭제
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# 제외 키워드
EXCLUDED_KEYWORDS = [
    'IR', 'M&A', '인수', '합병', '상장', 'IPO', '행사', '세미나',
    '채용', '인사', '임원', '대표이사', '엔젤리그', '실홀딩스',
    '일본', 'Japan', '미국', 'USA', '투자사', '캐피탈', 'VC',
    'MOU', '협약', 'TEST', '테스트'
]

# 투자 키워드
INVESTMENT_KEYWORDS = [
    '투자', '유치', '시리즈', '펀딩', 'funding', 'investment',
    'Series', 'Pre-A', '시드', 'Seed', '억원', 'rounds'
]


def clean_existing_articles():
    """기존 기사 중 부적합한 것 삭제"""

    print("="*60)
    print("Cleaning Existing Articles")
    print("="*60)

    # 기존 기사 전체 조회
    result = supabase.table('investment_news_articles').select('*').order('id').execute()

    print(f"\nTotal articles: {len(result.data)}")

    to_delete = []
    to_keep = []

    for article in result.data:
        title = article['article_title']
        article_id = article['id']

        # 제외 키워드 체크
        has_excluded = any(kw in title for kw in EXCLUDED_KEYWORDS)

        # 투자 키워드 체크
        has_investment = any(kw in title for kw in INVESTMENT_KEYWORDS)

        if has_excluded or not has_investment:
            to_delete.append(article_id)
            print(f"[DELETE] ID {article_id}: {title[:60]}")
        else:
            to_keep.append(article_id)

    print(f"\n{'='*60}")
    print(f"To Delete: {len(to_delete)}")
    print(f"To Keep: {len(to_keep)}")
    print(f"{'='*60}")

    # 삭제 확인
    if to_delete:
        print(f"\nDeleting {len(to_delete)} articles...")

        deleted = 0
        failed = 0

        for article_id in to_delete:
            try:
                supabase.table('investment_news_articles').delete().eq('id', article_id).execute()
                deleted += 1
                print(f"  [OK] Deleted ID {article_id}")
            except Exception as e:
                failed += 1
                print(f"  [ERROR] Failed to delete ID {article_id}: {str(e)[:50]}")

        print(f"\n{'='*60}")
        print(f"Deleted: {deleted}")
        print(f"Failed: {failed}")
        print(f"{'='*60}")

    # 최종 확인
    final_result = supabase.table('investment_news_articles').select('id', count='exact').execute()
    final_count = final_result.count if hasattr(final_result, 'count') else len(final_result.data)

    print(f"\nFinal article count: {final_count}")
    print("\nCleaning completed!")


if __name__ == '__main__':
    clean_existing_articles()
