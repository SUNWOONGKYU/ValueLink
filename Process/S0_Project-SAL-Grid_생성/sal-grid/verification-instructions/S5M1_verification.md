# S5M1 Verification

## 검증 대상

- **Task ID**: S5M1
- **Task Name**: 최종 문서화 및 핸드북
- **Stage**: S5 (개발 마무리)
- **Area**: M (Documentation)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **Markdown 문법 검증** (markdownlint 또는 수동 확인)
- [ ] **링크 유효성 검증** (내부 링크 작동 확인)
- [ ] **코드 블록 문법 검증** (Syntax Highlighting 정상)
- [ ] **이미지 경로 검증** (존재 확인)

---

### 2. 파일 생성 확인

- [ ] **`README.md` 존재** (루트 디렉토리)
- [ ] **`docs/architecture.md` 존재**
- [ ] **`docs/maintenance-guide.md` 존재**
- [ ] **`docs/troubleshooting.md` 존재**

---

### 3. 핵심 기능 테스트

#### 3.1 README.md 검증 (~400줄)

**필수 섹션:**
- [ ] **프로젝트 개요**
  - 프로젝트명
  - 핵심 기능 (5개 평가 방법, 14단계 워크플로우, 22개 AI 승인 포인트)
  - 기술 스택 (Next.js 14, React 18, TypeScript 5.3, Supabase, Vercel)

- [ ] **시작하기**
  - 사전 요구사항 (Node.js, npm, Supabase, Vercel)
  - 설치 단계 (1-5단계)
  - 환경 변수 설정 예시 (`.env.local`)

- [ ] **프로젝트 구조**
  - 폴더 트리 (app/, components/, lib/, types/, public/, tests/, docs/)
  - 각 폴더 설명

- [ ] **테스트**
  - 전체 테스트 실행 (`npm test`)
  - 통합 테스트 (`npm run test:integration`)
  - E2E 테스트 (`npm run test:e2e`)
  - 커버리지 (`npm run test:coverage`)
  - 테스트 현황 (21개, 85% 커버리지)

- [ ] **배포**
  - Vercel 배포 (단계별)
  - 환경 변수 설정
  - Cron Jobs 설정
  - GitHub Actions 자동 배포

- [ ] **문서**
  - 아키텍처 가이드 링크
  - 배포 가이드 링크
  - 유지보수 가이드 링크
  - 문제 해결 가이드 링크
  - 테스트 리포트 링크

- [ ] **보안**
  - RLS (Row Level Security)
  - CORS 설정
  - Secrets 관리
  - CRON_SECRET 인증
  - HTTPS 강제

- [ ] **기여**
  - Fork 및 브랜치 생성
  - 커밋 메시지 규칙 (feat:, fix:, docs:, refactor:, test:)
  - Pull Request 프로세스

- [ ] **지원**
  - 이슈 트래커 링크
  - 이메일
  - Slack (선택)

- [ ] **라이선스**
  - MIT License 명시

- [ ] **주요 기능 스크린샷 (선택)**
  - 대시보드
  - DCF 평가
  - 투자 뉴스 트래커

**코드 예시 검증:**
- [ ] 설치 명령어 실행 가능
- [ ] 환경 변수 예시 정확
- [ ] 테스트 명령어 작동
- [ ] 배포 명령어 작동

#### 3.2 docs/architecture.md 검증 (~500줄)

**필수 섹션:**
- [ ] **목차 (TOC)**

- [ ] **1. 시스템 개요**
  - ValueLink 소개
  - 핵심 개념 (Project, Valuation Method, Approval Point, Role)
  - 시스템 흐름 (14단계)

- [ ] **2. 기술 스택**
  - Frontend (Next.js, React, TypeScript, Tailwind CSS)
  - Backend (Supabase, Vercel)
  - AI (Claude, Gemini, OpenAI)
  - 크롤링 (Cheerio, node-cron)
  - 테스팅 (Jest, Playwright)
  - 선택 이유 설명

