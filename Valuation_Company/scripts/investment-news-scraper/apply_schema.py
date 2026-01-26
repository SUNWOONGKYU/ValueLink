#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase에 데이터베이스 스키마 적용
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

# Supabase 연결 정보
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# PostgreSQL 연결 문자열 구성
# Supabase URL 형식: https://arxrfetgaitkgiiqabap.supabase.co
# PostgreSQL 연결: postgres://postgres:[password]@db.arxrfetgaitkgiiqabap.supabase.co:5432/postgres

def get_connection_string():
    """Supabase URL에서 PostgreSQL 연결 문자열 생성"""

    print("="*60)
    print("Supabase Database Schema Setup")
    print("="*60)

    # .env에서 DB 비밀번호 읽기
    db_password = os.getenv('DB_PASSWORD')

    if not db_password:
        print("\nDB_PASSWORD not found in .env file")
        print("Please add: DB_PASSWORD=your-password")
        exit(1)

    # URL에서 프로젝트 ID 추출
    project_id = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')

    # PostgreSQL 연결 문자열 (SSL 모드 추가)
    connection_string = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres?sslmode=require"

    print(f"\nConnecting to: db.{project_id}.supabase.co (Direct connection with SSL)")
    return connection_string


def apply_schema():
    """스키마 적용"""

    # 연결 문자열 생성
    conn_string = get_connection_string()

    print("\n[1/3] Connecting to Supabase...")

    try:
        # PostgreSQL 연결
        conn = psycopg2.connect(conn_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("[SUCCESS] Connected to Supabase!\n")

        # 스키마 파일 읽기
        print("[2/3] Reading schema file...")
        with open('DATABASE_SCHEMA.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        print("[SUCCESS] Schema file loaded!\n")

        # 스키마 적용
        print("[3/3] Applying schema to database...")

        # SQL을 세미콜론으로 분리하여 각각 실행
        statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]

        total = len(statements)
        for i, statement in enumerate(statements, 1):
            try:
                # 주석 제거된 실제 SQL만 실행
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
                    print(f"  [{i}/{total}] Executed successfully")
            except Exception as e:
                # 이미 존재하는 테이블/인덱스는 무시
                if 'already exists' in str(e):
                    print(f"  [{i}/{total}] Already exists (skipped)")
                else:
                    print(f"  [{i}/{total}] ERROR: {str(e)[:100]}")

        print("\n[SUCCESS] Schema applied successfully!\n")

        # 테이블 확인
        print("="*60)
        print("Verifying tables...")
        print("="*60)

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print(f"\nTotal tables: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")

        # View 확인
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        views = cursor.fetchall()
        print(f"\nTotal views: {len(views)}")
        for view in views:
            print(f"  - {view[0]}")

        # 초기 데이터 확인
        print("\n" + "="*60)
        print("Verifying initial data...")
        print("="*60)

        cursor.execute("SELECT COUNT(*) FROM investment_news_network_sources;")
        sources_count = cursor.fetchone()[0]
        print(f"\ninvestment_news_network_sources: {sources_count} records")

        if sources_count > 0:
            cursor.execute("""
                SELECT rank, source_name, category, collection_method
                FROM investment_news_network_sources
                ORDER BY rank;
            """)
            sources = cursor.fetchall()
            print("\nSources:")
            for rank, name, category, method in sources:
                print(f"  {rank}. {name} ({category} - {method})")

        cursor.close()
        conn.close()

        print("\n" + "="*60)
        print("Setup Complete!")
        print("="*60)
        print("\nNext steps:")
        print("  1. RSS collection script")
        print("  2. Web scraping script")
        print("  3. Integration script")
        print("  4. Email system")

    except psycopg2.OperationalError as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("\nPlease check:")
        print("  1. Database password is correct")
        print("  2. Supabase project is active")
        print("  3. Database is accessible")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")


if __name__ == '__main__':
    apply_schema()
