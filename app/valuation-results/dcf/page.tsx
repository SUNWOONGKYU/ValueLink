/**
 * @task S2F1
 * @description DCF (현금흐름할인법) 평가 결과 페이지
 *
 * - React Server Component (async, NO 'use client')
 * - Supabase 서버 클라이언트로 데이터 fetch
 * - 한국어 숫자 포맷 (toLocaleString('ko-KR'))
 * - 반응형 테이블 (overflow-x-auto)
 * - ARIA 레이블 접근성
 */

import { notFound } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import type { DCFResult } from '@/types/valuation'

// ---------------------------------------------------------------------------
// 유틸
// ---------------------------------------------------------------------------

/** 억 단위 포맷 (예: 123.4억) */
function formatBillions(value: number): string {
  const billions = value / 100_000_000
  if (Math.abs(billions) >= 10_000) {
    return `${(billions / 10_000).toFixed(2)}조`
  }
  if (Math.abs(billions) >= 1) {
    return `${billions.toFixed(1)}억`
  }
  return value.toLocaleString('ko-KR')
}

/** 원 포맷 */
function formatWon(value: number): string {
  return `${Math.round(value).toLocaleString('ko-KR')}원`
}

/** 퍼센트 포맷 */
function formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`
}

// ---------------------------------------------------------------------------
// Page (Server Component)
// ---------------------------------------------------------------------------

interface PageProps {
  searchParams: Promise<{ project_id?: string }>
}

export default async function DCFResultsPage({ searchParams }: PageProps) {
  const { project_id } = await searchParams

  if (!project_id) {
    notFound()
  }

  // --- Supabase 데이터 fetch ---
  const supabase = await createClient()

  const { data, error } = await supabase
    .from('valuation_results')
    .select(
      'result_id, project_id, company_name, valuation_method, valuation_date, shares_outstanding, enterprise_value, equity_value, value_per_share, created_at, updated_at, wacc_components, fcff_projections, terminal_growth_rate, terminal_value, pv_terminal_value, pv_fcff_sum, operating_value, non_operating_assets, interest_bearing_debt, sensitivity_analysis'
    )
    .eq('project_id', project_id)
    .eq('valuation_method', 'dcf')
    .order('created_at', { ascending: false })
    .limit(1)
    .single()

  if (error || !data) {
    notFound()
  }

  const result = data as unknown as DCFResult

  // --- Render ---
  return (
    <ValuationResultsTemplate
      method="dcf"
      projectId={result.project_id}
      companyName={result.company_name}
      valuationDate={result.valuation_date}
    >
      {/* =============================== */}
      {/* 요약 카드                        */}
      {/* =============================== */}
      <section aria-label="DCF 평가 요약">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <SummaryCard
            label="영업가치"
            sublabel="Operating Value"
            value={formatBillions(result.operating_value)}
          />
          <SummaryCard
            label="기업가치"
            sublabel="Enterprise Value"
            value={formatBillions(result.enterprise_value)}
          />
          <SummaryCard
            label="주식가치"
            sublabel="Equity Value"
            value={formatBillions(result.equity_value)}
          />
          <SummaryCard
            label="주당가치"
            sublabel="Value per Share"
            value={formatWon(result.value_per_share)}
            highlight
          />
        </div>
      </section>

      {/* =============================== */}
      {/* WACC 상세                        */}
      {/* =============================== */}
      <section aria-label="할인율 (WACC) 상세" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              할인율 (WACC)
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
              <MetricItem
                label="무위험이자율 (Rf)"
                value={formatPercent(result.wacc_components.risk_free_rate)}
              />
              <MetricItem
                label="시장위험프리미엄"
                value={formatPercent(result.wacc_components.market_risk_premium)}
              />
              <MetricItem
                label="베타 (Beta)"
                value={result.wacc_components.levered_beta.toFixed(2)}
              />
              <MetricItem
                label="규모 프리미엄"
                value={formatPercent(result.wacc_components.size_premium)}
              />
              <MetricItem
                label="자기자본비용"
                value={formatPercent(result.wacc_components.cost_of_equity)}
              />
              <MetricItem
                label="타인자본비용 (세후)"
                value={formatPercent(
                  result.wacc_components.cost_of_debt *
                    (1 - result.wacc_components.tax_rate)
                )}
              />
              <MetricItem
                label="자기자본 비중"
                value={formatPercent(result.wacc_components.equity_ratio)}
              />
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <p className="text-xs text-blue-600 mb-1">계산된 WACC</p>
                <p className="text-2xl font-bold text-blue-700">
                  {formatPercent(result.wacc_components.wacc)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* FCFF 현재가치 테이블             */}
      {/* =============================== */}
      <section aria-label="FCFF 현재가치" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              FCFF 현재가치
            </h2>
          </div>
          <div className="p-6 overflow-x-auto">
            <table
              className="min-w-full text-sm"
              aria-label="연도별 FCFF 현재가치"
            >
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="py-3 px-4 text-left font-semibold text-gray-600">
                    연도
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    매출액
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    FCFF
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    할인계수
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    현재가치
                  </th>
                </tr>
              </thead>
              <tbody>
                {result.fcff_projections.map((row) => (
                  <tr
                    key={row.year}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="py-3 px-4 text-gray-700">
                      {row.year}년차
                    </td>
                    <td className="py-3 px-4 text-right text-gray-900">
                      {formatBillions(row.revenue)}
                    </td>
                    <td className="py-3 px-4 text-right text-gray-900">
                      {formatBillions(row.fcff)}
                    </td>
                    <td className="py-3 px-4 text-right text-gray-600">
                      {row.discount_factor.toFixed(4)}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-gray-900">
                      {formatBillions(row.present_value)}
                    </td>
                  </tr>
                ))}
                {/* Terminal Value 행 */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-gray-700">Terminal</td>
                  <td className="py-3 px-4 text-right text-gray-400">-</td>
                  <td className="py-3 px-4 text-right text-gray-900">
                    {formatBillions(result.terminal_value)}
                  </td>
                  <td className="py-3 px-4 text-right text-gray-600">
                    {(
                      1 /
                      Math.pow(
                        1 + result.wacc_components.wacc,
                        result.fcff_projections.length
                      )
                    ).toFixed(4)}
                  </td>
                  <td className="py-3 px-4 text-right font-medium text-gray-900">
                    {formatBillions(result.pv_terminal_value)}
                  </td>
                </tr>
                {/* 합계 행 */}
                <tr className="bg-blue-50 font-semibold">
                  <td className="py-3 px-4 text-blue-800">합계</td>
                  <td className="py-3 px-4 text-right text-blue-400">-</td>
                  <td className="py-3 px-4 text-right text-blue-400">-</td>
                  <td className="py-3 px-4 text-right text-blue-400">-</td>
                  <td className="py-3 px-4 text-right text-blue-800">
                    {formatBillions(result.operating_value)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 가치 산출 테이블                 */}
      {/* =============================== */}
      <section aria-label="가치 산출" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">가치 산출</h2>
          </div>
          <div className="p-6 overflow-x-auto">
            <table className="min-w-full text-sm" aria-label="가치 산출 내역">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="py-3 px-4 text-left font-semibold text-gray-600">
                    항목
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    금액
                  </th>
                </tr>
              </thead>
              <tbody>
                <ValueRow
                  label="FCFF 현재가치 합계"
                  value={formatBillions(result.pv_fcff_sum)}
                />
                <ValueRow
                  label="Terminal Value 현재가치"
                  value={formatBillions(result.pv_terminal_value)}
                />
                <ValueRow
                  label="영업가치"
                  value={formatBillions(result.operating_value)}
                  highlight
                />
                <ValueRow
                  label="(+) 비영업자산"
                  value={formatBillions(result.non_operating_assets)}
                />
                <ValueRow
                  label="기업가치"
                  value={formatBillions(result.enterprise_value)}
                  highlight
                />
                <ValueRow
                  label="(-) 이자부부채"
                  value={formatBillions(result.interest_bearing_debt)}
                />
                <ValueRow
                  label="주식가치"
                  value={formatBillions(result.equity_value)}
                  highlight
                />
                <ValueRow
                  label="발행주식수"
                  value={`${result.shares_outstanding.toLocaleString('ko-KR')}주`}
                />
                <ValueRow
                  label="주당가치"
                  value={formatWon(result.value_per_share)}
                  highlight
                />
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 민감도 분석 (있을 경우)          */}
      {/* =============================== */}
      {result.sensitivity_analysis && (
        <section aria-label="민감도 분석">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900">
                민감도 분석
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                WACC과 영구성장률 변화에 따른 주당가치 (원)
              </p>
            </div>
            <div className="p-6 overflow-x-auto">
              <table
                className="min-w-full text-sm"
                aria-label="WACC/성장률 민감도 분석"
              >
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="py-3 px-3 text-left font-semibold text-gray-600">
                      WACC \ 성장률
                    </th>
                    {result.sensitivity_analysis.growth_range.map(
                      (g, i) => (
                        <th
                          key={i}
                          className="py-3 px-3 text-center font-semibold text-gray-600"
                        >
                          {formatPercent(g)}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {result.sensitivity_analysis.wacc_range.map(
                    (w, ri) => (
                      <tr
                        key={ri}
                        className="border-b border-gray-100 hover:bg-gray-50"
                      >
                        <td className="py-3 px-3 font-medium text-gray-900">
                          {formatPercent(w)}
                        </td>
                        {result.sensitivity_analysis!.value_matrix[ri].map(
                          (v, ci) => (
                            <td
                              key={ci}
                              className="py-3 px-3 text-center text-gray-700"
                            >
                              {Math.round(v).toLocaleString('ko-KR')}
                            </td>
                          )
                        )}
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}
    </ValuationResultsTemplate>
  )
}

// ---------------------------------------------------------------------------
// 서브 컴포넌트 (Server Component 내부)
// ---------------------------------------------------------------------------

function SummaryCard({
  label,
  sublabel,
  value,
  highlight = false,
}: {
  label: string
  sublabel: string
  value: string
  highlight?: boolean
}) {
  return (
    <div
      className={`rounded-xl p-5 text-center ${
        highlight
          ? 'bg-blue-700 text-white'
          : 'bg-white border border-gray-200 shadow-sm'
      }`}
    >
      <p
        className={`text-xs mb-1 ${
          highlight ? 'text-blue-200' : 'text-gray-500'
        }`}
      >
        {label}
      </p>
      <p
        className={`text-xl sm:text-2xl font-bold ${
          highlight ? 'text-white' : 'text-gray-900'
        }`}
      >
        {value}
      </p>
      <p
        className={`text-xs mt-1 ${
          highlight ? 'text-blue-300' : 'text-gray-400'
        }`}
      >
        {sublabel}
      </p>
    </div>
  )
}

function MetricItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-lg font-semibold text-gray-900">{value}</p>
    </div>
  )
}

function ValueRow({
  label,
  value,
  highlight = false,
}: {
  label: string
  value: string
  highlight?: boolean
}) {
  return (
    <tr
      className={
        highlight
          ? 'bg-blue-50 font-semibold'
          : 'border-b border-gray-100 hover:bg-gray-50'
      }
    >
      <td
        className={`py-3 px-4 ${
          highlight ? 'text-blue-800' : 'text-gray-700'
        }`}
      >
        {label}
      </td>
      <td
        className={`py-3 px-4 text-right ${
          highlight ? 'text-blue-800' : 'text-gray-900'
        }`}
      >
        {value}
      </td>
    </tr>
  )
}
