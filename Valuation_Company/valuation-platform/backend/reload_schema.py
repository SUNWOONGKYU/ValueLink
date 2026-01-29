from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def reload_schema():
    print("Reloading PostgREST schema cache...")
    try:
        # 스키마 캐시 갱신을 위한 SQL 명령 실행
        supabase.rpc('exec_sql', {'query': "NOTIFY pgrst, 'reload schema';"}).execute()
        print("Schema reload command sent.")
    except Exception as e:
        print(f"Failed to reload schema via RPC: {e}")
        # RPC가 실패할 경우, 간단한 쿼리로 연결 확인만 시도
        try:
            supabase.table("deals").select("*", count="exact").limit(1).execute()
            print("Successfully queried 'deals' table (which might force cache update).")
        except Exception as e2:
            print(f"Failed to query 'deals' table: {e2}")

if __name__ == "__main__":
    reload_schema()
