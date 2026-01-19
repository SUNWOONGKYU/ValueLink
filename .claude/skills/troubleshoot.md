# Troubleshoot Skill

**PoliticianFinder 프로젝트 전용 문제 해결 및 디버깅 스킬**

---

## 프로젝트 컨텍스트

**프로젝트**: PoliticianFinder (AI 기반 정치인 평가 플랫폼)
**기술 스택**:
- Frontend/Backend: Next.js 14, React, TypeScript
- Database: Supabase (PostgreSQL)
- Deployment: Vercel

---

## AI-only 개발 원칙 (필수 준수)

### ✅ 허용
- CLI 명령어로 로그 분석
- 코드 검사 도구 사용
- 자동화된 디버깅 스크립트

### ❌ 금지
- 웹 브라우저에서 수동 디버깅
- GUI 디버거 수동 사용
- 사용자에게 수동 문제 해결 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 트러블슈터입니다:

1. **문제 진단**: 에러 메시지 분석 및 원인 파악
2. **로그 분석**: 로그 파일에서 패턴 찾기
3. **근본 원인 분석**: RCA (Root Cause Analysis) 수행
4. **해결책 제시**: 단기 및 장기 해결 방안 제시
5. **문서화**: 문제 해결 과정 기록

---

## 문제 해결 프로세스

### 1. 문제 인식 및 재현

```bash
#!/bin/bash
# scripts/reproduce-issue.sh

echo "🔍 문제 재현 시도..."

# 1. 환경 정보 수집
echo "\n📊 환경 정보:"
echo "Node: $(node --version)"
echo "npm: $(npm --version)"
echo "OS: $(uname -a)"

# 2. 재현 단계 실행
echo "\n🎬 재현 단계 실행 중..."
# 여기에 재현 단계 입력

# 3. 에러 로그 캡처
echo "\n📝 에러 로그:"
# 에러 로그 저장
```

---

### 2. 로그 분석

#### Next.js 로그 확인
```bash
# 개발 서버 로그
npm run dev 2>&1 | tee dev.log

# 빌드 로그
npm run build 2>&1 | tee build.log

# 프로덕션 로그 (Vercel)
vercel logs --follow
```

#### 에러 패턴 검색
```bash
# 특정 에러 검색
grep -r "Error:" logs/ --color

# 시간대별 에러 빈도
grep "Error" logs/app.log | cut -d' ' -f1-2 | uniq -c

# 최다 발생 에러 Top 10
grep "Error" logs/app.log | sort | uniq -c | sort -rn | head -10
```

---

## 일반적인 문제 및 해결책

### Next.js 관련

#### 1. "Module not found" 에러

**증상**:
```
Error: Cannot find module '@/components/PoliticianCard'
```

**원인**:
- 파일 경로 오류
- tsconfig.json paths 설정 오류
- 파일이 실제로 존재하지 않음

**해결책**:
```bash
# 1. 파일 존재 확인
ls -la src/components/PoliticianCard.tsx

# 2. tsconfig.json 확인
cat tsconfig.json | jq '.compilerOptions.paths'

# 3. 경로 별칭 확인
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}

# 4. 캐시 삭제 후 재시작
rm -rf .next
npm run dev
```

---

#### 2. "Hydration failed" 에러

**증상**:
```
Error: Hydration failed because the initial UI does not match
what was rendered on the server.
```

**원인**:
- 서버와 클라이언트 렌더링 불일치
- 조건부 렌더링 문제
- 브라우저 확장 프로그램 간섭

**해결책**:
```typescript
// ❌ 나쁜 예: 서버와 클라이언트 불일치
export default function Component() {
  return <div>{new Date().toISOString()}</div>; // 매번 다른 값!
}

// ✅ 좋은 예: useEffect로 클라이언트 전용 처리
'use client';
import { useEffect, useState } from 'react';

export default function Component() {
  const [time, setTime] = useState<string | null>(null);

  useEffect(() => {
    setTime(new Date().toISOString());
  }, []);

  return <div>{time || 'Loading...'}</div>;
}

// 또는 suppressHydrationWarning 사용
<div suppressHydrationWarning>
  {new Date().toISOString()}
</div>
```

