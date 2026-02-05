# S2F1: Valuation Results Template & 5 Method Pages

## Task 정보

- **Task ID**: S2F1
- **Task Name**: 평가 결과 페이지 템플릿 및 5개 방법별 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S1D1 (DB 스키마)
- **Task Agent**: frontend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

5개 평가 방법(DCF, Relative, Asset, Intrinsic, Tax)별 결과 페이지를 구현하여 평가 완료 후 사용자에게 결과를 시각화하여 표시

---

## 상세 지시사항

### 0. 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트가 초기화되어 있어야 함
- `app/`, `components/`, `lib/`, `types/` 폴더 존재
- Supabase 클라이언트 설정 완료 (`lib/supabase/client.ts`)
- TypeScript 설정 완료 (`tsconfig.json`에 `@/*` alias)

**S1D1 완료 확인:**
- `valuation_results` 테이블 생성됨
- 평가 결과 데이터 스키마 정의됨

---

### 1. 타입 정의

**파일**: `types/valuation.ts`

```typescript
// 공통 평가 결과 타입
export interface BaseValuationResult {
  result_id: string
  project_id: string
  valuation_method: 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
  enterprise_value: number
  equity_value: number
  value_per_share: number
  created_at: string
  updated_at: string
}

// DCF 평가 결과
export interface DCFResult extends BaseValuationResult {
  valuation_method: 'dcf'
  calculation_data: {
    revenue_5years: number[]
    fcf_5years: number[]
    wacc: number
    terminal_growth_rate: number
    pv_fcf_sum: number
    terminal_value: number
    pv_terminal_value: number
    net_debt: number
  }
  sensitivity_analysis: {
    wacc_range: number[]
    growth_range: number[]
    value_matrix: number[][]
  }
}

// Relative 평가 결과
export interface RelativeResult extends BaseValuationResult {
  valuation_method: 'relative'
  calculation_data: {
    revenue: number
    ebitda: number
    comparable_companies: Array<{
      name: string
      revenue_multiple: number
      ebitda_multiple: number
    }>
    median_revenue_multiple: number
    median_ebitda_multiple: number
  }
}

// Asset 평가 결과
export interface AssetResult extends BaseValuationResult {
  valuation_method: 'asset'
  calculation_data: {
    assets: {
      current_assets: number
      non_current_assets: number
      total_assets: number
    }
    liabilities: {
      current_liabilities: number
      non_current_liabilities: number
      total_liabilities: number
    }
    net_asset_value: number
    adjustments: Array<{
      item: string
      amount: number
      reason: string
    }>
  }
}

// Intrinsic 평가 결과
export interface IntrinsicResult extends BaseValuationResult {
  valuation_method: 'intrinsic'
  calculation_data: {
    financial_metrics: {
      roe: number
      book_value_per_share: number
      growth_rate: number
    }
    valuation: {
      intrinsic_value_per_share: number
      market_price: number
      margin_of_safety: number
    }
  }
}

// Tax 평가 결과
export interface TaxResult extends BaseValuationResult {
  valuation_method: 'tax'
  calculation_data: {
    method: 'net_asset' | 'earnings_multiple' | 'weighted_average'
    net_asset_value: number
    earnings_value: number
    weight_net_asset: number
    weight_earnings: number
    supplementary_value: number
  }
}

// 평가 결과 Union 타입
export type ValuationResult = DCFResult | RelativeResult | AssetResult | IntrinsicResult | TaxResult
```

---

### 2. 공통 템플릿 컴포넌트

**파일**: `components/valuation-results-template.tsx`

```typescript
'use client'

import { ReactNode } from 'react'
import Link from 'next/link'
import { ArrowLeft, Download, Share2 } from 'lucide-react'

interface ValuationResultsTemplateProps {
  method: 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
  projectId: string
  projectName: string
  children: ReactNode
}

export default function ValuationResultsTemplate({
  method,
  projectId,
  projectName,
  children,
}: ValuationResultsTemplateProps) {
  const methodNames: Record<string, string> = {
    dcf: 'DCF (현금흐름할인법)',
    relative: 'Relative (상대가치평가)',
    asset: 'Asset (자산가치평가)',
    intrinsic: 'Intrinsic (내재가치평가)',
    tax: 'Tax (세법상평가)',
  }

  const handleDownloadPDF = () => {
    // TODO: S2BA3에서 구현될 PDF 다운로드 API 호출
    console.log('PDF 다운로드 시작:', projectId, method)
  }

  const handleShare = () => {
    // TODO: 공유 기능 구현
    console.log('결과 공유:', projectId, method)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href={`/projects/${projectId}`}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>프로젝트로 돌아가기</span>
              </Link>
              <div className="border-l pl-4">
                <h1 className="text-xl font-bold text-gray-900">
                  {methodNames[method]} 결과
                </h1>
                <p className="text-sm text-gray-500">{projectName}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleShare}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
              >
                <Share2 className="w-4 h-4" />
                <span>공유</span>
              </button>
              <button
                onClick={handleDownloadPDF}
                className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                <span>PDF 다운로드</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* 푸터 */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>
              이 평가 결과는 참고용이며, 최종 투자 결정 시 전문가 상담을
              권장합니다.
            </p>
            <p className="mt-2">© 2026 ValueLink. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
```

