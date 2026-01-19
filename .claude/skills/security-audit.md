# Security Audit Skill

**PoliticianFinder 프로젝트 전용 보안 취약점 검사 스킬**

---

## 프로젝트 컨텍스트

**프로젝트**: PoliticianFinder (AI 기반 정치인 평가 플랫폼)
**기술 스택**:
- Frontend: Next.js 14 (App Router), React, TypeScript, Tailwind CSS
- Backend: Next.js API Routes
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth

---

## AI-only 개발 원칙 (필수 준수)

### ✅ 허용
- CLI 명령어로 보안 스캔 도구 실행
- 코드 분석으로 취약점 탐지
- 보안 보고서를 파일로 생성

### ❌ 금지
- 웹 기반 보안 스캔 도구 수동 사용
- Dashboard에서 수동으로 보안 설정 변경
- 사용자에게 수동 보안 검토 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 보안 감사관입니다:

1. **취약점 스캔**: OWASP Top 10 기반 보안 점검
2. **인증/인가 검증**: Supabase Auth 설정 및 RLS 정책 확인
3. **데이터 보호**: 민감 정보 노출 방지 확인
4. **의존성 검사**: 알려진 취약점이 있는 패키지 탐지
5. **보안 보고서 작성**: 취약점과 수정 방안 문서화

---

## 보안 감사 프로세스

### 1. 초기 스캔

```bash
# 의존성 취약점 검사
cd /g/내\ 드라이브/Developement/PoliticianFinder/frontend
npm audit

# 고위험 취약점 확인
npm audit --audit-level=high

# 자동 수정 가능한 항목
npm audit fix
```

### 2. OWASP Top 10 체크리스트

#### A01: Broken Access Control (접근 제어 취약점)

**체크 항목**:
- [ ] RLS (Row Level Security) 정책이 모든 테이블에 활성화되었는가?
- [ ] API Routes에 인증 미들웨어가 있는가?
- [ ] 사용자가 자신의 데이터만 접근하는가?
- [ ] 관리자 기능에 역할 기반 접근 제어가 있는가?

**검사 방법**:
```typescript
// ✅ 좋은 예: 인증 확인
export async function GET(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // 사용자 데이터만 조회
  const { data } = await supabase
    .from('evaluations')
    .select('*')
    .eq('user_id', user.id);

  return NextResponse.json({ data });
}

// ❌ 나쁜 예: 인증 없음
export async function GET(request: NextRequest) {
  const { data } = await supabase.from('evaluations').select('*'); // 모든 데이터 노출!
  return NextResponse.json({ data });
}
```

**RLS 정책 확인**:
```sql
-- 테이블별 RLS 활성화 확인
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- RLS 정책 확인
SELECT tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename;
```

---

#### A02: Cryptographic Failures (암호화 실패)

**체크 항목**:
- [ ] HTTPS 사용 (Vercel은 기본 제공)
- [ ] 환경변수에 민감 정보 저장
- [ ] 비밀번호 평문 저장 금지 (Supabase Auth 사용)
- [ ] API 키가 코드에 하드코딩되지 않았는가?

**검사 방법**:
```bash
# .env 파일이 .gitignore에 있는지 확인
grep -r "SUPABASE" --include="*.ts" --include="*.tsx" /g/내\ 드라이브/Developement/PoliticianFinder/frontend/src

# 하드코딩된 시크릿 검색
grep -r "password\s*=\s*['\"]" --include="*.ts" --include="*.tsx" /g/내\ 드라이브/Developement/PoliticianFinder/frontend/src
```

**환경변수 체크**:
```typescript
// ✅ 좋은 예
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// ❌ 나쁜 예
const supabaseUrl = "https://xxxxx.supabase.co"; // 하드코딩!
```

---

#### A03: Injection (인젝션)

**체크 항목**:
- [ ] SQL Injection 방지 (Supabase 클라이언트 사용)
- [ ] NoSQL Injection 방지
- [ ] Command Injection 방지
- [ ] 사용자 입력 검증

