#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 중복 제거
- 같은 기업명의 중복 레코드 중 최신 것만 남김
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from collections import defaultdict

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


def remove_duplicates():
    """중복 레코드 제거 (최신 것만 남김)"""

    print("=" * 70)
    print("Deal 테이블 중복 제거")
    print("=" * 70)

    # 모든 Deal 가져오기
    result = supabase.table("deals")\
        .select("*")\
        .order("id", desc=True)\
        .execute()

    deals = result.data
    print(f"\n총 레코드: {len(deals)}개")

    # 기업명별로 그룹핑 (id가 큰 것이 최신)
    company_groups = defaultdict(list)
    for deal in deals:
        company_name = deal['company_name']
        company_groups[company_name].append(deal)

    # 중복 찾기
    duplicates_to_delete = []
    for company_name, group in company_groups.items():
        if len(group) > 1:
            # ID가 가장 큰 것(최신)만 남기고 나머지 삭제
            sorted_group = sorted(group, key=lambda x: x['id'], reverse=True)
            keep = sorted_group[0]
            delete = sorted_group[1:]

            for deal in delete:
                duplicates_to_delete.append(deal['id'])

            print(f"  {company_name}: {len(group)}개 → 1개 (ID {keep['id']} 유지)")

    print(f"\n삭제할 중복 레코드: {len(duplicates_to_delete)}개")

    if duplicates_to_delete:
        print("\n삭제 시작...")
        deleted_count = 0

        # 배치로 삭제 (한 번에 100개씩)
        batch_size = 100
        for i in range(0, len(duplicates_to_delete), batch_size):
            batch = duplicates_to_delete[i:i+batch_size]

            for deal_id in batch:
                try:
                    supabase.table("deals")\
                        .delete()\
                        .eq("id", deal_id)\
                        .execute()
                    deleted_count += 1
                except Exception as e:
                    print(f"  ❌ ID {deal_id} 삭제 실패: {str(e)[:50]}")

            print(f"  진행: {deleted_count}/{len(duplicates_to_delete)}")

        print("\n" + "=" * 70)
        print("중복 제거 완료")
        print("=" * 70)
        print(f"✅ 삭제: {deleted_count}개")
        print(f"남은 레코드: {len(deals) - deleted_count}개")
        print("=" * 70)
    else:
        print("\n중복 없음!")


if __name__ == '__main__':
    remove_duplicates()
