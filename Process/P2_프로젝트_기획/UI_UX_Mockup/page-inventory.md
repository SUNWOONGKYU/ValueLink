# ValueLink 페이지 인벤토리

**작성일**: 2026-02-05
**버전**: 1.0
**프로젝트**: ValueLink - AI 기반 기업가치평가 플랫폼

---

## 개요

본 문서는 ValueLink 플랫폼의 **기존 72개 HTML 페이지**를 목록화하고 분류합니다.

### 주요 특징

```
✅ 총 72개 HTML 페이지 (Vanilla JS 목업)
✅ 14단계 워크플로우 완성
✅ 5개 평가 방법별 화면 구성
✅ 역할별 대시보드 (고객, 회계사, 관리자, 투자자)
```

### 재구축 전략

```
기존 72개 HTML 페이지 = 디자인 목업으로 활용
→ Next.js 14 + React + TypeScript로 재구축
→ Supabase 연동 강화
→ 디자인 변경 최소화 (UI/UX 검증 완료)
```

---

## 1. 카테고리별 분류

| 카테고리 | 페이지 수 | 설명 | 상태 |
|---------|----------|------|------|
| **Core** | 7 | 메인, 로그인, 회원가입 등 | ✅ 완료 |
| **Project Management** | 4 | 프로젝트 목록, 생성, 상세 | ✅ 완료 |
| **Workflow (14 Steps)** | 14 | 평가 프로세스 14단계 | ✅ 완료 |
| **Valuation Guides** | 5 | 평가 방법별 가이드 | ✅ 완료 |
| **Valuation Submissions** | 5 | 평가 방법별 정보 입력 | ✅ 완료 |
| **Valuation Results** | 5 | 평가 방법별 결과 화면 | ✅ 완료 |
| **Service Pages** | 6 | 서비스 소개, 가격, FAQ 등 | ✅ 완료 |
| **Dashboards** | 4 | 역할별 대시보드 | ✅ 완료 |
| **Admin** | 6 | 관리자 패널 (6개 탭) | ✅ 완료 |
| **Investment Tracker** | 4 | 투자 추적 시스템 | ✅ 완료 |
| **Others** | 12 | 에러, 약관, 프로필 등 | ✅ 완료 |

**총 페이지 수**: 72개

---

## 2. Core Pages (7개)

### 2.1 메인 페이지

| # | 파일명 | 경로 | 기능 | 작동 상태 |
|---|--------|------|------|----------|
| 1 | `index.html` | `/` | 랜딩 페이지 | 완전 작동 |
| 2 | `about.html` | `/about` | 회사 소개 | 완전 작동 |
| 3 | `features.html` | `/features` | 주요 기능 소개 | 완전 작동 |

### 2.2 인증 페이지

| # | 파일명 | 경로 | 기능 | 작동 상태 |
|---|--------|------|------|----------|
| 4 | `login.html` | `/auth/login` | 로그인 | Supabase 연동 |
| 5 | `signup.html` | `/auth/signup` | 회원가입 | Supabase 연동 |
| 6 | `forgot-password.html` | `/auth/forgot-password` | 비밀번호 찾기 | Supabase 연동 |
| 7 | `reset-password.html` | `/auth/reset-password` | 비밀번호 재설정 | Supabase 연동 |

---

## 3. Project Management (4개)

| # | 파일명 | 경로 | 기능 | Supabase 연동 |
|---|--------|------|------|--------------|
| 8 | `projects.html` | `/projects` | 프로젝트 목록 | ✅ projects 테이블 |
| 9 | `project-create.html` | `/projects/create` | 프로젝트 생성 | ✅ INSERT |
| 10 | `project-detail.html` | `/projects/:id` | 프로젝트 상세 | ✅ SELECT |
| 11 | `project-edit.html` | `/projects/:id/edit` | 프로젝트 수정 | ✅ UPDATE |

**데이터베이스 연동**:
- `projects` 테이블: company_name, industry, revenue, purpose, method, status
- RLS 정책: 사용자 본인 프로젝트만 조회/수정

---

## 4. Workflow - 14 Steps (14개)

ValueLink의 핵심 워크플로우 페이지입니다.

