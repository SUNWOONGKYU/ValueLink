# S5F8: UX Improvement (Toast & Loading Indicator)

## Task 정보
- **Task ID**: S5F8
- **Task Name**: UX 개선 (Toast 및 로딩 인디케이터)
- **Stage**: S5 (Finalization - 개발 마무리)
- **Area**: F (Frontend)
- **Dependencies**: S5T1

## Task 목표

S5T1 통합 테스트에서 발견된 2가지 UX 이슈를 개선하여 사용자 경험을 향상시킵니다.

**발견된 이슈:**
1. **Toast 메시지 자동 숨김 시간 너무 짧음** (2초 → 4초 권장)
2. **DCF 평가 실행 중 로딩 인디케이터 누락** (7-8초 대기 시간)

**개선 목표:**
- 완성도 +1점 (17 → 18)

---

## 생성/수정 파일

| 파일 | 변경 내용 | 저장 위치 |
|------|----------|----------|
| `toast.tsx` | Toast 컴포넌트 생성 (자동 숨김 4초) | `Process/S5_개발_마무리/Frontend/app/components/ui/toast.tsx` |
| `loading-indicator.tsx` | 로딩 인디케이터 컴포넌트 생성 | `Process/S5_개발_마무리/Frontend/app/components/ui/loading-indicator.tsx` |

**Pre-commit Hook 자동 복사:**
- `toast.tsx` → `app/components/ui/toast.tsx`
- `loading-indicator.tsx` → `app/components/ui/loading-indicator.tsx`

---

## 개선 항목 상세

### 1. Toast 컴포넌트 개선 ⭐

**현재 문제:**
- 자동 숨김 시간: 2초 (사용자가 메시지를 읽기 어려움)

**개선 방안:**
```typescript
// app/components/ui/toast.tsx

'use client'

import { useEffect, useState } from 'react'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastProps {
  message: string
  type?: ToastType
  duration?: number // 기본값: 4000ms (4초)
  onClose?: () => void
}

export function Toast({ message, type = 'info', duration = 4000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      onClose?.()
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, onClose])

  if (!isVisible) return null

  const bgColors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500',
  }

  return (
    <div
      className={`fixed top-4 right-4 ${bgColors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in`}
      role="alert"
    >
      <p className="text-sm font-medium">{message}</p>
    </div>
  )
}
```

**핵심 변경:**
- `duration` 기본값: 2000ms → 4000ms (4초)
- `type` 지원: success, error, warning, info
- ARIA 접근성: `role="alert"` 추가

---

### 2. 로딩 인디케이터 컴포넌트 생성 ⭐

**현재 문제:**
- DCF 평가 실행 중 7-8초 대기 시간 동안 로딩 표시 없음
- 사용자가 "멈춘 것인가?" 불안감 느낌

**개선 방안:**
```typescript
// app/components/ui/loading-indicator.tsx

'use client'

export interface LoadingIndicatorProps {
  message?: string
  size?: 'sm' | 'md' | 'lg'
}

export function LoadingIndicator({ message = '평가 진행 중...', size = 'md' }: LoadingIndicatorProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  }

  return (
    <div className="flex flex-col items-center justify-center gap-4" role="status" aria-live="polite">
      {/* Spinner */}
      <div
        className={`${sizeClasses[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`}
        aria-hidden="true"
      />

      {/* Message */}
      {message && (
        <p className="text-sm text-gray-600 font-medium">{message}</p>
      )}

      {/* Screen reader text */}
      <span className="sr-only">{message}</span>
    </div>
  )
}
```

**핵심 기능:**
- 3가지 크기: sm, md, lg
- 커스텀 메시지 지원
- ARIA 접근성: `role="status"`, `aria-live="polite"`, `sr-only`

---

### 3. DCF 평가 페이지 적용

**수정 대상 파일** (기존 파일 수정, 새 파일 아님):
- `app/(valuation)/valuation/dcf/page.tsx`

**적용 위치:**
```typescript
// DCF 평가 실행 버튼 클릭 시

import { LoadingIndicator } from '@/app/components/ui/loading-indicator'
import { Toast } from '@/app/components/ui/toast'

const [isCalculating, setIsCalculating] = useState(false)
const [toast, setToast] = useState<{ message: string; type: ToastType } | null>(null)

async function handleCalculate() {
  setIsCalculating(true) // 로딩 시작

  try {
    const result = await calculateDCF(inputData)

    // 성공 Toast (4초 표시)
    setToast({ message: 'DCF 평가가 완료되었습니다.', type: 'success' })

  } catch (error) {
    // 에러 Toast (4초 표시)
    setToast({ message: '평가 중 오류가 발생했습니다.', type: 'error' })

  } finally {
    setIsCalculating(false) // 로딩 종료
  }
}

// JSX
{isCalculating && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-40">
    <div className="bg-white p-8 rounded-lg">
      <LoadingIndicator message="DCF 평가 진행 중..." size="lg" />
    </div>
  </div>
)}

{toast && (
  <Toast
    message={toast.message}
    type={toast.type}
    onClose={() => setToast(null)}
  />
)}
```

**핵심 변경:**
- 평가 실행 중: 전체 화면 오버레이 + 로딩 인디케이터
- 평가 완료 시: 4초 Toast 메시지
- 에러 발생 시: 4초 에러 Toast

---

## 검증 기준

### 1. Toast 컴포넌트
- [ ] Toast 자동 숨김 시간 4초 확인
- [ ] 4가지 타입 (success, error, warning, info) 정상 작동
- [ ] ARIA 접근성 속성 포함 (`role="alert"`)
- [ ] 애니메이션 부드러움

### 2. 로딩 인디케이터
- [ ] 3가지 크기 (sm, md, lg) 정상 렌더링
- [ ] 커스텀 메시지 표시
- [ ] ARIA 접근성 속성 포함 (`role="status"`, `aria-live`)
- [ ] 회전 애니메이션 부드러움

### 3. DCF 페이지 통합
- [ ] 평가 실행 시 로딩 인디케이터 표시
- [ ] 평가 완료 시 성공 Toast 표시 (4초)
- [ ] 에러 발생 시 에러 Toast 표시 (4초)
- [ ] 전체 화면 오버레이 정상 작동

---

## 예상 결과

**개선 전:**
- Toast 2초 (너무 빠름)
- DCF 평가 중 로딩 표시 없음

**개선 후:**
- Toast 4초 (사용자가 읽기 충분한 시간)
- DCF 평가 중 로딩 인디케이터 표시 (7-8초 대기 시간 안심)

**품질 향상:**
- 완성도: 17/20 → 18/20 (+1점)

---

## 참고 사항

1. **기존 파일 수정 최소화**: DCF 페이지만 수정, 다른 페이지는 건드리지 않음
2. **재사용 가능한 컴포넌트**: Toast, LoadingIndicator는 다른 페이지에서도 사용 가능
3. **접근성 우선**: ARIA 속성 필수 포함
4. **성능 최적화**: useEffect 클린업 함수로 메모리 누수 방지

---

**작성자**: Main Agent
**작성일**: 2026-02-23
**버전**: 1.0