- [ ] **3. 아키텍처 패턴**
  - 레이어 구조 (Presentation, Application, Domain, Infrastructure)
  - 디자인 패턴 (Orchestrator, Abstract Class, Singleton, Strategy)

- [ ] **4. 데이터베이스 스키마**
  - 핵심 테이블 12개 (users, projects, quotes, negotiations, documents, approval_points, valuation_results, drafts, revisions, reports, investment_tracker, matching_requests)
  - RLS 정책 예시 (users, projects, documents)
  - 트리거 8개 (타임스탬프, 상태 전이, 알림)

- [ ] **5. API 설계**
  - RESTful API 규칙
  - 주요 엔드포인트 (Auth, Projects, Quotes, Valuation, Scheduler, Cron)
  - 에러 응답 형식
  - 에러 코드 (VALIDATION_ERROR, UNAUTHORIZED, FORBIDDEN, NOT_FOUND, INTERNAL_ERROR)

- [ ] **6. 평가 엔진 구조**
  - 오케스트레이터 (ValuationOrchestrator)
  - 추상 엔진 클래스 (ValuationEngine)
  - DCF 엔진 예시
  - 재무 수학 라이브러리 (WACC, NPV, IRR, Terminal Value, FCF)

- [ ] **7. 크롤러 구조**
  - 아키텍처 다이어그램
  - BaseCrawler (추상 클래스)
  - 사이트별 크롤러 (Naver 예시)

- [ ] **8. 스케줄러 구조**
  - TaskScheduler (클래스)
  - 주간 수집 작업
  - Vercel Cron 통합

- [ ] **9. 인증 및 권한**
  - 역할 (customer, accountant, admin)
  - 인증 흐름 (이메일 로그인, OAuth)
  - 권한 체크 (미들웨어)

- [ ] **10. 보안 고려사항**
  - 인증 보안 (JWT, HTTPS, CORS, Rate Limiting)
  - 데이터 보안 (RLS, 암호화, 환경 변수, Secrets)
  - API 보안 (CRON_SECRET, Input Validation, SQL Injection 방지, XSS 방지)
  - 파일 보안 (권한 정책, 타입 검증, 크기 제한)
  - 보안 헤더 (vercel.json)

**코드 예시 검증:**
- [ ] TypeScript 코드 문법 정확
- [ ] SQL 쿼리 실행 가능
- [ ] 설명과 코드 일치

#### 3.3 docs/maintenance-guide.md 검증 (~350줄)

**필수 섹션:**
- [ ] **목차 (TOC)**

- [ ] **1. 일상적 점검 항목**
  - 매일 확인 (시스템 상태, 크롤러 실행, 사용자 활동)
  - 주간 확인 (성능 메트릭, DB 크기, Storage 사용량)
  - 월간 확인 (보안 점검, 비즈니스 메트릭)

- [ ] **2. 데이터베이스 관리**
  - 인덱스 최적화 (느린 쿼리 확인, 인덱스 추가)
  - 데이터 정리 (오래된 데이터 삭제, 중복 데이터 확인)
  - 테이블 VACUUM

- [ ] **3. 크롤러 관리**
  - 상태 점검 (수동 실행, 수집 결과 확인)
  - 실패 원인 파악 (CSS 선택자, Rate Limiting, 타임아웃, 403/404)
  - CSS 선택자 업데이트

- [ ] **4. 로그 모니터링**
  - Vercel 로그 (Error 필터, 주요 에러 패턴)
  - Supabase 로그 (API, Database, Auth)
  - 커스텀 로깅 (logError 함수)

- [ ] **5. 백업 및 복구**
  - DB 백업 (Supabase 자동, 수동, S3)
  - DB 복구 (Dashboard, 로컬 파일)
  - Storage 백업

- [ ] **6. 성능 최적화**
  - DB 쿼리 최적화 (N+1 방지, 인덱스 활용)
  - 프론트엔드 최적화 (이미지, 코드 스플리팅, 서버 컴포넌트, Streaming, 캐싱)
  - 크롤러 최적화 (병렬 처리, Rate Limiting 조정)

