# ValueLink Project SAL Grid - Task Plan

## 프로젝트 개요

- **프로젝트명**: ValueLink 기업가치평가 플랫폼 재구축
- **총 Task 수**: 28개
- **적용 방법론**: SAL Grid (Stage-Area-Level)
- **버전**: v1.0
- **최종 수정일**: 2026-02-05

---

## Task 그룹핑 원칙 (파일 기반)

> **핵심 규칙**: 생성되는 파일이 같으면 Task를 쪼개지 않음, 동시 처리 가능한 작업은 1개 Task로 통합

### 그룹핑 기준
1. **같은 템플릿 공유 시** → 1개 Task (템플릿 + 모든 변형)
2. **Frontend + Backend API 동시 작업 가능 시** → 1개 Task
3. **공통 인터페이스를 가진 모듈** → 적절히 배치 (2-3개 Task)
4. **대용량 복잡 페이지** → 개별 Task

### 향후 추가 기능 (Phase 2)
- 🔜 AI Avatar IR
- 🔜 랭킹 시스템
- 🔜 투자 매칭 시스템 (investment_automation)

---

## Stage별 Task 수

| Stage | 영문명 | 한글명 | Task 수 | 설명 |
|-------|--------|--------|---------|------|
| **S1** | Development Setup | 개발 준비 | 4 | 환경설정, DB스키마, 문서화 |
| **S2** | Core Platform | 개발 1차 | 12 | 핵심 워크플로우, 페이지, API |
| **S3** | Valuation Engines | 개발 2차 | 4 | 5개 평가 엔진 통합 |
| **S4** | External Integration | 개발 3차 | 5 | 뉴스 크롤링, 외부 연동 |
| **S5** | Finalization | 개발 마무리 | 3 | 배포, QA, 문서화 |
| **합계** | | | **28** | |

---

## Area별 분포

| Area | 코드 | Frontend | Backend APIs | Backend Infra | External | Database | Testing | DevOps | Documentation | 합계 |
|------|------|----------|--------------|---------------|----------|----------|---------|--------|---------------|------|
| **S1** | 개발 준비 | - | - | 1 | - | 1 | - | - | 2 | 4 |
| **S2** | 개발 1차 | 7 | 4 | - | - | - | - | - | 1 | 12 |
| **S3** | 개발 2차 | - | 4 | - | - | - | - | - | - | 4 |
| **S4** | 개발 3차 | 1 | - | - | 4 | - | - | - | - | 5 |
| **S5** | 마무리 | - | - | - | - | - | 1 | 1 | 1 | 3 |
| **합계** | | 8 | 8 | 1 | 4 | 1 | 1 | 1 | 4 | **28** |

---

## S1: Development Setup (개발 준비)

### 목표
프로젝트 개발 환경 구축, 데이터베이스 스키마 정의, API 명세 작성

### Tasks (4개)

#### S1BI1: Database & Configuration Infrastructure
- **Task Name**: 데이터베이스 및 설정 인프라 구축
- **Area**: BI (Backend Infrastructure)
- **Dependencies**: 없음
- **생성 파일**:
  - `lib/supabase/client.ts` (브라우저용 Supabase 클라이언트)
  - `lib/supabase/server.ts` (서버용 Supabase 클라이언트)
  - `lib/config.ts` (환경 설정)
  - `.env.local.example` (환경 변수 템플릿)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

#### S1D1: Database Schema & RLS Policies
- **Task Name**: 데이터베이스 스키마 및 RLS 정책 정의
- **Area**: D (Database)
- **Dependencies**: 없음
- **생성 파일**:
  - `database/schema.sql` (12개 테이블 정의)
  - `database/rls-policies.sql` (Row Level Security 정책)
  - `database/triggers.sql` (updated_at 트리거)
- **Task Agent**: database-specialist
- **Verification Agent**: database-specialist
- **참조**: `Process/P3_프로토타입_제작/Database/complete-schema.sql`

#### S1M1: API Specification & Documentation
- **Task Name**: API 명세서 및 기술 문서 작성
- **Area**: M (Documentation)
- **Dependencies**: 없음
- **생성 파일**:
  - `docs/api-specification.md` (14단계 워크플로우 API)
  - `docs/valuation-engines-api.md` (5개 평가 엔진 API)
  - `docs/authentication.md` (인증 흐름)