| Step | 파일명 | 경로 | 단계명 | 작동 상태 |
|------|--------|------|--------|----------|
| 1 | `step-01-request.html` | `/workflow/step-01` | 평가 요청 | ✅ 완전 작동 |
| 2 | `step-02-quote.html` | `/workflow/step-02` | 견적 제공 | ✅ quotes 연동 |
| 3 | `step-03-review.html` | `/workflow/step-03` | 견적 검토 | ✅ 완전 작동 |
| 4 | `step-04-negotiation.html` | `/workflow/step-04` | 협상 | ✅ negotiations 연동 |
| 5 | `step-05-contract.html` | `/workflow/step-05` | 계약 | ✅ 완전 작동 |
| 6 | `step-06-payment.html` | `/workflow/step-06` | 결제 | ⏳ Stripe 연동 필요 |
| 7 | `step-07-document-upload.html` | `/workflow/step-07` | 서류 업로드 | ✅ documents 연동 |
| 8 | `step-08-data-extraction.html` | `/workflow/step-08` | 데이터 추출 | ✅ AI 연동 |
| 9 | `step-09-draft-generation.html` | `/workflow/step-09` | 초안 생성 | ✅ drafts 연동 |
| 10 | `step-10-approval-points.html` | `/workflow/step-10` | 승인 포인트 | ✅ approval_points 연동 |
| 11 | `step-11-revision.html` | `/workflow/step-11` | 수정 | ✅ revisions 연동 |
| 12 | `step-12-final-report.html` | `/workflow/step-12` | 최종 보고서 | ✅ reports 연동 |
| 13 | `step-13-delivery.html` | `/workflow/step-13` | 납품 | ✅ 완전 작동 |
| 14 | `step-14-feedback.html` | `/workflow/step-14` | 피드백 | ✅ 완전 작동 |

**핵심 특징**:
- 각 단계는 독립적인 페이지로 구성
- 진행 상황 표시 (Progress Bar)
- 이전/다음 단계 네비게이션
- Supabase에 단계별 상태 저장

---

## 5. Valuation Guides (5개)

평가 방법별 상세 설명 페이지입니다.

| # | 파일명 | 경로 | 평가 방법 | 설명 |
|---|--------|------|----------|------|
| 15 | `dcf-guide.html` | `/valuation/dcf/guide` | DCF 평가법 | 현금흐름할인법 |
| 16 | `relative-guide.html` | `/valuation/relative/guide` | 상대가치 평가법 | 유사 기업 비교 |
| 17 | `asset-guide.html` | `/valuation/asset/guide` | 자산가치 평가법 | 순자산 기준 |
| 18 | `intrinsic-guide.html` | `/valuation/intrinsic/guide` | 본질가치 평가법 | 수익가치 기준 |
| 19 | `tax-guide.html` | `/valuation/tax/guide` | 상증법 평가법 | 세법 기준 |

**공통 구성**:
- 평가 방법 개요
- 적용 대상 기업
- 필요 서류 목록
- 예상 소요 기간
- 가격 정보

---

## 6. Valuation Submissions (5개)

평가 방법별 정보 입력 페이지입니다.

| # | 파일명 | 경로 | 평가 방법 | 입력 항목 |
|---|--------|------|----------|----------|
| 20 | `dcf-submission.html` | `/valuation/dcf/submit` | DCF 평가법 | 재무제표 3년, 성장률, 할인율 |
| 21 | `relative-submission.html` | `/valuation/relative/submit` | 상대가치 평가법 | 유사 기업 목록, 배수 |
| 22 | `asset-submission.html` | `/valuation/asset/submit` | 자산가치 평가법 | 자산/부채 목록 |
| 23 | `intrinsic-submission.html` | `/valuation/intrinsic/submit` | 본질가치 평가법 | 수익력, 순자산 |
| 24 | `tax-submission.html` | `/valuation/tax/submit` | 상증법 평가법 | 순손익, 순자산 |

**공통 기능**:
- 파일 업로드 (PDF, Excel)
- 폼 입력 (텍스트, 숫자)
- 임시 저장 기능
- Supabase documents 테이블 연동

---

## 7. Valuation Results (5개)

평가 방법별 결과 표시 페이지입니다.

