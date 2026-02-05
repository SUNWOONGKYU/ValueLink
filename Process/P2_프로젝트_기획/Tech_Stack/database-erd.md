# ValueLink Database ERD

**작성일**: 2026-02-05
**버전**: 1.0
**Database**: Supabase PostgreSQL 15.x

---

## ERD Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                       projects (마스터)                       │
├──────────────────────────────────────────────────────────────┤
│ PK │ project_id          VARCHAR(50)                         │
│    │ status              VARCHAR(50)                         │
│    │ company_name_kr     VARCHAR(200)                        │
│    │ company_name_en     VARCHAR(200)                        │
│    │ business_registration_number VARCHAR(20)               │
│    │ representative_name VARCHAR(100)                        │
│    │ valuation_purpose   VARCHAR(50)                         │
│    │ requested_methods   TEXT[]                              │
│    │ target_date         DATE                                │
│    │ actual_completion_date DATE                             │
│    │ created_at          TIMESTAMP                           │
│    │ updated_at          TIMESTAMP                           │
└──────────────────────────────────────────────────────────────┘
         │
         ├────────────┬─────────────┬──────────────┬───────────┐
         ▼            ▼             ▼              ▼           ▼
┌─────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   quotes    │ │negotiations│ │documents │ │ approval │ │valuation │
│   (견적)     │ │  (협상)     │ │ (문서)    │ │ _points  │ │ _results │
├─────────────┤ ├────────────┤ ├──────────┤ ├──────────┤ ├──────────┤
│PK quote_id  │ │PK neg_id   │ │PK doc_id │ │PK appr_id│ │PK result_│
│FK project_id│ │FK project_│ │FK project│ │FK project│ │   id     │
│  base_fee   │ │   id       │ │   _id    │ │   _id    │ │FK project│
│  final_fee  │ │  type      │ │  file_   │ │  point_  │ │   _id    │
│  valid_until│ │  details   │ │  name    │ │  code    │ │  method  │
└─────────────┘ └────────────┘ │  file_url│ │  ai_dec  │ │  enter_  │
                                └──────────┘ │  human_  │ │  prise_  │
                                             │  dec     │ │  value   │
                                             └──────────┘ │  equity_ │
                                                          │  value   │
         ┌───────────────────────────────────────────────┤  calc_   │
         │                                               │  details │
         ▼                                               └──────────┘
┌──────────────┐              ┌──────────────┐
│   drafts     │──────────────│  revisions   │
│   (초안)      │ 1          N │   (수정)      │
├──────────────┤              ├──────────────┤
│PK draft_id   │              │PK revision_id│
│FK project_id │              │FK project_id │
│   content    │              │FK draft_id   │
│   version    │              │   type       │
│   created_by │              │   details    │
└──────────────┘              └──────────────┘
         │
         │ 1
         │
         ▼ 1