- **Task Agent**: documentation-specialist
- **Verification Agent**: code-reviewer

#### S1M2: Development Workflow Guide
- **Task Name**: 개발 워크플로우 가이드 작성
- **Area**: M (Documentation)
- **Dependencies**: 없음
- **생성 파일**:
  - `docs/development-guide.md` (Git 전략, 브랜치 규칙)
  - `docs/coding-standards.md` (TypeScript/Python 코딩 표준)
- **Task Agent**: documentation-specialist
- **Verification Agent**: code-reviewer

---

## S2: Core Platform (개발 1차)

### 목표
핵심 워크플로우, 사용자 인터페이스, 백엔드 API 구현

### Frontend Tasks (7개)

#### S2F1: Valuation Results Template & 5 Method Pages
- **Task Name**: 평가 결과 페이지 템플릿 및 5개 방법별 페이지
- **Area**: F (Frontend)
- **Dependencies**: S1BI1, S1D1
- **생성 파일** (6개):
  - `components/valuation-results-template.tsx` (공통 템플릿)
  - `app/valuation/results/dcf/page.tsx`
  - `app/valuation/results/relative/page.tsx`
  - `app/valuation/results/asset/page.tsx`
  - `app/valuation/results/intrinsic/page.tsx`
  - `app/valuation/results/tax/page.tsx`
- **그룹핑 근거**: 5개 페이지가 동일한 레이아웃/구조를 공유, 데이터 필드만 차이
- **Task Agent**: frontend-developer
- **Verification Agent**: code-reviewer
- **참조**:
  - `frontend/app/valuation/results/dcf-valuation.html` (기존 목업)
  - `Process/P2_프로젝트_기획/Design_System/design-tokens.md`

#### S2F2: Valuation Submission Forms Template & 5 Method Pages
- **Task Name**: 평가 신청 폼 템플릿 및 5개 방법별 페이지
- **Area**: F (Frontend)
- **Dependencies**: S1BI1, S2F1
- **생성 파일** (6개):
  - `components/submission-form-template.tsx` (공통 폼 템플릿)
  - `app/valuation/submissions/dcf/page.tsx`
  - `app/valuation/submissions/relative/page.tsx`
  - `app/valuation/submissions/asset/page.tsx`
  - `app/valuation/submissions/intrinsic/page.tsx`
  - `app/valuation/submissions/tax/page.tsx`
- **그룹핑 근거**: 동일한 폼 구조, 방법별 입력 필드만 차이
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist
- **참조**: `frontend/app/valuation/submissions/dcf-submission.html`

#### S2F3: Educational Guide Template & 5 Method Pages
- **Task Name**: 평가 방법 가이드 템플릿 및 5개 가이드 페이지
- **Area**: F (Frontend)
- **Dependencies**: S1BI1
- **생성 파일** (6개):
  - `components/guide-template.tsx` (공통 가이드 템플릿)
  - `app/valuation/guides/dcf/page.tsx`
  - `app/valuation/guides/relative/page.tsx`
  - `app/valuation/guides/asset/page.tsx`
  - `app/valuation/guides/intrinsic/page.tsx`
  - `app/valuation/guides/tax/page.tsx`
- **그룹핑 근거**: 교육 콘텐츠 레이아웃 동일, 사이드바 네비게이션 공유
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist
- **참조**: `frontend/app/valuation/guides/guide-dcf.html`

#### S2F4: Role-Based My Page Template & 6 Role Variants
- **Task Name**: 역할별 마이페이지 템플릿 및 6개 역할 페이지
- **Area**: F (Frontend)
- **Dependencies**: S1BI1, S1D1
- **생성 파일** (7개):
  - `components/mypage-template.tsx` (기본 마이페이지 템플릿)
  - `app/mypage/company/page.tsx`
  - `app/mypage/accountant/page.tsx`
  - `app/mypage/investor/page.tsx`
  - `app/mypage/partner/page.tsx`
  - `app/mypage/supporter/page.tsx`
  - `app/mypage/admin/page.tsx` (관리자 - 복잡, 2188줄)
- **그룹핑 근거**: 핵심 프로필/대시보드 구조 동일, 역할별 섹션만 차이
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist
- **참조**: `frontend/app/core/mypage-admin.html`

