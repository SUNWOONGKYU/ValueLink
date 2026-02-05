# S2F5 Verification

## 검증 대상

- **Task ID**: S2F5
- **Task Name**: 프로세스 단계 템플릿 및 12개 워크플로우 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)

## 검증자

**Verification Agent**: qa-specialist

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **TypeScript 빌드 성공** (`npm run type-check`)
- [ ] **Next.js 빌드 성공** (`npm run build`)
- [ ] **ESLint 경고 0개** (`npm run lint`)

---

### 2. 파일 생성 확인

#### 2.1 프로세스 템플릿 컴포넌트

- [ ] **`components/process-step-template.tsx` 파일 존재**
  - Props: `projectId`, `projectName`, `currentStep`, `totalSteps`, `stepTitle`, `children`
  - 14단계 프로세스 사이드바 포함

#### 2.2 12개 워크플로우 페이지

- [ ] **`app/valuation/evaluation-progress/page.tsx` 존재** (Step 5)
- [ ] **`app/valuation/data-collection/page.tsx` 존재** (Step 6)
- [ ] **`app/valuation/accountant-review/page.tsx` 존재** (Step 7)
- [ ] **`app/valuation/draft-generation/page.tsx` 존재** (Step 8)
- [ ] **`app/valuation/report-draft/page.tsx` 존재** (Step 9)
- [ ] **`app/valuation/revision-request/page.tsx` 존재** (Step 10)
- [ ] **`app/valuation/final-preparation/page.tsx` 존재** (Step 11)
- [ ] **`app/valuation/report-final/page.tsx` 존재** (Step 12)
- [ ] **`app/valuation/deposit-payment/page.tsx` 존재** (Step 13 - 무통장 입금)
- [ ] **`app/valuation/balance-payment/page.tsx` 존재** (Step 13 - 잔금)
- [ ] **`app/valuation/payment/page.tsx` 존재** (Step 13 - 통합 결제)
- [ ] **`app/valuation/report-download/page.tsx` 존재** (Step 14)

---

### 3. 핵심 기능 테스트

#### 3.1 템플릿 컴포넌트 재사용

- [ ] **12개 워크플로우 페이지 모두 `ProcessStepTemplate` 사용**
  - 각 페이지에서 import 확인
  - 각 페이지마다 `currentStep` 값이 다름

#### 3.2 프로세스 사이드바 동작

- [ ] **14단계 프로세스 표시**
  - 완료 단계: 녹색 체크마크
  - 현재 단계: 빨간색 시계 아이콘
  - 예정 단계: 회색 숫자

- [ ] **현재 단계 하이라이트**
  - `currentStep` 기준으로 동적 상태 설정
  - 이전 단계는 'completed', 현재는 'current', 이후는 'upcoming'

#### 3.3 무통장 입금 페이지 특수 기능

- [ ] **계좌 정보 표시**
  - 은행: 우리은행
  - 계좌번호: 1005-404-483025
  - 예금주: 호수회계법인

- [ ] **계좌번호 복사 기능**
  - "복사" 버튼 클릭 시 클립보드에 복사
  - 복사 완료 시 "복사됨" 표시 (2초)

- [ ] **입금 금액 표시**
  - 평가 방법별 금액 표시

#### 3.4 페이지별 상태 카드

- [ ] **각 워크플로우 페이지에 상태 카드 포함**
  - 예상 완료일, 진행률, 평가 방법 등
  - 아이콘 + 제목 + 값 구조

---

### 4. 통합 테스트

#### 4.1 선행 Task 호환

- [ ] **S1BI1 (Next.js 초기화) 의존성 충족**
  - `@/lib/supabase/client` import 가능

#### 4.2 후행 Task 준비

- [ ] **S2BA1 (워크플로우 API) 연결 준비**
  - API 없이도 UI 정상 렌더링
  - API 호출 시 에러 처리

#### 4.3 데이터 흐름 검증

- [ ] **URL 파라미터로 프로젝트 조회**
  - `?project_id={uuid}` 형식
  - Supabase에서 프로젝트 정보 로드

---

### 5. Blocker 확인

#### 5.1 의존성 차단

- [ ] **S1BI1 완료 확인**
  - Next.js 프로젝트 초기화 완료

#### 5.2 환경 차단

- [ ] **lucide-react 패키지 설치 확인**
  - 명령어: `npm list lucide-react`

#### 5.3 외부 API 차단

- [ ] **Supabase 연결 필요**
  - 환경 변수 설정 완료 확인
  - `projects` 테이블 접근 가능

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **모든 파일 생성 완료** ✅ (13개 파일)
3. **템플릿 컴포넌트 재사용** ✅
4. **프로세스 사이드바 동작** ✅
5. **무통장 입금 페이지 (계좌정보 표시)** ✅

### 권장 (Nice to Pass)

1. **입금 확인 자동화** ✨
2. **실시간 상태 업데이트** ✨

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

**검증일**: _______________

**검증자**: _______________

---

## 주의사항

1. **무통장 입금 정보**
   - 계좌번호: 1005-404-483025 (우리은행)
   - 예금주: 호수회계법인
   - **Stripe 결제 영원히 제외**

2. **프로세스 흐름**
   - 단계 순서 엄격히 준수
   - 이전 단계 완료 전 다음 단계 진입 불가

3. **템플릿 일관성**
   - 12개 페이지 모두 동일한 레이아웃
   - 사이드바, 헤더, 버튼 위치 일치

---

## 참조

- Task Instruction: `task-instructions/S2F5_instruction.md`
- 기존 프로토타입: `Valuation_Company/valuation-platform/frontend/app/valuation/evaluation-progress.html`

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
