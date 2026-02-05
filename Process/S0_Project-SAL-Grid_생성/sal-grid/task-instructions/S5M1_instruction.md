# S5M1: 최종 문서화 및 핸드북

## Task 정보

- **Task ID**: S5M1
- **Task Name**: 최종 문서화 및 핸드북
- **Stage**: S5 (개발 마무리)
- **Area**: M (Documentation)
- **Dependencies**: 모든 S1-S4 Task 완료
- **Task Agent**: documentation-specialist
- **Verification Agent**: code-reviewer

---

## Task 목표

프로젝트의 모든 구현을 종합한 **완전한 문서 세트**를 작성하여, 향후 유지보수자와 신규 개발자가 시스템을 이해하고 운영할 수 있도록 함.

---

## 상세 지시사항

### 1. README.md (프로젝트 개요 및 설치 가이드) - ~400줄

**파일 위치:** `README.md` (루트)

**구조:**
```markdown
# ValueLink - 기업가치평가 플랫폼

[![CI](https://github.com/user/valuelink/actions/workflows/ci.yml/badge.svg)](https://github.com/user/valuelink/actions/workflows/ci.yml)
[![Deploy](https://github.com/user/valuelink/actions/workflows/cd.yml/badge.svg)](https://github.com/user/valuelink/actions/workflows/cd.yml)

## 📋 프로젝트 개요

ValueLink는 AI 기반 기업가치평가 자동화 플랫폼입니다.

**핵심 기능:**
- 5개 평가 방법 (DCF, Relative, Asset, Intrinsic, Tax)
- 14단계 평가 워크플로우
- 22개 AI 승인 포인트
- 투자 뉴스 자동 수집 및 모니터링
- 실시간 협업 (고객 ↔ 회계사)

**기술 스택:**
- Frontend: Next.js 14, React 18, TypeScript 5.3, Tailwind CSS 3.4
- Backend: Supabase (PostgreSQL 15, Auth, Storage, RLS)
- AI: Claude API (60%), Gemini API (20%), OpenAI API (20%)
- 배포: Vercel (Seoul region)
- 크롤링: Cheerio, node-cron
- 테스팅: Jest, Playwright

---

## 🚀 시작하기

### 사전 요구사항

- Node.js 20.x 이상
- npm 10.x 이상
- Supabase 계정 (무료)
- Vercel 계정 (무료)

### 설치

**1단계: 레포지토리 클론**
```bash
git clone https://github.com/user/valuelink.git
cd valuelink
```

**2단계: 의존성 설치**
```bash
npm install
```

**3단계: 환경 변수 설정**
```bash
cp .env.local.example .env.local
```

`.env.local` 파일 편집:
```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI APIs
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
GOOGLE_AI_API_KEY=xxx

# Cron Security
CRON_SECRET=random-secret-string
```

**4단계: 데이터베이스 마이그레이션**
```bash
# Supabase CLI 로그인
npx supabase login

# 마이그레이션 실행
npx supabase db push
```

**5단계: 개발 서버 실행**
```bash
npm run dev
```

브라우저에서 http://localhost:3000 열기

---

## 📁 프로젝트 구조

```
valuelink/
├── app/                        # Next.js App Router
│   ├── (auth)/                 # 인증 그룹 (로그인, 회원가입)
│   ├── (customer)/             # 고객 그룹 (프로젝트, 견적, 문서)
│   ├── (accountant)/           # 회계사 그룹 (평가, 초안, 검토)
│   ├── (admin)/                # 관리자 그룹 (대시보드)
│   ├── deal/                   # 투자 뉴스 트래커
│   ├── link/                   # 투자 매칭
│   └── api/                    # API 라우트
│       ├── auth/               # 인증 API
│       ├── valuation/          # 평가 API
│       ├── scheduler/          # 스케줄러 API
│       └── cron/               # Vercel Cron 엔드포인트
├── components/                 # React 컴포넌트
│   ├── auth/                   # 인증 컴포넌트
│   ├── layout/                 # 레이아웃 (헤더, 사이드바)
│   ├── project/                # 프로젝트 관련
│   ├── valuation/              # 평가 관련
│   └── ui/                     # 공통 UI (버튼, 카드, 테이블)
├── lib/                        # 라이브러리 및 유틸리티
│   ├── supabase/               # Supabase 클라이언트
│   ├── valuation/              # 평가 엔진
│   │   ├── orchestrator.ts     # 평가 오케스트레이터
│   │   ├── financial-math.ts   # 재무 수학 라이브러리
│   │   ├── engines/            # 5개 평가 엔진
│   │   └── sensitivity.ts      # 민감도 분석
│   ├── crawler/                # 뉴스 크롤러
│   │   ├── base-crawler.ts     # 추상 크롤러 클래스
│   │   ├── crawler-manager.ts  # 크롤러 관리자
│   │   ├── news-parser.ts      # 뉴스 파싱
│   │   └── sites/              # 사이트별 크롤러 (6개)
│   ├── scheduler/              # 작업 스케줄러
│   ├── integrations/           # 외부 연동
│   └── utils/                  # 유틸리티 함수
├── types/                      # TypeScript 타입 정의
├── public/                     # 정적 파일
├── tests/                      # 테스트
│   ├── integration/            # 통합 테스트
│   └── e2e/                    # E2E 테스트
├── docs/                       # 문서
│   ├── architecture.md         # 아키텍처
│   ├── deployment-guide.md     # 배포 가이드
│   ├── maintenance-guide.md    # 유지보수 가이드
│   ├── troubleshooting.md      # 문제 해결
│   └── test-report.md          # 테스트 리포트
├── scripts/                    # 스크립트
│   └── deploy.sh               # 배포 스크립트
├── .github/                    # GitHub Actions
│   └── workflows/
│       ├── ci.yml              # CI 파이프라인
│       └── cd.yml              # CD 파이프라인
├── .env.local.example          # 환경 변수 예시
├── vercel.json                 # Vercel 설정
├── next.config.js              # Next.js 설정
├── tsconfig.json               # TypeScript 설정
├── package.json                # 의존성
└── README.md                   # 이 파일
```

---

## 🧪 테스트

### 전체 테스트 실행
```bash
npm test
```

### 통합 테스트
```bash
npm run test:integration
```

### E2E 테스트
```bash
npm run test:e2e
```

### 커버리지
```bash
npm run test:coverage
```

**테스트 현황:**
- 총 21개 테스트 (18 통합 + 3 E2E)
- 커버리지: 85%
- 모든 테스트 통과 ✅

---

## 🚢 배포

### Vercel 배포

**1단계: Vercel CLI 설치**
```bash
npm install -g vercel
```

**2단계: 배포**
```bash
vercel --prod
```

**3단계: 환경 변수 설정 (Vercel Dashboard)**
- Project Settings → Environment Variables
- `.env.local`의 모든 변수 추가

**4단계: Cron Jobs 설정**
- Vercel Dashboard → Cron Jobs
- `vercel.json`에 정의된 Cron 확인

### GitHub Actions 자동 배포

`main` 브랜치에 푸시하면 자동 배포:
```bash
git push origin main
```

CI/CD 파이프라인:
- ✅ Lint (ESLint)
- ✅ Type Check (TypeScript)
- ✅ Build (Next.js)
- ✅ Test (Jest)
- ✅ Deploy (Vercel)

---

## 📚 문서

- [아키텍처 가이드](docs/architecture.md) - 시스템 아키텍처 및 설계 패턴
- [배포 가이드](docs/deployment-guide.md) - 배포 프로세스 및 설정
- [유지보수 가이드](docs/maintenance-guide.md) - 일상적 유지보수 작업
- [문제 해결 가이드](docs/troubleshooting.md) - 일반적인 문제 및 해결책
- [테스트 리포트](docs/test-report.md) - 테스트 결과 및 커버리지

---

## 🔒 보안

- **RLS (Row Level Security)**: 모든 Supabase 테이블에 적용
- **CORS**: 허용된 도메인만 접근
- **Secrets**: 환경 변수로 관리, 절대 커밋하지 않음
- **CRON_SECRET**: Vercel Cron 인증
- **HTTPS**: 모든 통신 암호화

---

## 🤝 기여

1. Fork 레포지토리
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 커밋 (`git commit -m 'feat: Add amazing feature'`)
4. 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

**커밋 메시지 규칙:**
- `feat:` 새로운 기능
- `fix:` 버그 수정
- `docs:` 문서 수정
- `refactor:` 리팩토링
- `test:` 테스트 추가

---

## 📞 지원

- 이슈 트래커: https://github.com/user/valuelink/issues
- 이메일: support@valuelink.ai.kr
- Slack: valuelink.slack.com

---

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

---

## ✨ 주요 기능 스크린샷

### 1. 대시보드
![대시보드](docs/images/dashboard.png)

### 2. DCF 평가
![DCF 평가](docs/images/dcf-valuation.png)

### 3. 투자 뉴스 트래커
![투자 뉴스](docs/images/deal-tracker.png)

---

**작성일**: 2026-02-06
**작성자**: ValueLink Team
```