---

#### 3. API Route 404 에러

**증상**:
```
GET /api/politicians 404 (Not Found)
```

**원인**:
- 파일 위치 오류
- export 함수명 오류
- 라우팅 설정 문제

**해결책**:
```bash
# 1. 파일 구조 확인
ls -la src/app/api/politicians/

# 올바른 구조:
# src/app/api/politicians/route.ts

# 2. export 함수명 확인
cat src/app/api/politicians/route.ts | grep "export async function"

# 올바른 형식:
# export async function GET(request: NextRequest) { ... }

# 3. 서버 재시작
# Next.js 개발 서버 재시작 필요
```

---

### Supabase 관련

#### 1. "Invalid API key" 에러

**증상**:
```
Error: Invalid API key
```

**원인**:
- 환경변수 미설정
- 잘못된 API 키
- 환경변수 로딩 실패

**해결책**:
```bash
# 1. 환경변수 확인
echo $NEXT_PUBLIC_SUPABASE_URL
echo $NEXT_PUBLIC_SUPABASE_ANON_KEY

# 2. .env.local 파일 확인
cat .env.local

# 3. 환경변수 다시 로드
# .env.local 수정 후 서버 재시작

# 4. Vercel 환경변수 확인
vercel env ls

# 5. 올바른 값으로 설정
vercel env add NEXT_PUBLIC_SUPABASE_URL production
```

---

#### 2. "Row Level Security policy violation" 에러

**증상**:
```
Error: new row violates row-level security policy for table "evaluations"
```

**원인**:
- RLS 정책이 요청을 차단
- 인증되지 않은 사용자
- 권한 부족

**해결책**:
```bash
# 1. RLS 정책 확인
# Supabase CLI 사용
npx supabase db dump --table evaluations --schema public

# 2. 정책 수정 (필요시)
```

```sql
-- 현재 정책 확인
SELECT * FROM pg_policies WHERE tablename = 'evaluations';

-- 정책 수정 예시
ALTER POLICY "Users can insert own evaluations"
ON evaluations
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

---

#### 3. "Connection timeout" 에러

**증상**:
```
Error: Connection to database timed out
```

**원인**:
- 네트워크 문제
- Supabase 서비스 장애
- 쿼리 실행 시간 초과

**해결책**:
```typescript
// 1. 타임아웃 설정 증가
const supabase = createClient(url, key, {
  db: {
    timeout: 10000, // 10초
  },
});

// 2. 재시도 로직 추가
async function queryWithRetry(queryFn: () => Promise<any>, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await queryFn();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}

// 3. 쿼리 최적화
// 불필요한 JOIN 제거, 인덱스 추가 등
```

---

### TypeScript 관련

#### 1. "Type 'X' is not assignable to type 'Y'" 에러

**증상**:
```typescript
Type 'string | null' is not assignable to type 'string'.
```

**원인**:
- 타입 불일치
- null/undefined 처리 누락
- 타입 정의 오류

**해결책**:
```typescript
// ❌ 나쁜 예
const name: string = politician.name; // name이 null일 수 있음

// ✅ 좋은 예 1: 타입 가드
if (politician.name) {
  const name: string = politician.name;
}

// ✅ 좋은 예 2: null 병합 연산자
const name: string = politician.name ?? 'Unknown';

// ✅ 좋은 예 3: 타입 단언 (확실한 경우만)
const name: string = politician.name!;

// ✅ 좋은 예 4: 옵셔널 타입
const name: string | null = politician.name;
```

---

#### 2. "Property 'X' does not exist on type 'Y'" 에러

**증상**:
```typescript
Property 'avg_rating' does not exist on type 'Politician'.
```

**원인**:
- 타입 정의 누락
- 인터페이스 불일치

**해결책**:
```typescript
// 1. 타입 정의 확인 및 수정
interface Politician {
  id: string;
  name: string;
  party: string;
  avg_rating?: number; // 누락된 속성 추가
}

