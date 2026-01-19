# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import dart_fss as dart
import requests
import os
from datetime import datetime

# API 키 설정
API_KEY = "9e4eb688beb65c2e908054762ac27eb39503b197"
dart.set_api_key(api_key=API_KEY)

print("=" * 80)
print("DART 자본시장법 평가보고서 검색 및 다운로드")
print("=" * 80)

# 검색 대상 기업 및 기간
targets = [
    {
        "company": "다음커뮤니케이션",
        "corp_code": None,  # 자동 검색
        "start_date": "20140501",
        "end_date": "20140831",
        "keywords": ["합병", "자본시장법", "외부평가"]
    },
    {
        "company": "카카오",
        "corp_code": "00164779",  # 카카오 고유번호
        "start_date": "20140501",
        "end_date": "20141031",
        "keywords": ["합병", "다음"]
    },
    {
        "company": "하이크",
        "corp_code": None,
        "start_date": "20230901",
        "end_date": "20240131",
        "keywords": ["SPAC", "합병", "IBKS"]
    }
]

def search_and_download(target):
    """DART에서 공시 검색 및 다운로드"""
    print(f"\n{'=' * 60}")
    print(f"검색 중: {target['company']}")
    print(f"기간: {target['start_date']} ~ {target['end_date']}")
    print(f"{'=' * 60}")

    try:
        # 회사 정보 검색
        if not target['corp_code']:
            corp_list = dart.get_corp_list()
            corp = corp_list.find_by_corp_name(target['company'], exactly=False)
            if corp:
                print(f"✓ 회사 발견: {corp[0].corp_name} (코드: {corp[0].corp_code})")
                corp_code = corp[0].corp_code
            else:
                print(f"✗ 회사를 찾을 수 없음: {target['company']}")
                return
        else:
            corp_code = target['corp_code']

        # 공시 검색
        print(f"\n공시 검색 중...")

        # API 직접 호출 (opendartreader 대신)
        url = "https://opendart.fss.or.kr/api/list.json"
        params = {
            "crtfc_key": API_KEY,
            "corp_code": corp_code,
            "bgn_de": target['start_date'],
            "end_de": target['end_date'],
            "pblntf_ty": "A",  # 정기공시
            "page_count": 100
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] != '000':
            print(f"✗ API 오류: {data['message']}")
            return

        if 'list' not in data:
            print(f"✗ 검색 결과 없음")
            return

        # 결과 필터링
        results = data['list']
        print(f"✓ 총 {len(results)}건의 공시 발견")

        for item in results:
            report_name = item['report_nm']
            rcpt_no = item['rcept_no']
            rcpt_dt = item['rcept_dt']

            # 키워드 필터링
            if any(kw in report_name for kw in target['keywords']):
                print(f"\n{'-' * 60}")
                print(f"[Report] {report_name}")
                print(f"   접수번호: {rcpt_no}")
                print(f"   접수일자: {rcpt_dt}")

                # 상세 정보 조회
                detail_url = f"https://opendart.fss.or.kr/api/document.xml?crtfc_key={API_KEY}&rcept_no={rcpt_no}"
                print(f"   URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcpt_no}")

                # PDF 다운로드 시도
                try:
                    # 첨부파일 목록 조회
                    attach_url = f"https://opendart.fss.or.kr/api/document.xml?crtfc_key={API_KEY}&rcept_no={rcpt_no}"

                    filename = f"{rcpt_dt}_{target['company']}_{report_name[:20]}.html"
                    filename = filename.replace("/", "_").replace("\\", "_").replace(":", "_")

                    # HTML 버전 저장
                    html_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcpt_no}"
                    print(f"   저장: {filename}")

                    # 정보 저장
                    info_file = f"{rcpt_dt}_{target['company']}_INFO.txt"
                    with open(info_file, 'w', encoding='utf-8') as f:
                        f.write(f"공시명: {report_name}\n")
                        f.write(f"접수번호: {rcpt_no}\n")
                        f.write(f"접수일자: {rcpt_dt}\n")
                        f.write(f"회사명: {target['company']}\n")
                        f.write(f"URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcpt_no}\n")
                        f.write(f"\n수동 다운로드 방법:\n")
                        f.write(f"1. 위 URL 접속\n")
                        f.write(f"2. '첨부파일' 탭 클릭\n")
                        f.write(f"3. '외부평가보고서' 또는 '합병계획서' PDF 다운로드\n")

                    print(f"   ✓ 정보 저장: {info_file}")

                except Exception as e:
                    print(f"   ✗ 다운로드 오류: {e}")

    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

# 모든 대상 검색
print("\n🔍 DART 검색 시작...\n")

for target in targets:
    search_and_download(target)

print("\n" + "=" * 80)
print("검색 완료!")
print("=" * 80)
print("\n생성된 파일:")
for file in os.listdir("."):
    if file.endswith((".txt", ".html", ".pdf")) and "INFO" in file or "커뮤니케이션" in file or "카카오" in file or "하이크" in file:
        size = os.path.getsize(file)
        print(f"  - {file} ({size:,} bytes)")
