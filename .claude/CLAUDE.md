# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🚨🚨🚨 7대 작업 규칙 - 반드시 먼저 확인! 🚨🚨🚨

> **⛔ 파일 생성/저장 전 반드시 해당 규칙 파일을 읽어야 함!**
> **⛔ 규칙 확인 없이 폴더 생성/파일 저장 절대 금지!**
> **⛔ "이렇게 하면 되겠지" 추측 금지 - 규칙 파일이 정답!**

| # | 규칙 파일 | 확인 시점 | 내용 |
|---|----------|----------|------|
| 1 | `01_file-naming.md` | 파일명 정할 때 | 파일 명명 규칙 |
| 2 | `02_save-location.md` | **파일 저장할 때** ⭐ | 저장 위치 규칙 |
| 3 | `03_area-stage.md` | 폴더 선택할 때 | Area/Stage 매핑 |
| 4 | `04_grid-writing-json.md` | **Grid/JSON/Viewer 작업할 때** ⭐ | Grid 작성 + JSON CRUD + **Viewer 확인** |
| 5 | `05_execution-process.md` | Task 실행할 때 | 6단계 실행 프로세스 |
| 6 | `06_verification.md` | 검증할 때 | 검증 기준 |
| 7 | `07_task-crud.md` | **Task 추가/삭제/수정할 때** ⭐ | Task CRUD 프로세스 |

**📁 위치:** `.claude/rules/`

---

## 📊 DB vs JSON 데이터 구분 (핵심 개념)

> **이 구분을 이해해야 viewer 관련 작업 시 혼란이 없음!**

### 두 가지 Viewer

| Viewer | 데이터 소스 | 용도 |
|--------|------------|------|
| `viewer_database.html` | SSAL Works DB | **예시** (참고용, 고정) |
| `viewer_json.html` | 본인 JSON 파일 | **내 프로젝트** (진행 중) |

### 작동 원리

```
┌─────────────────────────────────────────────────────────────┐
│  viewer_database.html                                       │
│  → SSAL Works 프로젝트 데이터 = "예시"로 고정                 │
│  → "완성된 프로젝트는 이렇게 보입니다" 참고용                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  viewer_json.html ⭐ 주로 사용                               │
│  → 내가 진행 중인 프로젝트 데이터                              │
│  → Task 완료할 때마다 업데이트됨                              │
│  → 경로: method/json/data/in_progress/project_sal_grid.json │
└─────────────────────────────────────────────────────────────┘
```

### ⚠️ 일반 이용자는 JSON 사용

```
✅ 내 프로젝트 진행 상황 = JSON 파일 (method/json/data/in_progress/project_sal_grid.json)
✅ Task 완료 시 = JSON 파일 업데이트
✅ 진행 현황 확인 = viewer_json.html
✅ 프로젝트 완료 시 = completed/ 폴더로 이동

❌ Supabase DB = 사용하지 않음 (SSAL Works 예시용)
```

### 📂 JSON 폴더 구조

```
method/json/data/
├── in_progress/        ← Viewer가 읽는 폴더 (진행 중)
│   └── project_sal_grid.json
└── completed/          ← 완료된 프로젝트 보관
    └── [project]_sal_grid.json
```

---

## ⛔⛔⛔ 절대 규칙 - 위반 시 작업 중단! ⛔⛔⛔

### 절대 규칙 1: 폴더 임의 생성 금지

```
🚫 폴더를 절대로 임의 생성하지 마라!
🚫 기존 폴더 확인 없이 새 폴더 만들면 파일 추적 불가!
🚫 "일단 만들고 나중에 정리" = 절대 금지!
```

**폴더 생성이 필요할 때 필수 프로세스:**

1. **즉시 작업 중단**
2. **기존 폴더 확인** - 정말 적절한 폴더가 없는가?
3. **사용자에게 승인 요청** (아래 양식 필수)
4. **승인 받은 후에만 폴더 생성**