// 2. 또는 동적 속성 허용
interface Politician {
  id: string;
  name: string;
  party: string;
  [key: string]: any; // 동적 속성 허용 (권장하지 않음)
}
```

---

### 성능 관련

#### 1. 느린 페이지 로딩

**증상**: 페이지 로드 시간 > 3초

**진단**:
```bash
# 1. Lighthouse 실행
npx lighthouse http://localhost:3000 --view

# 2. 번들 크기 분석
ANALYZE=true npm run build

# 3. 네트워크 탭 분석 (개발자 도구)
```

**해결책**:
```typescript
// 1. 이미지 최적화
import Image from 'next/image';

<Image
  src="/politician.jpg"
  width={400}
  height={300}
  alt="Politician"
  loading="lazy"
/>

// 2. 코드 스플리팅
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <div>Loading...</div>,
  ssr: false,
});

// 3. 데이터 fetching 최적화
// React Query 사용
import { useQuery } from '@tanstack/react-query';

const { data } = useQuery({
  queryKey: ['politicians'],
  queryFn: fetchPoliticians,
  staleTime: 5 * 60 * 1000, // 5분 캐싱
});
```

---

#### 2. 메모리 누수

**증상**: 브라우저 메모리 사용량 지속 증가

**진단**:
```typescript
// Chrome DevTools > Memory > Take heap snapshot
// 메모리 프로파일링으로 누수 원인 파악
```

**해결책**:
```typescript
// ❌ 나쁜 예: 정리되지 않은 이벤트 리스너
useEffect(() => {
  window.addEventListener('resize', handleResize);
  // cleanup 함수 없음!
}, []);

// ✅ 좋은 예: cleanup 함수 포함
useEffect(() => {
  window.addEventListener('resize', handleResize);

  return () => {
    window.removeEventListener('resize', handleResize);
  };
}, []);

// ❌ 나쁜 예: 정리되지 않은 타이머
useEffect(() => {
  setInterval(() => {
    fetchData();
  }, 1000);
}, []);

// ✅ 좋은 예: cleanup으로 타이머 정리
useEffect(() => {
  const timer = setInterval(() => {
    fetchData();
  }, 1000);

  return () => clearInterval(timer);
}, []);
```

---

## 디버깅 도구

### 1. Next.js 디버그 모드

```bash
# 디버그 로그 활성화
DEBUG=* npm run dev

# 특정 모듈만
DEBUG=next:* npm run dev
```

### 2. React Developer Tools (CLI)

```bash
# React 컴포넌트 트리 출력
npm install -g react-devtools

# 실행
react-devtools
```

### 3. Supabase CLI 디버깅

```bash
# 로컬 Supabase 로그
npx supabase logs

# 특정 서비스 로그
npx supabase logs db
npx supabase logs api
```

---

## 근본 원인 분석 (RCA) 템플릿

```markdown
# 근본 원인 분석 보고서

**문제 ID**: #123
**보고 날짜**: [YYYY-MM-DD]
**분석자**: Claude Code

---

## 문제 요약

### 증상
- 사용자가 평가 제출 시 500 에러 발생
- 발생 빈도: 10회 중 8회
- 영향 범위: 모든 사용자

### 타임라인
- 14:30 - 첫 에러 보고
- 14:35 - 문제 재현 확인
- 14:40 - 로그 분석 시작
- 15:00 - 근본 원인 파악
- 15:30 - 수정 완료
- 16:00 - 배포 및 검증

---

## 근본 원인

### 직접 원인
- POST /api/evaluations 엔드포인트에서 `politician_id` 검증 로직 누락

### 근본 원인
- 코드 리뷰 시 입력 검증 체크리스트 미준수
- 단위 테스트 커버리지 부족 (65%)

### 기여 요인
- 급하게 배포한 핫픽스
- 테스트 케이스 작성 누락

---

## 영향 분석

### 비즈니스 영향
- 80% 평가 제출 실패
- 약 50명의 사용자 영향
- 평가 데이터 손실 없음

### 기술적 영향
- API 에러율: 5% → 25%
- 서버 부하 증가 (재시도 요청)

