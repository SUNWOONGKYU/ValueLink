# S2F2: Valuation Submission Forms Template & 5 Method Pages

## Task 정보

- **Task ID**: S2F2
- **Task Name**: 평가 신청 폼 템플릿 및 5개 방법별 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S2F1 (결과 페이지 타입 정의)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

5개 평가 방법(DCF, Relative, Asset, Intrinsic, Tax)별 신청 폼을 구현하여 사용자가 평가에 필요한 데이터를 입력할 수 있도록 함

---

## 상세 지시사항

### 0. 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase 클라이언트 설정 완료

**S2F1 완료 확인:**
- `types/valuation.ts` 파일 존재 (타입 재사용)

---

### 1. 폼 입력 타입 정의

**파일**: `types/valuation-forms.ts`

```typescript
// 공통 프로젝트 정보
export interface ProjectInfo {
  project_name: string
  company_name: string
  industry: string
  valuation_method: 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
  description?: string
}

// DCF 입력 폼
export interface DCFFormData extends ProjectInfo {
  valuation_method: 'dcf'
  revenue_5years: number[] // 5년 매출 예측
  operating_margin: number // 영업이익률
  tax_rate: number // 법인세율
  wacc: number // 가중평균자본비용
  terminal_growth_rate: number // 영구성장률
  net_debt: number // 순부채
  shares_outstanding: number // 발행주식수
}

// Relative 입력 폼
export interface RelativeFormData extends ProjectInfo {
  valuation_method: 'relative'
  revenue: number // 매출
  ebitda: number // EBITDA
  comparable_companies: Array<{
    name: string
    revenue_multiple: number
    ebitda_multiple: number
  }>
}

// Asset 입력 폼
export interface AssetFormData extends ProjectInfo {
  valuation_method: 'asset'
  current_assets: number // 유동자산
  non_current_assets: number // 비유동자산
  current_liabilities: number // 유동부채
  non_current_liabilities: number // 비유동부채
  adjustments: Array<{
    item: string
    amount: number
    reason: string
  }>
}

// Intrinsic 입력 폼
export interface IntrinsicFormData extends ProjectInfo {
  valuation_method: 'intrinsic'
  roe: number // 자기자본이익률
  book_value_per_share: number // 주당순자산가치
  growth_rate: number // 성장률
  market_price: number // 현재 시장가격
}

// Tax 입력 폼
export interface TaxFormData extends ProjectInfo {
  valuation_method: 'tax'
  method: 'net_asset' | 'earnings_multiple' | 'weighted_average'
  net_asset_value: number // 순자산가치
  earnings_value: number // 손익가치
  weight_net_asset?: number // 순자산가치 비중
  weight_earnings?: number // 손익가치 비중
}

// 폼 데이터 Union 타입
export type ValuationFormData = DCFFormData | RelativeFormData | AssetFormData | IntrinsicFormData | TaxFormData
```

---

### 2. 공통 폼 템플릿 컴포넌트

**파일**: `components/submission-form-template.tsx`

```typescript
'use client'

import { ReactNode, FormEvent } from 'react'
import Link from 'next/link'
import { ArrowLeft, Save, Send } from 'lucide-react'

interface SubmissionFormTemplateProps {
  method: 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
  title: string
  description: string
  children: ReactNode
  onSubmit: (e: FormEvent<HTMLFormElement>) => void
  onSaveDraft: () => void
  isSubmitting: boolean
}

export default function SubmissionFormTemplate({
  method,
  title,
  description,
  children,
  onSubmit,
  onSaveDraft,
  isSubmitting,
}: SubmissionFormTemplateProps) {
  const methodNames: Record<string, string> = {
    dcf: 'DCF (현금흐름할인법)',
    relative: 'Relative (상대가치평가)',
    asset: 'Asset (자산가치평가)',
    intrinsic: 'Intrinsic (내재가치평가)',
    tax: 'Tax (세법상평가)',
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <Link
              href="/projects/create"
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>뒤로</span>
            </Link>
            <div className="border-l pl-4">
              <h1 className="text-xl font-bold text-gray-900">{title}</h1>
              <p className="text-sm text-gray-500">{methodNames[method]}</p>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 폼 */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 안내 메시지 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">{description}</p>
        </div>

        <form onSubmit={onSubmit} className="space-y-6">
          {children}

          {/* 액션 버튼 */}
          <div className="flex justify-end gap-3 pt-6 border-t">
            <button
              type="button"
              onClick={onSaveDraft}
              disabled={isSubmitting}
              className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              <span>임시저장</span>
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span>{isSubmitting ? '제출 중...' : '제출하기'}</span>
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
```

