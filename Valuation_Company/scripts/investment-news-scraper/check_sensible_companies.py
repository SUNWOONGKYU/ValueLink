#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서블박스 CSV 확인
"""

import os
import sys
import csv

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

GEMINI_CSV = 'sensible_companies_2026_01_GEMINI.csv'

print("=" * 80)
print("센서블박스 CSV 확인")
print("=" * 80)

companies = []
with open(GEMINI_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company_name = row['기업명']
        if company_name and company_name not in ['```', '```csv']:
            companies.append(company_name)

print(f"\n📋 센서블박스 총 기업 수: {len(companies)}개")

# 문제의 두 기업 확인
print("\n❓ 문제의 두 기업 확인:")

target1 = '디앤티테크솔루션'
target2 = '엘리시전'

if target1 in companies:
    print(f"  ✅ {target1} 있음")
else:
    print(f"  ❌ {target1} 없음")

if target2 in companies:
    print(f"  ✅ {target2} 있음")
else:
    print(f"  ❌ {target2} 없음")

# 유사 이름 검색
print("\n🔍 유사 이름 검색:")

print("\n[디앤티/디엔티/DNT 검색]")
found = False
for c in companies:
    if any(keyword in c for keyword in ['DNT', 'dnt', '디앤티', '디엔티', 'D&T']):
        print(f"  - {c}")
        found = True
if not found:
    print("  (없음)")

print("\n[엘리/Elli/Elisi 검색]")
found = False
for c in companies:
    if any(keyword in c for keyword in ['엘리', 'elli', 'Elli', 'elisi', 'Elisi']):
        print(f"  - {c}")
        found = True
if not found:
    print("  (없음)")

# 전체 리스트 출력
print("\n" + "=" * 80)
print("센서블박스 전체 기업 리스트 (125개)")
print("=" * 80)
for idx, company in enumerate(sorted(companies), 1):
    print(f"{idx:3d}. {company}")
