# Valuation API Documentation

## 개요

평가법별 14단계 프로세스를 관리하는 RESTful API 엔드포인트

## 지원 평가법

| 평가법 | method 값 | 설명 |
|--------|----------|------|
| DCF (현금흐름할인법) | `dcf` | Discounted Cash Flow |
| 상대가치평가법 | `relative` | Relative Valuation |
| 본질가치평가법 | `intrinsic` | Intrinsic Value |
| 자산가치평가법 | `asset` | Asset-based Valuation |
| 상증세법 평가법 | `inheritance_tax` | Inheritance Tax Law |

## API 엔드포인트

### 1. POST /api/v1/valuation/start

평가 시작

**Request Body:**
```json
{
  "project_id": "uuid-string",
  "method": "dcf"
}
```

**Response:**
```json
{
  "status": "started",
  "project_id": "uuid-string",
  "method": "dcf",
  "message": "DCF 평가가 시작되었습니다 (단계 5/14)"
}
```

**동작:**
- `{method}_status`를 `in_progress`로 설정
- `{method}_step`을 5로 설정
- `updated_at` 업데이트

**HTTP Status Codes:**
- `200`: 성공
- `404`: 프로젝트를 찾을 수 없음
- `500`: 서버 오류

---

### 2. GET /api/v1/valuation/progress

진행 상황 조회

**Query Parameters:**
- `project_id` (required): 프로젝트 ID
- `method` (required): 평가법 (`dcf`, `relative`, `intrinsic`, `asset`, `inheritance_tax`)

**Example:**
```
GET /api/v1/valuation/progress?project_id=uuid&method=dcf
```

**Response:**
```json
{
  "progress": 35,
  "current_step": 5,
  "status": "in_progress",
  "message": "진행 중입니다 (단계 5/14)"
}
```

**진행률 계산:**
- `progress = (current_step / 14) * 100`
- 0 ~ 100 범위

**상태 메시지:**
| status | 메시지 |
|--------|--------|
| `not_requested` | 평가가 신청되지 않았습니다 |
| `pending` | 승인 대기 중입니다 |
| `approved` | 승인되었습니다 |
| `in_progress` | 진행 중입니다 (단계 X/14) |
| `completed` | 평가가 완료되었습니다 |

**HTTP Status Codes:**
- `200`: 성공
- `404`: 프로젝트를 찾을 수 없음
- `500`: 서버 오류

---

### 3. GET /api/v1/valuation/result

평가 결과 조회

**Query Parameters:**
- `project_id` (required): 프로젝트 ID
- `method` (required): 평가법

**Example:**
```
GET /api/v1/valuation/result?project_id=uuid&method=dcf
```

**Response:**
```json
{
  "valuation_amount": 1500000000,
  "currency": "KRW",
  "report_url": "https://example.com/report.pdf",
  "completed_at": "2026-01-27T10:30:00Z"
}
```

**주의:**
- 평가 상태가 `completed`일 때만 조회 가능
- 그 외 상태면 `400 Bad Request` 반환

**HTTP Status Codes:**
- `200`: 성공
- `400`: 평가가 완료되지 않음
- `404`: 프로젝트를 찾을 수 없음
- `500`: 서버 오류

---

### 4. POST /api/v1/valuation/advance-step

다음 단계로 전진 (테스트용)

**Request Body:**
```json
{
  "project_id": "uuid-string",
  "method": "dcf"
}
```

**Response:**
```json
{
  "status": "advanced",
  "new_step": 6,
  "message": "단계가 5에서 6(으)로 전진했습니다"
}
```

**동작:**
- `{method}_step`을 1 증가
- 단계 14 도달 시 `{method}_status`를 `completed`로 변경
- 이미 단계 14면 `400 Bad Request` 반환

**HTTP Status Codes:**
- `200`: 성공
- `400`: 이미 최대 단계 (14)
- `404`: 프로젝트를 찾을 수 없음
- `500`: 서버 오류

---

### 5. POST /api/v1/valuation/update-status

평가 상태 업데이트

**Request Body:**
```json
{
  "project_id": "uuid-string",
  "method": "dcf",
  "status": "completed",
  "step": 14
}
```

**Parameters:**
- `project_id` (required): 프로젝트 ID
- `method` (required): 평가법
- `status` (required): 새 상태 (`not_requested`, `pending`, `approved`, `in_progress`, `completed`)
- `step` (optional): 단계 번호 (1-14)

**Response:**
```json
{
  "status": "updated",
  "message": "상태가 'completed'(으)로 업데이트되었습니다 (단계 14)"
}
```

**동작:**
- `{method}_status` 업데이트
- `step`이 제공되면 `{method}_step`도 업데이트
- `updated_at` 업데이트

**HTTP Status Codes:**
- `200`: 성공
- `404`: 프로젝트를 찾을 수 없음
- `500`: 서버 오류

---

## 데이터베이스 스키마

### projects 테이블 (평가 상태 필드)

