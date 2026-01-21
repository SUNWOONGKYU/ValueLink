# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import os

# API 키 설정
API_KEY = "9e4eb688beb65c2e908054762ac27eb39503b197"

print("=" * 80)
print("DART 자본시장법 평가보고서 검색")
print("=" * 80)

# 카카오 고유번호로 직접 검색
print("\n카카오 합병 공시 검색 중...\n")

url = "https://opendart.fss.or.kr/api/list.json"
params = {
    "crtfc_key": API_KEY,
    "corp_code": "00164779",  # 카카오
    "bgn_de": "20140501",
    "end_de": "20141031",
    "page_count": 100
}

try:
    response = requests.get(url, params=params)
    data = response.json()

    print(f"API 응답 상태: {data.get('status', 'unknown')}")
    print(f"메시지: {data.get('message', 'N/A')}")

    if data['status'] == '000' and 'list' in data:
        results = data['list']
        print(f"\n총 {len(results)}건의 공시 발견\n")

        # 합병 관련 공시만 필터링
        merger_reports = [r for r in results if '합병' in r['report_nm']]

        print(f"합병 관련 공시: {len(merger_reports)}건\n")

        for idx, item in enumerate(merger_reports, 1):
            print(f"{idx}. {item['report_nm']}")
            print(f"   접수번호: {item['rcept_no']}")
            print(f"   접수일자: {item['rcept_dt']}")
            print(f"   URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}")

            # 정보 파일 저장
            filename = f"{item['rcept_dt']}_카카오_{item['report_nm'][:30]}_INFO.txt"
            filename = filename.replace("/", "_").replace("\\", "_").replace(":", "_").replace("?", "_")

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"공시명: {item['report_nm']}\n")
                f.write(f"접수번호: {item['rcept_no']}\n")
                f.write(f"접수일자: {item['rcept_dt']}\n")
                f.write(f"회사명: 카카오\n")
                f.write(f"제출인: {item.get('flr_nm', 'N/A')}\n")
                f.write(f"URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}\n")
                f.write(f"\n수동 다운로드 방법:\n")
                f.write(f"1. 위 URL 접속\n")
                f.write(f"2. '첨부파일' 탭 클릭\n")
                f.write(f"3. '외부평가보고서' 또는 '합병계획서' PDF 다운로드\n")

            print(f"   저장: {filename}\n")

        print("=" * 80)
        print("검색 완료!")
        print("=" * 80)

    else:
        print(f"검색 실패: {data.get('message', '알 수 없는 오류')}")

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