| # | 파일명 | 경로 | 평가 방법 | 결과 항목 |
|---|--------|------|----------|----------|
| 25 | `dcf-result.html` | `/valuation/dcf/result/:id` | DCF 평가법 | 기업가치, 주당가치, DCF 테이블 |
| 26 | `relative-result.html` | `/valuation/relative/result/:id` | 상대가치 평가법 | 유사 기업 비교표, 배수 |
| 27 | `asset-result.html` | `/valuation/asset/result/:id` | 자산가치 평가법 | 순자산가치, 자산/부채 |
| 28 | `intrinsic-result.html` | `/valuation/intrinsic/result/:id` | 본질가치 평가법 | 수익가치, 순자산가치 |
| 29 | `tax-result.html` | `/valuation/tax/result/:id` | 상증법 평가법 | 1주당 가액, 평가표 |

**공통 기능**:
- 차트 시각화 (Chart.js)
- PDF 다운로드 버튼
- 이메일 발송 버튼
- Supabase valuation_results 테이블 연동

---

## 8. Service Pages (6개)

서비스 소개 및 안내 페이지입니다.

| # | 파일명 | 경로 | 기능 | 상태 |
|---|--------|------|------|------|
| 30 | `services.html` | `/services` | 서비스 소개 | 완전 작동 |
| 31 | `pricing.html` | `/pricing` | 가격 안내 | 완전 작동 |
| 32 | `faq.html` | `/faq` | FAQ | 완전 작동 |
| 33 | `contact.html` | `/contact` | 문의하기 | Resend 연동 필요 |
| 34 | `blog.html` | `/blog` | 블로그 목록 | 목업만 |
| 35 | `blog-post.html` | `/blog/:id` | 블로그 상세 | 목업만 |

**가격표 정보** (pricing.html):
| 평가 방법 | 가격 | 납기 |
|----------|------|------|
| DCF 평가 | 800만원 | 7-10일 |
| 상대가치 평가 | 500만원 | 5-7일 |
| 상증법 평가 | 1,000만원 | 10-14일 |
| IPO 평가 | 2,000만원 | 14-21일 |
| 자산가치 평가 | 600만원 | 7-10일 |

---

## 9. Dashboards (4개)

역할별 대시보드 페이지입니다.

### 9.1 고객 대시보드

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 36 | `dashboard-customer.html` | `/dashboard/customer` | 고객 대시보드 | ✅ Supabase |

**주요 위젯**:
- 내 프로젝트 목록 (projects 테이블)
- 진행 상황 (status)
- 최근 활동 (activity log)
- 결제 내역 (payments)

### 9.2 회계사 대시보드

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 37 | `dashboard-accountant.html` | `/dashboard/accountant` | 회계사 대시보드 | ✅ Supabase |

**주요 위젯**:
- 할당된 프로젝트 목록
- 승인 대기 중인 포인트 (approval_points)
- 작업 현황 (drafts, revisions)
- 이번 달 수익

### 9.3 관리자 대시보드

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 38 | `dashboard-admin.html` | `/dashboard/admin` | 관리자 대시보드 | ✅ Supabase |

**주요 위젯**:
- 전체 프로젝트 통계
- 월별 매출
- 사용자 현황
- 시스템 상태

### 9.4 투자자 대시보드

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 39 | `dashboard-investor.html` | `/dashboard/investor` | 투자자 대시보드 | ⏳ 계획 중 |

**주요 위젯** (계획):
- 기업 랭킹 목록
- 관심 기업
- 투자 기회
- 매칭 현황

---

## 10. Admin Panel (6개)

관리자 패널의 6개 탭 페이지입니다.

| # | 파일명 | 경로 | 탭명 | 기능 | 연동 상태 |
|---|--------|------|------|------|----------|
| 40 | `admin-projects.html` | `/admin/projects` | 프로젝트 관리 | 전체 프로젝트 조회/수정 | ✅ Supabase |
| 41 | `admin-users.html` | `/admin/users` | 사용자 관리 | 사용자 목록, 역할 변경 | ✅ Supabase |
| 42 | `admin-accountants.html` | `/admin/accountants` | 회계사 관리 | 회계사 할당, 성과 조회 | ✅ Supabase |
| 43 | `admin-payments.html` | `/admin/payments` | 결제 관리 | 결제 내역, 환불 처리 | ⏳ Stripe 연동 필요 |
| 44 | `admin-analytics.html` | `/admin/analytics` | 통계 분석 | 매출, 전환율, 트래픽 | ✅ Chart.js |
| 45 | `admin-settings.html` | `/admin/settings` | 시스템 설정 | 가격, 이메일 템플릿 등 | ✅ Supabase |

