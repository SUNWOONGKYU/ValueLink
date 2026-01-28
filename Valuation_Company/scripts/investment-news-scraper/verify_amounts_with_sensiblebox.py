#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서블박스 이미지에서 투자금액 추출하여 Deal 테이블과 비교 검증
"""

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# Gemini 클라이언트 (새 API)
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 80)
print("센서블박스 이미지에서 투자금액 추출 및 검증")
print("=" * 80)

# inbox 폴더의 PNG 파일들
inbox_path = Path("C:/ValueLink/Valuation_Company/inbox")
png_files = list(inbox_path.glob("*.png"))

print(f"\n센서블박스 이미지: {len(png_files)}개")

# Gemini로 전체 이미지 읽기
sensible_data = {}

for idx, png_file in enumerate(png_files, 1):
    print(f"\n[{idx}/{len(png_files)}] {png_file.name} 처리 중...")

    try:
        # 이미지 읽기
        with open(png_file, 'rb') as f:
            image_data = f.read()

        # Gemini에게 CSV 추출 요청
        prompt = """
이 이미지는 센서블박스 투자 데이터 표입니다.
표에서 다음 정보를 CSV 형식으로 추출해주세요:
- 기업명
- 투자금액 (억원 단위, 숫자만)

CSV 형식으로 출력:
기업명,투자금액
엔포러스,10
크레온유니티,300
...

주의: 비공개는 0으로 표시
"""

        # 이미지를 base64로 인코딩
        import base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        response = gemini_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                types.Content(
                    role='user',
                    parts=[
                        types.Part(inline_data=types.Blob(
                            mime_type='image/png',
                            data=image_base64
                        )),
                        types.Part(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=4096
            )
        )

        text = response.text.strip()

        # CSV 파싱
        lines = text.split('\n')
        for line in lines:
            if ',' in line and '기업명' not in line:
                parts = line.split(',')
                if len(parts) >= 2:
                    company = parts[0].strip()
                    amount_str = parts[1].strip()

                    # 숫자 추출
                    match = re.search(r'(\d+(?:\.\d+)?)', amount_str)
                    if match:
                        amount = float(match.group(1))
                        sensible_data[company] = amount

        print(f"  ✅ {len(lines)-1}개 회사 추출")

    except Exception as e:
        print(f"  ❌ 오류: {str(e)[:50]}")

print(f"\n총 센서블박스 데이터: {len(sensible_data)}개")

# Deal 테이블 조회
deals = supabase.table("deals").select("*").execute()

print("\n" + "=" * 80)
print("Deal 테이블과 비교 검증")
print("=" * 80)

matched = 0
different = 0
missing_in_sensible = 0
missing_in_deal = 0

for deal in deals.data:
    company = deal['company_name']
    deal_amount = deal.get('amount')

    if company in sensible_data:
        sensible_amount = sensible_data[company]

        if deal_amount:
            # 금액 비교 (10% 오차 허용)
            if sensible_amount == 0:
                # 센서블박스가 비공개인 경우
                if deal_amount not in [0, '비공개']:
                    matched += 1
            else:
                diff_ratio = abs(deal_amount - sensible_amount) / sensible_amount

                if diff_ratio < 0.1:  # 10% 이내
                    matched += 1
                else:
                    different += 1
                    print(f"  ⚠️  {company:20s}: Deal {deal_amount}억 vs 센서블 {sensible_amount}억")

                    # Deal 테이블을 센서블박스로 업데이트
                    supabase.table("deals")\
                        .update({'amount': sensible_amount})\
                        .eq("id", deal['id'])\
                        .execute()
        else:
            # Deal에 금액 없음 -> 센서블박스로 채우기
            missing_in_deal += 1

            if sensible_amount == 0:
                print(f"  ✅ {company:20s}: 센서블박스 비공개 (NULL 유지)")
                # amount는 NULL로 유지 (UI에서 "비공개"로 표시)
                matched += 1
            else:
                print(f"  ✅ {company:20s}: 센서블박스 {sensible_amount}억 추가")
                supabase.table("deals")\
                    .update({'amount': sensible_amount})\
                    .eq("id", deal['id'])\
                    .execute()
    else:
        if deal_amount:
            missing_in_sensible += 1

print("\n" + "=" * 80)
print("검증 결과")
print("=" * 80)

print(f"\n✅ 일치: {matched}개")
print(f"⚠️  차이: {different}개 (센서블박스로 수정)")
print(f"➕ Deal 추가: {missing_in_deal}개")
print(f"❓ 센서블박스 없음: {missing_in_sensible}개")

# 최종 통계
deals_final = supabase.table("deals").select("*").execute()
empty_amount = len([d for d in deals_final.data if not d.get('amount') or d.get('amount') == 0])

print(f"\n📊 최종: 투자금액 없음 {empty_amount}개")