#### S2F5: Process Step Template & 12 Workflow Pages
- **Task Name**: 프로세스 단계 템플릿 및 12개 워크플로우 페이지
- **Area**: F (Frontend)
- **Dependencies**: S1BI1, S2BA1
- **생성 파일** (13개):
  - `components/process-step-template.tsx` (진행 상태 템플릿)
  - `app/valuation/evaluation-progress/page.tsx`
  - `app/valuation/data-collection/page.tsx`
  - `app/valuation/accountant-review/page.tsx`
  - `app/valuation/draft-generation/page.tsx`
  - `app/valuation/report-draft/page.tsx`
  - `app/valuation/revision-request/page.tsx`
  - `app/valuation/final-preparation/page.tsx`
  - `app/valuation/report-final/page.tsx`
  - `app/valuation/payment/page.tsx`
  - `app/valuation/deposit-payment/page.tsx` (무통장 입금)
  - `app/valuation/balance-payment/page.tsx` (잔금 입금)
  - `app/valuation/report-download/page.tsx`
- **그룹핑 근거**: 14단계 워크플로우의 진행 상태 표시 패턴 동일
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist
- **참조**: `frontend/app/valuation/evaluation-progress.html`

#### S2F6: Project Management Pages
- **Task Name**: 프로젝트 관리 페이지 (목록, 상세, 생성)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1, S2BA1
- **생성 파일** (3개):
  - `app/projects/list/page.tsx` (프로젝트 목록)
  - `app/projects/[id]/page.tsx` (프로젝트 상세)
  - `app/projects/create/page.tsx` (프로젝트 생성)
- **그룹핑 근거**: 프로젝트 CRUD 기능, 동시 작업 가능
- **주의**: 기존 `core/project-list.html`과 `projects/valuation-list.html` 중복 → 통합
- **Task Agent**: frontend-developer
- **Verification Agent**: code-reviewer
- **참조**: `frontend/app/core/project-detail.html`

#### S2F7: Authentication & Landing Pages
- **Task Name**: 인증 페이지 및 랜딩 페이지
- **Area**: F (Frontend)
- **Dependencies**: S1BI1, S2S1
- **생성 파일** (5개):
  - `app/(auth)/login/page.tsx`
  - `app/(auth)/register/page.tsx` (1079줄)
  - `app/page.tsx` (홈/랜딩 페이지)
  - `app/service-guide/page.tsx` (서비스 안내)
  - `components/header.tsx`, `components/sidebar.tsx` (공통 컴포넌트)
- **그룹핑 근거**: 인증 흐름 연결, 공통 컴포넌트 인프라 포함
- **Task Agent**: frontend-developer
- **Verification Agent**: security-auditor
- **참조**: `frontend/app/login.html`, `frontend/app/register.html`

### Backend Tasks (4개)

#### S2BA1: Valuation Process API & 14-Step Workflow
- **Task Name**: 평가 프로세스 API 및 14단계 워크플로우
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1, S1D1
- **생성 파일** (3개):
  - `app/api/valuation/route.ts` (14단계 엔드포인트)
  - `lib/workflow/workflow-manager.ts` (워크플로우 관리)
  - `lib/workflow/approval-points.ts` (22개 승인 포인트)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**: `backend/app/api/v1/endpoints/valuation.py` (기존 FastAPI)

#### S2BA2: Projects & Quotes API
- **Task Name**: 프로젝트 및 견적 API
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1, S1D1
- **생성 파일** (3개):
  - `app/api/projects/route.ts` (프로젝트 CRUD)
  - `app/api/quotes/route.ts` (견적 생성/수정)
  - `app/api/negotiations/route.ts` (협상 처리)
- **그룹핑 근거**: 프로젝트 생성부터 견적/협상까지 하나의 흐름
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

#### S2BA3: Documents & Reports API
- **Task Name**: 문서 및 보고서 API
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1, S1D1
- **생성 파일** (4개):
  - `app/api/documents/route.ts` (파일 업로드, Supabase Storage 연동)
  - `app/api/drafts/route.ts` (초안 생성/버전 관리)
  - `app/api/revisions/route.ts` (수정 요청)
  - `app/api/reports/route.ts` (최종 보고서 PDF 생성)
- **그룹핑 근거**: 문서 워크플로우 (업로드 → 초안 → 수정 → 최종)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