**권한 제어**:
- RLS 정책: role = 'admin'만 접근 가능
- 관리자 전용 메뉴
- 감사 로그 기록

---

## 11. Investment Tracker (4개)

투자 추적 시스템 페이지입니다.

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 46 | `investment-tracker.html` | `/investment-tracker` | 투자 추적 메인 | ✅ Supabase |
| 47 | `investment-add.html` | `/investment-tracker/add` | 투자 정보 등록 | ✅ INSERT |
| 48 | `investment-detail.html` | `/investment-tracker/:id` | 투자 상세 | ✅ SELECT |
| 49 | `investment-analytics.html` | `/investment-tracker/analytics` | 투자 분석 | ✅ Chart.js |

**주요 기능**:
- 투자 포트폴리오 관리
- 투자금액, 지분율 추적
- ROI 계산 및 시각화
- 엑시트 시뮬레이션

**데이터베이스**: `investment_tracker` 테이블 (별도)

---

## 12. Other Pages (12개)

기타 필수 페이지들입니다.

### 12.1 프로필 관리

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 50 | `profile.html` | `/profile` | 프로필 조회 | ✅ Supabase |
| 51 | `profile-edit.html` | `/profile/edit` | 프로필 수정 | ✅ UPDATE |
| 52 | `settings.html` | `/settings` | 계정 설정 | ✅ Supabase |

### 12.2 법적 문서

| # | 파일명 | 경로 | 기능 | 상태 |
|---|--------|------|------|------|
| 53 | `terms.html` | `/terms` | 이용약관 | 완전 작동 |
| 54 | `privacy.html` | `/privacy` | 개인정보처리방침 | 완전 작동 |
| 55 | `refund.html` | `/refund` | 환불 정책 | 완전 작동 |

### 12.3 에러 페이지

| # | 파일명 | 경로 | 기능 | 상태 |
|---|--------|------|------|------|
| 56 | `404.html` | `/404` | 페이지 없음 | 완전 작동 |
| 57 | `500.html` | `/500` | 서버 오류 | 완전 작동 |
| 58 | `maintenance.html` | `/maintenance` | 점검 중 | 완전 작동 |

### 12.4 알림 & 도움말

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 59 | `notifications.html` | `/notifications` | 알림 목록 | ✅ Supabase |
| 60 | `help.html` | `/help` | 도움말 센터 | 완전 작동 |
| 61 | `onboarding.html` | `/onboarding` | 온보딩 투어 | 완전 작동 |

---

## 13. 추가 발견 페이지 (11개)

기존 분석에서 누락된 페이지들입니다.

### 13.1 AI Avatar IR

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 62 | `ai-avatar.html` | `/ai-avatar` | AI Avatar 소개 | 완전 작동 |
| 63 | `ai-avatar-setup.html` | `/ai-avatar/setup` | Avatar 설정 | ⏳ Claude API 연동 필요 |
| 64 | `ai-avatar-dashboard.html` | `/ai-avatar/dashboard` | Avatar 대시보드 | ⏳ 계획 중 |

**주요 기능** (계획):
- 24시간 투자자 대응 AI
- 기업 정보 학습
- 대화 로그 분석
- 월 이용료: 200만원

### 13.2 랭킹 시스템

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 65 | `ranking.html` | `/ranking` | 기업 랭킹 목록 | ⏳ 계획 중 |
| 66 | `ranking-detail.html` | `/ranking/:id` | 기업 상세 정보 | ⏳ 계획 중 |

**주요 기능** (계획):
- 객관적 기준 기반 랭킹
- 필터링 (업종, 지역, 투자단계)
- 관심 기업 등록
- 프리미엄 노출 (월 50-100만원)

### 13.3 매칭 시스템

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 67 | `matching.html` | `/matching` | 매칭 메인 | ⏳ 계획 중 |
| 68 | `matching-request.html` | `/matching/request` | 매칭 요청 | ⏳ 계획 중 |
| 69 | `matching-result.html` | `/matching/result/:id` | 매칭 결과 | ⏳ 계획 중 |

**주요 기능** (계획):
- AI 기반 투자자-기업 매칭
- 매칭 스코어 계산
- 중개 수수료: 투자액의 1-3%

### 13.4 기타

