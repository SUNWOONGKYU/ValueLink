# JSON CRUD 작업 방법

> JSON 파일 CRUD 작업 시 반드시 이 방법을 따르세요.

---

## 핵심 원칙

```
✅ AI가 Edit 도구로 JSON 파일 직접 수정!
✅ JSON 파일 위치: method/json/data/in_progress/project_sal_grid.json
✅ 수정 후 반드시 저장 확인!
```

---

## JSON 파일 수정 프로세스

```
1. JSON 파일 읽기 (Read 도구)
     ↓
2. 해당 Task 객체 찾기
     ↓
3. 필드 값 수정 (Edit 도구)
     ↓
4. 저장 확인
```

---

## JSON 파일 위치

```
{project-root}/S0_Project-SAL-Grid_생성/method/json/data/in_progress/project_sal_grid.json
```

---

## JSON 파일 구조

```json
{
  "project_id": "프로젝트ID",
  "project_name": "프로젝트명",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "tasks": [
    {
      "task_id": "S1F1",
      "task_name": "로그인 페이지 구현",
      "stage": 1,
      "area": "F",
      "task_status": "Pending",
      "task_progress": 0,
      "verification_status": "Not Verified",
      ...
    }
  ]
}
```

---

## 읽기 (Read)

```javascript
const fs = require('fs');
const jsonPath = 'S0_Project-SAL-Grid_생성/method/json/data/in_progress/project_sal_grid.json';
const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

// tasks 배열에서 특정 Task 찾기
const task = data.tasks.find(t => t.task_id === 'S1F1');
```

---

## 수정 (Update)

```javascript
// 특정 Task 찾기
const taskIndex = data.tasks.findIndex(t => t.task_id === 'S1F1');

if (taskIndex !== -1) {
    // 필드 수정
    data.tasks[taskIndex].task_status = 'Completed';
    data.tasks[taskIndex].task_progress = 100;
    data.tasks[taskIndex].verification_status = 'Verified';
}

// updated_at 갱신
data.updated_at = new Date().toISOString();
```

---

## 쓰기 (Write)

```javascript
// JSON 파일 저장 (pretty print)
fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2), 'utf-8');
```

---

## 주의사항

- JSON 문법 오류 방지 (쉼표, 중괄호 등)
- UTF-8 인코딩 유지
- tasks 배열 구조 유지
- 수정 후 반드시 저장 확인
- `updated_at` 필드 갱신 잊지 말기

---

## Claude Code Edit 도구 사용 시

Claude Code의 Edit 도구로 직접 수정할 때:

```
1. Read 도구로 JSON 파일 읽기
2. 수정할 Task 객체의 필드 위치 파악
3. Edit 도구로 해당 필드 값만 변경
4. JSON 문법이 깨지지 않도록 주의
```

**예시 - task_status 변경:**
```json
// 변경 전
"task_status": "Pending",

// 변경 후
"task_status": "Completed",
```

---

## 상세 규칙

자세한 내용은 `.claude/rules/04_grid-writing-json.md` 참조