---

### 2. docs/architecture.md (아키텍처 문서) - ~500줄

**파일 위치:** `docs/architecture.md`

**구조:**
```markdown
# ValueLink 아키텍처 가이드

## 목차
1. [시스템 개요](#시스템-개요)
2. [기술 스택](#기술-스택)
3. [아키텍처 패턴](#아키텍처-패턴)
4. [데이터베이스 스키마](#데이터베이스-스키마)
5. [API 설계](#api-설계)
6. [평가 엔진 구조](#평가-엔진-구조)
7. [크롤러 구조](#크롤러-구조)
8. [스케줄러 구조](#스케줄러-구조)
9. [인증 및 권한](#인증-및-권한)
10. [보안 고려사항](#보안-고려사항)

---

## 1. 시스템 개요

ValueLink는 **AI 기반 기업가치평가 자동화 플랫폼**으로, 14단계 평가 워크플로우를 통해 고객과 회계사를 연결합니다.

**핵심 개념:**
- **Project**: 평가 의뢰 건 (1개 = 1개 기업)
- **Valuation Method**: 5가지 (DCF, Relative, Asset, Intrinsic, Tax)
- **Approval Point**: 22개 (AI 승인 포인트)
- **Role**: 3가지 (Customer, Accountant, Admin)

**시스템 흐름:**
```
고객 평가 요청
    ↓
견적 생성 (AI)
    ↓
협상 (고객 ↔ 회계사)
    ↓
문서 업로드 (고객)
    ↓
평가 실행 (회계사 + AI)
    ↓
초안 생성 (AI)
    ↓
수정 요청 (고객)
    ↓
최종 보고서 (PDF)
    ↓
완료
```

---

## 2. 기술 스택

### Frontend
- **Next.js 14**: React 프레임워크 (App Router)
- **React 18**: UI 라이브러리 (Server Components)
- **TypeScript 5.3**: 타입 안전성
- **Tailwind CSS 3.4**: 스타일링

**선택 이유:**
- Next.js App Router: SSR, RSC, 파일 기반 라우팅
- TypeScript: 런타임 에러 방지
- Tailwind CSS: 빠른 프로토타이핑

### Backend
- **Supabase**: BaaS (PostgreSQL 15 + Auth + Storage + RLS)
  - Auth: 이메일, Google, Kakao OAuth
  - Storage: 파일 업로드 (문서, 보고서)
  - RLS: 행 수준 보안 (role 기반)
- **Vercel**: Serverless 배포 (Seoul region)

**선택 이유:**
- Supabase: DB + Auth + Storage 통합, RLS 지원
- Vercel: Next.js 최적화, Edge Functions

### AI
- **Claude API (60%)**: 초안 생성, 검토
- **Gemini API (20%)**: 문서 분석
- **OpenAI API (20%)**: 재무 계산 검증

**선택 이유:**
- Claude: 긴 문맥 (200K 토큰), 한국어 성능
- Gemini: 빠른 응답, 저렴한 비용
- OpenAI: 재무 계산 정확도

### 크롤링
- **Cheerio**: HTML 파싱 (jQuery-like API)
- **node-cron**: 스케줄링 (로컬)
- **Vercel Cron**: 스케줄링 (프로덕션)

### 테스팅
- **Jest**: 단위 테스트, 통합 테스트
- **Playwright**: E2E 테스트

---

## 3. 아키텍처 패턴

### 3.1 레이어 구조

```
┌─────────────────────────────────────────────────────────┐
│  Presentation Layer (UI)                                │
│  - Next.js Pages (app/)                                 │
│  - React Components (components/)                       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Application Layer (Business Logic)                     │
│  - API Routes (app/api/)                                │
│  - Orchestrator (lib/valuation/orchestrator.ts)         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Domain Layer (Core Logic)                              │
│  - Valuation Engines (lib/valuation/engines/)           │
│  - Financial Math (lib/valuation/financial-math.ts)     │
│  - Crawlers (lib/crawler/)                              │
│  - Scheduler (lib/scheduler/)                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Infrastructure Layer (External Services)               │
│  - Supabase (lib/supabase/)                             │
│  - AI APIs (lib/ai/)                                    │
│  - External Integrations (lib/integrations/)            │
└─────────────────────────────────────────────────────────┘
```

### 3.2 디자인 패턴

#### Orchestrator 패턴
- **목적**: 5개 평가 엔진을 통합 관리
- **파일**: `lib/valuation/orchestrator.ts`
- **책임**:
  - 엔진 등록 (registerEngine)
  - 엔진 선택 (method 기반)
  - 실행 및 결과 반환 (executeValuation)

```typescript
class ValuationOrchestrator {
  private engines: Map<ValuationMethod, ValuationEngine>

  registerEngine(method: ValuationMethod, engine: ValuationEngine)
  async executeValuation(input: ValuationInput): Promise<ValuationResult>
}
```

#### Abstract Class 패턴
- **목적**: 공통 인터페이스 정의
- **예시**: BaseCrawler, ValuationEngine

```typescript
abstract class BaseCrawler {
  protected config: CrawlerConfig
  abstract crawl(): Promise<CrawlResult[]>
  protected async fetchHTML(url: string): Promise<string> { /* 공통 구현 */ }
}
```

#### Singleton 패턴
- **목적**: 전역 인스턴스 관리
- **예시**: orchestrator, crawlerManager, taskScheduler, newsParser

```typescript
export const orchestrator = new ValuationOrchestrator()
export const crawlerManager = new CrawlerManager()
```

#### Strategy 패턴
- **목적**: 알고리즘 교체 가능
- **예시**: 5개 평가 엔진 (DCF, Relative, Asset, Intrinsic, Tax)

---

## 4. 데이터베이스 스키마

### 4.1 핵심 테이블 (12개)

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|----------|
| **users** | 사용자 | id, email, role, full_name |
| **projects** | 평가 프로젝트 | id, company_name, status, valuation_method |
| **quotes** | 견적 | id, project_id, amount, status |
| **negotiations** | 협상 | id, project_id, quote_id, status |
| **documents** | 문서 | id, project_id, file_path, document_type |
| **approval_points** | AI 승인 | id, project_id, approval_type, status |
| **valuation_results** | 평가 결과 | id, project_id, method, equity_value |
| **drafts** | 초안 | id, project_id, content, version |
| **revisions** | 수정 요청 | id, draft_id, customer_comments |
| **reports** | 최종 보고서 | id, project_id, file_path, status |
| **investment_tracker** | 투자 뉴스 | id, company_name, investors, amount |
| **matching_requests** | 매칭 요청 | id, user_id, company_info, status |

### 4.2 RLS (Row Level Security) 정책

**users 테이블:**
```sql
-- 사용자는 자신의 정보만 조회 가능
CREATE POLICY "users_select_own" ON users
  FOR SELECT USING (auth.uid() = id);

