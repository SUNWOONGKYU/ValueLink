# ValueLink 프로젝트 일정 & 마일스톤

**작성일**: 2026-02-05
**버전**: 1.0
**프로젝트**: ValueLink - AI 기업가치평가 플랫폼 재구축

---

## 개요

본 문서는 ValueLink 플랫폼 **재구축 프로젝트**의 전체 일정과 마일스톤을 정의합니다.

### 프로젝트 기간

```
시작일: 2026-02-05
종료일: 2026-05-05 (3개월)
방법론: SAL Grid (P0-P3 → S0-S5)
```

### 핵심 전략

```
✅ 기존 85% 완성도 활용 (재작성 최소화)
✅ 역공학 방식 (코드 → 문서)
✅ 단계별 검증 (Stage Gate)
✅ 부트스트래핑 (최소 비용)
```

---

## 1. 전체 일정 개요

```
┌──────────────────────────────────────────────────────────────┐
│  Phase       │ 기간      │ 주요 작업                         │
├──────────────────────────────────────────────────────────────┤
│  P0-P3       │ 1주       │ 문서화 (P0 검증, P1-P3 문서 작성)  │
│  S0          │ 1주       │ SAL Grid 생성 (66 Tasks 정의)     │
│  S1          │ 1주       │ 개발 준비 (환경, DB, Auth)        │
│  S2          │ 3주       │ 인증 & 핵심 기능 (28페이지)       │
│  S3          │ 3주       │ 평가 워크플로우 (29페이지)        │
│  S4          │ 2주       │ 플랫폼 기능 (16페이지)            │
│  S5          │ 1주       │ 배포 & QA                         │
│              │           │                                   │
│  Total       │ 12주      │ 3개월 (여유 포함)                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Phase별 상세 일정

### P0: 디렉토리 구조 검증 (1일)

**날짜**: 2026-02-05

| 시간 | 작업 | 담당 | 산출물 |
|------|------|------|--------|
| 2H | Process/ 폴더 구조 확인 | Claude Code | 폴더 목록 |
| 2H | P0_Project_Status.md 작성 | Claude Code | 상태 문서 |
| 1H | P0_Project_Directory_Structure.md | Claude Code | 구조 문서 |

**완료 기준**:
- [x] 모든 필수 폴더 존재 확인
- [x] README 파일 존재 확인
- [x] Git 저장소 초기화

---

### P1: 사업계획 문서화 (2일)

**날짜**: 2026-02-06 ~ 02-07

**Day 1 (02-06)**:
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 2H | Vision_Mission/vision-statement.md | 비전 문서 |
| 2H | Business_Model/business-model-canvas.md | 비즈니스 모델 |
| 2H | Market_Analysis/market-size-analysis.md | 시장 분석 |

**Day 2 (02-07)**:
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 2H | Patent/ip-strategy.md | IP 전략 |
| 3H | BusinessPlan/executive-summary.md | 경영진 요약 |
| 3H | BusinessPlan/financial-projections.md | 재무 예측 |

**완료 기준**:
- [x] 5개 하위 폴더에 각 1개 이상 문서
- [x] 비즈니스 모델 명확히 정의
- [x] TAM/SAM/SOM 정량 제시
- [x] 3년 재무 예측 포함

---

### P2: 프로젝트 기획 (3일)

**날짜**: 2026-02-08 ~ 02-10

**Day 1 (02-08)**:
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 3H | Tech_Stack/architecture.md | 아키텍처 문서 |
| 3H | Tech_Stack/database-erd.md | ERD 문서 |
| 2H | User_Flows/customer-journey.md | 사용자 여정 |

**Day 2 (02-09)**:
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 4H | UI_UX_Mockup/page-inventory.md | 72페이지 목록 |
| 4H | Design_System/design-tokens.md | 디자인 시스템 |

**Day 3 (02-10)**:
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 3H | Requirements/functional-requirements.md | 기능 요구사항 |
| 2H | Project_Plan/timeline-milestones.md | 프로젝트 일정 |
| 3H | Workflows/development-workflow.md | 개발 워크플로우 |

**완료 기준**:
- [ ] 모든 기능 요구사항 문서화
- [ ] ERD에 9개 테이블 정의
- [ ] 72페이지 인벤토리 완료
- [ ] 기술 스택 확정

---

### P3: 프로토타입 정리 (2일)

**날짜**: 2026-02-11 ~ 02-12

**Day 1 (02-11)**:
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 3H | Frontend 인벤토리 생성 | Frontend/README.md |
| 3H | Database 스키마 통합 | Database/complete-schema.sql |
| 2H | 5개 평가 엔진 문서화 | Documentation/engines.md |

**Day 2 (02-12)**:
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 3H | API 명세 추출 | Documentation/api-spec.md |
| 3H | Prototype Overview 작성 | Documentation/prototype-overview.md |
| 2H | P3 검증 및 승인 | 검증 리포트 |

**완료 기준**:
- [ ] 72페이지 복사 완료
- [ ] 데이터베이스 스키마 문서화
- [ ] 5개 엔진 작동 원리 문서화
- [ ] API 엔드포인트 목록

---

### S0: SAL Grid 생성 (5일)

**날짜**: 2026-02-13 ~ 02-19 (1주)

**Day 1-2 (02-13 ~ 02-14): 코드베이스 분석**
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 8H | 126 Python 파일 분석 | 기능 목록 |
| 8H | 72 HTML 페이지 분석 | 화면 목록 |

**Day 3 (02-15): Task 정의**
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 4H | Task ID 부여 및 그룹핑 | TASK_PLAN.md (66 Tasks) |
| 4H | 의존성 정의 | 의존성 그래프 |

**Day 4-5 (02-16 ~ 02-19): Instruction 작성**
| 시간 | 작업 | 산출물 |
|------|------|--------|
| 16H | 66개 Task Instruction | task-instructions/ |
| 16H | 66개 Verification Instruction | verification-instructions/ |

**완료 기준**:
- [ ] TASK_PLAN.md에 66 Tasks 정의
- [ ] 모든 Task Instruction 작성
- [ ] 모든 Verification Instruction 작성
- [ ] JSON 구조 설정 (index.json + grid_records/)
- [ ] Viewer 테스트 통과

**예상 Task 수**: 66개

---

### S1: 개발 준비 (5일)

**날짜**: 2026-02-20 ~ 02-26 (1주)

**주요 작업**:
1. Next.js 프로젝트 초기화
2. Supabase 클라이언트 설정
3. Auth Provider 설정 (Google, Email)
4. Database Migration
5. Vercel 배포 설정
6. CI/CD 파이프라인

**예상 Task 수**: 13개

| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Backend Infra (BI) | 5 | Supabase Client, FastAPI 설정 |
| Database (D) | 3 | Migration, RLS 정책 |
| Security (S) | 2 | OAuth, JWT |
| DevOps (O) | 2 | Vercel, CI/CD |
| Documentation (M) | 1 | 환경 설정 가이드 |

**완료 기준**:
- [ ] Next.js 빌드 성공
- [ ] Supabase 연결 확인
- [ ] Auth 테스트 통과
- [ ] Vercel 배포 성공

---

### S2: 인증 & 핵심 기능 (15일)

**날짜**: 2026-02-27 ~ 03-13 (3주)

**Week 1 (02-27 ~ 03-05): 인증 시스템**
| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Frontend (F) | 6 | 로그인, 회원가입, 비밀번호 재설정 |
| Security (S) | 3 | Google OAuth, Email Auth, JWT |
| Backend APIs (BA) | 2 | Auth API, User Management |

**Week 2 (03-06 ~ 03-12): 프로젝트 관리**
| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Frontend (F) | 4 | 프로젝트 CRUD |
| Backend APIs (BA) | 3 | Project API |
| Database (D) | 1 | projects 테이블 RLS |

**Week 3 (03-13): 대시보드**
| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Frontend (F) | 3 | 고객, 회계사, 관리자 대시보드 |
| Backend APIs (BA) | 2 | Dashboard API |

**예상 Task 수**: 24개

**완료 기준**:
- [ ] 로그인/회원가입 작동
- [ ] 프로젝트 CRUD 작동
- [ ] 3개 대시보드 작동
- [ ] Stage Gate 검증 통과

---

### S3: 평가 워크플로우 (15일)

**날짜**: 2026-03-14 ~ 03-28 (3주)

**Week 1 (03-14 ~ 03-20): 14단계 워크플로우**
| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Frontend (F) | 14 | Step 01 ~ Step 14 |
| Backend APIs (BA) | 5 | Workflow API |
| Database (D) | 2 | quotes, negotiations, documents |

**Week 2 (03-21 ~ 03-27): 평가 엔진 통합**
| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Frontend (F) | 10 | 5개 가이드 + 5개 제출 |
| Backend Infra (BI) | 5 | 5개 엔진 FastAPI 래퍼 |
| External (E) | 3 | AI 연동 (Claude, Gemini, GPT-4) |

**Week 3 (03-28): 결과 화면**
| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Frontend (F) | 5 | 5개 결과 화면 |
| Backend APIs (BA) | 2 | Result API |
| Database (D) | 1 | valuation_results, reports |

**예상 Task 수**: 47개

**완료 기준**:
- [ ] 14단계 워크플로우 작동
- [ ] 5개 평가 엔진 통합
- [ ] 5개 결과 화면 작동
- [ ] 22개 승인 포인트 작동

---

### S4: 플랫폼 기능 (10일)

**날짜**: 2026-03-29 ~ 04-09 (2주)

**Week 1 (03-29 ~ 04-04): 관리자 & 결제**
| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Frontend (F) | 6 | Admin 6개 탭 |
| Backend APIs (BA) | 3 | Admin API |
| External (E) | 2 | Stripe 연동 |

**Week 2 (04-05 ~ 04-09): 확장 기능**
| Task 그룹 | Task 수 | 예시 |
|-----------|---------|------|
| Frontend (F) | 8 | Service 페이지, Investment Tracker |
| Backend APIs (BA) | 2 | Investment Tracker API |
| Content (C) | 2 | FAQ, Blog 콘텐츠 |

**예상 Task 수**: 23개

**완료 기준**:
- [ ] 관리자 패널 작동
- [ ] Stripe 결제 작동
- [ ] Investment Tracker 작동

---

### S5: 배포 & QA (5일)

**날짜**: 2026-04-10 ~ 04-16 (1주)

**Day 1-2 (04-10 ~ 04-11): E2E 테스트**
| 시간 | 작업 | 담당 |
|------|------|------|
| 8H | 전체 페이지 E2E 테스트 | Test Agent |
| 8H | API 통합 테스트 | Test Agent |

**Day 3 (04-12): 보안 감사**
| 시간 | 작업 | 담당 |
|------|------|------|
| 4H | 보안 취약점 검사 | Security Agent |
| 4H | RLS 정책 검증 | Security Agent |

**Day 4 (04-13): 성능 최적화**
| 시간 | 작업 | 담당 |
|------|------|------|
| 4H | Lighthouse 스코어 개선 | DevOps Agent |
| 4H | DB 쿼리 최적화 | Database Agent |

**Day 5 (04-14 ~ 04-16): Production 배포**
| 시간 | 작업 | 담당 |
|------|------|------|
| 4H | Vercel Production 배포 | DevOps Agent |
| 4H | 모니터링 설정 (Sentry, Vercel Analytics) | DevOps Agent |
| 4H | 최종 문서화 | Documentation Agent |

**예상 Task 수**: 10개

**완료 기준**:
- [ ] E2E 테스트 통과
- [ ] 보안 감사 통과
- [ ] Lighthouse 스코어 90+
- [ ] Production 배포 완료

---

## 3. 주요 마일스톤

```
┌──────────────────────────────────────────────────────────────┐
│  M0  │ 2026-02-12  │ P0-P3 완료 (문서화)                     │
│  M1  │ 2026-02-19  │ S0 완료 (SAL Grid 생성)                │
│  M2  │ 2026-02-26  │ S1 완료 (개발 환경 준비)               │
│  M3  │ 2026-03-13  │ S2 완료 (인증 & 핵심 기능)             │
│  M4  │ 2026-03-28  │ S3 완료 (평가 워크플로우)              │
│  M5  │ 2026-04-09  │ S4 완료 (플랫폼 기능)                  │
│  M6  │ 2026-04-16  │ S5 완료 (Production 배포)              │
│                                                              │
│  🚀 Launch  │ 2026-04-16  │ 공식 런칭                       │
└──────────────────────────────────────────────────────────────┘
```

### 마일스톤별 검증 기준

| 마일스톤 | 완료 기준 | 검증자 |
|---------|----------|--------|
| M0 | 모든 P1-P3 문서 작성 완료 | PO |
| M1 | 66개 Task 정의 + JSON 설정 | Main Agent |
| M2 | Next.js 빌드 + Supabase 연결 | Verification Agent |
| M3 | 인증 + 프로젝트 CRUD 작동 | PO |
| M4 | 14단계 + 5개 엔진 작동 | PO |
| M5 | 관리자 패널 + 결제 작동 | PO |
| M6 | E2E 테스트 + 보안 감사 통과 | PO |

---

## 4. 리소스 계획

### 4.1 인력 계획

| 역할 | 인원 | 투입 기간 | 비용 |
|------|------|----------|------|
| **대표 (Full-time)** | 1명 | 3개월 | 무급 (부트스트래핑) |
| **회계사 (Part-time)** | 2명 | S3-S5 (6주) | 주 40만원 × 2명 × 6주 = 480만원 |
| **개발자 (계획)** | - | - | - (1년차 추가 예정) |

**총 인건비**: 480만원 (회계사 파트타임만)

### 4.2 인프라 비용

| 항목 | 월 비용 | 3개월 비용 |
|------|---------|------------|
| **Vercel** | Pro $20 | $60 (7만원) |
| **Supabase** | Pro $25 | $75 (9만원) |
| **Claude API** | ~$50 | $150 (18만원) |
| **Gemini API** | ~$20 | $60 (7만원) |
| **GPT-4 API** | ~$30 | $90 (11만원) |
| **Resend (Email)** | Free → Pro $20 | $40 (5만원) |
| **Stripe** | 수수료만 | - |

**총 인프라 비용**: 약 57만원 (3개월)

### 4.3 총 프로젝트 비용

```
인건비: 480만원 (회계사)
인프라: 57만원
총 비용: 537만원

