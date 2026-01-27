#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최적 뉴스 소스 조합 추천
"""

import sys

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# 11개 미디어 사이트 목록
ALL_SOURCES = [
    {'name': '벤처스퀘어', 'coverage': 27, 'percentage': 21.4},
    {'name': '스타트업투데이', 'coverage': 3, 'percentage': 2.4},
    {'name': '더VC', 'coverage': 0, 'percentage': 0, 'note': '필수 (향후 중요)'},
    {'name': '비석세스', 'coverage': 0, 'percentage': 0},
    {'name': '아웃스탠딩', 'coverage': 0, 'percentage': 0},
    {'name': '플래텀', 'coverage': 0, 'percentage': 0},
    {'name': '블로터', 'coverage': 0, 'percentage': 0},
    {'name': '스타트업엔', 'coverage': 0, 'percentage': 0},
    {'name': 'WOWTALE', 'coverage': 96, 'percentage': 76.2},
    {'name': '넥스트유니콘', 'coverage': 0, 'percentage': 0},
    {'name': '이코노미스트', 'coverage': 0, 'percentage': 0},
]


def recommend():
    """최적 조합 추천"""

    print("=" * 70)
    print("투자 뉴스 미디어 최적 조합 추천")
    print("=" * 70)

    print("\n📊 현재 11개 미디어 목록 및 커버리지:")
    print("-" * 70)
    print(f"{'순위':<5} {'미디어명':<15} {'현재 커버':<12} {'비율':<10} {'비고'}")
    print("-" * 70)

    for idx, source in enumerate(sorted(ALL_SOURCES, key=lambda x: x['coverage'], reverse=True), 1):
        note = source.get('note', '')
        if source['coverage'] > 0:
            print(f"{idx:<5} {source['name']:<15} {source['coverage']}개      {source['percentage']:>6.1f}%   {note}")
        else:
            status = "⭐필수" if '필수' in note else "미발견"
            print(f"{idx:<5} {source['name']:<15} {status:<12} {'':<10} {note}")

    # 추천 조합
    print("\n" + "=" * 70)
    print("🎯 최종 추천: 5개 미디어 조합")
    print("=" * 70)

    recommended = [
        {'name': 'WOWTALE', 'reason': '압도적 1위 (76% 커버)', 'priority': '필수'},
        {'name': '벤처스퀘어', 'reason': '2위 (21% 커버)', 'priority': '필수'},
        {'name': '더VC', 'reason': '향후 일일 수집에서 핵심 소스', 'priority': '필수'},
        {'name': '스타트업투데이', 'reason': '3위 (2% 커버, 틈새 기업)', 'priority': '권장'},
        {'name': '아웃스탠딩', 'reason': '주요 스타트업 미디어', 'priority': '권장'},
    ]

    print("\n✅ 추천 조합:")
    print("-" * 70)
    for idx, source in enumerate(recommended, 1):
        priority_icon = "🔴" if source['priority'] == '필수' else "🟡"
        print(f"{idx}. {priority_icon} {source['name']:<15} - {source['reason']}")

    # 제외된 미디어
    excluded = ['비석세스', '플래텀', '블로터', '스타트업엔', '넥스트유니콘', '이코노미스트']

    print("\n" + "-" * 70)
    print("❌ 제외된 6개 미디어:")
    print("-" * 70)
    for source in excluded:
        print(f"   - {source}")

    # 이유 설명
    print("\n" + "=" * 70)
    print("📌 선정 근거")
    print("=" * 70)

    print("""
1️⃣  WOWTALE (필수)
   - 현재 76%의 압도적 커버리지
   - 가장 많은 투자 뉴스 보유

2️⃣  벤처스퀘어 (필수)
   - 21% 커버, WOWTALE과 상호 보완
   - 국내 대표 벤처 미디어

3️⃣  더VC (필수)
   - 사용자 지정 필수 소스
   - 향후 일일 수집에서 핵심 역할 예상
   - VC 전문 미디어로 투자 정보 풍부

4️⃣  스타트업투데이 (권장)
   - 2% 커버, 틈새 기업 발굴
   - WOWTALE, 벤처스퀘어에서 누락된 기업

5️⃣  아웃스탠딩 (권장)
   - 주요 스타트업 미디어
   - 심층 분석 기사 강점
   - 향후 추가 커버리지 기대
""")

    # 커버리지 예상
    print("=" * 70)
    print("📈 예상 효과")
    print("=" * 70)

    print("""
현재 커버리지: 100% (WOWTALE + 벤처스퀘어 + 스타트업투데이)
향후 커버리지: 100%+ (더VC, 아웃스탠딩 추가로 확장)

✅ 10개 → 5개로 축소하면서도 커버리지 유지
✅ 향후 일일 수집 시 더VC에서 추가 기업 발굴 가능
✅ 크롤링 속도 2배 향상 (10개 → 5개)
✅ 유지보수 부담 50% 감소
""")

    print("=" * 70)


if __name__ == '__main__':
    recommend()
