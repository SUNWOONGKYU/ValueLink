import json
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

file_path = 'backend/reparse_result.json'

def update_deals_industry():
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'companies' not in data:
        print("Error: 'companies' key not found in JSON.")
        return

    print("Starting update of 'deals' table industries...")
    updated_count = 0
    errors = 0

    for item in data['companies']:
        company_name = item.get('company')
        industry = item.get('industry')

        if not company_name or not industry:
            continue

        try:
            # Update industry where company_name matches
            response = supabase.table("deals").update({"industry": industry}).eq("company_name", company_name).execute()
            
            # Check if any row was updated
            if response.data and len(response.data) > 0:
                print(f"Updated {company_name}: {industry}")
                updated_count += 1
            else:
                # print(f"Skipped {company_name}: Not found in DB")
                pass

        except Exception as e:
            print(f"Error updating {company_name}: {e}")
            errors += 1

    print("-" * 50)
    print(f"Update complete. Updated: {updated_count}, Errors: {errors}")

if __name__ == "__main__":
    update_deals_industry()
