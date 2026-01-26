#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블 생성 스크립트 (psycopg2 사용)
"""

import psycopg2
from psycopg2 import sql

# Supabase PostgreSQL 연결 정보
DATABASE_URL = "postgresql://postgres:데이터베이스유하리@db.arxrfetgaitkgiiqabap.supabase.co:5432/postgres"

def create_deals_table():
    """Deal 테이블 생성"""
    conn = None
    cursor = None

    try:
        # DB 연결
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 테이블 생성 SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS deals (
            id BIGSERIAL PRIMARY KEY,

            -- 기업 정보
            company_name TEXT NOT NULL,
            industry TEXT,
            location TEXT,
            employees INTEGER,

            -- 투자 정보
            stage TEXT,
            investors TEXT,
            amount NUMERIC,  -- 투자금액 (억원)

            -- 뉴스 출처
            news_title TEXT,
            news_url TEXT,
            news_date DATE,
            site_name TEXT,

            -- 메타데이터
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """

        print("Creating deals table...")
        cursor.execute(create_table_sql)

        # 인덱스 생성
        print("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_deals_company_name ON deals(company_name);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_deals_news_date ON deals(news_date DESC);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_deals_created_at ON deals(created_at DESC);
        """)

        # updated_at 자동 업데이트 함수
        print("Creating trigger function...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # 트리거 생성
        print("Creating trigger...")
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_deals_updated_at ON deals;
        """)
        cursor.execute("""
            CREATE TRIGGER update_deals_updated_at
                BEFORE UPDATE ON deals
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)

        # RLS (Row Level Security) 설정
        print("Setting up RLS...")
        cursor.execute("""
            ALTER TABLE deals ENABLE ROW LEVEL SECURITY;
        """)

        # 기존 정책 삭제
        cursor.execute("""
            DROP POLICY IF EXISTS "Enable read access for all users" ON deals;
        """)
        cursor.execute("""
            DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON deals;
        """)
        cursor.execute("""
            DROP POLICY IF EXISTS "Enable update for authenticated users only" ON deals;
        """)
        cursor.execute("""
            DROP POLICY IF EXISTS "Enable delete for authenticated users only" ON deals;
        """)

        # 새 정책 생성
        cursor.execute("""
            CREATE POLICY "Enable read access for all users" ON deals
                FOR SELECT
                USING (true);
        """)
        cursor.execute("""
            CREATE POLICY "Enable insert for authenticated users only" ON deals
                FOR INSERT
                WITH CHECK (true);
        """)
        cursor.execute("""
            CREATE POLICY "Enable update for authenticated users only" ON deals
                FOR UPDATE
                USING (true);
        """)
        cursor.execute("""
            CREATE POLICY "Enable delete for authenticated users only" ON deals
                FOR DELETE
                USING (true);
        """)

        # 커밋
        conn.commit()

        print("\n" + "=" * 60)
        print("[SUCCESS] Deal table created successfully!")
        print("=" * 60)

    except Exception as e:
        if conn:
            conn.rollback()
        print("\n" + "=" * 60)
        print(f"[ERROR] Failed to create table: {e}")
        print("=" * 60)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    create_deals_table()
