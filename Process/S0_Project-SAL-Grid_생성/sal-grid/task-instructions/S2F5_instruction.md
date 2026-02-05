# S2F5: Process Step Template & 12 Workflow Pages

## Task 정보

- **Task ID**: S2F5
- **Task Name**: 프로세스 단계 템플릿 및 12개 워크플로우 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S2BA1 (14단계 워크플로우 API)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

14단계 평가 워크플로우 중 12개 주요 단계 페이지를 구현하여 프로젝트 진행 상황을 시각화하고 각 단계별 액션 제공

---

## 상세 지시사항

### 0. 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨

**S2BA1 완료 확인 (선택적):**
- 워크플로우 API는 동시 개발 가능
- API 없이도 UI 먼저 구현 가능

---

### 1. 프로세스 단계 템플릿 컴포넌트

**파일**: `components/process-step-template.tsx`

```typescript
'use client'

import { ReactNode } from 'react'
import Link from 'next/link'
import { ArrowLeft, Check, Clock } from 'lucide-react'

interface Step {
  number: number
  title: string
  status: 'completed' | 'current' | 'upcoming'
}

interface ProcessStepTemplateProps {
  projectId: string
  projectName: string
  currentStep: number
  totalSteps: number
  stepTitle: string
  children: ReactNode
}

export default function ProcessStepTemplate({
  projectId,
  projectName,
  currentStep,
  totalSteps,
  stepTitle,
  children,
}: ProcessStepTemplateProps) {
  const steps: Step[] = [
    { number: 1, title: '프로젝트 생성', status: 'completed' },
    { number: 2, title: '견적 요청', status: 'completed' },
    { number: 3, title: '협상', status: 'completed' },
    { number: 4, title: '문서 업로드', status: 'completed' },
    { number: 5, title: '평가 진행', status: 'current' },
    { number: 6, title: '데이터 수집', status: 'upcoming' },
    { number: 7, title: '회계사 검토', status: 'upcoming' },
    { number: 8, title: '초안 생성', status: 'upcoming' },
    { number: 9, title: '초안 확인', status: 'upcoming' },
    { number: 10, title: '수정 요청', status: 'upcoming' },
    { number: 11, title: '최종 준비', status: 'upcoming' },
    { number: 12, title: '최종 보고서', status: 'upcoming' },
    { number: 13, title: '결제', status: 'upcoming' },
    { number: 14, title: '보고서 다운로드', status: 'upcoming' },
  ]

  // currentStep 기준으로 status 동적 설정
  const updatedSteps = steps.map((step) => ({
    ...step,
    status:
      step.number < currentStep
        ? 'completed'
        : step.number === currentStep
        ? 'current'
        : 'upcoming',
  })) as Step[]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <Link
              href={`/projects/${projectId}`}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>프로젝트로 돌아가기</span>
            </Link>
            <div className="border-l pl-4">
              <h1 className="text-xl font-bold text-gray-900">{projectName}</h1>
              <p className="text-sm text-gray-500">
                Step {currentStep}/{totalSteps} - {stepTitle}
              </p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* 프로세스 사이드바 */}
          <aside className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow p-4 sticky top-8">
              <h2 className="text-sm font-semibold text-gray-900 mb-4">
                진행 상황
              </h2>
              <div className="space-y-2">
                {updatedSteps.map((step, index) => (
                  <div key={step.number} className="relative">
                    {index < updatedSteps.length - 1 && (
                      <div
                        className={`absolute left-4 top-8 w-0.5 h-6 ${
                          step.status === 'completed'
                            ? 'bg-green-500'
                            : 'bg-gray-200'
                        }`}
                      />
                    )}
                    <div className="flex items-start gap-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          step.status === 'completed'
                            ? 'bg-green-500 text-white'
                            : step.status === 'current'
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-200 text-gray-500'
                        }`}
                      >
                        {step.status === 'completed' ? (
                          <Check className="w-4 h-4" />
                        ) : step.status === 'current' ? (
                          <Clock className="w-4 h-4" />
                        ) : (
                          <span className="text-xs">{step.number}</span>
                        )}
                      </div>
                      <div>
                        <p
                          className={`text-sm ${
                            step.status === 'current'
                              ? 'font-semibold text-red-600'
                              : step.status === 'completed'
                              ? 'text-gray-700'
                              : 'text-gray-400'
                          }`}
                        >
                          {step.title}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </aside>

          {/* 메인 콘텐츠 */}
          <main className="flex-1">{children}</main>
        </div>
      </div>
    </div>
  )
}
```

---

### 2. 평가 진행 페이지 (Step 5)

**파일**: `app/valuation/evaluation-progress/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import ProcessStepTemplate from '@/components/process-step-template'
import { TrendingUp, Clock, CheckCircle } from 'lucide-react'

