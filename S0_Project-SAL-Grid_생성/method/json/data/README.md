# JSON Data Folder Structure

> Project SAL Grid JSON 데이터 관리 가이드

---

## 폴더 구조

```
data/
├── in_progress/                ← 진행 중인 프로젝트 (Viewer가 읽는 폴더)
│   └── project_sal_grid.json   ← 현재 프로젝트의 Task Grid (전체 요약)
│
├── grid_records/               ← 개별 Task 상세 데이터
│   ├── _TEMPLATE.json          ← Task JSON 템플릿
│   ├── S1F1.json               ← 개별 Task 상세 정보
│   └── ...
│
├── completed/                  ← 완료된 프로젝트 (보관용)
│   └── [project]_sal_grid.json
│
├── users/                      ← 사용자별 데이터 (다중 사용자용)
│   └── [email]/
│       └── project_sal_grid.json
│
├── index.json                  ← 전체 Task 인덱스 (요약)
│
└── README.md                   ← 이 파일
```

---

## 파일 역할 구분

| 파일/폴더 | 역할 | 용도 |
|-----------|------|------|
| `in_progress/project_sal_grid.json` | **Viewer가 읽는 파일** | Task 목록 표시 |
| `grid_records/{TaskID}.json` | 개별 Task 상세 데이터 | Task별 전체 22개 속성 저장 |
| `index.json` | 전체 Task 인덱스 | Task 목록 요약 (빠른 조회용) |
| `completed/` | 완료된 프로젝트 보관 | 히스토리 관리 |
| `users/` | 다중 사용자 지원 | 사용자별 프로젝트 분리 |

---

## 사용 방법

### 1. 진행 중인 프로젝트

- `in_progress/` 폴더에 `project_sal_grid.json` 파일을 저장
- **Viewer는 이 폴더의 JSON만 로드**
- Task 완료 시 JSON 파일 업데이트

### 2. 개별 Task 상세 관리

- `grid_records/` 폴더에 `{TaskID}.json` 파일로 개별 저장
- `_TEMPLATE.json`을 복사하여 새 Task 생성
- Task당 전체 22개 속성 저장 가능

### 3. 프로젝트 완료 시

프로젝트가 완료되면 JSON을 `completed/` 폴더로 이동:

```bash
# 예시: 프로젝트명을 붙여서 이동
mv in_progress/project_sal_grid.json completed/myproject_sal_grid.json
```

### 4. 새 프로젝트 시작 시

1. 기존 JSON이 있다면 `completed/`로 이동
2. 새 `project_sal_grid.json`을 `in_progress/`에 생성

---

## Viewer 동작

| Viewer | 읽는 폴더 | 설명 |
|--------|----------|------|
| `viewer_json.html` | `in_progress/` | 진행 중인 프로젝트만 표시 |
| `viewer_mobile_json.html` | `in_progress/` | 모바일용 Viewer |

**경로**: `../method/json/data/in_progress/project_sal_grid.json`

---

## JSON 파일 구조

### project_sal_grid.json (Viewer용)

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
      ...
    }
  ]
}
```

### grid_records/{TaskID}.json (개별 Task 상세)

```json
{
  "task_id": "S1F1",
  "task_name": "Task 이름",
  "stage": 1,
  "area": "F",
  "task_status": "Pending",
  "task_progress": 0,
  "verification_status": "Not Verified",
  "dependencies": "-",
  "task_instruction": "sal-grid/task-instructions/S1F1_instruction.md",
  "task_agent": "frontend-developer",
  "tools": "",
  "execution_type": "AI-Only",
  "generated_files": "",
  "modification_history": "",
  "verification_instruction": "sal-grid/verification-instructions/S1F1_verification.md",
  "verification_agent": "code-reviewer",
  "test_result": "",
  "build_verification": "",
  "integration_verification": "",
  "blockers": "",
  "comprehensive_verification": "",
  "remarks": ""
}
```

---

## 여러 프로젝트 관리

여러 프로젝트를 순차적으로 진행할 경우:

1. **현재 프로젝트**: `in_progress/project_sal_grid.json`
2. **이전 프로젝트**: `completed/project1_sal_grid.json`
3. **더 이전**: `completed/project2_sal_grid.json`

**핵심**: `in_progress/`에는 항상 하나의 프로젝트만 존재

---

## 주의사항

- `in_progress/` 폴더가 비어있으면 Viewer에서 "프로젝트 없음" 메시지 표시
- JSON 파일명은 반드시 `project_sal_grid.json`으로 유지 (in_progress 내)
- 완료된 프로젝트는 구분을 위해 프로젝트명 접두사 권장
- JSON 문법 오류 시 Viewer에서 로드 실패
- `grid_records/` 폴더의 파일명은 Task ID와 동일하게 유지 (예: `S1F1.json`)
