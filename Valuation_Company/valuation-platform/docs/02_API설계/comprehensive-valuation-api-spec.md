# 종합 기업가치평가 API 명세서

> 작성일: 2026-01-20
> 상태: 설계 (v2.0 - 프로세스 수정)
> 기반: 기존 연구 (MASTER_PLAN, INPUT_DATA_CLASSIFICATION, ARCHITECTURE.md) + 프론트엔드 HTML

---

## API 엔드포인트 구조

### 기본 URL
```
BASE_URL: /api/v1/valuations
```

---

## 프로젝트 번호 형식

```
{5자리 회사코드}-{YYMMDDHHmm}-{2자리 평가법코드}

예시: SAMSU-2501191430-DC

- 회사코드 (5자리): 영문 회사명에서 추출 (부족하면 X로 채움)
- 타임코드 (10자리): 생성 시점 (연월일시분)
- 평가법 코드 (2자리):
  * DC (DCF평가법)
  * RV (상대가치평가법)
  * AV (자산가치평가법)
  * IV (본질가치평가법, Intrinsic Value)
  * TX (상증세법평가법)
  * CP (종합평가, Comprehensive)
```

---

## 프로젝트 상태 (Status)

| 상태 코드 | 한글명 | 설명 | 담당자 |
|----------|--------|------|--------|
| `requested` | 평가 신청 | 고객 신청 완료 | 고객 |
| `quote_sent` | 견적 발송 | 견적서 발송 완료 | 관리자 |
| `negotiating` | 조건 협의 중 | 조건 협의 중 | 관리자 ↔ 고객 |
| `approved` | 승인 완료 | 계약 확정, 회계사 배정 | 관리자 |
| `documents_uploaded` | 자료 업로드 | 고객 자료 업로드 완료 | 고객 |
| `collecting` | 자료 수집 중 | AI 자료 수집 중 | 시스템 |
| `evaluating` | 평가 진행 중 | 평가 계산 중 | AI |
| `human_approval` | 회계사 승인 대기 | 22개 판단 포인트 검토 | 회계사 |
| `draft_generated` | 초안 생성 완료 | 평가서 초안 생성 | 시스템 |
| `revision_requested` | 수정 요청 | 고객 수정 요청 | 고객 |
| `completed` | 최종 확정 | 평가 보고서 확정 | 회계사 |

---

## 5가지 평가법 코드

| 코드 | 평가법 | 영문명 | 적용 상황 |
|------|--------|--------|----------|
| `dcf` | DCF평가법 | Discounted Cash Flow | M&A, 투자유치 |
| `relative` | 상대가치평가법 | Relative Valuation | IPO, 빠른 의사결정 |
| `asset` | 자산가치평가법 | Net Asset Value | 부동산/지주회사, 청산 |
| `capital_market_law` | 본질가치평가법 | Intrinsic Value (Capital Market Law) | 합병, 분할, 주식매수청구권 |
| `inheritance_tax_law` | 상증세법평가법 | Inheritance Tax Law | 상속세, 증여세 신고 |

---

## 워크플로우 (11단계)

```
1. 고객 평가 신청 (프로젝트 등록)
   → status: requested
        ↓
2. 관리자 견적서 발송
   → status: quote_sent
        ↓
3. 조건 협의
   → status: negotiating
        ↓
4. 계약 확정 + 회계사 배정
   → status: approved
        ↓
5. 고객 자료 업로드 (6개 카테고리)
   → status: documents_uploaded
        ↓
6. AI/시스템 자료 수집 (외부 API 연동)
   → status: collecting
        ↓
7. 평가 진행 (5가지 평가법 실행)
   → status: evaluating
        ↓
8. 회계사 판단 포인트 승인 (22개)
   → status: human_approval
        ↓
9. 평가서 초안 생성
   → status: draft_generated
        ↓
10. 고객 수정 요청 (선택)
   → status: revision_requested (→ evaluating 재진행)
        ↓
11. 평가 보고서 최종 확정
   → status: completed
```

---

## 1. 고객 평가 신청 API (프로젝트 생성)

### POST /projects

**설명**: 고객이 평가 신청 (프로젝트 즉시 등록, 프로젝트 번호 생성)