**승인 요청 양식 (필수):**
```
"폴더 생성 승인 요청

📁 생성할 폴더: [전체 경로]
📝 생성 이유: [왜 이 폴더가 필요한지 구체적으로]
🔍 대안 검토: [기존 폴더 중 사용 가능한 것이 없는 이유]
📂 기존 폴더 목록: [확인한 유사 폴더들]

승인하시겠습니까?"
```

**❌ 절대 금지 행동:**
- 승인 없이 폴더 생성
- 기존 폴더 확인 없이 새 폴더 생성
- 오타나 유사 이름으로 중복 폴더 생성 (sal-grid vs ssal-grid 같은 실수)

---

### 절대 규칙 2: 일반 작업 - 검증 및 문서화 필수

> **적용 대상**: Project SAL Grid Task가 아닌 모든 요청 (한 건씩 처리)

```
🚫 작업만 하고 검증 없이 완료 보고 금지!
🚫 검증 없이 work_logs 업데이트 금지!
🚫 Reports 폴더 저장 생략 금지!
```

**필수 프로세스 (단순 - 4단계):**
```
1. 작업 수행
     ↓
2. 검증 에이전트 투입 (Task tool 사용)
   - 적합한 서브에이전트 선택 (code-reviewer, qa-specialist 등)
   - 검증 결과 받기
     ↓
3. 문서화 (두 곳 모두 필수!)
   ✅ .claude/work_logs/current.md - 작업 내역 기록
   ✅ Human_ClaudeCode_Bridge/Reports/{작업명}_report.json - 결과 저장
     ↓
4. 사용자에게 완료 보고
```

---

### 절대 규칙 3: Project SAL Grid Task - 프로세스 및 상태 전이 규칙

> **적용 대상**: Project SAL Grid의 Task 실행 (한 번에 여러 개 처리 가능)
> **핵심**: 6단계 프로세스 + 상태 전이 규칙 반드시 준수!

```
🚫 이 프로세스를 건너뛰면 Grid 데이터가 엉망이 됨!
🚫 상태 전이 순서 반드시 지켜야 함!
🚫 여러 Task를 동시에 처리할 때 각 Task마다 상태 관리 필수!
```

**📋 Task 실행 6단계 프로세스:**

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Task Instruction 읽기                              │
│  → sal-grid/task-instructions/{TaskID}_instruction.md       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: 규칙 파일 확인                                      │
│  → .claude/rules/ 폴더의 관련 규칙 읽기                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Grid 상태 업데이트 (JSON)                           │
│  → task_status: 'Pending' → 'In Progress'                   │
│  → JSON 파일 UPDATE                                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Task Agent로 작업 수행                              │
│  → Task Instruction에 따라 작업 실행                         │
│  → 작업 완료 시: task_status: 'In Progress' → 'Executed'    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Verification Agent 투입 (서브에이전트)              │
│  → verification_status: 'Not Verified' → 'In Review'        │
│  → Verification Instruction에 따라 검증                      │
│  → 검증 결과: 'Verified' 또는 'Needs Fix'                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: 최종 상태 업데이트 (JSON)                           │
│  → verification_status: 'Verified'일 때만                    │
│  → task_status: 'Executed' → 'Completed'                    │
│  → work_logs, Reports 저장                                  │
└─────────────────────────────────────────────────────────────┘
```

**📊 상태 전이 규칙 (순서 반드시 준수!):**

```
task_status 전이:
┌─────────┐    ┌─────────────┐    ┌──────────┐    ┌───────────┐
│ Pending │ →  │ In Progress │ →  │ Executed │ →  │ Completed │
└─────────┘    └─────────────┘    └──────────┘    └───────────┘
                                       ↑              ↑
                                   작업 완료      Verified 후만!