**검사 방법**:
```typescript
// ✅ 좋은 예: Supabase 클라이언트 사용
const { data } = await supabase
  .from('politicians')
  .select('*')
  .eq('name', userInput); // 자동으로 이스케이프됨

// ❌ 나쁜 예: 원시 SQL (사용 금지)
const query = `SELECT * FROM politicians WHERE name = '${userInput}'`; // SQL Injection 위험!
```

**입력 검증 패턴**:
```typescript
import { z } from 'zod';

// Zod를 사용한 입력 검증
const searchSchema = z.object({
  query: z.string().min(1).max(100),
  page: z.number().int().positive().max(1000),
  party: z.enum(['민주당', '국민의힘', '정의당', '기타']).optional(),
});

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const params = {
      query: searchParams.get('query'),
      page: parseInt(searchParams.get('page') || '1'),
      party: searchParams.get('party'),
    };

    // 검증
    const validated = searchSchema.parse(params);

    // 안전한 쿼리
    const { data } = await supabase
      .from('politicians')
      .select('*')
      .ilike('name', `%${validated.query}%`)
      .eq('party', validated.party || undefined);

    return NextResponse.json({ data });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: 'Invalid input' }, { status: 400 });
    }
    throw error;
  }
}
```

---

#### A04: Insecure Design (불안전한 설계)

**체크 항목**:
- [ ] 보안이 설계 단계부터 고려되었는가?
- [ ] Threat modeling이 수행되었는가?
- [ ] 최소 권한 원칙이 적용되었는가?
- [ ] 실패 시 안전한 기본값 사용

**검사 예시**:
```typescript
// ✅ 좋은 예: 기본적으로 비공개
interface Evaluation {
  id: string;
  politician_id: string;
  user_id: string;
  score: number;
  is_public: boolean; // 기본값: false
}

// RLS 정책: 자신의 평가만 조회
CREATE POLICY "Users can view own evaluations"
ON evaluations FOR SELECT
USING (auth.uid() = user_id OR is_public = true);
```

---

#### A05: Security Misconfiguration (보안 설정 오류)

**체크 항목**:
- [ ] CORS 설정이 올바른가?
- [ ] 불필요한 HTTP 헤더가 제거되었는가?
- [ ] 에러 메시지가 과도한 정보를 노출하지 않는가?
- [ ] 개발 도구가 프로덕션에 포함되지 않았는가?

**Next.js 보안 헤더 설정**:
```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
};
```

**에러 처리**:
```typescript
// ❌ 나쁜 예: 상세한 에러 노출
catch (error) {
  return NextResponse.json({ error: error.message }, { status: 500 }); // 스택 트레이스 노출 위험
}

// ✅ 좋은 예: 일반적인 에러 메시지
catch (error) {
  console.error('Internal error:', error); // 로그에만 기록
  return NextResponse.json({ error: 'An error occurred' }, { status: 500 });
}
```

---

#### A06: Vulnerable and Outdated Components (취약한 구성 요소)

**체크 항목**:
- [ ] 의존성이 최신 상태인가?
- [ ] 알려진 취약점이 있는 패키지 사용 중인가?
- [ ] 사용하지 않는 의존성이 제거되었는가?

**자동 검사**:
```bash
# 취약점 검사
npm audit

# 업데이트 가능한 패키지 확인
npm outdated

# 자동 수정
npm audit fix

# 주요 버전 업그레이드 (주의 필요)
npm audit fix --force
```

---

#### A07: Identification and Authentication Failures (인증 실패)

**체크 항목**:
- [ ] 세션 관리가 안전한가?
- [ ] 비밀번호 정책이 강력한가?
- [ ] 다중 인증(MFA) 지원하는가?
- [ ] 세션 고정 공격 방지

**Supabase Auth 체크**:
```typescript
// ✅ 좋은 예: 세션 확인
export async function authenticateUser(request: NextRequest) {
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();

  if (!session) {
    throw new Error('Not authenticated');
  }

  // 세션 갱신 (자동)
  const { data: { user } } = await supabase.auth.getUser();

  return user;
}
```