-- 사용자는 자신의 정보만 수정 가능
CREATE POLICY "users_update_own" ON users
  FOR UPDATE USING (auth.uid() = id);
```

**projects 테이블:**
```sql
-- 고객은 자신의 프로젝트만 조회
CREATE POLICY "projects_select_customer" ON projects
  FOR SELECT USING (
    customer_id = auth.uid()
    OR assigned_accountant_id = auth.uid()
    OR (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- 회계사는 배정된 프로젝트만 수정
CREATE POLICY "projects_update_accountant" ON projects
  FOR UPDATE USING (
    assigned_accountant_id = auth.uid()
    OR (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );
```

**documents 테이블:**
```sql
-- 프로젝트 참여자만 문서 조회
CREATE POLICY "documents_select" ON documents
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = documents.project_id
        AND (projects.customer_id = auth.uid() OR projects.assigned_accountant_id = auth.uid())
    )
  );
```

### 4.3 트리거 (8개)

**자동 타임스탬프:**
```sql
CREATE TRIGGER update_projects_updated_at
  BEFORE UPDATE ON projects
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

**프로젝트 상태 전이:**
```sql
CREATE TRIGGER validate_project_status_transition
  BEFORE UPDATE ON projects
  FOR EACH ROW
  EXECUTE FUNCTION validate_status_transition();
```

**알림 생성:**
```sql
CREATE TRIGGER create_notification_on_quote_approval
  AFTER UPDATE ON quotes
  FOR EACH ROW
  WHEN (NEW.status = 'approved' AND OLD.status != 'approved')
  EXECUTE FUNCTION create_notification();
```

---

## 5. API 설계

### 5.1 RESTful API 규칙

**Base URL:** `/api`

**인증:** JWT 토큰 (Supabase Auth)

**요청 헤더:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### 5.2 주요 엔드포인트

#### 인증 (Auth)
```
POST   /api/auth/login              로그인
POST   /api/auth/signup             회원가입
POST   /api/auth/logout             로그아웃
GET    /api/auth/google/callback    Google OAuth 콜백
GET    /api/auth/kakao/callback     Kakao OAuth 콜백
```

#### 프로젝트 (Projects)
```
GET    /api/projects                프로젝트 목록
POST   /api/projects                프로젝트 생성
GET    /api/projects/:id            프로젝트 상세
PUT    /api/projects/:id            프로젝트 수정
DELETE /api/projects/:id            프로젝트 삭제
```

#### 견적 (Quotes)
```
POST   /api/projects/:id/quote      견적 생성
GET    /api/projects/:id/quote      견적 조회
PUT    /api/projects/:id/quote      견적 수정
```

#### 평가 (Valuation)
```
POST   /api/valuation/execute       평가 실행
GET    /api/valuation/result/:id    평가 결과 조회
POST   /api/valuation/sensitivity   민감도 분석
```

#### 스케줄러 (Scheduler)
```
GET    /api/scheduler               스케줄러 상태
POST   /api/scheduler/trigger       수동 실행
```

#### Cron Jobs
```
GET    /api/cron/weekly-collection  주간 뉴스 수집 (Vercel Cron 전용)
```

### 5.3 에러 응답 형식

```typescript
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "company_name",
        "message": "Company name is required"
      }
    ]
  }
}
```

**에러 코드:**
- `VALIDATION_ERROR`: 입력 검증 실패 (400)
- `UNAUTHORIZED`: 인증 실패 (401)
- `FORBIDDEN`: 권한 없음 (403)
- `NOT_FOUND`: 리소스 없음 (404)
- `INTERNAL_ERROR`: 서버 에러 (500)

---

## 6. 평가 엔진 구조

### 6.1 오케스트레이터

**파일:** `lib/valuation/orchestrator.ts`

```typescript
export class ValuationOrchestrator {
  private engines: Map<ValuationMethod, ValuationEngine> = new Map()

  registerEngine(method: ValuationMethod, engine: ValuationEngine): void {
    this.engines.set(method, engine)
  }

  async executeValuation(input: ValuationInput): Promise<ValuationResult> {
    // 1. 엔진 선택
    const engine = this.engines.get(input.method)

    // 2. 입력 검증
    const validation = engine.validate(input)
    if (!validation.valid) throw new Error(...)

    // 3. 평가 실행
    const result = await engine.calculate(input)

    // 4. 결과 저장
    await this.saveResult(result)

    return result
  }
}
```

### 6.2 추상 엔진 클래스

```typescript
export abstract class ValuationEngine {
  protected method: ValuationMethod

  constructor(method: ValuationMethod) {
    this.method = method
  }

  abstract calculate(input: ValuationInput): Promise<ValuationResult>
  abstract validate(input: ValuationInput): { valid: boolean; errors: string[] }

  protected async saveResult(result: ValuationResult): Promise<void> {
    // 공통 저장 로직
  }
}
```

### 6.3 DCF 엔진 (예시)

**파일:** `lib/valuation/engines/dcf-engine.ts`

```typescript
export class DCFEngine extends ValuationEngine {
  constructor() {
    super('dcf')
  }

  async calculate(input: ValuationInput): Promise<ValuationResult> {
    // 1. WACC 계산
    const wacc = calculateWACC(input.wacc_components)

    // 2. FCF 프로젝션
    const fcf_projections = input.projections.map(p => calculateFCF(p))

    // 3. Terminal Value
    const terminal_value = calculateTerminalValue(
      fcf_projections[fcf_projections.length - 1],
      input.terminal_growth_rate,
      wacc
    )

    // 4. NPV
    const pv_projections = calculateNPV(fcf_projections, wacc)
    const pv_terminal = terminal_value / Math.pow(1 + wacc, fcf_projections.length)

    // 5. Enterprise Value
    const operating_value = pv_projections + pv_terminal
    const enterprise_value = operating_value + input.non_operating_assets

    // 6. Equity Value
    const equity_value = enterprise_value - input.debt

    // 7. Value Per Share
    const value_per_share = Math.round(equity_value / input.shares_outstanding)

    return {
      method: 'dcf',
      equity_value,
      value_per_share,
      enterprise_value,
      operating_value,
      pv_projections,
      pv_terminal,
      wacc,
      // ...
    }
  }

  validate(input: ValuationInput): { valid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!input.projections || input.projections.length === 0) {
      errors.push('Projections are required')
    }

    if (!input.wacc_components) {
      errors.push('WACC components are required')
    }

    return { valid: errors.length === 0, errors }
  }
}
```

### 6.4 재무 수학 라이브러리

**파일:** `lib/valuation/financial-math.ts`

**핵심 함수:**
- `calculateWACC()`: WACC 계산 (CAPM)
- `calculateNPV()`: NPV 계산 (현재가치 합계)
- `calculateIRR()`: IRR 계산 (Newton-Raphson)
- `calculateTerminalValue()`: Terminal Value (Gordon Growth)
- `calculateFCF()`: Free Cash Flow
- `calculateDepreciation()`: 감가상각비
- `calculateWorkingCapital()`: 운전자본 변동
- `calculateBeta()`: 레버리지 베타

---

## 7. 크롤러 구조

### 7.1 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│  CrawlerManager (Singleton)                             │
│  - 6개 크롤러 등록 및 관리                                │
│  - executeAll() / executeCrawler()                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  BaseCrawler (Abstract Class)                           │
│  - fetchHTML() (retry + timeout + rate limiting)        │
│  - sleep()                                              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Site-Specific Crawlers (6개)                           │
│  - NaverCrawler, OutstandingCrawler, ...                │
│  - 사이트별 CSS 선택자                                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  NewsParser (Singleton)                                 │
│  - parseArticle() (Cheerio)                             │
│  - extractDealInfo() (Regex)                            │
└─────────────────────────────────────────────────────────┘
```

### 7.2 BaseCrawler

```typescript
export abstract class BaseCrawler {
  protected config: CrawlerConfig

  constructor(config: CrawlerConfig) {
    this.config = config
  }

  abstract crawl(): Promise<CrawlResult[]>

  protected async fetchHTML(url: string): Promise<string> {
    for (let attempt = 0; attempt < this.config.max_retries; attempt++) {
      try {
        const response = await fetch(url, {
          signal: AbortSignal.timeout(this.config.timeout_ms)
        })

        await this.sleep(this.config.rate_limit_ms)
        return await response.text()
      } catch (error) {
        // Exponential backoff
        await this.sleep(1000 * Math.pow(2, attempt))
      }
    }
    throw new Error(`Failed to fetch ${url}`)
  }

  protected sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}
```

### 7.3 사이트별 크롤러 (예시: Naver)

```typescript
export class NaverCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '네이버 뉴스',
      base_url: 'https://search.naver.com',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    const searchUrl = `${this.config.base_url}/search.naver?where=news&query=${encodeURIComponent('스타트업 투자 유치')}`
    const html = await this.fetchHTML(searchUrl)

    const $ = cheerio.load(html)
    const articleUrls: string[] = []

    $('.news_tit').each((_, elem) => {
      articleUrls.push($(elem).attr('href') || '')
    })

    const results: CrawlResult[] = []

    for (const url of articleUrls.slice(0, 10)) {
      const articleHtml = await this.fetchHTML(url)
      const parsed = newsParser.parseArticle(articleHtml, {
        title: 'h2#title_area, h3#articleTitle',
        content: '#dic_area, #articleBodyContents',
        date: '.media_end_head_info_datestamp_time, .t11'
      })

      results.push({
        url,
        title: parsed.title,
        content: parsed.content,
        published_date: parsed.published_date,
        source: this.config.site_name,
        company_name: parsed.deal_info.company_name,
        investment_stage: parsed.deal_info.investment_stage,
        investment_amount: parsed.deal_info.investment_amount,
        investors: parsed.deal_info.investors
      })
    }

    return results
  }
}
```

---

## 8. 스케줄러 구조

### 8.1 TaskScheduler

**파일:** `lib/scheduler/task-scheduler.ts`

```typescript
export class TaskScheduler {
  private tasks: Map<string, { task: ScheduledTask; job: CronJob }> = new Map()
  private running: boolean = false