---

### 3. 재사용 가능한 폼 컴포넌트

**파일**: `components/form-field.tsx`

```typescript
import { InputHTMLAttributes } from 'react'

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  helperText?: string
  required?: boolean
}

export function FormField({
  label,
  error,
  helperText,
  required,
  ...inputProps
}: FormFieldProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-600 ml-1">*</span>}
      </label>
      <input
        {...inputProps}
        className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      />
      {helperText && !error && (
        <p className="mt-1 text-sm text-gray-500">{helperText}</p>
      )}
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
}
```

---

### 4. DCF 신청 폼 페이지

**파일**: `app/valuation/submissions/dcf/page.tsx`

```typescript
'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import SubmissionFormTemplate from '@/components/submission-form-template'
import { FormField } from '@/components/form-field'
import { DCFFormData } from '@/types/valuation-forms'

export default function DCFSubmissionPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState<DCFFormData>({
    project_name: '',
    company_name: '',
    industry: '',
    valuation_method: 'dcf',
    revenue_5years: [0, 0, 0, 0, 0],
    operating_margin: 0.15,
    tax_rate: 0.22,
    wacc: 0.12,
    terminal_growth_rate: 0.03,
    net_debt: 0,
    shares_outstanding: 1000000,
  })

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const supabase = createClient()

      // 1. 프로젝트 생성
      const { data: project, error: projectError } = await supabase
        .from('projects')
        .insert({
          project_name: formData.project_name,
          valuation_method: 'dcf',
          status: 'pending',
          current_step: 1,
        })
        .select()
        .single()

      if (projectError) throw projectError

      // 2. 입력 데이터 저장 (documents 테이블에 JSON으로 저장)
      const { error: dataError } = await supabase.from('documents').insert({
        project_id: project.project_id,
        document_type: 'input_data',
        file_name: 'dcf_input.json',
        file_path: JSON.stringify(formData),
      })

      if (dataError) throw dataError

      // 3. 성공 시 프로젝트 상세 페이지로 이동
      router.push(`/projects/${project.project_id}`)
    } catch (error) {
      console.error('제출 실패:', error)
      alert('제출에 실패했습니다. 다시 시도해주세요.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSaveDraft = async () => {
    // TODO: 임시저장 기능 구현
    console.log('임시저장:', formData)
    alert('임시저장되었습니다.')
  }

  const handleRevenueChange = (index: number, value: string) => {
    const newRevenue = [...formData.revenue_5years]
    newRevenue[index] = parseFloat(value) || 0
    setFormData({ ...formData, revenue_5years: newRevenue })
  }

  return (
    <SubmissionFormTemplate
      method="dcf"
      title="DCF 평가 신청"
      description="현금흐름할인법(DCF)은 미래 현금흐름을 현재가치로 할인하여 기업가치를 평가합니다. 5년간의 매출 예측과 할인율 정보를 입력해주세요."
      onSubmit={handleSubmit}
      onSaveDraft={handleSaveDraft}
      isSubmitting={isSubmitting}
    >
      {/* 프로젝트 기본 정보 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          프로젝트 정보
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            label="프로젝트명"
            required
            value={formData.project_name}
            onChange={(e) =>
              setFormData({ ...formData, project_name: e.target.value })
            }
            placeholder="예: ABC 스타트업 기업가치평가"
          />
          <FormField
            label="기업명"
            required
            value={formData.company_name}
            onChange={(e) =>
              setFormData({ ...formData, company_name: e.target.value })
            }
            placeholder="예: ABC 주식회사"
          />
          <FormField
            label="산업분야"
            required
            value={formData.industry}
            onChange={(e) =>
              setFormData({ ...formData, industry: e.target.value })
            }
            placeholder="예: AI, 헬스케어, 핀테크"
          />
        </div>
      </div>

      {/* 5년 매출 예측 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          5년 매출 예측 (백만원)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[1, 2, 3, 4, 5].map((year) => (
            <FormField
              key={year}
              label={`${year}년차`}
              type="number"
              required
              value={formData.revenue_5years[year - 1]}
              onChange={(e) => handleRevenueChange(year - 1, e.target.value)}
              placeholder="0"
            />
          ))}
        </div>
      </div>

      {/* 주요 가정 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">주요 가정</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            label="영업이익률"
            type="number"
            step="0.01"
            required
            value={formData.operating_margin}
            onChange={(e) =>
              setFormData({
                ...formData,
                operating_margin: parseFloat(e.target.value),
              })
            }
            helperText="0.15 = 15%"
          />
          <FormField
            label="법인세율"
            type="number"
            step="0.01"
            required
            value={formData.tax_rate}
            onChange={(e) =>
              setFormData({
                ...formData,
                tax_rate: parseFloat(e.target.value),
              })
            }
            helperText="0.22 = 22%"
          />
          <FormField
            label="가중평균자본비용 (WACC)"
            type="number"
            step="0.01"
            required
            value={formData.wacc}
            onChange={(e) =>
              setFormData({ ...formData, wacc: parseFloat(e.target.value) })
            }
            helperText="0.12 = 12%"
          />
          <FormField
            label="영구성장률"
            type="number"
            step="0.01"
            required
            value={formData.terminal_growth_rate}
            onChange={(e) =>
              setFormData({
                ...formData,
                terminal_growth_rate: parseFloat(e.target.value),
              })
            }
            helperText="0.03 = 3%"
          />
          <FormField
            label="순부채 (백만원)"
            type="number"
            required
            value={formData.net_debt}
            onChange={(e) =>
              setFormData({
                ...formData,
                net_debt: parseFloat(e.target.value),
              })
            }
            helperText="부채 - 현금"
          />
          <FormField
            label="발행주식수"
            type="number"
            required
            value={formData.shares_outstanding}
            onChange={(e) =>
              setFormData({
                ...formData,
                shares_outstanding: parseFloat(e.target.value),
              })
            }
          />
        </div>
      </div>
    </SubmissionFormTemplate>
  )
}
```

