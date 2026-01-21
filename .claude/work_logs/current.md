# Work Log - Valuation Platform Backend Development

## 작업 날짜: 2026-01-20

---

## Pydantic 스키마 정의 완료 ✅

### 작업 상태: ✅ 완료

### 작업 개요
API 명세서 (comprehensive-valuation-api-spec.md)를 기반으로 15개 API 엔드포인트에 필요한 모든 Pydantic Request/Response 스키마를 정의함.

---

### 생성된 파일 목록 (9개)

#### 1. backend/schemas/__init__.py
- 전체 스키마 export
- 모든 Request/Response 모델 임포트

#### 2. backend/schemas/common.py
- `CompanyInfo`: 회사 기본 정보
- `ContactInfo`: 담당자 정보
- `ValuationInfo`: 평가 정보
- `ProjectStatusCode`: 프로젝트 상태 (11개)
- `ValuationMethodCode`: 평가법 코드 (5개)
- `ValuationPurposeCode`: 평가 목적 코드
- `ErrorResponse`: 에러 응답

#### 3. backend/schemas/project.py
- `ProjectCreateRequest/Response`: 프로젝트 생성
- `QuoteRequest/Response`: 견적서 발송
- `NegotiationRequest/Response`: 조건 협의
- `ApprovalRequest/Response`: 계약 확정 및 회계사 배정
- `AccountantInfo`: 회계사 정보

#### 4. backend/schemas/document.py
- `DocumentCategory`: 6개 문서 카테고리
- `UploadedFileInfo`: 업로드된 파일 정보
- `UploadProgress`: 업로드 진행 상황
- `DocumentUploadResponse`: 문서 업로드 응답

#### 5. backend/schemas/extraction.py
- `ExtractionRequest/Response`: AI 데이터 추출
- `ExtractedCompanyData`: 추출된 회사 데이터
- `ExtractedFinancials`: 추출된 재무 데이터
- `ExtractedBalanceSheet`: 추출된 재무상태표
- `ExtractedCapitalStructure`: 추출된 자본 구조
- `AutoCollectResponse`: AI 자동 수집
- `MarketData`: 시장 데이터
- `IndustryData`: 업종 데이터
- `ComparableCompany`: 비교 기업

#### 6. backend/schemas/valuation.py
- `CalculationRequest/Response`: 평가 실행
- `DCFResult`: DCF평가법 결과
- `RelativeResult`: 상대가치평가법 결과
- `AssetResult`: 자산가치평가법 결과
- `CapitalMarketLawResult`: 본질가치평가법 결과
- `InheritanceTaxLawResult`: 상증세법평가법 결과
- `IntegratedResult`: 통합 평가 결과
- `PreviewResponse`: 결과 미리보기
- `SimulationRequest/Response`: 시뮬레이션
- `SensitivityMatrix`: 민감도 분석

#### 7. backend/schemas/approval.py
- `ApprovalPoint`: 회계사 판단 포인트
- `ApprovalPointsResponse`: 판단 포인트 목록
- `ApprovalDecisionRequest/Response`: 판단 포인트 승인
- `ImpactAnalysis`: 영향 분석
- `APPROVAL_POINTS_SPEC`: 22개 판단 포인트 전체 목록
  - JP001-JP008: DCF평가법 (8개)
  - JP009-JP012: 상대가치평가법 (4개)
  - JP013-JP018: 자산가치평가법 (6개)
  - JP019-JP020: 본질가치평가법 (2개)
  - JP021-JP022: 상증세법평가법 (2개)

#### 8. backend/schemas/draft.py
- `DraftRequest/Response`: 초안 생성
- `RevisionRequest/Response`: 수정 요청

#### 9. backend/schemas/report.py
- `FinalizeRequest/Response`: 최종 확정
- `FinalValuation`: 최종 평가 결과
- `ReportRequest/Response`: 보고서 발행

---

### 커버된 API 엔드포인트 (16개)

1. **POST /projects** - 프로젝트 생성
2. **POST /projects/{id}/quote** - 견적서 발송
3. **POST /projects/{id}/negotiate** - 조건 협의
4. **POST /projects/{id}/approve** - 계약 확정 및 회계사 배정
5. **POST /projects/{id}/documents** - 문서 업로드
6. **POST /projects/{id}/extract** - AI 데이터 추출
7. **POST /projects/{id}/auto-collect** - AI 자동 수집
8. **POST /projects/{id}/calculate** - 평가 실행
9. **GET /projects/{id}/approval-points** - 판단 포인트 조회
10. **POST /projects/{id}/approval-points/{point_id}** - 판단 포인트 승인
11. **POST /projects/{id}/draft** - 초안 생성
12. **POST /projects/{id}/revisions** - 수정 요청
13. **GET /projects/{id}/preview** - 결과 미리보기
14. **POST /projects/{id}/simulate** - 시뮬레이션
15. **POST /projects/{id}/finalize** - 최종 확정
16. **POST /projects/{id}/report** - 보고서 발행

---

### 특징