#### S2BA4: AI Client & Email Services
- **Task Name**: AI 클라이언트 및 이메일 서비스
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1
- **생성 파일** (3개):
  - `lib/ai/client.ts` (Claude/Gemini/GPT-4 통합)
  - `lib/email/sender.ts` (이메일 발송, Resend 연동)
  - `lib/notifications/service.ts` (알림 디스패치)
- **그룹핑 근거**: 외부 서비스 연동 유틸리티, 동시 작업 가능
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**: `backend/app/services/ai_client.py`

### Documentation Tasks (1개)

#### S2M1: User Manual & FAQ
- **Task Name**: 사용자 매뉴얼 및 FAQ
- **Area**: M (Documentation)
- **Dependencies**: S2F1~S2F7 (모든 페이지 완료 후)
- **생성 파일**:
  - `docs/user-manual.md` (사용자 가이드)
  - `docs/faq.md` (자주 묻는 질문)
- **Task Agent**: documentation-specialist
- **Verification Agent**: qa-specialist

---

## S3: Valuation Engines (개발 2차)

### 목표
5개 평가 엔진 통합 (DCF, Relative, Asset, Intrinsic, Tax)

### Tasks (4개)

#### S3BA1: Valuation Engine Orchestrator
- **Task Name**: 평가 엔진 오케스트레이터
- **Area**: BA (Backend APIs)
- **Dependencies**: S2BA1
- **생성 파일** (2개):
  - `lib/valuation/orchestrator.ts` (엔진 관리, 실행 순서 제어)
  - `lib/valuation/engine-interface.ts` (공통 인터페이스)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**: `backend/app/services/valuation_orchestrator.py`

#### S3BA2: Financial Math Library
- **Task Name**: 금융 수학 라이브러리
- **Area**: BA (Backend APIs)
- **Dependencies**: 없음
- **생성 파일** (1개):
  - `lib/valuation/financial-math.ts` (WACC, NPV, IRR, 할인율 계산)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**: `backend/app/services/valuation_engine/common/financial_math.py`

#### S3BA3: DCF Engine & Sensitivity Analysis
- **Task Name**: DCF 평가 엔진 및 민감도 분석
- **Area**: BA (Backend APIs)
- **Dependencies**: S3BA1, S3BA2
- **생성 파일** (2개):
  - `lib/valuation/engines/dcf-engine.ts` (504줄 Python → TypeScript 포팅)
  - `lib/valuation/engines/sensitivity-analysis.ts` (민감도 분석)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**:
  - `backend/app/services/valuation_engine/dcf/dcf_engine.py`
  - `Process/P3_프로토타입_제작/Documentation/valuation-engines.md`

#### S3BA4: Other Valuation Engines (Relative, Asset, Intrinsic, Tax)
- **Task Name**: 기타 평가 엔진 (상대, 자산, 내재, 세법)
- **Area**: BA (Backend APIs)
- **Dependencies**: S3BA1, S3BA2
- **생성 파일** (4개):
  - `lib/valuation/engines/relative-engine.ts` (487줄)
  - `lib/valuation/engines/asset-engine.ts` (497줄)
  - `lib/valuation/engines/intrinsic-engine.ts` (258줄)
  - `lib/valuation/engines/tax-engine.ts` (379줄)
- **그룹핑 근거**: 4개 엔진이 동일한 인터페이스를 공유, 계산 로직만 차이
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**: `backend/app/services/valuation_engine/` (4개 폴더)

---

## S4: External Integration (개발 3차)

### 목표
뉴스 크롤링, 외부 서비스 연동

### Frontend Tasks (1개)

#### S4F1: Deal News Tracker & Investment Monitor
- **Task Name**: Deal 뉴스 트래커 및 투자 모니터
- **Area**: F (Frontend)
- **Dependencies**: S1BI1, S4E2
- **생성 파일** (2개):
  - `app/deal/page.tsx` (Deal 뉴스 페이지, 2497줄 복잡도)
  - `app/link/page.tsx` (네트워크/연결 페이지, 959줄)
- **그룹핑 근거**: 투자 생태계 관련 기능, 뉴스 데이터 시각화
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist
- **참조**: `frontend/app/deal.html`, `frontend/app/link.html`

### External Integration Tasks (4개)

#### S4E1: News Crawler Infrastructure
- **Task Name**: 뉴스 크롤러 인프라
- **Area**: E (External)
- **Dependencies**: S1BI1
- **생성 파일** (2개):
  - `lib/crawler/base-crawler.ts` (추상 베이스 클래스)
  - `lib/crawler/crawler-manager.ts` (크롤러 관리, 스케줄링)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**:
  - `backend/app/services/news_crawler/base_crawler.py`
  - `backend/app/services/news_crawler/crawler_manager.py`