**비밀번호 정책 (Supabase 설정)**:
```sql
-- 최소 8자, 대소문자, 숫자, 특수문자 포함
-- Supabase Dashboard > Authentication > Policies에서 설정
```

---

#### A08: Software and Data Integrity Failures (무결성 실패)

**체크 항목**:
- [ ] CI/CD 파이프라인이 안전한가?
- [ ] 무결성 검증이 있는가? (SRI, 체크섬)
- [ ] 역직렬화 공격 방지

**예시**:
```typescript
// ✅ 좋은 예: 타입 검증
import { z } from 'zod';

const EvaluationSchema = z.object({
  politician_id: z.string().uuid(),
  score: z.number().min(1).max(5),
  comment: z.string().max(1000),
});

export async function POST(request: NextRequest) {
  const body = await request.json();
  const validated = EvaluationSchema.parse(body); // 검증 실패 시 에러
  // ...
}
```

---

#### A09: Security Logging and Monitoring Failures (로깅/모니터링 실패)

**체크 항목**:
- [ ] 중요 이벤트가 로깅되는가?
- [ ] 로그에 민감 정보가 포함되지 않는가?
- [ ] 실패한 로그인 시도를 추적하는가?
- [ ] 비정상적인 패턴 감지

**로깅 패턴**:
```typescript
// ✅ 좋은 예: 구조화된 로깅
import { logger } from '@/lib/logger';

export async function POST(request: NextRequest) {
  const user = await authenticateUser(request);

  logger.info('Evaluation created', {
    user_id: user.id,
    timestamp: new Date().toISOString(),
    endpoint: '/api/evaluations',
  });

  // ❌ 나쁜 예: 민감 정보 로깅
  logger.info('User login', {
    password: '********', // 절대 금지!
    email: user.email,
  });
}
```

---

#### A10: Server-Side Request Forgery (SSRF)

**체크 항목**:
- [ ] 외부 URL 요청 시 검증하는가?
- [ ] 내부 네트워크 접근이 차단되었는가?
- [ ] URL 파라미터를 그대로 사용하지 않는가?

**예시**:
```typescript
// ❌ 나쁜 예: 검증 없는 외부 요청
export async function POST(request: NextRequest) {
  const { url } = await request.json();
  const response = await fetch(url); // SSRF 위험!
  return NextResponse.json(await response.json());
}

// ✅ 좋은 예: URL 검증
const ALLOWED_DOMAINS = ['api.example.com', 'data.gov.kr'];

export async function POST(request: NextRequest) {
  const { url } = await request.json();
  const parsedUrl = new URL(url);

  if (!ALLOWED_DOMAINS.includes(parsedUrl.hostname)) {
    return NextResponse.json({ error: 'Invalid domain' }, { status: 400 });
  }

  const response = await fetch(url);
  return NextResponse.json(await response.json());
}
```

---

## Supabase RLS 정책 검증

### RLS 활성화 확인
```bash
# Supabase CLI 사용
npx supabase db dump --table politicians --schema public
```

### 필수 RLS 정책

```sql
-- 1. Politicians 테이블: 모두 읽기, 인증된 사용자만 생성
CREATE POLICY "Anyone can view politicians"
ON politicians FOR SELECT
USING (true);

CREATE POLICY "Authenticated users can insert politicians"
ON politicians FOR INSERT
WITH CHECK (auth.role() = 'authenticated');

-- 2. Evaluations 테이블: 자신의 평가만 CRUD
CREATE POLICY "Users can view own evaluations"
ON evaluations FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own evaluations"
ON evaluations FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own evaluations"
ON evaluations FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own evaluations"
ON evaluations FOR DELETE
USING (auth.uid() = user_id);

-- 3. Users 테이블: 자신의 프로필만 접근
CREATE POLICY "Users can view own profile"
ON users FOR SELECT
USING (auth.uid() = id);
```

---

## 보안 감사 보고서 템플릿