verification_status 전이:
┌──────────────┐    ┌───────────┐    ┌──────────┐
│ Not Verified │ →  │ In Review │ →  │ Verified │
└──────────────┘    └───────────┘    └──────────┘
                                           ↓
                                      Needs Fix (실패 시)
```

**⚠️ 핵심 규칙:**
- **Executed** = 작업은 끝났지만 검증 전 상태
- **Completed** = 검증(Verified)까지 완료된 상태
- **Completed는 Verified일 때만 가능!**
- **상태 건너뛰기 금지** (Pending → Completed 불가!)
- **각 Task마다 상태 업데이트 필수** (여러 개 처리 시)

**❌ 절대 금지 행동:**
- Executed 없이 바로 Completed 처리
- 검증 없이 Verified 표시
- 상태 전이 순서 건너뛰기
- Verification Agent 투입 생략
- JSON 상태 업데이트 생략
- **검증만 하고 결과 기록 생략** ⭐ 신규 추가

**⭐ 검증 결과 기록 필수 (절대 생략 금지!):**

```
🚫 검증만 수행하고 기록 안 하면 무의미!
🚫 "검증했습니다" 말만 하고 JSON에 기록 안 하면 안 됨!
✅ 검증 결과는 JSON 파일에 기록!
```

**검증 후 필수 기록 위치:**
```
JSON 파일 (method/json/data/in_progress/project_sal_grid.json)
   → verification_status: 'Verified' 또는 'Needs Fix'
   → test_result: 테스트 결과
   → build_verification: 빌드 검증
   → integration_verification: 통합 검증
   → blockers: 차단 요소
   → comprehensive_verification: 종합 결과
```

**검증 기록 체크리스트:**
- [ ] JSON에 verification_status 업데이트했는가?
- [ ] JSON에 검증 관련 필드(test_result, build_verification 등) 저장했는가?

---

### 절대 규칙 4: Stage 폴더에 먼저 저장 → Pre-commit Hook 자동 복사

> **적용 대상**: Frontend, Backend_APIs, Security, Backend_Infra, External 코드 파일 생성/수정 시

```
✅ Stage 폴더에 먼저 저장 (원본, 프로세스 관리용)
✅ git commit 시 Pre-commit Hook이 자동으로 루트 폴더에 복사
🚫 수동으로 이중 저장 금지 - 자동화에 맡겨라!
```

**저장 순서:**

```
1. Stage 폴더에 저장 (원본)
      ↓
2. git commit 실행
      ↓
3. Pre-commit Hook 자동 실행 (scripts/sync-to-root.js)
      ↓
4. 루트 폴더로 자동 복사 (배포용)
```

**Stage → 루트 매핑:**
| Area | Stage 폴더 | 루트 폴더 (자동 복사) |
|------|-----------|---------------------|
| F (Frontend) | `S?_*/Frontend/` | `pages/` |
| BA (Backend_APIs) | `S?_*/Backend_APIs/` | `api/Backend_APIs/` |
| S (Security) | `S?_*/Security/` | `api/Security/` |
| BI (Backend_Infra) | `S?_*/Backend_Infra/` | `api/Backend_Infra/` |
| E (External) | `S?_*/External/` | `api/External/` |
| **S0 Viewer** | `S0_*/viewer/` | `viewer/` |
| **S0 JSON** | `S0_*/method/json/data/` | `method/json/data/` |

**완료 보고 양식:**
```
"코드 파일 저장 완료

📁 Stage 저장: S2_개발-1차/Frontend/pages/auth/login.html (원본)
📁 자동 복사: pages/auth/login.html (배포용)

