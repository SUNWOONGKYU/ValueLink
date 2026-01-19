# Work Log - Dev Package CSV to JSON Migration

## 작업 날짜: 2025-01-02

---

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
