# ValueLink 프로젝트 백서 및 업무 인수인계서

**작성일**: 2026-02-09
**작성자**: Claude Opus 4.6 (Main Agent)
**프로젝트**: ValueLink - 기업가치 평가 플랫폼
**현재 상태**: S2 완료 (PO 승인) → S3 대기

---

## 1. 프로젝트 개요

### 1.1 프로젝트 목적
ValueLink는 5가지 기업가치 평가 방법(DCF, 상대가치, 본질가치, 자산가치, 상증세법)을 제공하는 SaaS 플랫폼입니다. AI가 평가 프로세스의 22개 핵심 판단 포인트(JP001-JP022)를 지원하며, 회계사가 최종 검토/승인하는 Human-AI 협업 구조입니다.

### 1.2 기술 스택
| 구분 | 기술 |
|------|------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | Next.js API Routes (Route Handlers) |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth (Google OAuth, Email) |
| AI | OpenAI GPT-4o, Google Gemini, Anthropic Claude |
| Email | Resend API |
| 배포 | Vercel (예정) |
| VCS | Git + GitHub |

### 1.3 개발 방법론
- **SAL Grid**: 28개 Task를 5 Stage x 11 Area로 관리
- **6단계 실행 프로세스**: Task 실행 → PO 도움 → 검증 → Stage Gate → PO 테스트 → PO 승인
- **상태 전이**: Pending → In Progress → Executed → (Verified) → Completed

---

## 2. Stage별 완료 현황

### 2.1 전체 진행률

| Stage | 명칭 | Task 수 | 완료 | 진행률 | PO 승인 |
|-------|------|:-------:|:----:|:------:|:-------:|
| S1 | 개발 준비 | 4 | 4 | 100% | Approved |
| S2 | 개발 1차 (Core Platform) | 12 | 12 | 100% | **Approved (2026-02-09)** |
| S3 | 개발 2차 (AI Integration) | 4 | 0 | 0% | - |
| S4 | 개발 3차 (Payment & Admin) | 6 | 0 | 0% | - |
| S5 | 개발 마무리 | 3 | 0 | 0% | - |
| **합계** | | **29** | **16** | **55%** | |

### 2.2 S1 완료 Task (4/4)

| Task ID | Task Name | Area | 산출물 |
|---------|-----------|------|--------|
| S1BI1 | DB 및 설정 인프라 구축 | BI | Supabase 클라이언트, 환경변수 설정 |
| S1D1 | DB 스키마 및 RLS 정책 | D | schema-v4-final.sql (41개 테이블) |
| S1M1 | API 명세서 및 기술 문서 | M | API 명세서 1,797줄 |
| S1M2 | 개발 워크플로우 가이드 | M | 코딩 표준/워크플로우 1,282줄 |

### 2.3 S2 완료 Task (12/12)

| Task ID | Task Name | Area | 산출물 (파일 수) |
|---------|-----------|------|-----------------|
| S2BA1 | 평가 엔진 API (5개 방법별) | BA | 3파일 (route.ts, workflow-manager.ts, approval-points.ts) |
| S2BA2 | 프로젝트/평가 요청 API | BA | 3파일 (projects, evaluation-requests, project-history) |
| S2BA3 | 문서/초안/수정/보고서 API | BA | 4파일 (documents, drafts, revisions, reports) |
| S2BA4 | AI 클라이언트/이메일/알림 | BA | 3파일 (ai/client.ts, email/sender.ts, notifications/service.ts) |
| S2F1 | 평가 결과 페이지 (5개 방법별) | F | 6파일 (template + 5 pages) |
| S2F2 | 평가 신청 폼 (5개 방법별) | F | 7파일 (template + 5 pages + types) |
| S2F3 | 평가 방법 가이드 (5개) | F | 6파일 (template + 5 pages) |
| S2F4 | 역할별 마이페이지 | F | 7파일 (template + 6 role pages) |
| S2F5 | 프로세스 단계 (12 steps) | F | 13파일 (template + 12 step pages) |
| S2F6 | 프로젝트 관리 (목록/상세/생성) | F | 3파일 |
| S2F7 | 인증/랜딩/헤더/사이드바 | F | 6파일 (login, register, landing, header, sidebar, service-guide) |
| S2M1 | 사용자 매뉴얼/FAQ | M | 2파일 (user-manual.md, faq.md) |

