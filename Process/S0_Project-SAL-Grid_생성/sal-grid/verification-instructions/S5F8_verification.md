# S5F8 Verification Instruction

## Task 정보
- **Task ID**: S5F8
- **Task Name**: UX 개선 (Toast 및 로딩 인디케이터)
- **Verification Agent**: qa-specialist

---

## 검증 체크리스트

### 1. 파일 생성 확인

- [ ] `Process/S5_개발_마무리/Frontend/app/components/ui/toast.tsx` 존재
- [ ] `Process/S5_개발_마무리/Frontend/app/components/ui/loading-indicator.tsx` 존재
- [ ] 총 2개 파일 생성 확인

---

### 2. Toast 컴포넌트 검증

#### 2.1 기본 기능
- [ ] `duration` 기본값이 4000ms (4초)인가?
- [ ] 4가지 타입 지원 (success, error, warning, info)
- [ ] `onClose` 콜백 함수 정상 작동

#### 2.2 접근성
- [ ] `role="alert"` 속성 포함
- [ ] 색상 구분 명확 (success: 초록, error: 빨강, warning: 노랑, info: 파랑)

#### 2.3 코드 품질
- [ ] `'use client'` directive 포함 (Client Component)
- [ ] TypeScript 타입 정의 (ToastType, ToastProps)
- [ ] useEffect cleanup 함수로 메모리 누수 방지

**검증 방법:**
```typescript
// toast.tsx 내용 확인
- duration 기본값: 4000ms ✅
- role="alert" ✅
- bgColors 객체에 4개 타입 정의 ✅
- useEffect return () => clearTimeout(timer) ✅
```

---

### 3. 로딩 인디케이터 컴포넌트 검증

#### 3.1 기본 기능
- [ ] 3가지 크기 지원 (sm, md, lg)
- [ ] 커스텀 메시지 지원
- [ ] 기본 메시지: "평가 진행 중..."

#### 3.2 접근성
- [ ] `role="status"` 속성 포함
- [ ] `aria-live="polite"` 속성 포함
- [ ] `sr-only` 클래스로 스크린 리더 텍스트 제공

#### 3.3 코드 품질
- [ ] `'use client'` directive 포함
- [ ] TypeScript 타입 정의 (LoadingIndicatorProps)
- [ ] Tailwind CSS 애니메이션 (`animate-spin`)

**검증 방법:**
```typescript
// loading-indicator.tsx 내용 확인
- sizeClasses 객체에 sm, md, lg 정의 ✅
- role="status" ✅
- aria-live="polite" ✅
- <span className="sr-only"> 존재 ✅
```

---

### 4. 통합 테스트 (DCF 페이지 적용)

#### 4.1 파일 수정 확인
- [ ] `app/(valuation)/valuation/dcf/page.tsx` 파일 수정됨 (선택 사항)
- [ ] Toast, LoadingIndicator import 문 추가
- [ ] `isCalculating` 상태 변수 추가
- [ ] `toast` 상태 변수 추가

#### 4.2 동작 테스트 (수동 테스트 - PO)
- [ ] DCF 평가 실행 시 로딩 인디케이터 표시
- [ ] 평가 완료 시 성공 Toast 4초 표시
- [ ] 에러 발생 시 에러 Toast 4초 표시
- [ ] 전체 화면 오버레이 정상 작동

**검증 방법:**
```bash
# (수동 테스트 - PO가 수행)
1. npm run dev
2. 브라우저에서 DCF 평가 페이지 접속
3. "평가 실행" 버튼 클릭
4. 로딩 인디케이터 표시 확인 (7-8초)
5. 평가 완료 후 Toast 4초 표시 확인
```

---

### 5. 코드 스타일 검증

- [ ] 파일 상단에 Task ID 주석 (`@task S5F8`)
- [ ] 파일 설명 주석 포함
- [ ] 일관된 들여쓰기 (2 spaces)
- [ ] 변수명 명확 (camelCase)