1. **타입 안전성**: Pydantic 모델로 Request/Response 타입 검증
2. **자동 문서화**: FastAPI Swagger에서 자동으로 API 문서 생성
3. **예제 포함**: 모든 스키마에 `json_schema_extra` 예제 포함
4. **검증 규칙**: Field validators (pattern, gt, ge, le 등)
5. **Literal 타입**: 상태 코드, 카테고리 등에 Literal 사용
6. **Union 타입**: 다양한 타입을 받는 필드 (approval point values)

---

---

## Database 모델 정의 완료 ✅

### 작업 상태: ✅ 완료

### 작업 개요
SQLAlchemy를 사용하여 9개 주요 테이블 모델 정의 완료. PostgreSQL 데이터베이스 기준으로 작성.

---

### 생성된 파일 목록 (13개)

#### 1. backend/models/__init__.py
- 전체 모델 export
- 9개 테이블 모델 임포트

#### 2. backend/models/base.py
- `Base`: SQLAlchemy declarative base
- `TimestampMixin`: created_at, updated_at 자동 관리

#### 3. backend/models/project.py
- `Project` 테이블 (프로젝트 기본 정보)
- `ProjectStatus` Enum (11개 상태)
- `ValuationPurpose` Enum (7개 목적)
- 필드: 회사 정보, 담당자 정보, 평가 정보, 배정 정보, 계약 정보
- Relationships: quotes, negotiations, documents, approval_points, valuation_results, drafts, reports

#### 4. backend/models/quote.py
- `Quote` 테이블 (견적서 정보)
- 필드: 견적 금액, 결제 조건, 포함 서비스, 유효 기간

#### 5. backend/models/negotiation.py
- `Negotiation` 테이블 (협의 내역)
- `NegotiationType` Enum (3개 유형)
- `RequesterType` Enum (customer, admin)

#### 6. backend/models/document.py
- `Document` 테이블 (업로드된 문서)
- `DocumentCategory` Enum (6개 카테고리)
- 필드: 파일명, 파일 크기, 저장 경로, 다운로드 URL

#### 7. backend/models/approval_point.py
- `ApprovalPoint` 테이블 (22개 판단 포인트)
- `ApprovalCategory` Enum (재무, 시장, 자산, 법률)
- `ImportanceLevel` Enum (high, medium, low)
- `ApprovalStatus` Enum (pending, approved, rejected, custom)
- 필드: AI 제안, 회계사 승인, 근거 문서, 영향 분석
- **복합 Primary Key**: (project_id, point_id)

#### 8. backend/models/valuation_result.py
- `ValuationResult` 테이블 (평가 결과)
- `ValuationMethod` Enum (5개 평가법)
- `CalculationStatus` Enum (pending, running, completed, failed, partial)
- 필드: 평가 결과 (JSONB), 민감도 분석, 주요 가정
- **복합 Primary Key**: (project_id, method)

#### 9. backend/models/draft.py
- `Draft` 테이블 (평가서 초안)
- 필드: 보고서 유형, 부록 포함 여부, 페이지 수, 다운로드 URL

#### 10. backend/models/revision.py
- `Revision` 테이블 (수정 요청)
- `RevisionType` Enum (3개 유형)
- 필드: 요청된 변경 사항 (JSONB), 사유, 근거 문서

#### 11. backend/models/report.py
- `Report` 테이블 (발행된 보고서)
- 필드: 보고서 유형, 파일 형식, 전달 방법, 발행 정보, 다운로드 횟수

#### 12. backend/database.py
- 데이터베이스 연결 설정
- `get_db()`: FastAPI 의존성 함수
- `create_tables()`: 테이블 생성 함수
- `drop_tables()`: 테이블 삭제 함수 (개발용)

#### 13. backend/.env.example + requirements.txt
- 환경 변수 예제
- Python 패키지 의존성 목록

---

### 테이블 구조 요약

| 테이블 | Primary Key | Foreign Key | 주요 필드 | 비고 |
|--------|------------|-------------|----------|------|
| **projects** | project_id | - | 회사 정보, 평가 정보, 배정 정보 | 중심 테이블 |
| **quotes** | quote_id | project_id | 견적 금액, 결제 조건 | 1:N |
| **negotiations** | negotiation_id | project_id | 협의 유형, 제안 내용 | 1:N |
| **documents** | file_id | project_id | 파일명, 카테고리, 저장 경로 | 1:N |
| **approval_points** | (project_id, point_id) | project_id | AI 제안, 회계사 승인 | 22개/프로젝트 |
| **valuation_results** | (project_id, method) | project_id | 평가 결과 (JSONB) | 5개/프로젝트 |
| **drafts** | draft_id | project_id | 초안 URL, 페이지 수 | 1:N |
| **revisions** | revision_id | project_id | 변경 요청 내용 (JSONB) | 1:N |
| **reports** | report_id | project_id | 보고서 URL, 발행 정보 | 1:N |

---

### 주요 특징

