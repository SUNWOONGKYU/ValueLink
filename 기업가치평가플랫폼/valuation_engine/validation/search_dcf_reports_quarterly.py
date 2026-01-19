# -*- coding: utf-8 -*-
"""
DCF 평가보고서 분기별 검색 스크립트
DART API 제약(3개월 제한)을 우회하여 분기별로 검색합니다.
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

# 검색 키워드 조합 (SPAC 및 합병/분할 사례)
SEARCH_KEYWORDS = [
    "스팩",
    "기업인수목적",
    "외부평가",
]

# 분기별 검색 기간 (최근 6개 분기)
QUARTERS = [
    {"name": "2024Q3", "start": "20240701", "end": "20240930"},
    {"name": "2024Q2", "start": "20240401", "end": "20240630"},
    {"name": "2024Q1", "start": "20240101", "end": "20240331"},
    {"name": "2023Q4", "start": "20231001", "end": "20231231"},
    {"name": "2023Q3", "start": "20230701", "end": "20230930"},
    {"name": "2023Q2", "start": "20230401", "end": "20230630"},
]

def search_by_keyword(keyword, start_date, end_date):
    """키워드로 공시 검색 (회사명 없이 기간으로만)"""
    url = "https://opendart.fss.or.kr/api/list.json"

    params = {
        "crtfc_key": API_KEY,
        "bgn_de": start_date,
        "end_de": end_date,
        "page_count": 100
    }

    print(f"  키워드: {keyword}, 기간: {start_date}~{end_date}")

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] != '000':
            print(f"    ✗ API 오류: {data.get('message', 'Unknown error')}")
            return []

        if 'list' not in data:
            print(f"    ✗ 결과 없음")
            return []

        results = data['list']

        # 필터링: 보고서명 또는 회사명에 키워드 포함
        filtered = []
        for r in results:
            if keyword in r['report_nm'] or keyword in r['corp_name']:
                # 합병/분할/외부평가 관련만
                if any(kw in r['report_nm'] for kw in ['합병', '분할', '외부평가', '증권신고서']):
                    filtered.append(r)

        print(f"    ✓ 필터링 결과: {len(filtered)}건")
        return filtered

    except Exception as e:
        print(f"    ✗ 검색 실패: {e}")
        return []

def save_quarterly_results(all_results):
    """분기별 검색 결과 통합 저장"""
    if not all_results:
        return

    # 디렉토리 생성
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_분기별_검색결과.json"
    filepath = os.path.join(SAVE_DIR, filename)

    # 중복 제거 (rcept_no 기준)
    unique_results = {}
    for r in all_results:
        rcept_no = r['rcept_no']
        if rcept_no not in unique_results:
            unique_results[rcept_no] = r

    results_list = list(unique_results.values())

    # JSON 저장
    data = {
        "search_date": datetime.now().isoformat(),
        "total_results": len(results_list),
        "results": results_list
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n  ✓ JSON 저장: {filepath}")

    # 텍스트 요약도 저장
    txt_file = filepath.replace('.json', '.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"=" * 80 + "\n")
        f.write(f"DCF 평가보고서 분기별 검색 결과\n")
        f.write(f"검색일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"총 {len(results_list)}건 (중복 제거)\n")
        f.write(f"=" * 80 + "\n\n")

        for idx, item in enumerate(results_list, 1):
            f.write(f"[{idx}] {item['report_nm']}\n")
            f.write(f"    접수일자: {item['rcept_dt']}\n")
            f.write(f"    회사명: {item['corp_name']}\n")
            f.write(f"    접수번호: {item['rcept_no']}\n")
            f.write(f"    URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}\n")
            f.write(f"\n    [다운로드 방법]\n")
            f.write(f"    1. 위 URL 접속\n")
            f.write(f"    2. '첨부파일' 탭 클릭\n")
            f.write(f"    3. '외부평가의견서' PDF 다운로드\n")
            f.write(f"\n" + "-" * 80 + "\n\n")

    print(f"  ✓ TXT 저장: {txt_file}")

    return results_list

def main():
    """메인 함수"""
    print("\n" + "=" * 80)
    print("DCF 평가보고서 분기별 검색 스크립트")
    print("=" * 80 + "\n")

    print(f"API 키: {API_KEY[:20]}...")
    print(f"저장 경로: {SAVE_DIR}\n")
    print(f"검색 기간: {len(QUARTERS)}개 분기")
    print(f"검색 키워드: {', '.join(SEARCH_KEYWORDS)}\n")

    all_results = []

    # 분기별 검색
    for q_idx, quarter in enumerate(QUARTERS, 1):
        print("\n" + "=" * 80)
        print(f"[{q_idx}/{len(QUARTERS)}] {quarter['name']} ({quarter['start']}~{quarter['end']})")
        print("=" * 80)

        quarter_results = []

        for kw in SEARCH_KEYWORDS:
            results = search_by_keyword(kw, quarter['start'], quarter['end'])
            quarter_results.extend(results)

        if quarter_results:
            # 중복 제거 (분기 내)
            unique = {}
            for r in quarter_results:
                rcept_no = r['rcept_no']
                if rcept_no not in unique:
                    unique[rcept_no] = r
            quarter_results = list(unique.values())

            print(f"\n  {quarter['name']} 요약: {len(quarter_results)}건 발견")

            # 상위 3개 출력
            for idx, item in enumerate(quarter_results[:3], 1):
                print(f"    [{idx}] {item['corp_name']} - {item['report_nm'][:50]}...")

            if len(quarter_results) > 3:
                print(f"    ... 외 {len(quarter_results) - 3}건")

            all_results.extend(quarter_results)
        else:
            print(f"  {quarter['name']}: 결과 없음")

    # 전체 결과 저장
    print("\n" + "=" * 80)
    print("검색 완료!")
    print("=" * 80)

    if all_results:
        saved_results = save_quarterly_results(all_results)

        print(f"\n총 {len(saved_results)}건 발견 (중복 제거)")

        # 회사별 요약
        company_count = {}
        for r in saved_results:
            corp = r['corp_name']
            company_count[corp] = company_count.get(corp, 0) + 1

        print("\n회사별 발견 건수 (상위 10개):")
        for corp, count in sorted(company_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {corp}: {count}건")

        print("\n다음 단계:")
        print("1. 저장된 .txt 파일 확인")
        print("2. DART URL 접속하여 첨부파일 확인")
        print("3. '외부평가의견서' PDF 다운로드")
        print(f"4. 다운로드한 PDF를 {SAVE_DIR}에 저장")
        print("\n⚠ 주의: 모든 보고서가 DCF 평가를 포함하지는 않습니다.")
    else:
        print("\n검색 결과가 없습니다.")

    print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    main()
