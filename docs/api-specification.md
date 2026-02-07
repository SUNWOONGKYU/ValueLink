# ValueLink API Specification

## 개요

- **Base URL**: `https://valuation.ai.kr/api`
- **Authentication**: Supabase Auth (JWT Bearer Token)
- **Content-Type**: `application/json`
- **API Version**: v1

---

## 프로젝트 라이프사이클 (3단계)

```
[1] 평가 요청 생성 (evaluation_requests)
         ↓
[2] 관리자 승인 → 프로젝트 생성 (projects)
         ↓
[3] 14단계 워크플로우 진행
         ↓
[4] 완료 → 히스토리 아카이브 (project_history)
```

---

## 1. 평가 요청 API (Evaluation Requests)

### POST /api/evaluation-requests

고객이 기업가치평가를 요청합니다.

**Request**:
```json
{
  "company_name_kr": "스타트업 A",
  "company_name_en": "Startup A Inc.",
  "business_registration_number": "123-45-67890",
  "representative_name": "홍길동",
  "industry": "AI/헬스케어",
  "revenue": 5000000000,
  "employees": 50,
  "founded_date": "2020-01-15",
  "company_website": "https://startup-a.com",
  "address": "서울시 강남구 테헤란로 123",
  "phone": "02-1234-5678",
  "valuation_purpose": "투자유치",
  "requested_methods": ["dcf", "relative"],
  "target_date": "2026-03-15",
  "requirements": "3개월 내 Series B 투자유치를 위한 기업가치평가 필요",
  "budget_min": 5000000,
  "budget_max": 10000000
}
```

**Response** (201 Created):
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-uuid",
  "company_name_kr": "스타트업 A",
  "status": "pending",
  "created_at": "2026-02-07T10:00:00Z"
}
```

**Status Codes**:
- 201: Created (요청 생성 성공)
- 400: Bad Request (필수 필드 누락)
- 401: Unauthorized (로그인 필요)

---

### GET /api/evaluation-requests

평가 요청 목록을 조회합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | 필터: pending, approved, rejected |

**역할별 필터링**:
- 고객(customer): 본인 요청만 조회
- 관리자(admin): 전체 요청 조회

**Response**:
```json
{
  "evaluation_requests": [
    {
      "request_id": "550e8400-e29b-41d4-a716-446655440000",
      "company_name_kr": "스타트업 A",
      "valuation_purpose": "투자유치",
      "requested_methods": ["dcf", "relative"],
      "status": "pending",
      "created_at": "2026-02-07T10:00:00Z"
    }
  ]
}
```

---

### PUT /api/evaluation-requests

평가 요청을 승인/거절합니다. (관리자 전용)

**Request**:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "approve",
  "accountant_id": "accountant-user-uuid",
  "admin_comment": "승인합니다. 담당 회계사를 배정합니다."
}
```

**거절 시**:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "reject",
  "admin_comment": "예산 범위가 너무 낮습니다."
}
```

**Response** (승인 시):
```json
{
  "project": {
    "project_id": "VL-2026-0001",
    "company_name_kr": "스타트업 A",
    "status": "in_progress",
    "current_step": 1,
    "accountant_id": "accountant-user-uuid"
  }
}
```

**Status Codes**:
- 200: OK
- 400: Bad Request (request_id 또는 action 누락)
- 403: Forbidden (관리자 권한 필요)

---

## 2. 프로젝트 API (Projects)

### GET /api/projects

진행 중인 프로젝트 목록을 조회합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | 필터: in_progress, completed |

**역할별 필터링**:
- 고객(customer): 본인 프로젝트만 조회
- 회계사(accountant): 담당 프로젝트만 조회
- 관리자(admin): 전체 프로젝트 조회

**Response**:
```json
{
  "projects": [
    {
      "project_id": "VL-2026-0001",
      "company_name_kr": "스타트업 A",
      "requested_methods": ["dcf", "relative"],
      "status": "in_progress",
      "current_step": 4,
      "accountant": {
        "name": "김회계",
        "email": "accountant@example.com"
      },
      "created_at": "2026-02-07T10:00:00Z"
    }
  ]
}
```

---

### PUT /api/projects

프로젝트 상태/단계를 업데이트합니다.

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "current_step": 5,
  "status": "in_progress"
}
```