  registerTask(task: ScheduledTask): void {
    const cronJob = new CronJob(
      task.schedule,  // '0 6 * * 0' (Sunday 6 AM KST)
      async () => { await this.runTask(task.id) },
      null,
      task.enabled,
      'Asia/Seoul'
    )

    this.tasks.set(task.id, { task, job: cronJob })
  }

  private async runTask(taskId: string): Promise<void> {
    const entry = this.tasks.get(taskId)
    if (!entry) return

    const { task } = entry

    // 중복 실행 방지
    if (task.status === 'running') return

    task.status = 'running'
    task.lastRun = new Date()

    try {
      await task.handler()
      task.status = 'idle'
      task.nextRun = entry.job.nextDate().toJSDate()
    } catch (error) {
      task.status = 'error'
      console.error(`Task ${taskId} failed:`, error)
    }
  }

  start(): void {
    if (this.running) return
    this.tasks.forEach(({ task, job }) => {
      if (task.enabled) job.start()
    })
    this.running = true
  }

  stop(): void {
    this.tasks.forEach(({ job }) => job.stop())
    this.running = false
  }
}
```

### 8.2 주간 수집 작업

**파일:** `lib/scheduler/tasks/weekly-collection.ts`

```typescript
export async function weeklyCollectionHandler(): Promise<void> {
  console.log('Starting weekly investment news collection...')

  const results = await crawlerManager.executeAll()

  let totalCount = 0
  for (const [siteName, articles] of results) {
    totalCount += articles.length
    console.log(`${siteName}: ${articles.length} articles`)
  }

  console.log(`Total: ${totalCount} articles collected`)
}

export function registerWeeklyCollectionTask(): void {
  taskScheduler.registerTask({
    id: 'weekly_investment_collection',
    name: 'Weekly Investment News Collection',
    schedule: '0 6 * * 0',  // 일요일 오전 6시 KST
    handler: weeklyCollectionHandler,
    enabled: true,
    status: 'idle',
    lastRun: null,
    nextRun: null
  })
}
```

### 8.3 Vercel Cron 통합

**파일:** `app/api/cron/weekly-collection/route.ts`

```typescript
export async function GET(request: Request) {
  // CRON_SECRET 검증
  const authHeader = request.headers.get('authorization')
  const token = authHeader?.replace('Bearer ', '')

  if (token !== process.env.CRON_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    await weeklyCollectionHandler()
    return NextResponse.json({ success: true })
  } catch (error) {
    return NextResponse.json({ error: 'Failed' }, { status: 500 })
  }
}
```

**vercel.json:**
```json
{
  "crons": [{
    "path": "/api/cron/weekly-collection",
    "schedule": "0 6 * * 0"
  }]
}
```

---

## 9. 인증 및 권한

### 9.1 역할 (Role)

| Role | 설명 | 권한 |
|------|------|------|
| **customer** | 고객 | 프로젝트 생성, 견적 확인, 문서 업로드, 초안 검토 |
| **accountant** | 회계사 | 견적 작성, 평가 실행, 초안 작성, 보고서 작성 |
| **admin** | 관리자 | 모든 프로젝트 조회, 사용자 관리, 시스템 설정 |

### 9.2 인증 흐름

#### 이메일 로그인
```
1. 사용자가 이메일/비밀번호 입력
2. Supabase Auth에 전송
3. JWT 토큰 발급
4. 클라이언트에 저장 (localStorage)
5. 이후 요청에 Authorization 헤더로 포함
```

#### OAuth (Google, Kakao)
```
1. 사용자가 "Google로 로그인" 클릭
2. Google 인증 페이지로 리다이렉트
3. 사용자 승인
4. /api/auth/google/callback으로 리다이렉트
5. Supabase가 토큰 발급
6. 클라이언트에 저장
```

### 9.3 권한 체크

**미들웨어:** `lib/middleware/auth.ts`

```typescript
export async function requireAuth(
  req: NextRequest,
  allowedRoles?: Role[]
): Promise<{ user: User; error?: never } | { user?: never; error: string }> {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')

  if (!token) {
    return { error: 'Unauthorized' }
  }

  const { data: { user }, error } = await supabase.auth.getUser(token)

  if (error || !user) {
    return { error: 'Unauthorized' }
  }

  // Role 체크
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return { error: 'Forbidden' }
  }

  return { user }
}
```

**사용 예시:**
```typescript
export async function GET(request: NextRequest) {
  const { user, error } = await requireAuth(request, ['customer', 'accountant'])

  if (error) {
    return NextResponse.json({ error }, { status: 401 })
  }

  // ...
}
```

---

## 10. 보안 고려사항

### 10.1 인증 보안
- ✅ JWT 토큰 (Supabase Auth)
- ✅ HTTPS only
- ✅ CORS 제한 (허용된 도메인만)
- ✅ Rate Limiting (Vercel)

### 10.2 데이터 보안
- ✅ RLS (Row Level Security) - 모든 테이블
- ✅ 암호화된 비밀번호 (bcrypt)
- ✅ 환경 변수로 Secrets 관리
- ✅ Secrets 절대 커밋 금지 (.gitignore)

### 10.3 API 보안
- ✅ CRON_SECRET (Vercel Cron 인증)
- ✅ Input Validation (Zod)
- ✅ SQL Injection 방지 (Parameterized Queries)
- ✅ XSS 방지 (React auto-escape)

### 10.4 파일 보안
- ✅ Supabase Storage 권한 정책
- ✅ 파일 타입 검증 (PDF, XLSX, DOCX만 허용)
- ✅ 파일 크기 제한 (10MB)
- ✅ 바이러스 스캔 (향후 추가 예정)

### 10.5 보안 헤더

**vercel.json:**
```json
{
  "headers": [{
    "source": "/(.*)",
    "headers": [
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "X-Frame-Options", "value": "DENY" },
      { "key": "X-XSS-Protection", "value": "1; mode=block" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
      { "key": "Permissions-Policy", "value": "geolocation=(), microphone=(), camera=()" }
    ]
  }]
}
```

---

**작성일**: 2026-02-06
**작성자**: ValueLink Team
```

