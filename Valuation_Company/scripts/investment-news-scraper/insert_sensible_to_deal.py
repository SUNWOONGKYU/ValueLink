#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서블박스 위클리 129개 기업을 Deal 테이블에 저장
"""

import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")  # .env 파일의 키 이름과 일치
)

def safe_print(text, end='\n'):
    """인코딩 에러 방지"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


def insert_companies_from_csv():
    """CSV에서 읽어서 Deal 테이블에 삽입"""

    csv_file = 'sensible_companies_2026_01.csv'

    print("="*60)
    print("센서블박스 위클리 129개 기업 → Deal 테이블 삽입")
    print("="*60)
    safe_print(f"\nCSV 파일: {csv_file}\n")

    success_count = 0
    fail_count = 0
    inserted_companies = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    safe_print(f"총 기업 수: {len(companies)}개\n")
    safe_print("="*60 + "\n")

    for idx, row in enumerate(companies, 1):
        company_name = row['기업명']
        safe_print(f"[{idx}/{len(companies)}] {company_name}...", end=" ")

        try:
            # Deal 테이블에 INSERT
            data = {
                "기업명": row['기업명'],
                "주요사업": row['주요사업'],
                "투자자": row['투자자'],
                "투자단계": row['단계'],
                "투자금액": row['신규'],
                "지역": None,
                "직원수": None,
                "뉴스": None,  # 나중에 역추적으로 채움
            }

            result = supabase.table("Deal").insert(data).execute()

            print("[OK]")
            success_count += 1
            inserted_companies.append(company_name)

        except Exception as e:
            error_msg = str(e)
            if "duplicate key" in error_msg.lower():
                print("[SKIP] 이미 존재")
            else:
                print(f"[FAIL] {error_msg[:50]}")
            fail_count += 1

    # 결과 요약
    print("\n" + "="*60)
    print("삽입 완료")
    print("="*60)
    print(f"성공: {success_count}개")
    print(f"실패/중복: {fail_count}개")

    if inserted_companies:
        print(f"\n삽입된 기업 (처음 10개):")
        for name in inserted_companies[:10]:
            safe_print(f"  - {name}")
        if len(inserted_companies) > 10:
            print(f"  ... 외 {len(inserted_companies)-10}개")

    print("\n" + "="*60)
    safe_print("다음 단계: 역추적으로 각 기업의 뉴스 찾기")
    print("="*60)


if __name__ == '__main__':
    insert_companies_from_csv()
