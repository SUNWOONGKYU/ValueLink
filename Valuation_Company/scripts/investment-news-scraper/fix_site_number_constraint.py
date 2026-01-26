#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
site_number check constraint 확인 및 수정
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def check_and_fix_constraint():
    """Check constraint 확인 및 수정"""

    print("="*60)
    print("Checking site_number constraint")
    print("="*60)

    # 1. 현재 sources 테이블의 모든 source_number 확인
    sources = supabase.table('investment_news_network_sources').select('source_number, source_name').execute()

    print("\n[Current Sources]")
    for source in sources.data:
        print(f"  {source['source_number']}: {source['source_name']}")

    # 2. SQL로 constraint 수정 시도
    # Supabase REST API는 ALTER TABLE을 직접 실행할 수 없으므로,
    # SQL Editor에서 수동으로 실행해야 함

    print("\n" + "="*60)
    print("SQL to run in Supabase SQL Editor:")
    print("="*60)
    print("""
-- 기존 constraint 제거
ALTER TABLE investment_news_articles
DROP CONSTRAINT IF EXISTS investment_news_articles_site_number_check;

-- 새 constraint 추가 (1-100 범위)
ALTER TABLE investment_news_articles
ADD CONSTRAINT investment_news_articles_site_number_check
CHECK (site_number >= 1 AND site_number <= 100);
""")

if __name__ == '__main__':
    check_and_fix_constraint()