**Response**:
```json
{
  "project": {
    "project_id": "VL-2026-0001",
    "current_step": 5,
    "status": "in_progress",
    "updated_at": "2026-02-07T11:00:00Z"
  }
}
```

---

## 3. 프로젝트 히스토리 API (Project History)

### GET /api/project-history

완료된 프로젝트 아카이브를 조회합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| year | string | 연도 필터: 2026 |

**Response**:
```json
{
  "history": [
    {
      "history_id": "uuid",
      "project_id": "VL-2026-0001",
      "company_name_kr": "스타트업 A",
      "valuation_methods": ["dcf", "relative"],
      "final_valuation": 50000000000,
      "completed_at": "2026-03-15T10:00:00Z"
    }
  ]
}
```

---

### POST /api/project-history

프로젝트 완료 시 히스토리로 아카이브합니다.

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "final_valuation": 50000000000
}
```

**Response** (201 Created):
```json
{
  "history": {
    "history_id": "uuid",
    "project_id": "VL-2026-0001",
    "completed_at": "2026-03-15T10:00:00Z"
  }
}
```

---

## 4. 문서 API (Documents)

### POST /api/documents/upload

파일을 Supabase Storage에 업로드합니다.

**Request** (multipart/form-data):
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | 업로드할 파일 |
| project_id | string | Yes | 프로젝트 ID |
| document_type | string | Yes | 문서 유형 |

**Document Types**:
- `financial_statement`: 재무제표
- `business_plan`: 사업계획서
- `articles_of_incorporation`: 정관
- `shareholder_list`: 주주명부
- `contract`: 계약서
- `other`: 기타

**Response**:
```json
{
  "document_id": "uuid",
  "file_name": "재무제표_2025.xlsx",
  "file_path": "projects/VL-2026-0001/documents/financial_statement_123.xlsx",
  "file_size": 1048576,
  "document_type": "financial_statement",
  "created_at": "2026-02-07T12:00:00Z"
}
```

---

### GET /api/documents

프로젝트 문서 목록을 조회합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string | 프로젝트 ID (필수) |

**Response**:
```json
{
  "documents": [
    {
      "document_id": "uuid",
      "file_name": "재무제표_2025.xlsx",
      "document_type": "financial_statement",
      "file_size": 1048576,
      "uploaded_by": "user-uuid",
      "created_at": "2026-02-07T12:00:00Z"
    }
  ]
}
```

---

## 5. 승인 포인트 API (Approval Points)

### GET /api/approval-points

프로젝트의 승인 포인트 상태를 조회합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string | 프로젝트 ID (필수) |

**Response**:
```json
{
  "approval_points": [
    {
      "approval_id": "uuid",
      "step_number": 1,
      "approval_type": "document_upload",
      "status": "approved",
      "approver_id": "accountant-uuid",
      "approved_at": "2026-02-07T13:00:00Z"
    },
    {
      "approval_id": "uuid",
      "step_number": 2,
      "approval_type": "data_review",
      "status": "pending",
      "approver_id": null,
      "approved_at": null
    }
  ]
}
```

---

### POST /api/approval-points/{step_number}/approve

특정 단계를 승인합니다. (회계사/관리자)

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "comment": "검토 완료. 승인합니다."
}
```

**Response**:
```json
{
  "approval_id": "uuid",
  "step_number": 2,
  "status": "approved",
  "approved_at": "2026-02-07T14:00:00Z"
}
```

---

### POST /api/approval-points/{step_number}/reject

특정 단계를 거절합니다.

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "comment": "재무제표에 오류가 있습니다. 수정 후 재제출 바랍니다.",
  "required_changes": ["매출액 재확인", "영업이익 산정 근거 추가"]
}
```

---

## 6. 초안 API (Drafts)

### GET /api/drafts

평가 초안 목록을 조회합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string | 프로젝트 ID (필수) |

**Response**:
```json
{
  "drafts": [
    {
      "draft_id": "uuid",
      "project_id": "VL-2026-0001",
      "valuation_method": "dcf",
      "version": 1,
      "status": "in_progress",
      "created_at": "2026-02-08T10:00:00Z"
    }
  ]
}
```

---

### POST /api/drafts

새 초안을 생성합니다.

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "valuation_method": "dcf"
}
```