**Request Body**:
```json
{
  "company_info": {
    "company_name_kr": "삼성전자",
    "company_name_en": "Samsung Electronics",
    "business_number": "124-81-00998",
    "ceo_name": "이재용",
    "industry": "전자제품 제조업",
    "industry_code": "C26",
    "founded_date": "1969-01-13",
    "is_listed": true,
    "ticker": "005930",
    "shares_outstanding": 5920370000
  },
  "contact": {
    "name": "김담당",
    "email": "contact@samsung.com",
    "phone": "02-1234-5678"
  },
  "valuation": {
    "methods": ["dcf", "relative", "asset"],
    "purpose": "MA",
    "valuation_date": "2025-01-01",
    "requirements": "특별 고려사항"
  }
}
```

**평가 목적 (purpose) 코드**:
| 코드 | 의미 | 권장 평가법 조합 |
|------|------|-----------------|
| `MA` | M&A | dcf, relative, asset |
| `IPO` | 기업공개 | relative, dcf |
| `investment` | 투자유치 | dcf, relative |
| `merger` | 합병 | capital_market_law |
| `inheritance` | 상속/증여 | inheritance_tax_law |
| `liquidation` | 청산 | asset |
| `comprehensive` | 종합 평가 | 5가지 전부 |

**Response** (201 Created):
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "requested",
  "created_at": "2026-01-19T14:30:00Z",
  "customer_portal_url": "https://valuelink.com/portal/SAMSU-2501191430-CP",
  "methods": ["dcf", "relative", "asset", "capital_market_law", "inheritance_tax_law"],
  "message": "평가 신청이 접수되었습니다. 견적서를 발송해드리겠습니다."
}
```

---

## 2. 견적서 발송 API

### POST /projects/{project_id}/quote

**설명**: 관리자가 견적서 발송

**Request Body**:
```json
{
  "quote_amount": 1500000,
  "currency": "KRW",
  "estimated_duration": "7 days",
  "payment_terms": "계약금 50% + 완료 후 50%",
  "included_services": [
    "5가지 평가법 종합 평가",
    "80페이지 종합 보고서",
    "민감도 분석",
    "1회 무료 수정"
  ],
  "valid_until": "2026-01-27",
  "notes": "추가 요청사항이 있으시면 협의 가능합니다."
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "quote_sent",
  "quote_id": "QT-SAMSU-001",
  "quote_url": "https://valuelink.com/quotes/QT-SAMSU-001.pdf",
  "sent_at": "2026-01-19T15:00:00Z",
  "valid_until": "2026-01-27T00:00:00Z"
}
```

---

## 3. 조건 협의 API

### POST /projects/{project_id}/negotiate

**설명**: 관리자 ↔ 고객 조건 협의

**Request Body**:
```json
{
  "negotiation_type": "price_adjustment" | "scope_change" | "timeline_change",
  "proposed_amount": 1200000,
  "proposed_scope": ["dcf", "relative", "asset"],
  "message": "예산 내에서 3가지 평가법으로 조정 가능할까요?",
  "requester": "customer" | "admin"
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "negotiating",
  "negotiation_id": "NEG-001",
  "updated_at": "2026-01-19T16:00:00Z",
  "pending_response_from": "admin"
}
```

---

## 4. 계약 확정 및 회계사 배정 API

### POST /projects/{project_id}/approve

**설명**: 관리자가 계약 확정 및 회계사 배정

**Request Body**:
```json
{
  "final_amount": 1500000,
  "final_scope": ["dcf", "relative", "asset", "capital_market_law", "inheritance_tax_law"],
  "payment_terms": "계약금 50% + 완료 후 50%",
  "assigned_accountant": "kim@company.com",
  "reviewer": "choi@company.com",
  "contract_signed": true,
  "contract_date": "2026-01-20"
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "approved",
  "assigned_accountant": {
    "email": "kim@company.com",
    "name": "김회계사",
    "specialization": ["DCF", "상대가치"]
  },
  "reviewer": {
    "email": "choi@company.com",
    "name": "최검토자"
  },
  "approved_at": "2026-01-20T10:00:00Z",
  "message": "계약이 확정되었습니다. 고객님께서 자료를 업로드해주시기 바랍니다."
}
```

---

## 5. 고객 자료 업로드 API

### POST /projects/{project_id}/documents

**설명**: 고객이 필요 서류 업로드 (6개 카테고리)

**Request** (multipart/form-data):
```
category: 'financial' | 'business_plan' | 'shareholder' | 'capex' | 'working_capital' | 'others'
files: File[]
```

**카테고리별 파일 요구사항**:
| 카테고리 | 한글명 | 필수 | 최대 파일 수 | 최대 크기 |
|----------|--------|------|-------------|----------|
| `financial` | 재무제표 | ✅ | 무제한 | 20MB/파일 |
| `business_plan` | 사업계획서 | ✅ | 무제한 | 20MB/파일 |
| `shareholder` | 주주명부 | ✅ | 무제한 | 20MB/파일 |
| `capex` | 자본적지출 | ⚪ | 무제한 | 20MB/파일 |
| `working_capital` | 운전자본 | ⚪ | 무제한 | 20MB/파일 |
| `others` | 기타 | ⚪ | 5개 | 100MB/전체 |

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "uploaded_files": [
    {
      "file_id": "doc_001",
      "file_name": "재무제표_2023.pdf",
      "category": "financial",
      "file_size": 15728640,
      "uploaded_at": "2026-01-20T11:00:00Z"
    }
  ],
  "upload_progress": {
    "financial": "completed",
    "business_plan": "completed",
    "shareholder": "completed",
    "capex": "pending",
    "working_capital": "pending",
    "others": "pending"
  },
  "status": "documents_uploaded",
  "message": "필수 서류 업로드가 완료되었습니다. AI 자료 수집을 시작합니다."
}
```