#### S4E2: News Parser & Data Extraction
- **Task Name**: 뉴스 파서 및 데이터 추출
- **Area**: E (External)
- **Dependencies**: S4E1
- **생성 파일** (1개):
  - `lib/crawler/news-parser.ts` (HTML 파싱, 데이터 추출, Deal 정보 추출)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**: `backend/app/services/news_parser.py`

#### S4E3: Site-Specific Crawlers (6 Implementations)
- **Task Name**: 사이트별 크롤러 구현 (6개)
- **Area**: E (External)
- **Dependencies**: S4E1, S4E2
- **생성 파일** (6개):
  - `lib/crawler/sites/naver-crawler.ts`
  - `lib/crawler/sites/outstanding-crawler.ts`
  - `lib/crawler/sites/platum-crawler.ts`
  - `lib/crawler/sites/startuptoday-crawler.ts`
  - `lib/crawler/sites/venturesquare-crawler.ts`
  - `lib/crawler/sites/wowtale-crawler.ts`
- **그룹핑 근거**: 6개 크롤러가 동일한 베이스 클래스 상속, 사이트별 파싱 로직만 차이
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**: `backend/app/services/news_crawler/` (6개 파일)

#### S4E4: Third-Party Integration (Enkino AI Verification)
- **Task Name**: 외부 서비스 연동 (Enkino AI 검증)
- **Area**: E (External)
- **Dependencies**: S2BA1
- **생성 파일** (1개):
  - `lib/integrations/enkino-verification.ts` (Enkino AI 검증 서비스 연동)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer
- **참조**: `backend/app/services/verify_enkinoai.py`

### DevOps Tasks (1개)

#### S4O1: Background Task Scheduler
- **Task Name**: 백그라운드 작업 스케줄러
- **Area**: O (DevOps)
- **Dependencies**: S4E1, S4E2
- **생성 파일** (2개):
  - `lib/scheduler/task-scheduler.ts` (스케줄러 인프라)
  - `lib/scheduler/tasks/weekly-collection.ts` (주간 데이터 수집)
- **Task Agent**: devops-troubleshooter
- **Verification Agent**: code-reviewer
- **참조**:
  - `backend/app/core/scheduler.py`
  - `backend/app/tasks/weekly_collection.py`

---

## S5: Finalization (개발 마무리)

### 목표
배포, 품질 보증, 최종 문서화

### Tasks (3개)

#### S5O1: Deployment Configuration & CI/CD
- **Task Name**: 배포 설정 및 CI/CD 파이프라인
- **Area**: O (DevOps)
- **Dependencies**: 모든 S2-S4 Task 완료
- **생성 파일** (5개):
  - `vercel.json` (Vercel 배포 설정)
  - `.github/workflows/ci.yml` (CI 파이프라인)
  - `.github/workflows/cd.yml` (CD 파이프라인)
  - `scripts/deploy.sh` (배포 스크립트)
  - `docs/deployment-guide.md` (배포 가이드)
- **Task Agent**: devops-troubleshooter
- **Verification Agent**: code-reviewer

#### S5T1: Testing & QA
- **Task Name**: 통합 테스트 및 품질 보증
- **Area**: T (Testing)
- **Dependencies**: 모든 S2-S4 Task 완료
- **생성 파일** (3개):
  - `tests/integration/valuation-workflow.test.ts` (14단계 워크플로우 테스트)
  - `tests/e2e/user-journey.test.ts` (E2E 테스트, Playwright)
  - `docs/test-report.md` (테스트 리포트)
- **Task Agent**: test-engineer
- **Verification Agent**: qa-specialist

#### S5M1: Final Documentation & Handbook
- **Task Name**: 최종 문서화 및 핸드북
- **Area**: M (Documentation)
- **Dependencies**: 모든 S2-S4 Task 완료
- **생성 파일** (4개):
  - `README.md` (프로젝트 개요, 설치 가이드)
  - `docs/architecture.md` (아키텍처 문서)
  - `docs/maintenance-guide.md` (유지보수 가이드)
  - `docs/troubleshooting.md` (문제 해결 가이드)