---

### 3. docs/maintenance-guide.md (유지보수 가이드) - ~350줄

**파일 위치:** `docs/maintenance-guide.md`

**구조:**
```markdown
# ValueLink 유지보수 가이드

## 목차
1. [일상적 점검 항목](#일상적-점검-항목)
2. [데이터베이스 관리](#데이터베이스-관리)
3. [크롤러 관리](#크롤러-관리)
4. [로그 모니터링](#로그-모니터링)
5. [백업 및 복구](#백업-및-복구)
6. [성능 최적화](#성능-최적화)
7. [보안 점검](#보안-점검)
8. [업데이트 절차](#업데이트-절차)

---

## 1. 일상적 점검 항목

### 1.1 매일 확인 (자동화 권장)

**시스템 상태:**
```bash
# Vercel 배포 상태
vercel status

# Supabase DB 상태
npx supabase db status

# 최근 에러 로그 (Vercel Dashboard)
# Settings → Logs → Filter by Error
```

**크롤러 실행 기록:**
```sql
-- 최근 7일간 수집 현황
SELECT
  DATE(created_at) as date,
  COUNT(*) as articles_count,
  COUNT(DISTINCT company_name) as companies_count
FROM investment_tracker
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

**사용자 활동:**
```sql
-- 오늘 생성된 프로젝트
SELECT COUNT(*) FROM projects WHERE DATE(created_at) = CURRENT_DATE;

-- 오늘 가입한 사용자
SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE;
```

### 1.2 주간 확인

**성능 메트릭:**
- Page Load Time: < 3초
- API Response Time: < 1초
- DCF Calculation Time: < 5초
- Crawler Execution Time: < 60초

**데이터베이스 크기:**
```sql
-- 테이블별 크기 확인
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Storage 사용량:**
```sql
-- Supabase Storage 사용량
SELECT
  bucket_id,
  COUNT(*) as files_count,
  SUM(metadata->>'size')::bigint as total_bytes,
  pg_size_pretty(SUM(metadata->>'size')::bigint) as total_size
FROM storage.objects
GROUP BY bucket_id;
```

### 1.3 월간 확인

**보안 점검:**
- [ ] 의존성 보안 취약점 스캔 (`npm audit`)
- [ ] RLS 정책 검토
- [ ] 사용자 권한 검토
- [ ] 환경 변수 로테이션

**비즈니스 메트릭:**
```sql
-- 월간 통계
SELECT
  COUNT(DISTINCT customer_id) as active_customers,
  COUNT(*) as total_projects,
  AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completion_rate,
  AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400) as avg_days_to_complete
FROM projects
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);
```

---

## 2. 데이터베이스 관리

### 2.1 인덱스 최적화

**느린 쿼리 확인:**
```sql
-- Supabase Dashboard → Database → Query Performance
-- 실행 시간 1초 이상인 쿼리 확인
```

**인덱스 추가 (예시):**
```sql
-- projects 테이블 - status 및 created_at 자주 조회
CREATE INDEX idx_projects_status_created ON projects(status, created_at DESC);

-- investment_tracker - company_name 검색
CREATE INDEX idx_investment_tracker_company ON investment_tracker(company_name);
```

### 2.2 데이터 정리

**오래된 임시 데이터 삭제:**
```sql
-- 6개월 이상 된 'draft' 상태 프로젝트 삭제
DELETE FROM projects
WHERE status = 'draft'
  AND created_at < NOW() - INTERVAL '6 months';

-- 1년 이상 된 로그 삭제
DELETE FROM audit_logs
WHERE created_at < NOW() - INTERVAL '1 year';
```

**중복 데이터 확인:**
```sql
-- 중복 투자 뉴스 기사
SELECT company_name, COUNT(*) as duplicates
FROM investment_tracker
GROUP BY company_name, investment_amount, published_date
HAVING COUNT(*) > 1;
```

### 2.3 테이블 VACUUM

**자동 VACUUM 설정 확인:**
```sql
-- autovacuum 설정 확인
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;
```

**수동 VACUUM (필요 시):**
```sql
-- 특정 테이블 VACUUM
VACUUM ANALYZE projects;
VACUUM ANALYZE investment_tracker;
```

---

## 3. 크롤러 관리

### 3.1 크롤러 상태 점검

**수동 실행 테스트:**
```bash
# 로컬 환경에서 크롤러 테스트
npm run dev

# 브라우저에서:
# http://localhost:3000/api/scheduler
# http://localhost:3000/api/scheduler/trigger (POST)
```

**수집 결과 확인:**
```sql
-- 사이트별 최근 수집 현황
SELECT
  source,
  COUNT(*) as articles_count,
  MAX(published_date) as latest_article
FROM investment_tracker
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY source
ORDER BY articles_count DESC;

-- 0건인 사이트 = 크롤러 문제 가능성
```

### 3.2 크롤러 실패 원인 파악

**일반적 실패 원인:**
1. **CSS 선택자 변경**: 사이트 리뉴얼
2. **Rate Limiting**: 너무 빠른 요청
3. **타임아웃**: 느린 응답
4. **403/404 에러**: IP 차단 또는 URL 변경

**디버깅 방법:**
```typescript
// lib/crawler/sites/naver-crawler.ts 수정
async crawl(): Promise<CrawlResult[]> {
  console.log('Starting Naver crawl...')

  const html = await this.fetchHTML(searchUrl)
  console.log('HTML length:', html.length)

  const $ = cheerio.load(html)
  console.log('Found articles:', $('.news_tit').length)

  // ...
}
```

### 3.3 CSS 선택자 업데이트

**사이트 구조 변경 시:**
1. 브라우저에서 사이트 열기
2. F12 → Elements 탭
3. 기사 제목/본문 우클릭 → Copy selector
4. 크롤러 파일 수정

```typescript
// 예시: 네이버 뉴스 선택자 변경
// 변경 전
const title = $('h2#title_area').text()

