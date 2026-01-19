# Code Review Skill

**PoliticianFinder 프로젝트 전용 코드 리뷰 및 품질 검증 스킬**

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
- CLI 명령어로 코드 분석 도구 실행
- 정적 분석 도구 자동화
- 코드 검토 결과를 파일로 저장

### ❌ 금지
- GitHub PR을 수동으로 웹에서 리뷰
- GUI 기반 코드 리뷰 도구 사용
- 사용자에게 수동 검토 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 코드 리뷰어입니다:

1. **코드 품질 검증**: 가독성, 유지보수성, 확장성 평가
2. **베스트 프랙티스 확인**: TypeScript, React, Next.js 패턴 검증
3. **보안 취약점 발견**: 잠재적 보안 이슈 식별
4. **성능 문제 파악**: 비효율적인 코드 패턴 감지
5. **일관성 검사**: 프로젝트 코딩 컨벤션 준수 확인

---

## 코드 리뷰 프로세스

### 1. 초기 스캔
```bash
# TypeScript 타입 체크
cd /g/내\ 드라이브/Developement/PoliticianFinder/frontend
npm run type-check

# ESLint 실행
npm run lint

# 테스트 실행
npm run test
```

### 2. 코드 분석

#### 2.1 아키텍처 리뷰
- [ ] 파일/폴더 구조가 프로젝트 표준을 따르는가?
- [ ] 컴포넌트 계층 구조가 논리적인가?
- [ ] 관심사 분리가 잘 되어 있는가?
- [ ] 의존성 방향이 올바른가?

#### 2.2 코드 품질 체크리스트

**가독성 (Readability)**
- [ ] 변수/함수명이 의도를 명확히 표현하는가?
- [ ] 함수가 단일 책임을 가지는가? (최대 30줄 권장)
- [ ] 중첩 깊이가 적절한가? (최대 3단계)
- [ ] 매직 넘버 대신 상수를 사용하는가?
- [ ] 주석이 필요한 복잡한 로직에만 있는가?

**타입 안전성 (Type Safety)**
- [ ] TypeScript 타입이 명시적으로 정의되었는가?
- [ ] `any` 타입 사용을 최소화했는가?
- [ ] 타입 가드를 적절히 사용하는가?
- [ ] null/undefined 처리가 명확한가?

**에러 핸들링**
- [ ] try-catch 블록이 적절히 사용되었는가?
- [ ] 에러 메시지가 명확하고 유용한가?
- [ ] 에러 로깅이 구현되었는가?
- [ ] 사용자 친화적인 에러 처리가 있는가?

**DRY 원칙**
- [ ] 중복 코드가 없는가?
- [ ] 공통 로직이 유틸리티로 추출되었는가?
- [ ] 재사용 가능한 컴포넌트로 분리되었는가?

**SOLID 원칙**
- [ ] 단일 책임 원칙 (SRP) 준수
- [ ] 개방-폐쇄 원칙 (OCP) 고려
- [ ] 의존성 역전 원칙 (DIP) 적용

#### 2.3 React/Next.js 특화 체크

**컴포넌트 설계**
```typescript
// ❌ 나쁜 예: 하나의 컴포넌트에 모든 로직
export default function PoliticianPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  // ... 100줄의 코드
}

// ✅ 좋은 예: 책임 분리
export default function PoliticianPage() {
  const { data, loading } = usePoliticians();

  if (loading) return <LoadingState />;
  return <PoliticianList data={data} />;
}
```

**Hooks 사용**
- [ ] Custom hooks로 로직을 재사용하는가?
- [ ] useEffect 의존성 배열이 올바른가?
- [ ] 불필요한 리렌더링을 방지하는가? (useMemo, useCallback)

**서버/클라이언트 컴포넌트**
- [ ] 'use client' 지시어가 필요한 곳에만 있는가?
- [ ] 서버 컴포넌트를 최대한 활용하는가?
- [ ] 데이터 fetching이 적절한 위치에서 이루어지는가?

#### 2.4 API Routes 리뷰

```typescript
// ✅ 좋은 예: 명확한 구조
export async function GET(request: NextRequest) {
  try {
    // 1. 인증 확인
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // 2. 입력 검증
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    if (page < 1) {
      return NextResponse.json({ error: 'Invalid page' }, { status: 400 });
    }

    // 3. 비즈니스 로직
    const { data, error } = await supabase
      .from('politicians')
      .select('*')
      .range((page - 1) * 10, page * 10 - 1);

    if (error) throw error;

    // 4. 응답 반환
    return NextResponse.json({ data, page });

  } catch (error) {
    console.error('GET /api/politicians error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
```

**API 체크리스트**
- [ ] 인증/인가 확인
- [ ] 입력 검증 (타입, 범위, 형식)
- [ ] 적절한 HTTP 상태 코드 사용
- [ ] 에러 핸들링 구현
- [ ] 로깅 추가

---

## 리뷰 우선순위

### P0 (Critical) - 즉시 수정 필요
- 보안 취약점 (SQL Injection, XSS, CSRF)
- 인증/인가 누락
- 심각한 성능 문제
- 데이터 유실 가능성
- TypeScript `any` 남용

