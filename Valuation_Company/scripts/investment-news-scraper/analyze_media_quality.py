#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
언론사 품질 분석 - STEP 2 결과 기반
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from collections import defaultdict

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
print("언론사 품질 분석 - STEP 2 결과 기반")
print("=" * 80)

# Deal 테이블에서 선정된 최적 기사 로드
result = supabase.table("deals").select("*").execute()
deals = result.data

print(f"\n📊 분석 대상: {len(deals)}개 Deal 레코드")

# 사이트별 통계
site_stats = defaultdict(lambda: {
    'count': 0,
    'companies': [],
    'articles': []
})

for deal in deals:
    site_name = deal.get('site_name', 'Unknown')
    company_name = deal.get('company_name', '')

    site_stats[site_name]['count'] += 1
    site_stats[site_name]['companies'].append(company_name)
    site_stats[site_name]['articles'].append(deal)

# 사이트별 정렬 (선택 횟수 desc)
sorted_sites = sorted(site_stats.items(), key=lambda x: x[1]['count'], reverse=True)

print("\n" + "=" * 80)
print("사이트별 최적 기사 선정 횟수 (Top 10)")
print("=" * 80)

for idx, (site_name, stats) in enumerate(sorted_sites[:10], 1):
    count = stats['count']
    companies = stats['companies'][:5]  # 상위 5개만

    print(f"\n[{idx:2d}] {site_name:20s} - {count:3d}개 기업")
    if count <= 5:
        print(f"     기업: {', '.join(companies)}")

# 분석 결과
print("\n" + "=" * 80)
print("분석 결과")
print("=" * 80)

# 1. 커버리지 분석
print("\n1️⃣ 커버리지 (기업 수 기준)")
for idx, (site_name, stats) in enumerate(sorted_sites[:10], 1):
    percentage = (stats['count'] / len(deals)) * 100
    print(f"   {idx:2d}. {site_name:20s}: {stats['count']:3d}개 ({percentage:5.1f}%)")

# 2. 언론사 카테고리 분류
major_media = ['WOWTALE', '벤처스퀘어', '아웃스탠딩', '플래텀', '스타트업투데이']
additional_media = ['더벨', '블로터', '지디넷', '전자신문', '이코노미스트', 'AI타임스']
aggregators = ['네이버 뉴스', 'Google News']

print("\n2️⃣ 카테고리별 분포")
print(f"   📰 주요 언론사 (5개): {sum([site_stats[s]['count'] for s in major_media if s in site_stats])}개")
print(f"   📰 추가 언론사 (6개): {sum([site_stats[s]['count'] for s in additional_media if s in site_stats])}개")
print(f"   🔍 뉴스 애그리게이터: {sum([site_stats[s]['count'] for s in aggregators if s in site_stats])}개")

# 3. 상위 5개 언론사 추천
print("\n3️⃣ 상위 5개 언론사 추천 (실제 선정 횟수 기준)")

top5_recommendation = []
rank = 1

for site_name, stats in sorted_sites:
    # 뉴스 애그리게이터는 제외
    if site_name in aggregators:
        continue

    top5_recommendation.append((site_name, stats['count']))
    print(f"   {rank}. {site_name:20s}: {stats['count']:3d}개 기업 ({(stats['count']/len(deals)*100):5.1f}%)")

    rank += 1
    if rank > 5:
        break

# 4. 현재 5개 언론사와 비교
print("\n4️⃣ 기존 5개 언론사 vs 실제 성과")
current_top5 = ['WOWTALE', '벤처스퀘어', '아웃스탠딩', '플래텀', '스타트업투데이']

for site in current_top5:
    count = site_stats[site]['count'] if site in site_stats else 0
    percentage = (count / len(deals)) * 100
    print(f"   {site:20s}: {count:3d}개 ({percentage:5.1f}%)")

# 5. 최종 추천
print("\n" + "=" * 80)
print("최종 추천: Top 5 언론사")
print("=" * 80)

for idx, (site_name, count) in enumerate(top5_recommendation[:5], 1):
    percentage = (count / len(deals)) * 100
    print(f"{idx}. {site_name:20s} - {count:3d}개 기업 커버 ({percentage:5.1f}%)")

print("\n✅ 분석 완료!")
print("\n💡 참고:")
print("   - '네이버 뉴스', 'Google News'는 뉴스 애그리게이터로 제외")
print("   - 실제 선정 횟수 = 최고 품질 기사로 선택된 횟수")
print("   - 커버리지 = 해당 언론사 기사가 Deal 테이블에 포함된 기업 수")