- [ ] **7. 보안 점검**
  - 의존성 보안 취약점 (npm audit, Dependabot)
  - RLS 정책 검토
  - 환경 변수 로테이션 (3개월마다)

- [ ] **8. 업데이트 절차**
  - 의존성 업데이트 (Minor/Patch, Major)
  - Next.js 업데이트
  - Supabase 마이그레이션

**명령어 예시 검증:**
- [ ] SQL 쿼리 실행 가능
- [ ] Bash 명령어 실행 가능
- [ ] 설명 명확

#### 3.4 docs/troubleshooting.md 검증 (~400줄)

**필수 섹션:**
- [ ] **목차 (TOC)**

- [ ] **1. 일반적인 문제**
  - 로컬 서버 시작 안 됨 (TypeScript path alias)
  - 환경 변수 undefined (prefix 오류)
  - Supabase 연결 실패 (URL 형식)

- [ ] **2. 빌드 에러**
  - TypeScript 컴파일 에러 (Optional 타입)
  - Module not found (경로 오류)
  - Next.js 빌드 실패 (서버/클라이언트 혼용)

- [ ] **3. 런타임 에러**
  - Hydration 에러 (SSR vs 클라이언트)
  - Supabase RLS 에러 (정책 차단)
  - CORS 에러 (설정 오류)

- [ ] **4. 데이터베이스 에러**
  - Connection timeout (과부하)
  - Slow query (인덱스 누락)
  - Deadlock (Lock 충돌)

- [ ] **5. 인증 에러**
  - JWT expired (토큰 만료)
  - OAuth 리다이렉트 실패 (URL 미설정)
  - 세션 유지 안 됨 (쿠키 설정)

- [ ] **6. 크롤러 에러**
  - 0건 수집 (CSS 선택자 변경, IP 차단)
  - Timeout (응답 느림)
  - Rate limiting (429 에러)

- [ ] **7. 배포 문제**
  - Vercel 빌드 실패 (TypeScript 에러, 환경 변수)
  - Vercel Cron 작동 안 함 (CRON_SECRET, 미활성화)
  - 환경 변수 undefined (프로덕션)

- [ ] **8. 성능 문제**
  - 페이지 로딩 느림 (이미지, 번들, 서버 컴포넌트, Streaming)
  - API 응답 느림 (DB 쿼리, 캐싱, 병렬 요청)
  - DCF 계산 느림 (IRR 반복)

**문제 해결 패턴:**
- [ ] 증상 → 원인 → 해결 구조
- [ ] 코드 예시 (❌ Bad, ✅ Good)
- [ ] 명령어 예시

---

### 4. 통합 테스트

#### 4.1 선행 Task 연동

- [ ] **모든 S1-S4 Task 완료 확인**
  - 문서에 언급된 모든 기능 구현 확인

#### 4.2 내부 링크 검증

**README.md:**
- [ ] [아키텍처 가이드](docs/architecture.md) 링크 작동
- [ ] [배포 가이드](docs/deployment-guide.md) 링크 작동
- [ ] [유지보수 가이드](docs/maintenance-guide.md) 링크 작동
- [ ] [문제 해결 가이드](docs/troubleshooting.md) 링크 작동
- [ ] [테스트 리포트](docs/test-report.md) 링크 작동

**architecture.md:**
- [ ] 섹션 내부 링크 (TOC) 작동

**maintenance-guide.md:**
- [ ] 섹션 내부 링크 (TOC) 작동

**troubleshooting.md:**
- [ ] 섹션 내부 링크 (TOC) 작동

#### 4.3 코드 예시 실행 검증

**README.md 설치 단계:**
```bash
# 1. 레포지토리 클론
git clone https://github.com/user/valuelink.git
cd valuelink

# 2. 의존성 설치
npm install

# 3. 환경 변수 설정
cp .env.local.example .env.local

# 4. 데이터베이스 마이그레이션
npx supabase db push

# 5. 개발 서버 실행
npm run dev
```

