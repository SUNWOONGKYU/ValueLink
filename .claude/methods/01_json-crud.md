# JSON CRUD 작업 방법

> JSON 파일 CRUD 작업 시 반드시 이 방법을 따르세요.

---

## 핵심 원칙

```
✅ AI가 Edit 도구로 JSON 파일 직접 수정!
✅ 프로젝트 메타데이터: method/json/data/index.json
✅ 개별 Task 파일: method/json/data/grid_records/{TaskID}.json
✅ 수정 후 반드시 저장 확인!
```

---

## JSON 폴더 구조 (개별 파일 방식)

```
{project-root}/Process/S0_Project-SAL-Grid_생성/method/json/data/
├── index.json             ← 프로젝트 메타데이터 + task_ids 배열
└── grid_records/          ← 개별 Task JSON 파일
    ├── S1BI1.json
    ├── S1BI2.json
    ├── S2F1.json
    └── ... (Task ID별 파일)
```

---

## index.json 구조

```json
{
  "project_id": "프로젝트ID",
  "project_name": "프로젝트명",
  "total_tasks": 66,
  "task_ids": ["S1BI1", "S1BI2", "S1D1", ...]
}
```

---

## 개별 Task JSON 구조 (grid_records/{TaskID}.json)

```json
{
  "task_id": "S1F1",
  "task_name": "로그인 페이지 구현",
  "stage": 1,
  "area": "F",
  "task_status": "Pending",
  "task_progress": 0,
  "verification_status": "Not Verified",
  "dependencies": "",
  "task_instruction": "Task 수행 지침",
  "task_agent": "frontend-developer",
  "verification_instruction": "검증 지침",
  "verification_agent": "code-reviewer",
  ...
}
```

---

## JSON 파일 수정 프로세스

```
1. 해당 Task의 JSON 파일 읽기 (Read 도구)
   → grid_records/{TaskID}.json
     ↓
2. 필드 값 수정 (Edit 도구)
     ↓
3. 저장 확인
```

---

## 읽기 (Read)

```javascript
const fs = require('fs');
const path = require('path');

// index.json 읽기 (Task ID 목록 확인)
const indexPath = path.join(__dirname, 'Process/S0_Project-SAL-Grid_생성/method/json/data/index.json');
const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));

// 개별 Task 파일 읽기
const taskPath = path.join(__dirname, 'Process/S0_Project-SAL-Grid_생성/method/json/data/grid_records/S1F1.json');
const taskData = JSON.parse(fs.readFileSync(taskPath, 'utf-8'));
```

---

## 수정 (Update)

```javascript
// 개별 Task 파일 직접 수정
taskData.task_status = 'Completed';
taskData.task_progress = 100;
taskData.verification_status = 'Verified';
taskData.updated_at = new Date().toISOString();
```

---

## 쓰기 (Write)

```javascript
// 개별 Task JSON 파일 저장 (pretty print)
fs.writeFileSync(taskPath, JSON.stringify(taskData, null, 2), 'utf-8');
```

---

## Task 추가 시

```javascript
// 1. index.json의 task_ids 배열에 추가
indexData.task_ids.push('S4F5');
indexData.total_tasks = indexData.task_ids.length;
fs.writeFileSync(indexPath, JSON.stringify(indexData, null, 2), 'utf-8');

// 2. 새 Task JSON 파일 생성
const newTaskData = {
    task_id: 'S4F5',
    task_name: 'Task 이름',
    stage: 4,
    area: 'F',
    task_status: 'Pending',
    task_progress: 0,
    verification_status: 'Not Verified'
};
const newTaskPath = path.join(__dirname, 'Process/S0_Project-SAL-Grid_생성/method/json/data/grid_records/S4F5.json');
fs.writeFileSync(newTaskPath, JSON.stringify(newTaskData, null, 2), 'utf-8');
```

---

## 주의사항

- JSON 문법 오류 방지 (쉼표, 중괄호 등)
- UTF-8 인코딩 유지
- index.json과 grid_records/ 동기화 유지
- 수정 후 반드시 저장 확인

---

## Claude Code Edit 도구 사용 시

Claude Code의 Edit 도구로 직접 수정할 때:

```
1. Read 도구로 해당 Task JSON 파일 읽기
   → grid_records/{TaskID}.json
2. 수정할 필드 위치 파악
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