```markdown
# 보안 감사 보고서

**감사 날짜**: [YYYY-MM-DD]
**감사자**: Claude Code
**프로젝트**: PoliticianFinder

---

## 요약

### 전체 보안 점수: X/100

**위험도 분포**:
- 🔴 Critical: N개
- 🟠 High: N개
- 🟡 Medium: N개
- 🟢 Low: N개

**OWASP Top 10 준수율**: X%

---

## Critical Issues (즉시 수정 필요)

### 1. [취약점 제목]

**위험도**: 🔴 Critical
**카테고리**: OWASP A01 - Broken Access Control
**영향도**: 사용자 데이터 무단 접근 가능

**발견 위치**:
- `src/app/api/evaluations/route.ts:25`

**취약점 설명**:
```typescript
// 현재 코드 (취약)
export async function GET() {
  const { data } = await supabase.from('evaluations').select('*');
  return NextResponse.json({ data }); // 모든 사용자 평가 노출!
}
```

**공격 시나리오**:
1. 인증되지 않은 사용자가 `/api/evaluations` 접근
2. 모든 사용자의 평가 데이터 조회
3. 개인정보 유출

**수정 방안**:
```typescript
export async function GET(request: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { data } = await supabase
    .from('evaluations')
    .select('*')
    .eq('user_id', user.id); // 자신의 데이터만

  return NextResponse.json({ data });
}
```

**예상 수정 시간**: 30분

---

## High Priority Issues

[동일한 형식으로 나열]

---

## Medium Priority Issues

[동일한 형식으로 나열]

---

## Low Priority Issues

[동일한 형식으로 나열]

---

## OWASP Top 10 체크리스트

- [ ] A01: Broken Access Control
- [x] A02: Cryptographic Failures
- [x] A03: Injection
- [ ] A04: Insecure Design
- [ ] A05: Security Misconfiguration
- [x] A06: Vulnerable Components
- [x] A07: Authentication Failures
- [x] A08: Integrity Failures
- [ ] A09: Logging Failures
- [x] A10: SSRF

---

## 의존성 취약점

**npm audit 결과**:
```
found X vulnerabilities (Y high, Z critical)
```

**조치 필요 패키지**:
1. `package-name@version` - CVE-XXXX-XXXX (Critical)
   - 수정 버전: `X.X.X`
   - 명령어: `npm install package-name@X.X.X`

---

## 권장 사항

### 즉시 조치
1. Critical 취약점 수정
2. RLS 정책 활성화
3. 의존성 업데이트

### 단기 조치 (1주일)
1. High 우선순위 취약점 수정
2. 보안 헤더 추가
3. 입력 검증 강화

### 중기 조치 (1개월)
1. 보안 모니터링 시스템 구축
2. 정기적인 보안 감사 자동화
3. 보안 교육 및 문서화

---

## 다음 감사 일정

**권장 주기**: 매월 1회
**다음 감사 예정일**: [YYYY-MM-DD]
```

---

## 자동화 스크립트

```bash
#!/bin/bash
# security-audit.sh

echo "🔍 PoliticianFinder 보안 감사 시작..."

# 1. 의존성 취약점 검사
echo "\n📦 의존성 검사 중..."
npm audit --json > audit-report.json

# 2. 환경변수 누출 검사
echo "\n🔑 환경변수 하드코딩 검사 중..."
grep -r "SUPABASE.*=" --include="*.ts" --include="*.tsx" src/ || echo "✅ 환경변수 안전"

# 3. TODO/FIXME 보안 이슈
echo "\n📝 보안 TODO 확인 중..."
grep -r "TODO.*security\|FIXME.*security" --include="*.ts" src/

echo "\n✅ 보안 감사 완료!"
```

---

## 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Supabase Security Best Practices](https://supabase.com/docs/guides/auth/row-level-security)
- [Next.js Security](https://nextjs.org/docs/app/building-your-application/configuring/security)

---

**이 스킬을 활성화하면, OWASP Top 10 기반으로 체계적인 보안 감사를 수행하여 PoliticianFinder 프로젝트의 보안을 강화합니다.**
