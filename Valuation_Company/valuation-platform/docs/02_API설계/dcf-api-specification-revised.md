# DCF 평가법 API 명세서 (Revised)

> 작성일: 2026-01-20
> 기반: 실제 프론트엔드 HTML 파일 (project-create.html, project-dashboard.html, project-detail.html, dcf-portal.html, dcf-valuation.html)

---

## 📐 프로젝트 번호 형식

```
{5자리 회사코드}-{YYMMDDHHmm}-{2자리 평가법코드}

예시: SAMSU-2501191430-DC

구성:
- 회사코드 (5자리): 영문명에서 특수문자 제거 후 앞 5자 (부족하면 X로 채움)
- 타임코드 (10자리): 생성 시점 YYMMDDHHmm
- 평가법 코드 (2자리): DC(DCF), RV(상대가치), IP(IPO), AV(자산가치), TX(상증법)
```

**생성 로직** (project-create.html 참조):
```javascript
function getCompanyCode(englishName) {
    const cleaned = englishName.replace(/[^a-zA-Z]/g, '').toUpperCase();
    return cleaned.substring(0, 5).padEnd(5, 'X');
}
// "Samsung Electronics" → "SAMSU"
// "ABC" → "ABCXX"
```

---

## 🔄 프로젝트 상태 (Status)

| 코드 | 한글 | 설명 | 단계 |
|------|------|------|------|
| `collecting` | 자료 수집중 | 고객이 dcf-portal.html에서 자료 제출 중 | 2 |
| `reviewing` | 검토중 | 회계사가 제출된 자료 검토 중 | 3 |
| `evaluating` | 평가 진행중 | 회계사가 dcf-valuation.html에서 WACC/FCFF 입력 중 | 4-5 |
| `completed` | 완료 | 평가 완료, 보고서 발행 가능 | 6 |

---

## 📊 워크플로우 (6단계)

```
[1단계] 프로젝트 생성 (회계사)
    Frontend: project-create.html
    API: POST /projects
         ↓
[2단계] 자료 수집 (고객)
    Frontend: dcf-portal.html
    API: POST /projects/{id}/documents
    Status: collecting
         ↓
[3단계] 자료 검토 (회계사)
    Frontend: project-detail.html
    API: GET /projects/{id}/documents
    Status: reviewing
         ↓
[4단계] 평가 입력 (회계사)
    Frontend: dcf-valuation.html
    API: POST /projects/{id}/wacc
         POST /projects/{id}/fcff
    Status: evaluating
         ↓
[5단계] 평가 실행 (AI)
    Frontend: dcf-valuation.html (결과 표시)
    API: POST /projects/{id}/calculate
         ↓
[6단계] 보고서 발행
    Frontend: project-detail.html
    API: POST /projects/{id}/report
    Status: completed
```

---

## API 엔드포인트 목록

| # | Method | Endpoint | 설명 | Frontend |
|---|--------|----------|------|----------|
| 1 | POST | /projects | 프로젝트 생성 | project-create.html |
| 2 | GET | /projects | 프로젝트 목록 조회 | project-dashboard.html |
| 3 | GET | /projects/{id} | 프로젝트 상세 조회 | project-detail.html |
| 4 | POST | /projects/{id}/documents | 파일 업로드 | dcf-portal.html |
| 5 | GET | /projects/{id}/documents | 파일 목록 조회 | project-detail.html |
| 6 | DELETE | /projects/{id}/documents/{fileId} | 파일 삭제 | project-detail.html |
| 7 | POST | /projects/{id}/wacc | WACC 계산 | dcf-valuation.html |
| 8 | POST | /projects/{id}/fcff | FCFF 입력 | dcf-valuation.html |
| 9 | POST | /projects/{id}/calculate | DCF 계산 실행 | dcf-valuation.html |
| 10 | GET | /projects/{id}/result | 평가 결과 조회 | dcf-valuation.html |

---

## 1️⃣ 프로젝트 생성 API

### POST /projects

**Frontend**: `project-create.html`

**Request**:
```json
{
  "company_name_kr": "삼성전자",
  "company_name_en": "Samsung Electronics",
  "business_number": "124-81-00998",
  "ceo_name": "이재용",
  "industry": "전자제품 제조업",
  "founded_date": "1969-01-13",
  "contact_name": "김담당",
  "contact_email": "contact@samsung.com",
  "valuation_method": "DC",
  "valuation_date": "2025-01-01",
  "purpose": "investment",
  "requirements": "특별 고려사항",
  "assigned_accountant": "kim",
  "reviewer": "choi"
}
```

**Response** (201):
```json
{
  "project_id": "SAMSU-2501191430-DC",
  "status": "collecting",
  "created_at": "2025-01-19T14:30:00Z",
  "customer_portal_url": "https://valuelink.com/portal/SAMSU-2501191430-DC",
  "submission_deadline": "2025-01-26"
}
```

---

## 2️⃣ 프로젝트 목록 조회 API

### GET /projects

**Frontend**: `project-dashboard.html`

