# S1M1: API Specification & Documentation

## Task 정보

- **Task ID**: S1M1
- **Task Name**: API 명세서 및 기술 문서 작성
- **Stage**: S1 (Development Setup - 개발 준비)
- **Area**: M (Documentation)
- **Dependencies**: 없음
- **Task Agent**: documentation-specialist
- **Verification Agent**: code-reviewer

---

## Task 목표

ValueLink 플랫폼의 API 엔드포인트, 인증 흐름, 평가 엔진 API 명세를 문서화하여 개발 가이드 제공

---

## 상세 지시사항

### 1. API 명세서 (14단계 워크플로우)

**파일**: `docs/api-specification.md`

#### 구조
```markdown
# ValueLink API Specification

## 개요
- Base URL: `https://valuation.ai.kr/api`
- Authentication: Supabase Auth (JWT Bearer Token)
- Content-Type: `application/json`

## 1. 프로젝트 생성 (Step 1)

### POST /projects

프로젝트를 생성합니다.

**Request**:
```json
{
  "project_name": "스타트업 A 기업가치평가",
  "valuation_method": "dcf"
}
```

**Response**:
```json
{
  "project_id": "uuid",
  "project_name": "스타트업 A 기업가치평가",
  "valuation_method": "dcf",
  "status": "pending",
  "current_step": 1,
  "created_at": "2026-02-05T10:00:00Z"
}
```

**Status Codes**:
- 201: Created
- 400: Bad Request (유효하지 않은 valuation_method)
- 401: Unauthorized

---

## 2. 견적 요청 (Step 2)

### POST /quotes

프로젝트에 대한 견적을 요청합니다.

**Request**:
```json
{
  "project_id": "uuid"
}
```

**Response**:
```json
{
  "quote_id": "uuid",
  "project_id": "uuid",
  "amount": 8000000,
  "deposit_amount": 4000000,
  "balance_amount": 4000000,
  "delivery_days": 10,
  "description": "DCF 평가 방법론 적용",
  "status": "pending",
  "created_at": "2026-02-05T11:00:00Z"
}
```

---

## 3. 협상 제안 (Step 3)

### POST /negotiations

견적에 대한 협상을 제안합니다.

**Request**:
```json
{
  "quote_id": "uuid",
  "negotiation_type": "price",
  "proposed_amount": 7000000,
  "message": "예산이 부족하여 7백만원으로 조정 가능할까요?"
}
```

---

## 4. 문서 업로드 (Step 4)

### POST /documents/upload

파일을 Supabase Storage에 업로드합니다.

**Request** (multipart/form-data):
- `file`: 업로드할 파일
- `project_id`: 프로젝트 ID
- `document_type`: "financial_statement" | "business_plan" | "contract" | "other"

**Response**:
```json
{
  "document_id": "uuid",
  "file_name": "재무제표_2025.xlsx",
  "file_path": "projects/{project_id}/documents/{filename}",
  "file_size": 1048576,
  "created_at": "2026-02-05T12:00:00Z"
}
```

---

(나머지 10개 단계 API 명세 작성...)

## 승인 포인트 (22개)

### POST /approval-points/{step_number}/approve

특정 단계를 승인합니다. (회계사/관리자만)

**Request**:
```json
{
  "project_id": "uuid",
  "comment": "승인합니다."
}
```

---

## 에러 코드

| Code | Message | 설명 |
|------|---------|------|
| 400 | Bad Request | 잘못된 요청 파라미터 |
| 401 | Unauthorized | 인증 필요 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 500 | Internal Server Error | 서버 오류 |

---

## Rate Limiting

- 인증된 사용자: 100 req/min
- 비인증 사용자: 10 req/min
```

---

### 2. 평가 엔진 API 문서

**파일**: `docs/valuation-engines-api.md`

#### 구조
```markdown
# Valuation Engines API

## 개요

ValueLink는 5개의 평가 방법을 지원합니다:
1. DCF (Discounted Cash Flow)
2. Relative (상대가치평가)
3. Asset (자산가치평가)
4. Intrinsic (내재가치평가)
5. Tax (세법상평가)

---

## 1. DCF 평가 엔진

### POST /valuation/dcf

DCF 방법으로 기업가치를 평가합니다.

**Request**:
```json
{
  "project_id": "uuid",
  "input_data": {
    "revenue_5years": [100, 120, 144, 173, 207],
    "operating_margin": 0.15,
    "tax_rate": 0.22,
    "wacc": 0.12,
    "terminal_growth_rate": 0.03,
    "net_debt": 50,
    "shares_outstanding": 1000000
  }
}
```

**Response**:
```json
{
  "result_id": "uuid",
  "valuation_method": "dcf",
  "enterprise_value": 1500000000,
  "equity_value": 1450000000,
  "value_per_share": 1450,
  "calculation_data": {
    "fcf_5years": [15, 18, 21.6, 25.9, 31.1],
    "pv_fcf": 78.5,
    "terminal_value": 1036.7,
    "pv_terminal_value": 588.2,
    "enterprise_value_calculation": {
      "pv_fcf_sum": 78.5,
      "pv_terminal_value": 588.2,
      "total": 666.7
    }
  },
  "sensitivity_analysis": {
    "wacc_range": [0.10, 0.11, 0.12, 0.13, 0.14],
    "growth_range": [0.01, 0.02, 0.03, 0.04, 0.05],
    "value_matrix": [[...], [...], [...]]
  },
  "created_at": "2026-02-05T13:00:00Z"
}
```

