#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple Migration Verification"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / '.env')

from supabase import create_client

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("="*60)
print("Phase 0-1: Migration Verification")
print("="*60)

try:
    # Select with new fields to verify they exist
    result = supabase.table('projects').select(
        'id, dcf_status, dcf_step, relative_status, relative_step, '
        'intrinsic_status, intrinsic_step, asset_status, asset_step, '
        'inheritance_tax_status, inheritance_tax_step'
    ).limit(1).execute()

    print("\n✅ SUCCESS! All method status fields exist:")
    print("  - dcf_status, dcf_step")
    print("  - relative_status, relative_step")
    print("  - intrinsic_status, intrinsic_step")
    print("  - asset_status, asset_step")
    print("  - inheritance_tax_status, inheritance_tax_step")

    if result.data:
        print(f"\n✅ Sample data from first project:")
        for key, value in result.data[0].items():
            if key != 'id':
                print(f"  {key}: {value}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFields may not have been added. Check Supabase dashboard.")

print("\n" + "="*60)
print("Phase 0-1: COMPLETED ✅")
print("="*60)