---

## 6. AI 데이터 추출 API

### POST /projects/{project_id}/extract

**설명**: 업로드된 서류에서 AI가 데이터 자동 추출

**Request Body**:
```json
{
  "extraction_type": "comprehensive",
  "use_ocr": true,
  "validate_data": true
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "extraction_status": "completed",
  "extracted_data": {
    "company": {
      "name": "삼성전자",
      "ticker": "005930",
      "is_listed": true,
      "industry": "전자제품 제조업",
      "shares_outstanding": 5920370000
    },
    "financials": {
      "revenue": [258937700, 243770400, 236806700, 229234200, 206205700],
      "ebit": [43372600, 47854000, 58886800, 61186600, 51630000],
      "net_income": [34451400, 26408100, 44344700, 39895100, 26263700],
      "capex": [28481900, 32784300, 48133000, 53625400, 43113600],
      "depreciation": [24336300, 27695200, 29095000, 30562900, 31747800]
    },
    "balance_sheet": {
      "total_assets": 378333900,
      "total_liabilities": 92970000,
      "equity": 285363900,
      "current_assets": 141482500,
      "fixed_assets": 184843200,
      "intangible_assets": 10285400,
      "investment_assets": 41722800
    },
    "capital_structure": {
      "debt": 97018900,
      "interest_bearing_debt": 46707100,
      "cash": 56678500
    }
  },
  "confidence_scores": {
    "financials": 0.95,
    "balance_sheet": 0.92,
    "capital_structure": 0.88
  }
}
```

---

## 7. AI 자동 수집 API

### POST /projects/{project_id}/auto-collect