---

### PUT /api/drafts/{draft_id}

초안 내용을 업데이트합니다.

**Request**:
```json
{
  "content": {
    "executive_summary": "...",
    "methodology": "...",
    "assumptions": "...",
    "calculation": "...",
    "conclusion": "..."
  },
  "section_1_completed": true,
  "section_2_completed": true
}
```

---

## 7. 수정 요청 API (Revisions)

### POST /api/revisions

초안에 대한 수정 요청을 생성합니다.

**Request**:
```json
{
  "draft_id": "uuid",
  "requested_by": "user-uuid",
  "revision_type": "content_change",
  "description": "가정치 수정 필요",
  "details": {
    "section": "assumptions",
    "current_value": "성장률 15%",
    "requested_value": "성장률 12%",
    "reason": "업계 평균 성장률 고려"
  }
}
```

---

### GET /api/revisions

수정 요청 목록을 조회합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| draft_id | string | 초안 ID |
| status | string | pending, in_progress, completed, rejected |

---

## 8. 보고서 API (Reports)

### GET /api/reports

최종 보고서 목록을 조회합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string | 프로젝트 ID |

---

### POST /api/reports/generate

최종 보고서를 생성합니다.

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "draft_ids": ["uuid-1", "uuid-2"],
  "report_type": "full",
  "include_appendix": true
}
```

**Response**:
```json
{
  "report_id": "uuid",
  "report_url": "/storage/reports/VL-2026-0001/final_report.pdf",
  "created_at": "2026-03-15T10:00:00Z"
}
```

---

## 14단계 워크플로우

| Step | Name | API Endpoint | Approval Points |
|------|------|--------------|-----------------|
| 1 | 평가 요청 | POST /api/evaluation-requests | - |
| 2 | 관리자 승인 | PUT /api/evaluation-requests | 1 |
| 3 | 계약금 결제 | POST /api/payments | - |
| 4 | 문서 업로드 | POST /api/documents/upload | 2-3 |
| 5 | 데이터 검증 | PUT /api/approval-points/5/approve | 4-5 |
| 6 | 평가 수행 | POST /api/valuation/{method} | 6-8 |
| 7 | 초안 생성 | POST /api/drafts | 9-10 |
| 8 | 내부 검토 | PUT /api/approval-points/8/approve | 11-12 |
| 9 | 고객 검토 | GET /api/drafts/{id} | 13-14 |
| 10 | 수정 요청 | POST /api/revisions | 15-16 |
| 11 | 수정 반영 | PUT /api/drafts/{id} | 17-18 |
| 12 | 최종 승인 | PUT /api/approval-points/12/approve | 19-20 |
| 13 | 잔금 결제 | POST /api/payments | - |
| 14 | 보고서 발행 | POST /api/reports/generate | 21-22 |

**총 22개 AI 승인 포인트**

---

## 에러 코드

| Code | Message | 설명 |
|------|---------|------|
| 400 | Bad Request | 잘못된 요청 파라미터 |
| 401 | Unauthorized | 인증 필요 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 409 | Conflict | 중복 리소스 |
| 422 | Unprocessable Entity | 유효성 검사 실패 |
| 500 | Internal Server Error | 서버 오류 |

---

## 에러 응답 형식

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "필수 필드가 누락되었습니다.",
    "details": {
      "field": "company_name_kr",
      "reason": "required"
    }
  }
}
```

---

## Rate Limiting

| 대상 | 제한 |
|------|------|
| 인증된 사용자 | 100 req/min |
| 비인증 사용자 | 10 req/min |
| 파일 업로드 | 10 req/min |

**Rate Limit 응답**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "요청 한도를 초과했습니다.",
    "retry_after": 60
  }
}
```

---

## 버전 정보

- **API Version**: v1
- **Last Updated**: 2026-02-07
- **Schema Version**: v4.0

---

**작성일**: 2026-02-07
**작성자**: Claude Code