- **Task Agent**: documentation-specialist
- **Verification Agent**: code-reviewer

---

## Task 의존성 관계

### S1 (개발 준비)
```
S1BI1, S1D1, S1M1, S1M2 (병렬 실행 가능, 의존성 없음)
```

### S2 (개발 1차)
```
S1BI1, S1D1 완료 후:
  → S2F1, S2F2, S2F3 (병렬 가능)
  → S2F4, S2F6 (병렬 가능)
  → S2BA1, S2BA2, S2BA3 (병렬 가능)
  → S2BA4 (병렬 가능)

S2BA1 완료 후:
  → S2F5 (14단계 워크플로우 페이지)

모든 S2F 완료 후:
  → S2M1 (사용자 매뉴얼)
```

### S3 (개발 2차)
```
S2BA1 완료 후:
  → S3BA1, S3BA2 (병렬 가능)

S3BA1, S3BA2 완료 후:
  → S3BA3, S3BA4 (병렬 가능)
```

### S4 (개발 3차)
```
S1BI1 완료 후:
  → S4E1

S4E1 완료 후:
  → S4E2

S4E1, S4E2 완료 후:
  → S4E3 (6개 크롤러)
  → S4O1 (스케줄러)

S4E2 완료 후:
  → S4F1 (Deal 페이지)

S2BA1 완료 후:
  → S4E4 (Enkino 연동)
```

### S5 (마무리)
```
모든 S2-S4 완료 후:
  → S5O1, S5T1, S5M1 (병렬 가능)
```

---

## 파일 생성 통계

### Frontend (8 Tasks, 59개 파일)
- S2F1: 6개 (템플릿 + 5개 결과 페이지)
- S2F2: 6개 (템플릿 + 5개 신청 폼)
- S2F3: 6개 (템플릿 + 5개 가이드)
- S2F4: 7개 (템플릿 + 6개 역할 페이지)
- S2F5: 13개 (템플릿 + 12개 프로세스 단계)
- S2F6: 3개 (프로젝트 관리)
- S2F7: 5개 (인증 + 랜딩)
- S4F1: 2개 (Deal + Link)
- **공통 컴포넌트**: 11개 (Header, Sidebar, Footer, Button, Card, Form, Table, Modal, Alert, Badge, Spinner)

### Backend APIs (8 Tasks, 23개 파일)
- S2BA1: 3개 (워크플로우 API)
- S2BA2: 3개 (프로젝트/견적 API)
- S2BA3: 4개 (문서/보고서 API)
- S2BA4: 3개 (AI/이메일 서비스)
- S3BA1: 2개 (오케스트레이터)
- S3BA2: 1개 (수학 라이브러리)
- S3BA3: 2개 (DCF 엔진)
- S3BA4: 4개 (4개 엔진)

### External Integration (4 Tasks, 10개 파일)
- S4E1: 2개 (크롤러 인프라)
- S4E2: 1개 (파서)
- S4E3: 6개 (6개 사이트 크롤러)
- S4E4: 1개 (Enkino 연동)

### Infrastructure & Docs (8 Tasks, 26개 파일)
- S1BI1: 4개 (DB/설정)
- S1D1: 3개 (스키마/RLS/트리거)
- S1M1: 3개 (API 문서)
- S1M2: 2개 (개발 가이드)
- S2M1: 2개 (사용자 매뉴얼)
- S4O1: 2개 (스케줄러)
- S5O1: 5개 (배포 설정)
- S5T1: 3개 (테스트)
- S5M1: 4개 (최종 문서)

**총 파일 수: 약 118개**

---

## 예상 리소스

### 개발 인력
- Frontend Developer: S2F1~S2F7, S4F1 (8 tasks)
- Backend Developer: S2BA1~S2BA4, S3BA1~S3BA4, S4E1~S4E4 (12 tasks)
- Database Specialist: S1D1 (1 task)
- DevOps Engineer: S4O1, S5O1 (2 tasks)
- Test Engineer: S5T1 (1 task)
- Documentation Specialist: S1M1, S1M2, S2M1, S5M1 (4 tasks)

### 외부 서비스
- Supabase Cloud (Database, Auth, Storage)
- Vercel (Frontend Hosting, Edge Functions)
- Resend (Email Service)
- Claude API (AI Integration)
- Gemini API (AI Integration)
- GPT-4 API (AI Integration)