**설명**: AI가 외부 API에서 필요 데이터 자동 수집

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "collecting",
  "collected_data": {
    "market_data": {
      "risk_free_rate": 0.035,
      "risk_free_rate_source": "한국은행 API (3년 국고채, 2026-01-20)",
      "market_risk_premium": 0.065,
      "market_risk_premium_source": "역사적 평균 (1980-2025)"
    },
    "industry_data": {
      "industry_beta": 1.15,
      "industry_beta_source": "KOSPI 전자업종 평균",
      "industry_per": 18.5,
      "industry_pbr": 1.8,
      "industry_roe": 0.09
    },
    "comparable_companies": [
      {
        "name": "SK하이닉스",
        "ticker": "000660",
        "per": 15.2,
        "pbr": 1.3,
        "ev_ebitda": 7.5,
        "market_cap": 75000000
      },
      {
        "name": "DB하이텍",
        "ticker": "000990",
        "per": 18.5,
        "pbr": 1.5,
        "ev_ebitda": 8.2,
        "market_cap": 3500000
      }
    ]
  },
  "message": "자료 수집이 완료되었습니다. 평가를 시작합니다."
}
```

---

## 8. 종합 평가 실행 API

### POST /projects/{project_id}/calculate

**설명**: 5가지 평가법을 모두 실행하고 통합 결과 산출

**Request Body**:
```json
{
  "methods": ["dcf", "relative", "asset", "capital_market_law", "inheritance_tax_law"],
  "purpose": "comprehensive",
  "include_sensitivity": true
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "evaluating",
  "calculation_status": "completed",
  "valuation_results": {
    "dcf": {
      "enterprise_value": 152300000000,
      "equity_value": 152300000000,
      "value_per_share": 15230,
      "wacc": 0.112,
      "terminal_growth": 0.025,
      "pv_fcff": 50720000000,
      "pv_terminal_value": 107780000000,
      "terminal_value_percentage": 0.68
    },
    "relative": {
      "per_valuation": 145000000000,
      "pbr_valuation": 138000000000,
      "ev_ebitda_valuation": 150000000000,
      "average_valuation": 144333000000,
      "value_per_share": 14433,
      "selected_multiples": {
        "per": 18.5,
        "pbr": 1.8,
        "ev_ebitda": 10.2
      }
    },
    "asset": {
      "nav": 135000000000,
      "value_per_share": 13500,
      "fair_value_adjustments": {
        "land_building": 15000000000,
        "intangible_assets": -2000000000,
        "contingent_liabilities": -5000000000
      }
    },
    "capital_market_law": {
      "intrinsic_value": 148000000000,
      "value_per_share": 14800,
      "asset_value": 135000000000,
      "income_value": 155000000000,
      "weight_asset": 0.40,
      "weight_income": 0.60
    },
    "inheritance_tax_law": {
      "valuation": 140000000000,
      "value_per_share": 14000,
      "income_value": 150000000000,
      "asset_value": 125000000000,
      "weight_income": 0.60,
      "weight_asset": 0.40,
      "discount_rate": 0.20,
      "shareholder_type": "minority"
    }
  },
  "integrated_result": {
    "final_value": 146000000000,
    "final_value_per_share": 14600,
    "weights": {
      "dcf": 0.30,
      "relative": 0.25,
      "asset": 0.20,
      "capital_market_law": 0.15,
      "inheritance_tax_law": 0.10
    },
    "valuation_range": {
      "min": 135000000000,
      "max": 155000000000,
      "confidence_level": 0.80
    }
  },
  "message": "평가가 완료되었습니다. 회계사 승인을 기다립니다."
}
```

---

## 9. 22개 회계사 판단 포인트 API

### GET /projects/{project_id}/approval-points

**설명**: 회계사 승인이 필요한 22개 판단 포인트 조회

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "human_approval",
  "total_points": 22,
  "approved_count": 0,
  "pending_count": 22,
  "approval_points": [
    {
      "point_id": "JP001",
      "point_name": "revenue_growth_rate",
      "display_name": "매출 성장률",
      "category": "재무",
      "importance": "high",
      "valuation_method": "dcf",
      "ai_value": 0.05,
      "ai_rationale": "최근 5년 평균 성장률 4.8%를 기반으로 5%를 제안합니다.",
      "suggested_range": [0.03, 0.08],
      "human_decision": null,
      "custom_value": null,
      "status": "pending",
      "accountant_notes": null
    },
    {
      "point_id": "JP004",
      "point_name": "terminal_growth_rate",
      "display_name": "영구성장률",
      "category": "재무",
      "importance": "medium",
      "valuation_method": "dcf",
      "ai_value": 0.025,
      "ai_rationale": "GDP 성장률 2.5%를 기준으로 설정했습니다.",
      "suggested_range": [0.02, 0.03],
      "human_decision": null,
      "custom_value": null,
      "status": "pending",
      "accountant_notes": null
    },
    {
      "point_id": "JP009",
      "point_name": "comparable_companies",
      "display_name": "비교기업 목록",
      "category": "시장",
      "importance": "medium",
      "valuation_method": "relative",
      "ai_value": ["SK하이닉스", "DB하이텍", "네패스"],
      "ai_rationale": "동일 업종, 유사 규모 기업 3개를 선정했습니다.",
      "human_decision": null,
      "custom_value": null,
      "status": "pending",
      "accountant_notes": null
    },
    {
      "point_id": "JP013",
      "point_name": "land_building_appraisal",
      "display_name": "토지/건물 감정평가액",
      "category": "자산",
      "importance": "high",
      "valuation_method": "asset",
      "ai_value": 15000000000,
      "ai_rationale": "공시지가 기준으로 추정했습니다. 실제 감정평가서 업로드를 권장합니다.",
      "suggested_range": [12000000000, 18000000000],
      "human_decision": null,
      "custom_value": null,
      "status": "pending",
      "accountant_notes": null
    },
    {
      "point_id": "JP022",
      "point_name": "ownership_ratio",
      "display_name": "지분율 및 주주 유형",
      "category": "법률",
      "importance": "high",
      "valuation_method": "inheritance_tax_law",
      "ai_value": {
        "ownership_ratio": 0.05,
        "shareholder_type": "minority",
        "discount_rate": 0.30
      },
      "ai_rationale": "5% 지분으로 소액주주에 해당하여 30% 할인율을 적용했습니다.",
      "human_decision": null,
      "custom_value": null,
      "status": "pending",
      "accountant_notes": null
    }
  ]
}
```