**Query Parameters**:
- `status` (optional): collecting | reviewing | evaluating | completed
- `search` (optional): 회사명 또는 프로젝트 번호
- `page` (optional): 페이지 번호
- `limit` (optional): 페이지당 항목 수

**Response**:
```json
{
  "total": 24,
  "page": 1,
  "limit": 20,
  "projects": [
    {
      "project_id": "SAMSU-2501191430-DC",
      "company_name": "삼성전자",
      "industry": "전자제품 제조업",
      "method": "DCF",
      "method_code": "DC",
      "status": "collecting",
      "progress": 30,
      "assigned_accountant": {
        "id": "kim",
        "name": "김철수"
      },
      "valuation_date": "2025-01-01",
      "created_at": "2025-01-19T14:30:00Z"
    }
  ]
}
```

---

## 3️⃣ 프로젝트 상세 조회 API

### GET /projects/{project_id}

**Frontend**: `project-detail.html`

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-DC",
  "company_name": "삼성전자",
  "business_number": "124-81-00998",
  "ceo_name": "이재용",
  "industry": "전자제품 제조업",
  "status": "collecting",
  "current_step": 2,
  "steps": [
    {"step": 1, "name": "프로젝트 생성", "status": "completed"},
    {"step": 2, "name": "자료 수집", "status": "in_progress"},
    {"step": 3, "name": "자료 검토", "status": "pending"},
    {"step": 4, "name": "평가 입력", "status": "pending"},
    {"step": 5, "name": "평가 실행", "status": "pending"},
    {"step": 6, "name": "보고서", "status": "pending"}
  ],
  "valuation_date": "2025-01-01",
  "purpose": "investment",
  "assigned_accountant": {"id": "kim", "name": "김철수"},
  "customer_portal_url": "https://valuelink.com/portal/SAMSU-2501191430-DC",
  "submission_deadline": "2025-01-26"
}
```

---

## 4️⃣ 파일 업로드 API

### POST /projects/{project_id}/documents

**Frontend**: `dcf-portal.html`, `project-detail.html`

**Request** (multipart/form-data):
```
category: "financial" | "business_plan" | "shareholder" | "capex" | "working_capital" | "others"
files: File[]
description: string (others 카테고리 전용, 필수)
```

**카테고리 설명**:
| 카테고리 | 한글명 | 필수 여부 | 파일 개수 |
|----------|--------|-----------|-----------|
| `financial` | 재무제표 (3개년) | 필수 | 다수 가능 |
| `business_plan` | 사업계획서 (5개년) | 필수 | 다수 가능 |
| `shareholder` | 주주명부 | 필수 | 다수 가능 |
| `capex` | CAPEX 계획 | 선택 | 다수 가능 |
| `working_capital` | 운전자본 계획 | 선택 | 다수 가능 |
| `others` | 기타 자료 | 선택 | **최대 5개** |

**파일 제약**:
```
허용 확장자: .pdf, .jpg, .jpeg, .png, .txt, .csv, .json, .xml, .md, .html, .zip,
             .doc, .docx, .xls, .xlsx, .ppt, .pptx, .gif, .webp, .bmp

금지 확장자: .hwp (PDF로 변환 필요)

파일 크기:
- 개별 파일: 최대 20MB
- 전체 (others 카테고리): 최대 100MB
```

**파일명 규칙 (others 카테고리)**:
```
{프로젝트ID}_ETC{순번}.{확장자}

예시:
- SAMSU-2501191430-DC_ETC1.pdf
- SAMSU-2501191430-DC_ETC2.xlsx
- SAMSU-2501191430-DC_ETC3.pdf
```

**Response** (201):
```json
{
  "uploaded_files": [
    {
      "file_id": "doc_f8a3c2d1",
      "file_name": "재무제표_2023.pdf",
      "stored_name": "SAMSU-2501191430-DC_ETC1.pdf",
      "category": "financial",
      "size": 2500000,
      "description": "핵심 기술 관련 특허등록증",
      "uploaded_at": "2025-01-19T15:00:00Z"
    }
  ]
}
```

---

## 5️⃣ 파일 목록 조회 API

### GET /projects/{project_id}/documents

**Frontend**: `project-detail.html`, `dcf-portal.html`

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-DC",
  "documents": {
    "financial": [
      {
        "file_id": "doc_001",
        "file_name": "재무제표_2023.pdf",
        "size": 2500000,
        "uploaded_at": "2025-01-19T15:00:00Z",
        "status": "uploaded"
      }
    ],
    "business_plan": [],
    "shareholder": [],
    "capex": [],
    "working_capital": [],
    "others": [
      {
        "file_id": "doc_etc1",
        "file_name": "SAMSU-2501191430-DC_ETC1.pdf",
        "description": "핵심 기술 관련 특허등록증",
        "size": 2500000,
        "uploaded_at": "2025-01-19T15:00:00Z",
        "status": "uploaded"
      }
    ]
  },
  "summary": {
    "total_count": 3,
    "required_count": 3,
    "required_completed": 1,
    "others_count": 1,
    "others_max": 5
  }
}
```

---