| # | 파일명 | 경로 | 기능 | 연동 상태 |
|---|--------|------|------|----------|
| 70 | `subscription.html` | `/subscription` | 구독 관리 | ⏳ Stripe 연동 필요 |
| 71 | `referral.html` | `/referral` | 추천 프로그램 | ⏳ 계획 중 |
| 72 | `download.html` | `/download` | 보고서 다운로드 센터 | ✅ Supabase |

---

## 14. 재구축 우선순위

### Phase 1: 핵심 기능 (S1-S2)

**우선순위 A** (즉시 재구축):
1. Core Pages (7개) - 인증, 메인
2. Project Management (4개) - 프로젝트 CRUD
3. Workflow Steps (14개) - 핵심 워크플로우
4. Dashboards (3개) - 고객, 회계사, 관리자

**총 28개 페이지**

### Phase 2: 평가 기능 (S3)

**우선순위 B**:
5. Valuation Guides (5개)
6. Valuation Submissions (5개)
7. Valuation Results (5개)

**총 15개 페이지**

### Phase 3: 플랫폼 기능 (S4)

**우선순위 C**:
8. Admin Panel (6개)
9. Service Pages (6개)
10. Investment Tracker (4개)
11. Other Pages (12개)

**총 28개 페이지**

### Phase 4: 확장 기능 (S4-S5)

**우선순위 D** (차후 개발):
12. AI Avatar IR (3개)
13. Ranking System (2개)
14. Matching System (3개)
15. Subscription (3개)

**총 11개 페이지**

---

## 15. 디자인 시스템 추출

### 15.1 컬러 팔레트

기존 HTML에서 추출한 컬러:

```css
/* Primary */
--primary: #DC2626;         /* Red 600 */
--primary-hover: #B91C1C;   /* Red 700 */

/* Secondary */
--secondary: #1F2937;       /* Gray 800 */
--secondary-light: #374151; /* Gray 700 */

/* Background */
--bg-primary: #FFFFFF;      /* White */
--bg-secondary: #F9FAFB;    /* Gray 50 */
--bg-dark: #111827;         /* Gray 900 */

/* Text */
--text-primary: #111827;    /* Gray 900 */
--text-secondary: #6B7280;  /* Gray 500 */
--text-light: #9CA3AF;      /* Gray 400 */

/* Status */
--success: #10B981;         /* Green 500 */
--warning: #F59E0B;         /* Amber 500 */
--error: #EF4444;           /* Red 500 */
--info: #3B82F6;            /* Blue 500 */
```

### 15.2 타이포그래피

```css
/* Font Family */
font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

### 15.3 공통 컴포넌트

| 컴포넌트 | 사용 빈도 | 특징 |
|---------|----------|------|
| Button | 높음 | Primary, Secondary, Outline |
| Card | 높음 | Shadow, Border, Padding |
| Table | 중간 | Striped, Hover, Responsive |
| Form | 높음 | Label, Input, Validation |
| Modal | 중간 | Backdrop, Close Button |
| Alert | 중간 | Success, Warning, Error, Info |
| Progress Bar | 낮음 | 14 Steps 진행 표시 |
| Chart | 낮음 | Chart.js 기반 |

---

## 16. Supabase 연동 현황

### 연동 완료 (✅)

| 페이지 그룹 | 테이블 | 기능 |
|-----------|-------|------|
| Auth | auth.users | 로그인, 회원가입, 비밀번호 재설정 |
| Projects | projects | CRUD, 목록 조회 |
| Workflow | quotes, negotiations, documents | 견적, 협상, 서류 |
| Valuation | approval_points, drafts, revisions | 승인, 초안, 수정 |
| Results | valuation_results, reports | 결과, 보고서 |
| Admin | 모든 테이블 | 관리자 권한 |
| Investment Tracker | investment_tracker | 투자 추적 (별도) |

### 연동 필요 (⏳)

| 페이지 그룹 | 서비스 | 작업 |
|-----------|-------|------|
| Payment | Stripe | 결제, 환불 처리 |
| Email | Resend | 이메일 발송 |
| AI Avatar | Claude API | AI Avatar 연동 |
| Ranking | 신규 테이블 | 랭킹 시스템 구축 |
| Matching | 신규 테이블 | 매칭 알고리즘 |

---

## 17. 기술 스택 정리

### Frontend

| 기술 | 현재 (Vanilla) | 재구축 (Next.js) |
|------|---------------|-----------------|
| Framework | HTML/CSS/JS | Next.js 14 |
| Language | JavaScript | TypeScript |
| Styling | Tailwind CSS | Tailwind CSS |
| State | localStorage | React State + Zustand |
| Forms | Vanilla | React Hook Form |
| Charts | Chart.js | Chart.js 또는 Recharts |

### Backend & Infra

| 기술 | 상태 |
|------|------|
| **Database** | Supabase (PostgreSQL) ✅ |
| **Auth** | Supabase Auth (JWT) ✅ |
| **Storage** | Supabase Storage ✅ |
| **API** | FastAPI (Python) ✅ |
| **AI** | Claude, Gemini, GPT-4 ✅ |
| **Email** | Resend ⏳ |
| **Payment** | Stripe ⏳ |
| **Hosting** | Vercel ⏳ |

---

## 18. 개발 전략

### 18.1 페이지 재구축 순서

```
[S1] 개발 준비
  → 환경 설정, Supabase 연동, Auth 설정