**22개 판단 포인트 전체 목록**:
| ID | 포인트명 | 카테고리 | 중요도 | 평가법 |
|----|---------|---------|--------|--------|
| JP001 | revenue_growth_rate | 재무 | ⭐⭐⭐ | dcf |
| JP002 | ebit_margin | 재무 | ⭐⭐ | dcf |
| JP003 | wacc_rate | 재무 | ⭐⭐⭐ | dcf |
| JP004 | terminal_growth_rate | 재무 | ⭐⭐ | dcf |
| JP005 | forecast_period | 재무 | ⭐ | dcf |
| JP006 | capex_rate | 재무 | ⭐⭐ | dcf |
| JP007 | working_capital_change | 재무 | ⭐⭐ | dcf |
| JP008 | beta_coefficient | 시장 | ⭐⭐ | dcf |
| JP009 | comparable_companies | 시장 | ⭐⭐ | relative |
| JP010 | selected_multiple | 시장 | ⭐⭐ | relative |
| JP011 | industry_multiple | 시장 | ⭐⭐ | relative |
| JP012 | unlisted_discount | 시장 | ⭐⭐⭐ | relative |
| JP013 | land_building_appraisal | 자산 | ⭐⭐⭐ | asset |
| JP014 | patent_valuation | 자산 | ⭐⭐ | asset |
| JP015 | contingent_liabilities | 법률 | ⭐⭐⭐ | asset |
| JP016 | allowance_for_bad_debts | 재무 | ⭐⭐ | asset |
| JP017 | inventory_nrv | 재무 | ⭐⭐ | asset |
| JP018 | unlisted_equity_valuation | 자산 | ⭐⭐⭐ | asset |
| JP019 | income_value_method | 법률 | ⭐⭐ | capital_market_law |
| JP020 | asset_income_weight | 법률 | ⭐⭐ | capital_market_law |
| JP021 | three_year_avg_income | 재무 | ⭐⭐ | inheritance_tax_law |
| JP022 | ownership_ratio | 법률 | ⭐⭐⭐ | inheritance_tax_law |

---

### POST /projects/{project_id}/approval-points/{point_id}

**설명**: 회계사가 특정 판단 포인트 승인/수정

**Request Body**:
```json
{
  "human_decision": "approved" | "rejected" | "custom",
  "custom_value": 0.06,
  "accountant_notes": "시장 상황을 고려하여 6%로 조정",
  "supporting_documents": ["doc_123", "doc_456"]
}
```

**Response**:
```json
{
  "point_id": "JP001",
  "status": "approved",
  "ai_value": 0.05,
  "human_decision": "custom",
  "custom_value": 0.06,
  "approved_by": "kim@company.com",
  "approved_at": "2026-01-20T14:30:00Z",
  "accountant_notes": "시장 상황을 고려하여 6%로 조정",
  "impact_analysis": {
    "affected_valuations": ["dcf", "capital_market_law"],
    "value_change": {
      "dcf": {
        "before": 152300000000,
        "after": 158500000000,
        "change_percent": 0.041
      },
      "integrated": {
        "before": 146000000000,
        "after": 148200000000,
        "change_percent": 0.015
      }
    }
  }
}
```

---

## 10. 평가서 초안 생성 API

### POST /projects/{project_id}/draft

**설명**: 회계사가 22개 판단 포인트 승인 완료 후 초안 생성

**Request Body**:
```json
{
  "report_type": "comprehensive",
  "include_appendix": true,
  "custom_notes": "특별 고려사항을 반영했습니다."
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "draft_generated",
  "draft_id": "DRAFT-SAMSU-001",
  "draft_url": "https://api.valuelink.com/drafts/DRAFT-SAMSU-001.pdf",
  "page_count": 80,
  "generated_at": "2026-01-20T15:00:00Z",
  "customer_review_url": "https://valuelink.com/portal/SAMSU-2501191430-CP/review",
  "message": "초안이 생성되었습니다. 고객 검토를 요청합니다."
}
```