export default function EvaluationProgressPage() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id')

  const [project, setProject] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!projectId) return

    async function loadProject() {
      const supabase = createClient()

      const { data } = await supabase
        .from('projects')
        .select('*')
        .eq('project_id', projectId)
        .single()

      setProject(data)
      setLoading(false)
    }

    loadProject()
  }, [projectId])

  if (loading || !project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  return (
    <ProcessStepTemplate
      projectId={projectId!}
      projectName={project.project_name}
      currentStep={5}
      totalSteps={14}
      stepTitle="평가 진행"
    >
      <div className="bg-white rounded-lg shadow p-8">
        <div className="flex items-center gap-3 mb-6">
          <TrendingUp className="w-8 h-8 text-red-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">평가 진행 중</h2>
            <p className="text-sm text-gray-500">
              회계사가 기업가치를 평가하고 있습니다.
            </p>
          </div>
        </div>

        {/* 진행 상태 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-blue-50 rounded-lg p-6">
            <Clock className="w-6 h-6 text-blue-600 mb-3" />
            <h3 className="text-sm font-medium text-blue-900 mb-1">
              예상 완료일
            </h3>
            <p className="text-2xl font-bold text-blue-600">3일 후</p>
          </div>
          <div className="bg-green-50 rounded-lg p-6">
            <CheckCircle className="w-6 h-6 text-green-600 mb-3" />
            <h3 className="text-sm font-medium text-green-900 mb-1">
              진행률
            </h3>
            <p className="text-2xl font-bold text-green-600">65%</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-6">
            <TrendingUp className="w-6 h-6 text-gray-600 mb-3" />
            <h3 className="text-sm font-medium text-gray-900 mb-1">
              평가 방법
            </h3>
            <p className="text-2xl font-bold text-gray-900">
              {project.valuation_method.toUpperCase()}
            </p>
          </div>
        </div>

        {/* 다음 단계 안내 */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            다음 단계
          </h3>
          <p className="text-gray-700 mb-4">
            평가가 완료되면 초안이 자동으로 생성됩니다. 생성된 초안을 검토하신 후
            수정 요청이나 승인을 진행하실 수 있습니다.
          </p>
          <button
            disabled
            className="px-6 py-2 text-white bg-gray-400 rounded-lg cursor-not-allowed"
          >
            평가 완료 대기 중...
          </button>
        </div>
      </div>
    </ProcessStepTemplate>
  )
}
```

---

### 3. 결제 페이지 (Step 13 - 무통장 입금)

**파일**: `app/valuation/deposit-payment/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import ProcessStepTemplate from '@/components/process-step-template'
import { CreditCard, Copy, CheckCircle } from 'lucide-react'

export default function DepositPaymentPage() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id')

  const [project, setProject] = useState<any>(null)
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!projectId) return

    async function loadProject() {
      const supabase = createClient()

      const { data } = await supabase
        .from('projects')
        .select('*')
        .eq('project_id', projectId)
        .single()

      setProject(data)
      setLoading(false)
    }

    loadProject()
  }, [projectId])

  const handleCopyAccountNumber = () => {
    navigator.clipboard.writeText('1005-404-483025')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading || !project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  return (
    <ProcessStepTemplate
      projectId={projectId!}
      projectName={project.project_name}
      currentStep={13}
      totalSteps={14}
      stepTitle="결제"
    >
      <div className="bg-white rounded-lg shadow p-8">
        <div className="flex items-center gap-3 mb-6">
          <CreditCard className="w-8 h-8 text-red-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">무통장 입금</h2>
            <p className="text-sm text-gray-500">
              아래 계좌로 입금 후 입금 확인 버튼을 클릭해주세요.
            </p>
          </div>
        </div>

        {/* 입금 정보 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            입금 계좌 정보
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-blue-800">은행</span>
              <span className="text-lg font-semibold text-blue-900">
                우리은행
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-blue-800">계좌번호</span>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-blue-900">
                  1005-404-483025
                </span>
                <button
                  onClick={handleCopyAccountNumber}
                  className="px-3 py-1 text-sm text-blue-700 bg-blue-100 rounded hover:bg-blue-200 flex items-center gap-1"
                >
                  {copied ? (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      <span>복사됨</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      <span>복사</span>
                    </>
                  )}
                </button>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-blue-800">예금주</span>
              <span className="text-lg font-semibold text-blue-900">
                호수회계법인
              </span>
            </div>
            <div className="flex justify-between items-center pt-3 border-t border-blue-300">
              <span className="text-sm text-blue-800">입금 금액</span>
              <span className="text-2xl font-bold text-red-600">
                8,000,000원
              </span>
            </div>
          </div>
        </div>

        {/* 주의사항 */}
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            주의사항
          </h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• 입금자명은 프로젝트명 또는 기업명으로 입력해주세요.</li>
            <li>• 입금 후 영업일 기준 1~2일 내 확인됩니다.</li>
            <li>
              • 입금 확인 후 세금계산서가 이메일로 발송됩니다.
            </li>
            <li>• 문의사항은 support@valuation.ai.kr로 연락주세요.</li>
          </ul>
        </div>

        {/* 액션 버튼 */}
        <button className="w-full px-6 py-3 text-white bg-red-600 rounded-lg hover:bg-red-700 font-semibold">
          입금 완료 확인 요청
        </button>
      </div>
    </ProcessStepTemplate>
  )
}
```

---

### 4. 나머지 10개 워크플로우 페이지

**파일**:
- `app/valuation/data-collection/page.tsx` (Step 6)
- `app/valuation/accountant-review/page.tsx` (Step 7)
- `app/valuation/draft-generation/page.tsx` (Step 8)
- `app/valuation/report-draft/page.tsx` (Step 9)
- `app/valuation/revision-request/page.tsx` (Step 10)
- `app/valuation/final-preparation/page.tsx` (Step 11)
- `app/valuation/report-final/page.tsx` (Step 12)
- `app/valuation/balance-payment/page.tsx` (Step 13 - 잔금)
- `app/valuation/payment/page.tsx` (Step 13 - 통합 결제)
- `app/valuation/report-download/page.tsx` (Step 14)

**공통 구조**:
1. ProcessStepTemplate 사용
2. 각 단계별 상태 표시
3. 다음 단계 액션 버튼

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `components/process-step-template.tsx` | 프로세스 템플릿 | ~200줄 |
| 12개 워크플로우 페이지 | 각 단계별 페이지 | ~150줄 × 12 = 1,800줄 |

**총 파일 수**: 13개
**총 라인 수**: ~2,000줄

---

## 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **Icons**: lucide-react

---

## 완료 기준

### 필수 (Must Have)

- [ ] 프로세스 템플릿 컴포넌트 구현
- [ ] 12개 워크플로우 페이지 구현
- [ ] 진행 상황 사이드바 동작
- [ ] 무통장 입금 페이지 (계좌정보 표시)
- [ ] 반응형 디자인

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 페이지 정상 렌더링
- [ ] 계좌번호 복사 기능 동작

### 권장 (Nice to Have)

- [ ] 입금 확인 자동화
- [ ] 실시간 상태 업데이트
- [ ] 알림 발송

---

## 참조

### 기존 프로토타입

- `Valuation_Company/valuation-platform/frontend/app/valuation/evaluation-progress.html`

### 관련 Task

- **S1BI1**: Next.js 초기화
- **S2BA1**: 14단계 워크플로우 API

---

## 주의사항

1. **무통장 입금 정보**
   - 계좌번호: 1005-404-483025 (우리은행)
   - 예금주: 호수회계법인
   - Stripe 결제 영원히 제외

2. **프로세스 흐름**
   - 단계 순서 엄격히 준수
   - 이전 단계 완료 전 다음 단계 진입 불가

3. **사용자 경험**
   - 현재 단계 명확히 표시
   - 다음 단계 안내 친절히

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 13개
**라인 수**: ~2,000줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