---

### 3. DCF 평가 결과 페이지

**파일**: `app/valuation/results/dcf/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import { DCFResult } from '@/types/valuation'
import { TrendingUp, DollarSign, Calendar } from 'lucide-react'

export default function DCFResultsPage() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id')

  const [result, setResult] = useState<DCFResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchResult() {
      const supabase = createClient()

      const { data, error: fetchError } = await supabase
        .from('valuation_results')
        .select('*')
        .eq('project_id', projectId)
        .eq('valuation_method', 'dcf')
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      if (fetchError) {
        setError('결과를 불러올 수 없습니다.')
        setLoading(false)
        return
      }

      setResult(data as DCFResult)
      setLoading(false)
    }

    fetchResult()
  }, [projectId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || '결과를 찾을 수 없습니다.'}</p>
        </div>
      </div>
    )
  }

  const { calculation_data, sensitivity_analysis } = result

  return (
    <ValuationResultsTemplate
      method="dcf"
      projectId={projectId!}
      projectName="프로젝트명" // TODO: projects 테이블에서 조회
    >
      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">기업가치</h3>
            <DollarSign className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {result.enterprise_value.toLocaleString('ko-KR')}원
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">자기자본가치</h3>
            <TrendingUp className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {result.equity_value.toLocaleString('ko-KR')}원
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">주당가치</h3>
            <Calendar className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {result.value_per_share.toLocaleString('ko-KR')}원
          </p>
        </div>
      </div>

      {/* 계산 상세 */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">계산 상세</h2>
        </div>
        <div className="p-6">
          {/* 5년 매출 예측 */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">5년 매출 예측</h3>
            <div className="grid grid-cols-5 gap-4">
              {calculation_data.revenue_5years.map((revenue, index) => (
                <div key={index} className="text-center">
                  <p className="text-xs text-gray-500 mb-1">Year {index + 1}</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {revenue.toLocaleString('ko-KR')}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* 잉여현금흐름 (FCF) */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">
              잉여현금흐름 (FCF)
            </h3>
            <div className="grid grid-cols-5 gap-4">
              {calculation_data.fcf_5years.map((fcf, index) => (
                <div key={index} className="text-center">
                  <p className="text-xs text-gray-500 mb-1">Year {index + 1}</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {fcf.toLocaleString('ko-KR')}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* 주요 가정 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-gray-500 mb-1">WACC</p>
              <p className="text-lg font-semibold text-gray-900">
                {(calculation_data.wacc * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">영구성장률</p>
              <p className="text-lg font-semibold text-gray-900">
                {(calculation_data.terminal_growth_rate * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">터미널가치 (PV)</p>
              <p className="text-lg font-semibold text-gray-900">
                {calculation_data.pv_terminal_value.toLocaleString('ko-KR')}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">순부채</p>
              <p className="text-lg font-semibold text-gray-900">
                {calculation_data.net_debt.toLocaleString('ko-KR')}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 민감도 분석 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">민감도 분석</h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    WACC / Growth
                  </th>
                  {sensitivity_analysis.growth_range.map((growth, index) => (
                    <th
                      key={index}
                      className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase"
                    >
                      {(growth * 100).toFixed(1)}%
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sensitivity_analysis.wacc_range.map((wacc, rowIndex) => (
                  <tr key={rowIndex}>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {(wacc * 100).toFixed(1)}%
                    </td>
                    {sensitivity_analysis.value_matrix[rowIndex].map(
                      (value, colIndex) => (
                        <td
                          key={colIndex}
                          className="px-4 py-3 text-sm text-center text-gray-700"
                        >
                          {value.toLocaleString('ko-KR')}
                        </td>
                      )
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </ValuationResultsTemplate>
  )
}
```