---

## 해결 과정

### 1. 즉각 조치 (Immediate Fix)
```typescript
// 입력 검증 추가
if (!isValidUUID(politician_id)) {
  return NextResponse.json(
    { error: 'Invalid politician_id' },
    { status: 400 }
  );
}
```

### 2. 단기 조치 (Short-term)
- 해당 엔드포인트에 단위 테스트 추가
- 입력 검증 라이브러리 도입 (Zod)

### 3. 장기 조치 (Long-term)
- 모든 API 엔드포인트에 입력 검증 강화
- 테스트 커버리지 80% 이상 유지
- 코드 리뷰 체크리스트 업데이트

---

## 재발 방지

### 프로세스 개선
1. 배포 전 필수 테스트 커버리지 확인
2. 입력 검증 자동화 (Zod 스키마)
3. 코드 리뷰 시 보안 체크리스트 필수 확인

### 모니터링 강화
1. API 에러율 알람 설정 (> 5%)
2. 입력 검증 실패 로깅
3. 주간 에러 리포트 자동 생성

---

## 교훈

### 잘한 점
- 빠른 문제 인식 및 대응 (30분 내 수정)
- 명확한 에러 로깅으로 원인 파악 용이

### 개선할 점
- 배포 전 테스트 강화 필요
- 입력 검증 표준화 필요
- 코드 리뷰 프로세스 개선

---

## 액션 아이템

- [ ] 입력 검증 라이브러리 (Zod) 도입 (담당자: -, 기한: 1주)
- [ ] 테스트 커버리지 80% 달성 (담당자: -, 기한: 2주)
- [ ] 코드 리뷰 체크리스트 업데이트 (담당자: -, 기한: 즉시)
- [ ] API 모니터링 알람 설정 (담당자: -, 기한: 1주)
```

---

## 일반적인 디버깅 체크리스트

### 프론트엔드
- [ ] 브라우저 콘솔 에러 확인
- [ ] Network 탭에서 API 요청/응답 확인
- [ ] React DevTools로 컴포넌트 상태 확인
- [ ] 캐시 삭제 후 재시도
- [ ] 다른 브라우저에서 테스트

### 백엔드
- [ ] 서버 로그 확인
- [ ] 데이터베이스 연결 확인
- [ ] 환경변수 설정 확인
- [ ] API 엔드포인트 직접 호출 (curl)
- [ ] 데이터베이스 쿼리 직접 실행

### 인프라
- [ ] Vercel 배포 로그 확인
- [ ] Supabase 상태 확인
- [ ] DNS 설정 확인
- [ ] SSL 인증서 확인
- [ ] 네트워크 연결 확인

---

## 긴급 상황 대응 플레이북

### 1. 서비스 완전 다운

**증상**: 사이트 접속 불가

**조치**:
```bash
# 1. 헬스 체크
curl -I https://politicianfinder.vercel.app

# 2. Vercel 상태 확인
vercel ls

# 3. 최근 배포 롤백
vercel promote [PREVIOUS_DEPLOYMENT_URL]

# 4. 로그 확인
vercel logs
```

### 2. 데이터베이스 연결 실패

**증상**: "Database connection failed"

**조치**:
```bash
# 1. Supabase 상태 확인
curl https://status.supabase.com/api/v2/status.json

# 2. 연결 테스트
npx supabase db ping

# 3. 환경변수 확인
vercel env ls | grep SUPABASE

# 4. 대기 또는 백업 DB 전환 (있는 경우)
```

### 3. 높은 에러율

**증상**: 에러율 > 10%

**조치**:
```bash
# 1. 에러 로그 확인
vercel logs | grep "Error"

# 2. 최근 배포 확인
vercel ls --json | jq '.[0]'

# 3. 필요시 롤백
vercel promote [PREVIOUS_DEPLOYMENT_URL]

# 4. 근본 원인 분석 시작
```

---

**이 스킬을 활성화하면, PoliticianFinder 프로젝트의 모든 문제를 체계적으로 진단하고 해결하여 서비스 안정성을 보장합니다.**
