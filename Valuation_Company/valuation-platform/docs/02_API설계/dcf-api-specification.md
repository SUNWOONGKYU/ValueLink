# DCF 평가법 API 명세서

> 작성일: 2026-01-20
> 상태: 설계
> 기반: 프론트엔드 HTML (project-create.html, project-detail.html, dcf-portal.html, dcf-valuation.html)

---

## API 엔드포인트 구조

### 기본 URL
```
BASE_URL: /api/v1/valuations/dcf
```

---

## 프로젝트 번호 형식

```
{5자리 회사코드}-{YYMMDDHHmm}-{2자리 평가법코드}

예시: SAMSU-2501191430-DC

- 회사코드 (5자리): 영문 회사명에서 추출 (부족하면 X로 채움)
- 타임코드 (10자리): 생성 시점 (연월일시분)
- 평가법 코드 (2자리): DC (DCF), RV (상대가치), IP (IPO), AV (자산가치), TX (상증법)
```

---

## 프로젝트 상태 (Status)

| 상태 코드 | 한글명 | 설명 |
|----------|--------|------|
| `collecting` | 자료 수집중 | 고객이 자료 제출 중 |
| `reviewing` | 검토중 | 회계사가 자료 검토 중 |
| `evaluating` | 평가 진행중 | WACC/FCFF 입력 및 계산 중 |
| `completed` | 완료 | 평가 완료 및 보고서 발행 |

---

## 워크플로우 (6단계)

```
1. 프로젝트 생성 (회계사)
        ↓
2. 자료 수집 (고객) → status: collecting
        ↓
3. 자료 검토 (회계사) → status: reviewing
        ↓
4. 평가 입력 (회계사) → status: evaluating
        ↓
5. 평가 실행 (AI)
        ↓
6. 보고서 발행 → status: completed
```

---

## 1. 프로젝트 생성 API

### POST /projects

**설명**: 회계사가 신규 DCF 평가 프로젝트 생성

**Frontend**: project-create.html

**Request Body**:
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

**Response** (201 Created):
```json
{
  "project_id": "SAMSU-2501191430-DC",
  "status": "collecting",
  "created_at": "2026-01-19T14:30:00Z",
  "customer_portal_url": "https://valuelink.com/portal/SAMSU-2501191430-DC"
}
```

---

## 2. 프로젝트 상태 조회 API

### GET /projects/{project_id}

**설명**: 프로젝트 현재 상태 및 진행 단계 조회

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "company_name": "ABC기업",
  "status": "APPROVED",
  "current_step": 4,
  "steps": [
    {"step": 1, "name": "안내문 보기", "status": "completed"},
    {"step": 2, "name": "평가 요청", "status": "completed"},
    {"step": 3, "name": "관리자 승인", "status": "completed"},
    {"step": 4, "name": "자료 제출", "status": "in_progress"},
    {"step": 5, "name": "결과 미리보기", "status": "pending"}
  ]
}
```

---

## 3. 자료 업로드 API

### POST /projects/{project_id}/documents

**설명**: 필요 서류 업로드 (재무제표, 사업계획서, 주주명부)

**User Flow**: Step 4

**Request** (multipart/form-data):
```
financial_statements: File[] (최근 3년 재무제표)
business_plan: File (향후 5년 사업계획서)
shareholder_list: File (주주명부)
other_documents: File[] (선택)
```

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "uploaded_files": [
    {
      "file_id": "doc_001",
      "file_name": "재무제표_2023.pdf",
      "file_type": "financial_statements",
      "uploaded_at": "2026-01-20T11:00:00Z"
    }
  ],
  "status": "DOCUMENTS_SUBMITTED"
}
```

---

## 4. AI 데이터 추출 API

### POST /projects/{project_id}/extract

**설명**: 업로드된 서류에서 AI가 데이터 자동 추출

**DCF Workflow**: Step 1-4