## 6️⃣ 파일 삭제 API

### DELETE /projects/{project_id}/documents/{file_id}

**Frontend**: `project-detail.html`

**Response** (204 No Content)

---

## 7️⃣ WACC 계산 API

### POST /projects/{project_id}/wacc

**Frontend**: `dcf-valuation.html`

**Request**:
```json
{
  "risk_free_rate": 3.5,
  "market_risk_premium": 6.0,
  "levered_beta": 1.2,
  "size_premium": 2.0,
  "cost_of_debt": 5.0,
  "tax_rate": 22.0,
  "equity_ratio": 70.0,
  "debt_ratio": 30.0
}
```

**Response**:
```json
{
  "wacc": 12.87,
  "cost_of_equity": 13.7,
  "after_tax_cost_of_debt": 3.9,
  "breakdown": {
    "equity_component": 9.59,
    "debt_component": 1.17
  }
}
```

**계산 공식**:
```
Ke (자기자본비용) = Rf + β × MRP + Size Premium
Kd (세후 타인자본비용) = Cost of Debt × (1 - Tax Rate)

WACC = (Ke × Equity%) + (Kd × Debt%)
```

---

## 8️⃣ FCFF 입력 API

### POST /projects/{project_id}/fcff

**Frontend**: `dcf-valuation.html`

**Request**:
```json
{
  "years": [
    {
      "year": "2026E",
      "revenue": 100000,
      "ebit": 15000,
      "tax_rate": 22.0,
      "nopat": 11700,
      "depreciation": 2000,
      "capex": 3000,
      "working_capital_change": 500,
      "fcff": 10200,
      "discount_period": 0.5
    },
    {
      "year": "2027E",
      "revenue": 110000,
      "ebit": 17000,
      "tax_rate": 22.0,
      "nopat": 13260,
      "depreciation": 2200,
      "capex": 3300,
      "working_capital_change": 600,
      "fcff": 11560,
      "discount_period": 1.5
    }
  ],
  "terminal_value": {
    "terminal_fcff": 12000,
    "terminal_growth_rate": 2.5
  }
}
```

**Response** (201):
```json
{
  "project_id": "SAMSU-2501191430-DC",
  "fcff_saved": true,
  "years_count": 5,
  "terminal_value_set": true
}
```

---

## 9️⃣ DCF 계산 실행 API

### POST /projects/{project_id}/calculate

**Frontend**: `dcf-valuation.html`

**Request**:
```json
{
  "shares_outstanding": 1000000
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-DC",
  "valuation_date": "2025-01-01",
  "wacc": 12.87,
  "terminal_growth_rate": 2.5,
  "pv_fcff": 50720000,
  "pv_terminal_value": 107780000,
  "enterprise_value": 158500000,
  "net_debt": 0,
  "equity_value": 158500000,
  "shares_outstanding": 1000000,
  "value_per_share": 158.50,
  "terminal_value_percentage": 68.0,
  "fcff_details": [
    {
      "year": "2026E",
      "fcff": 10200,
      "discount_factor": 0.9428,
      "pv_fcff": 9616
    },
    {
      "year": "2027E",
      "fcff": 11560,
      "discount_factor": 0.8351,
      "pv_fcff": 9654
    }
  ]
}
```

---

## 🔟 평가 결과 조회 API

### GET /projects/{project_id}/result

**Frontend**: `dcf-valuation.html`

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-DC",
  "company_name": "삼성전자",
  "valuation_date": "2025-01-01",
  "enterprise_value": 158500000,
  "equity_value": 158500000,
  "value_per_share": 158.50,
  "wacc": 12.87,
  "terminal_growth_rate": 2.5,
  "pv_fcff": 50720000,
  "pv_terminal_value": 107780000,
  "terminal_value_percentage": 68.0,
  "fcff_projections": [...],
  "calculated_at": "2025-01-20T10:30:00Z",
  "status": "completed"
}
```

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 (필수 필드 누락, 형식 오류) |
| 401 | 인증 필요 |
| 403 | 권한 없음 (다른 회계사의 프로젝트 접근) |
| 404 | 프로젝트를 찾을 수 없음 |
| 409 | 상태 충돌 (잘못된 워크플로우 순서) |
| 413 | 파일 크기 초과 |
| 415 | 지원하지 않는 파일 형식 |
| 500 | 서버 내부 오류 |

**에러 응답 형식**:
```json
{
  "error": "FILE_SIZE_EXCEEDED",
  "message": "파일 크기는 20MB를 초과할 수 없습니다.",
  "details": {
    "file_name": "report.pdf",
    "file_size": 25000000,
    "max_size": 20971520
  }
}
```

---

## 다음 단계

1. ✅ API 명세서 작성 완료
2. ⏳ Pydantic 스키마 정의 (Request/Response 모델)
3. ⏳ Database 모델 정의 (SQLAlchemy)
4. ⏳ FastAPI 라우터 구현
5. ⏳ dcf_engine.py 통합
6. ⏳ 파일 업로드 로직 구현 (S3 or Local)
7. ⏳ 프론트엔드 연동 테스트