**예시:**
```typescript
/**
 * @task S5F8
 * @description Toast 컴포넌트 - 자동 숨김 시간 4초
 */

'use client'

import { useEffect, useState } from 'react'

export type ToastType = 'success' | 'error' | 'warning' | 'info'
...
```

---

### 6. 빌드 & 타입 체크

- [ ] TypeScript 컴파일 성공
- [ ] Next.js 빌드 성공
- [ ] ESLint 경고 0개

**검증 방법:**
```bash
# TypeScript 타입 체크
npm run type-check

# Next.js 빌드
npm run build

# ESLint
npm run lint
```

**예상 결과:**
```
✓ Type checking complete (0 errors)
✓ Creating an optimized production build
✓ ESLint (0 warnings, 0 errors)
```

---

## 검증 결과 기록 형식

### Test Result
```json
{
  "unit_test": "PASS/FAIL - Toast duration 4s, LoadingIndicator 3 sizes",
  "integration_test": "PASS/FAIL - DCF 페이지 통합 테스트 (PO 수동)",
  "edge_cases": "PASS/FAIL - 접근성 속성 검증",
  "manual_test": "PENDING/PASS/FAIL - PO 브라우저 테스트"
}
```

### Build Verification
```json
{
  "compile": "PASS/FAIL - TypeScript 컴파일",
  "lint": "PASS/FAIL - ESLint 0 warnings",
  "deploy": "N/A - Frontend 컴포넌트",
  "runtime": "PASS/FAIL - 브라우저 렌더링"
}
```

### Integration Verification
```json
{
  "dependency_propagation": "PASS/FAIL - S5T1 이슈 해결",
  "cross_task_connection": "PASS/FAIL - DCF 페이지와 연동",
  "data_flow": "PASS/FAIL - 상태 관리 (isCalculating, toast)"
}
```

### Blockers
```json
{
  "dependency": "None/WARNING - 설명",
  "environment": "None/WARNING - 설명",
  "external_api": "None/WARNING - 설명",
  "status": "No Blockers / N Blockers"
}
```

### Comprehensive Verification
```json
{
  "task_instruction": "PASS/FAIL - 2개 파일 생성",
  "test": "PASS/FAIL - 접근성, 타입, 동작",
  "build": "PASS/FAIL - TypeScript, Next.js, ESLint",
  "integration": "PASS/FAIL - DCF 페이지 통합",
  "blockers": "None/N개",
  "final": "Verified / Needs Fix"
}
```

---

## PO 테스트 가이드

### 테스트 전 준비
1. `npm run dev` 실행
2. 브라우저에서 http://localhost:3000/valuation/dcf 접속

### 테스트 시나리오

#### 시나리오 1: Toast 4초 표시 확인
1. 평가 완료 후 성공 Toast 표시
2. 스톱워치로 4초 측정
3. 4초 후 자동 숨김 확인

**예상 결과**: Toast가 정확히 4초 동안 표시됨 ✅

#### 시나리오 2: 로딩 인디케이터 표시 확인
1. "평가 실행" 버튼 클릭
2. 즉시 전체 화면 오버레이 표시
3. 로딩 인디케이터 + "DCF 평가 진행 중..." 메시지 표시
4. 7-8초 대기
5. 평가 완료 후 오버레이 사라짐

**예상 결과**: 로딩 상태가 명확하게 표시됨 ✅

#### 시나리오 3: 에러 Toast 확인
1. 잘못된 입력값으로 평가 실행
2. 에러 Toast (빨간색) 표시
3. 4초 후 자동 숨김

**예상 결과**: 에러가 명확하게 전달됨 ✅

---

## 승인 기준

- ✅ 2개 파일 생성 완료
- ✅ Toast 자동 숨김 4초 확인
- ✅ 로딩 인디케이터 3가지 크기 지원
- ✅ 접근성 속성 포함 (ARIA)
- ✅ TypeScript 타입 체크 통과
- ✅ Next.js 빌드 성공
- ✅ ESLint 경고 0개
- ✅ PO 브라우저 테스트 통과

**최종 판정**: Verified / Needs Fix

---

**작성자**: Main Agent
**작성일**: 2026-02-23
**버전**: 1.0