---

### 5. Relative 신청 폼 페이지

**파일**: `app/valuation/submissions/relative/page.tsx`

```typescript
'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import SubmissionFormTemplate from '@/components/submission-form-template'
import { FormField } from '@/components/form-field'
import { RelativeFormData } from '@/types/valuation-forms'
import { Plus, Trash2 } from 'lucide-react'

export default function RelativeSubmissionPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState<RelativeFormData>({
    project_name: '',
    company_name: '',
    industry: '',
    valuation_method: 'relative',
    revenue: 0,
    ebitda: 0,
    comparable_companies: [
      { name: '', revenue_multiple: 0, ebitda_multiple: 0 },
    ],
  })

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const supabase = createClient()

      const { data: project, error: projectError } = await supabase
        .from('projects')
        .insert({
          project_name: formData.project_name,
          valuation_method: 'relative',
          status: 'pending',
          current_step: 1,
        })
        .select()
        .single()

      if (projectError) throw projectError

      const { error: dataError } = await supabase.from('documents').insert({
        project_id: project.project_id,
        document_type: 'input_data',
        file_name: 'relative_input.json',
        file_path: JSON.stringify(formData),
      })

      if (dataError) throw dataError

      router.push(`/projects/${project.project_id}`)
    } catch (error) {
      console.error('제출 실패:', error)
      alert('제출에 실패했습니다. 다시 시도해주세요.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSaveDraft = async () => {
    console.log('임시저장:', formData)
    alert('임시저장되었습니다.')
  }

  const addComparable = () => {
    setFormData({
      ...formData,
      comparable_companies: [
        ...formData.comparable_companies,
        { name: '', revenue_multiple: 0, ebitda_multiple: 0 },
      ],
    })
  }

  const removeComparable = (index: number) => {
    const newComparables = formData.comparable_companies.filter(
      (_, i) => i !== index
    )
    setFormData({ ...formData, comparable_companies: newComparables })
  }

  const updateComparable = (
    index: number,
    field: 'name' | 'revenue_multiple' | 'ebitda_multiple',
    value: string | number
  ) => {
    const newComparables = [...formData.comparable_companies]
    newComparables[index] = { ...newComparables[index], [field]: value }
    setFormData({ ...formData, comparable_companies: newComparables })
  }

  return (
    <SubmissionFormTemplate
      method="relative"
      title="Relative 평가 신청"
      description="상대가치평가는 유사기업의 배수를 활용하여 기업가치를 평가합니다. 기업의 재무정보와 유사기업 정보를 입력해주세요."
      onSubmit={handleSubmit}
      onSaveDraft={handleSaveDraft}
      isSubmitting={isSubmitting}
    >
      {/* 프로젝트 기본 정보 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          프로젝트 정보
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            label="프로젝트명"
            required
            value={formData.project_name}
            onChange={(e) =>
              setFormData({ ...formData, project_name: e.target.value })
            }
          />
          <FormField
            label="기업명"
            required
            value={formData.company_name}
            onChange={(e) =>
              setFormData({ ...formData, company_name: e.target.value })
            }
          />
          <FormField
            label="산업분야"
            required
            value={formData.industry}
            onChange={(e) =>
              setFormData({ ...formData, industry: e.target.value })
            }
          />
        </div>
      </div>

      {/* 재무정보 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">재무정보</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            label="매출 (백만원)"
            type="number"
            required
            value={formData.revenue}
            onChange={(e) =>
              setFormData({ ...formData, revenue: parseFloat(e.target.value) })
            }
          />
          <FormField
            label="EBITDA (백만원)"
            type="number"
            required
            value={formData.ebitda}
            onChange={(e) =>
              setFormData({ ...formData, ebitda: parseFloat(e.target.value) })
            }
          />
        </div>
      </div>

      {/* 유사기업 */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">유사기업</h2>
          <button
            type="button"
            onClick={addComparable}
            className="px-3 py-1 text-sm text-white bg-red-600 rounded hover:bg-red-700 flex items-center gap-1"
          >
            <Plus className="w-4 h-4" />
            <span>추가</span>
          </button>
        </div>
        <div className="space-y-4">
          {formData.comparable_companies.map((company, index) => (
            <div
              key={index}
              className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border border-gray-200 rounded-lg"
            >
              <FormField
                label="기업명"
                required
                value={company.name}
                onChange={(e) =>
                  updateComparable(index, 'name', e.target.value)
                }
                placeholder="예: 네이버"
              />
              <FormField
                label="매출 배수 (P/S)"
                type="number"
                step="0.1"
                required
                value={company.revenue_multiple}
                onChange={(e) =>
                  updateComparable(
                    index,
                    'revenue_multiple',
                    parseFloat(e.target.value)
                  )
                }
              />
              <FormField
                label="EBITDA 배수 (EV/EBITDA)"
                type="number"
                step="0.1"
                required
                value={company.ebitda_multiple}
                onChange={(e) =>
                  updateComparable(
                    index,
                    'ebitda_multiple',
                    parseFloat(e.target.value)
                  )
                }
              />
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={() => removeComparable(index)}
                  disabled={formData.comparable_companies.length === 1}
                  className="w-full px-3 py-2 text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>삭제</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </SubmissionFormTemplate>
  )
}
```

