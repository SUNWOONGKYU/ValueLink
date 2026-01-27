#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
못 찾은 14개 기업의 정확한 이름을 Gemini에게 다시 확인
"""

import os
import sys
from pathlib import Path
from google import genai
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

# 못 찾은 기업들 (```csv, ``` 제외)
missing_companies = [
    "에봄에이아이",
    "디앤티테크솔루션",
    "엑스닷츠",
    "하이파이브랩",
    "스카이인텔리전스",
    "엘리시전",
    "오픈웨딩",
    "스튜디오에피소드",
    "부스터스",
    "투모로우",
    "비바트로로보틱스",
    "덱사스튜디오",
    "한양로보틱스",
    "소서릭스코리아"
]


def verify_company_name(image_path, company_name):
    """이미지에서 특정 기업명을 찾아 정확한 표기 확인"""

    print(f"\n🔍 {company_name} 확인 중 ({Path(image_path).name})...")

    # 이미지 로드
    img = Image.open(image_path)

    # Gemini Vision API 프롬프트
    prompt = f"""
이 이미지는 Sensible Box Weekly 투자 뉴스 표입니다.

표에서 "{company_name}"와 비슷한 기업명을 찾아주세요.

**출력 형식:**
정확한 기업명만 출력해주세요. 만약 찾지 못했으면 "없음"이라고만 출력하세요.

예시:
- 입력: "에봄에이아이" → 출력: "애플에이아이" (정확한 이름)
- 입력: "엘리시전" → 출력: "엘리사젠" (정확한 이름)
- 입력: "부스터스" → 출력: "부스티스" (정확한 이름)

다른 설명 없이 정확한 기업명만 출력하세요.
"""

    # Gemini API 호출
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=[prompt, img]
    )

    # 응답 텍스트
    result = response.text.strip()

    return result


def main():
    print("=" * 80)
    print("못 찾은 14개 기업의 정확한 이름 확인")
    print("=" * 80)

    # inbox 폴더의 PNG 파일들
    inbox_dir = Path("C:/ValueLink/Valuation_Company/inbox")
    png_files = sorted(inbox_dir.glob("*.png"))

    results = {}

    for company in missing_companies:
        found = False

        # 5개 이미지 모두 확인
        for png_file in png_files:
            correct_name = verify_company_name(png_file, company)

            if correct_name != "없음" and correct_name.lower() != company.lower():
                print(f"  ✅ 정확한 이름 발견: {company} → {correct_name}")
                results[company] = correct_name
                found = True
                break

        if not found:
            print(f"  ❌ {company} - 이미지에서 찾지 못함")
            results[company] = company  # 원래 이름 유지

    print(f"\n{'='*80}")
    print("확인 완료")
    print(f"{'='*80}")

    # 결과 출력
    print("\n📋 정정된 기업명:")
    for original, corrected in results.items():
        if original != corrected:
            print(f"  {original:20s} → {corrected}")
        else:
            print(f"  {original:20s} (변경 없음)")

    # CSV로 저장
    with open('missing_14_corrected.csv', 'w', encoding='utf-8') as f:
        f.write("원래이름,정확한이름\n")
        for original, corrected in results.items():
            f.write(f"{original},{corrected}\n")

    print(f"\n✅ 저장 완료: missing_14_corrected.csv")


if __name__ == '__main__':
    main()
