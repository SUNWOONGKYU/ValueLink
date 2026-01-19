# -*- coding: utf-8 -*-
"""
DCF 평가보고서 확장 검색 스크립트
DART API를 사용하여 2023-2024년 합병/분할 관련 DCF 평가보고서를 광범위하게 검색합니다.
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

# 확장 검색 대상 (2023-2024년)
SEARCH_TARGETS = [
    # === SPAC 합병 사례 (DCF 평가 필수) ===
    {
        "company": "스팩",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "기업인수목적",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "외부평가"],
        "rcpNo": None
    },

    # === 주요 대기업 계열 ===
    {
        "company": "삼성",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "LG",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "SK",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "현대",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "롯데",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "카카오",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "네이버",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "한화",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "포스코",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "CJ",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "두산",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "GS",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "신세계",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },

    # === 기타 주요 기업 ===
    {
        "company": "셀트리온",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "크래프톤",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "엔씨소프트",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "넷마블",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "쿠팡",
        "start_date": "20230101",
        "end_date": "20241231",
        "keywords": ["합병", "분할", "외부평가"],
        "rcpNo": None
    },
]

def search_disclosures(corp_name, start_date, end_date, keywords):
    """공시 검색 (회사명 기반)"""
    url = "https://opendart.fss.or.kr/api/list.json"

    params = {
        "crtfc_key": API_KEY,
        "bgn_de": start_date,
        "end_de": end_date,
        "corp_name": corp_name,
        "page_count": 100
    }

    print(f"\n공시 검색: {corp_name} ({start_date} ~ {end_date})")

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] != '000':
            print(f"  ✗ API 오류: {data.get('message', 'Unknown error')}")
            return []

        if 'list' not in data:
            print(f"  ✗ 검색 결과 없음")
            return []

        results = data['list']
        print(f"  ✓ 총 {len(results)}건 발견")

        # 키워드 필터링
        filtered = [r for r in results if any(kw in r['report_nm'] for kw in keywords)]
        print(f"  ✓ 키워드 필터 후: {len(filtered)}건")

        return filtered

    except Exception as e:
        print(f"  ✗ 검색 실패: {e}")
        return []

def save_search_results(results, target):
    """검색 결과 저장"""
    if not results:
        return

    # 디렉토리 생성
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{target['company']}_검색결과.json"
    filepath = os.path.join(SAVE_DIR, filename)

    # JSON 저장
    data = {
        "search_target": target,
        "search_date": datetime.now().isoformat(),
        "total_results": len(results),
        "results": results
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n  ✓ 저장 완료: {filepath}")

    # 텍스트 요약도 저장
    txt_file = filepath.replace('.json', '.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"=" * 80 + "\n")
        f.write(f"DCF 평가보고서 검색 결과\n")
        f.write(f"회사명: {target['company']}\n")
        f.write(f"검색일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"=" * 80 + "\n\n")

        for idx, item in enumerate(results, 1):
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

    print(f"  ✓ 텍스트 저장: {txt_file}")

def main():
    """메인 함수"""
    print("\n" + "=" * 80)
    print("DCF 평가보고서 확장 검색 스크립트 (2023-2024)")
    print("=" * 80 + "\n")

    print(f"API 키: {API_KEY[:20]}...")
    print(f"저장 경로: {SAVE_DIR}\n")
    print(f"검색 대상: {len(SEARCH_TARGETS)}개 회사/키워드\n")

    all_results = []
    summary_by_company = {}

    # 각 대상 검색
    for idx, target in enumerate(SEARCH_TARGETS, 1):
        print("\n" + "=" * 80)
        print(f"[{idx}/{len(SEARCH_TARGETS)}] 검색 대상: {target['company']}")
        print("=" * 80)

        # 공시 검색
        results = search_disclosures(
            target['company'],
            target['start_date'],
            target['end_date'],
            target['keywords']
        )

        if results:
            # 결과 출력
            print(f"\n발견된 공시:")
            for result_idx, item in enumerate(results[:5], 1):  # 상위 5개만 출력
                print(f"\n  [{result_idx}] {item['report_nm']}")
                print(f"      접수일: {item['rcept_dt']}")
                print(f"      회사: {item['corp_name']}")
                print(f"      URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}")

            if len(results) > 5:
                print(f"\n  ... 외 {len(results) - 5}건 (파일에 저장됨)")

            # 저장
            save_search_results(results, target)
            all_results.extend(results)
            summary_by_company[target['company']] = len(results)
        else:
            print(f"  ✗ 검색 결과 없음")
            summary_by_company[target['company']] = 0

    # 전체 요약
    print("\n" + "=" * 80)
    print(f"검색 완료! 총 {len(all_results)}건 발견")
    print("=" * 80)

    # 회사별 요약
    print("\n회사별 발견 건수:")
    for company, count in summary_by_company.items():
        if count > 0:
            print(f"  - {company}: {count}건")

    if all_results:
        print("\n다음 단계:")
        print("1. 저장된 .txt 파일 확인")
        print("2. DART URL 접속하여 첨부파일 확인")
        print("3. '외부평가의견서' PDF 수동 다운로드")
        print(f"4. 다운로드한 PDF를 {SAVE_DIR}에 저장")
        print("\n⚠ 주의: 모든 보고서가 DCF 평가를 포함하지는 않습니다.")
        print("   첨부파일을 확인하여 '외부평가의견서'가 있는지 확인하세요.")
    else:
        print("\n검색 결과가 없습니다.")

    print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    main()
