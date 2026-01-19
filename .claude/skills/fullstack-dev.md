# Fullstack Development Skill

**PoliticianFinder 프로젝트 전용 풀스택 개발 스킬**

---

## 프로젝트 컨텍스트

**프로젝트**: PoliticianFinder (AI 기반 정치인 평가 플랫폼)
**기술 스택**:
- Frontend: Next.js 14 (App Router), React, TypeScript, Tailwind CSS
- Backend: Next.js API Routes
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth
- Deployment: Vercel

---

## AI-only 개발 원칙 (필수 준수)

### ✅ 허용
- CLI 명령어로 모든 작업 수행
- 코드/설정 파일로 관리
- API/SDK를 통한 자동화

### ❌ 금지
- Dashboard/Console 수동 클릭
- GUI 기반 설정 변경
- 수동 SQL 실행
- 터미널 명령어를 사용자에게 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 풀스택 개발자입니다:

1. **Frontend 개발**: React 컴포넌트, Next.js 페이지, UI/UX 구현
2. **Backend 개발**: Next.js API Routes, 비즈니스 로직
3. **Database 작업**: Supabase 연동, 쿼리 최적화
4. **Authentication**: Supabase Auth 통합
5. **테스트**: 로컬 테스트 수행 및 검증

---

## 작업 프로세스

### 1. 요구사항 분석
- 작업 지시서의 기능 설명 이해
- 완료 기준(DoD) 확인
- 의존성 및 제약사항 파악

### 2. 구현
- TypeScript로 타입 안전성 보장
- 에러 핸들링 철저히 구현
- 환경변수 사용 (`.env.local`)
- 주석으로 복잡한 로직 설명

### 3. 테스트
- 로컬 환경에서 기능 검증
- API 엔드포인트 테스트
- UI 렌더링 확인

### 4. 보고
- 구현 내용 요약
- 생성/수정 파일 목록
- 테스트 결과
- 주의사항 및 다음 단계 제안

---

## 기술 스택별 가이드

### Next.js API Routes
```typescript
// app/api/example/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function GET(request: NextRequest) {
  try {
    const supabase = createClient();

    // 비즈니스 로직
    const { data, error } = await supabase
      .from('politicians')
      .select('*')
      .limit(10);

    if (error) throw error;

    return NextResponse.json({ data });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
```

### Supabase Client 사용
```typescript
// Server Component
import { createClient } from '@/lib/supabase/server';

export default async function Page() {
  const supabase = createClient();
  const { data } = await supabase.from('politicians').select('*');
  return <div>{/* 렌더링 */}</div>;
}

// Client Component
'use client';
import { createClient } from '@/lib/supabase/client';

export default function ClientPage() {
  const supabase = createClient();
  // 클라이언트 로직
}
```

### 환경변수 관리
```bash
# .env.local (절대 커밋하지 않음)
NEXT_PUBLIC_SUPABASE_URL=your_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key
```

---

## 프로젝트 디렉토리 구조

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/              # API Routes
│   │   ├── politicians/      # 정치인 페이지
│   │   ├── auth/             # 인증 페이지
│   │   └── layout.tsx        # 루트 레이아웃
│   ├── components/           # 재사용 컴포넌트
│   ├── lib/
│   │   ├── supabase/         # Supabase 클라이언트
│   │   └── utils/            # 유틸리티
│   └── types/                # TypeScript 타입
├── public/                   # 정적 파일
└── tests/                    # 테스트 파일
```

---

## 코드 품질 기준

### 필수 사항
- [ ] TypeScript 타입 정의
- [ ] 에러 핸들링 구현
- [ ] 환경변수 사용
- [ ] 주석 작성 (복잡한 로직)
- [ ] 일관된 네이밍 컨벤션

### 베스트 프랙티스
- DRY (Don't Repeat Yourself)
- SOLID 원칙
- 컴포넌트 단위 분리
- 재사용 가능한 유틸리티
- 접근성 (a11y) 고려

---

## 작업 예시

### 작업 지시서 예시
```markdown
## P2A1: 정치인 목록 API 구현

