#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Migration Script
Phase 0-1: Add method status fields to projects table
"""

import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
# migrations/ -> database/ -> backend/ -> .env
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / '.env'
load_dotenv(env_path)

import psycopg2

def run_migration():
    """Execute migration SQL"""

    # Get DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not found in .env file")
        sys.exit(1)

    # Read SQL file
    sql_file = Path(__file__).parent / 'add_method_status_fields.sql'
    if not sql_file.exists():
        print(f"[ERROR] SQL file not found: {sql_file}")
        sys.exit(1)

    with open(sql_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    print("[INFO] Connecting to Supabase...")

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("[SUCCESS] Connected to Supabase!")
        print("[INFO] Running migration...")

        # Execute SQL
        cursor.execute(migration_sql)

        print("[SUCCESS] Migration completed!")

        # Verify results
        print("\n[INFO] Verifying added fields:")
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'projects'
            AND column_name LIKE '%_status'
            ORDER BY ordinal_position;
        """)

        results = cursor.fetchall()
        if results:
            print("\nStatus fields added:")
            for row in results:
                print(f"  - {row[0]}: {row[1]} (default: {row[2]})")

        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'projects'
            AND column_name LIKE '%_step'
            ORDER BY ordinal_position;
        """)

        results = cursor.fetchall()
        if results:
            print("\nStep fields added:")
            for row in results:
                print(f"  - {row[0]}: {row[1]} (default: {row[2]})")

        cursor.close()
        conn.close()

        print("\n[SUCCESS] All tasks completed!")

    except psycopg2.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_migration()
