# Dev_Package vs ValueLink 비교 분석 보고서

**비교 날짜**: 2025-01-21
**원본**: `C:\!SSAL_Works_Private\공개_전환_업무\Dev_Package`
**대상**: `C:\ValueLink`

---

## 📊 핵심 차이점 요약

### 1. JSON 데이터 구조 방식 차이 (중요!)

| 항목 | 원본 (Dev_Package) | 대상 (ValueLink) |
|------|-------------------|------------------|
| **JSON 구조** | 개별 파일 방식 (`grid_records/{TaskID}.json`) | 단일 파일 방식 (`in_progress/project_sal_grid.json`) |
| **메타데이터** | `index.json` (task_ids 배열) | `index.json` + 단일 JSON 파일 |
| **폴더 구조** | `grid_records/`, `stage_gate_records/` | `in_progress/`, `completed/`, `users/` |

#### 원본 구조 (개별 파일)
```
method/json/data/
├── index.json             ← 프로젝트 메타 + task_ids 배열
├── grid_records/          ← 개별 Task JSON 파일
│   ├── S1BI1.json
│   ├── S1BI2.json
│   └── ...
└── stage_gate_records/    ← Stage Gate 기록
```

#### 대상 구조 (단일 파일)
```
method/json/data/
├── index.json
├── in_progress/           ← 진행 중인 프로젝트
│   └── project_sal_grid.json  ← 모든 Task 포함
├── completed/             ← 완료된 프로젝트 보관
└── users/                 ← 사용자별 데이터
```

**영향**:
- `.claude/methods/01_json-crud.md` 내용이 다름
- `build-progress.js` 로직이 다름 (개별 파일 읽기 vs 단일 파일 읽기)

---

## 📁 파일 차이 목록

### 1. .claude 폴더 차이

#### 원본에만 존재하는 파일
- `.claude/methods/00_initial-setup.md` ⭐ **중요**
  - 초기 설정 가이드
  - project_id 자동 조회 프로세스
  - GitHub Pages 배포 가이드

#### 내용이 다른 파일
- `.claude/rules/01_file-naming.md` ~ `07_task-crud.md` (모든 규칙 파일)
  - JSON 구조 차이로 인한 설명 변경
- `.claude/methods/01_json-crud.md` ⭐ **핵심 차이**
  - 원본: 개별 파일 방식 (grid_records/{TaskID}.json)
  - 대상: 단일 파일 방식 (in_progress/project_sal_grid.json)

---

### 2. README.md 차이

#### 원본 (Dev_Package/README.md)
- 더 상세한 초기 설정 가이드
- JSON 구조 설명: index.json + grid_records/
- 초기 상태와 S0 완료 후 상태 비교표

#### 대상 (ValueLink/README.md)
- 간단한 소개
- 필수 도구 설치 가이드
- 패키지 구조 개요

**권장**: 원본의 README.md가 더 체계적 → 대상에 복사 필요

---

### 3. scripts 폴더 차이

#### 원본에만 존재
- `scripts/build-progress.js` (개별 파일 방식용)
- `scripts/connect-viewer.js` ⭐ Viewer 연동 스크립트

#### 대상에만 존재
- `scripts/auto-commit.ps1`, `auto-commit.log`
- `scripts/install-auto-commit.ps1`, `install-auto-commit-simple.ps1`
- `scripts/INSTALL_AUTO_COMMIT.bat`
- `scripts/voice.ps1` (음성 입력 관련)

**분석**:
- 원본은 Viewer 연동 기능 포함
- 대상은 자동 커밋 기능 추가됨 (ValueLink 프로젝트 고유 기능)

---

### 4. Process_Monitor 폴더 차이

#### 원본 (Dev_Package)
- `build-progress.js` (10,020 bytes) - 최신 버전, 개별 JSON 파일 방식
- `README.md` (62,268 bytes) - 더 상세한 가이드

#### 대상 (ValueLink)
- `build-progress.js` (9,166 bytes) - 구버전, CSV 방식
- `README.md` (40,374 bytes) - 간략한 가이드
- `DEVELOPMENT_PROCESS_WORKFLOW.md` (추가 문서)

**권장**: 원본의 `build-progress.js`와 `README.md` 복사 필요

---

### 5. Human_ClaudeCode_Bridge 폴더 차이

#### 대상에만 존재
- `register_startup.ps1`
- `START_VOICE_CLIPBOARD.bat`, `START_VOICE_DIRECT.bat`, `START_VOICE_INPUT.bat`
- `voice_clipboard.ahk`, `voice_direct.py`, `voice_input.ps1`, `voice_realtime.py`
- `tmpclaude-40f8-cwd`

**분석**: ValueLink에 음성 입력 기능이 추가됨 (프로젝트 고유 기능)

---

### 6. Process/S0_Project-SAL-Grid_생성 폴더 차이

