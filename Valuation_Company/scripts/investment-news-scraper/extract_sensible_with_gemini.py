#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Vision API로 Sensible Box 이미지에서 정확한 데이터 추출
"""

import os
import sys
import csv
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# Gemini API 클라이언트
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def extract_table_from_image(image_path):
    """이미지에서 표 데이터 추출"""

    print(f"\n📸 {Path(image_path).name} 처리 중...")

    # 이미지 로드
    img = Image.open(image_path)

    # Gemini Vision API 프롬프트
    prompt = """
이 이미지는 Sensible Box Weekly 투자 뉴스 표입니다.

표의 각 행에서 다음 정보를 정확하게 추출해주세요:
- 기업명
- 주요사업
- 투자자
- 단계 (시리즈A, 프리A, 시드 등)
- 신규 (투자금액)
- 주차 (몇 주차)

출력 형식은 CSV 형식으로 해주세요:
기업명,주요사업,투자자,단계,신규,주차

**중요 사항:**
1. 기업명을 정확하게 읽어주세요 (OCR 오류 없이)
2. 투자자명도 정확하게 읽어주세요
3. 금액은 "142억원", "300억원" 형식으로
4. 단계는 "시리즈A", "프리A", "시드", "M&A" 등
5. 주차는 "3주차", "1주차" 등
6. 헤더 행은 제외하고 데이터 행만 출력
7. CSV 형식으로만 출력 (추가 설명 없이)
"""

    # Gemini API 호출
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=[prompt, img]
    )

    # 응답 텍스트
    text = response.text.strip()

    print(f"✅ {len(text.split(chr(10)))}개 행 추출")

    return text


def main():
    print("=" * 80)
    print("Gemini Vision API로 Sensible Box 이미지 데이터 추출")
    print("=" * 80)

    # inbox 폴더의 PNG 파일들
    inbox_dir = Path("C:/ValueLink/Valuation_Company/inbox")
    png_files = sorted(inbox_dir.glob("*.png"))

    print(f"\n📁 {len(png_files)}개 이미지 발견")

    all_data = []

    for png_file in png_files:
        csv_text = extract_table_from_image(png_file)

        # CSV 텍스트를 행으로 분리
        lines = csv_text.strip().split('\n')
        for line in lines:
            if line.strip():
                all_data.append(line)

    print(f"\n📊 총 {len(all_data)}개 데이터 추출")

    # CSV 파일로 저장
    output_file = "sensible_companies_2026_01_GEMINI.csv"

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        # 헤더 작성
        f.write("기업명,주요사업,투자자,단계,신규,주차\n")

        # 데이터 작성
        for line in all_data:
            f.write(line + '\n')

    print(f"\n✅ 저장 완료: {output_file}")

    # 미리보기
    print(f"\n📋 처음 10개 행:")
    print("-" * 80)
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 11:  # 헤더 + 10개 행
                break
            print(line.strip())


if __name__ == '__main__':
    main()