✅ git commit 시 자동 동기화됨"
```

**❌ 절대 금지 행동:**
- 루트 폴더에 직접 저장 (Stage 거치지 않고)
- 수동으로 이중 저장 (자동화 무시)

**⚠️ 폴더명 변경 금지:** Vercel이 `api` 이름을 인식함

**상세 규칙:** `.claude/rules/02_save-location.md` 참조

---

### 절대 규칙 5: Task 완료/수정 시 Grid 자동 업데이트 ⭐ 신규

> **적용 대상**: SAL Grid Task 작업 완료 또는 버그 수정 시

```
🚫 Task 작업만 하고 Grid 업데이트 없이 끝내지 마라!
🚫 "작업 완료했습니다" 말만 하고 JSON 업데이트 안 하면 안 됨!
✅ 작업 완료 후 반드시 JSON 파일 업데이트!
```

**업데이트 시점:**
| 상황 | 업데이트 필드 |
|------|-------------|
| Task 완료 | `task_status`, `task_progress`, `generated_files`, `remarks` |
| 버그 수정 | `modification_history`, `remarks`, `updated_at` |

**필수 프로세스:**
```
Task 작업 완료
     ↓
JSON 파일 (method/json/data/in_progress/project_sal_grid.json) 업데이트
     ↓
work_logs/current.md 기록
     ↓
완료 보고
```

**상세 규칙:** `.claude/rules/04_grid-writing-json.md` 섹션 8 참조

---

### 절대 규칙 6: 파괴적 작업은 반드시 사용자 사전 승인 필수 ⭐ 신규

> **적용 대상**: DB 테이블 삭제/변경, 데이터 삭제, 스키마 변경 등 되돌릴 수 없는 작업

```
🚫 DROP TABLE, DELETE, TRUNCATE 등 데이터 파괴 작업을 사용자 승인 없이 절대 실행 금지!
🚫 "충돌 해결을 위해 삭제했습니다" = 절대 금지! 사전 승인 없는 삭제는 어떤 이유로도 허용 안 됨!
🚫 ALTER TABLE로 컬럼 삭제, 타입 변경 등도 사전 승인 필수!
✅ 파괴적 작업이 필요하면 반드시 사용자에게 먼저 보고하고 승인을 받아야 함!
```

**파괴적 작업 목록 (사전 승인 필수):**
| 작업 | 설명 | 위험도 |
|------|------|--------|
| `DROP TABLE` | 테이블 삭제 | **치명적** |
| `DELETE FROM` | 데이터 삭제 | **치명적** |
| `TRUNCATE TABLE` | 테이블 데이터 전체 삭제 | **치명적** |
| `ALTER TABLE DROP COLUMN` | 컬럼 삭제 | **높음** |
| `ALTER TABLE ALTER COLUMN` | 컬럼 타입 변경 | **높음** |
| `git push --force` | 원격 히스토리 덮어쓰기 | **높음** |
| `git reset --hard` | 로컬 변경 전체 삭제 | **높음** |
| `rm -rf` | 파일/폴더 재귀 삭제 | **높음** |

**승인 요청 양식 (필수):**
```
"⚠️ 파괴적 작업 승인 요청

🔴 작업 내용: [구체적 SQL/명령어]
📊 영향 범위: [영향 받는 테이블/데이터/행 수]
💡 대안: [비파괴적 대안이 있는지]
⚠️ 복구 방법: [실행 후 복구 가능 여부]

승인하시겠습니까?"
```

**올바른 프로세스:**
```
충돌/문제 발생
     ↓
비파괴적 대안 먼저 검토 (ALTER TABLE ADD, CREATE TABLE IF NOT EXISTS 등)
     ↓
대안 불가 시 → 사용자에게 상황 보고 + 승인 요청
     ↓
승인 받은 후에만 실행
     ↓
실행 전 백업 (SELECT INTO, pg_dump 등)
     ↓
