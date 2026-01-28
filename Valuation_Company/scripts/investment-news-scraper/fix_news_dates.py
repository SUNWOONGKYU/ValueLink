#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블의 뉴스 게재 시간 수정
- investment_news_articles 테이블에서 실제 published_date 가져오기
- 투자단계 빈 것들 채우기 (센서블박스 데이터)
"""

import os
import sys
import csv
from datetime import datetime
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

print("=" * 80)
print("Deal 테이블 뉴스 게재 시간 및 투자단계 수정")
print("=" * 80)

# 1. 뉴스 게재 시간 수정
print("\n1️⃣ 뉴스 게재 시간 수정 중...")

deals = supabase.table("deals").select("*").execute()
update_count = 0

for deal in deals.data:
    if not deal.get('news_url'):
        continue

    # 뉴스 테이블에서 실제 발행일 찾기
    articles = supabase.table("investment_news_articles")\
        .select("published_date")\
        .eq("article_url", deal['news_url'])\
        .execute()

    if articles.data and articles.data[0]['published_date']:
        actual_date = articles.data[0]['published_date']
        current_date = deal.get('news_date')

        # 날짜가 다르면 업데이트
        if actual_date != current_date:
            supabase.table("deals")\
                .update({'news_date': actual_date})\
                .eq("id", deal['id'])\
                .execute()

            print(f"  ✅ {deal['number']}. {deal['company_name']}: {current_date} → {actual_date}")
            update_count += 1

print(f"\n  총 {update_count}개 뉴스 게재 시간 수정 완료")

# 2. 투자단계 빈 것들 채우기 (센서블박스 CSV)
print("\n2️⃣ 투자단계 빈 것들 채우기...")

# 센서블박스 CSV 로드
csv_path = "data/sensiblebox_companies_gemini_extracted.csv"
stage_map = {}

if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row.get('회사명', '').strip()
            stage = row.get('투자단계', '').strip()
            if company and stage and stage not in ['', '-', 'N/A']:
                stage_map[company] = stage

    print(f"  센서블박스에서 {len(stage_map)}개 회사 투자단계 로드")

# 투자단계 빈 Deal들 찾아서 업데이트
empty_stage_deals = [d for d in deals.data if not d.get('stage') or d.get('stage') in ['-', 'None']]

stage_update_count = 0
for deal in empty_stage_deals:
    company = deal['company_name']

    if company in stage_map:
        stage = stage_map[company]
        supabase.table("deals")\
            .update({'stage': stage})\
            .eq("id", deal['id'])\
            .execute()

        print(f"  ✅ {deal['number']}. {company}: stage='{stage}'")
        stage_update_count += 1
    else:
        print(f"  ⚠️  {deal['number']}. {company}: 센서블박스에 투자단계 없음")

print(f"\n  총 {stage_update_count}개 투자단계 수정 완료")

# 3. 최종 통계
print("\n" + "=" * 80)
print("최종 결과")
print("=" * 80)

# 뉴스 게재일 분포 확인
deals_updated = supabase.table("deals").select("news_date").execute()
from collections import Counter
date_counter = Counter([d['news_date'] for d in deals_updated.data if d.get('news_date')])

print(f"\n뉴스 게재일 분포 (상위 10개):")
for date, count in date_counter.most_common(10):
    print(f"  {date}: {count}개")

print(f"\n✅ 뉴스 게재 시간: {update_count}개 수정")
print(f"✅ 투자단계: {stage_update_count}개 수정")
