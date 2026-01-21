# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import os

# API 키 설정
API_KEY = "9e4eb688beb65c2e908054762ac27eb39503b197"

print("=" * 80)
print("DART 다음커뮤니케이션 합병 공시 검색")
print("=" * 80)

# 먼저 다음커뮤니케이션 고유번호 찾기
print("\n1단계: 다음커뮤니케이션 고유번호 검색...\n")

corp_url = "https://opendart.fss.or.kr/api/corpCode.xml"
corp_params = {"crtfc_key": API_KEY}

try:
    # 기업 고유번호 조회 (ZIP 파일)
    import zipfile
    import xml.etree.ElementTree as ET
    from io import BytesIO

    response = requests.get(corp_url, params=corp_params)

    if response.status_code == 200:
        # ZIP 파일 압축 해제
        with zipfile.ZipFile(BytesIO(response.content)) as zf:
            with zf.open('CORPCODE.xml') as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # 다음 관련 회사 찾기
                daum_companies = []
                for company in root.findall('.//list'):
                    corp_name = company.find('corp_name').text
                    if '다음' in corp_name:
                        corp_code = company.find('corp_code').text
                        stock_code = company.find('stock_code').text if company.find('stock_code') is not None else 'N/A'
                        daum_companies.append({
                            'name': corp_name,
                            'corp_code': corp_code,
                            'stock_code': stock_code.text if hasattr(stock_code, 'text') else stock_code
                        })
                        print(f"발견: {corp_name} (고유번호: {corp_code}, 종목코드: {stock_code})")

    print(f"\n총 {len(daum_companies)}개 회사 발견\n")

    # 각 회사별로 합병 공시 검색
    for company in daum_companies:
        print(f"\n{'=' * 60}")
        print(f"검색 대상: {company['name']}")
        print(f"{'=' * 60}")

        url = "https://opendart.fss.or.kr/api/list.json"
        params = {
            "crtfc_key": API_KEY,
            "corp_code": company['corp_code'],
            "bgn_de": "20140501",
            "end_de": "20141031",
            "page_count": 100
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] == '000' and 'list' in data:
            results = data['list']
            print(f"총 {len(results)}건의 공시 발견")

            # 합병 관련 공시 필터링
            merger_reports = [r for r in results if '합병' in r['report_nm'] or '카카오' in r['report_nm']]

            if merger_reports:
                print(f"합병 관련 공시: {len(merger_reports)}건\n")

                for idx, item in enumerate(merger_reports, 1):
                    print(f"\n{idx}. {item['report_nm']}")
                    print(f"   접수번호: {item['rcept_no']}")
                    print(f"   접수일자: {item['rcept_dt']}")
                    print(f"   URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}")

                    # 정보 파일 저장
                    filename = f"{item['rcept_dt']}_{company['name'][:10]}_{item['report_nm'][:20]}_INFO.txt"
                    filename = filename.replace("/", "_").replace("\\", "_").replace(":", "_").replace("?", "_").replace(")", "_").replace("(", "_")

                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"공시명: {item['report_nm']}\n")
                        f.write(f"접수번호: {item['rcept_no']}\n")
                        f.write(f"접수일자: {item['rcept_dt']}\n")
                        f.write(f"회사명: {company['name']}\n")
                        f.write(f"고유번호: {company['corp_code']}\n")
                        f.write(f"제출인: {item.get('flr_nm', 'N/A')}\n")
                        f.write(f"URL: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['rcept_no']}\n")
                        f.write(f"\n수동 다운로드 방법:\n")
                        f.write(f"1. 위 URL 접속\n")
                        f.write(f"2. '첨부파일' 탭 클릭\n")
                        f.write(f"3. '외부평가보고서', '합병계획서' 또는 '주식교환계획서' PDF 다운로드\n")

                    print(f"   저장: {filename}")
            else:
                print("합병 관련 공시 없음")

    print("\n" + "=" * 80)
    print("검색 완료!")
    print("=" * 80)

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