파괴적 작업 실행
```

**❌ 절대 금지 행동:**
- 사용자 승인 없이 테이블 삭제
- 사용자 승인 없이 데이터 삭제
- "충돌 해결"을 이유로 임의 삭제
- 백업 없이 파괴적 작업 실행

---

## 📘 작업 방법 (Methods)

> **특정 작업 수행 시 반드시 해당 방법을 따라야 함!**

| # | 방법 파일 | 적용 시점 | 핵심 |
|---|----------|----------|------|
| 1 | `01_json-crud.md` | **JSON CRUD 작업 시** | AI가 Edit 도구로 직접 수정 |

**📁 위치:** `.claude/methods/`

### JSON CRUD 작업 시 필수 준수

```
✅ AI가 Edit 도구로 JSON 파일 직접 수정!
✅ JSON 파일 위치: method/json/data/in_progress/project_sal_grid.json
✅ 수정 후 반드시 저장 확인!
```

**JSON 파일 수정 프로세스:**
```
1. JSON 파일 읽기 (Read 도구)
     ↓
2. 해당 Task 객체 찾기
     ↓
3. 필드 값 수정 (Edit 도구)
     ↓
4. 저장 확인
```

**⚠️ JSON 수정 시 주의사항:**
- JSON 문법 유지 (쉼표, 중괄호 등)
- UTF-8 인코딩 유지
- tasks 배열 구조 유지

---

## 📊 Progress Monitor - DB 업로드 (필수!) ⭐

> **웹에서 개인별 진행률을 표시하려면 반드시 설정해야 함!**

### 왜 필수인가?

```
❌ 로컬 JSON만 생성 → 웹에서 개인별 진행률 표시 불가
✅ DB에 업로드 → 웹에서 로그인한 사용자별 진행률 표시
```

### 필수 설정

1. **Supabase 테이블 생성**: `Development_Process_Monitor/DB_Method/create_table.sql` 실행
2. **환경변수 설정**: `.env` 파일에 Supabase URL/KEY 추가
3. **업로드 스크립트 배치**: `DB_Method/upload-progress.js` → `scripts/`에 복사
4. **pre-commit hook 설정**: git commit 시 자동 업로드

**상세 가이드:** `Development_Process_Monitor/DB_Method/README.md`

### 작동 흐름

```
git commit
    ↓
build-progress.js (진행률 계산)
    ↓
upload-progress.js (DB 업로드) ← 필수!
    ↓
웹에서 loadProjectProgress() (DB 조회)
    ↓
사이드바 진행률 표시
```

---

## 📋 기타 참조 문서

### AI 12대 준수사항
> `.claude/compliance/AI_12_COMPLIANCE.md`

### SAL Grid 매뉴얼 (v4.0 일반화 버전)
> `S0_Project-SAL-Grid_생성/manual/PROJECT_SAL_GRID_MANUAL.md`
> - **Task 데이터 저장: JSON Method 사용**
> - 27개 섹션으로 구성된 완전 매뉴얼

### Progress Monitor DB Method (필수!)
> `Development_Process_Monitor/DB_Method/README.md`
> - **진행률 표시: DB 업로드 필수**
> - 웹에서 개인별 진행률 표시를 위해 반드시 설정

### 주의사항
> `.claude/CAUTION.md` (일반 주의사항, 개발 TODO)

---

## 🌾 세션 시작 시 확인

### 1. 작업 기록
`.claude/work_logs/current.md` 🔴 최우선

### 2. 이전 작업 결과
`Human_ClaudeCode_Bridge/Reports/` 확인

### 3. 프로젝트 상태
- `P0_작업_디렉토리_구조_생성/Project_Status.md`
- `P0_작업_디렉토리_구조_생성/Project_Directory_Structure.md`

---

## 📂 웹 배포 파일 업데이트

Order Sheet, 안내문, Manual 수정 시:
```bash
node scripts/build-web-assets.js
```

---

## 🚀 S0 완료 후: GitHub Pages로 Viewer 배포 ⭐

> **S0 (Project SAL Grid 생성)이 완료되면 Viewer를 배포하여 웹에서 확인 가능!**
> **Claude Code가 자동으로 수행 - 사용자는 GitHub 계정만 있으면 됨**

### 배포 전 사전 조건 확인

**Claude Code가 먼저 확인할 것:**

```bash
# 1. GitHub CLI 설치 확인
gh --version

