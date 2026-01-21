# -*- coding: utf-8 -*-
"""
DCF 평가보고서 검색 스크립트
DART API를 사용하여 2024년 합병/분할 관련 DCF 평가보고서를 검색합니다.
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

# 검색 대상 (2024년 우선순위 높은 사례)
SEARCH_TARGETS = [
    {
        "company": "케이비제21호스팩",
        "start_date": "20240701",
        "end_date": "20241231",
        "keywords": ["합병", "외부평가"],
        "rcpNo": "20240729000685"  # 알고 있는 경우
    },
    {
        "company": "오건에코텍",
        "start_date": "20240801",
        "end_date": "20240930",
        "keywords": ["영업양도", "외부평가", "DCF"],
        "rcpNo": None
    },
    {
        "company": "두산에너빌리티",
        "start_date": "20240701",
        "end_date": "20240930",
        "keywords": ["분할", "합병", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "두산로보틱스",
        "start_date": "20240701",
        "end_date": "20240930",
        "keywords": ["합병", "외부평가"],
        "rcpNo": None
    },
    {
        "company": "키움제8호스팩",
        "start_date": "20240801",
        "end_date": "20241231",
        "keywords": ["합병", "외부평가"],
        "rcpNo": None
    },
]

def search_company_list(query):
    """회사명으로 회사 코드 검색"""
    url = "https://opendart.fss.or.kr/api/corpCode.xml"
    params = {"crtfc_key": API_KEY}

    print(f"  회사 검색: {query}")

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"  ✗ API 요청 실패: {response.status_code}")
            return None

        # XML 파싱은 복잡하므로 간단한 검색으로 대체
        # 실제로는 XML 파싱 필요
        print(f"  ⚠ 회사 코드 검색은 XML 파싱이 필요합니다.")
        print(f"  💡 대안: rcpNo로 직접 검색하거나 DART 웹사이트에서 수동 확인")
        return None

    except Exception as e:
        print(f"  ✗ 오류: {e}")
        return None

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

def get_document_info(rcpNo):
    """접수번호로 문서 정보 조회"""
    print(f"\n문서 정보 조회: {rcpNo}")

    # DART 문서 URL
    url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcpNo}"

    info = {
        "rcpNo": rcpNo,
        "url": url,
        "download_guide": [
            "1. 위 URL 접속",
            "2. '첨부파일' 탭 클릭",
            "3. '외부평가기관평가의견서' 또는 '외부평가보고서' PDF 다운로드"
        ]
    }

    print(f"  ✓ URL: {url}")

    return info

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
    print("DCF 평가보고서 검색 스크립트")
    print("=" * 80 + "\n")

    print(f"API 키: {API_KEY[:20]}...")
    print(f"저장 경로: {SAVE_DIR}\n")

    all_results = []

    # 각 대상 검색
    for target in SEARCH_TARGETS:
        print("\n" + "=" * 80)
        print(f"검색 대상: {target['company']}")
        print("=" * 80)

        # 알려진 rcpNo가 있으면 직접 조회
        if target.get('rcpNo'):
            print(f"알려진 접수번호 사용: {target['rcpNo']}")
            info = get_document_info(target['rcpNo'])

            results = [{
                "corp_name": target['company'],
                "report_nm": "알려진 공시",
                "rcept_dt": "미확인",
                "rcept_no": target['rcpNo'],
                "url": info['url']
            }]
        else:
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
            for idx, item in enumerate(results, 1):
                print(f"\n  [{idx}] {item['report_nm']}")
                print(f"      접수일: {item['rcept_dt']}")
                print(f"      URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}")

            # 저장
            save_search_results(results, target)
            all_results.extend(results)
        else:
            print(f"  ✗ 검색 결과 없음")

    # 전체 요약
    print("\n" + "=" * 80)
    print(f"검색 완료! 총 {len(all_results)}건 발견")
    print("=" * 80)

    if all_results:
        print("\n다음 단계:")
        print("1. 저장된 .txt 파일 확인")
        print("2. DART URL 접속하여 첨부파일 확인")
        print("3. '외부평가의견서' PDF 수동 다운로드")
        print(f"4. 다운로드한 PDF를 {SAVE_DIR}에 저장")
    else:
        print("\n검색 결과가 없습니다.")
        print("다음을 확인해주세요:")
        print("- 회사명이 정확한지")
        print("- 검색 기간이 적절한지")
        print("- DART 웹사이트에서 수동 검색 시도")

    print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    main()