---

### 6. Asset, Intrinsic, Tax 신청 폼 페이지

나머지 3개 페이지는 위와 유사한 구조로 작성:

**파일**:
- `app/valuation/submissions/asset/page.tsx`
- `app/valuation/submissions/intrinsic/page.tsx`
- `app/valuation/submissions/tax/page.tsx`

**구조 패턴**:
1. 프로젝트 기본 정보 섹션 (공통)
2. 해당 평가 방법별 입력 필드
3. Supabase에 프로젝트 + documents 저장
4. 성공 시 `/projects/{project_id}` 이동

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `types/valuation-forms.ts` | 폼 입력 타입 정의 (5개 방법) | ~200줄 |
| `components/submission-form-template.tsx` | 공통 폼 템플릿 컴포넌트 | ~100줄 |
| `components/form-field.tsx` | 재사용 가능한 폼 필드 | ~30줄 |
| `app/valuation/submissions/dcf/page.tsx` | DCF 신청 폼 | ~250줄 |
| `app/valuation/submissions/relative/page.tsx` | Relative 신청 폼 | ~280줄 |
| `app/valuation/submissions/asset/page.tsx` | Asset 신청 폼 | ~200줄 |
| `app/valuation/submissions/intrinsic/page.tsx` | Intrinsic 신청 폼 | ~180줄 |
| `app/valuation/submissions/tax/page.tsx` | Tax 신청 폼 | ~200줄 |

