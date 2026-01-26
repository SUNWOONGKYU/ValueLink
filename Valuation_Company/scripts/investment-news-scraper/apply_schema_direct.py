#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase에 직접 SQL 실행
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')


def execute_sql_via_rest(sql):
    """REST API로 SQL 실행"""

    # Supabase는 REST API로 DDL을 실행할 수 없음
    # SQL Editor에 붙여넣기용 파일 생성

    print("="*60)
    print("Creating SQL file for manual execution")
    print("="*60)

    # SQL 파일 생성
    output_file = 'schema_to_execute.sql'

    with open('DATABASE_SCHEMA.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(schema_sql)

    print(f"\n[SUCCESS] SQL file created: {output_file}")
    print("\n" + "="*60)
    print("Manual Execution Steps:")
    print("="*60)
    print("\n1. Open Supabase SQL Editor:")
    print("   https://supabase.com/dashboard/project/arxrfetgaitkgiiqabap/editor")
    print("\n2. Click '+ New query'")
    print(f"\n3. Open file: {os.path.abspath(output_file)}")
    print("\n4. Copy all content and paste into SQL Editor")
    print("\n5. Click 'Run' button")
    print("\n" + "="*60)

    # SQL 내용 미리보기
    lines = schema_sql.split('\n')
    print(f"\nSQL Preview (first 20 lines):")
    print("-"*60)
    for line in lines[:20]:
        print(line)
    print("...")
    print(f"\nTotal lines: {len(lines)}")


if __name__ == '__main__':
    execute_sql_via_rest(None)