---

## 2. Relative 평가 엔진

### POST /valuation/relative

상대가치평가 방법으로 기업가치를 평가합니다.

**Request**:
```json
{
  "project_id": "uuid",
  "input_data": {
    "revenue": 100,
    "ebitda": 20,
    "comparable_companies": [
      {"name": "A사", "revenue_multiple": 3.5, "ebitda_multiple": 12.0},
      {"name": "B사", "revenue_multiple": 4.0, "ebitda_multiple": 14.0}
    ]
  }
}
```

---

(나머지 3개 평가 엔진 API 명세 작성...)

## 공통 에러 응답

```json
{
  "error": "INVALID_INPUT",
  "message": "revenue_5years must have exactly 5 values",
  "details": {
    "field": "revenue_5years",
    "received": 4,
    "expected": 5
  }
}
```
```

---

### 3. 인증 흐름 문서

**파일**: `docs/authentication.md`

#### 구조
```markdown
# Authentication Flow

## 개요

ValueLink는 Supabase Auth를 사용하여 인증을 처리합니다.

---

## 1. 회원가입 (이메일)

### POST /auth/signup

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "홍길동",
  "company_name": "스타트업 A",
  "role": "customer"
}
```

**Response**:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "email_confirmed_at": null
  },
  "session": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "expires_at": 1738752000
  }
}
```

---

## 2. 로그인 (이메일)

### POST /auth/login

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

---

## 3. OAuth 로그인 (Google)

### GET /auth/google

리디렉션: `https://accounts.google.com/o/oauth2/v2/auth?...`

**Callback**: `/auth/callback`

---

## 4. 세션 갱신

### POST /auth/refresh

```json
{
  "refresh_token": "refresh_token"
}
```

---

## 5. 로그아웃

### POST /auth/logout

---

## 6. 비밀번호 재설정

### POST /auth/reset-password

```json
{
  "email": "user@example.com"
}
```

이메일로 재설정 링크 발송

---

## JWT 토큰 사용

모든 API 요청에 `Authorization` 헤더 포함:

```
Authorization: Bearer {access_token}
```

---

## 역할 기반 접근 제어 (RBAC)

| 역할 | 설명 | 권한 |
|------|------|------|
| customer | 고객 (기업) | 프로젝트 생성, 견적 요청, 문서 업로드 |
| accountant | 회계사 | 승인, 평가 수행, 초안 작성 |
| admin | 관리자 | 모든 권한 |
| investor | 투자자 | Deal 뉴스 조회 |
| partner | 파트너 | 제한적 접근 |
| supporter | 서포터 | 제한적 접근 |

---

## RLS (Row Level Security)

Supabase RLS 정책으로 데이터 접근 제어:

- 고객: 본인 프로젝트만 접근
- 회계사: 담당 프로젝트 접근
- 관리자: 모든 프로젝트 접근
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `docs/api-specification.md` | 14단계 워크플로우 API 명세 | ~800줄 |
| `docs/valuation-engines-api.md` | 5개 평가 엔진 API 명세 | ~600줄 |
| `docs/authentication.md` | 인증 흐름 문서 | ~200줄 |

**총 파일 수**: 3개
**총 라인 수**: ~1,600줄

---

## 기술 스택

- **Format**: Markdown
- **Tools**: 없음 (순수 문서 작성)

---

## 완료 기준

### 필수 (Must Have)
- [ ] api-specification.md 작성 완료
- [ ] valuation-engines-api.md 작성 완료
- [ ] authentication.md 작성 완료
- [ ] 모든 API 엔드포인트 문서화
- [ ] Request/Response 예시 포함
- [ ] 에러 코드 정의

### 검증 (Verification)
- [ ] Markdown 문법 검증
- [ ] 링크 정상 작동 확인
- [ ] 코드 블록 하이라이팅 확인

### 권장 (Nice to Have)
- [ ] Sequence Diagram 추가
- [ ] Postman Collection 생성
- [ ] OpenAPI (Swagger) 스펙 생성

---

## 참조

### 기존 프로토타입
- `Process/P3_프로토타입_제작/Documentation/valuation-engines.md` (평가 엔진 로직)
- `backend/app/api/v1/endpoints/valuation.py` (기존 FastAPI 엔드포인트)

### 관련 Task
- **S1D1**: Database Schema & RLS Policies (데이터 모델 참조)
- **S2BA1**: Valuation Process API (API 구현 시 참조)
- **S3BA1~S3BA4**: Valuation Engines (엔진 API 구현 시 참조)

---

## 주의사항

1. **API 버전 관리**
   - 현재 v1으로 작성
   - 향후 v2 추가 시 버전 분리

2. **실제 구현과 동기화**
   - API 구현 시 문서 업데이트 필수
   - Request/Response 형식 정확히 일치

3. **보안 정보 제외**
   - API 키, 비밀번호 등 민감 정보 제외
   - 예시 데이터만 사용

4. **명확한 설명**
   - 각 필드의 타입, 필수 여부 명시
   - 예외 상황 처리 방법 설명

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 3개
**라인 수**: ~1,600줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