부트스트래핑 전략:
- 대표 무급 (자체 자금으로 생활비)
- 회계사 파트타임 (최소 인건비)
- 인프라 최소화 (Free Tier 최대 활용)
```

---

## 5. 리스크 관리

### 5.1 일정 리스크

| 리스크 | 확률 | 영향 | 대응 방안 |
|--------|------|------|----------|
| S3 평가 엔진 통합 지연 | 중 | 높음 | Python 엔진 그대로 사용 (포팅 대신 래핑) |
| S4 Stripe 연동 복잡도 | 중 | 중 | Stripe Checkout 사용 (간단한 방식) |
| S5 E2E 테스트 실패 | 낮음 | 중 | 단계별 검증으로 사전 방지 |
| 외부 API 장애 | 낮음 | 중 | Fallback 로직 구현 |

### 5.2 기술 리스크

| 리스크 | 확률 | 영향 | 대응 방안 |
|--------|------|------|----------|
| Next.js 14 호환성 이슈 | 낮음 | 중 | Next.js 공식 문서 참조 |
| Supabase RLS 복잡도 | 중 | 중 | RLS 패턴 템플릿 사용 |
| FastAPI 배포 어려움 | 중 | 높음 | Vercel Serverless Function |
| AI API 비용 초과 | 중 | 중 | 캐싱 + 요청 제한 |

### 5.3 완화 전략

```
1. 일정 버퍼: 각 Stage에 20% 여유 시간
2. 기술 검증: S1에서 모든 외부 서비스 연동 테스트
3. 단계별 검증: Stage Gate 통과 후 다음 단계 진행
4. 롤백 계획: 각 Stage마다 Git 브랜치 생성
5. 문서화: 모든 이슈를 work_logs에 기록
```

---

## 6. 성공 지표

### 6.1 개발 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **Task 완료율** | 100% (66/66) | SAL Grid JSON |
| **빌드 성공률** | 100% | CI/CD 로그 |
| **테스트 통과율** | 95%+ | E2E 테스트 결과 |
| **Lighthouse 스코어** | 90+ | Lighthouse 보고서 |
| **코드 재사용률** | 80%+ | 기존 엔진 보존 |

### 6.2 비즈니스 지표 (3개월 후)

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **첫 고객 확보** | 5개 기업 | CRM |
| **월 매출** | 4,000만원 | 결제 시스템 |
| **사용자 등록** | 50명 | Supabase 통계 |
| **페이지 방문** | 1,000회/월 | Vercel Analytics |

---

## 7. 변경 관리

### 7.1 범위 변경 프로세스

```
변경 요청
    ↓