**Request Body**:
```json
{
  "extraction_type": "full",
  "use_ocr": true,
  "validate_data": true
}
```

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "extraction_status": "completed",
  "extracted_data": {
    "company_info": {
      "company_name": "ABC기업",
      "fiscal_year_end": "12-31"
    },
    "financial_data": {
      "revenue_2021": 50000000000,
      "revenue_2022": 55000000000,
      "revenue_2023": 60000000000,
      "ebit_2023": 10000000000
    },
    "projections": {
      "revenue_growth_rate": 0.08,
      "ebit_margin": 0.15
    }
  },
  "missing_fields": [
    "beta_coefficient",
    "market_risk_premium"
  ]
}
```

---

## 5. AI 자동 수집 API

### POST /projects/{project_id}/auto-collect

**설명**: AI가 외부 API에서 필요 데이터 자동 수집 (무위험이자율, 베타, 시장위험프리미엄)

**DCF Workflow**: Step 3 (C 유형 데이터 42%)

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "collected_data": {
    "risk_free_rate": 0.035,
    "risk_free_rate_source": "한국은행 API (3년 국고채)",
    "industry_beta": 1.15,
    "industry_beta_source": "KOSPI 제조업 평균",
    "market_risk_premium": 0.065,
    "market_risk_premium_source": "Damodaran 한국 MRP"
  }
}
```

---

## 6. WACC 시나리오 생성 API

### GET /projects/{project_id}/wacc-scenarios

**설명**: 3가지 WACC 시나리오 자동 생성 (낙관/중립/보수)

**DCF Workflow**: Step 5

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "scenarios": [
    {
      "scenario_id": "wacc_optimistic",
      "scenario_name": "낙관적 시나리오",
      "wacc": 0.095,
      "components": {
        "cost_of_equity": 0.105,
        "cost_of_debt": 0.04,
        "equity_weight": 0.70,
        "debt_weight": 0.30
      }
    },
    {
      "scenario_id": "wacc_neutral",
      "scenario_name": "중립적 시나리오",
      "wacc": 0.112,
      "components": {
        "cost_of_equity": 0.120,
        "cost_of_debt": 0.045,
        "equity_weight": 0.65,
        "debt_weight": 0.35
      }
    },
    {
      "scenario_id": "wacc_conservative",
      "scenario_name": "보수적 시나리오",
      "wacc": 0.135,
      "components": {
        "cost_of_equity": 0.145,
        "cost_of_debt": 0.05,
        "equity_weight": 0.60,
        "debt_weight": 0.40
      }
    }
  ]
}
```

---

## 7. WACC 승인 API

### POST /projects/{project_id}/wacc-approve

**설명**: 평가자가 3가지 WACC 시나리오 중 하나를 선택

**DCF Workflow**: Step 6 (평가자 승인 1/3)

**Request Body**:
```json
{
  "approved_scenario_id": "wacc_neutral",
  "evaluator_notes": "중립적 시나리오가 적정하다고 판단함"
}
```

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "approved_wacc": 0.112,
  "approval_status": "wacc_approved",
  "approved_at": "2026-01-20T14:00:00Z"
}
```

---

## 8. DCF 계산 실행 API

### POST /projects/{project_id}/calculate

**설명**: 승인된 WACC로 DCF 계산 실행 (FCFF, Terminal Value, NPV)

**DCF Workflow**: Step 7

**Request Body**:
```json
{
  "calculation_type": "full",
  "include_sensitivity": true
}
```

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "calculation_status": "completed",
  "enterprise_value": 152300000000,
  "equity_value": 152300000000,
  "value_per_share": 15230,
  "calculation_details": {
    "pv_fcff": 50720000000,
    "pv_terminal_value": 107780000000,
    "terminal_value_percentage": 0.68
  }
}
```

---

## 9. 결과 미리보기 API

### GET /projects/{project_id}/preview

**설명**: AI 평가 결과 미리보기 (민감도 분석 포함)

**User Flow**: Step 5

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "enterprise_value": 152300000000,
  "equity_value": 152300000000,
  "value_per_share": 15230,
  "key_assumptions": {
    "wacc": 0.112,
    "terminal_growth_rate": 0.025,
    "forecast_period": 5
  },
  "sensitivity_analysis": {
    "wacc_range": [0.10, 0.11, 0.12],
    "growth_range": [0.02, 0.025, 0.03],
    "value_matrix": [
      [148000000000, 162000000000],
      [135000000000, 147000000000],
      [124000000000, 134000000000]
    ]
  }
}
```