| 필드명 | 타입 | 기본값 | 설명 |
|--------|------|--------|------|
| `dcf_status` | TEXT | `not_requested` | DCF 평가 상태 |
| `dcf_step` | INTEGER | 1 | DCF 평가 단계 (1-14) |
| `relative_status` | TEXT | `not_requested` | 상대가치 평가 상태 |
| `relative_step` | INTEGER | 1 | 상대가치 평가 단계 (1-14) |
| `intrinsic_status` | TEXT | `not_requested` | 본질가치 평가 상태 |
| `intrinsic_step` | INTEGER | 1 | 본질가치 평가 단계 (1-14) |
| `asset_status` | TEXT | `not_requested` | 자산가치 평가 상태 |
| `asset_step` | INTEGER | 1 | 자산가치 평가 단계 (1-14) |
| `inheritance_tax_status` | TEXT | `not_requested` | 상증세법 평가 상태 |
| `inheritance_tax_step` | INTEGER | 1 | 상증세법 평가 단계 (1-14) |

**제약조건:**
- `status` 값: `not_requested`, `pending`, `approved`, `in_progress`, `completed`
- `step` 값: 1 ~ 14

---

## 사용 예시

### Python (httpx)

```python
import httpx

BASE_URL = "http://localhost:8000"

async def start_valuation():
    async with httpx.AsyncClient() as client:
        # 평가 시작
        response = await client.post(
            f"{BASE_URL}/api/v1/valuation/start",
            json={
                "project_id": "your-project-id",
                "method": "dcf"
            }
        )
        print(response.json())

        # 진행 상황 조회
        response = await client.get(
            f"{BASE_URL}/api/v1/valuation/progress",
            params={
                "project_id": "your-project-id",
                "method": "dcf"
            }
        )
        print(response.json())
```

### cURL

```bash
# 평가 시작
curl -X POST http://localhost:8000/api/v1/valuation/start \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "your-project-id",
    "method": "dcf"
  }'

# 진행 상황 조회
curl http://localhost:8000/api/v1/valuation/progress?project_id=your-project-id&method=dcf

# 단계 전진
curl -X POST http://localhost:8000/api/v1/valuation/advance-step \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "your-project-id",
    "method": "dcf"
  }'

# 상태 업데이트
curl -X POST http://localhost:8000/api/v1/valuation/update-status \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "your-project-id",
    "method": "dcf",
    "status": "completed",
    "step": 14
  }'
```

### JavaScript (fetch)

```javascript
// 평가 시작
const startResponse = await fetch('/api/v1/valuation/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    project_id: 'your-project-id',
    method: 'dcf'
  })
});
const startData = await startResponse.json();

// 진행 상황 조회
const progressResponse = await fetch(
  '/api/v1/valuation/progress?project_id=your-project-id&method=dcf'
);
const progressData = await progressResponse.json();

console.log(`진행률: ${progressData.progress}%`);
console.log(`현재 단계: ${progressData.current_step}/14`);
```

---

## 에러 처리

### 에러 응답 형식

```json
{
  "detail": "에러 메시지"
}
```

### 주요 에러 케이스

| HTTP Status | 상황 | detail |
|-------------|------|--------|
| `400` | 최대 단계 도달 | Already at maximum step: 14 |
| `400` | 평가 미완료 | Valuation is not completed yet. Current status: in_progress |
| `404` | 프로젝트 없음 | Project not found: {project_id} |
| `500` | 서버 오류 | Failed to start valuation: {error_message} |

---

## 테스트

### 테스트 스크립트 실행

```bash
cd valuation-platform/backend
python test_valuation_api.py
```

### 테스트 내용

1. 프로젝트 목록 조회
2. 평가 시작 (DCF)
3. 진행 상황 조회
4. 단계 전진 (5 → 6)
5. 상태 업데이트 (completed)
6. 최종 상태 확인
7. 상태 초기화

---

## 주의사항

1. **프로젝트 존재 확인**: 모든 엔드포인트에서 프로젝트가 존재하는지 먼저 확인합니다.

2. **유효한 method 값**: `dcf`, `relative`, `intrinsic`, `asset`, `inheritance_tax` 중 하나여야 합니다.

3. **단계 범위**: 1 ~ 14 범위 내에서만 설정 가능합니다.

4. **상태 전이**: 상태 전이는 임의로 설정 가능하지만, 일반적으로 다음 순서를 따릅니다:
   ```
   not_requested → pending → approved → in_progress → completed
   ```

5. **동시성**: 여러 평가법을 동시에 진행할 수 있습니다 (독립적 관리).

---

## 향후 개선 사항

1. **평가 결과 테이블**: 별도 테이블에서 평가 금액, 보고서 URL 관리
2. **인증/인가**: JWT 토큰 기반 인증 추가
3. **웹소켓**: 실시간 진행 상황 업데이트
4. **로깅**: 상세한 작업 로그 기록
5. **알림**: 평가 완료 시 이메일/SMS 알림

---

## 관련 파일

| 파일 | 설명 |
|------|------|
| `app/api/v1/endpoints/valuation.py` | API 엔드포인트 구현 |
| `app/db/supabase_client.py` | Supabase 클라이언트 |
| `database/migrations/add_method_status_fields.sql` | DB 마이그레이션 |
| `test_valuation_api.py` | 테스트 스크립트 |

---

## 문의

문제가 발생하면 다음을 확인하세요:

1. Supabase URL/KEY가 `.env`에 설정되어 있는가?
2. `projects` 테이블에 평가 상태 필드가 추가되었는가?
3. 프로젝트 ID가 올바른가?
4. method 값이 유효한가?

자세한 로그는 서버 콘솔에서 확인할 수 있습니다.