**총 파일 수**: 8개
**총 라인 수**: ~1,440줄

---

## 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Icons**: lucide-react
- **Form Handling**: React Hooks (useState)

---

## 완료 기준

### 필수 (Must Have)

- [ ] 폼 타입 정의 파일 생성
- [ ] 공통 템플릿 및 FormField 컴포넌트 구현
- [ ] 5개 평가 방법별 신청 폼 구현
- [ ] Supabase에 프로젝트 생성 기능
- [ ] 입력 데이터 저장 기능 (documents 테이블)
- [ ] 폼 유효성 검사 (필수 필드)
- [ ] 제출 중 로딩 상태 표시
- [ ] 에러 핸들링

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 폼에서 데이터 입력 가능
- [ ] Supabase에 프로젝트 정상 생성
- [ ] 제출 후 프로젝트 상세 페이지 이동
- [ ] 반응형 디자인 (모바일/데스크톱)

### 권장 (Nice to Have)

- [ ] 실시간 폼 유효성 검사
- [ ] 임시저장 기능 완성
- [ ] 자동완성/제안 기능
- [ ] 입력 필드 툴팁

---

## 참조

### 기존 프로토타입

- `Valuation_Company/valuation-platform/frontend/app/valuation/submissions/dcf-submission.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/submissions/relative-submission.html`

### 관련 Task

- **S1BI1**: Next.js 프로젝트 초기화
- **S1D1**: Database Schema (projects, documents 테이블)
- **S2F1**: 결과 페이지 타입 정의
- **S2BA2**: Projects API (프로젝트 생성 로직)

---

## 주의사항

1. **데이터 타입 안전성**
   - TypeScript 타입 엄격히 정의
   - 필수 필드 유효성 검사

2. **사용자 경험**
   - 명확한 레이블 및 도움말 텍스트
   - 에러 메시지 친절하게 표시
   - 제출 중 버튼 비활성화

3. **데이터 저장**
   - documents 테이블에 JSON 형식 저장
   - 프로젝트 생성 후 입력 데이터 연결

4. **보안**
   - RLS 정책으로 본인 프로젝트만 생성
   - SQL Injection 방지 (Supabase 자동 처리)

5. **TODO 항목**
   - 임시저장 기능은 향후 구현
   - 파일 업로드는 S2BA3에서 구현

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 8개
**라인 수**: ~1,440줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
