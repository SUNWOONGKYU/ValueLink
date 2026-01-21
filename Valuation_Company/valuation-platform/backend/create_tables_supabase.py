"""
Supabase를 통한 테이블 생성 및 모의 데이터 삽입

목업 데이터: 5가지 평가법별로 5건씩
"""

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

load_dotenv()

# Supabase 클라이언트 생성
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# SQL 테이블 생성 스크립트
CREATE_TABLES_SQL = """
-- 1. Projects 테이블
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'requested',
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    valuation_purpose VARCHAR(50),
    requested_methods TEXT[],
    target_date DATE,
    actual_completion_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Quotes 테이블
CREATE TABLE IF NOT EXISTS quotes (
    quote_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    base_fee BIGINT,
    discount_rate FLOAT,
    final_fee BIGINT,
    payment_terms TEXT,
    valid_until DATE,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Negotiations 테이블
CREATE TABLE IF NOT EXISTS negotiations (
    negotiation_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    request_type VARCHAR(50),
    details TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Documents 테이블
CREATE TABLE IF NOT EXISTS documents (
    document_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    file_name VARCHAR(500),
    file_url VARCHAR(1000),
    file_type VARCHAR(50),
    upload_status VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- 5. Approval Points 테이블
CREATE TABLE IF NOT EXISTS approval_points (
    approval_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    point_code VARCHAR(10),
    category VARCHAR(50),
    question TEXT,
    ai_decision VARCHAR(50),
    ai_rationale TEXT,
    human_decision VARCHAR(50),
    human_note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Valuation Results 테이블
CREATE TABLE IF NOT EXISTS valuation_results (
    result_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    method VARCHAR(50) NOT NULL,
    enterprise_value BIGINT,
    equity_value BIGINT,
    value_per_share BIGINT,
    calculation_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. Drafts 테이블
CREATE TABLE IF NOT EXISTS drafts (
    draft_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    content TEXT,
    version INTEGER DEFAULT 1,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. Revisions 테이블
CREATE TABLE IF NOT EXISTS revisions (
    revision_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    draft_id INTEGER REFERENCES drafts(draft_id),
    revision_type VARCHAR(50),
    details TEXT,
    requested_at TIMESTAMP DEFAULT NOW()
);

-- 9. Reports 테이블
CREATE TABLE IF NOT EXISTS reports (
    report_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    report_url VARCHAR(1000),
    issued_at TIMESTAMP DEFAULT NOW()
);
"""

def create_tables():
    """테이블 생성"""
    try:
        # Supabase SQL 실행
        result = supabase.rpc('exec_sql', {'query': CREATE_TABLES_SQL}).execute()
        print("✅ 테이블 생성 완료")
        return True
    except Exception as e:
        print(f"⚠️ 테이블 생성 중 오류 (이미 존재하거나 권한 문제일 수 있음): {e}")
        return False

def insert_mock_data():
    """5가지 평가법별로 모의 데이터 5건씩 삽입"""

    # 5가지 평가법
    methods = [
        "dcf",                    # DCF평가법
        "relative",               # 상대가치평가법
        "capital_market_law",     # 본질가치평가법
        "asset",                  # 자산가치평가법
        "inheritance_tax_law"     # 상증세법평가법
    ]

    companies = [
        "테크스타트업 A", "바이오텍 B", "핀테크 C", "이커머스 D", "게임테크 E",
        "AI플랫폼 F", "헬스케어 G", "모빌리티 H", "에듀테크 I", "푸드테크 J",
        "클라우드 K", "블록체인 L", "로보틱스 M", "SaaS N", "마켓플레이스 O",
        "패션테크 P", "프롭테크 Q", "애그테크 R", "스포츠테크 S", "미디어테크 T",
        "뷰티테크 U", "펫테크 V", "여행테크 W", "물류테크 X", "HR테크 Y"
    ]

    purposes = ["MA", "IPO", "investment", "merger", "inheritance"]

    print("\n📊 모의 데이터 삽입 시작...")

    # 각 평가법별로 5건씩 (총 25건)
    for idx, method in enumerate(methods):
        print(f"\n{idx+1}. {method} 평가법 데이터 5건 삽입 중...")

        for i in range(5):
            project_idx = idx * 5 + i
            company_name = companies[project_idx]

            # Project ID 생성
            date_str = datetime.now().strftime("%y%m%d%H%M")
            project_id = f"{company_name[:3]}-{date_str}-{chr(65+project_idx)}"

            # 1. Project 삽입
            project_data = {
                "project_id": project_id,
                "status": random.choice(["requested", "evaluating", "completed"]),
                "company_name_kr": company_name,
                "company_name_en": f"{company_name} Inc.",
                "business_registration_number": f"110-81-{10000 + project_idx}",
                "representative_name": f"대표자{chr(65+project_idx)}",
                "valuation_purpose": purposes[i],
                "requested_methods": [method],
                "target_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            try:
                supabase.table("projects").insert(project_data).execute()
                print(f"   ✅ Project {project_idx+1}: {company_name}")
            except Exception as e:
                print(f"   ⚠️ Project {project_idx+1} 삽입 실패: {e}")

            # 2. Valuation Result 삽입
            base_value = random.randint(50, 200) * 100000000  # 50억 ~ 200억

            valuation_data = {
                "project_id": project_id,
                "method": method,
                "enterprise_value": base_value,
                "equity_value": int(base_value * 0.9),
                "value_per_share": random.randint(10000, 50000),
                "calculation_details": {
                    "wacc": round(random.uniform(0.08, 0.15), 4),
                    "growth_rate": round(random.uniform(0.02, 0.05), 4),
                    "terminal_value": base_value * 0.6,
                    "formula": f"{method} 평가 공식"
                },
                "created_at": datetime.now().isoformat()
            }

            try:
                supabase.table("valuation_results").insert(valuation_data).execute()
                print(f"      ✅ Valuation Result: {base_value:,}원")
            except Exception as e:
                print(f"      ⚠️ Valuation Result 삽입 실패: {e}")

    print("\n✅ 모의 데이터 삽입 완료!")
    print(f"   총 {len(methods) * 5}개 프로젝트 생성")
    print(f"   5가지 평가법 × 5건씩 = 25건")

if __name__ == "__main__":
    print("=" * 60)
    print("Supabase 테이블 생성 및 모의 데이터 삽입")
    print("=" * 60)

    # 1. 테이블 생성
    print("\n[Step 1] 테이블 생성...")
    create_tables()

    # 2. 모의 데이터 삽입
    print("\n[Step 2] 모의 데이터 삽입...")
    insert_mock_data()

    print("\n" + "=" * 60)
    print("✅ 모든 작업 완료!")
    print("=" * 60)
