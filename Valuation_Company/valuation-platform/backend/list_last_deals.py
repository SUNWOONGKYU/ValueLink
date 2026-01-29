import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(override=True)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def list_deals():
    r = supabase.table('deals').select('company_name, news_title, news_date, site_name')\
        .order('created_at', desc=True).limit(41).execute()
    
    print(f"{'.':<3} | {'Company':<15} | {'News Title'}")
    print("-" * 80)
    for i, d in enumerate(r.data):
        print(f"{i+1:<3} | {d['company_name']:<15} | {d['news_title']}")

if __name__ == "__main__":
    list_deals()