**S2 총 산출물: 66파일** (Backend 14, Frontend 50, Documentation 2)

### 2.4 미완료 Stage (S3~S5)

#### S3 - AI Integration (4 Tasks)
| Task ID | Task Name | Area |
|---------|-----------|------|
| S3BA1 | AI 평가 엔진 연동 | BA |
| S3BA2 | AI 문서 분석 서비스 | BA |
| S3BA3 | AI 보고서 생성 서비스 | BA |
| S3BA4 | AI Q&A 챗봇 서비스 | BA |

#### S4 - Payment & Admin (6 Tasks)
| Task ID | Task Name | Area |
|---------|-----------|------|
| S4F1 | 관리자 대시보드 | F |
| S4E1 | 결제 연동 (Stripe/토스) | E |
| S4E2 | 알림 서비스 (이메일/푸시) | E |
| S4E3 | 파일 스토리지 연동 | E |
| S4E4 | 외부 데이터 연동 (DART/KIND) | E |
| S4O1 | CI/CD 파이프라인 | O |

#### S5 - 개발 마무리 (3 Tasks)
| Task ID | Task Name | Area |
|---------|-----------|------|
| S5O1 | 배포 및 모니터링 | O |
| S5T1 | 통합 테스트 및 QA | T |
| S5M1 | 최종 문서화 | M |

---

## 3. 데이터베이스 현황

### 3.1 Supabase 프로젝트
- **URL**: https://arxrfetgaitkgiiqabap.supabase.co
- **Project Ref**: arxrfetgaitkgiiqabap
- **Management API Token**: [REDACTED - Supabase Dashboard에서 확인]

### 3.2 테이블 현황 (56개)

#### 데이터 있는 테이블 (주요)
| 테이블 | 행 수 | 설명 |
|--------|:-----:|------|
| investment_news_articles | 1,003 | 투자 뉴스 기사 (스크래퍼 수집) |
| deals | 140 | 투자 딜 (기사에서 추출) |
| investment_news | 78 | 일별 뉴스 수집 기록 |
| valuation_results | 25 | 평가 결과 (5방법 x 5건) |
| investment_news_network_sources | 13 | 뉴스 소스 사이트 목록 |
| projects | 10 | 프로젝트 (5개 모의 + 5개 기존) |
| investment_news_ranking | 10 | 뉴스 랭킹 |
| weekly_collections | 8 | 주간 수집 기록 |
| startup_companies | 5 | 스타트업 기업 정보 |
| valuation_reports | 3 | 샘플 평가 보고서 |
| newsletter_subscribers | 3 | 뉴스레터 구독자 |

#### v4 평가법별 테이블 (30개 = 6종류 x 5방법)
| 종류 | DCF | Relative | Intrinsic | Asset | Tax |
|------|:---:|:--------:|:---------:|:-----:|:---:|
| Documents | 3 | 2 | 2 | 2 | 2 |
| Drafts | 1 | 1 | 1 | 1 | 1 |
| Results | 1 | 1 | 1 | 1 | 1 |
| Approval Points | 8 | 4 | 2 | 6 | 2 |
| Revisions | 0 | 0 | 0 | 0 | 0 |
| Reports | 0 | 0 | 0 | 0 | 0 |

### 3.3 스키마 파일
- **위치**: `database/schema-v4-final.sql`
- **테이블 수**: 41개 정의 (기존 11 + 평가법별 30)
- **주의**: 복원 후 일부 v4 신규 테이블(evaluation_requests, project_history 등)은 아직 미생성

### 3.4 DB 사고 이력
| 날짜 | 사고 | 원인 | 복구 |
|------|------|------|------|
| 2026-02-08 | deals 테이블 140행 삭제 | v4 스키마 배포 시 DROP TABLE 실행 (사용자 승인 없이) | 2026-02-09 Supabase 백업(Feb 8) 복원 |

**재발 방지**: 절대 규칙 6 추가 (파괴적 작업 사전 승인 필수)

---

## 4. 환경 설정