### P1 (High) - 빠른 시일 내 수정
- 에러 핸들링 누락
- 메모리 누수 가능성
- 중요한 테스트 누락
- 잘못된 타입 정의
- 접근성 문제

### P2 (Medium) - 개선 권장
- 코드 중복
- 가독성 저하
- 비효율적인 알고리즘
- 불필요한 리렌더링
- 네이밍 컨벤션 불일치

### P3 (Low) - 선택적 개선
- 주석 개선
- 코드 스타일 통일
- 사소한 최적화
- 더 나은 패턴 제안

---

## 리뷰 결과 보고 템플릿

```markdown
# 코드 리뷰 보고서

**리뷰 대상**: [파일/기능명]
**리뷰 날짜**: [YYYY-MM-DD]
**리뷰어**: Claude Code

---

## 요약
- 총 검토 파일: X개
- 발견된 이슈: Y개
  - P0 (Critical): N개
  - P1 (High): N개
  - P2 (Medium): N개
  - P3 (Low): N개

## 전체 평가
⭐⭐⭐⭐☆ (4/5)

**강점**:
- [좋은 점 1]
- [좋은 점 2]

**개선 필요**:
- [개선점 1]
- [개선점 2]

---

## 상세 리뷰

### P0 - Critical Issues

#### 1. [이슈 제목]
**파일**: `src/app/api/example/route.ts:25`
**문제**:
```typescript
// 현재 코드
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

**이유**: SQL Injection 취약점

**수정 제안**:
```typescript
// 수정된 코드
const { data } = await supabase
  .from('users')
  .select('*')
  .eq('id', userId);
```

---

### P1 - High Priority

#### 1. [이슈 제목]
**파일**: `src/components/PoliticianCard.tsx:45`
**문제**: 에러 핸들링 누락
**수정 제안**: try-catch 블록 추가

---

### P2 - Medium Priority

#### 1. 코드 중복
**파일**: `src/lib/utils/format.ts`, `src/lib/utils/display.ts`
**개선 제안**: 공통 함수로 통합

---

### P3 - Low Priority

#### 1. 네이밍 개선
**파일**: `src/components/List.tsx`
**제안**: `List` → `PoliticianList` (더 명확한 이름)

---

## 체크리스트 결과

### 코드 품질
- [x] 가독성
- [x] DRY 원칙
- [ ] SOLID 원칙 (일부 위반)
- [x] 타입 안전성

### 보안
- [ ] 인증/인가 (개선 필요)
- [x] XSS 방어
- [x] SQL Injection 방어
- [ ] CSRF 보호 (미구현)

### 성능
- [x] 효율적인 쿼리
- [ ] 불필요한 리렌더링 방지 (개선 필요)
- [x] 이미지 최적화

### 테스트
- [ ] 단위 테스트 (커버리지 부족)
- [ ] 통합 테스트 (미구현)

---

## 액션 아이템

1. [ ] P0 이슈 수정 (담당자: -, 기한: 즉시)
2. [ ] P1 이슈 수정 (담당자: -, 기한: 1주일)
3. [ ] 테스트 커버리지 개선 (담당자: -, 기한: 2주일)
4. [ ] 코드 리팩토링 (담당자: -, 기한: 3주일)

---

## 다음 단계

- P0 이슈부터 순차적으로 수정
- 수정 후 재검토 필요
- 테스트 추가 권장
```

---

## 자동화 도구 활용

### ESLint 설정
```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "max-lines-per-function": ["warn", 50]
  }
}
```

### TypeScript 엄격 모드
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

---

## 리뷰 시 참고할 패턴

### 좋은 패턴 ✅

```typescript
// 1. 명확한 타입 정의
interface Politician {
  id: string;
  name: string;
  party: string;
  region: string;
}

// 2. 에러 핸들링
async function getPolitician(id: string): Promise<Politician | null> {
  try {
    const { data, error } = await supabase
      .from('politicians')
      .select('*')
      .eq('id', id)
      .single();

    if (error) throw error;
    return data;
  } catch (error) {
    console.error('getPolitician error:', error);
    return null;
  }
}

// 3. Custom Hook으로 로직 분리
function usePolitician(id: string) {
  const [data, setData] = useState<Politician | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPolitician(id).then(setData).finally(() => setLoading(false));
  }, [id]);

  return { data, loading };
}
```

### 나쁜 패턴 ❌

```typescript
// 1. any 타입 남용
function process(data: any) { // ❌
  return data.map((item: any) => item.value);
}

// 2. 에러 무시
async function getData() {
  const { data } = await supabase.from('table').select('*'); // ❌ error 무시
  return data;
}

// 3. 과도한 중첩
function complex() { // ❌
  if (condition1) {
    if (condition2) {
      if (condition3) {
        if (condition4) {
          // ...
        }
      }
    }
  }
}
```

---

## 참고 자료

- [TypeScript Best Practices](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [React Best Practices](https://react.dev/learn/thinking-in-react)
- [Next.js Best Practices](https://nextjs.org/docs/app/building-your-application)
- [Clean Code JavaScript](https://github.com/ryanmcdermott/clean-code-javascript)

---

**이 스킬을 활성화하면, 체계적이고 엄격한 코드 리뷰를 수행하여 PoliticianFinder 프로젝트의 품질을 보장합니다.**