영향 분석 (일정, 비용, 리소스)
    ↓
PO 승인 / 거부
    ↓
승인 시 → TASK_PLAN.md 업데이트 + JSON 수정
거부 시 → 이유 기록 + Backlog 추가
```

### 7.2 우선순위 변경 기준

**P0 (긴급)**: 시스템 장애, 보안 취약점
**P1 (높음)**: 핵심 기능 버그, 성능 이슈
**P2 (중간)**: 사용성 개선, UI 버그
**P3 (낮음)**: 문서화, 마이너 개선

---

## 8. 커뮤니케이션 계획

### 8.1 일일 보고

```
방식: .claude/work_logs/current.md 업데이트
시간: 매일 18:00
내용:
- 오늘 완료한 Task
- 내일 계획
- 블로커 (있는 경우)
```

### 8.2 주간 리뷰

```
방식: Stage Gate Verification Report
시간: 매주 금요일
내용:
- 주간 진행 현황
- 완료된 Task 목록
- 다음 주 계획
- 리스크 및 이슈
```

### 8.3 마일스톤 리뷰

```
방식: PO 승인 회의
시간: 각 마일스톤 완료 시
내용:
- 마일스톤 완료 기준 검증
- 테스트 가이드 제공
- 승인 / 거부 결정
```

---

## 9. 참조 문서

| 문서 | 경로 | 용도 |
|------|------|------|
| **재구축 계획** | `.claude/work_logs/ValueLink_재구축_계획.md` | 전체 계획 |
| **SAL Grid 매뉴얼** | `S0_Project-SAL-Grid_생성/manual/` | SAL Grid 방법론 |
| **TASK_PLAN** | `S0_Project-SAL-Grid_생성/sal-grid/TASK_PLAN.md` | 66개 Task 정의 |
| **작업 로그** | `.claude/work_logs/current.md` | 일일 진행 상황 |

---

## 10. 다음 단계

```
✅ P0 완료 (2026-02-05)
✅ P1 완료 (2026-02-06 ~ 02-07)
🔄 P2 진행 중 (2026-02-08 ~ 02-10) ← 현재
⏳ P3 예정 (2026-02-11 ~ 02-12)
⏳ S0 예정 (2026-02-13 ~ 02-19)
```

**현재 진행률**: P2 6/8 문서 완료 (75%)

---

## 요약

```
✅ 전체 일정: 12주 (3개월)
✅ 총 비용: 537만원 (부트스트래핑)
✅ 예상 Task 수: 66개
✅ 마일스톤: 7개 (M0-M6)
✅ 단계별 검증: Stage Gate 6회
✅ 리스크 관리: 10개 리스크 식별 + 완화 전략
```

**목표 런칭일**: 2026-04-16 (73일 후)

**작성자**: Claude Code
**버전**: 1.0
**작성일**: 2026-02-05
