# PROJECT SAL GRID MANUAL v4.0

> **작성일**: 2025-11-25
> **최종 수정**: 2025-12-27 (v4.0 - 일반화 버전, DB/CSV 방식 모두 지원)
> **용도**: PROJECT SAL GRID 완전 매뉴얼 (템플릿)

---

## 📋 목차 (전체 27개 섹션)

### PART 1: 개요 및 프레임워크

1. [개요](#1-개요)
2. [표준 프레임워크](#2-표준-프레임워크)
3. [22개 속성 정의](#3-22개-속성-정의)
4. [표준 프로젝트 디렉토리 구조](#4-표준-프로젝트-디렉토리-구조)

### PART 2: Grid 생성

5. [PROJECT SAL GRID 생성 프로세스](#5-project-sal-grid-생성-프로세스)
6. [Task 선정 원칙](#6-task-선정-원칙)
7. [Task Instruction 작성](#7-task-instruction-작성)
8. [Verification Instruction 작성](#8-verification-instruction-작성)

### PART 3: 검증 및 추적 시스템

9. [3단계 검증 시스템](#9-3단계-검증-시스템)
10. [Stage Gate 시스템](#10-stage-gate-시스템)
11. [Orders/Reports JSON 시스템](#11-ordersreports-json-시스템)
12. [Git 통합 추적 시스템](#12-git-통합-추적-시스템)

### PART 4: 데이터 저장 방식 선택 및 설정

- [📌 데이터 저장 방식 선택 가이드 (v4.0 신규)](#-데이터-저장-방식-선택-가이드-v40-신규)
13. [5분 만에 시작하기 (DB Method)](#13-5분-만에-시작하기-db-method)
14. [표준 Grid 설치](#14-표준-grid-설치)
15. [설치 확인 및 문제 해결](#15-설치-확인-및-문제-해결)
16. [Supabase 기본 개념](#16-supabase-기본-개념)
17. [CRUD 작업](#17-crud-작업)

### PART 5: Viewer 및 자동화

18. [HTML Viewer로 Grid 보기](#18-html-viewer로-grid-보기)
19. [Task 추가/수정/삭제 방법](#19-task-추가수정삭제-방법)
20. [Claude Code로 자동화](#20-claude-code로-자동화)
21. [API 직접 활용](#21-api-직접-활용)

### PART 6: 문제 해결 및 운영

22. [문제 해결 A to Z](#22-문제-해결-a-to-z)
23. [보안 및 백업](#23-보안-및-백업)
24. [추가 리소스](#24-추가-리소스)

### PART 7: 정리 및 부록

25. [정리 및 요약](#25-정리-및-요약)
26. [마무리](#26-마무리)
27. [버전 이력](#27-버전-이력)

---

## ⚠️ 🚨 AI 필수 준수 규칙 (Grid 데이터 작성 시) 🚨 ⚠️

> **이 섹션은 AI(Claude Code)가 Grid 데이터를 생성/수정할 때 반드시 준수해야 할 규칙입니다.**
> **상세 규칙은 `.claude/rules/` 폴더에서 자동 포함됩니다.**

### 🛑 절대 규칙: 폴더 생성 전 사용자 승인 필수

```
⛔ Task 실행 중 새 폴더가 필요하면 반드시 사용자에게 먼저 물어야 합니다!
⛔ 임의로 폴더를 생성하면 프로젝트 구조가 엉망이 됩니다!
```

**폴더 생성이 필요할 때:**
1. 작업 중단
2. 사용자에게 질문: "폴더 [폴더명] 생성이 필요합니다. 승인하시겠습니까?"
3. 승인 후에만 폴더 생성

---

### 📌 상세 규칙 (자동 포함)

> 아래 규칙들은 `.claude/rules/` 폴더에서 자동으로 포함됩니다.
> **규칙 수정 시 해당 파일만 수정하면 매뉴얼에 자동 반영됩니다.**
> 빌드: `node S0_Project-SAL-Grid_생성/manual/build-manual.js`

<!-- INCLUDE: .claude/rules/01_file-naming.md -->

---

<!-- INCLUDE: .claude/rules/03_area-stage.md -->

---

<!-- INCLUDE: .claude/rules/04_grid-writing-supabase.md -->

---

<!-- INCLUDE: .claude/rules/05_execution-process.md -->

---

<!-- INCLUDE: .claude/rules/06_verification.md -->

---

### 📌 규칙 참조 우선순위

```
1순위: CLAUDE.md 절대 불변 규칙
2순위: .claude/rules/ 상세 규칙
3순위: Order Sheet 지시사항
4순위: 본 매뉴얼 (PROJECT_SAL_GRID_MANUAL)
```

---

## PART 1: 개요 및 프레임워크

---

## 1. 개요

### 1.1 PROJECT SAL GRID란?

**PROJECT SAL GRID**는 **풀스택 웹사이트 개발 프로젝트**의 모든 작업을 체계적으로 관리하는 핵심 시스템입니다.

**주요 목적:**
- 복잡한 풀스택 웹 애플리케이션 개발
- Frontend, Backend, Database, DevOps 등 모든 영역 통합 관리
- AI 자동화 기반 개발 프로세스 구축
- 대규모 프로젝트의 체계적 진행

```
5×11 매트릭스 (표준 템플릿)
         ↓
Task 선정 (프로젝트별 커스터마이징)
         ↓
22개 속성 반영 (상세 정보 입력)
         ↓
Task Instruction + Verification Instruction 작성
         ↓
PROJECT SAL GRID 완성! ✅
```

### 1.2 핵심 원칙

#### **1. 🤖 AI-First 원칙 (작업 수행의 기본 규칙)**

**프로젝트 그리드에 제시되어 있는 모든 작업은 AI가 먼저 수행하고, 안 되는 것만 인간이 수행합니다.**

**기본 원칙:**
- ✅ **모든 작업은 AI가 먼저 수행**: 코드 작성, 테스트, 빌드, 배포 등 모든 개발 작업
- ✅ **Project Owner의 역할**: 초기 계획 자료 제공, AI가 못하는 작업 수행, 최종 검수 및 승인
- ✅ **작업 방식 속성(#8 Execution Type) 기본값**: "AI-Only" (전체 작업의 80% 목표)

**예외 상황 (Project Owner 협력이 필요한 경우):**

Project Owner가 협력 지원하는 경우는 **AI가 할 수 없는 명확한 사유**가 있을 때만 허용됩니다:

1. **외부 서비스 관련**
   - 유료 서비스 가입 및 결제 필요
   - 외부 API 키 발급 (이메일 인증, 신원 확인 등)
   - 도메인 구매 및 등록

2. **물리적 작업**
   - 하드웨어 설정 및 연결
   - 네트워크 장비 구성
   - 물리적 서버 설치

3. **법적/행정적 작업**
   - 법적 서명 및 승인
   - 계약서 작성 및 검토
   - 개인정보 취급 동의

4. **인간 고유 판단**
   - 최종 디자인 승인
   - 비즈니스 의사결정
   - 윤리적 판단 필요

**작업 방식 속성 지정:**
- **"AI-Only"**: 기본값 (AI가 독립적으로 수행 가능)
- **"Human-AI"**: 위 예외 상황에만 사용
- **명확한 사유 기재**: Task Instruction(#5) 또는 Remarks(#22)에 인간 협력이 필요한 이유 명시

⚠️ **주의**: "AI가 어려울 것 같아서"는 명확한 사유가 아닙니다. AI가 실제로 시도했으나 기술적으로 불가능한 경우에만 예외 처리합니다.

---

#### **2. 📅 미래 계획의 절대 시간 금지 원칙**

**계획 수립 시 절대 시간 개념(특정 날짜, 시간, 기간)을 사용하지 않습니다.**

**❌ 금지 사항 (미래 계획에 절대 시간 사용):**
```
잘못된 예시:
- "1시간 내에 완료"
- "2일 안에 개발"
- "이번 주까지 완료"
- "10월 25일까지 배포"
- "30분 소요 예정"
```

**문제점:**
- AI 작업 속도는 예측 불가능 (컨텍스트 크기, 복잡도에 따라 변동)
- 절대 시간 목표는 불필요한 압박과 실패감 유발
- 실제 완료 시간과 괴리 발생 시 계획 전체가 무의미해짐

**✅ 허용 사항 1: 이미 발생한 이력 (절대 시간 기록 필수)**

완료된 작업에는 정확한 시간 기록이 필수입니다:
```
속성 #11 (Task Status): "Completed"
속성 #12 (Generated Files): "src/App.tsx, src/components/Header.tsx"
DB 자동 기록: created_at, updated_at (Supabase)
```

**이유:**
- 과거 데이터는 AI 성능 분석의 기초
- 실제 소요 시간 추적으로 미래 프로젝트 계획 개선
- KPI 측정 및 최적화에 활용

**✅ 허용 사항 2: 상대적 순서 표현 (의존성만 명시)**

미래 작업은 순서와 의존성만 표현합니다:
```
속성 #9 (Dependencies): "S2F1, S2BA3" ← "S2F1과 S2BA3 완료 후 시작"
속성 #10 (Task Progress): "0%" → "50%" → "100%" ← 진행률만 표시
속성 #11 (Task Status): "Pending" → "In Progress" → "Completed" ← 상태만 표시
```

**올바른 계획 방식:**
- "S2F1이 완료되면 S2F2를 시작한다"
- "S3BA1, S3BA2, S3BA3가 모두 완료되면 S3F5를 시작한다"
- "해당 Stage의 모든 Task가 완료되면 다음 Stage로 진입한다"

**핵심 철학:**

> **"언제 끝날지는 중요하지 않습니다. 올바른 순서로 완료되는 것이 중요합니다."**

- AI는 의존성 체인을 따라 자동으로 작업을 진행
- 각 작업이 완료되면 다음 작업이 자동으로 시작
- 프로젝트는 자연스럽게 흘러가며 완성됨
- 절대 시간 압박 없이 품질에 집중

---

#### **3. 완전한 추적성**
- ✅ 모든 Task는 고유 ID로 추적
- ✅ Task → 파일 → Git 커밋 양방향 추적
- ✅ 작업 이력 100% 기록

---

## 2. 표준 프레임워크

### 2.1 5×11 매트릭스

**5 Stages × 11 Areas = 55개 표준 영역**

> **중요 변경사항 (v3.1)**:
> - 기존 6×11 → **5×11 매트릭스**로 변경
> - P1-P3 (Preliminary)는 **GRID 범위 밖**에서 별도 관리
> - PROJECT SAL GRID는 **S1-S5 실행단계만** 관리

#### **전체 프로세스 (GRID 범위 포함)**
```
╔═══════════════════════════════════════════════════════════════════════╗
║              PRELIMINARY (예비단계) - GRID 범위 밖                     ║
╠═══════════════════════════════════════════════════════════════════════╣
║   [P1 사업계획] ──→ [P2 프로젝트 기획] ──→ [P3 프로토타입 제작]        ║
║                                                                       ║
║   ※ Preliminary 단계는 GRID 생성 전에 완료해야 함                     ║
║   ※ 프로토타입(P3) 완료 후 GRID 생성                                  ║
╚═══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
                    ┌────────────────┐
                    │   Gate 검증    │
                    │  P3 프로토타입 │
                    │  승인 여부     │
                    └────────────────┘
                              │
                              ▼
╔═══════════════════════════════════════════════════════════════════════╗
║                PROJECT SAL GRID 관리 범위 (S1-S5)                     ║
╠═══════════════════════════════════════════════════════════════════════╣
║   Stage 1: Development Setup (개발 준비)        ← 일부 Areas          ║
║   Stage 2: Auth & Registration (개발 1차)       ← 11 Areas            ║
║   Stage 3: AI Integration (개발 2차)            ← 11 Areas            ║
║   Stage 4: Payment & Admin (개발 3차)           ← 일부 Areas          ║
║   Stage 5: Development Stabilization (개발 마무리) ← 9 Areas          ║
╚═══════════════════════════════════════════════════════════════════════╝
```

#### **기호 설명**
- **P (Preliminary)**: 예비단계 - GRID 범위 밖 (P1, P2, P3)
- **S (Stage)**: 실행단계 - GRID 관리 범위 (S1, S2, S3, S4, S5)

#### **5 Stages (GRID 관리 범위)**
```
Stage 1: Development Setup (개발 준비)
Stage 2: Auth & Registration (개발 1차)
Stage 3: AI Integration (개발 2차)
Stage 4: Payment & Admin (개발 3차)
Stage 5: Development Stabilization (개발 마무리)
```

#### **11 Areas (작업 영역)**
```
M  - Documentation (문서화)
U  - Design (UI/UX 디자인)
F  - Frontend (프론트엔드)
BI - Backend Infrastructure (백엔드 기반)
BA - Backend APIs (백엔드 API)
D  - Database (데이터베이스)
S  - Security (보안/인증/인가)
T  - Testing (테스트)
O  - DevOps (운영/배포)
E  - External (외부 연동)
C  - Content System (콘텐츠 시스템)
```

### 2.2 Task 개수의 유연성

> ⚠️ **중요**: 55개 Task는 "표준 템플릿"일 뿐, 필수 개수가 아닙니다!

**핵심 원칙: 프로젝트에 맞게 자유롭게 조정**

```
┌─────────────────────────────────────────────────────────┐
│  Task 개수는 프로젝트 규모와 상황에 따라 유연하게 조정  │
│                                                         │
│  • 10개로 시작 → 필요시 100개로 확장 ✅                │
│  • 100개로 시작 → 불필요한 것 삭제하여 축소 ✅         │
│  • 표준 템플릿 그대로 사용 ✅                           │
│  • 프로젝트 진행 중 언제든 추가/삭제 가능 ✅           │
└─────────────────────────────────────────────────────────┘
```

**예시 시나리오:**

| 프로젝트 유형 | 권장 시작 Task 수 | 설명 |
|--------------|------------------|------|
| 간단한 랜딩페이지 | 10~20개 | 필수 기능만 선택 |
| MVP 웹앱 | 30~50개 | 핵심 기능 중심 |
| 풀스택 웹 서비스 | 60~80개 | 표준 템플릿 활용 |
| 대규모 엔터프라이즈 | 100개+ | 세부 Task 분할 |

**Task 조정 방법:**
- 추가: [19-1. 새 Task 추가](#19-1-새-task-추가-create) 참조
- 삭제: [19-3. Task 삭제](#19-3-task-삭제-delete) 참조
- 수정: [19-2. Task 수정](#19-2-task-수정-update) 참조

### 2.3 Task ID 구조

```
형식: S[Stage][Area][Number]

예시:
- S1M1: Stage 1 (개발 준비) - Documentation - Task 1
- S3F5: Stage 3 (개발 2차) - Frontend - Task 5
- S5O1: Stage 5 (개발 마무리) - DevOps - Task 1
```

### 2.4 병렬 작업 표현

```
동시 실행 가능한 Task는 알파벳으로 구분:

S4F5a: 프로필 페이지 (병렬 a)
S4F5b: 설정 페이지 (병렬 b)
S4F5c: 알림 페이지 (병렬 c)

→ 모두 동시 작업 가능
```

### 2.5 Task 위치이동 시 ID 변경 규칙

**3D 좌표 기반 ID 변경 규칙**

Task ID는 3개의 축으로 이루어진 3D 좌표입니다:
```
Task ID = S[X축][Y축][Z축]
        = S[Stage][Area][Number]

예: S2BA5
    ├─ X축 (Stage): 2
    ├─ Y축 (Area): BA
    └─ Z축 (Number): 5
```

#### 번호 부여 규칙

**기본 원칙: X, Y, Z 중 하나라도 변경되면 새로운 ID 부여**

1. **XYZ 모두 동일 - ID 유지 (변경 없음)**
   ```
   S1F3 → S1F3 (위치 변경 없음)
   S2D7 → S2D7 (위치 변경 없음)
   ```

2. **하나 이상의 축이 변경 - 새로운 ID 부여**
   ```
   형식: [기존ID]_[새로운ID]
   ```

#### 변경 사례

**【X축(Stage) 변경 예시】**
```
S2F1이 새로운 Stage 1로 이동하고 Z축도 변경되면:
  기존: S2F1 (Stage 2, Area F, Number 1)
  변경: S2F1_S1F6 (Stage 1로 이동, Number도 6으로 변경)
```

**【Y축(Area) 변경 예시】**
```
S2BA5가 Area 변경되고 Stage도 변경되면:
  기존: S2BA5 (Stage 2, Area BA, Number 5)
  변경: S2BA5_S3F2 (Stage 3, Area F로 변경, Number 2로 변경)
```

**【Z축(Number) 변경 예시】**
```
Stage 1 내에서 S1D3이 D5로 위치가 변경되면:
  기존: S1D3 (Stage 1, Area D, Number 3)
  변경: S1D3_S1D5 (Stage 1, Area D 유지, Number만 5로 변경)
```

**【X, Y, Z 모두 변경 예시】**
```
S2BA5가 완전히 다른 위치로 이동하면:
  기존: S2BA5 (Stage 2, Area BA, Number 5)
  변경: S2BA5_S1F10 (Stage 1, Area F, Number 10으로 모든 축 변경)
```

#### 파일 및 커밋에서의 활용

**파일명:**
```
S2F1_S1F6_login_component.tsx
└─ Task ID 체인이 파일명에 그대로 반영
```

**Git 커밋 메시지:**
```
[S2F1_S1F6] 로그인 컴포넌트 위치 이동 및 수정
```

**용도:**
- Task 재배치 이력 추적
- 파일 이름에서 변경 이력 확인 가능
- Git 히스토리에서 Task 이동 추적

---

## 3. 22개 속성 정의

> **출처**: PROJECT_GRID_22_ATTRIBUTES_FINAL.md

---

## 📊 22개 속성 전체 구조

### **[1-4] Basic Info (기본 정보)**

```
1. Stage (단계)
   - **정의**: 프로젝트의 개발 단계 (순차적 개발 진행 단계)
   - **값 범위**: 1, 2, 3, 4, 5, ... (프로젝트별로 가변)
   - **데이터 타입**: 정수 (Integer)
   - **예시**: 4
   - **주의**: 프로젝트 규모에 따라 확대/축소 가능
   - **용도**: X축 좌표, 순차적 진행 관리

2. Area (영역)
   - **정의**: 작업이 속한 개발 영역
   - **값 범위**: 11개 표준 영역 또는 프로젝트에 따라 유연하게 정의
   - **표준 영역** (11개):
     • **M (Documentation)**: 문서화
     • **U (Design)**: UI/UX 디자인
     • **F (Frontend)**: 프론트엔드
     • **BI (Backend Infrastructure)**: 백엔드 기반 (Supabase 클라이언트, 미들웨어, 공통 유틸)
     • **BA (Backend APIs)**: 백엔드 API (비즈니스 로직, REST API 엔드포인트)
     • **D (Database)**: 데이터베이스
     • **S (Security)**: 보안/인증/인가
     • **T (Testing)**: 테스트
     • **O (DevOps)**: 운영/배포
     • **E (External)**: 외부 연동
     • **C (Content System)**: 콘텐츠 시스템
   - **커스텀 영역**: 프로젝트 필요에 따라 자유롭게 정의 가능
   - **데이터 타입**: 텍스트 (고정값)
   - **예시**: "DevOps", "Frontend", "Backend Infrastructure", "Backend APIs"
   - **용도**: Y축 좌표, 작업 분류 및 담당 AI Agent 역할 결정

3. Task ID (작업ID)
   - **정의**: 각 작업의 고유 식별 번호
   - **형식**: S[Stage][Area][Number][병렬기호]
     • Stage: 1, 2, 3, 4, 5
     • Area: M, U, F, BI, BA, D, S, T, O, E, C
     • Number: 1, 2, 3... (순차적)
     • 병렬기호: a, b, c... (소문자, 병렬 작업 시만 사용)
   - **데이터 타입**: 텍스트 (고정값)
   - **예시**:
     • "S1O1" (Stage 1, DevOps, 작업 1번 - 단독)
     • "S2BI3a" (Stage 2, Backend Infrastructure, 작업 3번 병렬 a)
     • "S2BA5b" (Stage 2, Backend APIs, 작업 5번 병렬 b)
     • "S3F7" (Stage 3, Frontend, 작업 7번 - 단독)
   - **용도**: Grid에서 작업을 추적하고 의존성/병렬성을 표현하는 핵심 키값

4. Task Name (업무명)
   - **정의**: 작업의 간단한 설명 (한 줄)
   - **값**: 간결한 작업 내용 요약
   - **데이터 타입**: 텍스트
   - **예시**: "크롤링 스케줄러", "회원가입 페이지 구현", "정치인 테이블 마이그레이션"
   - **용도**: Grid Viewer에서 Task 식별 및 빠른 이해
```

---

### **[5-9] Task Definition (작업 정의)**

```
5. Task Instruction (작업지시서)
   - **정의**: 작업을 수행하기 위한 상세 지시사항이 저장된 파일의 경로
   - **값**: 파일 경로 또는 URL
   - **데이터 타입**: 텍스트
   - **예시**:
     • "tasks/S4O1_instruction.md" (상대 경로)
     • "/docs/instructions/S4BA1.md" (절대 경로)
     • "https://docs.example.com/tasks/S1O1" (웹 문서)
     • "-" (지시서 없음)
   - **표준 위치**: `S0_Project-SAL-Grid_생성/task-instructions/{TaskID}_instruction.md` (별도 폴더 관리)
   - **표준 파일명**: `{TaskID}_instruction.md`
   - **용도**: AI Agent가 작업 수행 시 참조하는 핵심 문서
   - **주의**: 경로가 틀리면 AI가 작업 불가

6. Task Agent (작업에이전트)
   - **정의**: 작업을 수행할 AI 에이전트 이름
   - **값**: Agent 이름
   - **데이터 타입**: 텍스트
   - **예시**: "devops-troubleshooter", "fullstack-developer", "frontend-specialist"
   - **용도**: 작업을 실제로 수행하는 AI Agent 지정

7. Tools (사용도구)
   - **정의**: Agent가 작업 수행 시 동원하는 도구 목록
   - **값**: 쉼표로 구분된 도구 목록
   - **데이터 타입**: 텍스트
   - **포함 항목** (Agent가 사용하는 도구만):
     • **Claude Code Plugins**: 플러그인 이름 (예: @anthropic/code-review)
     • **Slash Commands**: /review-pr, /test, /deploy 등
     • **Skills**: pdf, xlsx, image-processing 등
     • **MCP Servers**: /mcp__github__*, /mcp__postgres__* 등
     • **CLI 도구**: gh (GitHub CLI), docker, npm 등
   - **제외 항목** (구현에 사용되는 것, Task Instruction에 명시):
     • ❌ 기술 스택: TypeScript, React, Next.js 등
     • ❌ 라이브러리: Tailwind CSS, Zustand, Zod 등
   - **예시**:
     • "/deploy, gh, @myteam/devops-plugin"
     • "/review-pr, pdf-skill, /mcp__github__create-pr"
     • "/test, docker, @anthropic/testing-tools"
   - **용도**: Agent가 작업 수행 시 동원할 수 있는 도구 명시
   - **참고**: Claude Code Plugin System (Commands, Skills, MCP 포함)

8. Execution Type (실행유형)
   - **정의**: 작업 수행 방식 (AI 자동화 수준)
   - **값**: AI-Only | Human-AI | Human-Only
   - **데이터 타입**: 텍스트 (고정값)
   - **예시**:
     • "AI-Only" (기본값, 80% 목표)
     • "Human-AI" (AI가 물리적으로 불가능한 경우만)
     • "Human-Only" (거의 사용 안 함)
   - **용도**: 작업의 자동화 수준 명시
   - **원칙**: AI-First, 명확한 사유 없이 Human 개입 금지

   ⚠️ **Human-AI Task 검증 규칙 (2025-12-15 추가)**:

   Human-AI Task는 가이드 문서 작성만으로 "완료" 처리 금지!

   **필수 완료 기준:**
   | 단계 | 수행자 | 필수 |
   |------|--------|------|
   | 1. 설정 가이드 작성 | AI | ✅ |
   | 2. PO에게 설정 요청 | AI | ✅ |
   | 3. 외부 서비스 설정 | PO (Human) | ✅ |
   | 4. 설정 완료 확인 | AI + PO | ✅ |
   | 5. **실제 작동 테스트** | AI + PO | ✅ **필수** |
   | 6. 테스트 성공 시 "완료" | AI | ✅ |

   **Human-AI Task 예시:**
   - S1S1: Google OAuth 설정
   - S2BI1: Resend 이메일 설정
   - S3E1: AI API 키 설정
   - S4O1: PG사 설정
   - S5O1/S5O2: 배포/도메인 연결

9. Dependencies (의존성체인)
   - **정의**: 현재 작업이 시작되기 전에 먼저 완료되어야 할 선행 작업의 ID
   - **값**: Task ID 목록 (쉼표로 구분)
   - **데이터 타입**: 텍스트
   - **예시**:
     • "S1O4" (단일 의존성)
     • "S2BI1, S2F2" (복수 의존성)
     • "S3F2a, S3F2b, S3F2c" (병렬 작업 그룹 전체 의존)
     • "-" 또는 빈 칸 (의존성 없음)
   - **용도**: Task 실행 순서 제어, 자동 의존성 검증
   - **참고**: 코드 import 문에서 자동 의존성 감지 가능
```

---

### **[10-13] Task Execution (작업 실행)**

```
10. Task Progress (작업진도)
    - **정의**: 작업 완료율
    - **값**: 0% ~ 100% (10% 단위 권장)
    - **데이터 타입**: 정수 (Integer)
    - **예시**: 0%, 50%, 100%
    - **용도**: 작업 진행 상황 추적

11. Task Status (작업상태)
    - **정의**: 현재 작업 상태
    - **값**: Pending | In Progress | Completed | Fixing
    - **데이터 타입**: 텍스트 (고정값)
    - **예시**:
      • "Pending" (대기)
      • "In Progress" (진행 중)
      • "Completed" (완료)
      • "Fixing" (수정 중)
    - **용도**: 작업 진행 단계 추적
    - **참고**: 타임스탬프는 DB의 created_at, updated_at 사용

12. Generated Files (생성파일)
    - **정의**: 작업으로 생성된 파일 목록
    - **값**: 쉼표로 구분된 파일 경로 목록
    - **데이터 타입**: 텍스트
    - **예시**:
      • "src/app/api/cron/route.ts, vercel.json, README.md"
      • "src/components/ProfileCard.tsx, src/lib/utils.ts"
    - **표준 파일명**: {TaskID}_ 접두사 사용 권장
    - **용도**: Task가 생성한 파일 추적
    - **참고**: Git 커밋으로 파일 생성 시점 추적 가능

13. Modification History (수정이력)
    - **정의**: 생성된 파일들의 수정 내역 및 오류 복구 과정
    - **값**: 버전 및 변경 내용 기록
    - **데이터 타입**: 텍스트
    - **예시**:
      • "[v1.0.0] 초기 구현"
      • "[ERROR] TypeScript 타입 오류 → [FIX] 인터페이스 수정 → [PASS] 빌드 성공"
      • "[v1.0.1] 코드 리뷰 반영"
    - **작성 원칙**: 버전 번호 포함, 오류 복구 과정 상세 기록
    - **용도**: 변경 이력 추적 및 문제 해결 과정 기록
```

---

### **[14-15] Verification Definition (검증 정의)**

```
14. Verification Instruction (검증지시서)
    - **정의**: 검증을 수행하기 위한 체크리스트가 저장된 파일의 경로
    - **값**: 파일 경로 또는 URL
    - **데이터 타입**: 텍스트
    - **예시**:
      • "tasks/S4O1_verification.md" (상대 경로)
      • "/docs/verifications/S4BA1.md" (절대 경로)
      • "-" (검증지시서 없음)
    - **표준 위치**: `S0_Project-SAL-Grid_생성/verification-instructions/{TaskID}_verification.md` (별도 폴더 관리)
    - **표준 파일명**: `{TaskID}_verification.md`
    - **용도**: 검증 Agent가 Task 검증 시 참조하는 체크리스트

15. Verification Agent (검증에이전트)
    - **정의**: 작업 완료 후 검증을 수행할 전문 AI 에이전트 이름
    - **값**: Agent 이름
    - **데이터 타입**: 텍스트
    - **예시**:
      • "qa-specialist" (품질 보증 전문가)
      • "code-reviewer" (코드 리뷰어)
      • "security-auditor" (보안 감사자)
      • "performance-tester" (성능 테스터)
    - **용도**: 1단계 Task 검증 수행 (작성자와 분리된 독립 검증자)
    - **참고**: Task Agent와 다른 Agent 사용 권장 (객관적 검증)
```

---

### **[16-19] Verification Execution (검증 실행)**

```
16. Test (테스트)
    - **정의**: 작업 결과물에 대한 테스트 수행 결과
    - **구성**: 4가지 테스트 유형
      • Unit Test (단위테스트): 개별 함수/컴포넌트 테스트
      • Integration Test (통합테스트): 모듈 간 연동 테스트
      • Edge Cases (엣지케이스): 경계값/예외 상황 테스트
      • Manual Test (수동테스트): 실제 동작 확인
    - **데이터 타입**: 구조화된 텍스트 (각 테스트별 Pass/Fail)
    - **예시**:
      • Unit Test (단위테스트): ✅ CRON_SECRET 인증
      • Integration Test (통합테스트): ✅ S4BA1 크롤러 연동
      • Edge Cases (엣지케이스): ✅ 빈 데이터 처리
      • Manual Test (수동테스트): ✅ curl 실행 확인
    - **용도**: 코드 품질 검증 및 오류 조기 발견
    - **참고**: 모든 항목이 ✅ Pass 되어야 Comprehensive Verification 통과

17. Build (빌드)
    - **정의**: 빌드 프로세스 각 단계의 성공 여부
    - **구성**: 4가지 빌드 단계
      • Compile (컴파일): 타입스크립트/컴파일 오류 검사
      • Lint (린트): 코드 스타일 및 정적 분석
      • Deploy (배포): 실제 배포 환경 테스트
      • Runtime (실행): 런타임 동작 확인
    - **데이터 타입**: 구조화된 텍스트 (각 단계별 Pass/Fail)
    - **예시**:
      • Compile (컴파일): ✅ TypeScript 오류 없음
      • Lint (린트): ✅ ESLint 통과
      • Deploy (배포): ✅ Vercel Production 정상
      • Runtime (실행): ✅ Cron 로그 확인
    - **용도**: 프로덕션 배포 가능 여부 판단
    - **참고**: Compile, Lint는 필수, Deploy/Runtime은 선택적

18. Integration Verification (연동검증)
    - **정의**: 다른 Task 또는 시스템과의 연동 상태 검증
    - **구성**: 3가지 연동 검증 항목
      • Dependency Propagation (의존성전파): 선행 Task의 결과물이 올바르게 전달되는지
      • Cross-Task Connection (Task간 연결): 관련 Task들과 정상 연동되는지
      • Data Flow (데이터 흐름): 데이터가 올바르게 흐르는지
    - **데이터 타입**: 구조화된 텍스트 (각 항목별 Pass/Fail)
    - **예시**:
      • Dependency Propagation (의존성전파): S4O2, S4O3 ✅
      • Cross-Task Connection (Task간 연결): ✅ S4BA1 API 정상 호출
      • Data Flow (데이터 흐름): ✅ DB → API → Frontend 데이터 전달
    - **용도**: 시스템 통합 상태 확인
    - **참고**: Dependencies가 있는 Task는 반드시 검증 필요

19. Blockers (블로커)
    - **정의**: 작업 완료를 방해하는 장애물 목록
    - **구성**: 4가지 블로커 유형
      • Dependency (의존성): 선행 Task 미완료
      • Environment (환경설정): 환경변수, API 키 등 설정 문제
      • External API (외부 API): 외부 서비스 장애 또는 제한
      • Status (상태): 전체 블로커 상태 요약
    - **데이터 타입**: 구조화된 텍스트 (각 유형별 블로커 내용)
    - **예시**:
      • Dependency (의존성): None
      • Environment (환경설정): None
      • External API (외부 API): None
      • Status (상태): No Blockers ✅
    - **예시 (블로커 있는 경우)**:
      • Dependency (의존성): ⚠️ S4BA1 미완료 대기중
      • Environment (환경설정): ⚠️ SUPABASE_URL 미설정
      • External API (외부 API): ⚠️ OpenAI API 할당량 초과
      • Status (상태): 3 Blockers 🚫 작업 중단
    - **용도**: 작업 진행 장애물 추적 및 해결
    - **참고**: 블로커 해결되면 즉시 Status 업데이트
```

---

### **[20-22] Verification Completion (검증 완료)**

```
20. Comprehensive Verification (종합검증결과)
    - **정의**: 모든 검증 항목을 종합한 최종 검증 결과 리포트
    - **구성**: 6가지 검증 항목 + 최종 판정
      • Task Instruction (작업지시서): 지시서 요구사항 충족 여부
      • Test (테스트): #16 테스트 결과 요약
      • Build (빌드): #17 빌드 결과 요약
      • Integration (연동): #18 연동 검증 결과 요약
      • Blockers (블로커): #19 블로커 상태 요약
      • Final (최종): 전체 검증 통과/실패 판정
    - **데이터 타입**: 구조화된 텍스트 (각 항목별 Pass/Fail + 최종 판정)
    - **예시 (통과)**:
      • [Task Instruction (작업지시서)] ✅ 모든 요구사항 충족
      • [Test (테스트)] ✅ 4/4 통과
      • [Build (빌드)] ✅ 4/4 통과
      • [Integration (연동)] ✅ 3/3 통과
      • [Blockers (블로커)] ✅ None
      • [Final (최종)] ✅ Passed (검증 통과)
    - **예시 (실패)**:
      • [Task Instruction (작업지시서)] ✅ 모든 요구사항 충족
      • [Test (테스트)] ❌ 2/4 실패 (Unit, Integration)
      • [Build (빌드)] ❌ Compile 오류 발생
      • [Integration (연동)] ⚠️ 검증 불가 (선행 Task 미완료)
      • [Blockers (블로커)] ❌ 2 Blockers
      • [Final (최종)] ❌ Failed (재작업 필요)
    - **용도**: Verification Agent가 작성하는 최종 검증 리포트
    - **참고**: 모든 항목 ✅ Pass 시에만 Verification Status가 "Passed"

21. Verification Status (검증상태)
    - **정의**: 검증 완료 후 최종 판정 상태
    - **값**: Not Verified | Passed | Failed
    - **데이터 타입**: 텍스트 (고정값)
    - **예시**:
      • "Not Verified" (미검증 - 초기 상태)
      • "Passed" (통과 - 검증 성공)
      • "Failed" (실패 - 재작업 필요)
    - **용도**: Task의 품질 승인 여부 추적
    - **참고**:
      • Passed → Task 완전 완료, 다음 Task 진행 가능
      • Failed → Task Status를 "Fixing"으로 변경, 재작업

22. Remarks (참고사항)
    - **정의**: 후속 작업자를 위한 참고사항, 주의사항, 제약사항
    - **값**: 자유 형식 텍스트
    - **데이터 타입**: 텍스트
    - **예시**:
      • "매일 6시 자동 실행됨"
      • "CRON_SECRET 환경변수 필수"
      • "S4O2 작업 시 이 Task의 로그 파일 경로 참조 필요"
      • "향후 시간 변경 시 vercel.json 수정"
      • "OpenAI API 할당량 주의 (월 100만 토큰 제한)"
    - **용도**:
      • 다음 세션 Agent가 작업 이어갈 때 참고
      • 운영/유지보수 시 주의사항 전달
      • 의존 Task에서 이 Task의 결과물 사용 시 필요한 정보
    - **작성 원칙**:
      • 구체적이고 실행 가능한 정보 기록
      • 환경변수, 파일 경로, 설정값 등 명시
      • "왜 이렇게 했는지" 맥락 제공
```

---

## 🔄 Task 작업 플로우

```
[1-9] Task 정의 (AI가 Supabase에 생성)
  ↓
[10] Task Progress: 0% → 작업 시작
[11] Task Status: Pending → In Progress
  ↓
[작업 에이전트 실행]
  - [5] Task Instruction 읽기
  - 코드 작성
  ↓
[10] Task Progress: 100%
[11] Task Status: Completed
[12] Generated Files 기록
[13] Modification History 기록
  ↓
[검증 에이전트 실행]
  - [14] Verification Instruction 읽기
  ↓
[16] Test 수행
[17] Build 수행
[18] Integration Verification 수행
[19] Blockers 확인
  ↓
[20] Comprehensive Verification 작성
[21] Verification Status 판정
  ↓
  ✅ Passed → 완료!
  ❌ Failed → [11] Task Status: Fixing → 10번부터 재작업
  ↓
[22] Remarks 작성 (후속 작업자를 위한 참고사항)
```

---

## ✅ 검증 로직

### **검증 통과 조건 (ALL 충족)**
```
✅ Test (16번) - 모든 테스트 통과
✅ Build (17번) - 모든 빌드 정상
✅ Integration Verification (18번) - 모든 연동 확인
✅ Blockers (19번) - 블로커 없음 (None)

→ Comprehensive Verification (20번): Passed
→ Verification Status (21번): Passed (통과)
```

### **검증 실패 조건 (ANY 해당)**
```
❌ Test 실패
❌ Build 실패
❌ Integration 실패
❌ Blockers 존재

→ Comprehensive Verification (20번): Failed
→ Verification Status (21번): Failed (실패)
→ Task Status (11번): Fixing (수정중)
→ Task Progress (10번): 재조정 후 재작업
```

---

## 🎯 핵심 원칙

### **1. 하이브리드 자동화**
- PROJECT SAL GRID: Task 자동 실행 (80%)
- Orders/Reports: Project Owner의 전략적 개입 (20%)
- Stage 시작/종료는 Project Owner가 제어

### **2. 이중 검증 (Stage Gate)**
- 1차: AI 자동 검증 (형식/완성도)
- 2차: Project Owner 수동 검증 (품질/방향성)
- 둘 다 통과해야 다음 Stage 진입

### **3. 검증 분리**
- Task 작업 에이전트 ≠ Task 검증 에이전트
- Task 검증 ≠ Stage 검증
- 독립적 검증으로 품질 보장

### **4. 명시적 Stage 제어**
- 모든 Stage는 Project Owner의 명령으로 시작
- 자동 진행 없음 (통제 유지)
- Stage Gate 거부 시 Order Sheet 필수

### **5. 블로커 관리**
- 블로커 있으면 검증 실패
- 의존성/환경/외부 API 체크 필수
- 블로커 해결 후 재작업

### **6. 후속 작업 배려**
- Remarks에 참고사항 필수 기록
- 다음 작업자가 막히지 않도록 상세 기록

---

## 4. 표준 프로젝트 디렉토리 구조

### 4.1 개요

**Standard Project Directory Structure**는 PROJECT SAL GRID 프로젝트의 표준 폴더 구조입니다.

**목적:**
- 일관된 프로젝트 구조
- 파일 위치 예측 가능
- 협업 효율성 향상
- Claude와의 원활한 작업

---

### 4.2 전체 구조

```
project-root/
├── README.md
├── PROJECT_STATUS.md
├── PROJECT_DIRECTORY_STRUCTURE.md
│
├── P1_사업계획/                        # Business Plan (GRID 범위 밖)
├── P2_프로젝트_기획/                   # Project Planning (GRID 범위 밖)
├── P3_프로토타입_제작/                 # Prototype (GRID 범위 밖)
├── S1_개발_준비/                       # Development Setup (Stage 1)
├── S2_개발-1차/                        # Auth & Registration (Stage 2)
├── S3_개발-2차/                        # AI Integration (Stage 3)
├── S4_개발-3차/                        # Payment & Admin (Stage 4)
├── S5_개발_마무리/                     # Development Stabilization (Stage 5)
│
├── .claude/                           # Claude Code 설정
│   └── CLAUDE.md
│
├── Web_ClaudeCode_Bridge/            # Web ↔ Claude Code 브릿지
│   ├── inbox/                        # 인간 → Claude
│   └── outbox/                       # Claude → 인간
│
└── S0_Project-SAL-Grid_생성/                # PROJECT SAL GRID 관리
    ├── sal-grid/                    # Task 기획 + Grid 데이터
    │   ├── TASK_PLAN.md   # Task 기획서
    │   └── 5x11_MATRIX.md # 5×11 매트릭스
    ├── manual/                       # 매뉴얼
    ├── supabase/                     # 데이터베이스 스키마
    └── viewer/                       # 뷰어
```

---

### 4.3 루트 파일 설명

#### **README.md**
```markdown
# 프로젝트명

프로젝트 개요 및 소개

## 디렉토리 구조
PROJECT_DIRECTORY_STRUCTURE.md 참고

## 프로젝트 상태
PROJECT_STATUS.md 참고
```

#### **PROJECT_STATUS.md**
```markdown
# Project Status

- **Current Stage**: Stage 2 (제작)
- **Progress**: 35%
- **Last Updated**: 2025-11-23

## Completed Stages
- ✅ 프로젝트 기획 (2025-11-15 완료) ← GRID 범위 외

## Current Tasks
- 🔄 S2F3: 로그인 페이지 (In Progress)
- 🔄 S2B2: 인증 API (In Progress)

## Blocked Tasks
- ⏸️ S2F5: 대시보드 (의존성: S2B3)
```

#### **PROJECT_DIRECTORY_STRUCTURE.md**
- 이 섹션의 내용을 그대로 포함
- 각 폴더의 역할 설명

---

### 4.4 작업 결과물 저장 2대 규칙 (2025-12-13 확정)

> **⚠️ 이 규칙은 모든 Task 작업에 적용됩니다. 반드시 준수하세요!**

#### 📌 제1 규칙: Stage + Area 폴더에 저장

**모든 작업 결과물은 Task ID의 Stage와 Area에 해당하는 폴더에 저장합니다.**

```
Task ID 구조: [Stage][Area][번호]
예: S1S1 → Stage: S1, Area: S (Security)
    S2F1 → Stage: S2, Area: F (Frontend)
```

**Stage 폴더 매핑:**
| Stage | 폴더명 |
|-------|--------|
| S1 | `S1_개발_준비/` |
| S2 | `S2_개발-1차/` |
| S3 | `S3_개발-2차/` |
| S4 | `S4_개발-3차/` |
| S5 | `S5_개발_마무리/` |

**Area 폴더 매핑:**
| Area 코드 | 폴더명 |
|-----------|--------|
| M | `Documentation/` |
| F | `Frontend/` |
| BI | `Backend_Infra/` |
| BA | `Backend_APIs/` |
| D | `Database/` |
| S | `Security/` |
| T | `Testing/` |
| O | `DevOps/` |
| E | `External/` |
| C | `Content/` |

**예시:**
- S1S1 → `S1_개발_준비/Security/`
- S1M1 → `S1_개발_준비/Documentation/`
- S2F1 → `S2_개발-1차/Frontend/`
- S3BA1 → `S3_개발-2차/Backend_APIs/`

#### 📌 제2 규칙: Production 코드는 이중 저장

**Frontend, Database, Backend_APIs 코드 파일은 Stage/Area 폴더 + Production 폴더 둘 다 저장합니다.**

```
Production/                 ← 배포용 코드 (최신 상태 유지)
├── Frontend/               # 프론트엔드 코드
├── Backend_APIs/           # API 코드
└── Database/               # DB 스키마
```

**이중 저장 대상:**
| Area | Stage 폴더 | Production 폴더 |
|------|------------|-----------------|
| F (Frontend) | `S?_*/Frontend/` | `Production/Frontend/` |
| BA (Backend_APIs) | `S?_*/Backend_APIs/` | `Production/Backend_APIs/` |
| D (Database) | `S?_*/Database/` | `Production/Database/` |

**예시:**
- S2F1 코드 → `S2_개발-1차/Frontend/` + `Production/Frontend/`
- S3BA1 코드 → `S3_개발-2차/Backend_APIs/` + `Production/Backend_APIs/`
- S1D1 스키마 → `S1_개발_준비/Database/` + `Production/Database/`

**문서는 Stage 폴더에만:**
- Documentation, Security, Testing, DevOps 등 문서는 Production에 저장하지 않음
- 예: S1S1 문서 → `S1_개발_준비/Security/` (Production에 저장 X)

#### ❌ 금지 사항

- 다른 Stage 폴더에 저장 금지 (예: S1 작업을 P3에 저장)
- Area 무시하고 임의 폴더에 저장 금지 (예: Security 작업을 Documentation에 저장)
- Stage 폴더 구조 무시 금지 (Security, Testing, DevOps 등 Area 폴더가 있는데 안 쓰기)

---

### 4.5 Stage 폴더 (0-5)

#### **명명 규칙**
```
{번호}_{한글명}/
```

#### **각 Stage 폴더 구조**
```
1_기획/
├── requirements.md           # 요구사항 문서
├── mockups/                  # 디자인 목업
├── erd.md                    # ERD 설계
└── tech-stack.md            # 기술 스택 결정
```

**Stage별 주요 산출물:**
- **P1_사업계획**: 사업계획서, 시장조사
- **1_기획**: 요구사항, 목업, ERD
- **2_프로토타입_제작**: 프로토타입 코드, 초기 화면
- **3_개발 준비**: 환경 설정, 기반 구조
- **4_개발**: 실제 기능 코드
- **5_개발_마무리**: 배포, QA, 안정화

---

### 4.5 claude/ 폴더

#### **claude.md**
```markdown
# Claude 작업 메모

## 현재 작업
- Task S2F3 진행 중

## 완료 작업
- S1M1: 프로젝트 계획서 작성
- S1M2: 기술 스택 문서화

## 다음 작업
- S2F4: 회원가입 페이지

## 참고사항
- Supabase RLS 정책 주의
- Tailwind v3 사용
```

**역할:**
- Claude의 작업 메모
- 세션 간 컨텍스트 유지
- 작업 기록

---

### 4.6 web_claude-code_bridge/ 폴더

#### **Orders/Reports System**

**Orders/ (수신함)**
```
inbox/
├── 20251123_143000_stage_start.json
├── 20251123_150000_gate_rejection.json
└── 20251123_160000_ad_hoc.json
```

**outbox/ (발신함)**
```
outbox/
├── 20251123_145000_progress.json
├── 20251123_155000_completion.json
└── 20251123_165000_question.json
```

**파일 명명 규칙:**
```
{YYYYMMDD}_{HHMMSS}_{type}.json
```

---

### 4.7 S0_Project-SAL-Grid_생성/ 폴더

#### **구조**
```
S0_Project-SAL-Grid_생성/
├── sal-grid/                        # Task 기획 + Grid 데이터
│   ├── TASK_PLAN.md       # Task 기획서 (v3.0)
│   └── 5x11_MATRIX.md     # 5×11 매트릭스 (v3.0)
│
├── manual/
│   ├── PROJECT_SAL_GRID_MANUAL.md  # 완전 매뉴얼
│   └── references/                   # 참조 문서
│
├── supabase/
│   ├── schema.sql
│   ├── migrations/
│   └── rls_policies.sql
│
└── viewer/
    └── viewer.html                   # HTML 뷰어
```

#### **각 폴더 역할**

**sal-grid/**
- Task 기획서 (TASK_PLAN.md)
- 5×11 매트릭스 정의 (5x11_MATRIX.md)
- Task 기획 완료 시 Grid 데이터 생성

**manual/**
- PROJECT SAL GRID 완전 매뉴얼
- 참조 문서 (references/)
- 사용법 가이드

**supabase/**
- 데이터베이스 스키마
- 마이그레이션 파일
- RLS 정책

**viewer/**
- HTML 뷰어
- Grid 시각화
- 진행 상황 모니터링

---

### 4.8 파일 명명 규칙

#### **Task Instruction**
```
형식: {TaskID}_instruction.md
예시: S2F3_instruction.md
```

#### **Verification Instruction**
```
형식: {TaskID}_verification.md
예시: S2F3_verification.md
```

#### **코드 파일**
```
형식: {TaskID}_{설명}.{확장자}
예시: S2F3_login_page.tsx
```

#### **Orders/Reports**
```
형식: {YYYYMMDD}_{HHMMSS}_{type}.json
예시: 20251123_143000_stage_start.json
```

---

### 4.9 주의사항

**필수 파일:**
- ✅ README.md (루트)
- ✅ PROJECT_STATUS.md (루트)
- ✅ PROJECT_DIRECTORY_STRUCTURE.md (루트)
- ✅ claude.md (claude/ 폴더)

**폴더 생성 시기:**
- **0-5 Stage 폴더**: 프로젝트 시작 시 즉시 생성
- **task-instructions/**: Task 생성 시 파일 추가
- **verification-instructions/**: Task 생성 시 파일 추가
- **inbox/outbox/**: 프로젝트 시작 시 생성 (비어있어도 OK)

**버전 관리:**
- 모든 폴더 Git 추적
- `.gitignore`로 임시 파일 제외
- `node_modules/`, `.env` 등 제외

---

## PART 2: Grid 생성

---

## 5. PROJECT SAL GRID 생성 프로세스

### 5.1 생성 시점

**PROJECT SAL GRID는 P3 프로토타입 완료 후, S1 개발 준비 시작 전에 생성합니다.**

```
[P1-P3: 예비단계 (GRID 범위 밖)]

  P1 사업계획
    ├─ Vision & Mission
    ├─ Market Analysis
    └─ Business Model
         ↓
  P2 프로젝트 기획
    ├─ 요구사항 정의
    ├─ 🎨 목업 디자인 완성 (필수!)
    ├─ ERD 설계
    └─ 기술 스택 결정
         ↓
  P3 프로토타입 제작
    ├─ Frontend 프로토타입
    ├─ Database 설정
    └─ 기본 동작 확인
         ↓
  ✨ PROJECT SAL GRID 생성
    ├─ AI가 S1~S5 모든 Task 도출
    ├─ 의존성 체인 설정
    └─ Task/Verification Instruction 작성
         ↓
  PROJECT SAL GRID 완성! ✅
  (예비단계 종료, 실행단계 진입 대기)

[S1-S5: 실행단계 (GRID 관리 범위)]
  └─ Grid에 정의된 Task를 순서대로 실행
```

**핵심:**
- Grid는 **예비단계 완료 후** 생성 (P3 프로토타입 → GRID → S1 개발 준비)
- **목업 디자인** 완성 후 Grid 생성 (순서 중요!)
- Grid 완성 = 예비단계 종료 = 실제 개발(S1~S5) 준비 완료

---

### 5.2 상세 생성 흐름

```
Step 1: 필수 초기 자료 확인
  ├─ 요구사항 정의서 ✅
  ├─ 목업 디자인 ✅
  ├─ ERD ✅
  └─ 기술 스택 ✅
         ↓
Step 2: 5×11 매트릭스 참고
  ├─ 각 Stage별 필요 Area 확인
  ├─ 일반적인 Task 예시 참고
  └─ 프로젝트에 맞게 조정
         ↓
Step 3: Task 선정 (2대 원칙 적용)
  ├─ 원칙 1: 파일 1개 = Task 1개
  └─ 원칙 2: 유사 작업 통합
         ↓
Step 4: 22개 속성 입력
  ├─ 기본 정보 (Stage, Area, Task ID)
  ├─ 작업 내용
  ├─ 의존성
  └─ 상태 관리
         ↓
Step 5: Task Instruction 작성
  ├─ 작업 목표
  ├─ 구체적 지시사항
  └─ 예상 출력물
         ↓
Step 6: Verification Instruction 작성
  ├─ 검증 기준
  ├─ 체크리스트
  └─ 합격 조건
         ↓
PROJECT SAL GRID 완성! ✅
```

### 5.3 필수 초기 자료

**AI가 정확한 Grid를 생성하려면 Project Owner가 다음 자료를 제공해야 합니다:**

#### **✅ 필수 자료**

**1. 프로젝트 요구사항**
- 명확한 최종 목표
- 전체 기능 목록
- 비기능 요구사항 (성능, 보안 등)

**2. 기술 사양**
- 시스템 아키텍처
- 기술 스택 (언어, 프레임워크)
- API/UI 명세

**3. 🔴 목업 디자인 (매우 중요!)**

**모든 화면 디자인 필수:**
- [ ] 전체 화면 목업
- [ ] 메인 페이지 디자인
- [ ] 로그인/회원가입 화면
- [ ] 대시보드 레이아웃
- [ ] 각 기능별 상세 화면
- [ ] 모바일/태블릿 반응형 디자인

**UI 컴포넌트 디자인:**
- [ ] 버튼, 폼, 카드 등 UI 컴포넌트
- [ ] 네비게이션 구조
- [ ] 모달/팝업 디자인

**플로우 및 인터랙션:**
- [ ] 화면 간 이동 흐름도
- [ ] 클릭/터치 시 동작 설명
- [ ] 애니메이션 명세

**4. 데이터 모델**
- ERD
- 테이블 구조
- 관계 설정

---

#### ⚠️ **경고: 목업 디자인 없이 시작하면 프로젝트 실패 확률 급증!**

**목업 디자인이 없으면:**
- ❌ AI가 UI를 상상으로 구현 → 완전히 다른 결과물
- ❌ 불충분한 자료 → AI의 잘못된 그리드 구성 → 프로젝트 실패
- ❌ 중간에 디자인 변경 → 전체 재작업 필요

**목업 디자인이 있으면:**
- ✅ AI가 정확한 UI 구현 → 기대한 결과물
- ✅ 완전한 자료 → AI의 정확한 그리드 구성 → 프로젝트 성공
- ✅ 초기 계획대로 진행 → 시간/비용 절감

---

## 6. Task 선정 원칙

### 6.1 원칙 1: 파일 1개 = Task 1개 (기본)

**생성되는 파일 하나당 Task 하나를 만듭니다.**

#### ✅ 올바른 예시
```
S4F1: src/app/page.tsx 생성
S4F2: src/app/search/page.tsx 생성
S4F3: src/components/Header.tsx 생성
S4F4: src/components/Footer.tsx 생성
```

#### ❌ 잘못된 예시
```
S4F1: 메인 페이지 전체 구현
  - page.tsx, Hero.tsx, Features.tsx, Footer.tsx...

→ 문제: 너무 크고 독립 작업 불가능
```

### 6.2 원칙 2: 동시 작업 가능한 유사 작업 통합

**같은 기능의 세부 파일들은 하나의 Task로 묶습니다.**

#### ✅ 올바른 예시
```
S4F5: 사용자 프로필 관련 컴포넌트 (통합)
  - src/components/ProfileCard.tsx
  - src/components/ProfileEdit.tsx
  - src/components/ProfileAvatar.tsx

→ 이유: 같은 "프로필" 기능, 동시 작업 가능
```

#### ❌ 잘못된 예시
```
S4F5: ProfileCard.tsx
S4F6: ProfileEdit.tsx
S4F7: ProfileAvatar.tsx

→ 문제: 너무 세분화, 관리 오버헤드
```

### 6.3 판단 기준

#### **언제 분리?**
- ✅ 독립적인 기능
- ✅ 다른 개발자가 동시 작업 불가
- ✅ 의존성이 복잡함

**예시:**
- 로그인 페이지 vs 회원가입 페이지 → **분리!**
- Header vs Footer → **분리!**

#### **언제 통합?**
- ✅ 같은 기능의 세부 파일들
- ✅ 함께 수정될 가능성 높음
- ✅ 동시 작업 가능

**예시:**
- 버튼 컴포넌트 variants → **통합!**
- 프로필 관련 컴포넌트들 → **통합!**

---

## 7. Task Instruction 작성

### 7.1 Task Instruction이란?

**Task Instruction (작업 지시서)**는 각 Task의 구체적인 작업 지시사항을 담은 문서입니다.

**저장 위치:**
- 속성 #19 `task_instruction` 필드
- 또는 별도 파일 (`tasks/S4F5_instruction.md`)

**작성 시점:**
- PROJECT SAL GRID 생성 단계
- Task 선정과 함께 작성

**역할:**
- Claude가 Task를 실행할 때 참고하는 기본 지침
- 무엇을 만들지 명확히 정의

### 🔗 필수 참조 규칙 파일 (2025-12-19)

> **Task Instruction 작성 및 실행 시 반드시 참조해야 할 규칙 파일들:**

| 규칙 파일 | 용도 | 참조 시점 |
|----------|------|----------|
| `.claude/rules/01_file-naming.md` | 파일 명명 규칙 | 파일 생성 시 |
| `.claude/rules/02_save-location.md` | 저장 위치 규칙 | 파일 저장 시 |
| `.claude/rules/03_area-stage.md` | Area/Stage 매핑 | Task 구조 파악 시 |
| `.claude/rules/05_execution-process.md` | 실행 프로세스 | 작업 수행 순서 |

**Task Instruction에 규칙 참조 포함:**
```markdown
## 작업 규칙
- 파일 명명: `.claude/rules/01_file-naming.md` 참조
- 저장 위치: `.claude/rules/02_save-location.md` 참조
- 실행 프로세스: `.claude/rules/05_execution-process.md` 참조
```

---

### 7.2 Task Instruction 작성 가이드

#### **작성 원칙**

**1. 명확성 (Clarity)**
- AI가 읽고 즉시 이해할 수 있어야 합니다
- 모호한 표현 금지 ("잘 만들어라", "적절히 구현" 등)
- 구체적인 기술 스택, 파일명, 경로 명시

**2. 완결성 (Completeness)**
- Task를 완료하는데 필요한 모든 정보 포함
- 선행 조건, 입력, 출력, 제약사항 명시
- 참고 자료 위치 정확히 기재

**3. 실행 가능성 (Actionability)**
- 단계별 구체적인 지시사항
- 예상 출력 파일 목록
- 기술 스택 및 라이브러리 명시

**4. 검증 가능성 (Verifiability)**
- 완료 기준을 체크리스트로 제공
- 측정 가능한 기준 (빌드 성공, 테스트 통과 등)

#### **필수 구성 요소**

| 섹션 | 필수 여부 | 설명 |
|------|----------|------|
| 작업 ID | ✅ 필수 | Task ID (예: S4F5) |
| 작업 제목 | ✅ 필수 | Task 이름 |
| 작업 목표 | ✅ 필수 | 무엇을 만들 것인지 한 문장으로 |
| 선행 조건 | ✅ 필수 | 의존하는 Task 목록 (depends_on) |
| 구체적 지시사항 | ✅ 필수 | 단계별 작업 내용 |
| 기술 스택 | ✅ 필수 | 사용할 언어, 프레임워크, 라이브러리 |
| 예상 출력 파일 | ✅ 필수 | 생성/수정할 파일 목록 |
| 완료 기준 | ✅ 필수 | 체크리스트 형태 |
| 참고 자료 | ⭐ 권장 | 디자인 목업, API 문서 등 |
| 주의사항 | ⭐ 권장 | 제약사항, 보안 이슈 등 |

#### **작성 단계별 가이드**

**Step 1: 작업 목표 정의**
```markdown
## 작업 목표
사용자가 자신의 프로필을 확인하고 수정할 수 있는 페이지 구현

❌ 나쁜 예: "프로필 페이지 만들기"
✅ 좋은 예: "사용자가 자신의 프로필을 확인하고 수정할 수 있는 페이지 구현"
```

**Step 2: 선행 조건 명시**
```markdown
## 선행 조건
- S4F1 (메인 레이아웃) 완료 → 레이아웃 컴포넌트 사용
- S4B3 (사용자 정보 API) 완료 → API 엔드포인트 호출
- S4S2 (인증 시스템) 완료 → 로그인 검증
```

**Step 3: 구체적 지시사항 작성**
```markdown
## 구체적 지시사항

### 1. 페이지 구조
- 경로: `/profile` (정확한 URL 명시)
- 레이아웃: MainLayout 사용 (구체적인 컴포넌트명)
- 인증: 로그인 필수 (middleware에서 체크)

### 2. 필수 구현 기능 (우선순위 순서)
1. **프로필 정보 표시**
   - 프로필 이미지 (기본 이미지: `/images/default-avatar.png`)
   - 사용자 이름 (DB 필드: `users.display_name`)
   - 이메일 (수정 불가, 읽기 전용)
   - 가입일 (포맷: "YYYY년 MM월 DD일")

2. **프로필 수정**
   - 프로필 이미지 업로드 (Supabase Storage 사용)
   - 사용자 이름 변경 (최소 2자, 최대 20자)
   - 저장 버튼 (API: PUT /api/users/me)
```

**Step 4: 기술 스택 명시**
```markdown
### 3. 기술 스택
- Next.js 14 App Router (특정 버전 명시)
- TypeScript 5.0+ (타입 정의 필수)
- Tailwind CSS (유틸리티 클래스 사용)
- Supabase Client (@supabase/supabase-js)
- React Hook Form (폼 검증)
- Zod (스키마 검증)
```

**Step 5: 예상 출력 파일 목록**
```markdown
### 4. 예상 출력 파일
새로 생성할 파일:
- src/app/profile/page.tsx (메인 페이지)
- src/components/ProfileCard.tsx (정보 표시)
- src/components/ProfileEdit.tsx (수정 폼)
- src/components/ProfileAvatar.tsx (아바타 컴포넌트)
- src/app/profile/profile.module.css (스타일)

수정할 파일:
- src/types/user.ts (타입 추가)
- src/lib/supabase.ts (업로드 함수 추가)
```

**Step 6: 완료 기준 체크리스트**
```markdown
## 완료 기준
- [ ] 프로필 정보 표시 (이미지, 이름, 이메일, 가입일)
- [ ] 프로필 이미지 업로드 (5MB 이하, jpg/png/webp)
- [ ] 정보 수정 기능 (이름 변경, 저장)
- [ ] 반응형 동작 확인 (모바일 320px~, 데스크톱 1024px~)
- [ ] TypeScript 빌드 성공 (에러 0개)
- [ ] 테스트 통과 (단위 테스트 작성)
```

#### **흔한 실수와 해결법**

| 실수 | 문제점 | 해결법 |
|------|--------|--------|
| "적절히 구현" | 모호함 | 구체적인 기준 명시 (예: "Tailwind CSS 사용") |
| 파일 경로 누락 | AI가 어디에 만들지 모름 | 정확한 경로 명시 (`src/app/profile/page.tsx`) |
| 버전 미명시 | 호환성 문제 | 버전 명시 (Next.js 14, React 18) |
| 참고 자료 위치 불명확 | AI가 찾지 못함 | 절대 경로 사용 (`docs/design/mockup.png`) |
| 완료 기준 없음 | 검증 불가 | 체크리스트 작성 |
| 의존성 누락 | 순서 문제 | depends_on과 일치하는 선행 조건 |

---

### 7.3 Task Instruction Template (템플릿)

```markdown
# Order Sheet - S4F5

## 작업 ID
S4F5

## 작업 제목
사용자 프로필 페이지

## 작업 목표
사용자가 자신의 프로필을 확인하고 수정할 수 있는 페이지 구현

## 선행 조건
- S4F1 (메인 레이아웃) 완료
- S4B3 (사용자 정보 API) 완료
- S4S2 (인증 시스템) 완료

## 구체적 지시사항

### 1. 페이지 구조
- 경로: `/profile`
- 레이아웃: MainLayout 사용
- 인증: 로그인 필수

### 2. 필수 구현 기능
1. **프로필 정보 표시**
   - 프로필 이미지
   - 사용자 이름
   - 이메일 (수정 불가)
   - 가입일

2. **프로필 수정**
   - 프로필 이미지 업로드
   - 사용자 이름 변경
   - 저장 버튼

3. **반응형 디자인**
   - 모바일: 세로 레이아웃
   - 데스크톱: 가로 레이아웃

### 3. 기술 스택
- Next.js 14 App Router
- TypeScript
- Tailwind CSS
- Supabase Client

### 4. 예상 출력 파일
```
src/app/profile/page.tsx
src/components/ProfileCard.tsx
src/components/ProfileEdit.tsx
src/components/ProfileAvatar.tsx
```

### 5. 참고 자료
- 디자인: `design/profile_mockup.png`
- API 문서: `docs/api/user.md`

### 6. 주의사항
- 이미지 크기 제한: 5MB
- 지원 포맷: jpg, png, webp
- 에러 처리 필수

## 완료 기준
- [ ] 프로필 정보 표시
- [ ] 프로필 이미지 업로드
- [ ] 정보 수정 기능
- [ ] 반응형 동작 확인
- [ ] 테스트 통과
```

---

## 8. Verification Instruction 작성

### 8.1 Verification Instruction이란?

**Verification Instruction (검증 지시서)**는 Task 완료 후 검증을 위한 체크리스트입니다.

**누가 사용하나?**
- 속성 #15 `verification_agent`에 지정된 Sub-agent
- 예: `qa-specialist`, `code-reviewer`

**언제 사용하나?**
- Task 완료 직후
- **1번만 검증** (1단계 검증 시스템의 일부)

### 🔗 필수 참조 규칙 파일 (2025-12-19)

> **Verification Instruction 작성 및 실행 시 반드시 참조해야 할 규칙 파일들:**

| 규칙 파일 | 용도 | 참조 시점 |
|----------|------|----------|
| `.claude/rules/04_grid-writing-supabase.md` | Grid 속성 검증 | 결과 기록 시 |
| `.claude/rules/05_execution-process.md` | 검증 프로세스 | 검증 수행 순서 |
| `.claude/rules/06_verification.md` | 검증 기준 | **핵심 참조** |

**Verification Instruction에 규칙 참조 포함:**
```markdown
## 검증 규칙
- 검증 기준: `.claude/rules/06_verification.md` 참조
- 결과 기록: `.claude/rules/04_grid-writing-supabase.md` 참조
- 검증 프로세스: `.claude/rules/05_execution-process.md` 참조
```

**검증 항목 참조 (`06_verification.md` 기준):**
- Test Result: unit_test, integration_test, edge_cases, manual_test
- Build Verification: compile, lint, deploy, runtime
- Integration Verification: dependency_propagation, cross_task_connection, data_flow
- Blockers: dependency, environment, external_api

---

### 8.2 Verification Instruction 작성 가이드

#### **⚠️ 🚨 CRITICAL: Task-Verification 일치 규칙 🚨 ⚠️**

> **이 규칙은 Verification Instruction 작성의 가장 기본적이고 중요한 규칙입니다!**
> **실제 검토 결과 42개 Task 중 11개(26%)가 불일치 상태였습니다!**

**필수 일치 항목:**

| 항목 | Task Instruction | Verification Instruction |
|------|-----------------|-------------------------|
| Task ID | `S2F1` | `S2F1` (동일해야 함) |
| Task Name | `Google 소셜 로그인 UI` | `Google 소셜 로그인 UI` (동일해야 함) |
| 검증 대상 | Expected Output Files | Verification Checklist에 포함 |
| 완료 기준 | Completion Criteria | Pass Criteria에 반영 |

**검증 방법:**

```bash
# Task Instruction의 Task Name 확인
grep "## Task Name" task-instructions/S2F1_instruction.md -A 1

# Verification Instruction의 Task Name 확인
grep "## Task Name" verification-instructions/S2F1_verification.md -A 1

# 두 값이 정확히 일치해야 함!
```

**❌ 발견된 불일치 사례 (실제 오류):**

| Task ID | Task Instruction | Verification Instruction (잘못됨) |
|---------|-----------------|----------------------------------|
| S1BI1 | 환경변수 설정 | ~~Supabase 클라이언트 설정~~ |
| S2F1 | Google 소셜 로그인 UI | ~~My Page UI~~ |
| S2BI2 | 에러 핸들링 시스템 | ~~구독 클라이언트 모듈~~ |

**불일치 시 발생하는 문제:**
- ❌ 잘못된 Task를 검증하게 됨
- ❌ 실제 Task의 품질이 검증되지 않음
- ❌ Grid 데이터 무결성 파괴
- ❌ Stage Gate 통과 후 결함 발견

**필수 점검 절차:**

1. **Verification Instruction 작성 전**:
   - 해당 Task Instruction 파일을 **반드시 먼저 읽기**
   - Task ID, Task Name 정확히 복사

2. **Verification Instruction 작성 후**:
   - Task Name이 정확히 일치하는지 확인
   - Checklist가 Task Instruction의 완료 기준을 검증하는지 확인

3. **일괄 검증 (권장)**:
   ```bash
   # 모든 Task-Verification 일치 여부 확인 스크립트
   for f in task-instructions/*.md; do
     id=$(basename "$f" _instruction.md)
     task_name=$(grep -A1 "## Task Name" "$f" | tail -1)
     verif_name=$(grep -A1 "## Task Name" "verification-instructions/${id}_verification.md" | tail -1)
     if [ "$task_name" != "$verif_name" ]; then
       echo "MISMATCH: $id - Task: $task_name vs Verif: $verif_name"
     fi
   done
   ```

---

#### **작성 원칙**

**1. 객관성 (Objectivity)**
- 주관적 판단 배제 ("잘 만들어졌다", "괜찮다" 등)
- 측정 가능한 기준 사용 (빌드 성공, 테스트 통과율 등)
- 명확한 합격/불합격 기준

**2. 완전성 (Completeness)**
- Task Instruction의 모든 완료 기준 검증
- 기능 동작, 코드 품질, 성능 모두 포함
- 필수 조건과 권장 조건 구분

**3. 실행 가능성 (Actionability)**
- 검증 단계별 구체적인 방법 제시
- Fail 시 명확한 수정 방향 제공
- 재검증 절차 명시

**4. 자동화 가능성 (Automatable)**
- 가능한 자동화된 검증 방법 사용
- 테스트 스크립트, 빌드 명령어 명시
- 수동 검증은 최소화

#### **필수 구성 요소**

| 섹션 | 필수 여부 | 설명 |
|------|----------|------|
| Verification Target | ✅ 필수 | Task ID 및 이름 |
| Verifier | ✅ 필수 | 검증 담당 Sub-agent (속성 #15) |
| 검증 체크리스트 | ✅ 필수 | 단계별 검증 항목 |
| 합격 기준 | ✅ 필수 | 필수 조건 및 권장 조건 |
| 검증 결과 | ✅ 필수 | Pass/Fail 및 지적사항 |
| 검증 방법 | ⭐ 권장 | 구체적인 테스트 방법 |
| 성능 기준 | ⭐ 권장 | 응답 시간, 처리량 등 |

#### **작성 단계별 가이드**

**Step 1: 검증 대상 명확히 정의**
```markdown
## Verification Target (검증 대상)
Task S4F5: 사용자 프로필 페이지

❌ 나쁜 예: "프로필 페이지"
✅ 좋은 예: "Task S4F5: 사용자 프로필 페이지 (프로필 정보 표시 및 수정 기능)"
```

**Step 2: 검증자 지정**
```markdown
## Verifier (검증자)
**담당**: qa-specialist (속성 #15에 지정)
**역할**: 기능 테스트, 코드 리뷰, 성능 검증

❌ 나쁜 예: "QA 담당자"
✅ 좋은 예: "qa-specialist (속성 #15에 지정)"
```

**Step 3: 체크리스트 작성 (우선순위 순)**
```markdown
## 검증 체크리스트

### 1. 빌드 및 컴파일 (최우선)
- [ ] TypeScript 빌드 성공
  ```bash
  npm run build
  # 예상: Build completed in 15s
  ```
- [ ] ESLint 통과 (경고 0개)
  ```bash
  npm run lint
  # 예상: ✓ No ESLint warnings or errors
  ```
- [ ] TypeScript 타입 에러 없음
  ```bash
  npm run type-check
  # 예상: Found 0 errors
  ```

### 2. 파일 생성 확인
- [ ] 모든 예상 파일 존재
  - [ ] src/app/profile/page.tsx (메인 페이지)
  - [ ] src/components/ProfileCard.tsx (카드 컴포넌트)
  - [ ] src/components/ProfileEdit.tsx (편집 컴포넌트)
  - [ ] src/components/ProfileAvatar.tsx (아바타)

### 3. 핵심 기능 동작
- [ ] 프로필 정보 표시
  - 방법: 로그인 후 /profile 접속
  - 예상: 이름, 이메일, 가입일 표시
- [ ] 프로필 이미지 업로드
  - 방법: 이미지 파일 선택 및 업로드
  - 예상: Supabase Storage에 저장, URL 업데이트
- [ ] 정보 수정 및 저장
  - 방법: 이름 변경 후 저장 버튼 클릭
  - 예상: DB 업데이트, 성공 메시지 표시
```

**Step 4: 합격 기준 정의**
```markdown
## 합격 기준

### 필수 조건 (하나라도 실패 시 불합격)
1. ✅ 빌드 성공 (TypeScript 에러 0개)
2. ✅ 모든 예상 파일 생성
3. ✅ 핵심 기능 동작 (정보 표시, 수정, 저장)
4. ✅ 반응형 동작 확인

### 권장 조건 (80% 이상 충족 권장)
1. ⭐ 코드 품질 (타입 정의, 네이밍)
2. ⭐ 테스트 커버리지 80%+
3. ⭐ 성능 기준 충족 (로딩 2초 이내)
4. ⭐ 접근성 (ARIA, 키보드 내비게이션)
5. ⭐ 문서화 (JSDoc 주석)

**최종 합격 조건:**
- 필수 조건: 4/4 충족
- 권장 조건: 4/5 충족 (80%)
```

**Step 5: 검증 결과 양식**
```markdown
## 검증 결과

### 결과
- ✅ Pass
- ❌ Fail

### 검증 일시
2025-11-25 14:30

### 검증자
qa-specialist

### 필수 조건 체크
- [x] 빌드 성공
- [x] 파일 생성
- [x] 기능 동작
- [x] 반응형

### 권장 조건 체크 (4/5 = 80%)
- [x] 코드 품질
- [x] 테스트 커버리지
- [x] 성능
- [ ] 접근성 (일부 미흡)
- [x] 문서화

### 지적사항 (Pass여도 개선 권장)
1. **접근성 개선 필요**
   - 문제: 이미지 업로드 버튼에 aria-label 없음
   - 수정: `<button aria-label="프로필 이미지 업로드">`
   - 파일: src/components/ProfileAvatar.tsx:45

### 보고서 위치
validation/results/S4F5_verification_2025-11-25.md
```

#### **흔한 실수와 해결법**

| 실수 | 문제점 | 해결법 |
|------|--------|--------|
| "잘 동작한다" | 주관적 판단 | "로그인 성공, 프로필 표시" (객관적 기준) |
| 검증 방법 누락 | 재현 불가 | 구체적인 테스트 절차 명시 |
| 합격 기준 모호 | 판단 어려움 | 필수/권장 조건 명확히 구분 |
| 자동화 미사용 | 시간 낭비 | 빌드, 테스트 스크립트 활용 |
| Fail 시 지침 없음 | 재작업 방향 불명확 | 구체적인 수정 방법 제시 |
| 성능 기준 없음 | 품질 저하 | 로딩 시간, 응답 시간 명시 |

---

### 8.3 Verification Instruction Template (템플릿)

```markdown
# Verification Instruction - S4F5

## Verification Target (검증 대상)
Task S4F5: 사용자 프로필 페이지

## Verifier (검증자)
**담당**: qa-specialist (속성 #15에 지정)

## 검증 체크리스트

### 1. 파일 생성 확인
- [ ] 모든 예상 파일 생성 완료
  - page.tsx 존재
  - 컴포넌트 파일 존재

### 2. 빌드 및 컴파일
- [ ] 빌드 성공
  - TypeScript 에러 없음
  - ESLint 통과
  - 경고 없음

### 3. 핵심 기능 동작
- [ ] 프로필 정보 표시
- [ ] 프로필 이미지 업로드
- [ ] 정보 수정 기능
- [ ] 저장 기능 동작

### 4. UI/UX 검증
- [ ] 디자인 목업과 일치
- [ ] 반응형 동작 (모바일/데스크톱)
- [ ] 로딩 상태 표시
- [ ] 에러 처리 UI

### 5. 코드 품질
- [ ] TypeScript 타입 정의 완료
- [ ] 주석 작성 (복잡한 로직)
- [ ] 네이밍 컨벤션 준수
- [ ] 불필요한 코드 없음

### 6. 테스트
- [ ] 단위 테스트 작성 (필요 시)
- [ ] 테스트 통과
- [ ] 커버리지 기준 충족

## 합격 기준

### 필수 조건 (하나라도 실패 시 불합격)
1. 모든 파일 생성 완료
2. 빌드 성공
3. 핵심 기능 동작
4. 반응형 확인

### 권장 조건 (80% 이상 충족 권장)
1. 코드 품질
2. 성능 최적화
3. 접근성
4. 문서화

## 검증 결과

### 결과
- ✅ Pass
- ❌ Fail

### 검증 일시
YYYY-MM-DD HH:MM

### 검증자
qa-specialist

### 지적사항 (Fail 시)
1. [문제점 설명]
2. [수정 방법]

### 보고서 위치
validation/results/S4F5_verification.md
```

---

### 8.4 Verification Instruction 작성 팁

**명확한 기준:**
- "동작한다" (X) → "로그인 후 프로필 페이지 접근 가능" (O)
- "잘 만들어졌다" (X) → "목업 디자인과 90% 일치" (O)

**측정 가능한 기준:**
- 정량적 지표 사용
- 빌드 시간, 번들 크기, 테스트 커버리지 등

**실행 가능한 지시:**
- Fail 시 구체적인 수정 방법 제시
- 어떤 파일의 어느 부분을 어떻게 수정할지

---

# PART 3: 검증 및 추적 시스템

PROJECT SAL GRID의 품질 보증과 작업 추적을 위한 핵심 시스템을 다룹니다.

---

## 9. 3단계 검증 시스템

PROJECT SAL GRID는 **3단계 검증 시스템**으로 품질을 보증합니다.

### 9.1 전체 구조

```
[1단계: Task 검증]
  각 Task 완료 시
  ├─ 작성자: Sub-agent (예: frontend-developer)
  └─ 검증자: 전문 검증 Sub-agent (예: qa-specialist)
       ↓
[2단계: Stage Gate - AI 자동 검증]
  Stage 전체 완료 후
  └─ 검증자: Main Agent (해당 세션의 Claude Code)
       ↓
[3단계: Stage Gate - Project Owner 수동 검증]
  AI 검증 통과 후
  └─ 검증자: Project Owner
       ↓
  최종 승인 또는 거부
```

---

### 9.2 1단계: Task 검증 (Sub-agent)

#### **⚠️ 핵심 원칙: 서브에이전트 투입 필수!**

**Claude Code(Main Agent)가 직접 작업/검증하면 안 됨!**
- Task 작업: 반드시 **Task Agent 서브에이전트 투입**
- Task 검증: 반드시 **Verification Agent 서브에이전트 투입**
- Grid 기록: **Main Agent가 서브에이전트 결과를 받아서 대리 기록**

#### **역할 분담**

| 역할 | 수행자 | 기록자 | 기록 필드 |
|------|--------|--------|----------|
| Task 작업 | Task Agent **서브에이전트** | Main Agent | #10-13 (진행/상태/파일/이력) |
| Task 검증 | Verification Agent **서브에이전트** | Main Agent | #16-21 (테스트/빌드/검증) |

**Task Agent (작업 담당 Sub-agent):**
- 예시: `frontend-developer`, `backend-developer`, `database-developer`
- **반드시 서브에이전트로 투입** (Main Agent가 직접 작업 금지)
- 실제 코드 작성, 기본 테스트 실행
- 작업 완료 후 **결과 보고서를 Main Agent에게 반환**

**Verification Agent (검증 담당 Sub-agent):**
- 예시: `code-reviewer`, `qa-specialist`, `test-engineer`
- 속성 #15 `verification_agent`에 지정
- **반드시 서브에이전트로 투입** (Main Agent가 직접 검증 금지)
- 코드 리뷰, 테스트 검증, 품질 확인
- 검증 완료 후 **검증 결과를 Main Agent에게 반환**

#### **작업-검증 프로세스 (7단계)**

```
┌─────────────────────────────────────────────────────────────────┐
│  1단계: Task 작업 - 서브에이전트 수행, Main Agent 기록          │
└─────────────────────────────────────────────────────────────────┘

[1. Main Agent → Task Agent 서브에이전트 투입]
Main Agent가 Task tool로 서브에이전트 투입
  └─ 예: Task tool (subagent_type="frontend-developer")
       ↓
[2. Task Agent 서브에이전트 → 작업 수행]
frontend-developer 서브에이전트가 작업
  - 파일 생성
  - 기능 구현
  - 기본 테스트
       ↓
[3. Task Agent 서브에이전트 → 결과 반환]
서브에이전트가 작업 결과를 Main Agent에게 반환
  - 생성된 파일 목록
  - 수정 이력
  - 작업 완료 상태
       ↓
[4. Main Agent → Grid에 작업 결과 기록]
Main Agent가 서브에이전트 결과를 받아 Grid에 기록:
  - generated_files: 생성된 파일 목록
  - modification_history: 수정 이력
  - task_status: 'Completed'
  - task_progress: 100

┌─────────────────────────────────────────────────────────────────┐
│  2단계: Task 검증 - 서브에이전트 수행, Main Agent 기록          │
└─────────────────────────────────────────────────────────────────┘
       ↓
[5. Main Agent → Verification Agent 서브에이전트 투입]
Main Agent가 Task tool로 서브에이전트 투입
  └─ 예: Task tool (subagent_type="code-reviewer")
       ↓
[6. Verification Agent 서브에이전트 → 검증 수행]
code-reviewer 서브에이전트가 검증
  - 코드 리뷰
  - 테스트 확인
  - 빌드 확인
       ↓
[7. Verification Agent 서브에이전트 → 결과 반환]
서브에이전트가 검증 결과를 Main Agent에게 반환
  - 테스트 결과
  - 빌드 결과
  - 종합 검증 결과
       ↓
[8. Main Agent → Grid에 검증 결과 기록]
Main Agent가 서브에이전트 결과를 받아 Grid에 기록:
  - test: 테스트 결과 JSON
  - build: 빌드 결과 JSON
  - integration_verification: 통합 검증 JSON
  - blockers: 차단 요소 JSON
  - comprehensive_verification: 종합 검증 JSON
  - verification_status: 'Passed' 또는 'Failed'
       ↓
[9. 결과]
✅ Pass → Task 완료, 다음 Task 진행
❌ Fail → Task Agent 재투입하여 재작업
```

#### **왜 Main Agent가 대리 기록하는가?**

```
기술적 이유:
├─ 서브에이전트는 Task tool 완료 시 결과를 텍스트로 반환
├─ 서브에이전트의 환경 변수/Supabase 접근이 불안정할 수 있음
├─ Main Agent가 Grid 전체를 총괄하여 일관성 유지
└─ 서브에이전트 중간 종료 시 기록 누락 방지
```

#### **❌ 금지 사항**

```
❌ Main Agent(Claude Code)가 직접 Task 작업 수행
❌ Main Agent(Claude Code)가 직접 Task 검증 수행
❌ Task Agent가 검증까지 수행 (작성자 ≠ 검증자)
❌ 서브에이전트 투입 없이 작업/검증 완료 표시
❌ 서브에이전트 결과 확인 없이 Grid에 기록
```

#### **✅ 올바른 방식**

```
✅ Task 작업: Task Agent 서브에이전트 투입 → 작업 수행 → 결과 반환 → Main Agent가 Grid 기록
✅ Task 검증: Verification Agent 서브에이전트 투입 → 검증 수행 → 결과 반환 → Main Agent가 Grid 기록
✅ 작성자 ≠ 검증자 원칙 준수
✅ Main Agent는 서브에이전트 투입/조율/기록 담당
```

#### **Grid 기록 필드 구분**

| 단계 | 기록 필드 | 기록자 |
|------|----------|--------|
| Task 작업 결과 | #10 task_progress, #11 task_status, #12 generated_files, #13 modification_history | Main Agent (서브에이전트 결과 기반) |
| Task 검증 결과 | #16 test, #17 build, #18 integration_verification, #19 blockers, #20 comprehensive_verification, #21 verification_status | Main Agent (서브에이전트 결과 기반) |

#### **세션 중단 시**

```
세션 A에서 작업 중 → 컨텍스트 한도 도달
       ↓
세션 종료
       ↓
새 세션 B 시작
       ↓
새 세션의 Main Agent가 서브에이전트 재투입
  - 동일 Task Agent 서브에이전트로 작업 계속
  - 동일 Verification Agent 서브에이전트로 검증
```

---

### 9.3 2단계: Stage Gate - AI 자동 검증 (Main Agent)

#### **검증자: Main Agent**

**Main Agent란?**
- 해당 세션의 Claude Code
- PROJECT SAL GRID를 총괄
- Grid 수정 권한 보유

#### **검증 항목**

```
[Main Agent 자동 검증]
├─ Stage 내 모든 Task 완료 확인
├─ 전체 빌드 성공 확인
├─ 통합 테스트 통과 확인
├─ 의존성 체인 완결성
├─ 파일 생성 완료 확인
└─ 자동 검증 리포트 생성 및 저장
```

#### **⭐ Stage Gate 검증 리포트 저장 (필수!)**

**저장 위치:**
```
S0_S0_Project-SAL-Grid_생성/sal-grid/stage-gates/
├── TEMPLATE_stage_gate_report.md    ← 템플릿
├── S1GATE_verification_report.md    ← Stage 1 검증 리포트
├── S2GATE_verification_report.md    ← Stage 2 검증 리포트
├── S3GATE_verification_report.md    ← Stage 3 검증 리포트
├── S4GATE_verification_report.md    ← Stage 4 검증 리포트
└── S5GATE_verification_report.md    ← Stage 5 검증 리포트
```

**파일명 규칙:**
```
S{N}GATE_verification_report.md

예시:
- S1GATE_verification_report.md (Stage 1)
- S2GATE_verification_report.md (Stage 2)
```

**리포트 내용:**
- Stage 완료 현황 (Task 완료율)
- 빌드 검증 결과
- 테스트 검증 결과 (Unit, Integration, E2E)
- 의존성 체인 검증
- 산출물 검증
- 블로커 확인
- 종합 판정

**DB 기록 (stage_verification 테이블):**
```sql
UPDATE stage_verification SET
  verification_report_path = 'S0_S0_Project-SAL-Grid_생성/sal-grid/stage-gates/S1GATE_verification_report.md',
  ai_verification_note = '검증 의견',
  ai_verification_date = NOW(),
  stage_gate_status = 'AI Verified'
WHERE stage_name = 'Stage 1';
```

#### **검증 프로세스**

```
[Stage 1의 모든 Task 완료]
S1M1, S1M2, S1U1, S1D1... 완료
       ↓
[S1GATE 도달]
       ↓
[Main Agent 자동 검증]
해당 세션의 Claude Code가:
  - 모든 Task 상태 확인
  - 빌드 실행
  - 테스트 실행
  - 리포트 작성
       ↓
[결과]
✅ Pass → 3단계로 진행
❌ Fail → Task 재작업
```

#### **세션 전환 시**

```
세션 A에서 Stage 1 작업 중
  - S1M1, S1M2, S1M3 완료
       ↓
컨텍스트 한도로 세션 종료
       ↓
새 세션 B 시작
  - S1M4, S1M5... 계속 진행
  - S1GATE 도달
       ↓
새 세션 B의 Main Agent가 검증
  - Stage 1 전체 검증
  - 이전 세션 작업 포함
```

**핵심:**
- Main Agent = 그 세션의 Claude Code
- 세션 바뀌면 = 새 세션의 Main Agent가 검증
- Stage 전체를 한 번에 검증

---

### 9.4 3단계: Stage Gate - Project Owner 수동 검증

#### **검증자: Project Owner**

**검증 항목:**
```
[Project Owner 검증]
├─ PROJECT SAL GRID 확인
├─ AI 검증 리포트 검토
├─ 실제 결과물 확인
├─ 비즈니스 목표 달성 여부
├─ 다음 Stage 준비 상태
└─ 최종 판단
```

#### **판단 결과**

**✅ 승인:**
```
관리자 → 관리 UI에서 [승인] 버튼
또는
관리자 → Supabase 직접 수정
  stage_gate_status = 'Approved'
       ↓
Stage 1 완료 ✅
Stage 2 자동 시작 🚀
```

**❌ 거부:**
```
관리자 → Inbox로 Order Sheet 발행
  - 문제점 지적
  - 수정 지시
  - 구체적 작업 요청
       ↓
Claude → 지적사항 수정
       ↓
Claude → Outbox로 완료 보고
       ↓
관리자 → 재검증
       ↓
승인 또는 추가 수정
```

---

### 9.5 검증 시스템 요약

| 단계 | 시점 | 검증자 | 대상 | 권한 |
|------|------|--------|------|------|
| **1단계** | Task 완료 시 | 전문 검증 Sub-agent | 개별 Task | 검증만 |
| **2단계** | Stage 완료 시 | Main Agent (Claude Code) | Stage 전체 | Grid 수정 |
| **3단계** | AI 검증 후 | Project Owner | Stage 품질 | 최종 승인 |

**특징:**
- 3중 안전장치
- 각 단계 독립적 검증
- 세션 전환 대응
- 품질 보증 체계화

---

## 10. Stage Gate 시스템

### 10.1 Stage Gate 개념

**각 Stage 끝에 있는 관문 (검문소)**

```
Stage 1 Tasks → S1GATE → Stage 2 Tasks → S2GATE → ...
                  ↑                        ↑
               관문 승인                  관문 승인
```

### 10.2 Gate 통과 조건

#### **필수 조건:**
```
✅ Stage 내 모든 핵심 Task 완료
✅ 2단계 검증 통과 (Main Agent)
✅ 3단계 검증 승인 (Project Owner)
```

#### **통과 효과:**
```
Gate 승인 시:
  ├─ 현재 Stage 완료 ✅
  ├─ 다음 Stage 자동 시작
  └─ 다음 Stage의 모든 Task 병렬 실행 가능
```

---

### 10.3 Stage Gate Task 구조

```json
{
  "task_id": "S1GATE",
  "stage": "S1",
  "area": "GATE",
  "title": "Stage 1 Gate",
  "dependencies": "S1M5,S1U3,S1D4",
  "status": "Pending",
  "stage_gate_status": "Pending"
}
```

**Stage Gate 체크리스트:**

각 Stage별 Gate는 해당 Stage의 핵심 Task들을 dependencies로 가지며, 다음 항목들을 검증합니다:

#### **공통 체크리스트:**
```
□ 모든 핵심 Task 완료
□ 전체 빌드 성공
□ 통합 테스트 통과
□ 의존성 체인 완결성
□ 산출물 완성도
□ 문서화 완료
```

#### **Stage별 특화 체크리스트:**

**S1GATE (기획 단계):**
```
□ 요구사항 문서 완성
□ ERD 설계 완료
□ API 설계서 작성
□ 목업/와이어프레임 완성
□ 기술 스택 결정
```

**S2GATE (제작 단계):**
```
□ 프로토타입 동작 확인
□ 핵심 화면 구현
□ 기본 API 연동
□ 데이터베이스 테스트 데이터 구축
```

**S3GATE (개발 준비):**
```
□ 개발 환경 세팅 완료
□ CI/CD 파이프라인 구축
□ 코드 스타일 가이드 설정
□ 테스트 프레임워크 구축
```

**S4GATE (프로덕션 개발):**
```
□ 모든 기능 구현 완료
□ 전체 테스트 통과
□ 성능 최적화 완료
□ 보안 검토 완료
```

**S5GATE (개발 마무리):**
```
□ 배포 완료
□ 모니터링 시스템 구축
□ 백업 체계 확립
□ 운영 매뉴얼 작성
```

---

### 10.4 승인/거부 처리

#### **✅ 승인 시**

**방법 1: 관리 UI**
```
Project Owner → [승인] 버튼 클릭
→ stage_gate_status = "Approved"
→ 자동으로 다음 Stage 시작
```

**방법 2: Supabase 직접 수정**
```sql
UPDATE project_grid
SET stage_gate_status = 'Approved',
    updated_at = NOW()
WHERE task_id = 'S1GATE';
```

**결과:**
- Stage 완료 ✅
- 다음 Stage 자동 시작 🚀
- Order Sheet 불필요!

#### **❌ 거부 시**

**Inbox로 Order Sheet 발행:**
```json
{
  "type": "stage_gate_rejection",
  "gate_id": "S1GATE",
  "reason": "데이터베이스 스키마 미완성",
  "required_tasks": [
    {
      "task_id": "S1D5",
      "issue": "users 테이블에 profile 관계 누락",
      "instruction": "users-profiles 1:1 관계 추가"
    }
  ]
}
```

**처리 흐름:**
```
Project Owner → Inbox에 Order Sheet 발행
  ↓
Claude → 지적사항 수정 작업
  ↓
Claude → Outbox로 완료 보고
  ↓
Project Owner → 재검증
  ↓
승인 또는 추가 수정
```

**Gate 실패 시 Roll-back:**
```
[Gate 거부 발생]
       ↓
현재 Stage로 복귀
       ↓
문제 Task 재작업
       ↓
재검증 요청
       ↓
Gate 재도전
```

---

### 10.5 Stage Gate 자동화

#### **1. 병목 방지**
- Gate 통과 = 다음 Stage 전체 병렬 실행
- Stage 단위 진행으로 효율적

#### **2. 품질 보증**
- 2중 검증 (AI + 인간)
- Stage별 품질 체크포인트

#### **3. 유연한 통제**
- 관리자가 진행 속도 조절
- 필요시 Stage 재작업 가능

#### **4. 명확한 마일스톤**
- Stage 완료 시점 명확
- 프로젝트 진행 상황 가시화

**자동화 스크립트 예시:**

```python
# gate_automation.py
def check_stage_gate(stage_id):
    """
    Stage Gate 자동 검증 스크립트
    """
    # 1. 모든 Task 완료 확인
    incomplete_tasks = get_incomplete_tasks(stage_id)
    if incomplete_tasks:
        return {
            "status": "fail",
            "reason": "미완료 Task 존재",
            "tasks": incomplete_tasks
        }

    # 2. 빌드 실행
    build_result = run_build()
    if not build_result.success:
        return {
            "status": "fail",
            "reason": "빌드 실패",
            "error": build_result.error
        }

    # 3. 테스트 실행
    test_result = run_tests()
    if not test_result.success:
        return {
            "status": "fail",
            "reason": "테스트 실패",
            "failed_tests": test_result.failures
        }

    # 4. 의존성 체크
    dependency_check = verify_dependencies(stage_id)
    if not dependency_check.valid:
        return {
            "status": "fail",
            "reason": "의존성 미충족",
            "missing": dependency_check.missing
        }

    return {
        "status": "pass",
        "message": "모든 검증 통과"
    }
```

---

## 11. Orders/Reports JSON 시스템

### 11.1 개요

**Orders/Reports JSON System**은 Project Owner와 AI 간의 비동기 커뮤니케이션 시스템입니다.

**목적:**
- 세션 중단에도 불구하고 연속성 유지
- Project Owner의 실시간 개입
- Order Sheet 전달 및 완료 보고

**핵심 구성:**
```
Project Owner
        ↓ Orders
   Order Sheet 발행
        ↓
Claude (AI Agent)
  작업 실행
        ↓ Reports
   완료 보고
        ↓
Human Manager
  검토 및 승인
```

---

### 11.2 Orders (수신함)

#### **역할:**
- Project Owner → Claude
- Order Sheet 전달
- 작업 지시 전달

#### **저장 위치:**
- Supabase `orders` 테이블
- Human_ClaudeCode_Bridge/Orders/ 폴더 (JSON 파일)

#### **JSON 구조:**
```json
{
  "id": "inbox_001",
  "timestamp": "2025-11-23T14:30:00Z",
  "from": "human_manager",
  "to": "claude",
  "type": "order_sheet",
  "status": "unread",
  "content": {
    // Order Sheet 내용
  }
}
```

#### **Orders JSON 속성:**

| 속성 | 타입 | 설명 | 필수 |
|------|------|------|------|
| `id` | string | 고유 식별자 | ✅ |
| `timestamp` | ISO8601 | 생성 시간 | ✅ |
| `from` | string | 발신자 (human_manager) | ✅ |
| `to` | string | 수신자 (claude) | ✅ |
| `type` | string | 메시지 타입 (order_sheet, instruction, query) | ✅ |
| `status` | string | 상태 (unread, read, processing, completed) | ✅ |
| `content` | object | 실제 내용 (Order Sheet 또는 지시사항) | ✅ |
| `priority` | string | 우선순위 (low, normal, high, urgent) | optional |
| `related_task_ids` | array | 관련 Task ID 목록 | optional |

---

### 11.3 Reports (발신함)

#### **역할:**
- Claude → Project Owner
- 작업 완료 보고
- 질문/요청

#### **저장 위치:**
- Supabase `reports` 테이블
- Human_ClaudeCode_Bridge/Reports/ 폴더 (JSON 파일)

#### **JSON 구조:**
```json
{
  "id": "outbox_001",
  "timestamp": "2025-11-23T16:00:00Z",
  "from": "claude",
  "to": "human_manager",
  "type": "completion_report",
  "content": {
    "task_id": "S4F5",
    "status": "completed",
    "message": "사용자 프로필 페이지 구현 완료",
    "output_files": [
      "src/app/profile/page.tsx",
      "src/components/ProfileCard.tsx"
    ]
  }
}
```

#### **Reports JSON 속성:**

| 속성 | 타입 | 설명 | 필수 |
|------|------|------|------|
| `id` | string | 고유 식별자 | ✅ |
| `timestamp` | ISO8601 | 생성 시간 | ✅ |
| `from` | string | 발신자 (claude) | ✅ |
| `to` | string | 수신자 (human_manager) | ✅ |
| `type` | string | 메시지 타입 (completion_report, question, status_update) | ✅ |
| `content` | object | 실제 내용 | ✅ |
| `task_id` | string | 관련 Task ID | optional |
| `status` | string | 작업 상태 | optional |
| `output_files` | array | 생성된 파일 목록 | optional |
| `git_commits` | array | 관련 Git 커밋 해시 | optional |
| `verification_result` | object | 검증 결과 | optional |

---

### 11.4 활용 예시

#### **Order Sheet 발행 (Orders 활용)**

Project Owner가 Orders를 통해 Order Sheet를 발행하는 시점:

**1. Stage Start (단계 시작)**
```json
{
  "type": "order_sheet",
  "subtype": "stage_start",
  "stage": "S2",
  "instructions": "프로토타입 단계 시작. 핵심 기능만 구현하고 세부사항은 생략."
}
```

**2. Stage Gate Rejection (관문 거부)**
```json
{
  "type": "order_sheet",
  "subtype": "stage_gate_rejection",
  "gate_id": "S1GATE",
  "issues": [
    {
      "task_id": "S1D3",
      "problem": "RLS 정책 누락",
      "instruction": "모든 테이블에 RLS 정책 추가"
    }
  ]
}
```

**3. Ad-hoc Instruction (수시 지시)**
```json
{
  "type": "order_sheet",
  "subtype": "ad_hoc",
  "target_tasks": ["S4F5", "S4F6"],
  "instruction": "반응형 디자인 우선순위 상향. 모바일 먼저 완성.",
  "priority": "high"
}
```

#### **Task 간 데이터 전달 예시:**

**시나리오:** S1M1에서 작성한 요구사항을 S1U1에서 활용

**S1M1의 Outbox:**
```json
{
  "id": "outbox_s1m1",
  "task_id": "S1M1",
  "type": "completion_report",
  "content": {
    "status": "completed",
    "output_files": ["docs/requirements.md"],
    "shared_data": {
      "key_features": [
        "사용자 인증",
        "정치인 검색",
        "투표 기록"
      ],
      "target_users": "20-40대 정치 관심층"
    }
  }
}
```

**S1U1의 Inbox (자동 생성):**
```json
{
  "id": "inbox_s1u1",
  "task_id": "S1U1",
  "type": "dependency_data",
  "from_task": "S1M1",
  "content": {
    "requirements": "docs/requirements.md 참조",
    "key_features": [
      "사용자 인증",
      "정치인 검색",
      "투표 기록"
    ]
  }
}
```

---

### 11.5 Best Practices

#### **처리 흐름**

```
[Project Owner]
  Stage 1 시작 결정
        ↓
  Inbox에 Order Sheet 발행
  {
    "type": "stage_start",
    "stage": "S1",
    "instructions": "..."
  }
        ↓
[Claude 세션 A]
  Inbox 확인
  Order Sheet 읽기
  S1M1, S1M2... 작업 시작
        ↓
  컨텍스트 한도 도달
  Outbox에 중간 보고
  {
    "status": "in_progress",
    "completed": ["S1M1", "S1M2"],
    "next": "S1M3"
  }
        ↓
  세션 종료
        ↓
[Claude 세션 B]
  Inbox 확인 (새 지시 있나?)
  Outbox 확인 (이전 진행 상황)
  S1M3부터 계속...
        ↓
  Stage 1 완료
  Outbox에 완료 보고
        ↓
[Project Owner]
  Outbox 확인
  Stage Gate 승인/거부 결정
```

#### **핵심 원칙**

**1. 비동기 커뮤니케이션**
- 실시간 응답 불필요
- JSON 파일로 영속성 보장

**2. 세션 독립성**
- 각 Claude 세션은 Orders/Reports로 연결
- 이전 세션 상태 파악 가능

**3. 인간 중심 제어**
- Project Owner가 언제든 개입 가능
- Order Sheet 발행으로 방향 수정

**4. 추적 가능성**
- 모든 커뮤니케이션 기록
- 타임스탬프로 순서 보장

#### **Orders/Reports 사용 가이드라인:**

```
✅ DO:
  - 모든 메시지에 타임스탬프 포함
  - Task ID 명시로 추적성 확보
  - 명확한 메시지 타입 사용
  - 읽은 후 status 업데이트

❌ DON'T:
  - 중요 정보 누락
  - 타임스탬프 없이 생성
  - 모호한 메시지 작성
  - status 업데이트 생략
```

---

## 12. Git 통합 추적 시스템

### 12.1 개요

**Git 통합 추적 시스템**은 Task ID를 기반으로 코드와 작업을 완벽하게 추적하는 시스템입니다.

**Git 통합의 필요성:**

1. **작업 추적성:** 모든 코드 변경을 Task로 역추적
2. **버전 관리:** Git 이력과 작업 기록 자동 연동
3. **협업 효율:** 누가 어떤 작업을 했는지 즉시 확인
4. **품질 보증:** 모든 파일의 출처와 작업자 명확

**핵심 원칙:**
- 모든 파일에 Task ID 헤더 포함
- 모든 Git 커밋에 Task ID 포함
- 양방향 추적 가능

---

### 12.2 Task ID 헤더 의무화

**모든 AI가 생성하는 소스 코드 파일은 반드시 Task ID 헤더를 포함해야 합니다.**

#### **TypeScript/JavaScript 파일**
```typescript
/**
 * Project Grid Task ID: S1F1
 * 작업명: 회원가입 페이지 구현
 * 생성시간: 2025-11-23 14:30
 * 생성자: Claude-Sonnet-4.5
 * 의존성: S1B2 (Supabase 클라이언트 설정)
 * 설명: 회원가입 폼 UI 및 유효성 검증 로직
 */

export default function SignupPage() {
  // 코드...
}
```

#### **Python 파일**
```python
"""
Project Grid Task ID: S2B3
작업명: 정치인 검색 API 구현
생성시간: 2025-11-23 14:30
생성자: Claude-Sonnet-4.5
의존성: S2B1 (API 기반 구조), S2D2 (정치인 테이블)
설명: 정치인 검색 REST API 엔드포인트
"""

from fastapi import APIRouter
# 코드...
```

#### **SQL 파일**
```sql
-- Project Grid Task ID: S1D2
-- 작업명: 정치인 테이블 마이그레이션
-- 생성시간: 2025-11-23 14:30
-- 생성자: Claude-Sonnet-4.5
-- 의존성: S1D1 (사용자 테이블)
-- 설명: 정치인 정보 저장을 위한 테이블 생성

CREATE TABLE politicians (
  id UUID PRIMARY KEY,
  -- ...
);
```

#### **Markdown 파일**
```markdown
<!--
Project Grid Task ID: S2B3
작업명: 정치인 검색 API 문서
생성시간: 2025-11-23 14:30
생성자: Claude-Sonnet-4.5
-->

# 정치인 검색 API

...
```

#### **헤더 포함 이유:**

1. **역추적 가능:** 파일을 보면 어떤 Task에서 생성되었는지 즉시 파악
2. **의존성 파악:** 어떤 작업에 의존하는지 명시
3. **생성자 확인:** AI 모델 및 생성 시간 기록
4. **작업 설명:** 파일의 목적과 역할 명시

---

### 12.3 파일 명명 규칙

**모든 생성 파일은 Task ID를 포함해야 합니다:**

```
형식: {TaskID}_{설명}.{확장자}

예시:
- S2B5_auth_api.py
- S2B5_auth_test.py
- S2F3_login_component.tsx
- S2B5_REPORT.md (자동 생성)
```

**테스트 파일:**
```
형식: {TaskID}_{테스트대상}_test.{확장자}

예시:
- S2B5_auth_test.spec.ts (단위 테스트)
- S2B5_login_integration_test.ts (통합 테스트)
- S3T1_e2e_test.ts (E2E 테스트)
```

**파일명 규칙 장점:**
- 파일명만으로 Task 추적
- 같은 Task의 파일들 그룹화
- 자동화 스크립트 작성 용이

---

### 12.4 Git 커밋 형식

**모든 Git 커밋 메시지는 Task ID를 포함해야 합니다.**

#### **커밋 메시지 형식**
```bash
[작업ID] 작업유형: 설명

- 상세 변경사항 1
- 상세 변경사항 2
- 상세 변경사항 3

소요시간: 실제 소요시간
생성자: AI 모델명
```

#### **실제 예시**

**예시 1: 기능 추가**
```bash
[S1F1] feat: 회원가입 페이지 구현 완료

- app/signup/page.tsx 생성
- 회원가입 폼 UI 구현
- 유효성 검증 로직 추가
- Supabase Auth 연동

소요시간: 45분
생성자: Claude-Sonnet-4.5
```

**예시 2: API 구현**
```bash
[S2B3] feat: 정치인 검색 API 구현

- app/api/politicians/search/route.ts 생성
- 검색 쿼리 파라미터 처리
- Supabase 데이터베이스 검색
- 페이지네이션 구현

소요시간: 60분
생성자: Claude-Sonnet-4.5
```

**예시 3: 버그 수정**
```bash
[S4F3] fix: 로그인 폼 유효성 검증 오류 수정

- 이메일 형식 검증 로직 수정
- 에러 메시지 표시 개선
- 테스트 케이스 추가

소요시간: 20분
생성자: Claude-Sonnet-4.5
```

#### **작업 유형 태그**
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `refactor`: 코드 리팩토링
- `test`: 테스트 코드 추가/수정
- `docs`: 문서 작업
- `style`: 코드 포맷팅
- `perf`: 성능 개선
- `chore`: 빌드/설정 작업

#### **Commit 추적 방법:**

**git_commits 속성 활용:**

PROJECT SAL GRID의 각 Task에는 `git_commits` 속성(선택적)이 있으며, 해당 Task와 관련된 Git 커밋 해시를 기록합니다:

```json
{
  "task_id": "S2B3",
  "title": "정치인 검색 API 구현",
  "git_commits": [
    "a3f9c2d",
    "b7e4f1a",
    "c9d2e8b"
  ],
  "status": "Completed"
}
```

**양방향 추적:**
```
Task (S2B3) → Git Commits (a3f9c2d, b7e4f1a)
       ↕
Git Commit (a3f9c2d) → Task ID [S2B3]
```

**조회 방법:**
```bash
# Task ID로 커밋 찾기
git log --all --grep="S2B3"

# 커밋으로 Task 찾기
git show a3f9c2d | head -1
# [S2B3] feat: 정치인 검색 API 구현
```

---

### 12.5 브랜치 명명 규칙

#### **형식:**
```bash
grid/[작업ID]/[작업명-간략]
```

#### **예시:**
```bash
# Stage 2, Backend 3번 Task
git checkout -b grid/S2B5/user-auth-api

# Stage 1, Frontend 1번 Task
git checkout -b grid/S1F1/signup-page

# Stage 3, Test 1번 Task (개발 1차)
git checkout -b grid/S3T1/e2e-tests
```

#### **브랜치 전략:**

**Feature 브랜치:**
```
main
 ├── grid/S1M1/project-planning
 ├── grid/S1U1/erd-design
 ├── grid/S1F1/signup-page
 └── grid/S1B1/auth-api
```

**Stage 브랜치 (선택적):**
```
main
 ├── stage/s1-planning
 │   ├── grid/S1M1/project-planning
 │   └── grid/S1U1/erd-design
 └── stage/s2-prototype
     ├── grid/S2F1/homepage
     └── grid/S2B1/api-setup
```

#### **Task-Commit 매핑:**

**완벽한 추적을 위한 매핑 구조:**

```
PROJECT GRID (작업 관리)
    ↓ 작업 할당
Task ID 헤더 (소스 코드)
    ↓ 파일 생성
Git Commit (버전 관리)
    ↓ 커밋
GitHub Repository (원격 저장소)
    ↓ 푸시
작업 완료 기록 → PROJECT GRID 업데이트
    ↓ 역추적
코드 → Task ID → 작업 지시서
```

**양방향 추적 흐름:**
```
[Task] S2B3: 정치인 검색 API
   ↓ 파일 생성
[File] S2B3_politician_search.py
   ↓ Git 추가
[Commit] a3f9c2d: [S2B3] feat: 정치인 검색 API 구현
   ↓ Grid 업데이트
[Task] S2B3: status="Completed", git_commits=["a3f9c2d"]
```

---

### 12.6 자동화 스크립트

#### **git_commits 자동 업데이트 스크립트:**

```python
# update_git_commits.py
"""
Git 커밋을 PROJECT SAL GRID에 자동 반영하는 스크립트
"""
import subprocess
import json
import re

def get_recent_commits(task_id):
    """특정 Task ID의 최근 커밋 가져오기"""
    cmd = f'git log --all --grep="\\[{task_id}\\]" --format="%H"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip().split('\n')

def update_task_commits(task_id, commits):
    """Supabase에 git_commits 업데이트"""
    # Supabase 업데이트 로직
    pass

def main():
    # 최근 커밋 분석
    recent_commit = subprocess.run(
        'git log -1 --format="%s"',
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()

    # Task ID 추출
    match = re.match(r'\[(\w+)\]', recent_commit)
    if match:
        task_id = match.group(1)
        commits = get_recent_commits(task_id)
        update_task_commits(task_id, commits)
        print(f"✅ Task {task_id} updated with {len(commits)} commits")

if __name__ == "__main__":
    main()
```

#### **Git Hook 설정:**

```bash
# .git/hooks/post-commit
#!/bin/bash
# 커밋 후 자동으로 PROJECT GRID 업데이트

python3 scripts/update_git_commits.py
```

---

### 12.7 추적 시스템의 장점

**1. 완벽한 이력 관리**
- 어떤 코드든 Task ID로 역추적 가능
- Git 이력과 작업 기록 자동 연동

**2. 협업 효율성**
- 누가 어떤 작업을 했는지 즉시 확인
- 의존성 추적 및 충돌 방지

**3. 자동화 가능**
- Git hook을 통한 자동 검증
- PROJECT GRID 자동 업데이트

**4. 품질 보증**
- 모든 파일의 출처 명확
- 작업 시간, 생성자 정보 투명

---

### 12.8 필수 규칙

✅ **모든 파일**에 Task ID 헤더 포함
✅ **모든 커밋**에 Task ID 포함
✅ **파일명**에 Task ID 포함
✅ **실제 소요시간만** 기록
✅ **생성자 정보** 명시 (AI 모델명)

❌ 헤더 없는 파일 생성 금지
❌ Task ID 없는 커밋 금지
❌ 시간 예측 금지
❌ 애매한 파일명 금지

---

## 부록: 검증 및 추적 체크리스트

### A. 3단계 검증 체크리스트

**1단계: Task 검증**
```
□ Sub-agent가 코드 작성 완료
□ 기본 테스트 실행 통과
□ verification_agent 검증 완료
□ 검증 리포트 생성
□ Task status를 "Completed"로 업데이트
```

**2단계: Stage Gate AI 검증**
```
□ Stage 내 모든 Task 완료
□ 전체 빌드 성공
□ 통합 테스트 통과
□ 의존성 체인 완결성 확인
□ 파일 생성 완료 확인
□ 자동 검증 리포트 생성
```

**3단계: Project Owner 수동 검증**
```
□ PROJECT SAL GRID 검토
□ AI 검증 리포트 확인
□ 실제 결과물 확인
□ 비즈니스 목표 달성 확인
□ 다음 Stage 준비 상태 확인
□ 최종 승인 또는 거부 결정
```

### B. Stage Gate 체크리스트

```
□ 모든 핵심 Task 완료
□ dependencies 명시된 Task 모두 완료
□ 2단계 검증 통과
□ 3단계 검증 대기 또는 완료
□ stage_gate_status 업데이트
□ 다음 Stage 시작 준비
```

### C. Orders/Reports 체크리스트

**Orders (수신):**
```
□ 새 메시지 확인
□ Order Sheet 읽기
□ 우선순위 파악
□ 관련 Task 식별
□ status를 "read"로 업데이트
```

**Outbox (발신):**
```
□ 작업 완료 보고 작성
□ 산출물 파일 목록 포함
□ Git 커밋 해시 포함
□ 검증 결과 첨부
□ timestamp 포함
```

### D. Git 통합 체크리스트

**파일 생성 시:**
```
□ Task ID 헤더 포함
□ 작업명 명시
□ 생성시간 기록
□ 생성자 (AI 모델명) 명시
□ 의존성 Task 나열
□ 파일 설명 작성
□ 파일명에 Task ID 포함
```

**Git 커밋 시:**
```
□ 커밋 메시지에 [TaskID] 포함
□ 작업 유형 태그 사용
□ 상세 변경사항 나열
□ 소요시간 기록
□ 생성자 명시
□ git_commits 속성 업데이트
```

**브랜치 작업 시:**
```
□ grid/[TaskID]/[작업명] 형식 준수
□ 브랜치명 명확하게 작성
□ 작업 완료 후 main에 병합
□ 병합 후 브랜치 삭제 고려
```

---

## 결론

PART 3에서는 PROJECT SAL GRID의 품질 보증과 추적 시스템을 다루었습니다:

1. **3단계 검증 시스템**: Task → Stage Gate (AI) → Stage Gate (Human)의 3중 안전장치
2. **Stage Gate 시스템**: 각 Stage의 품질을 보증하는 관문 시스템
3. **Orders/Reports JSON 시스템**: 비동기 커뮤니케이션으로 세션 중단에도 연속성 유지
4. **Git 통합 추적 시스템**: Task ID 기반 완벽한 코드 추적

이 시스템들은 AI와 인간이 협업하는 대규모 프로젝트에서 품질과 추적성을 보장합니다.

---

# PART 4: 데이터 저장 방식 선택 및 설정

## 📌 데이터 저장 방식 선택 가이드 (v4.0 신규)

> PROJECT SAL GRID는 **두 가지 데이터 저장 방식**을 지원합니다.
> 프로젝트 상황에 맞는 방식을 선택하세요.

### 두 가지 방식 비교

| 항목 | DB Method (Supabase) | CSV Method (JSON) |
|------|---------------------|-------------------|
| **데이터 저장** | Supabase 클라우드 DB | 로컬 JSON 파일 |
| **장점** | 실시간 동기화, 다중 사용자, 웹 API | 설치 불필요, 독립 실행, Git 추적 |
| **단점** | Supabase 계정/설정 필요 | 단일 사용자, 수동 동기화 |
| **추천 대상** | 팀 프로젝트, 클라우드 선호 | 개인 프로젝트, 오프라인 작업 |

### 방식 선택 가이드

```
[방식 선택 플로우]

Supabase를 사용할 수 있는가?
    │
    ├─ Yes → DB Method (섹션 13~17)
    │        └─ Supabase 설정 → REST API로 CRUD
    │
    └─ No → CSV Method (아래 가이드)
            └─ JSON 파일로 Grid 데이터 관리
```

### CSV Method 간단 가이드

**1. 데이터 파일 위치:**
```
S0_Project-SAL-Grid_생성/
└── data/
    └── project_sal_grid.json    ← Grid 데이터 저장
```

**2. JSON 파일 구조:**
```json
{
    "tasks": [
        {
            "task_id": "S1F1",
            "task_name": "Task 이름",
            "stage": 1,
            "area": "F",
            "task_status": "Pending",
            "task_progress": 0,
            "verification_status": "Not Verified",
            "dependencies": "",
            "task_instruction": "수행 지침",
            "task_agent": "frontend-developer",
            "verification_instruction": "검증 지침",
            "verification_agent": "code-reviewer"
        }
    ],
    "metadata": {
        "version": "1.0",
        "updated_at": "2025-12-27T00:00:00Z"
    }
}
```

**3. CRUD 작업:**
- Claude Code의 Read/Edit 도구로 JSON 파일 직접 수정
- Task 추가: tasks 배열에 새 객체 추가
- Task 수정: 해당 task_id 항목 찾아 필드 수정
- Task 삭제: 해당 task_id 항목 제거

**4. Stage Gate 저장:**
```
S0_Project-SAL-Grid_생성/
└── stage-gates/
    ├── S1GATE_verification_report.md
    ├── S2GATE_verification_report.md
    └── ...
```

> **CSV Method를 선택한 경우**: 섹션 13~17(Supabase 설정)을 건너뛰고, 섹션 18(Viewer)부터 참조하세요.
> Viewer는 JSON 파일에서도 데이터를 읽어올 수 있습니다.

---

## 13. 5분 만에 시작하기 (DB Method)

> ⏱️ **목표**: 5분 안에 Supabase 프로젝트 만들고 테이블 생성하기

### 13-1. 준비물 체크

- [ ] 인터넷 연결
- [ ] 구글 또는 GitHub 계정 (로그인용)
- [ ] 2개 SQL 파일:
  - `template/supabase/schema.sql`
  - `STANDARD_PROJECT_SAL_GRID_FINAL.sql`

**파일 위치:**
```
{프로젝트 폴더}/
├── template\
│   └── supabase\
│       └── schema.sql (테이블 생성용)
└── STANDARD_PROJECT_SAL_GRID_FINAL.sql (표준 Task 데이터)
```

---

### 13-2. Supabase 프로젝트 생성 (2분)

**Step 1: 회원가입 및 로그인**

1. 브라우저에서 https://supabase.com 접속
2. 우측 상단 "Start your project" 클릭
3. GitHub 또는 Google 계정으로 로그인

![](https://supabase.com/images/...)

**Step 2: 새 프로젝트 만들기**

1. 로그인 후 "New Project" 버튼 클릭
2. Organization 선택 (처음이면 자동으로 생성됨)

**Step 3: 프로젝트 정보 입력**

```
📝 입력 항목 (초보자 추천값)

Name (프로젝트 이름):
→ My_Project_Grid
   (영문, 숫자, 언더스코어만 사용)

Database Password (비밀번호):
→ "Generate a password" 버튼 클릭
→ 자동 생성된 비밀번호 복사
→ ⚠️ 메모장에 안전하게 저장!

Region (지역):
→ Northeast Asia (Seoul) 선택
   (한국이면 서울이 가장 빠름)

Pricing Plan (요금제):
→ Free 선택
   (무료로 충분합니다)
```

4. "Create new project" 버튼 클릭
5. ⏱️ 약 2분 대기 (프로젝트 생성 중...)
6. 완료되면 Dashboard 화면으로 이동

**✅ 성공!** 이제 나만의 Supabase 프로젝트가 생겼습니다.

---

### 13-3. API 키 저장 (1분)

**중요:** 나중에 필요하니 지금 복사해두세요!

1. 왼쪽 사이드바 → **Settings** (톱니바퀴 아이콘) 클릭
2. **API** 메뉴 클릭
3. 다음 2가지 정보를 메모장에 복사:

```
📍 Project URL (프로젝트 주소)
https://abcdefghijk.supabase.co
👆 이 주소를 복사하세요

🔑 anon public (API 키)
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdX...
👆 이 긴 키를 복사하세요
```

**메모장 예시:**
```
내 Supabase 정보
-----------------
프로젝트 이름: My_Project_Grid
Project URL: https://abcdefghijk.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
비밀번호: (자동생성된 비밀번호)
```

**⚠️ 주의:**
- `anon public` 키는 안전 (공개해도 괜찮음)
- `service_role` 키는 **절대 공개 금지!** (우리는 사용 안 함)

---

### 13-4. AI 협업을 위한 .env 파일 설정 (중요!)

> **목적**: AI(Claude Code)가 Supabase에 직접 접근하여 CRUD 작업을 수행할 수 있게 합니다.

**역할 분담:**
```
┌─────────────────────────────────────────────────────────────┐
│  [Project Owner가 해야 할 일]                                │
│  1. Supabase 프로젝트 생성 (초기 셋업)                        │
│  2. SQL Editor에서 schema.sql 실행 (테이블 생성)              │
│  3. .env 파일 생성 및 API 키 저장                            │
├─────────────────────────────────────────────────────────────┤
│  [AI가 할 수 있는 일] (.env 파일 설정 후)                     │
│  1. REST API로 데이터 조회 (SELECT)                          │
│  2. REST API로 데이터 삽입 (INSERT)                          │
│  3. REST API로 데이터 수정 (UPDATE)                          │
│  4. REST API로 데이터 삭제 (DELETE)                          │
└─────────────────────────────────────────────────────────────┘
```

**프로젝트 루트에 `.env` 파일 생성:**

```bash
# ================================================================
# PROJECT SAL GRID - Supabase Configuration
# ================================================================

# Supabase Project URL
SUPABASE_URL=https://[your-project-id].supabase.co

# Supabase Anonymous Key (공개키 - 클라이언트에서 사용)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Supabase Service Role Key (비밀키 - 서버에서만 사용, 선택사항)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ 중요:**
- `.env` 파일이 있어야 AI가 Supabase에 접근 가능
- `.gitignore`에 `.env` 추가하여 Git에 커밋되지 않도록 설정
- `SUPABASE_URL`과 `SUPABASE_ANON_KEY`는 필수
- `SUPABASE_SERVICE_ROLE_KEY`는 RLS 우회 필요 시에만 사용

---

### 13-5. 다음 단계

✅ Supabase 프로젝트 생성 완료!

**이제 다음 중 선택:**

1. **바로 설치하고 싶다면** → [14. 표준 Grid 설치](#14-표준-grid-설치-66개-task)
2. **먼저 이해하고 싶다면** → [16. Supabase 기본 개념](#16-supabase-기본-개념)

---

## 14. 표준 Grid 설치

> ⏱️ **목표**: 표준 Task들을 내 Supabase에 설치하기

### 14-1. 설치 순서 (중요!)

```
순서를 꼭 지켜주세요!

1단계: schema.sql 실행 (테이블 생성)
   ↓
2단계: STANDARD_PROJECT_SAL_GRID_FINAL.sql 실행 (데이터 입력)

순서 바꾸면 에러 발생!
```

---

### 14-2. Step 1: 테이블 생성 (schema.sql)

**목적:** 빈 테이블(표)을 만듭니다. 엑셀의 빈 시트를 만드는 것과 같습니다.

**1. SQL Editor 열기**

1. 왼쪽 사이드바 → **SQL Editor** 아이콘 클릭
2. 상단 "+ New query" 버튼 클릭

**2. schema.sql 파일 열기**

```
파일 위치:
{프로젝트 폴더}/template\supabase\schema.sql

방법:
- 메모장으로 열기
- 또는 VS Code로 열기
- 전체 선택 (Ctrl+A)
- 복사 (Ctrl+C)
```

**3. SQL Editor에 붙여넣기**

1. Supabase SQL Editor 창에 커서 클릭
2. 붙여넣기 (Ctrl+V)
3. 긴 SQL 코드가 보이면 성공!

**4. 실행!**

1. 우측 하단 "Run" 버튼 클릭
   - 또는 키보드: `Ctrl + Enter` (Windows)
   - Mac: `Cmd + Enter`
2. ⏱️ 3-5초 대기

**5. 성공 확인**

✅ 성공하면 이런 메시지가 보입니다:
```
Success. No rows returned
```

또는 초록색 체크 표시 ✓

❌ 에러가 나면:
- [15-2. 자주 나는 에러](#15-2-자주-나는-에러) 참고

**6. 테이블 확인**

1. 왼쪽 사이드바 → **Table Editor** 클릭
2. `project_sal_grid_tasks` 테이블이 보이면 성공!
3. 클릭하면 빈 테이블(0 rows)이 보임

---

### 14-3. Step 2: 데이터 입력

**목적:** 표준 Task들을 테이블에 입력합니다.

**1. 새 SQL 쿼리 생성**

1. SQL Editor → "+ New query" 버튼 클릭
   (또는 기존 내용 전체 삭제 `Ctrl+A` → `Delete`)

**2. 데이터 파일 열기**

```
파일 위치:
{프로젝트 폴더}/STANDARD_PROJECT_SAL_GRID_FINAL.sql

주의:
- 매우 긴 파일입니다 (약 다수의 INSERT문)
- 끝까지 스크롤해서 전체 선택했는지 확인!

방법:
- 메모장으로 열기
- 전체 선택 (Ctrl+A)
- 복사 (Ctrl+C)
```

**3. SQL Editor에 붙여넣기**

1. Supabase SQL Editor에 붙여넣기 (Ctrl+V)
2. 스크롤해서 파일 끝까지 잘 붙여넣어졌는지 확인
3. 마지막 줄이 `);  -- S5C2` 이면 정상

**4. 실행!**

1. "Run" 버튼 클릭 (또는 Ctrl+Enter)
2. ⏱️ 10-20초 대기 (Task 입력 중...)

**5. 성공 확인**

✅ 성공하면:
```
Success. No rows returned
```
또는
```
Success. N rows affected
```
(N = 입력한 Task 개수)

**6. 데이터 확인**

1. 왼쪽 사이드바 → **Table Editor** 클릭
2. `project_sal_grid_tasks` 테이블 클릭
3. Task 개수만큼 rows가 표시되면 성공!
4. 스크롤하면 S1M1, S1M2, ... 순서대로 보임

---

### 14-4. 빠른 확인 SQL

**복사해서 SQL Editor에서 실행해보세요:**

```sql
-- 1. Task 개수 확인
SELECT COUNT(*) as total_tasks
FROM project_sal_grid_tasks;

-- 결과: 프로젝트 Task 기획서에 정의된 개수가 표시됨
```

```sql
-- 2. Stage별 분포 확인
SELECT stage, COUNT(*) as count
FROM project_sal_grid_tasks
GROUP BY stage
ORDER BY stage;

-- 결과: Stage 1~5별 Task 개수가 표시됨
-- (구체적인 개수는 TASK_PLAN.md 참조)
```

```sql
-- 3. 처음 10개 Task 보기
SELECT task_id, task_name, stage, area, priority
FROM project_sal_grid_tasks
ORDER BY task_id
LIMIT 10;

-- 결과: S1M1, S1M2, ... S1U4 등이 보임
```

---

### 14-5. 설치 완료! 🎉

**축하합니다!** 이제 다음을 완료했습니다:

- ✅ Supabase 프로젝트 생성
- ✅ `project_sal_grid_tasks` 테이블 생성
- ✅ 표준 Task 입력
- ✅ 5×11 매트릭스 완성

**다음 단계:**

1. [18. HTML Viewer로 Grid 보기](#18-html-viewer로-grid-보기) - 시각화
2. [19. Task 추가/수정/삭제](#19-task-추가수정삭제-방법) - 관리 방법

---

## 15. 설치 확인 및 문제 해결

### 15-1. 설치 체크리스트

**다음을 모두 확인하세요:**

```
설치 전:
☑ Supabase 계정 생성 완료
☑ 프로젝트 생성 완료
☑ API Key 복사 및 저장
☑ 2개 SQL 파일 준비됨

Step 1 (schema.sql):
☑ SQL Editor에서 schema.sql 실행
☑ "Success" 메시지 확인
☑ Table Editor에 project_sal_grid_tasks 테이블 생성됨
☑ 테이블이 비어있음 (0 rows)

Step 2 (데이터):
☑ 프로젝트 Task SQL 파일 실행
☑ "Success" 메시지 확인
☑ Table Editor에 Task 개수만큼 rows 표시
☑ SELECT COUNT(*) 실행 시 Task 개수 반환

최종 확인:
☑ Stage 1~5 각각 Task 존재
☑ Task ID: S1으로 시작해서 S5까지 존재
☑ 모든 Task에 task_name, stage, area 입력됨
```

---

### 15-2. 설치 중 에러가 발생하면

설치 과정에서 에러가 발생할 수 있습니다. 자주 발생하는 에러들:

| 에러 메시지 | 의미 | 빠른 해결 |
|------------|------|----------|
| `relation already exists` | 테이블이 이미 있음 | 기존 테이블 삭제 후 재실행 |
| `duplicate key value` | 같은 Task가 이미 있음 | 데이터 삭제 후 재입력 |
| `column does not exist` | 테이블 구조 오류 | 테이블 삭제 후 schema.sql 재실행 |
| `permission denied` | RLS 보안 정책 문제 | RLS 비활성화 후 재시도 |

> **상세한 에러 해결 방법은 [22. 문제 해결 A to Z](#22-문제-해결-a-to-z)를 참조하세요.**

---

## 16. Supabase 기본 개념

> 🤔 **초보자 설명**: 프로그래밍 몰라도 이해할 수 있게 설명합니다.

### 16-1. 엑셀로 이해하기

**엑셀과 비교:**

```
엑셀 파일          →  Supabase 프로젝트
엑셀 시트          →  테이블 (project_sal_grid_tasks)
행(Row)            →  Task 1개
열(Column)         →  속성 (task_id, task_name, stage 등)
필터 기능          →  SQL WHERE 절
정렬 기능          →  SQL ORDER BY
자동 저장          →  자동으로 클라우드에 저장됨
```

**차이점:**

| 기능 | 엑셀 | Supabase |
|------|------|----------|
| 저장 위치 | 내 컴퓨터 | 클라우드 (인터넷) |
| 동시 작업 | 어려움 | 여러 명 가능 |
| 자동화 | 매크로 필요 | API로 쉽게 가능 |
| 데이터 크기 | 100만 행 제한 | 무제한 (유료) |
| 실시간 업데이트 | 불가 | 가능 |

---

### 16-2. 왜 Supabase를 쓰나요?

**장점:**

1. **무료로 시작 가능**
   - 소규모 프로젝트는 평생 무료
   - 신용카드 등록 불필요

2. **프로그래밍 몰라도 사용 가능**
   - 웹 브라우저에서 모든 작업
   - SQL도 복사 붙여넣기면 됨

3. **어디서나 접근 가능**
   - 인터넷만 있으면 OK
   - 스마트폰에서도 가능

4. **자동 백업**
   - 데이터 손실 걱정 없음
   - 클라우드에 안전하게 저장

5. **팀 협업 가능**
   - URL과 Key만 공유하면 됨
   - 동시에 여러 명이 작업 가능

**단점:**

1. **인터넷 필요**
   - 오프라인에서는 작동 안 함

2. **무료 한도**
   - 500MB 데이터베이스
   - 월 2GB 전송량
   - (우리 프로젝트는 충분함)

3. **학습 필요**
   - SQL 기본 문법 알면 좋음
   - (하지만 복사 붙여넣기로도 가능)

---

### 16-3. PROJECT SAL GRID와 Supabase

**우리가 하는 일:**

```
1. PROJECT SAL GRID 정의
   ↓
2. Supabase에 저장 (클라우드 데이터베이스)
   ↓
3. 언제 어디서나 접근 가능
   ↓
4. HTML Viewer로 시각화
   ↓
5. Claude Code가 자동으로 업데이트
```

**전체 그림:**

```
┌─────────────────────────────────┐
│   Supabase Cloud (클라우드)      │
│                                 │
│  project_sal_grid_tasks        │
│  (Task 저장됨)             │
│                                 │
└─────────────────────────────────┘
         ↓         ↓         ↓
    ┌──────┐  ┌──────┐  ┌──────┐
    │ 내PC │  │Viewer│  │Claude│
    │(SQL) │  │(HTML)│  │(API) │
    └──────┘  └──────┘  └──────┘
```

---

## 17. CRUD 작업

> 🤔 **초보자 설명**: 데이터베이스의 4가지 기본 동작

### 17-1. CRUD란?

**C**reate (생성) - 새로 만들기
**R**ead (읽기) - 보기
**U**pdate (수정) - 고치기
**D**elete (삭제) - 지우기

### 17-2. 엑셀로 비유하면

| CRUD | 엑셀 작업 | Supabase SQL |
|------|-----------|--------------|
| **Create** | 새 행 추가 | INSERT |
| **Read** | 데이터 보기, 필터 | SELECT |
| **Update** | 셀 값 수정 | UPDATE |
| **Delete** | 행 삭제 | DELETE |

### 17-3. 실제 예시

**예시: Task "S1M1" 관리**

```sql
-- CREATE (생성): 새 Task 추가
INSERT INTO project_sal_grid_tasks (
  task_id, task_name, stage, area
) VALUES (
  'S1M1', '프로젝트 기획서 작성', 1, 'M'
);

-- READ (읽기): Task 보기
SELECT * FROM project_sal_grid_tasks
WHERE task_id = 'S1M1';

-- UPDATE (수정): 진행률 변경
UPDATE project_sal_grid_tasks
SET progress = 50, status = 'In Progress'
WHERE task_id = 'S1M1';

-- DELETE (삭제): Task 제거
DELETE FROM project_sal_grid_tasks
WHERE task_id = 'S1M1';
```

**초보자 팁:**
- SQL 몰라도 괜찮습니다
- 위 예시를 복사해서 값만 바꿔 쓰면 됩니다
- SQL Editor에 붙여넣기 → Run 하면 끝!

---

# PART 5: Viewer 및 자동화

## 18. HTML Viewer로 Grid 보기

> 🎨 **목표**: 브라우저에서 Grid를 예쁘게 보기

### 18-1. Viewer란?

**Viewer = Grid 시각화 도구**

- 엑셀처럼 표 형태로 보여줌
- 필터링 가능 (Stage, Status 등)
- 실시간 업데이트 반영
- 프로그래밍 불필요

**위치:**
```
{프로젝트 폴더}/template\viewer\
├── viewer.html (메인 파일)
└── run_viewer.py (간편 실행 스크립트)
```

---

### 18-2. Viewer 설정 (3분)

**Step 1: viewer.html 파일 열기**

1. `template/viewer/viewer.html` 파일을 메모장 또는 VS Code로 열기
2. 15-20번째 줄 근처에서 다음 찾기:

```javascript
// ⚠️ 본인의 Supabase 정보로 교체!
const SUPABASE_URL = 'https://xxxxx.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhb...'
```

**Step 2: 내 정보로 수정**

1. `SUPABASE_URL` 값을 내 Project URL로 변경
2. `SUPABASE_ANON_KEY` 값을 내 Anon Key로 변경

**예시:**
```javascript
// 수정 전:
const SUPABASE_URL = 'https://xxxxx.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhb...'

// 수정 후:
const SUPABASE_URL = 'https://abcdefghijk.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...'
```

3. 파일 저장 (Ctrl+S)

---

### 18-3. Viewer 실행

**방법 1: Python 스크립트 사용 (추천)**

```bash
# 터미널 또는 명령 프롬프트에서:
cd "{프로젝트 폴더}/template\viewer"
python run_viewer.py
```

- 자동으로 브라우저가 열립니다
- `http://localhost:8080/viewer.html`

**방법 2: 직접 실행**

1. `viewer.html` 파일을 브라우저로 드래그 앤 드롭
2. 또는 더블클릭

**방법 3: HTTP 서버 수동 실행**

```bash
# Python 3
cd "{프로젝트 폴더}/template\viewer"
python -m http.server 8080

# 브라우저에서 열기:
# http://localhost:8080/viewer.html
```

---

### 18-4. Viewer 사용법

**화면 구성:**

```
┌────────────────────────────────────┐
│  PROJECT SAL GRID Viewer          │
├────────────────────────────────────┤
│ [모든 Stage ▼] [모든 상태 ▼] [🔄] │  ← 필터
├────────────────────────────────────┤
│ Task ID │ 작업명 │ Stage │ Area │  │  ← 테이블
│ S1M1    │ 프로.. │   1   │  M   │  │
│ S1M2    │ 요구.. │   1   │  M   │  │
│ ...     │ ...    │  ...  │ ...  │  │
└────────────────────────────────────┘
```

**필터 사용:**

1. **Stage별 필터**
   - "모든 Stage" 드롭다운 클릭
   - "Stage 1: 프로토타입" 선택
   - → Stage 1 Task만 보임

2. **Status별 필터**
   - "모든 상태" 드롭다운 클릭
   - "대기" 선택
   - → Pending Task만 보임

3. **새로고침**
   - 🔄 버튼 클릭
   - → 최신 데이터 다시 불러오기

**실시간 업데이트:**
- Supabase에서 데이터 변경 시 자동 반영
- 새로고침 불필요 (Real-time 구독 기능)

---

### 18-5. Viewer 문제 해결

**문제 1: 데이터가 안 보임**

**확인 사항:**
1. Supabase URL과 Key가 정확한지 확인
2. F12 → Console 탭에서 에러 확인
3. Table Editor에서 데이터 존재 여부 확인

**해결:**
```javascript
// viewer.html 15-20번째 줄 다시 확인
// URL 끝에 / 없어야 함
// Key 전체가 복사되었는지 확인
```

**문제 2: "CORS error"**

**에러 메시지:**
```
Access to fetch at 'https://...' has been blocked by CORS policy
```

**해결:**
- Supabase는 기본적으로 CORS 허용
- 브라우저 캐시 삭제 후 재시도
- HTTP 서버 사용 (방법 1 또는 3)
- 파일을 직접 열지 말고 서버로 실행

**문제 3: "Invalid API key"**

**해결:**
1. Supabase Dashboard → Settings → API
2. Anon Key 다시 복사
3. viewer.html 수정 및 저장
4. 브라우저 새로고침 (Ctrl+F5)

---

## 19. Task 추가/수정/삭제 방법

> 🛠️ **목표**: SQL로 직접 Task 관리하기

### 19-1. 새 Task 추가 (CREATE)

**상황:** "긴급 버그 수정" Task를 추가하고 싶다.

**SQL:**
```sql
INSERT INTO project_sal_grid_tasks (
  task_id,
  task_name,
  stage,
  area,
  priority,
  task_description,
  execution_type,
  estimated_complexity,
  status,
  progress
) VALUES (
  'S4F99',                          -- Task ID (고유해야 함)
  '긴급 버그 수정',                 -- Task 이름
  4,                                -- Stage (1-5)
  'F',                              -- Area (M, U, F, BI, BA, D, S, T, O, E, C)
  'Critical',                       -- 우선순위
  '로그인 버그 긴급 수정 필요',      -- 설명
  'AI-Only',                        -- 실행 방식
  'Low',                            -- 복잡도
  'Pending',                        -- 상태
  0                                 -- 진행률 (0-100)
);
```

**실행:**
1. SQL Editor → New query
2. 위 SQL 복사 → 붙여넣기
3. 값 수정 (task_id, task_name 등)
4. Run 버튼 클릭

**확인:**
```sql
SELECT * FROM project_sal_grid_tasks
WHERE task_id = 'S4F99';
```

---

### 19-2. Task 수정 (UPDATE)

**상황 1: 진행률 업데이트**

```sql
-- Task S1M1의 진행률을 50%로 변경
UPDATE project_sal_grid_tasks
SET
  progress = 50,
  status = 'In Progress',
  updated_at = NOW()
WHERE task_id = 'S1M1';
```

**상황 2: Task 완료 처리**

```sql
-- Task S1M1 완료 처리
UPDATE project_sal_grid_tasks
SET
  progress = 100,
  status = 'Completed',
  completion_date = NOW(),
  updated_at = NOW()
WHERE task_id = 'S1M1';
```

**상황 3: 여러 필드 동시 수정**

```sql
-- Task 정보 대폭 수정
UPDATE project_sal_grid_tasks
SET
  task_name = '프로젝트 기획서 작성 (수정)',
  priority = 'High',
  task_description = '업데이트된 설명',
  notes = '기획서 양식 변경됨',
  updated_at = NOW()
WHERE task_id = 'S1M1';
```

**초보자 팁:**
- `WHERE task_id = 'S1M1'` 부분은 필수!
- 없으면 모든 Task가 수정됨 (위험!)
- 실행 전에 꼭 `SELECT`로 확인:
  ```sql
  SELECT * FROM project_sal_grid_tasks
  WHERE task_id = 'S1M1';
  ```

---

### 19-3. Task 삭제 (DELETE)

**⚠️ 주의: 삭제는 되돌릴 수 없습니다!**

**상황 1: 특정 Task 삭제**

```sql
-- 실행 전 확인
SELECT * FROM project_sal_grid_tasks
WHERE task_id = 'S4F99';

-- 삭제 실행
DELETE FROM project_sal_grid_tasks
WHERE task_id = 'S4F99';
```

**상황 2: 조건부 삭제**

```sql
-- Pending 상태의 Task만 삭제
DELETE FROM project_sal_grid_tasks
WHERE status = 'Pending';

-- Stage 6의 모든 Task 삭제
DELETE FROM project_sal_grid_tasks
WHERE stage = 5;
```

**상황 3: 전체 삭제 (초기화)**

```sql
-- ⚠️ 모든 데이터 삭제!
DELETE FROM project_sal_grid_tasks;

-- 확인
SELECT COUNT(*) FROM project_sal_grid_tasks;
-- 결과: 0
```

**안전한 삭제 순서:**

1. **먼저 SELECT로 확인**
   ```sql
   SELECT * FROM project_sal_grid_tasks
   WHERE task_id = 'S4F99';
   ```

2. **맞으면 DELETE 실행**
   ```sql
   DELETE FROM project_sal_grid_tasks
   WHERE task_id = 'S4F99';
   ```

3. **삭제 확인**
   ```sql
   SELECT * FROM project_sal_grid_tasks
   WHERE task_id = 'S4F99';
   -- 결과: 0 rows (삭제됨)
   ```

---

### 19-4. Task 조회 (READ)

**기본 조회:**

```sql
-- 모든 Task 보기
SELECT * FROM project_sal_grid_tasks
ORDER BY stage, area;

-- 특정 Task 보기
SELECT * FROM project_sal_grid_tasks
WHERE task_id = 'S1M1';

-- Stage별로 보기
SELECT * FROM project_sal_grid_tasks
WHERE stage = 1
ORDER BY area;
```

**필터링 조회:**

```sql
-- 대기 중인 Task만
SELECT task_id, task_name, stage, area
FROM project_sal_grid_tasks
WHERE status = 'Pending'
ORDER BY stage;

-- 진행률 50% 이상
SELECT task_id, task_name, progress
FROM project_sal_grid_tasks
WHERE progress >= 50;

-- Critical 우선순위
SELECT task_id, task_name, priority
FROM project_sal_grid_tasks
WHERE priority = 'Critical';
```

**집계 조회:**

```sql
-- Stage별 Task 개수
SELECT stage, COUNT(*) as count
FROM project_sal_grid_tasks
GROUP BY stage
ORDER BY stage;

-- 상태별 Task 개수
SELECT status, COUNT(*) as count
FROM project_sal_grid_tasks
GROUP BY status;

-- Area별 평균 진행률
SELECT area, AVG(progress) as avg_progress
FROM project_sal_grid_tasks
GROUP BY area;
```

**검색:**

```sql
-- Task 이름에 "API" 포함
SELECT task_id, task_name
FROM project_sal_grid_tasks
WHERE task_name LIKE '%API%';

-- Task 이름에 "설계" 포함
SELECT task_id, task_name
FROM project_sal_grid_tasks
WHERE task_name LIKE '%설계%';
```

---

### 19-5. 실전 시나리오

**시나리오 1: 새 프로젝트 시작**

```sql
-- 1. Stage 1 Task만 보기
SELECT task_id, task_name, depends_on
FROM project_sal_grid_tasks
WHERE stage = 1
ORDER BY task_id;

-- 2. 첫 번째 Task 시작
UPDATE project_sal_grid_tasks
SET status = 'In Progress', start_date = NOW()
WHERE task_id = 'S1M1';

-- 3. 완료 처리
UPDATE project_sal_grid_tasks
SET
  status = 'Completed',
  progress = 100,
  completion_date = NOW()
WHERE task_id = 'S1M1';
```

**시나리오 2: 진행 상황 확인**

```sql
-- 전체 진행률 확인
SELECT
  stage,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
  ROUND(AVG(progress), 1) as avg_progress
FROM project_sal_grid_tasks
GROUP BY stage
ORDER BY stage;
```

**시나리오 3: 긴급 Task 추가**

```sql
-- 1. 긴급 Task 추가
INSERT INTO project_sal_grid_tasks (
  task_id, task_name, stage, area, priority, status
) VALUES (
  'S4F99', '긴급 버그 수정', 4, 'F', 'Critical', 'Pending'
);

-- 2. 바로 시작
UPDATE project_sal_grid_tasks
SET status = 'In Progress', start_date = NOW()
WHERE task_id = 'S4F99';
```

---

## 20. Claude Code로 자동화

> 🤖 **대상**: 개발자 또는 자동화에 관심 있는 사용자

### 20-1. 자동화가 필요한 이유

**수동 관리의 한계:**
- Task마다 SQL 실행 번거로움
- 진행 상황 업데이트 깜빡할 수 있음
- 반복 작업이 많음

**자동화의 장점:**
- Claude Code가 알아서 Task 처리
- 진행 상황 자동 업데이트
- 24시간 작동 가능

---

### 20-2. 필수 라이브러리 설치

**JavaScript/Node.js:**
```bash
npm install @supabase/supabase-js dotenv
```

**Python:**
```bash
pip install supabase python-dotenv
```

---

### 20-3. 환경 변수 설정

**프로젝트 루트에 `.env` 파일 생성:**

```bash
# .env
SUPABASE_URL=https://abcdefghijk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ .gitignore에 추가:**
```bash
# .gitignore
.env
.env.local
.env.*.local
```

---

### 20-4. Supabase 클라이언트 생성

**JavaScript:**
```javascript
// supabase-client.js
const { createClient } = require('@supabase/supabase-js')
require('dotenv').config()

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
)

module.exports = supabase
```

**Python:**
```python
# supabase_client.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
```

---

### 20-5. CRUD 함수 예시

**JavaScript:**

```javascript
const supabase = require('./supabase-client')

// CREATE: 새 Task 추가
async function createTask(taskData) {
  const { data, error } = await supabase
    .from('project_sal_grid_tasks')
    .insert(taskData)

  if (error) {
    console.error('❌ Task 생성 실패:', error)
    return null
  }
  console.log('✅ Task 생성 완료:', data)
  return data
}

// READ: Task 조회
async function getTask(taskId) {
  const { data, error } = await supabase
    .from('project_sal_grid_tasks')
    .select('*')
    .eq('task_id', taskId)
    .single()

  if (error) {
    console.error('❌ 조회 실패:', error)
    return null
  }
  return data
}

// UPDATE: Task 수정
async function updateTask(taskId, updates) {
  const { data, error } = await supabase
    .from('project_sal_grid_tasks')
    .update(updates)
    .eq('task_id', taskId)

  if (error) {
    console.error('❌ 업데이트 실패:', error)
    return null
  }
  console.log('✅ 업데이트 완료:', taskId)
  return data
}

// DELETE: Task 삭제
async function deleteTask(taskId) {
  const { data, error } = await supabase
    .from('project_sal_grid_tasks')
    .delete()
    .eq('task_id', taskId)

  if (error) {
    console.error('❌ 삭제 실패:', error)
    return null
  }
  console.log('✅ 삭제 완료:', taskId)
  return data
}

// 사용 예시
async function main() {
  // 새 Task 추가
  await createTask({
    task_id: 'S4F99',
    task_name: '긴급 버그 수정',
    stage: 4,
    area: 'F',
    priority: 'Critical',
    status: 'Pending',
    progress: 0
  })

  // Task 조회
  const task = await getTask('S4F99')
  console.log('Task:', task)

  // Task 업데이트
  await updateTask('S4F99', {
    progress: 50,
    status: 'In Progress'
  })

  // Task 삭제
  // await deleteTask('S4F99')
}

main()
```

**Python:**

```python
from supabase_client import supabase

# CREATE
def create_task(task_data):
    response = supabase.table('project_sal_grid_tasks').insert(task_data).execute()
    print('✅ Task 생성 완료:', response.data)
    return response.data

# READ
def get_task(task_id):
    response = supabase.table('project_sal_grid_tasks')\
        .select('*')\
        .eq('task_id', task_id)\
        .execute()
    return response.data[0] if response.data else None

# UPDATE
def update_task(task_id, updates):
    response = supabase.table('project_sal_grid_tasks')\
        .update(updates)\
        .eq('task_id', task_id)\
        .execute()
    print('✅ 업데이트 완료:', task_id)
    return response.data

# DELETE
def delete_task(task_id):
    response = supabase.table('project_sal_grid_tasks')\
        .delete()\
        .eq('task_id', task_id)\
        .execute()
    print('✅ 삭제 완료:', task_id)
    return response.data

# 사용 예시
if __name__ == '__main__':
    # 새 Task 추가
    create_task({
        'task_id': 'S4F99',
        'task_name': '긴급 버그 수정',
        'stage': 4,
        'area': 'F',
        'priority': 'Critical',
        'status': 'Pending',
        'progress': 0
    })

    # Task 조회
    task = get_task('S4F99')
    print('Task:', task)

    # Task 업데이트
    update_task('S4F99', {
        'progress': 50,
        'status': 'In Progress'
    })
```

---

### 20-6. 자동 Task 처리 스크립트

**개념:**
1. Pending Task 찾기
2. 작업 시작 표시
3. 실제 작업 수행
4. 완료 기록

**JavaScript 예시:**

```javascript
const supabase = require('./supabase-client')

async function processNextTask() {
  console.log('🔍 대기 중인 Task 검색...')

  // 1. Pending Task 찾기
  const { data: tasks } = await supabase
    .from('project_sal_grid_tasks')
    .select('*')
    .eq('status', 'Pending')
    .order('stage', { ascending: true })
    .limit(1)

  if (!tasks || tasks.length === 0) {
    console.log('✅ 처리할 Task 없음')
    return
  }

  const task = tasks[0]
  console.log(`📋 Task 시작: ${task.task_id} - ${task.task_name}`)

  // 2. 작업 시작 표시
  await supabase
    .from('project_sal_grid_tasks')
    .update({
      status: 'In Progress',
      start_date: new Date().toISOString(),
      progress: 0
    })
    .eq('task_id', task.task_id)

  // 3. 실제 작업 수행 (여기서는 시뮬레이션)
  console.log('💻 작업 수행 중...')

  // Task Instruction 파일 읽기 (실제 구현 필요)
  // const instruction = await readTaskInstruction(task.task_id)
  // await executeTask(instruction)

  // 시뮬레이션 (2초 대기)
  await new Promise(resolve => setTimeout(resolve, 2000))

  // 4. 작업 완료 기록
  await supabase
    .from('project_sal_grid_tasks')
    .update({
      status: 'Completed',
      progress: 100,
      completion_date: new Date().toISOString(),
      generated_files: 'example.ts, test.spec.ts',
      notes: '자동 완료'
    })
    .eq('task_id', task.task_id)

  console.log('✅ 작업 완료!')

  // 5. 다음 Task 처리 (재귀)
  await processNextTask()
}

// 실행
processNextTask()
```

---

## 21. API 직접 활용

> 🌐 **대상**: REST API를 사용하고 싶은 개발자

### 21-1. Supabase REST API

Supabase는 자동으로 REST API를 생성합니다.

**기본 URL:**
```
https://[your-project].supabase.co/rest/v1/project_sal_grid_tasks
```

**필수 헤더:**
```
apikey: YOUR_ANON_KEY
Authorization: Bearer YOUR_ANON_KEY
```

---

### 21-2. API 예시 (curl)

**1. 모든 Task 조회:**
```bash
curl "https://abcdefghijk.supabase.co/rest/v1/project_sal_grid_tasks" \
  -H "apikey: eyJhbGci..." \
  -H "Authorization: Bearer eyJhbGci..."
```

**2. 특정 Task 조회:**
```bash
curl "https://abcdefghijk.supabase.co/rest/v1/project_sal_grid_tasks?task_id=eq.S1M1" \
  -H "apikey: YOUR_KEY" \
  -H "Authorization: Bearer YOUR_KEY"
```

**3. Task 생성:**
```bash
curl -X POST "https://abcdefghijk.supabase.co/rest/v1/project_sal_grid_tasks" \
  -H "apikey: YOUR_KEY" \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "S4F99",
    "task_name": "긴급 버그 수정",
    "stage": 4,
    "area": "F",
    "priority": "Critical"
  }'
```

**4. Task 업데이트:**
```bash
curl -X PATCH "https://abcdefghijk.supabase.co/rest/v1/project_sal_grid_tasks?task_id=eq.S4F99" \
  -H "apikey: YOUR_KEY" \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "progress": 50,
    "status": "In Progress"
  }'
```

**5. Task 삭제:**
```bash
curl -X DELETE "https://abcdefghijk.supabase.co/rest/v1/project_sal_grid_tasks?task_id=eq.S4F99" \
  -H "apikey: YOUR_KEY" \
  -H "Authorization: Bearer YOUR_KEY"
```

---

### 21-3. 고급 쿼리

**필터링:**
```bash
# Stage 4, Area F (개발 2차)
curl "https://[project].supabase.co/rest/v1/project_sal_grid_tasks?stage=eq.4&area=eq.F"

# 진행률 50% 이상
curl "https://[project].supabase.co/rest/v1/project_sal_grid_tasks?progress=gte.50"

# Status가 Pending 또는 In Progress
curl "https://[project].supabase.co/rest/v1/project_sal_grid_tasks?status=in.(Pending,In%20Progress)"
```

**정렬:**
```bash
# Stage 오름차순
curl "https://[project].supabase.co/rest/v1/project_sal_grid_tasks?order=stage.asc"

# 진행률 내림차순
curl "https://[project].supabase.co/rest/v1/project_sal_grid_tasks?order=progress.desc"
```

**제한:**
```bash
# 처음 10개만
curl "https://[project].supabase.co/rest/v1/project_sal_grid_tasks?limit=10"

# 5개 건너뛰고 10개
curl "https://[project].supabase.co/rest/v1/project_sal_grid_tasks?offset=5&limit=10"
```

---

## 마무리

**축하합니다!** 🎉

이제 여러분은:
- ✅ Supabase 프로젝트를 생성할 수 있습니다
- ✅ 표준 Grid를 설치할 수 있습니다
- ✅ SQL로 Task를 관리할 수 있습니다
- ✅ Viewer로 Grid를 시각화할 수 있습니다
- ✅ Claude Code로 자동화할 수 있습니다
- ✅ REST API를 활용할 수 있습니다

**PROJECT SAL GRID + Supabase = 완벽한 조합**

```
┌─────────────────────────────────┐
│   당신의 프로젝트 관리 시스템    │
│                                 │
│  Supabase (데이터)              │
│     +                           │
│  Grid Viewer (시각화)           │
│     +                           │
│  Claude Code (자동화)           │
│     =                           │
│  🚀 생산성 10배 향상            │
└─────────────────────────────────┘
```

---

# PART 6: 문제 해결 및 운영

## 22. 문제 해결 A to Z

> 🔧 **모든 문제의 해결 방법**

### 22-1. 일반적인 에러

다음은 자주 발생하는 에러들과 해결 방법입니다:

#### 에러 1: "relation already exists"

**화면에 표시:**
```
ERROR: relation "project_sal_grid_tasks" already exists
```

**의미:** 테이블이 이미 있습니다.

**해결 방법 A (테이블 삭제 후 재생성):**
```sql
-- ⚠️ 주의: 기존 데이터가 모두 삭제됩니다!

DROP TABLE IF EXISTS project_sal_grid_tasks CASCADE;

-- 그 다음 schema.sql 다시 실행
```

**해결 방법 B (데이터만 입력):**
- schema.sql 건너뛰기
- STANDARD_PROJECT_SAL_GRID_FINAL.sql만 실행

---

#### 에러 2: "duplicate key value"

**화면에 표시:**
```
ERROR: duplicate key value violates unique constraint "project_sal_grid_tasks_pkey"
DETAIL: Key (id)=(xxx) already exists.
```

**의미:** 같은 Task가 이미 있습니다.

**해결 방법 (데이터 초기화):**
```sql
-- 테이블 구조는 유지하고 데이터만 삭제
DELETE FROM project_sal_grid_tasks;

-- 그 다음 STANDARD_PROJECT_SAL_GRID_FINAL.sql 다시 실행
```

---

#### 에러 3: "column does not exist"

**화면에 표시:**
```
ERROR: column "task_id" does not exist
```

**의미:** 테이블이 제대로 생성되지 않았습니다.

**해결:**
1. 테이블 삭제:
```sql
DROP TABLE IF EXISTS project_sal_grid_tasks CASCADE;
```

2. schema.sql 전체를 다시 복사해서 실행
3. 파일 전체가 제대로 복사되었는지 확인

---

#### 에러 4: SQL 실행이 멈춤

**증상:**
- "Run" 버튼 클릭 후 10분 이상 응답 없음
- 로딩 아이콘만 계속 돌아감

**해결:**
1. 브라우저 새로고침 (F5)
2. SQL Editor 다시 열기
3. 다시 붙여넣기 및 실행

**여전히 안 되면:**
- 다른 브라우저 사용 (Chrome → Firefox)
- Supabase 상태 확인: https://status.supabase.com
- 인터넷 연결 확인

---

#### 에러 5: 한글이 깨짐

**증상:**
```
task_name: "íë¡ì í¸ ê¸°íì"
```

**원인:** 파일 인코딩 문제

**해결:**

**메모장 사용 시:**
1. SQL 파일을 메모장으로 열기
2. 파일 → 다른 이름으로 저장
3. 인코딩: "UTF-8" 선택
4. 저장 후 다시 복사 → 붙여넣기

**VS Code 사용 시:**
1. 우측 하단 인코딩 표시 클릭
2. "Save with Encoding" 선택
3. "UTF-8" 선택
4. 저장 후 다시 복사 → 붙여넣기

---

#### 에러 6: "permission denied"

**화면에 표시:**
```
ERROR: permission denied for table project_sal_grid_tasks
```

**원인:** RLS (보안 정책) 문제

**해결:**
```sql
-- RLS 일시 비활성화 (개발용)
ALTER TABLE project_sal_grid_tasks DISABLE ROW LEVEL SECURITY;

-- 데이터 입력 후 다시 활성화
ALTER TABLE project_sal_grid_tasks ENABLE ROW LEVEL SECURITY;
```

---

### 22-2. Viewer 관련 에러

#### 문제 1: 데이터가 안 보임

**체크리스트:**
1. F12 → Console 탭 → 에러 메시지 확인
2. Network 탭 → supabase.co 요청 확인
3. URL과 Key가 정확한지 확인
4. Table Editor에서 데이터 존재 여부 확인

**해결:**
```javascript
// viewer.html 수정
const SUPABASE_URL = 'https://correct-url.supabase.co'  // 끝에 / 없음
const SUPABASE_ANON_KEY = 'eyJ...'  // 전체 키
```

---

#### 문제 2: "Failed to fetch"

**원인:**
- 네트워크 문제
- Supabase 서버 다운
- URL 오타

**해결:**
1. https://status.supabase.com 확인
2. URL 다시 복사
3. 인터넷 연결 확인
4. 브라우저 캐시 삭제

---

#### 문제 3: "CORS error"

**에러 메시지:**
```
Access to fetch at 'https://...' has been blocked by CORS policy
```

**해결:**
- Supabase는 기본적으로 CORS 허용
- 브라우저 캐시 삭제 후 재시도
- HTTP 서버 사용 (파일을 직접 열지 말고)
- 파일을 직접 열지 말고 서버로 실행

---

#### 문제 4: "Invalid API key"

**해결:**
1. Supabase Dashboard → Settings → API
2. Anon Key 다시 복사
3. viewer.html 수정 및 저장
4. 브라우저 새로고침 (Ctrl+F5)

---

### 22-3. 데이터베이스 문제

#### 문제: Task 개수가 예상과 다름

**확인:**
```sql
SELECT COUNT(*) FROM project_sal_grid_tasks;
```

**원인별 해결:**

**50개 정도만 있음:**
- SQL 파일이 일부만 복사됨
- 해결: 파일 전체 복사 확인 후 재실행

**중복 에러로 일부 실패:**
```sql
-- 데이터 삭제 후 재실행
DELETE FROM project_sal_grid_tasks;
-- STANDARD_PROJECT_SAL_GRID_FINAL.sql 다시 실행
```

**0개:**
- INSERT 실행 안 됨
- 해결: STANDARD_PROJECT_SAL_GRID_FINAL.sql 실행

---

### 22-4. 디버깅 팁

#### 1. 브라우저 개발자 도구 활용

```
F12 → Console 탭
- 빨간 에러 메시지 확인
- "supabase" 키워드 검색

F12 → Network 탭
- supabase.co 요청 확인
- Response 탭에서 응답 내용 확인
- 401 에러: API Key 문제
- 404 에러: URL 또는 테이블 이름 문제
```

---

#### 2. SQL 직접 실행

```sql
-- 테이블 존재 확인
SELECT table_name
FROM information_schema.tables
WHERE table_name = 'project_sal_grid_tasks';

-- 컬럼 목록 확인
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'project_sal_grid_tasks';

-- 데이터 샘플
SELECT * FROM project_sal_grid_tasks LIMIT 5;

-- 통계
SELECT
  COUNT(*) as total,
  COUNT(DISTINCT stage) as stages,
  COUNT(DISTINCT area) as areas
FROM project_sal_grid_tasks;
```

---

#### 3. 로그 확인

```javascript
// JavaScript에서
console.log('Supabase URL:', process.env.SUPABASE_URL)
console.log('Key length:', process.env.SUPABASE_KEY.length)

const { data, error } = await supabase...
console.log('Data:', data)
console.log('Error:', error)
```

---

### 22-5. 완전 초기화 (마지막 수단)

**모든 것을 처음부터:**

```sql
-- 1. 테이블 완전 삭제
DROP TABLE IF EXISTS project_sal_grid_tasks CASCADE;

-- 2. schema.sql 전체 실행
-- (새로 복사해서 붙여넣기)

-- 3. STANDARD_PROJECT_SAL_GRID_FINAL.sql 실행
-- (새로 복사해서 붙여넣기)

-- 4. 확인
SELECT COUNT(*) FROM project_sal_grid_tasks;
-- 결과: 93
```

---

### 22-6. 도움이 필요하면

**순서대로 시도해보세요:**

1. **브라우저 콘솔 확인**
   - F12 → Console 탭
   - 빨간 에러 메시지 복사
   - 구글 검색: "supabase [에러 메시지]"

2. **SQL 직접 확인**
   ```sql
   -- 테이블 존재 여부
   SELECT table_name
   FROM information_schema.tables
   WHERE table_name = 'project_sal_grid_tasks';

   -- 데이터 개수
   SELECT COUNT(*) FROM project_sal_grid_tasks;

   -- 샘플 데이터
   SELECT * FROM project_sal_grid_tasks LIMIT 5;
   ```

3. **처음부터 다시 시작**
   ```sql
   -- 완전히 삭제
   DROP TABLE IF EXISTS project_sal_grid_tasks CASCADE;

   -- schema.sql 실행
   -- STANDARD_PROJECT_SAL_GRID_FINAL.sql 실행
   ```

4. **Supabase 공식 문서**
   - https://supabase.com/docs
   - 검색: "sql error [에러 메시지]"

---

## 23. 보안 및 백업

> 🔒 **중요**: 데이터 안전하게 지키기

### 23-1. 보안 체크리스트

#### 필수 (꼭 해야 함)

- ✅ `.env` 파일을 `.gitignore`에 추가
  ```bash
  # .gitignore
  .env
  .env.local
  .env.*.local
  ```

- ✅ `service_role` 키는 절대 공개 금지
  - GitHub에 올리지 말 것
  - 클라이언트 코드에 넣지 말 것

- ✅ `anon public` 키만 클라이언트에서 사용
  - 브라우저, HTML Viewer에 사용 가능
  - 공개되어도 RLS로 보호됨

#### 권장 (하면 좋음)

- ✅ Supabase 계정에 2FA 활성화
  - Settings → Account → Two-Factor Authentication

- ✅ API Key 주기적 재발급 (6개월마다)
  - Settings → API → "Regenerate" 버튼

- ✅ 데이터베이스 백업 (주 1회)
  - 아래 백업 방법 참고

---

### 23-2. RLS (Row Level Security) 설정

#### 개발 중 (현재 설정)

```sql
-- 모든 사람이 접근 가능 (개발/테스트용)
CREATE POLICY "Allow public read access"
    ON project_sal_grid_tasks
    FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Allow public write access"
    ON project_sal_grid_tasks
    FOR ALL
    TO public
    USING (true)
    WITH CHECK (true);
```

#### 프로덕션 (실제 서비스)

```sql
-- 기존 정책 삭제
DROP POLICY IF EXISTS "Allow public read access" ON project_sal_grid_tasks;
DROP POLICY IF EXISTS "Allow public write access" ON project_sal_grid_tasks;

-- 인증된 사용자만 접근
CREATE POLICY "Authenticated users only"
    ON project_sal_grid_tasks
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
```

---

### 23-3. 백업 방법

#### 방법 1: SQL Editor에서 수동 백업

```sql
-- 1. 모든 데이터 조회
SELECT * FROM project_sal_grid_tasks;

-- 2. Results → "Export to CSV" 버튼 클릭
-- 3. 파일 저장: backup_2025-11-25.csv
```

---

#### 방법 2: Supabase CLI (개발자용)

```bash
# Supabase CLI 설치 (한 번만)
npm install -g supabase

# 프로젝트 연결
supabase link --project-ref [your-project-id]

# 백업 실행
supabase db dump -f backup.sql

# 파일 저장됨: backup.sql
```

---

#### 방법 3: 자동 백업 스크립트 (JavaScript)

```javascript
const supabase = require('./supabase-client')
const fs = require('fs')

async function backup() {
  const { data, error } = await supabase
    .from('project_sal_grid_tasks')
    .select('*')

  if (error) {
    console.error('백업 실패:', error)
    return
  }

  const filename = `backup_${new Date().toISOString().split('T')[0]}.json`
  fs.writeFileSync(filename, JSON.stringify(data, null, 2))
  console.log(`✅ 백업 완료: ${filename}`)
}

backup()
```

**권장 백업 주기:**
- 개발 중: 주 1회
- 프로덕션: 매일 자동

---

### 23-4. 복원 방법

#### CSV에서 복원

1. Table Editor → project_sal_grid_tasks 테이블 클릭
2. "Insert" → "Import from CSV"
3. backup.csv 파일 선택
4. 컬럼 매핑 확인
5. "Import" 버튼 클릭

---

#### SQL에서 복원

```bash
# Supabase CLI 사용
supabase db push --file backup.sql
```

---

#### JSON에서 복원 (JavaScript)

```javascript
const supabase = require('./supabase-client')
const fs = require('fs')

async function restore(filename) {
  const data = JSON.parse(fs.readFileSync(filename, 'utf8'))

  const { error } = await supabase
    .from('project_sal_grid_tasks')
    .insert(data)

  if (error) {
    console.error('복원 실패:', error)
  } else {
    console.log(`✅ 복원 완료: ${data.length}개 Task`)
  }
}

restore('backup_2025-11-25.json')
```

---

### 23-5. 성능 최적화

#### 인덱스 추가 (이미 schema.sql에 포함됨)

```sql
-- 자주 검색하는 컬럼에 인덱스
CREATE INDEX IF NOT EXISTS idx_stage ON project_sal_grid_tasks(stage);
CREATE INDEX IF NOT EXISTS idx_area ON project_sal_grid_tasks(area);
CREATE INDEX IF NOT EXISTS idx_status ON project_sal_grid_tasks(status);
CREATE INDEX IF NOT EXISTS idx_priority ON project_sal_grid_tasks(priority);
```

---

#### 쿼리 최적화

```javascript
// ❌ 나쁜 예: 모든 데이터 가져온 후 JavaScript로 필터링
const { data } = await supabase
  .from('project_sal_grid_tasks')
  .select('*')

const pending = data.filter(t => t.status === 'Pending')

// ✅ 좋은 예: DB에서 바로 필터링
const { data } = await supabase
  .from('project_sal_grid_tasks')
  .select('*')
  .eq('status', 'Pending')
```

---

## 24. 추가 리소스

### 24-1. 공식 문서

#### Supabase

- 공식 홈: https://supabase.com
- 문서: https://supabase.com/docs
- JavaScript SDK: https://supabase.com/docs/reference/javascript
- Python SDK: https://github.com/supabase-community/supabase-py
- REST API: https://supabase.com/docs/guides/api
- SQL Tutorial: https://supabase.com/docs/guides/database

#### PROJECT SAL GRID

- 생성 가이드: `PROJECT_SAL_GRID_생성_가이드_V2.0.md`
- 22 속성: `PROJECT_GRID_22_ATTRIBUTES_FINAL.md`
- 5×11 매트릭스: `5x11_MATRIX.md`
- 디렉토리 구조: `PROJECT_DIRECTORY_STRUCTURE.md`
- 템플릿 README: `template/README.md`

---

### 24-2. 전체 체크리스트

#### 설치 완료 체크

```
☑ Supabase 프로젝트 생성
☑ API Key 저장
☑ schema.sql 실행 (테이블 생성)
☑ STANDARD_PROJECT_SAL_GRID_FINAL.sql 실행
☑ SELECT COUNT(*) 확인 (93)
☑ Stage별 개수 확인
☑ Viewer 설정 완료
☑ Viewer에서 Grid 확인
```

#### 학습 완료 체크

```
☑ Supabase가 무엇인지 이해
☑ CRUD 개념 이해
☑ SQL Editor 사용법 숙지
☑ Task 추가/수정/삭제 가능
☑ Viewer 사용 가능
☑ 문제 해결 방법 숙지
```

#### 개발자 체크 (선택)

```
☑ 라이브러리 설치 완료
☑ 환경 변수 설정
☑ Supabase 클라이언트 생성
☑ CRUD 함수 작성
☑ 자동화 스크립트 작성
☑ API 사용법 숙지
```

---

### 24-3. 자주 묻는 질문 (FAQ)

#### Q1: Supabase 무료 플랜 한도는?

A:
- 500MB 데이터베이스
- 1GB 파일 저장소
- 월 2GB 전송량
- 월 50,000 인증 사용자
- (우리 프로젝트는 충분함)

---

#### Q2: 여러 프로젝트를 하나의 Supabase에?

A:
- 가능하지만 비추천
- 프로젝트마다 별도 Supabase 프로젝트 생성 권장
- 또는 테이블 이름에 프로젝트 구분 (예: project1_tasks, project2_tasks)

---

#### Q3: 팀원과 공유하려면?

A:
- Settings → Team → Invite member
- 또는 API Key만 공유 (읽기 전용)
- RLS 정책으로 권한 제어 가능

---

#### Q4: 데이터 백업은 어떻게?

A:
- 무료 플랜: 수동 백업 필요 (23-3. 백업 방법 참고)
- Pro 플랜: 자동 백업 (Point-in-Time Recovery)

---

#### Q5: SQL 몰라도 괜찮나요?

A:
- 네! 이 가이드의 예시를 복사해서 사용하세요
- 값만 바꾸면 됩니다
- SQL 기본만 알면 충분 (SELECT, INSERT, UPDATE, DELETE)

---

#### Q6: Claude Code가 자동으로 하나요?

A:
- 네, CRUD 함수를 제공하면 자동으로 Task 처리 가능
- 자동화 관련 내용은 Supabase 통합 가이드 참고

---

# PART 7: 정리 및 부록

## 25. 정리 및 요약

### 25-1. 핵심 요약

**Supabase = 클라우드 데이터베이스**
- 엑셀처럼 사용 가능
- 웹에서 관리
- 무료로 시작
- API 자동 생성

**PROJECT SAL GRID → Supabase 흐름:**
```
1. 표준 Grid 정의
   ↓
2. Supabase에 저장 (클라우드)
   ↓
3. 어디서나 접근 가능
   ↓
4. HTML Viewer로 시각화
   ↓
5. Claude Code가 자동 관리
```

---

### 25-2. 초보자가 기억할 3가지

#### 1. 설치는 5분
- Supabase 프로젝트 생성 (2분)
- schema.sql 실행 (1분)
- 데이터 SQL 실행 (2분)

#### 2. 관리는 SQL Editor
- 복사 → 붙여넣기 → Run
- 값만 바꾸면 됨
- 예시 많이 제공됨

#### 3. 시각화는 Viewer
- 브라우저에서 바로 보기
- 필터링, 정렬 가능
- 실시간 업데이트

---

### 25-3. 개발자가 기억할 3가지

#### 1. 자동화 가능
- @supabase/supabase-js 사용
- CRUD 함수 작성
- Claude Code 통합

#### 2. API 사용 간편
- REST API 자동 생성
- curl, axios, fetch 모두 가능
- 인증은 API Key만

#### 3. 확장성 좋음
- Real-time 지원
- RLS로 보안 제어
- Serverless Functions 연동 가능

---

### 25-4. 다음 단계

#### 1. 실전 프로젝트에 적용
- 새 Supabase 프로젝트 생성
- 프로젝트 전용 Grid 설계
- Task Instruction 작성
- Claude Code 자동화

#### 2. 심화 학습
- RLS 정책 상세 설정
- Supabase Functions 활용
- Real-time Subscriptions
- Storage 연동 (파일 저장)

#### 3. 팀 협업
- 팀원 초대
- 권한 관리
- Viewer 공유
- 진행 상황 모니터링

---

## 26. 마무리

**축하합니다!** 🎉

이제 여러분은:
- ✅ Supabase 프로젝트를 생성할 수 있습니다
- ✅ 표준 Grid를 설치할 수 있습니다
- ✅ SQL로 Task를 관리할 수 있습니다
- ✅ Viewer로 Grid를 시각화할 수 있습니다
- ✅ 문제를 스스로 해결할 수 있습니다

**PROJECT SAL GRID + Supabase = 완벽한 조합**

```
┌─────────────────────────────────┐
│   당신의 프로젝트 관리 시스템    │
│                                 │
│  Supabase (데이터)              │
│     +                           │
│  Grid Viewer (시각화)           │
│     +                           │
│  Claude Code (자동화)           │
│     =                           │
│  🚀 생산성 10배 향상            │
└─────────────────────────────────┘
```

---

## 27. 버전 이력

### PROJECT SAL GRID 생성 가이드 버전 이력

- **V2.0 (2025-11-23)**: 섹션 5를 22개 속성 최종 정의로 교체
  - **섹션 5 완전 교체**:
    - 기존 간단한 속성 정의 삭제
    - PROJECT_GRID_22_ATTRIBUTES_FINAL.md의 상세 내용으로 대체
    - 22개 속성을 5개 그룹으로 재구성
    - Task 작업 플로우, 검증 로직, 핵심 원칙 포함
    - P → S 변경 완료 (Task ID 통일)

- **V1.3 (2025-11-23)**: 용어 통일 및 표준 디렉토리 구조 추가
  - **용어 통일**:
    - Order Sheet → Task Instruction (Inbox/Outbox 외 모든 곳)
    - Verification Sheet → Verification Instruction (전체)
    - 속성 #20 이름 변경: verification_sheet → verification_instruction
  - **표준 디렉토리 구조 추가** (신규 섹션 12):
    - 6개 Stage 폴더 (P1_사업계획 ~ 5_개발_마무리)
    - claude/ 폴더
    - web_claude-code_bridge/ (Inbox/Outbox)
    - S0_Project-SAL-Grid_생성/ (매뉴얼, DB, 뷰어, sal-grid)
    - 파일 명명 규칙
    - 폴더별 역할 상세 설명

- **V1.2 (2025-11-23)**: 대규모 구조 개선
  - **Task Instruction (작업 지시서)**: order_sheet → task_instruction 명칭 변경
  - **22개 속성 영어/한글 병기**: 모든 속성에 영문명 추가
  - **Inbox/Outbox JSON System 추가** (섹션 10)
  - **섹션 재배치**: Git 시스템 → 섹션 11로 이동

- **V1.1 (2025-11-23)**: 주요 개선
  - **Task ID 통일**: P → S 변경
  - **Verification Sheet 간소화**: verification_agent 1번 검증
  - **Git 통합 추적 시스템 추가**

- **V1.0 (2025-11-23)**: 초기 버전
  - 5×11 매트릭스 반영
  - Task 선정 2대 원칙
  - 22개 속성 체계
  - 3단계 검증 시스템
  - Stage Gate 시스템

---

### PROJECT SAL GRID MANUAL 버전 이력

- **v4.0 (2025-12-27)**: 일반화 버전 (템플릿)
  - 브랜드 고유 참조 제거 → 일반화
  - DB Method (Supabase) + CSV Method (JSON) 두 가지 방식 모두 지원
  - 외부 사용자가 자신의 프로젝트에 적용할 수 있는 템플릿 형태로 변경
  - CLAUDE.md에서 참조용 문서로 활용

- **v3.8 (2025-12-23)**: S4F6 Task 확장
  - S4F6 Task 이름 변경: "인앱 알림 UI" -> "My Page 기능 (알림/문의)"
  - My Page 문의 관리 페이지 추가
  - S4F1 modification_history 업데이트 (크레딧 관리 섹션 개선)
  - TASK_PLAN.md v3.5 반영

- **v3.7 (2025-12-22)**: 인앱 알림 시스템 Task 추가
  - S4D2 (user_notifications 테이블) Task 추가
  - S4F6 (인앱 알림 UI) Task 추가
  - TASK_PLAN.md v4.3 반영 (55 → 57 tasks)

- **v3.6 (2025-12-22)**: S5M1 Task 삭제
  - S5M1 (운영 매뉴얼) Task 삭제 - 비현실적 Task
  - S5O1 Task명 변경: "프로덕션 배포" → "배포상황 최종 검증"
  - TASK_PLAN.md v4.3 반영 (56 → 55 tasks)


- **v3.5 (2025-12-20)**: Task 확장 반영
  - S4F5 (프로젝트 등록 API 연동) Task 추가 반영
  - S5U1 (디자인 QA 및 일관성 점검) Task 추가 반영
  - S5T1 (프로덕션 완성도 점검) Task 추가 반영
  - TASK_PLAN.md v4.2 반영 (53 → 55 tasks)

- **v3.4 (2025-12-19)**: .claude/rules/ 참조 추가
  - AI 필수 준수 규칙에 .claude/rules/ 참조 추가

- **v3.3 (2025-12-18)**: Task Plan 동기화
  - TASK_PLAN.md v3.3~v3.4 변경사항 반영
  - S2BI3 이메일 도메인 인증 Task 추가

- **v3.2 (2025-12-12)**: 유연성 확보 및 현행화
  - 섹션 5.1 Grid 생성 시점: P1-P3 + S1-S5 구조에 맞게 수정
  - 섹션 14: Task 개수 일반화 (66개/93개 → 프로젝트별 Task)
  - 구체적인 Task 개수는 TASK_PLAN.md 참조하도록 안내
  - 매뉴얼은 기준과 원칙 제시, Task 기획서에서 개수 관리

- **v3.1 (2025-12-12)**: 폴더 구조 정리 및 매뉴얼 현행화
  - `S0_Project-SAL-Grid_생성/sal-grid/` 폴더로 Task 기획 파일 통합
  - 섹션 4.2 전체 구조 업데이트 (P1-P3, S1-S5 표기 통일)
  - 섹션 4.7 S0_Project-SAL-Grid 폴더 구조 업데이트
  - task-instructions, verification-instructions 폴더 제거 (별도 관리)
  - TASK_PLAN.md (v3.0), 5x11_MATRIX.md (v3.0) 참조

- **v3.0 (2025-11-25)**: 생성 가이드와 Supabase 가이드를 통합한 완전 매뉴얼 제작
  - PART 1: 프로젝트 개요 및 핵심 개념
  - PART 2: Grid 생성 및 설정
  - PART 3: 개발 워크플로우
  - PART 4: Supabase 통합
  - PART 5: 실전 활용
  - PART 6: 문제 해결 및 운영
  - PART 7: 정리 및 부록
  - 총 7개 Part, 27개 섹션으로 구성
  - 초보자부터 개발자까지 모두 사용 가능한 완전한 매뉴얼

---

**본 매뉴얼은 PROJECT SAL GRID의 핵심 문서입니다.**
**PROJECT SAL GRID를 올바르게 생성하면 AI와 함께하는 체계적인 풀스택 웹 애플리케이션 개발이 가능합니다.** 🌾

---

**문서 끝**

> 🌾 **PROJECT SAL GRID - Your AI-Powered Project Management System**
>
> **작성**: 2025-11-25
> **버전**: v4.0
> **최종 수정**: 2025-12-27
> **문의**: PROJECT_SAL_GRID 관련 문서 참고

**Happy Coding!** 💻✨
