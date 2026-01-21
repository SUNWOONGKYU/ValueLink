# -*- coding: utf-8 -*-
"""
새로운 회사의 DCF 평가보고서 검색
두산, 케이비 제외하고 완전히 다른 회사 찾기
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import os
import json
from datetime import datetime

# DART API 키
API_KEY = "9e4eb688beb65c2e908054762ac27eb39503b197"

# 저장 경로
SAVE_DIR = "G:/내 드라이브/Content/기업가치평가플랫폼/교육자료/5가지평가법/샘플보고서/DCF평가법/실제평가보고서"

# 더 광범위한 분기 (2023년 전체 + 2024년 전체)
QUARTERS = [
    # 2024년
    {"name": "2024Q4", "start": "20241001", "end": "20241231"},
    {"name": "2024Q3", "start": "20240701", "end": "20240930"},
    {"name": "2024Q2", "start": "20240401", "end": "20240630"},
    {"name": "2024Q1", "start": "20240101", "end": "20240331"},
    # 2023년
    {"name": "2023Q4", "start": "20231001", "end": "20231231"},
    {"name": "2023Q3", "start": "20230701", "end": "20230930"},
    {"name": "2023Q2", "start": "20230401", "end": "20230630"},
    {"name": "2023Q1", "start": "20230101", "end": "20230331"},
]

def search_merger_reports(start_date, end_date):
    """합병 관련 보고서 전체 검색 (회사명 제한 없이)"""
    url = "https://opendart.fss.or.kr/api/list.json"

    params = {
        "crtfc_key": API_KEY,
        "bgn_de": start_date,
        "end_de": end_date,
        "page_count": 100
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] != '000':
            return []

        if 'list' not in data:
            return []

        results = data['list']

        # 필터링: 합병/분할 + 외부평가 포함
        filtered = []
        for r in results:
            report_nm = r['report_nm']
            corp_name = r['corp_name']

            # 제외할 회사 (이미 찾은 것들)
            if any(exclude in corp_name for exclude in ['두산', '케이비', '키움']):
                continue

            # 합병/분할 관련만
            if '합병' in report_nm or '분할' in report_nm:
                # 외부평가 관련 키워드
                if any(kw in report_nm for kw in ['외부평가', '첨부추가', '증권신고서']):
                    filtered.append(r)

        return filtered

    except Exception as e:
        print(f"  ✗ 검색 실패: {e}")
        return []

def save_results(all_results):
    """검색 결과 저장"""
    if not all_results:
        return []

    os.makedirs(SAVE_DIR, exist_ok=True)

    # 중복 제거
    unique_results = {}
    for r in all_results:
        rcept_no = r['rcept_no']
        if rcept_no not in unique_results:
            unique_results[rcept_no] = r

    results_list = list(unique_results.values())

    # 파일명
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_신규회사_검색결과.json"
    filepath = os.path.join(SAVE_DIR, filename)

    # JSON 저장
    data = {
        "search_date": datetime.now().isoformat(),
        "total_results": len(results_list),
        "results": results_list
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ JSON 저장: {filename}")

    # TXT 저장
    txt_file = filepath.replace('.json', '.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"=" * 80 + "\n")
        f.write(f"신규 회사 DCF 평가보고서 검색 결과\n")
        f.write(f"검색일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"총 {len(results_list)}건 (중복 제거)\n")
        f.write(f"=" * 80 + "\n\n")

        for idx, item in enumerate(results_list, 1):
            f.write(f"[{idx}] {item['report_nm']}\n")
            f.write(f"    접수일자: {item['rcept_dt']}\n")
            f.write(f"    회사명: {item['corp_name']}\n")
            f.write(f"    접수번호: {item['rcept_no']}\n")
            f.write(f"    URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}\n\n")
            f.write(f"-" * 80 + "\n\n")

    print(f"✓ TXT 저장: {txt_file.split('\\\\')[-1]}")

    return results_list

def main():
    """메인 함수"""
    print("\n" + "=" * 80)
    print("신규 회사 DCF 평가보고서 검색")
    print("(두산, 케이비, 키움 제외)")
    print("=" * 80 + "\n")

    all_results = []

    # 분기별 검색
    for q_idx, quarter in enumerate(QUARTERS, 1):
        print(f"[{q_idx}/{len(QUARTERS)}] {quarter['name']} 검색 중...")

        results = search_merger_reports(quarter['start'], quarter['end'])

        if results:
            print(f"  ✓ {len(results)}건 발견")

            # 상위 3개 출력
            for idx, item in enumerate(results[:3], 1):
                print(f"    • {item['corp_name']}: {item['report_nm'][:40]}...")

            if len(results) > 3:
                print(f"    ... 외 {len(results) - 3}건")

            all_results.extend(results)
        else:
            print(f"  - 결과 없음")

    # 저장
    print("\n" + "=" * 80)

    if all_results:
        saved_results = save_results(all_results)

        print(f"\n📊 총 {len(saved_results)}건 발견 (중복 제거)\n")

        # 회사별 통계
        company_count = {}
        for r in saved_results:
            corp = r['corp_name']
            company_count[corp] = company_count.get(corp, 0) + 1

        print("회사별 발견 건수:")
        for corp, count in sorted(company_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {corp}: {count}건")

        print("\n" + "=" * 80)
    else:
        print("검색 결과 없음")
        print("=" * 80)

if __name__ == '__main__':
    main()
