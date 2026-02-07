# Process Monitor - Claude Code 구현 가이드

> 다른 Claude Code가 이 시스템을 이해하고 구현할 수 있도록 작성된 문서

---

## 핵심 개념

```
┌─────────────────────────────────────────────────────────────┐
│  SSAL Works 플랫폼 = 중앙 서버                              │
│  → 모든 사용자의 진행률을 SSAL Works DB에 저장               │
│  → ssalworks.com에서 진행률 표시                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  사용자 PC (이 프로젝트)                                     │
│  → git commit 시 진행률 계산                                │
│  → SSAL Works DB에 업로드                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 데이터 흐름

```
git commit
    ↓
pre-commit hook 실행
    ↓
build-progress.js (Process_Monitor/)
    → Process/ 폴더 스캔
    → 진행률 계산
    → data/phase_progress.json 생성
    ↓
upload-progress.js (scripts/)
    → .ssal-project.json에서 project_id 읽기
    → phase_progress.json 읽기
    → SSAL Works DB에 PATCH 요청
    ↓
SSAL Works DB 업데이트
    ↓
ssalworks.com에서 진행률 표시
```

---

## 파일 역할

| 파일 | 위치 | 역할 |
|------|------|------|
| `build-progress.js` | Process_Monitor/ | 진행률 계산 (로컬 실행) |
| `upload-progress.js` | **scripts/** | DB 업로드 (실제 사용) |
| `upload-progress.js` | Process_Monitor/ | 템플릿 (참고용) |
| `phase_progress.json` | Process_Monitor/data/ | 계산 결과 (자동 생성) |
| `.ssal-project.json` | 프로젝트 루트 | 프로젝트 설정 (SSAL Works 제공) |

**중요:** 실제 실행되는 파일은 `scripts/upload-progress.js`

---

## Supabase 정보 출처

```javascript
// scripts/upload-progress.js 내부에 하드코딩됨

// SSAL Works Supabase 설정 (고정 - 모든 사용자 동일)
const SUPABASE_URL = 'https://zwjmfewyshhwpgwdtrus.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

// Project ID만 프로젝트마다 다름
// → .ssal-project.json에서 읽음
```

**왜 하드코딩?**
- SUPABASE_URL, KEY = SSAL Works 플랫폼 고정값 (변경 없음)
- PROJECT_ID = 프로젝트마다 다름 (파일에서 읽음)

---

## .ssal-project.json 파일

**생성 주체:** SSAL Works 플랫폼 (사용자가 직접 만들지 않음)

**생성 시점:** SSAL Works에서 프로젝트 등록 시

**위치:** 프로젝트 루트 디렉토리

**구조:**
```json
{
    "project_id": "2512000006TH-P001",
    "project_name": "ValueLink",
    "owner_email": "user@example.com",
    "created_at": "2026-01-12T14:18:50.876Z",
    "version": "1.0.0"
}
```

**핵심:** `project_id`만 사용됨 → SSAL Works DB에서 이 ID로 데이터 저장/조회

---

## Pre-commit Hook 설정

**위치:** `.git/hooks/pre-commit`

**내용:**
```bash
#!/bin/sh
PROJECT_ROOT="$(git rev-parse --show-toplevel)"

node "$PROJECT_ROOT/Process_Monitor/build-progress.js"
git add "$PROJECT_ROOT/Process_Monitor/data/phase_progress.json" 2>/dev/null
node "$PROJECT_ROOT/scripts/upload-progress.js"

exit 0
```

**참고:** `pre-commit-hook-example.sh` 파일 참조

---

## 구현 시 주의사항

### 1. 파일 수정 금지
- `scripts/upload-progress.js` 내 SUPABASE_URL, KEY 변경 금지
- `.ssal-project.json` 직접 생성/수정 금지 (SSAL Works가 관리)

### 2. 경로 주의
```
✅ Process_Monitor/build-progress.js
✅ scripts/upload-progress.js
❌ Process_Monitor/upload-progress.js (템플릿, 실행 안 함)
```

### 3. 진행률 계산 로직 (build-progress.js)
- P0~S0: 폴더 내 파일 존재 여부로 계산
- S1~S5: `grid_records/*.json`에서 `task_status: "Completed"` 비율

---

## 테스트 방법

```bash
# 1. 진행률 계산 테스트
node Process_Monitor/build-progress.js

# 2. DB 업로드 테스트
node scripts/upload-progress.js

# 3. DB에서 데이터 확인
curl -s "https://zwjmfewyshhwpgwdtrus.supabase.co/rest/v1/project_phase_progress?project_id=eq.2512000006TH-P001&select=phase_code,progress" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3am1mZXd5c2hod3Bnd2R0cnVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzU3MTU1MSwiZXhwIjoyMDc5MTQ3NTUxfQ.ZMNl9_lCJQMG8lC0MEQjHrLEuYbCFJYsVsBIzvwnj1s"
```

---

## 문제 해결

| 문제 | 원인 | 해결 |
|------|------|------|
| "project_id 없음" 에러 | .ssal-project.json 없음 | SSAL Works에서 프로젝트 등록 |
| 업로드 실패 | 네트워크 또는 권한 | SUPABASE_KEY 확인 |
| 진행률 0% 표시 | 데이터 없음 | upload-progress.js 실행 |

---

## 요약

```
1. .ssal-project.json = SSAL Works가 생성 (project_id 포함)
2. SUPABASE_URL, KEY = 코드에 하드코딩 (고정값)
3. 실행 파일 = scripts/upload-progress.js
4. 템플릿 파일 = Process_Monitor/upload-progress.js
5. git commit 시 자동 업로드 = pre-commit hook
```