---

### 4. Relative 평가 결과 페이지

**파일**: `app/valuation/results/relative/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import { RelativeResult } from '@/types/valuation'
import { BarChart3, Users, TrendingUp } from 'lucide-react'

export default function RelativeResultsPage() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id')

  const [result, setResult] = useState<RelativeResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchResult() {
      const supabase = createClient()

      const { data, error: fetchError } = await supabase
        .from('valuation_results')
        .select('*')
        .eq('project_id', projectId)
        .eq('valuation_method', 'relative')
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      if (fetchError) {
        setError('결과를 불러올 수 없습니다.')
        setLoading(false)
        return
      }

      setResult(data as RelativeResult)
      setLoading(false)
    }

    fetchResult()
  }, [projectId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || '결과를 찾을 수 없습니다.'}</p>
        </div>
      </div>
    )
  }

  const { calculation_data } = result

  return (
    <ValuationResultsTemplate
      method="relative"
      projectId={projectId!}
      projectName="프로젝트명"
    >
      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">기업가치</h3>
            <BarChart3 className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {result.enterprise_value.toLocaleString('ko-KR')}원
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">매출 배수</h3>
            <TrendingUp className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {calculation_data.median_revenue_multiple.toFixed(2)}x
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">EBITDA 배수</h3>
            <Users className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {calculation_data.median_ebitda_multiple.toFixed(2)}x
          </p>
        </div>
      </div>

      {/* 유사기업 비교 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">유사기업 비교</h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    기업명
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    매출 배수 (P/S)
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    EBITDA 배수 (EV/EBITDA)
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {calculation_data.comparable_companies.map((company, index) => (
                  <tr key={index}>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {company.name}
                    </td>
                    <td className="px-4 py-3 text-sm text-center text-gray-700">
                      {company.revenue_multiple.toFixed(2)}x
                    </td>
                    <td className="px-4 py-3 text-sm text-center text-gray-700">
                      {company.ebitda_multiple.toFixed(2)}x
                    </td>
                  </tr>
                ))}
                <tr className="bg-gray-50 font-semibold">
                  <td className="px-4 py-3 text-sm text-gray-900">중앙값</td>
                  <td className="px-4 py-3 text-sm text-center text-red-600">
                    {calculation_data.median_revenue_multiple.toFixed(2)}x
                  </td>
                  <td className="px-4 py-3 text-sm text-center text-red-600">
                    {calculation_data.median_ebitda_multiple.toFixed(2)}x
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* 계산 근거 */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700 mb-3">계산 근거</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">매출</p>
                <p className="text-lg font-semibold text-gray-900">
                  {calculation_data.revenue.toLocaleString('ko-KR')}원
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">EBITDA</p>
                <p className="text-lg font-semibold text-gray-900">
                  {calculation_data.ebitda.toLocaleString('ko-KR')}원
                </p>
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-600">
              <p>
                기업가치 = (매출 × 매출배수 + EBITDA × EBITDA배수) ÷ 2
              </p>
            </div>
          </div>
        </div>
      </div>
    </ValuationResultsTemplate>
  )
}
```

---

### 5. Asset 평가 결과 페이지