---

## 10. 시뮬레이션 실행 API

### POST /projects/{project_id}/simulate

**설명**: 가정 변경 시뮬레이션 (매출성장률, 영업이익률, WACC 조정)

**User Flow**: Step 5 (시뮬레이션 기능)

**Request Body**:
```json
{
  "modified_assumptions": {
    "revenue_growth_rate": 0.05,
    "ebit_margin": 0.15,
    "wacc": 0.112
  }
}
```

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "original_value": 152300000000,
  "simulated_value": 145800000000,
  "change_percentage": -0.043,
  "impact_breakdown": {
    "revenue_growth_impact": -4500000000,
    "ebit_margin_impact": 0,
    "wacc_impact": -2000000000
  }
}
```

---

## 11. 수정 요청 API

### POST /projects/{project_id}/revisions

**설명**: 평가 결과에 대한 수정 요청 (가정/파라미터 변경)

**User Flow**: Step 6

**Request Body**:
```json
{
  "revision_type": "assumption_change",
  "requested_changes": {
    "wacc": 0.105,
    "terminal_growth_rate": 0.03
  },
  "reason": "시장 상황 반영",
  "supporting_documents": ["doc_123"]
}
```

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "revision_id": "REV-001",
  "status": "revision_requested",
  "estimated_completion": "2026-01-21T10:00:00Z"
}
```

---

## 12. 최종 확정 API

### POST /projects/{project_id}/finalize

**설명**: 평가 결과 최종 확정

**DCF Workflow**: Step 8 (평가자 승인 2/3)

**Request Body**:
```json
{
  "final_approval": true,
  "evaluator_comments": "평가 결과 확정 승인"
}
```

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "final_enterprise_value": 158500000000,
  "final_equity_value": 158500000000,
  "final_value_per_share": 15850,
  "status": "FINALIZED",
  "finalized_at": "2026-01-20T16:00:00Z"
}
```

---

## 13. 보고서 발행 요청 API

### POST /projects/{project_id}/report

**설명**: 공식 평가 보고서 발행 요청

**User Flow**: Step 8

**Request Body**:
```json
{
  "report_type": "formal",
  "delivery_format": "pdf",
  "delivery_method": "download"
}
```

**Response**:
```json
{
  "project_id": "PRJ-0047",
  "report_id": "RPT-0047-001",
  "report_url": "https://api.valuelink.com/reports/RPT-0047-001.pdf",
  "status": "REPORT_ISSUED",
  "issued_at": "2026-01-20T17:00:00Z"
}
```

---

## 프로젝트 상태 흐름

```
REQUESTED (요청됨)
    ↓
APPROVED (승인됨)
    ↓
DOCUMENTS_SUBMITTED (자료 제출 완료)
    ↓
DATA_EXTRACTED (데이터 추출 완료)
    ↓
WACC_APPROVED (WACC 승인)
    ↓
ANALYSIS_COMPLETE (분석 완료)
    ↓
REVISION_REQUESTED (수정 요청, 선택) → ANALYSIS_COMPLETE (재분석)
    ↓
FINALIZED (최종 확정)
    ↓
REPORT_ISSUED (보고서 발행)
```

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 (필수 필드 누락, 형식 오류) |
| 401 | 인증 필요 |
| 403 | 권한 없음 (승인되지 않은 프로젝트 접근) |
| 404 | 프로젝트를 찾을 수 없음 |
| 409 | 상태 충돌 (잘못된 프로세스 순서) |
| 500 | 서버 내부 오류 |

---

## 다음 단계

1. **Pydantic 스키마 정의** (Request/Response 모델)
2. **Database 모델 정의** (SQLAlchemy)
3. **FastAPI 라우터 구현**
4. **DCF 엔진 통합**
5. **프론트엔드 연동**
