# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

# API 키 설정
API_KEY = "9e4eb688beb65c2e908054762ac27eb39503b197"

print("=" * 80)
print("DART 최근 SPAC 합병 공시 검색 (2024년)")
print("=" * 80)

# 2024년 전체 SPAC 합병 검색
url = "https://opendart.fss.or.kr/api/list.json"
params = {
    "crtfc_key": API_KEY,
    "bgn_de": "20240101",
    "end_de": "20241231",
    "page_count": 100,
    "pblntf_detail_ty": "F001"  # 주요사항보고서
}

print("\n2024년 주요사항보고서 검색 중...\n")

try:
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == '000' and 'list' in data:
        results = data['list']
        print(f"총 {len(results)}건의 공시 발견\n")

        # SPAC 또는 합병 관련 필터링
        target_keywords = ['SPAC', '스팩', '합병', '자본시장법', '외부평가']
        filtered = []

        for item in results:
            report_name = item['report_nm']
            corp_name = item['corp_name']

            if any(kw in report_name or kw in corp_name for kw in target_keywords):
                filtered.append(item)

        print(f"SPAC/합병 관련 공시: {len(filtered)}건\n")

        # 상위 30건만 출력
        for idx, item in enumerate(filtered[:30], 1):
            print(f"{idx}. [{item['corp_name']}] {item['report_nm']}")
            print(f"   접수번호: {item['rcept_no']}")
            print(f"   접수일자: {item['rcept_dt']}")
            print(f"   URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}")

            # 정보 저장
            if '합병' in item['report_nm'] and ('SPAC' in item['corp_name'] or '스팩' in item['corp_name'] or 'IBKS' in item['corp_name'] or 'NH' in item['corp_name']):
                filename = f"{item['rcept_dt']}_{item['corp_name'][:15]}_합병_INFO.txt"
                filename = filename.replace("/", "_").replace("\\", "_").replace(":", "_").replace("?", "_").replace(")", "_").replace("(", "_")

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"공시명: {item['report_nm']}\n")
                    f.write(f"접수번호: {item['rcept_no']}\n")
                    f.write(f"접수일자: {item['rcept_dt']}\n")
                    f.write(f"회사명: {item['corp_name']}\n")
                    f.write(f"제출인: {item.get('flr_nm', 'N/A')}\n")
                    f.write(f"URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}\n")
                    f.write(f"\n수동 다운로드 방법:\n")
                    f.write(f"1. 위 URL 접속\n")
                    f.write(f"2. '첨부파일' 탭 클릭\n")
                    f.write(f"3. '외부평가보고서' 또는 '합병계획서' PDF 다운로드\n")
                    f.write(f"   (자본시장법 제176조의5 적용 사례 찾기)\n")

                print(f"   저장: {filename}\n")
            else:
                print()

        print("\n" + "=" * 80)
        print("검색 완료!")
        print("=" * 80)

    else:
        print(f"검색 실패: {data.get('message', '알 수 없는 오류')}")

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