# 2. GitHub 로그인 상태 확인
gh auth status
```

**❌ 설치 안 됨 또는 로그인 안 됨 → 사용자에게 안내:**

```
"GitHub Pages 배포를 위해 사전 설정이 필요합니다.

1. GitHub CLI 설치:
   - Windows: winget install GitHub.cli
   - Mac: brew install gh
   - 또는: https://cli.github.com/ 에서 다운로드

2. GitHub 로그인:
   gh auth login
   (브라우저에서 인증 진행)

설정 완료 후 '배포 진행해줘'라고 말씀해주세요."
```

### 배포 프로세스 (Claude Code가 자동 수행)

**✅ 사전 조건 충족 시 Claude Code가 실행:**

```bash
# Step 1: Git 초기화 (없으면)
git init

# Step 2: 모든 파일 커밋
git add .
git commit -m "Initial commit: Project SAL Grid setup complete"

# Step 3: GitHub 레포지토리 생성 + 푸시
gh repo create {프로젝트명} --public --source=. --push

# Step 4: GitHub Pages 활성화
gh api repos/{owner}/{repo}/pages -X POST -f source='{"branch":"main","path":"/"}'
```

**⚠️ Step 4 실패 시 대안:**
```
"GitHub Pages 자동 활성화가 안 됩니다. 수동으로 설정해주세요:

1. https://github.com/{username}/{repo}/settings/pages 접속
2. Source: 'Deploy from a branch' 선택
3. Branch: 'main', Folder: '/ (root)' 선택
4. Save 클릭

설정 완료 후 알려주세요."
```

### 배포 완료 후 안내

```
"🎉 배포 완료!

📊 Viewer URL: https://{username}.github.io/{repo}/S0_Project-SAL-Grid_생성/viewer/viewer_json.html

⏱️ 첫 배포는 1-2분 후 접속 가능합니다.
   (GitHub Pages 빌드 시간)

📌 북마크 해두시면 언제든 프로젝트 진행 상황을 확인할 수 있습니다!"
```

### 이후 업데이트 시

Task 완료 후 JSON이 업데이트되면:

```bash
git add .
git commit -m "Update: {TaskID} 완료"
git push
```

**Claude Code가 Task 완료 시 자동으로 커밋 & 푸시!**

### 배포 관련 체크리스트

- [ ] `gh --version` 작동하는가?
- [ ] `gh auth status` 로그인 되어 있는가?
- [ ] GitHub 레포지토리 생성되었는가?
- [ ] GitHub Pages 활성화되었는가?
- [ ] Viewer URL 접속 가능한가?

---

## ⚠️ 빌드 vs 서버 구분 (혼동 금지!)

| 작업 | 사용 파일 | 용도 |
|------|----------|------|
| **빌드** (MD→JS 번들) | `build-web-assets.js` | 배포용 파일 생성 |
| **서버** (실시간 API) | `bridge_server.js` | 개발용 로컬 서버 |

**⛔ 혼동 금지:**
- "Order Sheet 빌드해" → `build-web-assets.js` 실행
- "안내문 빌드해" → `build-web-assets.js` 실행
- **`bridge_server.js`는 빌드 도구가 아님!** (런타임 API 서버)

**스크립트 저장 원칙:**
```
1. 단일 대상 스크립트 → 해당 폴더에 저장
2. 복수 대상 스크립트 → 루트 scripts/에 저장
```

**빌드 스크립트 위치:**
```
scripts/build-web-assets.js             ← 통합 빌드 (복수 대상)
Briefings_OrderSheets/OrderSheet_Templates/generate-ordersheets-js.js  ← Order Sheet (단일)
Briefings_OrderSheets/Briefings/generate-briefings-js.js               ← Briefings (단일)
```

