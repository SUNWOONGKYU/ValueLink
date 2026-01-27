#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
잘못 추출된 CEO 이름 수정
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


def fix_wrong_ceo():
    """잘못된 CEO 이름 NULL로 초기화"""

    print("=" * 70)
    print("잘못된 CEO 이름 수정")
    print("=" * 70)

    # 잘못된 CEO 이름 패턴
    wrong_ceos = [
        '우테일의',
        '와우테일',
        '벤처스퀘어',
        '더브이씨',
        '인터뷰',
        '기자',
        '편집장',
    ]

    # CEO가 있는 모든 레코드 가져오기
    result = supabase.table("deals")\
        .select("id, company_name, ceo")\
        .not_.is_("ceo", "null")\
        .execute()

    deals = result.data
    print(f"\nCEO가 있는 레코드: {len(deals)}개\n")

    fixed_count = 0

    for deal in deals:
        ceo = deal.get('ceo', '')
        company_name = deal['company_name']

        # 잘못된 CEO인지 확인
        is_wrong = False
        for wrong in wrong_ceos:
            if wrong in ceo:
                is_wrong = True
                break

        if is_wrong:
            print(f"✅ {company_name}: '{ceo}' → NULL")
            supabase.table("deals")\
                .update({"ceo": None})\
                .eq("id", deal['id'])\
                .execute()
            fixed_count += 1

    print("\n" + "=" * 70)
    print("수정 완료")
    print("=" * 70)
    print(f"✅ 수정: {fixed_count}개")
    print("=" * 70)


if __name__ == '__main__':
    fix_wrong_ceo()