---

## 11. 고객 수정 요청 API

### POST /projects/{project_id}/revisions

**설명**: 고객이 초안 검토 후 수정 요청

**Request Body**:
```json
{
  "revision_type": "assumption_change" | "scope_change" | "clarification",
  "requested_changes": {
    "wacc": 0.105,
    "terminal_growth_rate": 0.03,
    "comparable_companies": ["SK하이닉스", "DB하이텍", "LX세미콘"]
  },
  "reason": "시장 상황 변화를 반영해주세요.",
  "supporting_documents": ["doc_789"],
  "customer_notes": "비교기업 추가 요청"
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "revision_requested",
  "revision_id": "REV-001",
  "requested_at": "2026-01-20T16:00:00Z",
  "estimated_completion": "2026-01-21T10:00:00Z",
  "message": "수정 요청이 접수되었습니다. 회계사가 검토 후 재평가를 진행합니다."
}
```

---

## 12. 평가 결과 미리보기 API

### GET /projects/{project_id}/preview

**설명**: 평가 결과 미리보기 (민감도 분석 포함)

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "current_status": "draft_generated",
  "integrated_result": {
    "final_value": 148200000000,
    "final_value_per_share": 14820,
    "valuation_range": {
      "min": 135000000000,
      "max": 155000000000
    }
  },
  "method_results": {
    "dcf": {
      "enterprise_value": 158500000000,
      "value_per_share": 15850
    },
    "relative": {
      "average_valuation": 144333000000,
      "value_per_share": 14433
    },
    "asset": {
      "nav": 135000000000,
      "value_per_share": 13500
    },
    "capital_market_law": {
      "intrinsic_value": 148000000000,
      "value_per_share": 14800
    },
    "inheritance_tax_law": {
      "valuation": 140000000000,
      "value_per_share": 14000
    }
  },
  "sensitivity_analysis": {
    "dcf": {
      "parameters": ["wacc", "terminal_growth"],
      "wacc_range": [0.10, 0.11, 0.12, 0.13, 0.14],
      "growth_range": [0.02, 0.025, 0.03],
      "value_matrix": [
        [162000, 148000, 135000],
        [155000, 142000, 130000],
        [149000, 137000, 126000],
        [143000, 132000, 121000],
        [138000, 127000, 117000]
      ]
    }
  },
  "key_assumptions": {
    "dcf": {
      "wacc": 0.10,
      "terminal_growth": 0.03,
      "forecast_period": 5,
      "revenue_growth_rate": 0.06
    },
    "relative": {
      "selected_multiple": "per",
      "industry_per": 18.5,
      "unlisted_discount": 0.20
    }
  }
}
```

---

## 13. 시뮬레이션 실행 API

### POST /projects/{project_id}/simulate

**설명**: 가정 변경 시뮬레이션 (What-If 분석)

**Request Body**:
```json
{
  "method": "dcf",
  "modified_assumptions": {
    "revenue_growth_rate": 0.07,
    "ebit_margin": 0.16,
    "wacc": 0.095,
    "terminal_growth": 0.03
  }
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "method": "dcf",
  "simulation_result": {
    "original_value": 158500000000,
    "simulated_value": 175200000000,
    "change_amount": 16700000000,
    "change_percentage": 0.105
  },
  "impact_breakdown": {
    "revenue_growth_impact": 6200000000,
    "ebit_margin_impact": 3800000000,
    "wacc_impact": 4500000000,
    "terminal_growth_impact": 2200000000
  },
  "new_assumptions": {
    "revenue_growth_rate": 0.07,
    "ebit_margin": 0.16,
    "wacc": 0.095,
    "terminal_growth": 0.03
  }
}
```

---

## 14. 최종 확정 API

### POST /projects/{project_id}/finalize

**설명**: 회계사가 평가 보고서 최종 확정

**Request Body**:
```json
{
  "final_approval": true,
  "accountant_comments": "모든 판단 포인트 검토 완료. 고객 수정 요청 반영 완료. 평가 결과 최종 확정 승인.",
  "selected_valuation": "integrated",
  "report_type": "comprehensive"
}
```

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "status": "completed",
  "final_valuation": {
    "enterprise_value": 148200000000,
    "equity_value": 148200000000,
    "value_per_share": 14820
  },
  "selected_method": "integrated",
  "weights": {
    "dcf": 0.30,
    "relative": 0.25,
    "asset": 0.20,
    "capital_market_law": 0.15,
    "inheritance_tax_law": 0.10
  },
  "finalized_at": "2026-01-20T17:00:00Z",
  "finalized_by": "kim@company.com",
  "all_approval_points_completed": true,
  "message": "평가가 최종 확정되었습니다. 보고서를 발행합니다."
}
```