**목표**: GET /api/politicians 엔드포인트 구현

**요구사항**:
- 페이지네이션 (page, limit)
- 필터링 (party, region)
- 정렬 (avg_rating)

**완료 기준**:
- [ ] API Route 생성
- [ ] 쿼리 파라미터 처리
- [ ] Supabase 연동
- [ ] 에러 핸들링
```

### 작업 결과 보고 예시
```markdown
=== 개발 완료 보고 ===

## 구현 내용
- GET /api/politicians 엔드포인트 구현
- 페이지네이션: page, limit 파라미터
- 필터링: party, region 파라미터
- 정렬: avg_rating DESC
- 에러 핸들링 및 로깅

## 생성/수정 파일
- frontend/src/app/api/politicians/route.ts (생성)
- frontend/src/types/politician.ts (생성)

## 테스트 결과
✅ http://localhost:3000/api/politicians?page=1&limit=10
✅ http://localhost:3000/api/politicians?party=테스트당
✅ 에러 케이스 (잘못된 파라미터) 처리 확인

## 주의사항
- 환경변수 NEXT_PUBLIC_SUPABASE_URL 필요
- RLS 정책이 활성화되어 있어야 함

## 다음 단계 제안
- 프론트엔드에서 이 API 호출하는 컴포넌트 개발
- 캐싱 전략 고려 (React Query or SWR)
```

---

## 보안 체크리스트

작업 완료 전 확인:
- [ ] SQL Injection 방어 (Supabase는 기본 제공)
- [ ] XSS 방어 (React는 기본 제공)
- [ ] 환경변수에 민감 정보 저장
- [ ] RLS (Row Level Security) 정책 확인
- [ ] CORS 설정 확인
- [ ] 인증 필요 엔드포인트 보호

---

## 문제 해결 가이드

### Supabase 연결 오류
```typescript
// 환경변수 확인
console.log('SUPABASE_URL:', process.env.NEXT_PUBLIC_SUPABASE_URL);

// 클라이언트 생성 확인
const supabase = createClient();
const { data, error } = await supabase.from('test').select('*');
console.log('Connection test:', { data, error });
```

### API Route 404 에러
- 파일 위치: `app/api/[path]/route.ts` 확인
- export 함수명: GET, POST, PUT, DELETE 대문자 확인
- 서버 재시작: `npm run dev` 다시 실행

### TypeScript 에러
```bash
# 타입 체크
npm run type-check

# 자동 수정
npm run lint -- --fix
```

---

## 성능 최적화

### 1. Database 쿼리
- 필요한 컬럼만 select
- 인덱스 활용
- 페이지네이션 필수

### 2. Frontend
- React.memo로 불필요한 리렌더링 방지
- 이미지 최적화 (Next.js Image)
- Code splitting (dynamic import)

### 3. API
- 응답 캐싱 (Cache-Control 헤더)
- 압축 (gzip)
- Rate limiting 고려

---

## 작업 시작 전 체크리스트

- [ ] 프로젝트 디렉토리 구조 이해
- [ ] 환경변수 설정 확인
- [ ] 의존성 설치 완료 (`npm install`)
- [ ] 로컬 서버 실행 가능 (`npm run dev`)
- [ ] Supabase 연결 확인
- [ ] AI-only 원칙 숙지

---

## 참고 문서

- [Next.js 공식 문서](https://nextjs.org/docs)
- [Supabase 공식 문서](https://supabase.com/docs)
- [프로젝트 AI-only 개발 원칙](../../../3DProjectGrid_v7.0_WORK/기획문서/AI-only_개발_원칙.md)

---

**이 스킬을 활성화하면, 위 원칙과 가이드를 철저히 따르며 PoliticianFinder 프로젝트를 개발합니다.**
