#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DART 자본시장법 평가보고서 다운로더
OpenDART API를 사용하여 합병 관련 공시를 검색하고 다운로드합니다.

사용 방법:
1. OpenDART API 키 발급: https://opendart.fss.or.kr
2. API_KEY 변수에 키 입력
3. 스크립트 실행: python dart_downloader.py
"""

import OpenDartReader
import pandas as pd
from datetime import datetime
import os

# ========================================
# 설정
# ========================================

# OpenDART API 키 (https://opendart.fss.or.kr에서 발급)
API_KEY = 'YOUR_API_KEY_HERE'  # 여기에 발급받은 API 키를 입력하세요

# 저장 경로
SAVE_DIR = 'G:/내 드라이브/Content/기업가치평가플랫폼/교육자료/5가지평가법/샘플보고서/자본시장법평가법'

# ========================================
# 검색 대상 기업
# ========================================

SEARCH_TARGETS = [
    {
        'name': '다음커뮤니케이션',
        'start_date': '2014-05-01',
        'end_date': '2014-08-31',
        'keywords': ['합병', '주요사항'],
        'output_prefix': '03_카카오다음'
    },
    {
        'name': '하이크코리아',
        'start_date': '2023-10-01',
        'end_date': '2024-01-31',
        'keywords': ['합병', 'SPAC', 'IBKS'],
        'output_prefix': '04_하이크코리아_IBKS15'
    },
    {
        'name': 'IBKS제15호스팩',
        'start_date': '2023-10-01',
        'end_date': '2024-01-31',
        'keywords': ['합병', '하이크'],
        'output_prefix': '04_IBKS15_하이크코리아'
    }
]

# ========================================
# 함수 정의
# ========================================

def initialize_dart(api_key):
    """DART 클라이언트 초기화"""
    if api_key == 'YOUR_API_KEY_HERE':
        print("=" * 80)
        print("ERROR: API 키를 입력하세요!")
        print("=" * 80)
        print("\n1. https://opendart.fss.or.kr 접속")
        print("2. 회원가입 후 '개발가이드' > '인증키 신청'")
        print("3. 발급받은 키를 이 스크립트의 API_KEY 변수에 입력")
        print("\n" + "=" * 80)
        return None

    try:
        dart = OpenDartReader(api_key)
        print("✓ DART 클라이언트 초기화 완료")
        return dart
    except Exception as e:
        print(f"✗ DART 초기화 실패: {e}")
        return None

def search_company(dart, company_name):
    """회사 검색"""
    print(f"\n회사 검색: {company_name}")
    try:
        companies = dart.list(company_name)
        if companies is not None and len(companies) > 0:
            print(f"  ✓ {len(companies)}개 회사 발견")
            for idx, row in companies.head(3).iterrows():
                print(f"    - {row['corp_name']} (코드: {row['corp_code']})")
            return companies
        else:
            print(f"  ✗ '{company_name}' 검색 결과 없음")
            return None
    except Exception as e:
        print(f"  ✗ 검색 실패: {e}")
        return None

def search_disclosures(dart, corp_code, start_date, end_date, keywords):
    """공시 검색"""
    print(f"\n공시 검색: {start_date} ~ {end_date}")
    try:
        disclosures = dart.list_date_ex(
            start=start_date,
            end=end_date,
            corp_code=corp_code
        )

        if disclosures is None or len(disclosures) == 0:
            print(f"  ✗ 공시 없음")
            return None

        print(f"  ✓ 전체 공시: {len(disclosures)}건")

        # 키워드 필터링
        filtered = disclosures.copy()
        for keyword in keywords:
            filtered = filtered[filtered['report_nm'].str.contains(keyword, na=False)]

        print(f"  ✓ 필터 후: {len(filtered)}건 (키워드: {', '.join(keywords)})")

        if len(filtered) > 0:
            print("\n  관련 공시 목록:")
            for idx, row in filtered.iterrows():
                print(f"    [{row['rcept_dt']}] {row['report_nm']}")
                print(f"      rcpNo: {row['rcept_no']}")
                print(f"      URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}")
                print()

        return filtered

    except Exception as e:
        print(f"  ✗ 공시 검색 실패: {e}")
        return None

def save_results(results, output_file):
    """검색 결과 저장"""
    if results is None or len(results) == 0:
        return

    try:
        # CSV 저장
        csv_file = output_file.replace('.txt', '.csv')
        results.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"✓ CSV 저장: {csv_file}")

        # 텍스트 요약 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DART 공시 검색 결과\n")
            f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            for idx, row in results.iterrows():
                f.write(f"공시일자: {row['rcept_dt']}\n")
                f.write(f"보고서명: {row['report_nm']}\n")
                f.write(f"회사명: {row['corp_name']}\n")
                f.write(f"rcpNo: {row['rcept_no']}\n")
                f.write(f"URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}\n")
                f.write("-" * 80 + "\n\n")

        print(f"✓ 텍스트 저장: {output_file}")

    except Exception as e:
        print(f"✗ 저장 실패: {e}")

def main():
    """메인 함수"""
    print("\n" + "=" * 80)
    print("DART 자본시장법 평가보고서 검색기")
    print("=" * 80 + "\n")

    # DART 초기화
    dart = initialize_dart(API_KEY)
    if dart is None:
        return

    # 저장 디렉토리 확인
    if not os.path.exists(SAVE_DIR):
        print(f"\n경고: 저장 경로가 없습니다: {SAVE_DIR}")
        print("현재 디렉토리에 저장합니다.")
        save_dir = '.'
    else:
        save_dir = SAVE_DIR

    # 각 대상 검색
    for target in SEARCH_TARGETS:
        print("\n" + "=" * 80)
        print(f"검색 대상: {target['name']}")
        print("=" * 80)

        # 회사 검색
        companies = search_company(dart, target['name'])
        if companies is None or len(companies) == 0:
            continue

        # 첫 번째 결과 사용
        corp_code = companies.iloc[0]['corp_code']
        corp_name = companies.iloc[0]['corp_name']

        # 공시 검색
        disclosures = search_disclosures(
            dart,
            corp_code,
            target['start_date'],
            target['end_date'],
            target['keywords']
        )

        # 결과 저장
        if disclosures is not None and len(disclosures) > 0:
            output_file = os.path.join(
                save_dir,
                f"{target['output_prefix']}_DART검색결과.txt"
            )
            save_results(disclosures, output_file)

    print("\n" + "=" * 80)
    print("검색 완료!")
    print("=" * 80)
    print("\n다음 단계:")
    print("1. 생성된 CSV 파일에서 rcpNo 확인")
    print("2. DART에서 해당 공시 열람")
    print("3. 첨부파일에서 '외부평가보고서' 또는 '합병계약서' PDF 다운로드")
    print("\nDART URL 형식:")
    print("https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcpNo}")
    print("\n" + "=" * 80 + "\n")

# ========================================
# 실행
# ========================================

if __name__ == '__main__':
    main()