---

## 15. 보고서 발행 API

### POST /projects/{project_id}/report

**설명**: 공식 평가 보고서 발행 (80페이지 종합 보고서)

**Request Body**:
```json
{
  "report_type": "comprehensive",
  "delivery_format": "pdf",
  "delivery_method": "download",
  "include_appendix": true,
  "watermark": false
}
```

**보고서 유형 (report_type)**:
| 유형 | 페이지 수 | 포함 내용 |
|------|----------|----------|
| `comprehensive` | 80p | 5가지 평가법 + 통합 결과 + 민감도 분석 |
| `single_method` | 35p | 선택한 1개 평가법만 |
| `executive_summary` | 10p | 핵심 요약만 |

**Response**:
```json
{
  "project_id": "SAMSU-2501191430-CP",
  "report_id": "RPT-SAMSU-2501191430-CP-001",
  "report_url": "https://api.valuelink.com/reports/RPT-SAMSU-2501191430-CP-001.pdf",
  "report_type": "comprehensive",
  "page_count": 80,
  "generation_time": "45 seconds",
  "status": "completed",
  "issued_at": "2026-01-20T17:30:00Z",
  "issued_by": "kim@company.com",
  "expires_at": "2026-02-20T17:30:00Z",
  "download_count": 0,
  "message": "평가 보고서가 발행되었습니다."
}
```

---

## 프로젝트 상태 흐름

```
REQUESTED (평가 신청)
    ↓
QUOTE_SENT (견적 발송)
    ↓
NEGOTIATING (조건 협의 중)
    ↓
APPROVED (승인 완료, 회계사 배정)
    ↓
DOCUMENTS_UPLOADED (자료 업로드)
    ↓
COLLECTING (자료 수집 중)
    ↓
EVALUATING (평가 진행 중)
    ↓
HUMAN_APPROVAL (회계사 승인 대기, 22개 포인트)
    ↓
DRAFT_GENERATED (초안 생성 완료)
    ↓
REVISION_REQUESTED (수정 요청, 선택) → EVALUATING (재평가)
    ↓
COMPLETED (최종 확정)
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
| 422 | 회계사 승인 포인트 미완료 |
| 423 | 협의 진행 중 (계약 미확정) |
| 500 | 서버 내부 오류 |

---

## 다음 단계

1. **Pydantic 스키마 정의** (Request/Response 모델)
   - ProjectCreate, QuoteRequest, NegotiationRequest
   - ApprovalPoint, ValuationResult
   - DraftRequest, RevisionRequest

2. **Database 모델 정의** (SQLAlchemy)
   - projects 테이블
   - quotes 테이블
   - negotiations 테이블
   - documents 테이블
   - approval_points 테이블 (22개 포인트)
   - valuation_results 테이블
   - drafts 테이블
   - revisions 테이블

3. **FastAPI 라우터 구현**
   - 프로젝트 관리 라우터 (생성, 견적, 협의, 승인)
   - 자료 수집 라우터
   - 5가지 평가법 라우터
   - 회계사 승인 포인트 라우터
   - 초안/수정 라우터
   - 통합 평가 라우터

4. **5가지 평가 엔진 통합**
   - dcf_engine.py (완료)
   - relative_engine.py (구현 필요)
   - asset_engine.py (구현 필요)
   - capital_market_law_engine.py (구현 필요)
   - inheritance_tax_law_engine.py (구현 필요)

5. **Master Valuation Engine 구현**
   - MasterValuationEngine 클래스
   - ValuationSelector 클래스 (목적별 가중치)
   - CrossChecker 클래스 (교차 검증)

6. **프론트엔드 연동**
   - 기존 HTML 파일들과 API 연동
   - 22개 판단 포인트 UI 구현
   - 초안 검토 및 수정 요청 UI
   - 통합 평가 결과 대시보드

---

**버전**: 2.0 (프로세스 수정)
**작성일**: 2026-01-20
**프로젝트**: 기업가치평가 플랫폼 (Valuation Platform)
