#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
126개 전체 기업을 Deal 테이블에 저장
"""

import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def safe_print(text, end='\n'):
    """인코딩 에러 방지"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('cp949', errors='replace').decode('cp949'), end=end)


def insert_all_companies():
    """126개 기업 전체 저장"""

    csv_file = 'sensible_companies_2026_01_COMPLETE.csv'

    print("="*60)
    print("126개 기업 → Deal 테이블 저장")
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
            # deals 테이블에 INSERT (영문 컬럼명)
            data = {
                "company_name": row['기업명'],
                "industry": row.get('주요사업', ''),
                "investors": row.get('투자자', ''),
                "stage": row.get('단계', ''),
                "location": None,
                "employees": None,
                "news_url": row.get('뉴스URL', ''),
                "news_title": f"{row['기업명']} {row.get('신규', '')} 투자 유치",
                "site_name": row.get('뉴스소스', '센서블박스 위클리'),
            }

            result = supabase.table("deals").insert(data).execute()

            print("✅")
            success_count += 1
            inserted_companies.append(company_name)

        except Exception as e:
            error_msg = str(e)
            if "duplicate key" in error_msg.lower():
                safe_print("⚠️ 중복")
            else:
                safe_print(f"❌ {error_msg[:30]}")
            fail_count += 1

    # 결과 요약
    print("\n" + "="*60)
    print("저장 완료")
    print("="*60)
    print(f"성공: {success_count}개")
    print(f"실패/중복: {fail_count}개")

    if inserted_companies:
        print(f"\n저장된 기업 (처음 10개):")
        for name in inserted_companies[:10]:
            safe_print(f"  - {name}")
        if len(inserted_companies) > 10:
            print(f"  ... 외 {len(inserted_companies)-10}개")

    print("\n" + "="*60)


if __name__ == '__main__':
    insert_all_companies()