┌──────────────┐
│   reports    │
│  (최종보고서) │
├──────────────┤
│PK report_id  │
│FK project_id │
│   report_url │
│   issued_at  │
└──────────────┘
```

---

## 테이블 상세 정의

### 1. projects (프로젝트 마스터)

**용도**: 평가 프로젝트의 마스터 정보

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| project_id | VARCHAR(50) | PK | 프로젝트 ID (PROJ-YYYYMMDD-NNN) |
| status | VARCHAR(50) | NOT NULL | 프로젝트 상태 (requested, approved, in_progress, completed) |
| company_name_kr | VARCHAR(200) | NOT NULL | 기업명 (한글) |
| company_name_en | VARCHAR(200) | | 기업명 (영문) |
| business_registration_number | VARCHAR(20) | | 사업자등록번호 |
| representative_name | VARCHAR(100) | | 대표자명 |
| valuation_purpose | VARCHAR(50) | | 평가 목적 (투자유치, M&A, 상속증여, IPO, 기타) |
| requested_methods | TEXT[] | | 요청 평가 방법 배열 (['dcf', 'relative', 'asset']) |
| target_date | DATE | | 목표 완료일 |
| actual_completion_date | DATE | | 실제 완료일 |
| created_at | TIMESTAMP | DEFAULT NOW() | 생성일 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 수정일 |

**인덱스**:
- PRIMARY KEY (project_id)
- INDEX (status)
- INDEX (created_at)

**샘플 데이터**:
```sql
INSERT INTO projects VALUES (
  'PROJ-20260205-001',
  'in_progress',
  '테크이노',
  'TechInno',
  '123-45-67890',
  '김철수',
  '투자유치',
  ARRAY['dcf', 'relative'],
  '2026-02-20',
  NULL,
  NOW(),
  NOW()
);
```

---

### 2. quotes (견적서)

**용도**: 평가 견적 정보

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| quote_id | SERIAL | PK | 견적 ID (자동증가) |
| project_id | VARCHAR(50) | FK → projects | 프로젝트 ID |
| base_fee | BIGINT | | 기본 수수료 (원) |
| discount_rate | FLOAT | | 할인율 (0.0 ~ 1.0) |
| final_fee | BIGINT | | 최종 수수료 (원) |
| payment_terms | TEXT | | 지불 조건 (예: "계약금 20%, 잔금 80%") |
| valid_until | DATE | | 견적 유효기한 |
| sent_at | TIMESTAMP | | 견적 발송일 |
| created_at | TIMESTAMP | DEFAULT NOW() | 생성일 |

**관계**:
- 1 project : N quotes (1개 프로젝트에 여러 견적 가능)

---

### 3. negotiations (협상 내역)

**용도**: 견적 협상 이력

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| negotiation_id | SERIAL | PK | 협상 ID |
| project_id | VARCHAR(50) | FK → projects | 프로젝트 ID |
| request_type | VARCHAR(50) | | 협상 유형 (discount, schedule, scope) |
| details | TEXT | | 협상 내용 |
| status | VARCHAR(50) | | 상태 (pending, accepted, rejected) |
| created_at | TIMESTAMP | DEFAULT NOW() | 생성일 |

---

### 4. documents (자료 업로드)

**용도**: 고객이 업로드한 문서 관리

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| document_id | SERIAL | PK | 문서 ID |
| project_id | VARCHAR(50) | FK → projects | 프로젝트 ID |
| file_name | VARCHAR(500) | | 파일명 |
| file_url | VARCHAR(1000) | | Supabase Storage URL |
| file_type | VARCHAR(50) | | 문서 유형 (재무제표, 사업계획서, 등기부등본, etc.) |
| upload_status | VARCHAR(50) | | 업로드 상태 (pending, uploaded, verified) |
| uploaded_at | TIMESTAMP | DEFAULT NOW() | 업로드일 |

**파일 유형**:
- `재무제표` - Financial statements
- `사업계획서` - Business plan
- `등기부등본` - Business registration
- `주주명부` - Shareholder list
- `감정평가서` - Appraisal report
- `기타` - Other

---

### 5. approval_points (인간 승인 포인트)

**용도**: 22개 승인 포인트 추적

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| approval_id | SERIAL | PK | 승인 ID |
| project_id | VARCHAR(50) | FK → projects | 프로젝트 ID |
| point_code | VARCHAR(10) | | 포인트 코드 (DCF_GROWTH_RATE, etc.) |
| category | VARCHAR(50) | | 카테고리 (DCF, 상대가치, 자산, 내재, 상증세, 통합) |
| question | TEXT | | 평가자에게 보여줄 질문 |
| ai_decision | VARCHAR(50) | | AI 추천 시나리오 |
| ai_rationale | TEXT | | AI 추천 근거 |
| human_decision | VARCHAR(50) | | 평가자 선택 |
| human_note | TEXT | | 평가자 의견 |
| created_at | TIMESTAMP | DEFAULT NOW() | 생성일 |

**주요 포인트 코드**:
- `DCF_GROWTH_RATE` - 매출 성장률
- `DCF_WACC` - WACC (할인율)
- `DCF_ONE_TIME_ITEMS` - 일회성 항목 조정
- `DCF_EBITDA_MARGIN` - 영업이익률
- `REL_COMPARABLE_COMPANIES` - 비교기업 선정
- `REL_MARKETABILITY_DISCOUNT` - 비상장 할인율
- `NAV_LAND_BUILDING_FV` - 토지/건물 공정가치
- `NAV_CONTINGENT_LIABILITIES` - 우발부채 인식
- `INTEGRATED_VALUE_RANGE` - 최종 가치 범위

---

### 6. valuation_results (평가 결과)

**용도**: 각 평가 방법별 결과 저장

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| result_id | SERIAL | PK | 결과 ID |
| project_id | VARCHAR(50) | FK → projects | 프로젝트 ID |
| method | VARCHAR(50) | NOT NULL | 평가 방법 (dcf, relative, intrinsic, asset, inheritance_tax) |
| enterprise_value | BIGINT | | 기업가치 (원) |
| equity_value | BIGINT | | 주주가치 (원) |
| value_per_share | BIGINT | | 주당가치 (원) |
| calculation_details | JSONB | | 계산 상세 (JSONB) |
| created_at | TIMESTAMP | DEFAULT NOW() | 생성일 |

**calculation_details JSONB 구조**:

**DCF:**
```json
{
  "fcff_projections": [1000, 1200, 1440, 1728, 2074],
  "terminal_value": 50000,
  "wacc": 0.0886,
  "pv_breakdown": {
    "cumulative_pv": 5000,
    "terminal_pv": 30000
  }
}
```

**Relative:**
```json
{
  "comparable_companies": ["Company A", "Company B"],
  "multiples": {
    "per": 15.2,
    "pbr": 2.1,
    "psr": 1.5,
    "ev_ebitda": 10.5
  },
  "marketability_discount": 0.2
}
```

---

### 7. drafts (초안 버전 관리)

**용도**: 보고서 초안 버전 관리

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| draft_id | SERIAL | PK | 초안 ID |
| project_id | VARCHAR(50) | FK → projects | 프로젝트 ID |
| content | TEXT | | 초안 내용 (Markdown 또는 HTML) |
| version | INTEGER | DEFAULT 1 | 버전 번호 |
| created_by | VARCHAR(100) | | 작성자 (accountant ID) |
| created_at | TIMESTAMP | DEFAULT NOW() | 생성일 |

**관계**:
- 1 project : N drafts (여러 버전)

---

### 8. revisions (수정 요청)

**용도**: 고객의 수정 요청 추적

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| revision_id | SERIAL | PK | 수정 ID |
| project_id | VARCHAR(50) | FK → projects | 프로젝트 ID |
| draft_id | INTEGER | FK → drafts | 초안 ID |
| revision_type | VARCHAR(50) | | 수정 유형 (수치변경, 문구수정, 차트추가) |
| details | TEXT | | 수정 내용 상세 |
| requested_at | TIMESTAMP | DEFAULT NOW() | 요청일 |

**관계**:
- 1 draft : N revisions

---

### 9. reports (최종 보고서)

**용도**: 최종 승인된 보고서

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| report_id | SERIAL | PK | 보고서 ID |
| project_id | VARCHAR(50) | FK → projects | 프로젝트 ID |
| report_url | VARCHAR(1000) | | Supabase Storage URL |
| issued_at | TIMESTAMP | DEFAULT NOW() | 발행일 |

**관계**:
- 1 project : 1 report (최종 보고서)

---

## 데이터 흐름

### 신규 프로젝트 생성
```sql
1. INSERT INTO projects (project_id, company_name_kr, ...)
2. INSERT INTO quotes (project_id, base_fee, ...)
3. INSERT INTO documents (project_id, file_name, file_url, ...)
   (고객이 재무제표, 사업계획서 업로드)