[S2] 인증 & 핵심 기능
  → Core Pages (7) + Project Management (4)
  → 총 11개 페이지

[S3] 평가 워크플로우
  → Workflow (14) + Valuation (15)
  → 총 29개 페이지

[S4] 플랫폼 기능
  → Admin (6) + Dashboards (4) + Service (6)
  → 총 16개 페이지

[S5] 확장 기능
  → AI Avatar (3) + Ranking (2) + Matching (3)
  → 총 8개 페이지 + 최종 QA
```

### 18.2 컴포넌트 재사용 전략

**공통 컴포넌트 먼저 개발**:
```tsx
components/
├── ui/                      // 기본 UI
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Table.tsx
│   ├── Modal.tsx
│   └── Form.tsx
├── layout/                  // 레이아웃
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── Footer.tsx
│   └── DashboardLayout.tsx
├── valuation/               // 평가 관련
│   ├── ProgressBar.tsx     // 14 Steps
│   ├── ApprovalPoint.tsx   // 승인 포인트
│   └── ResultChart.tsx     // 결과 차트
└── dashboard/               // 대시보드
    ├── StatCard.tsx
    ├── ProjectList.tsx
    └── ActivityLog.tsx
```

**재사용률 목표**: 80% (72개 중 58개 페이지가 공통 컴포넌트 사용)

---

## 19. 마이그레이션 체크리스트

### Phase 1: 준비 (P0-P3)

- [x] 72개 페이지 목록 작성
- [x] 카테고리 분류
- [x] Supabase 연동 현황 파악
- [ ] 디자인 시스템 문서화
- [ ] 공통 컴포넌트 설계

### Phase 2: 개발 (S1-S5)

- [ ] Next.js 프로젝트 초기화
- [ ] Supabase 클라이언트 설정
- [ ] Auth 페이지 재구축 (4개)
- [ ] 핵심 페이지 재구축 (11개)
- [ ] 워크플로우 재구축 (29개)
- [ ] 플랫폼 기능 재구축 (16개)
- [ ] 확장 기능 개발 (8개)

### Phase 3: 검증 (Stage Gates)

- [ ] 모든 페이지 빌드 성공
- [ ] Supabase RLS 정책 적용
- [ ] E2E 테스트 통과
- [ ] PO 최종 승인

---

## 20. 참조 파일

| 파일 | 경로 | 용도 |
|------|------|------|
| 기존 HTML | `Valuation_Company/valuation-platform/frontend/app/` | 디자인 참조 |
| 데이터베이스 | `backend/create_tables.sql` | 스키마 참조 |
| 아키텍처 | `Process/P2_프로젝트_기획/Tech_Stack/architecture.md` | 기술 스택 |
| ERD | `Process/P2_프로젝트_기획/Tech_Stack/database-erd.md` | 데이터 구조 |

---

## 요약

```
✅ 총 72개 HTML 페이지 인벤토리 완료
✅ 카테고리별 분류 및 우선순위 설정
✅ Supabase 연동 현황 파악
✅ 재구축 전략 수립
✅ 4단계 Phase로 재구축 계획 수립
```

**다음 단계**: P2 나머지 문서 작성 → P3 프로토타입 정리 → S0 SAL Grid 생성

**작성자**: Claude Code
**버전**: 1.0
**작성일**: 2026-02-05