**파일**: `app/valuation/results/asset/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import { AssetResult } from '@/types/valuation'
import { Wallet, CreditCard, PiggyBank } from 'lucide-react'

export default function AssetResultsPage() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id')

  const [result, setResult] = useState<AssetResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchResult() {
      const supabase = createClient()

      const { data, error: fetchError } = await supabase
        .from('valuation_results')
        .select('*')
        .eq('project_id', projectId)
        .eq('valuation_method', 'asset')
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      if (fetchError) {
        setError('결과를 불러올 수 없습니다.')
        setLoading(false)
        return
      }

      setResult(data as AssetResult)
      setLoading(false)
    }

    fetchResult()
  }, [projectId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || '결과를 찾을 수 없습니다.'}</p>
        </div>
      </div>
    )
  }

  const { calculation_data } = result

  return (
    <ValuationResultsTemplate
      method="asset"
      projectId={projectId!}
      projectName="프로젝트명"
    >
      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">순자산가치</h3>
            <PiggyBank className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {calculation_data.net_asset_value.toLocaleString('ko-KR')}원
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">총자산</h3>
            <Wallet className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {calculation_data.assets.total_assets.toLocaleString('ko-KR')}원
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">총부채</h3>
            <CreditCard className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {calculation_data.liabilities.total_liabilities.toLocaleString('ko-KR')}원
          </p>
        </div>
      </div>

      {/* 자산 상세 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">자산</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">유동자산</span>
                <span className="text-lg font-semibold text-gray-900">
                  {calculation_data.assets.current_assets.toLocaleString('ko-KR')}원
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">비유동자산</span>
                <span className="text-lg font-semibold text-gray-900">
                  {calculation_data.assets.non_current_assets.toLocaleString('ko-KR')}원
                </span>
              </div>
              <div className="pt-4 border-t flex justify-between items-center">
                <span className="text-sm font-medium text-gray-900">총자산</span>
                <span className="text-xl font-bold text-red-600">
                  {calculation_data.assets.total_assets.toLocaleString('ko-KR')}원
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">부채</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">유동부채</span>
                <span className="text-lg font-semibold text-gray-900">
                  {calculation_data.liabilities.current_liabilities.toLocaleString('ko-KR')}원
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">비유동부채</span>
                <span className="text-lg font-semibold text-gray-900">
                  {calculation_data.liabilities.non_current_liabilities.toLocaleString('ko-KR')}원
                </span>
              </div>
              <div className="pt-4 border-t flex justify-between items-center">
                <span className="text-sm font-medium text-gray-900">총부채</span>
                <span className="text-xl font-bold text-red-600">
                  {calculation_data.liabilities.total_liabilities.toLocaleString('ko-KR')}원
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 조정 사항 */}
      {calculation_data.adjustments.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">조정 사항</h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      항목
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                      금액
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      사유
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {calculation_data.adjustments.map((adj, index) => (
                    <tr key={index}>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {adj.item}
                      </td>
                      <td className="px-4 py-3 text-sm text-center text-gray-700">
                        {adj.amount >= 0 ? '+' : ''}
                        {adj.amount.toLocaleString('ko-KR')}원
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {adj.reason}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </ValuationResultsTemplate>
  )
}
```

---

### 6. Intrinsic 평가 결과 페이지