```

### 평가 실행
```sql
4. INSERT INTO approval_points (project_id, point_code, ...)
   (AI가 22개 승인 포인트 생성)
5. UPDATE approval_points SET human_decision = '...'
   (회계사가 승인)
6. INSERT INTO valuation_results (project_id, method, ...)
   (각 평가 방법별 결과 저장)
```

### 초안 생성 및 수정
```sql
7. INSERT INTO drafts (project_id, content, version)
8. INSERT INTO revisions (project_id, draft_id, details)
   (고객이 수정 요청)
9. INSERT INTO drafts (project_id, content, version=2)
   (수정 반영 후 새 버전)
```

### 최종 보고서
```sql
10. INSERT INTO reports (project_id, report_url)
11. UPDATE projects SET status='completed', actual_completion_date=NOW()
```

---

## 인덱스 전략

### 성능 최적화를 위한 인덱스

```sql
-- projects 테이블
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

-- approval_points 테이블
CREATE INDEX idx_approval_project_id ON approval_points(project_id);
CREATE INDEX idx_approval_point_code ON approval_points(point_code);

-- valuation_results 테이블
CREATE INDEX idx_results_project_id ON valuation_results(project_id);
CREATE INDEX idx_results_method ON valuation_results(method);

-- documents 테이블
CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_documents_type ON documents(file_type);
```

---

## Row Level Security (RLS)

### Supabase RLS 정책

**Customer (고객)**:
```sql
-- 본인 프로젝트만 조회
CREATE POLICY customer_select_own ON projects
FOR SELECT USING (auth.uid() = customer_user_id);

-- 본인 문서만 업로드
CREATE POLICY customer_insert_own_doc ON documents
FOR INSERT WITH CHECK (auth.uid() = customer_user_id);
```

**Accountant (회계사)**:
```sql
-- 할당된 프로젝트만 조회
CREATE POLICY accountant_select_assigned ON projects
FOR SELECT USING (accountant_user_id = auth.uid());

-- 할당된 프로젝트의 승인 포인트만 수정
CREATE POLICY accountant_update_approval ON approval_points
FOR UPDATE USING (accountant_user_id = auth.uid());
```

**Admin (관리자)**:
```sql
-- 모든 프로젝트 접근
CREATE POLICY admin_all_access ON projects
FOR ALL USING (user_role = 'admin');
```

---

## 백업 전략

### 자동 백업 (Supabase)
- **일일 백업**: 매일 02:00 KST
- **보관 기간**: 7일
- **수동 백업**: 주요 배포 전

### 복구 절차
```bash
# Supabase CLI로 백업
supabase db dump -f backup.sql

# 복구
psql -h db.xxx.supabase.co -U postgres -d postgres -f backup.sql
```

---

## 마이그레이션 전략

### Schema 변경 프로세스

```sql
-- 1. 마이그레이션 파일 생성
-- migrations/20260205_add_user_preferences.sql

-- 2. ALTER 문 작성
ALTER TABLE projects ADD COLUMN user_preferences JSONB;

-- 3. 데이터 마이그레이션 (필요 시)
UPDATE projects SET user_preferences = '{}' WHERE user_preferences IS NULL;

-- 4. Supabase Dashboard에서 실행 또는
supabase db push
```

---

**작성자**: Claude Code
**참조**: create_tables.sql, Explore Agent 분석
**버전**: 1.0