- [ ] **각 단계 실행 가능**
- [ ] **에러 없음**

**architecture.md 코드 예시:**
```typescript
// Orchestrator 패턴
class ValuationOrchestrator {
  private engines: Map<ValuationMethod, ValuationEngine>
  registerEngine(method: ValuationMethod, engine: ValuationEngine)
  async executeValuation(input: ValuationInput): Promise<ValuationResult>
}
```

- [ ] **TypeScript 문법 정확**
- [ ] **코드 설명과 일치**

**maintenance-guide.md SQL 쿼리:**
```sql
-- 최근 7일간 수집 현황
SELECT
  DATE(created_at) as date,
  COUNT(*) as articles_count
FROM investment_tracker
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

- [ ] **SQL 문법 정확**
- [ ] **Supabase에서 실행 가능**

**troubleshooting.md 해결 코드:**
```typescript
// ❌ Bad
const url: string = process.env.NEXT_PUBLIC_SUPABASE_URL

// ✅ Good
const url = process.env.NEXT_PUBLIC_SUPABASE_URL!
```

- [ ] **문제와 해결책 명확**
- [ ] **코드 작동 가능**

#### 4.4 외부 링크 검증

- [ ] **Vercel 공식 문서** (https://vercel.com/docs)
- [ ] **GitHub Actions 문서** (https://docs.github.com/en/actions)
- [ ] **Supabase 공식 문서** (https://supabase.com/docs)
- [ ] **Jest 공식 문서** (https://jestjs.io/)
- [ ] **Playwright 공식 문서** (https://playwright.dev/)

---

### 5. Blocker 확인

- [ ] **의존성 차단**
  - 모든 S1-S4 Task 완료 확인

- [ ] **환경 차단**
  - Markdown 편집기 설치 (VS Code, Typora 등)

- [ ] **외부 API 차단**
  - 없음

---

## 합격 기준

### 필수 (Must Pass)

1. **파일 생성 완료** ✅ (4개)
2. **README.md 완성도** ✅ (~400줄, 모든 섹션)
3. **architecture.md 완성도** ✅ (~500줄, 10개 섹션)
4. **maintenance-guide.md 완성도** ✅ (~350줄, 8개 섹션)
5. **troubleshooting.md 완성도** ✅ (~400줄, 8개 섹션)
6. **내부 링크 작동** ✅ (TOC, 문서 간)
7. **코드 예시 정확** ✅ (문법, 실행 가능)
8. **외부 링크 유효** ✅

### 권장 (Nice to Pass)

1. **스크린샷 추가** ✨ (대시보드, DCF, 뉴스)
2. **다이어그램 추가** ✨ (Mermaid, 아키텍처)
3. **FAQ 섹션** ✨
4. **영문 버전** ✨

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **Markdown 문법**
   - 제목 레벨 (#, ##, ###)
   - 코드 블록 (```언어)
   - 링크 ([텍스트](URL))
   - 리스트 (-, 1., [ ])

2. **코드 예시 정확성**
   - 실행 가능한 코드만 작성
   - TypeScript 문법 준수
   - SQL 쿼리 검증
   - Bash 명령어 검증

3. **일관성**
   - 용어 통일 (Project, Valuation Method, Task, Verification)
   - 파일 경로 일관성 (`lib/`, `app/`, `docs/`)
   - 명령어 일관성 (`npm run`, `npx`)

4. **최신성**
   - Next.js 14, React 18 기준
   - 2026년 현재 기준
   - 최신 API 문법

5. **완결성**
   - 신규 개발자가 이해 가능
   - 모든 주요 기능 문서화
   - 예외 상황 처리 방법 제시

6. **가독성**
   - 목차(TOC) 제공
   - 섹션 구분 명확
   - 코드 예시 충분
   - 설명 간결

---

## PO 테스트 가이드

