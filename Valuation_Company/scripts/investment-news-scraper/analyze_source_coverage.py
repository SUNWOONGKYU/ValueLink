#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 소스별 커버리지 분석 및 최적 조합 도출
"""

import os
import csv
import sys
from collections import Counter

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def analyze_source_coverage():
    """뉴스 소스별 커버리지 분석"""

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    print("=" * 60)
    print("뉴스 소스 커버리지 분석")
    print("=" * 60)

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    total = len(companies)
    print(f"\n총 기업 수: {total}개\n")

    # 뉴스 소스별 집계
    source_counter = Counter()
    company_by_source = {}

    for row in companies:
        source = row.get('뉴스소스', '').strip()
        company_name = row['기업명']

        if source:
            source_counter[source] += 1

            if source not in company_by_source:
                company_by_source[source] = []
            company_by_source[source].append(company_name)

    # 소스별 통계 출력
    print("=" * 60)
    print("소스별 커버리지")
    print("=" * 60)
    print(f"{'순위':<5} {'소스명':<20} {'건수':<8} {'비율':<10} {'누적비율'}")
    print("-" * 60)

    cumulative = 0
    for idx, (source, count) in enumerate(source_counter.most_common(), 1):
        percentage = (count / total) * 100
        cumulative += percentage
        print(f"{idx:<5} {source:<20} {count:<8} {percentage:>6.2f}%   {cumulative:>6.2f}%")

    # 최적 조합 분석 (더VC 필수 포함)
    print("\n" + "=" * 60)
    print("최적 소스 조합 분석")
    print("=" * 60)

    # Top 소스들로 조합 테스트
    top_sources = [source for source, _ in source_counter.most_common(10)]

    print("\n🎯 추천 조합:")
    print("-" * 60)

    # 조합 1: Top 3 (더VC 없는 경우)
    top3 = top_sources[:3]
    coverage3 = sum(source_counter[s] for s in top3)
    print(f"\n1️⃣  Top 3 소스 ({', '.join(top3)})")
    print(f"   커버리지: {coverage3}/{total} ({coverage3/total*100:.1f}%)")

    # 조합 2: Top 5 (더VC 없는 경우)
    top5 = top_sources[:5]
    coverage5 = sum(source_counter[s] for s in top5)
    print(f"\n2️⃣  Top 5 소스 ({', '.join(top5)})")
    print(f"   커버리지: {coverage5}/{total} ({coverage5/total*100:.1f}%)")

    # 조합 3: Top 5 + 더VC (더VC가 Top 5에 없는 경우)
    thevc_count = source_counter.get('더VC', 0)
    if thevc_count > 0:
        if '더VC' in top5:
            print(f"\n3️⃣  Top 5 소스 (더VC 이미 포함)")
            print(f"   커버리지: {coverage5}/{total} ({coverage5/total*100:.1f}%)")
        else:
            top5_with_thevc = top5 + ['더VC']
            coverage5_thevc = coverage5 + thevc_count
            print(f"\n3️⃣  Top 5 + 더VC ({', '.join(top5_with_thevc)})")
            print(f"   커버리지: {coverage5_thevc}/{total} ({coverage5_thevc/total*100:.1f}%)")
    else:
        print(f"\n⚠️  더VC에서 발견된 기업 없음 (향후 수집 대상)")

    # 각 소스별 샘플 기업 (처음 5개)
    print("\n" + "=" * 60)
    print("소스별 샘플 기업")
    print("=" * 60)

    for source, count in source_counter.most_common(10):
        print(f"\n📰 {source} ({count}개):")
        for company in company_by_source[source][:5]:
            print(f"   - {company}")
        if count > 5:
            print(f"   ... 외 {count - 5}개")

    print("\n" + "=" * 60)

    # 최종 추천
    print("\n" + "=" * 60)
    print("✅ 최종 추천")
    print("=" * 60)

    if coverage3 / total >= 0.95:  # 95% 이상 커버
        print(f"\n🎯 Top 3 소스만으로 충분합니다!")
        print(f"   {', '.join(top3)}")
        print(f"   커버리지: {coverage3/total*100:.1f}%")
    elif coverage5 / total >= 0.95:  # 95% 이상 커버
        print(f"\n🎯 Top 5 소스 추천!")
        print(f"   {', '.join(top5)}")
        print(f"   커버리지: {coverage5/total*100:.1f}%")
    else:
        print(f"\n🎯 Top 5 소스 + 더VC (향후 수집) 추천!")
        if '더VC' not in top5:
            print(f"   {', '.join(top5 + ['더VC'])}")
        else:
            print(f"   {', '.join(top5)}")
        print(f"   현재 커버리지: {coverage5/total*100:.1f}%")
        print(f"   더VC 추가 시: 향후 확장 가능")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    analyze_source_coverage()