### 4.1 API 키 (.env.local)
| 키 | 용도 | 상태 |
|----|------|------|
| NEXT_PUBLIC_SUPABASE_URL | Supabase 접속 | 설정됨 |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | Supabase 인증 | 설정됨 |
| OPENAI_API_KEY | GPT-4o AI 기능 | 설정됨 (동작 확인) |
| GOOGLE_AI_API_KEY | Gemini AI 기능 | 설정됨 (무료 할당량 소진) |
| ANTHROPIC_API_KEY | Claude AI 기능 | 설정됨 |
| RESEND_API_KEY | 이메일 발송 | 설정됨 (미테스트) |
| ADMIN_REGISTRATION_CODE | 관리자 가입 코드 | ADMIN2026 |

### 4.2 Gemini API 할당량 이슈
- 무료 티어: 일 20회 (gemini-2.5-flash), 전 모델 할당량 소진 상태
- 뉴스 스크래퍼(daily_auto_collect.py)가 Gemini 사용
- **해결 방안**: 유료 전환 또는 OpenAI로 대체

### 4.3 주요 스크립트
| 스크립트 | 위치 | 용도 |
|---------|------|------|
| sync-to-root.js | scripts/ | Stage→Root 자동 복사 (Pre-commit Hook) |
| build-progress.js | Process_Monitor/ | 진행률 계산 |
| upload-progress.js | scripts/ | 진행률 DB 업로드 |
| daily_auto_collect.py | Valuation_Company/scripts/investment-news-scraper/ | 투자 뉴스 자동 수집 |

---

## 5. 프로젝트 구조

### 5.1 디렉토리 구조 (핵심)
```
C:\ValueLink\
├── app/                          ← Next.js App Router (배포용, 자동복사)
│   ├── api/                      ← Backend API Routes
│   ├── (auth)/                   ← 인증 페이지
│   ├── mypage/                   ← 마이페이지
│   ├── projects/                 ← 프로젝트 관리
│   └── valuation/                ← 평가 (guides, process, submissions)
├── components/                   ← 재사용 컴포넌트
├── lib/                          ← 유틸리티 (AI, Email, Workflow)
├── types/                        ← TypeScript 타입 정의
├── database/                     ← DB 스키마
│   └── schema-v4-final.sql
├── Process/                      ← SAL Grid 프로세스 관리 (원본)
│   ├── S0_Project-SAL-Grid_생성/ ← Grid 데이터, Viewer
│   ├── S1_개발_준비/              ← S1 산출물
│   └── S2_개발-1차/              ← S2 산출물 (66파일)
├── Valuation_Company/            ← 부수 기능
│   └── scripts/investment-news-scraper/  ← 뉴스 스크래퍼
├── .claude/                      ← AI 규칙/로그
│   ├── CLAUDE.md                 ← 7대 규칙 + 6대 절대 규칙
│   ├── rules/                    ← 상세 규칙 8개
│   └── work_logs/current.md      ← 작업 로그
├── .env.local                    ← 환경변수
└── .git/hooks/pre-commit         ← Git Hook (동기화+진행률)
```

### 5.2 저장 규칙
- **원본**: `Process/S{N}_*/Area/` (Stage 폴더)
- **배포본**: 루트 `app/`, `lib/`, `components/`, `types/` (자동 복사)
- **Pre-commit Hook**: `scripts/sync-to-root.js`가 Stage→Root 자동 복사
- **규칙 위반 금지**: 루트에 직접 저장 X, 반드시 Stage 먼저

---

## 6. 절대 규칙 (6대)

| # | 규칙 | 핵심 |
|---|------|------|
| 1 | 폴더 임의 생성 금지 | 사용자 승인 후에만 생성 |
| 2 | 일반 작업 검증/문서화 필수 | 서브에이전트 검증 + work_logs + Reports |
| 3 | SAL Grid Task 프로세스 | 6단계 + 상태 전이 순서 준수 |
| 4 | Stage 먼저 저장 | Pre-commit Hook 자동 복사 |
| 5 | Task 완료 시 Grid 업데이트 | JSON 파일 반드시 업데이트 |
| 6 | **파괴적 작업 사전 승인** | DROP TABLE, DELETE 등 반드시 사용자 승인 |