1. **Enum 타입 사용**: 상태, 카테고리 등에 Enum 활용
2. **JSONB 필드**: 유연한 데이터 구조 (approval_points, valuation_results, revisions)
3. **ARRAY 필드**: 배열 데이터 저장 (valuation_methods, included_services)
4. **복합 Primary Key**: approval_points, valuation_results
5. **Cascade Delete**: 프로젝트 삭제 시 관련 데이터 자동 삭제
6. **TimestampMixin**: 모든 테이블에 created_at, updated_at 자동 추가
7. **Relationships**: SQLAlchemy ORM 관계 정의

---

### 다음 단계

1. **FastAPI 라우터 구현**
   - 프로젝트 관리 라우터 (생성, 견적, 협의, 승인)
   - 자료 수집 라우터 (문서 업로드, AI 추출, 자동 수집)
   - 평가 라우터 (계산, 미리보기, 시뮬레이션)
   - 승인 포인트 라우터 (조회, 승인)
   - 초안/수정 라우터
   - 보고서 라우터

2. **CRUD 유틸리티 함수 구현**
   - 프로젝트 CRUD
   - 판단 포인트 CRUD
   - 평가 결과 CRUD

3. **5가지 평가 엔진 통합**
   - dcf_engine.py (이미 존재)
   - relative_engine.py, asset_engine.py
   - capital_market_law_engine.py, inheritance_tax_law_engine.py

---

## 이전 작업: CSV to JSON Migration (2025-01-02)

### 작업 상태: ✅ 완료

## CSV to JSON Migration 작업 완료

### 작업 상태: ✅ 완료

### 작업 개요
Dev Package의 모든 CSV 관련 파일을 JSON 방식으로 변경하여 일반 사용자가 JSON 기반으로 프로젝트를 관리할 수 있도록 함.

---

### 변경된 폴더 구조

| Before | After |
|--------|-------|
| `method/csv/` | `method/json/` |
| `method/csv/data/in_progress/sal_grid.csv` | `method/json/data/in_progress/project_sal_grid.json` |
| `method/csv/data/completed/` | `method/json/data/completed/` |

---

### 수정된 파일 목록

#### 1. .claude/CLAUDE.md
- CSV 참조를 JSON으로 변경
- DB vs JSON 데이터 구분 설명 추가
- JSON 폴더 구조 설명 추가

#### 2. .claude/methods/01_json-crud.md
- CSV CRUD → JSON CRUD로 변경
- JSON 파일 경로 및 구조 설명

#### 3. .claude/rules/04_grid-writing-json.md
- CSV 작업 규칙을 JSON 작업 규칙으로 전면 변경
- JSON 파일 위치 및 CRUD 방법 설명
- Viewer 확인 방법 섹션 추가 (로컬 + GitHub Pages)

#### 4. .claude/rules/05_execution-process.md
- CSV 참조를 JSON으로 변경

#### 5. .claude/rules/07_task-crud.md
- Task CRUD 프로세스의 CSV 참조를 JSON으로 변경
- JSON 폴더 구조 설명 추가

#### 6. viewer/viewer_json.html (이전: viewer_csv.html)
- 타이틀: `Project SAL Grid Viewer (CSV)` → `Project SAL Grid Viewer (JSON)`
- 헤더 텍스트: 로컬 CSV 파일 기반 → 로컬 JSON 파일 기반
- fetch 경로 변경:
  - Before: `../method/csv/data/in_progress/sal_grid.csv`
  - After: `../method/json/data/in_progress/project_sal_grid.json`
- CSV 파싱 함수(`parseCSV`, `parseCSVLine`) 제거
- `response.json()` 방식으로 데이터 로드
- Stage Gate 관련 메시지 CSV → JSON

#### 7. viewer/viewer_mobile_json.html (이전: viewer_mobile_csv.html)
- 타이틀: `Project SAL Grid Viewer - Mobile (CSV)` → `Project SAL Grid Viewer - Mobile (JSON)`
- 헤더 텍스트: `SAL Grid Viewer (CSV)` → `SAL Grid Viewer (JSON)`
- fetch 경로 변경:
  - Before: `../method/csv/data/sal_grid.csv`
  - After: `../method/json/data/in_progress/project_sal_grid.json`
- CSV 파싱 함수 제거
- `response.json()` 방식으로 데이터 로드

---

### JSON 파일 구조

```json
{
  "project_id": "프로젝트ID",
  "project_name": "프로젝트명",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "tasks": [
    {
      "task_id": "S1F1",
      "task_name": "Task 이름",
      "stage": 1,
      "area": "F",
      "task_status": "Pending",
      "task_progress": 0,
      "verification_status": "Not Verified",
      ...22개 속성
    }
  ]
}
```

---

### 핵심 변경 사항

1. **데이터 형식**: CSV → JSON
2. **파싱 방식**: `parseCSV()` 함수 → `response.json()`
3. **파일 경로**: `method/csv/` → `method/json/`
4. **파일명**: `sal_grid.csv` → `project_sal_grid.json`

---

### 비고

- DB Method는 SSAL Works 예시용으로 유지 (viewer_database.html)
- 일반 사용자는 JSON Method 사용 (viewer_json.html)
- Viewer는 `method/json/data/in_progress/` 폴더의 JSON 파일을 로드

---

### 관련 리포트
`Human_ClaudeCode_Bridge/Reports/csv_to_json_migration_report.json`