**파일**: `app/valuation/results/intrinsic/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import { IntrinsicResult } from '@/types/valuation'
import { TrendingUp, BookOpen, Shield } from 'lucide-react'

export default function IntrinsicResultsPage() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id')

  const [result, setResult] = useState<IntrinsicResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchResult() {
      const supabase = createClient()

      const { data, error: fetchError } = await supabase
        .from('valuation_results')
        .select('*')
        .eq('project_id', projectId)
        .eq('valuation_method', 'intrinsic')
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      if (fetchError) {
        setError('결과를 불러올 수 없습니다.')
        setLoading(false)
        return
      }

      setResult(data as IntrinsicResult)
      setLoading(false)
    }

    fetchResult()
  }, [projectId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || '결과를 찾을 수 없습니다.'}</p>
        </div>
      </div>
    )
  }

  const { calculation_data } = result
  const marginOfSafetyPercent =
    ((calculation_data.valuation.intrinsic_value_per_share -
      calculation_data.valuation.market_price) /
      calculation_data.valuation.intrinsic_value_per_share) *
    100

  return (
    <ValuationResultsTemplate
      method="intrinsic"
      projectId={projectId!}
      projectName="프로젝트명"
    >
      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">내재가치 (주당)</h3>
            <BookOpen className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {calculation_data.valuation.intrinsic_value_per_share.toLocaleString('ko-KR')}원
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">시장가격</h3>
            <TrendingUp className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {calculation_data.valuation.market_price.toLocaleString('ko-KR')}원
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">안전마진</h3>
            <Shield className="w-5 h-5 text-red-600" />
          </div>
          <p
            className={`text-2xl font-bold ${
              marginOfSafetyPercent > 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {marginOfSafetyPercent.toFixed(2)}%
          </p>
        </div>
      </div>

      {/* 재무 지표 */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">재무 지표</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">자기자본이익률 (ROE)</p>
              <p className="text-2xl font-semibold text-gray-900">
                {(calculation_data.financial_metrics.roe * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">주당순자산가치 (BPS)</p>
              <p className="text-2xl font-semibold text-gray-900">
                {calculation_data.financial_metrics.book_value_per_share.toLocaleString('ko-KR')}원
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">성장률</p>
              <p className="text-2xl font-semibold text-gray-900">
                {(calculation_data.financial_metrics.growth_rate * 100).toFixed(2)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 평가 해석 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">평가 해석</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div
              className={`p-4 rounded-lg ${
                marginOfSafetyPercent > 20
                  ? 'bg-green-50 border border-green-200'
                  : marginOfSafetyPercent > 0
                  ? 'bg-yellow-50 border border-yellow-200'
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              <h3 className="text-sm font-medium mb-2">
                {marginOfSafetyPercent > 20
                  ? '강력 매수 추천'
                  : marginOfSafetyPercent > 0
                  ? '매수 고려'
                  : '과대평가'}
              </h3>
              <p className="text-sm text-gray-700">
                {marginOfSafetyPercent > 20
                  ? '내재가치가 시장가격보다 20% 이상 높아 매우 저평가된 상태입니다.'
                  : marginOfSafetyPercent > 0
                  ? '내재가치가 시장가격보다 높지만, 안전마진이 충분하지 않을 수 있습니다.'
                  : '시장가격이 내재가치보다 높아 과대평가된 상태입니다.'}
              </p>
            </div>

            <div className="text-sm text-gray-600">
              <h3 className="font-medium mb-2">계산 방법</h3>
              <p>
                내재가치 = 주당순자산가치 × (1 + ROE × (1 - 배당성향)) ^
                예상기간
              </p>
              <p className="mt-2">
                안전마진 = (내재가치 - 시장가격) ÷ 내재가치 × 100
              </p>
            </div>
          </div>
        </div>
      </div>
    </ValuationResultsTemplate>
  )
}
```

---

### 7. Tax 평가 결과 페이지

**파일**: `app/valuation/results/tax/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import { TaxResult } from '@/types/valuation'
import { Calculator, Scale, FileText } from 'lucide-react'

export default function TaxResultsPage() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id')

  const [result, setResult] = useState<TaxResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchResult() {
      const supabase = createClient()

      const { data, error: fetchError } = await supabase
        .from('valuation_results')
        .select('*')
        .eq('project_id', projectId)
        .eq('valuation_method', 'tax')
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      if (fetchError) {
        setError('결과를 불러올 수 없습니다.')
        setLoading(false)
        return
      }

      setResult(data as TaxResult)
      setLoading(false)
    }

    fetchResult()
  }, [projectId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || '결과를 찾을 수 없습니다.'}</p>
        </div>
      </div>
    )
  }

  const { calculation_data } = result

  const methodNames: Record<string, string> = {
    net_asset: '순자산가치법',
    earnings_multiple: '손익가치법',
    weighted_average: '가중평균법',
  }

  return (
    <ValuationResultsTemplate
      method="tax"
      projectId={projectId!}
      projectName="프로젝트명"
    >
      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">세법상 평가액</h3>
            <FileText className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {result.enterprise_value.toLocaleString('ko-KR')}원
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">평가 방법</h3>
            <Calculator className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-lg font-semibold text-gray-900">
            {methodNames[calculation_data.method]}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">보충적 가치</h3>
            <Scale className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {calculation_data.supplementary_value.toLocaleString('ko-KR')}원
          </p>
        </div>
      </div>

      {/* 계산 상세 */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">계산 상세</h2>
        </div>
        <div className="p-6">
          <div className="space-y-6">
            {/* 순자산가치 */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">
                1. 순자산가치
              </h3>
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <span className="text-gray-700">순자산가치</span>
                <span className="text-xl font-semibold text-gray-900">
                  {calculation_data.net_asset_value.toLocaleString('ko-KR')}원
                </span>
              </div>
            </div>

            {/* 손익가치 */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">
                2. 손익가치
              </h3>
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <span className="text-gray-700">손익가치</span>
                <span className="text-xl font-semibold text-gray-900">
                  {calculation_data.earnings_value.toLocaleString('ko-KR')}원
                </span>
              </div>
            </div>

            {/* 가중평균 계산 */}
            {calculation_data.method === 'weighted_average' && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  3. 가중평균 계산
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">
                      순자산가치 비중
                    </span>
                    <span className="font-semibold text-gray-900">
                      {(calculation_data.weight_net_asset * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">
                      손익가치 비중
                    </span>
                    <span className="font-semibold text-gray-900">
                      {(calculation_data.weight_earnings * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-red-50 rounded-lg border border-red-200 mt-4">
                    <span className="font-medium text-gray-900">
                      가중평균 가치
                    </span>
                    <span className="text-xl font-bold text-red-600">
                      {(
                        calculation_data.net_asset_value * calculation_data.weight_net_asset +
                        calculation_data.earnings_value * calculation_data.weight_earnings
                      ).toLocaleString('ko-KR')}
                      원
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 세법 근거 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">세법 근거</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="text-sm font-medium text-blue-900 mb-2">
                상속세 및 증여세법 시행령 제54조 (비상장주식의 평가)
              </h3>
              <p className="text-sm text-blue-800">
                비상장주식의 가액은 1주당 순손익가치와 순자산가치를 각각 3과 2의
                비율로 가중평균한 금액으로 평가합니다.
              </p>
            </div>

            <div className="text-sm text-gray-600">
              <h3 className="font-medium mb-2">계산식</h3>
              <p>
                주당가치 = (순손익가치 × 3 + 순자산가치 × 2) ÷ 5
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">
                보충적 평가방법
              </h3>
              <p className="text-sm text-gray-700">
                장부가액, 매출액 등으로 평가한 가액이{' '}
                {calculation_data.supplementary_value.toLocaleString('ko-KR')}원
                입니다.
              </p>
            </div>
          </div>
        </div>
      </div>
    </ValuationResultsTemplate>
  )
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `types/valuation.ts` | 평가 결과 타입 정의 (5개 방법) | ~200줄 |
| `components/valuation-results-template.tsx` | 공통 템플릿 컴포넌트 | ~100줄 |
| `app/valuation/results/dcf/page.tsx` | DCF 평가 결과 페이지 | ~250줄 |
| `app/valuation/results/relative/page.tsx` | Relative 평가 결과 페이지 | ~200줄 |
| `app/valuation/results/asset/page.tsx` | Asset 평가 결과 페이지 | ~220줄 |
| `app/valuation/results/intrinsic/page.tsx` | Intrinsic 평가 결과 페이지 | ~230줄 |
| `app/valuation/results/tax/page.tsx` | Tax 평가 결과 페이지 | ~240줄 |

**총 파일 수**: 7개
**총 라인 수**: ~1,440줄

---

## 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Icons**: lucide-react
- **State Management**: React Hooks (useState, useEffect)

---

## 완료 기준

### 필수 (Must Have)

- [ ] 타입 정의 파일 생성 (`types/valuation.ts`)
- [ ] 공통 템플릿 컴포넌트 구현
- [ ] 5개 평가 방법별 페이지 구현 완료
- [ ] Supabase에서 데이터 정상 조회
- [ ] 로딩 상태 표시
- [ ] 에러 핸들링 구현
- [ ] 반응형 디자인 (모바일/데스크톱)

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 페이지가 올바른 데이터 표시
- [ ] PDF 다운로드 버튼 존재 (TODO 주석)
- [ ] 공유 버튼 존재 (TODO 주석)
- [ ] 브라우저 개발자 도구에서 에러 없음

### 권장 (Nice to Have)

- [ ] 차트 라이브러리 추가 (recharts, chart.js)
- [ ] 애니메이션 효과 (framer-motion)
- [ ] 인쇄 최적화 CSS
- [ ] 다크 모드 지원

---

## 참조

### 기존 프로토타입

- `Valuation_Company/valuation-platform/frontend/app/valuation/results/dcf-valuation.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/results/relative-valuation.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/results/asset-valuation.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/results/intrinsic-valuation.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/results/tax-valuation.html`

### 관련 Task

- **S1BI1**: Next.js 프로젝트 초기화 (의존성)
- **S1D1**: Database Schema (valuation_results 테이블)
- **S2BA3**: Documents & Reports API (PDF 다운로드)
- **S3BA1~S3BA4**: Valuation Engines (평가 데이터 생성)

---

## 주의사항

1. **데이터 타입 안전성**
   - TypeScript 타입을 엄격히 정의
   - Supabase 응답 데이터를 타입 캐스팅

2. **에러 처리**
   - project_id 누락 시 명확한 에러 메시지
   - Supabase 조회 실패 시 fallback UI

3. **성능 최적화**
   - 클라이언트 컴포넌트만 사용 (`'use client'`)
   - 데이터 캐싱은 향후 고려

4. **보안**
   - RLS 정책으로 데이터 접근 제어
   - 본인 프로젝트 결과만 조회 가능

5. **TODO 주석**
   - PDF 다운로드는 S2BA3에서 구현
   - 공유 기능은 향후 구현
   - 프로젝트명 조회는 projects 테이블 연동 필요

6. **디자인 일관성**
   - Tailwind CSS 클래스 재사용
   - 색상: Primary red-600, 보조 gray
   - 카드 그림자: shadow

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 7개
**라인 수**: ~1,440줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