---

## 7. 알려진 이슈 및 주의사항

### 7.1 스키마 정합성 주의
- Sub-agent가 API 코드 생성 시 **잘못된 컬럼명** 사용하는 경우 빈번
- 반드시 `database/schema-v4-final.sql` 기준으로 검증 필요
- 주요 매핑:
  - `users.name` (NOT full_name)
  - `users.company_name` (NOT company_name_kr)
  - `users.user_id` (NOT id/owner_id)
  - `projects.project_id` = VARCHAR(50), 형식: VL-YYYYMMDD-XXXX
  - `drafts`: 9개 개별 섹션 컬럼 (NOT JSONB)

### 7.2 DB 복원 후 미완료 사항
- `evaluation_requests`, `project_history`, `balance_payments`, `report_delivery_requests` 테이블 미생성
- `users` 테이블: auth.users FK 없이 생성됨 (실제 사용자 등록 시 FK 추가 필요)
- 기존 `projects` 테이블 스키마가 v4와 다름 (customer_id vs user_id)

### 7.3 투자 뉴스 스크래퍼
- Gemini API 무료 할당량 소진 → 스크래퍼 동작 불가
- GitHub Actions (daily-news-scraper.yml)로 매일 8시 자동 실행 설정됨
- GitHub Secrets에 별도 GEMINI_API_KEY 설정 필요

### 7.4 S2BA4 (Human-AI Task)
- 코드는 완성이나 **실제 작동 테스트 미완**
- OpenAI, Gemini, Anthropic, Resend 4개 API 키 설정 필요
- PO가 직접 테스트 후 완료 처리 필요

---

## 8. S3 시작 가이드

### 8.1 S3 작업 목록
| Task ID | Task Name | Dependencies |
|---------|-----------|-------------|
| S3BA1 | AI 평가 엔진 연동 | S2BA1 |
| S3BA2 | AI 문서 분석 서비스 | S2BA3 |
| S3BA3 | AI 보고서 생성 서비스 | S2BA3 |
| S3BA4 | AI Q&A 챗봇 서비스 | S2BA4 |

### 8.2 S3 시작 전 확인사항
- [ ] S2 Stage Gate PO 승인 완료 (2026-02-09 완료)
- [ ] AI API 키 동작 확인 (OpenAI: 동작, Gemini: 할당량 소진, Anthropic: 미확인)
- [ ] `database/schema-v4-final.sql` 기준 테이블 완전성 확인
- [ ] `Process/S0_.../sal-grid/task-instructions/S3*.md` 파일 존재 확인

### 8.3 권장 실행 순서
1. S3BA1 (AI 평가 엔진) - 핵심 기능
2. S3BA2 (문서 분석) + S3BA3 (보고서 생성) - 병렬 실행 가능
3. S3BA4 (챗봇) - 마지막

---

## 9. 연락처 및 참고

### 9.1 주요 파일 위치
| 항목 | 경로 |
|------|------|
| 작업 로그 | `.claude/work_logs/current.md` |
| 보고서 | `Human_ClaudeCode_Bridge/Reports/` |
| 스키마 | `database/schema-v4-final.sql` |
| AI 규칙 | `.claude/CLAUDE.md` + `.claude/rules/` |
| Stage Gate | `Process/S0_.../sal-grid/stage-gates/` |
| Grid 데이터 | `Process/S0_.../method/json/data/grid_records/` |
| 환경변수 | `.env.local` |

### 9.2 Git 브랜치
- **master**: 메인 브랜치 (모든 작업)
- Pre-commit Hook 활성화: sync-to-root.js + build-progress.js + upload-progress.js

### 9.3 Supabase 관리
- Dashboard: https://supabase.com/dashboard/project/arxrfetgaitkgiiqabap
- 백업: 매일 자동 (Physical, WAL-G), PITR 미활성화
- 관리 API: `https://api.supabase.com/v1/projects/arxrfetgaitkgiiqabap/database/query`

---

*이 문서는 2026-02-09 기준으로 작성되었습니다.*
*다음 세션에서는 S3 (AI Integration) 작업을 시작하면 됩니다.*
