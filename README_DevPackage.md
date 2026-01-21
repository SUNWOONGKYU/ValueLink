# Dev Package

## What is this?

풀스택 웹사이트 개발 프로젝트를 Claude Code와 함께 처음부터 끝까지 체계적으로 수행할 수 있도록 설계된 통합 개발 환경입니다.

---

## Initial Setup (첫 실행 시)

### 환경 확인
```bash
git --version      # Git 설치 확인
node --version     # Node.js 18+ 권장
npm --version      # npm 확인
```

### 초기 설정
```bash
npm install        # 패키지 설치 (package.json 있는 경우)
cp .env.sample .env  # 환경 변수 파일 생성 (선택)
```

### 첫 지시 예시
```
"개발 환경 확인하고 프로젝트 초기 설정 해줘"
```

---

## Rules Location

**모든 작업 규칙은 `.claude/CLAUDE.md`에 있습니다.**

```
.claude/
├── CLAUDE.md              ← 핵심 규칙 (반드시 먼저 읽기)
├── rules/                 ← 7대 작업 규칙
│   ├── 01_file-naming.md
│   ├── 02_save-location.md
│   ├── 03_area-stage.md
│   ├── 04_grid-writing-json.md
│   ├── 05_execution-process.md
│   ├── 06_verification.md
│   └── 07_task-crud.md
├── methods/               ← 작업 방법
├── compliance/            ← AI 준수사항
└── work_logs/             ← 작업 기록
```

---

## Project Structure

```
Dev_Package/
├── .claude/                         ← Claude Code 설정 및 규칙
├── Process/                         ← 진행 프로세스 (P0~S5)
│   ├── P0_작업_디렉토리_구조_생성/   ← 기획 단계
│   ├── P1_사업계획_수립/
│   ├── P2_프로젝트_기획/
│   ├── P3_프로토타입_제작/
│   ├── S0_Project-SAL-Grid_생성/    ← SAL Grid 시스템
│   │   ├── method/json/data/        ← Task 데이터 (JSON)
│   │   │   ├── index.json           ← 프로젝트 메타 + task_ids
│   │   │   └── grid_records/        ← 개별 Task JSON 파일
│   │   ├── sal-grid/                ← Task Instructions
│   │   │   ├── task-instructions/
│   │   │   └── verification-instructions/
│   │   └── viewer/                  ← Viewer HTML
│   ├── S1_개발_준비/                 ← 본개발 Stage 폴더
│   ├── S2_개발-1차/
│   ├── S3_개발-2차/
│   ├── S4_개발-3차/
│   └── S5_개발_마무리/
├── Human_ClaudeCode_Bridge/         ← Orders/Reports
├── Process_Monitor/     ← 진행률 모니터
└── .env.sample                      ← 환경 변수 템플릿
```

---

## Data Files (JSON Method)

**위치:** `Process/S0_Project-SAL-Grid_생성/method/json/data/`

### 초기 상태 (다운로드 직후)

| 파일/폴더 | 상태 |
|-----------|------|
| `index.json` | 빈 템플릿 (project_id, task_ids 비어있음) |
| `grid_records/` | 템플릿 파일만 존재 |
| `task-instructions/` | `TEMPLATE_instruction.md` 템플릿만 있음 |

### S0 완료 후

| 파일/폴더 | 상태 |
|-----------|------|
| `index.json` | 프로젝트 정보 + Task ID 목록 |
| `grid_records/` | 각 Task별 JSON 파일 (S1BI1.json, S2F1.json 등) |
| `task-instructions/` | 각 Task별 지침 파일 |

---

## Development Flow

```
P0~P3 (기획) → S0 (SAL Grid 생성) → S1~S5 (본개발) → 배포/연동
```

### 개발 단계

| 단계 | 내용 | 산출물 |
|------|------|--------|
| **P0~P3** | 사업계획, 요구사항, 프로토타입 | 기획 문서 |
| **S0** | Task 목록 정의 + SAL Grid 생성 | index.json, grid_records/*.json |
| **S1~S5** | 정의된 Task 순서대로 개발 | 코드 파일 |

### 진행률 확인 방법

**자동 업데이트 프로세스:**
```
작업 완료 → Claude Code에게 "커밋해줘" 요청
  ↓
git commit 실행
  ↓
Pre-commit Hook 자동 실행
  ↓
진행률 계산 및 Supabase DB 업로드
  ↓
SSAL Works 플랫폼에 자동 반영 ✅
```

**SSAL Works 플랫폼에서 확인:**
1. www.ssalworks.ai.kr 접속
2. 로그인
3. **왼쪽 사이드바에서 진행률 바로 확인** (자동 표시)
   - P0, P1, P2, P3, S0, S1~S5 각 단계별 진행률 바

**Project SAL Grid Viewer (Task 상세 확인):**
- 메인 화면 하단 "Project SAL Grid" 섹션
- "{프로젝트명}(진행중) Viewer 열기" 버튼 클릭
- 각 Task별 상세 현황 확인 가능

**추가 확인 방법 (선택):**
- GitHub Pages 배포: → CLAUDE.md "GitHub Pages로 Viewer 배포" 참조
- Viewer 연결 설정: → CLAUDE.md "SSAL Works 플랫폼 연동" 참조

---

## Session Start Checklist

1. **`.claude/work_logs/current.md`** - 이전 작업 기록 확인
2. **`Human_ClaudeCode_Bridge/Reports/`** - 이전 작업 결과 확인
3. **`.claude/CLAUDE.md`** - 규칙 확인

---

## Environment Variables

`.env.sample`을 `.env`로 복사 후 필요한 값 입력.

**참고:** DB 연동은 선택사항. GitHub Pages만 사용 시 불필요.

---

## Related Documentation

| 문서 | 위치 | 내용 |
|------|------|------|
| **핵심 규칙** | `.claude/CLAUDE.md` | 7대 규칙, 절대 규칙, 작업 방법, 배포, 연동 |
| SAL Grid 매뉴얼 | `Process/S0_Project-SAL-Grid_생성/manual/` | Grid 시스템 상세 |
| AI 준수사항 | `.claude/compliance/` | AI 12대 준수사항 |
| 주의사항 | `.claude/CAUTION.md` | 일반 주의사항 |

---

## Quick Reference

**작업 전 필수 확인:** `.claude/CLAUDE.md`

| 상황 | CLAUDE.md 섹션 |
|------|---------------|
| Task 실행할 때 | "절대 규칙 3: Project SAL Grid Task" |
| 파일 저장할 때 | "절대 규칙 4: Stage 폴더에 먼저 저장" |
| JSON 수정할 때 | "JSON CRUD 작업 시 필수 준수" |
| 배포할 때 | "GitHub Pages로 Viewer 배포" |
| 연동할 때 | "SSAL Works 플랫폼 연동" |
