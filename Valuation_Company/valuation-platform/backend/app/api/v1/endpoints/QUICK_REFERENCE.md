# Valuation API - Quick Reference

## API Base URL
```
http://localhost:8000/api/v1/valuation
```

## Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/start` | 평가 시작 |
| GET | `/progress` | 진행 상황 조회 |
| GET | `/result` | 평가 결과 조회 |
| POST | `/advance-step` | 단계 전진 (테스트) |
| POST | `/update-status` | 상태 업데이트 |

## Supported Methods

| method | 평가법 |
|--------|--------|
| `dcf` | DCF (현금흐름할인법) |
| `relative` | 상대가치평가법 |
| `intrinsic` | 본질가치평가법 |
| `asset` | 자산가치평가법 |
| `inheritance_tax` | 상증세법 평가법 |

## Status Values

| status | 의미 |
|--------|------|
| `not_requested` | 신청 안 함 (기본값) |
| `pending` | 승인 대기 중 |
| `approved` | 승인됨 |
| `in_progress` | 진행 중 |
| `completed` | 완료 |

## Step Range

- Min: 1
- Max: 14
- Progress: `(step / 14) * 100`

## Quick Examples

### Start Valuation
```bash
curl -X POST http://localhost:8000/api/v1/valuation/start \
  -H "Content-Type: application/json" \
  -d '{"project_id":"abc-123","method":"dcf"}'
```

### Get Progress
```bash
curl "http://localhost:8000/api/v1/valuation/progress?project_id=abc-123&method=dcf"
```

### Advance Step
```bash
curl -X POST http://localhost:8000/api/v1/valuation/advance-step \
  -H "Content-Type: application/json" \
  -d '{"project_id":"abc-123","method":"dcf"}'
```

### Update Status
```bash
curl -X POST http://localhost:8000/api/v1/valuation/update-status \
  -H "Content-Type: application/json" \
  -d '{"project_id":"abc-123","method":"dcf","status":"completed","step":14}'
```

## JavaScript Example

```javascript
// Start valuation
const start = await fetch('/api/v1/valuation/start', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({project_id: 'abc-123', method: 'dcf'})
});

// Get progress
const progress = await fetch('/api/v1/valuation/progress?project_id=abc-123&method=dcf');
const data = await progress.json();
console.log(`Progress: ${data.progress}%`);
```

## Common Responses

### Success
```json
{
  "status": "started",
  "project_id": "abc-123",
  "method": "dcf",
  "message": "DCF 평가가 시작되었습니다 (단계 5/14)"
}
```

### Error
```json
{
  "detail": "Project not found: abc-123"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request (invalid input) |
| 404 | Project Not Found |
| 500 | Internal Server Error |

## Testing

```bash
cd valuation-platform/backend
python test_valuation_api.py
```

## Documentation

- Full API Docs: `README_VALUATION_API.md`
- Implementation Report: `Human_ClaudeCode_Bridge/Reports/valuation_api_implementation_report.md`