### 1. README.md 확인

**브라우저에서 열기:**
```bash
open README.md
# 또는 GitHub에서 확인
```

**확인 사항:**
- [ ] 프로젝트 개요 명확
- [ ] 설치 단계 따라하기 가능
- [ ] 프로젝트 구조 이해 가능
- [ ] 테스트 명령어 작동
- [ ] 배포 단계 이해 가능
- [ ] 문서 링크 작동
- [ ] 스크린샷 표시 (있으면)

### 2. architecture.md 확인

**브라우저에서 열기:**
```bash
open docs/architecture.md
```

**확인 사항:**
- [ ] 목차(TOC) 작동
- [ ] 시스템 개요 이해 가능
- [ ] 기술 스택 설명 명확
- [ ] 아키텍처 패턴 이해 가능
- [ ] DB 스키마 다이어그램 (있으면)
- [ ] API 엔드포인트 목록 완전
- [ ] 평가 엔진 구조 이해 가능
- [ ] 코드 예시 정확

### 3. maintenance-guide.md 확인

**브라우저에서 열기:**
```bash
open docs/maintenance-guide.md
```

**확인 사항:**
- [ ] 일상적 점검 항목 명확
- [ ] DB 관리 명령어 작동
- [ ] 크롤러 관리 방법 이해 가능
- [ ] 로그 모니터링 위치 확인
- [ ] 백업/복구 절차 명확
- [ ] 성능 최적화 팁 유용
- [ ] 보안 점검 체크리스트 완전
- [ ] 업데이트 절차 명확

### 4. troubleshooting.md 확인

**브라우저에서 열기:**
```bash
open docs/troubleshooting.md
```

**확인 사항:**
- [ ] 일반적인 문제 포함
- [ ] 증상 → 원인 → 해결 구조
- [ ] 코드 예시 (Bad vs Good) 명확
- [ ] 빌드 에러 해결 가능
- [ ] 런타임 에러 해결 가능
- [ ] DB 에러 해결 가능
- [ ] 인증 에러 해결 가능
- [ ] 크롤러 에러 해결 가능
- [ ] 배포 문제 해결 가능
- [ ] 성능 문제 해결 가능

### 5. 링크 검증

**내부 링크 (README.md에서):**
```bash
# 각 링크 클릭하여 파일 열리는지 확인
- [아키텍처 가이드](docs/architecture.md)
- [배포 가이드](docs/deployment-guide.md)
- [유지보수 가이드](docs/maintenance-guide.md)
- [문제 해결 가이드](docs/troubleshooting.md)
- [테스트 리포트](docs/test-report.md)
```

- [ ] 모든 내부 링크 작동

**외부 링크:**
- [ ] Vercel 문서 접속 가능
- [ ] GitHub Actions 문서 접속 가능
- [ ] Supabase 문서 접속 가능
- [ ] Jest 문서 접속 가능
- [ ] Playwright 문서 접속 가능

### 6. 코드 예시 실행

**README.md 설치 단계 실행:**
```bash
# 1. 레포지토리 클론 (이미 완료)
# 2. 의존성 설치
npm install

# 3. 환경 변수 설정
cp .env.local.example .env.local
# .env.local 편집

# 4. DB 마이그레이션
npx supabase db push

# 5. 개발 서버 실행
npm run dev
# http://localhost:3000 접속 확인
```

- [ ] 각 단계 성공
- [ ] 에러 없음

**maintenance-guide.md SQL 쿼리 실행:**
```sql
-- Supabase Dashboard → SQL Editor에서 실행
SELECT
  DATE(created_at) as date,
  COUNT(*) as articles_count
FROM investment_tracker
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

- [ ] 쿼리 실행 성공
- [ ] 결과 반환

---

## 참조

- Task Instruction: `task-instructions/S5M1_instruction.md`
- Markdown Guide: https://www.markdownguide.org/
- GitHub README Best Practices: https://github.com/RichardLitt/standard-readme

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
