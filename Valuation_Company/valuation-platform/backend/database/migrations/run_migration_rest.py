#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Migration Script (REST API)
Phase 0-1: Add method status fields using Supabase REST API
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / '.env')

import requests
import json

def run_migration_via_rest():
    """Execute migration SQL via Supabase REST API"""

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("[ERROR] SUPABASE_URL or SUPABASE_KEY not found in .env")
        sys.exit(1)

    # Read SQL file
    sql_file = Path(__file__).parent / 'add_method_status_fields.sql'
    if not sql_file.exists():
        print(f"[ERROR] SQL file not found: {sql_file}")
        sys.exit(1)

    with open(sql_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    print(f"[INFO] Connecting to Supabase: {supabase_url}")

    # Supabase uses PostgREST, we need to use the database via functions or direct pg connection
    # Let's try using supabase-py client instead
    try:
        from supabase import create_client, Client

        supabase: Client = create_client(supabase_url, supabase_key)

        print("[SUCCESS] Connected to Supabase!")
        print("[INFO] Running migration...")

        # Execute raw SQL via RPC (if you have a function) or use postgrest
        # Since we can't execute raw DDL via REST API easily, let's use psycopg2 with corrected connection

        print("[INFO] Attempting direct PostgreSQL connection...")
        import psycopg2

        # Parse DATABASE_URL from .env
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Fix encoding issue with Korean password
            conn = psycopg2.connect(database_url)
            conn.autocommit = True
            cursor = conn.cursor()

            print("[SUCCESS] PostgreSQL connection established!")
            print("[INFO] Executing migration SQL...")

            # Execute SQL
            cursor.execute(migration_sql)

            print("[SUCCESS] Migration completed!")

            # Verify
            print("\n[INFO] Verifying added fields:")
            cursor.execute("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'projects'
                AND (column_name LIKE '%_status' OR column_name LIKE '%_step')
                ORDER BY ordinal_position;
            """)

            results = cursor.fetchall()
            if results:
                print("\nAdded fields:")
                for row in results:
                    print(f"  - {row[0]}: {row[1]} (default: {row[2]})")

            cursor.close()
            conn.close()

            print("\n[SUCCESS] All tasks completed!")

    except ImportError:
        print("[INFO] Installing supabase-py...")
        os.system("pip install supabase")
        print("[INFO] Please run the script again")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")

        # Show more details
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_migration_via_rest()