#### 원본에만 존재
- `PROJECT_SAL_GRID_VIEWER_PROCESS.md` ⭐ Viewer 프로세스 가이드

#### 대상에만 존재
- `build-sal-grid-csv.js` (CSV 빌드 스크립트)

---

## 🎯 동기화 필요 파일 목록

### 우선순위 1 (필수)

1. **`.claude/methods/00_initial-setup.md`** ⭐⭐⭐
   - 원본 → 대상 복사
   - 초기 설정 자동화 가이드 (project_id 자동 조회)

2. **`README.md`**
   - 원본 → 대상 복사 (더 상세함)
   - 단, 대상의 프로젝트 특화 정보는 유지

3. **`Process_Monitor/build-progress.js`**
   - 원본 → 대상 복사
   - 개별 JSON 파일 방식 지원

4. **`Process_Monitor/README.md`**
   - 원본 → 대상 복사 (더 상세함)

5. **`scripts/connect-viewer.js`**
   - 원본 → 대상 복사
   - Viewer 연동 기능

6. **`Process/S0_Project-SAL-Grid_생성/PROJECT_SAL_GRID_VIEWER_PROCESS.md`**
   - 원본 → 대상 복사
   - Viewer 프로세스 가이드

### 우선순위 2 (권장)

7. **`.claude/methods/01_json-crud.md`**
   - 원본 → 대상 복사
   - 개별 JSON 파일 방식 설명

8. **`.claude/rules/*.md` (7개 규칙 파일)**
   - 원본 버전이 더 최신일 가능성
   - 내용 검토 후 선택적 복사

### 우선순위 3 (선택)

9. **`.claude/CLAUDE.md`**
   - 내용 비교 후 차이점 병합

---

## 🔄 JSON 구조 마이그레이션 계획

현재 대상 (ValueLink)이 단일 파일 방식을 사용 중이므로, 원본의 개별 파일 방식으로 전환하려면:

### Option A: 개별 파일 방식으로 전환 (원본 방식)

**장점**:
- Task별 독립적 관리
- Git diff 추적 용이
- 병렬 처리 가능

**단계**:
1. `method/json/data/grid_records/` 폴더 생성
2. 현재 `in_progress/project_sal_grid.json`의 tasks 배열을 개별 파일로 분리
3. `index.json`에 task_ids 배열 추가
4. `build-progress.js` 업데이트 (원본 버전 사용)

### Option B: 단일 파일 방식 유지 (현재 대상 방식)

**장점**:
- 구조가 단순
- 파일 관리 용이

**단계**:
1. 원본의 새 기능만 선택적으로 적용
2. `.claude/methods/01_json-crud.md`는 현재 구조에 맞게 유지

**권장**: Option A (개별 파일 방식) - 원본의 설계가 더 확장성 있음

---

## 📋 동기화 스크립트 작성

```bash
# 1. 필수 파일 복사
cp "C:/!SSAL_Works_Private/공개_전환_업무/Dev_Package/.claude/methods/00_initial-setup.md" \
   "C:/ValueLink/.claude/methods/"

cp "C:/!SSAL_Works_Private/공개_전환_업무/Dev_Package/README.md" \
   "C:/ValueLink/README.md.new"  # 수동 병합 필요

cp "C:/!SSAL_Works_Private/공개_전환_업무/Dev_Package/Process_Monitor/build-progress.js" \
   "C:/ValueLink/Process_Monitor/"

cp "C:/!SSAL_Works_Private/공개_전환_업무/Dev_Package/scripts/connect-viewer.js" \
   "C:/ValueLink/scripts/"

# 2. S0 폴더 파일 복사
cp "C:/!SSAL_Works_Private/공개_전환_업무/Dev_Package/Process/S0_Project-SAL-Grid_생성/PROJECT_SAL_GRID_VIEWER_PROCESS.md" \
   "C:/ValueLink/Process/S0_Project-SAL-Grid_생성/"
```

---

## ⚠️ 주의사항

### 1. 프로젝트 고유 기능 보존
대상(ValueLink)에만 있는 다음 기능들은 보존:
- 자동 커밋 스크립트 (`auto-commit.ps1` 등)
- 음성 입력 기능 (voice 관련 파일들)

### 2. JSON 구조 전환 시
- 기존 데이터 백업 필수
- `in_progress/project_sal_grid.json` → `grid_records/{TaskID}.json` 분리 스크립트 필요

### 3. 규칙 파일 병합
- `.claude/rules/*.md` 파일들은 내용 검토 후 선택적 병합
- 대상에 추가된 신규 규칙이 있을 수 있음

---

## 📝 다음 단계 제안

1. **즉시 복사**: 우선순위 1 파일들
2. **내용 검토**: 우선순위 2 파일들
3. **JSON 구조 결정**: 개별 파일 vs 단일 파일 방식 선택
4. **테스트**: 동기화 후 Viewer 작동 확인

---

**보고서 작성 완료**: 2025-01-21