### 예상 비용 (3개월 기준)
- Supabase: $25/month = 75만원
- Vercel Pro: $20/month = 60만원
- Domain: $12/year = 1만원
- AI API (Claude/Gemini/GPT): 월 30만원 = 90만원
- Email (Resend): $20/month = 60만원
- **총계**: 286만원 (3개월)

---

## 주요 기술 스택 확정

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.x
- **UI Components**: Radix UI + shadcn/ui
- **State**: Zustand (전역), React Query (서버 상태)
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts (평가 결과 시각화)

### Backend
- **Runtime**: Node.js 20 (Vercel Edge Functions)
- **Database**: PostgreSQL (Supabase)
- **ORM**: Prisma (TypeScript)
- **Auth**: Supabase Auth (OAuth + Email)
- **Storage**: Supabase Storage (파일 업로드)
- **AI**:
  - Claude Sonnet 3.5 (60%)
  - Gemini Pro 1.5 (20%)
  - GPT-4 (20%)

### DevOps
- **Hosting**: Vercel
- **CI/CD**: GitHub Actions
- **Monitoring**: Vercel Analytics + Sentry
- **Logging**: Vercel Logs + Supabase Logs

---

## 중요 참고사항

### 1. 기존 Python 코드 활용
- **5개 평가 엔진** (2,125줄): TypeScript로 포팅 (S3BA3, S3BA4)
- **계산 로직 검증**: 기존 Python 결과와 비교 테스트 필수
- **API 명세**: `backend/app/api/v1/endpoints/valuation.py` 참조

### 2. Phase 2 추가 예정 기능
- 🔜 AI Avatar IR (프로덕션 1차 이후 추가)
- 🔜 랭킹 시스템 (프로덕션 1차 이후 추가)
- 🔜 투자 매칭 시스템 (프로덕션 1차 이후 추가)

### 3. 결제 방식
- **프로덕션 1차**: 무통장 입금 (계좌번호 표시 → 입금 확인 → 세금계산서 발행)
- 온라인 결제 연동은 고려하지 않음

### 4. 파일 기반 그룹핑 원칙
- **같은 템플릿 → 1 Task**: 5개 결과 페이지, 5개 신청 폼 등
- **Frontend + Backend 동시 작업 가능 → 1 Task**: 없음 (의존성 분리)
- **대용량 복잡 페이지 → 개별 Task**: `deal.html` (2497줄), `mypage-admin.html` (2188줄)

### 5. 기존 목업 활용
- **72개 HTML 페이지**: UI/UX 디자인 참조
- **Supabase 통합 코드**: `assets/js/supabase.js` 재사용 가능
- **공통 컴포넌트**: Header, Sidebar, Footer 추출

### 6. 데이터베이스 스키마 (12개 테이블)
1. `users` (프로필, 역할)
2. `projects` (프로젝트 마스터)
3. `quotes` (견적)
4. `negotiations` (협상)
5. `documents` (파일 업로드)
6. `approval_points` (22개 승인 포인트)
7. `valuation_results` (5개 방법 결과)
8. `drafts` (초안, Markdown)
9. `revisions` (수정 요청)
10. `reports` (최종 보고서 PDF)
11. `investment_tracker` (Deal 뉴스)
12. `feedbacks` (평가)

---

## 변경 이력

### v1.0 (2026-02-05)
- 초안 작성
- 파일 기반 그룹핑 원칙 적용
- 총 28개 Task 정의
- 프로덕션 1차 출시 범위 확정 (AI Avatar, 랭킹, 매칭은 Phase 2에서 추가)
- 결제 방식: 무통장 입금 (온라인 결제 연동 제외)
- Stage별 Task 분배 완료

---

## 다음 단계

1. **Task Instruction 작성**: 28개 Task별 상세 지침 (`task-instructions/{TaskID}_instruction.md`)
2. **Verification Instruction 작성**: 28개 Task별 검증 지침 (`verification-instructions/{TaskID}_verification.md`)
3. **JSON 구조 설정**: `index.json` + `grid_records/` (28개 파일)
4. **Viewer 테스트**: `viewer/viewer_json.html` 확인
5. **S1 Task 시작**: 개발 준비 4개 Task 실행

---

**문서 작성자**: Claude Code (Sonnet 4.5)
**프로젝트 소유자**: ValueLink
**버전**: v1.0
**최종 수정**: 2026-02-05