// 변경 후 (사이트 리뉴얼 대응)
const title = $('h2#title_area, h2.media_end_head_headline').text()
```

---

## 4. 로그 모니터링

### 4.1 Vercel 로그

**위치:** Vercel Dashboard → Logs

**필터 기준:**
- **Error**: 에러만 표시
- **Path**: 특정 API 경로 (`/api/valuation/*`)
- **Time Range**: 최근 1시간, 24시간, 7일

**주요 에러 패턴:**
```
TypeError: Cannot read property 'x' of undefined
→ null 체크 누락

TimeoutError: Request timeout
→ 외부 API 응답 지연

PGRST116: relation "projects" not found
→ 데이터베이스 연결 실패
```

### 4.2 Supabase 로그

**위치:** Supabase Dashboard → Logs

**주요 확인 사항:**
- **API Logs**: 비정상적으로 많은 요청 (DDoS?)
- **Database Logs**: Slow queries (1초 이상)
- **Auth Logs**: 로그인 실패 횟수 (brute force?)

### 4.3 커스텀 로깅

**로깅 라이브러리 (권장):**
```typescript
// lib/utils/logger.ts
export function logError(error: Error, context?: Record<string, any>) {
  console.error('[ERROR]', {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString()
  })

  // 프로덕션에서는 외부 로깅 서비스로 전송
  // (예: Sentry, Datadog, LogRocket)
}
```

---

## 5. 백업 및 복구

### 5.1 데이터베이스 백업

**Supabase 자동 백업:**
- 매일 자동 백업 (Supabase Pro 플랜 이상)
- 최근 7일 보관
- Dashboard → Database → Backups

**수동 백업 (로컬):**
```bash
# pg_dump로 백업
npx supabase db dump > backup_$(date +%Y%m%d).sql

# 특정 테이블만 백업
npx supabase db dump -t projects > projects_backup.sql
```

**S3에 백업 (자동화):**
```bash
# GitHub Actions에 추가
# .github/workflows/backup.yml
name: Daily Database Backup
on:
  schedule:
    - cron: '0 3 * * *'  # 매일 오전 3시 KST
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npx supabase db dump > backup.sql
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      - run: aws s3 cp backup.sql s3://valuelink-backups/$(date +%Y%m%d).sql
```

### 5.2 데이터베이스 복구

**Supabase Dashboard에서 복구:**
1. Dashboard → Database → Backups
2. 복구할 백업 선택
3. Restore 버튼 클릭
4. 확인 (기존 데이터 덮어쓰기 주의!)

**로컬 백업 파일로 복구:**
```bash
# 백업 파일 복구
psql -h db.your-project.supabase.co -U postgres -d postgres < backup_20260206.sql
```

### 5.3 Storage 백업

**Supabase Storage 다운로드:**
```typescript
// scripts/backup-storage.ts
import { createClient } from '@supabase/supabase-js'
import * as fs from 'fs'

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_KEY!)

async function backupBucket(bucketName: string) {
  const { data: files } = await supabase.storage.from(bucketName).list()

  for (const file of files || []) {
    const { data } = await supabase.storage.from(bucketName).download(file.name)
    fs.writeFileSync(`./backups/${bucketName}/${file.name}`, Buffer.from(await data!.arrayBuffer()))
  }
}

backupBucket('documents')
backupBucket('reports')
```

---

## 6. 성능 최적화

### 6.1 데이터베이스 쿼리 최적화

**N+1 쿼리 방지:**
```typescript
// ❌ Bad: N+1 쿼리
const projects = await supabase.from('projects').select('*')
for (const project of projects.data) {
  const { data: documents } = await supabase
    .from('documents')
    .select('*')
    .eq('project_id', project.id)
}

// ✅ Good: JOIN 사용
const { data: projects } = await supabase
  .from('projects')
  .select(`
    *,
    documents(*)
  `)
```

**인덱스 활용:**
```sql
-- 복합 인덱스 생성
CREATE INDEX idx_projects_customer_status ON projects(customer_id, status);

-- 인덱스 사용 확인
EXPLAIN ANALYZE
SELECT * FROM projects WHERE customer_id = 'xxx' AND status = 'active';
```

### 6.2 프론트엔드 최적화

**이미지 최적화:**
```tsx
// next/image 사용
import Image from 'next/image'

<Image
  src="/logo.png"
  width={200}
  height={50}
  alt="ValueLink"
  priority  // LCP 개선
/>
```

**코드 스플리팅:**
```tsx
// Dynamic Import
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
  loading: () => <div>Loading...</div>,
  ssr: false  // 클라이언트에서만 로드
})
```

**캐싱:**
```typescript
// API Route에서 캐싱
export async function GET(request: Request) {
  return NextResponse.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400'
    }
  })
}
```

### 6.3 크롤러 최적화

**병렬 처리:**
```typescript
// 순차 실행 (느림)
for (const url of urls) {
  await fetchHTML(url)
}

// 병렬 실행 (빠름)
await Promise.all(urls.map(url => fetchHTML(url)))
```

**Rate Limiting 조정:**
```typescript
// 사이트가 느리면 interval 증가
const config = {
  rate_limit_ms: 2000,  // 1초 → 2초
  timeout_ms: 20000,    // 10초 → 20초
}
```

---

## 7. 보안 점검

### 7.1 의존성 보안 취약점

**매주 실행:**
```bash
# npm audit
npm audit

# 취약점 자동 수정 (가능한 경우)
npm audit fix

# 강제 수정 (breaking change 가능)
npm audit fix --force
```

**Dependabot 활성화 (GitHub):**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
```

### 7.2 RLS 정책 검토

**정기적 확인 (월 1회):**
```sql
-- 모든 RLS 정책 조회
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'public';

-- RLS 비활성화된 테이블 확인 (위험!)
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename NOT IN (
    SELECT tablename FROM pg_policies WHERE schemaname = 'public'
  );
```

### 7.3 환경 변수 로테이션

**3개월마다:**
- Supabase Service Role Key 재생성
- AI API Key 로테이션
- CRON_SECRET 변경
- OAuth Client Secret 변경

**절차:**
1. 새 키 생성
2. Vercel 환경 변수 업데이트
3. 재배포
4. 이전 키 비활성화

---

## 8. 업데이트 절차

### 8.1 의존성 업데이트

**Minor/Patch 업데이트 (안전):**
```bash
# package.json 업데이트
npm update

# 특정 패키지 업데이트
npm update next react react-dom
```

**Major 업데이트 (주의):**
```bash
# 최신 버전 확인
npm outdated

# 하나씩 업데이트 + 테스트
npm install next@latest
npm test
npm run build
```

### 8.2 Next.js 업데이트

**공식 가이드 확인:**
- https://nextjs.org/docs/upgrading

**일반 절차:**
1. Breaking Changes 확인
2. 로컬에서 업데이트
3. 테스트 실행
4. 빌드 확인
5. Staging 배포
6. Production 배포

### 8.3 Supabase 마이그레이션

**스키마 변경 시:**
```bash
# 마이그레이션 파일 생성
npx supabase migration new add_new_column

# SQL 작성
# migrations/20260206123456_add_new_column.sql
ALTER TABLE projects ADD COLUMN new_field TEXT;

# 마이그레이션 실행
npx supabase db push
```

---

**작성일**: 2026-02-06
**작성자**: ValueLink Team
```

---

### 4. docs/troubleshooting.md (문제 해결 가이드) - ~400줄

**파일 위치:** `docs/troubleshooting.md`

**구조:**
```markdown
# ValueLink 문제 해결 가이드

## 목차
1. [일반적인 문제](#일반적인-문제)
2. [빌드 에러](#빌드-에러)
3. [런타임 에러](#런타임-에러)
4. [데이터베이스 에러](#데이터베이스-에러)
5. [인증 에러](#인증-에러)
6. [크롤러 에러](#크롤러-에러)
7. [배포 문제](#배포-문제)
8. [성능 문제](#성능-문제)

---

## 1. 일반적인 문제

### 문제: 로컬 서버가 시작되지 않음

**증상:**
```
Error: Cannot find module '@/lib/supabase/client'
```

**원인:** TypeScript path alias 미설정

**해결:**
```bash
# tsconfig.json 확인
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}

# 의존성 재설치
rm -rf node_modules package-lock.json
npm install
```

---

### 문제: 환경 변수가 undefined

**증상:**
```typescript
console.log(process.env.NEXT_PUBLIC_SUPABASE_URL)  // undefined
```

**원인:** 환경 변수 파일 누락 또는 prefix 오류

**해결:**
```bash
# 1. .env.local 파일 존재 확인
ls -la .env.local

# 2. NEXT_PUBLIC_ prefix 확인
# ✅ Good: NEXT_PUBLIC_SUPABASE_URL (클라이언트에서 접근)
# ❌ Bad: SUPABASE_URL (서버에서만 접근)

# 3. 서버 재시작
npm run dev
```

---

### 문제: Supabase 연결 실패

**증상:**
```
Error: Invalid Supabase URL
```

**원인:** URL 형식 오류 또는 잘못된 키

**해결:**
```typescript
// lib/supabase/client.ts 확인
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

// URL 형식: https://your-project.supabase.co (마지막 슬래시 없음)
// Key 형식: eyJhbGciOi... (매우 긴 문자열)

// 테스트 코드
console.log('Supabase URL:', supabaseUrl)
console.log('Key length:', supabaseKey?.length)  // 100자 이상이어야 정상
```

---

## 2. 빌드 에러

### 문제: TypeScript 컴파일 에러

**증상:**
```
Type 'string | undefined' is not assignable to type 'string'
```

**원인:** Optional 타입 처리 누락

**해결:**
```typescript
// ❌ Bad
const url: string = process.env.NEXT_PUBLIC_SUPABASE_URL

// ✅ Good (Option 1: Non-null assertion)
const url = process.env.NEXT_PUBLIC_SUPABASE_URL!

// ✅ Good (Option 2: Default value)
const url = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://default.supabase.co'

// ✅ Good (Option 3: Throw error)
if (!process.env.NEXT_PUBLIC_SUPABASE_URL) {
  throw new Error('NEXT_PUBLIC_SUPABASE_URL is required')
}
const url = process.env.NEXT_PUBLIC_SUPABASE_URL
```

---

### 문제: Module not found 에러

**증상:**
```
Module not found: Can't resolve '@/components/ui/button'
```

**원인:** 파일 경로 오류 또는 파일 미생성

**해결:**
```bash
# 1. 파일 존재 확인
ls -la components/ui/button.tsx

# 2. tsconfig.json의 paths 확인
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}

# 3. VS Code 재시작 (TypeScript 서버 재시작)
# Cmd+Shift+P → "TypeScript: Restart TS Server"
```

---

### 문제: Next.js 빌드 실패

**증상:**
```
Error: Page build optimization failed
```

**원인:** 서버/클라이언트 컴포넌트 혼용 오류

**해결:**
```typescript
// ❌ Bad: 서버 컴포넌트에서 useState 사용
export default function Page() {
  const [state, setState] = useState(0)  // Error!
  return <div>{state}</div>
}

// ✅ Good: 클라이언트 컴포넌트로 명시
'use client'

export default function Page() {
  const [state, setState] = useState(0)
  return <div>{state}</div>
}
```

---

## 3. 런타임 에러

### 문제: Hydration 에러

**증상:**
```
Warning: Text content did not match. Server: "Hello" Client: "Hi"
```

**원인:** SSR과 클라이언트 렌더링 결과 불일치

**해결:**
```typescript
// ❌ Bad: Date.now()는 SSR과 클라이언트에서 다름
export default function Page() {
  return <div>{Date.now()}</div>
}

// ✅ Good: useEffect로 클라이언트에서만 렌더링
'use client'

export default function Page() {
  const [time, setTime] = useState<number | null>(null)

  useEffect(() => {
    setTime(Date.now())
  }, [])

  if (time === null) return <div>Loading...</div>
  return <div>{time}</div>
}
```

---

### 문제: Supabase RLS 에러

**증상:**
```
Error: new row violates row-level security policy for table "projects"
```

**원인:** RLS 정책이 INSERT를 차단

**해결:**
```sql
-- 1. RLS 정책 확인
SELECT * FROM pg_policies WHERE tablename = 'projects';

-- 2. INSERT 정책 추가
CREATE POLICY "projects_insert_customer" ON projects
  FOR INSERT
  WITH CHECK (
    customer_id = auth.uid()
  );

-- 3. Service Role Key 사용 (RLS 우회 - 주의!)
-- lib/supabase/server.ts
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!  // Service Role Key
)
```

---

### 문제: CORS 에러

**증상:**
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**원인:** Supabase CORS 설정 또는 외부 API CORS

**해결:**
```typescript
// Supabase는 기본적으로 CORS 허용됨
// 문제가 있다면 Supabase Dashboard → Settings → API → CORS

// 외부 API 호출 시: 서버에서 proxy
// app/api/proxy/route.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const url = searchParams.get('url')

  const response = await fetch(url!)
  const data = await response.json()

  return NextResponse.json(data)
}

// 클라이언트에서 호출
fetch('/api/proxy?url=https://external-api.com/data')
```

---

## 4. 데이터베이스 에러

### 문제: Connection timeout

**증상:**
```
Error: Connection to database timed out
```

**원인:** DB 과부하 또는 네트워크 문제

**해결:**
```typescript
// 1. Connection Pooling 설정
// Supabase는 기본적으로 pooling 지원

// 2. Timeout 증가
const { data, error } = await supabase
  .from('projects')
  .select('*')
  .abortSignal(AbortSignal.timeout(30000))  // 30초

// 3. Supabase Dashboard → Database → Connection Pooler
// Transaction Mode → Session Mode 변경
```

---

### 문제: Slow query

**증상:**
API 응답이 5초 이상 걸림

**원인:** 인덱스 누락 또는 비효율적 쿼리

**해결:**
```sql
-- 1. Slow query 확인
-- Supabase Dashboard → Database → Query Performance

-- 2. EXPLAIN ANALYZE 실행
EXPLAIN ANALYZE
SELECT * FROM projects WHERE customer_id = 'xxx';

-- 3. 인덱스 추가
CREATE INDEX idx_projects_customer ON projects(customer_id);

-- 4. 쿼리 최적화
-- ❌ Bad: 불필요한 JOIN
SELECT * FROM projects
JOIN documents ON documents.project_id = projects.id;

-- ✅ Good: 필요한 컬럼만
SELECT projects.id, projects.company_name
FROM projects;
```

---

### 문제: Deadlock

**증상:**
```
Error: deadlock detected
```

**원인:** 동시 업데이트 시 Lock 충돌

**해결:**
```typescript
// Row Lock 사용
const { data, error } = await supabase
  .rpc('update_project_with_lock', {
    project_id: 'xxx',
    new_status: 'active'
  })

// SQL Function
CREATE OR REPLACE FUNCTION update_project_with_lock(
  project_id UUID,
  new_status TEXT
)
RETURNS VOID AS $$
BEGIN
  UPDATE projects
  SET status = new_status
  WHERE id = project_id
  FOR UPDATE;  -- Row Lock
END;
$$ LANGUAGE plpgsql;
```

---

## 5. 인증 에러

### 문제: JWT expired

**증상:**
```
Error: JWT expired
```

**원인:** Access Token 만료 (기본 1시간)

**해결:**
```typescript
// lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  {
    auth: {
      autoRefreshToken: true,  // 자동 갱신
      persistSession: true,
      detectSessionInUrl: true
    }
  }
)

// 수동 갱신
const { data, error } = await supabase.auth.refreshSession()
```

---

### 문제: OAuth 리다이렉트 실패

**증상:**
Google 로그인 후 에러 페이지

**원인:** Redirect URL 미설정

**해결:**
```bash
# Supabase Dashboard → Authentication → URL Configuration
# Redirect URLs에 추가:
http://localhost:3000/api/auth/google/callback  # 로컬
https://valuelink.vercel.app/api/auth/google/callback  # 프로덕션
```

---

### 문제: 세션이 유지되지 않음

**증상:**
새로고침하면 로그아웃됨

**원인:** 쿠키 설정 오류

**해결:**
```typescript
// middleware.ts 추가
import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          request.cookies.set({ name, value, ...options })
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          })
          response.cookies.set({ name, value, ...options })
        },
        remove(name: string, options: CookieOptions) {
          request.cookies.set({ name, value: '', ...options })
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          })
          response.cookies.set({ name, value: '', ...options })
        },
      },
    }
  )

  await supabase.auth.getSession()

  return response
}
```

---

## 6. 크롤러 에러

### 문제: 크롤러가 0건 수집

**증상:**
```typescript
console.log(results.length)  // 0
```

**원인:** CSS 선택자 변경 또는 사이트 차단

**해결:**
```typescript
// 1. 브라우저에서 사이트 열기
// 2. F12 → Network 탭 → Fetch/XHR 확인
// 3. 403/429 에러 → IP 차단

// 4. CSS 선택자 확인
const $ = cheerio.load(html)
console.log('HTML length:', html.length)
console.log('Found elements:', $('.news_tit').length)

// 5. 선택자 업데이트
// lib/crawler/sites/naver-crawler.ts
const title = $('h2#title_area, h2.new-selector').text()
```

---

### 문제: Timeout 에러

**증상:**
```
Error: Request timeout after 10000ms
```

**원인:** 사이트 응답 느림

**해결:**
```typescript
// lib/crawler/base-crawler.ts
export abstract class BaseCrawler {
  protected config: CrawlerConfig = {
    timeout_ms: 20000,  // 10초 → 20초
    max_retries: 5,     // 3회 → 5회
    rate_limit_ms: 2000  // 1초 → 2초
  }
}
```

---

### 문제: Rate limiting (429 에러)

**증상:**
```
Error: 429 Too Many Requests
```

**원인:** 너무 빠른 요청

**해결:**
```typescript
// 1. Rate limiting 증가
const config = {
  rate_limit_ms: 3000  // 2초 → 3초
}

// 2. Exponential backoff
protected async fetchHTML(url: string): Promise<string> {
  for (let attempt = 0; attempt < this.config.max_retries; attempt++) {
    try {
      const response = await fetch(url)

      if (response.status === 429) {
        await this.sleep(5000 * Math.pow(2, attempt))  // 5초, 10초, 20초...
        continue
      }

      return await response.text()
    } catch (error) {
      // ...
    }
  }
}
```

---

## 7. 배포 문제

### 문제: Vercel 빌드 실패

**증상:**
```
Error: Command "npm run build" exited with 1
```

**원인:** TypeScript 에러 또는 환경 변수 누락

**해결:**
```bash
# 1. 로컬에서 빌드 테스트
npm run build

# 2. TypeScript 체크
npm run type-check

# 3. Vercel 환경 변수 확인
# Vercel Dashboard → Settings → Environment Variables
# .env.local의 모든 변수 추가

# 4. 빌드 로그 확인
# Vercel Dashboard → Deployments → 실패한 빌드 클릭
```

---

### 문제: Vercel Cron 작동 안 함

**증상:**
주간 뉴스 수집이 자동으로 실행되지 않음

**원인:** CRON_SECRET 미설정 또는 Cron 미활성화

**해결:**
```bash
# 1. vercel.json 확인
{
  "crons": [{
    "path": "/api/cron/weekly-collection",
    "schedule": "0 6 * * 0"
  }]
}

# 2. CRON_SECRET 환경 변수 추가
# Vercel Dashboard → Settings → Environment Variables
# CRON_SECRET=random-secret-string

# 3. Vercel Dashboard → Cron Jobs 탭
# "weekly-collection" 작업 확인

# 4. 수동 테스트
curl https://your-domain.vercel.app/api/cron/weekly-collection \
  -H "Authorization: Bearer your-secret"
```

---

### 문제: 환경 변수가 프로덕션에서 undefined

**증상:**
로컬에서는 작동하지만 배포 후 에러

**원인:** Vercel 환경 변수 미설정

**해결:**
```bash
# Vercel CLI로 환경 변수 설정
vercel env add ANTHROPIC_API_KEY production
# 값 입력: sk-ant-xxx

# 또는 Dashboard에서 설정
# Settings → Environment Variables
# Name: ANTHROPIC_API_KEY
# Value: sk-ant-xxx
# Environment: Production
```

---

## 8. 성능 문제

### 문제: 페이지 로딩 느림 (5초 이상)

**원인 및 해결:**

**1. 이미지 최적화**
```tsx
// ❌ Bad: 일반 <img> 태그
<img src="/large-image.jpg" />

// ✅ Good: next/image
import Image from 'next/image'

<Image
  src="/large-image.jpg"
  width={800}
  height={600}
  alt="..."
  priority  // LCP 개선
/>
```

**2. 번들 크기 줄이기**
```bash
# 번들 분석
npm run build
# .next/analyze/client.html 확인

# 큰 라이브러리 제거 또는 대체
# lodash → lodash-es (tree-shaking)
# moment → date-fns (가볍고 빠름)
```

**3. 서버 컴포넌트 활용**
```typescript
// ✅ Good: 서버 컴포넌트 (기본)
export default async function Page() {
  const { data } = await supabase.from('projects').select('*')
  return <div>{data.length}</div>
}

// 클라이언트 번들에 Supabase 코드 포함 X
```

**4. Streaming**
```tsx
// app/projects/page.tsx
export default function ProjectsPage() {
  return (
    <Suspense fallback={<Loading />}>
      <ProjectList />
    </Suspense>
  )
}

async function ProjectList() {
  const { data } = await supabase.from('projects').select('*')
  return <ul>{data.map(...)}</ul>
}
```

---

### 문제: API 응답 느림 (3초 이상)

**원인 및 해결:**

**1. DB 쿼리 최적화 (위 섹션 4 참조)**

**2. 캐싱**
```typescript
// app/api/projects/route.ts
export async function GET(request: Request) {
  const { data } = await supabase.from('projects').select('*')

  return NextResponse.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300'
    }
  })
}
```

**3. 병렬 요청**
```typescript
// ❌ Bad: 순차 요청 (느림)
const projects = await supabase.from('projects').select('*')
const users = await supabase.from('users').select('*')

// ✅ Good: 병렬 요청 (빠름)
const [projectsResult, usersResult] = await Promise.all([
  supabase.from('projects').select('*'),
  supabase.from('users').select('*')
])
```

---

### 문제: DCF 계산이 10초 이상 걸림

**원인:** IRR 계산(Newton-Raphson)의 과도한 반복

**해결:**
```typescript
// lib/valuation/financial-math.ts
export function calculateIRR(
  cash_flows: number[],
  initial_guess: number = 0.1,
  max_iterations: number = 100,  // 1000 → 100
  tolerance: number = 0.001      // 0.0001 → 0.001
): number | null {
  // ...
}
```

---

**작성일**: 2026-02-06
**작성자**: ValueLink Team
```

---

## 생성/수정 파일

| 파일 | 설명 | 예상 줄 수 |
|------|------|----------|
| `README.md` | 프로젝트 개요 및 설치 가이드 | ~400줄 |
| `docs/architecture.md` | 아키텍처 문서 | ~500줄 |
| `docs/maintenance-guide.md` | 유지보수 가이드 | ~350줄 |
| `docs/troubleshooting.md` | 문제 해결 가이드 | ~400줄 |

**총 ~1,650줄**

---

## 기술 스택

- **문서 형식**: Markdown
- **구조**: GitHub README 표준 + Docs 폴더
- **이미지**: 스크린샷 (docs/images/)
- **코드 블록**: Syntax Highlighting

---

## 완료 기준

### Must Have (필수)
- [ ] README.md 작성 완료 (~400줄)
- [ ] architecture.md 작성 완료 (~500줄)
- [ ] maintenance-guide.md 작성 완료 (~350줄)
- [ ] troubleshooting.md 작성 완료 (~400줄)
- [ ] 모든 문서에 목차(TOC) 포함
- [ ] 코드 예시 포함 (실행 가능한 코드)
- [ ] 명확한 섹션 구분

### Verification (검증)
- [ ] 모든 링크 작동 확인
- [ ] 코드 예시 문법 오류 없음
- [ ] Markdown 렌더링 확인

### Nice to Have (권장)
- [ ] 스크린샷 추가 (docs/images/)
- [ ] 다이어그램 추가 (Mermaid)
- [ ] FAQ 섹션

---

## 참조

**기존 프로토타입:**
- `Valuation_Company/WHITE_PAPER_v1.0.md` - 전체 시스템 개요
- `Valuation_Company/플랫폼개발계획/valuation.ai.kr_홈페이지_개발계획서.md` - 사업 계획
- `Valuation_Company/valuation-platform/ARCHITECTURE.md` - 기존 아키텍처 문서

**관련 Task:**
- S1M1 (API Documentation)
- S1M2 (Development Workflow)
- S5O1 (Deployment Configuration)
- S5T1 (Testing & QA)

---

## 주의사항

1. **정확성**: 코드 예시는 실행 가능해야 함
2. **최신성**: Next.js 14, React 18 기준
3. **완결성**: 신규 개발자가 이해할 수 있을 정도로 상세
4. **구조**: 목차 → 섹션 → 예시 → 주의사항 순서
5. **링크**: 내부 문서 간 상호 참조
6. **일관성**: 용어 통일 (예: Project, Valuation Method)

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
