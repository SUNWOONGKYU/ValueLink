/**
 * @task S2F1
 * @description 상대가치 평가 결과 페이지
 *
 * - React Server Component (async, NO 'use client')
 * - 유사기업 멀티플 비교 테이블 (PER, PBR, PSR, EV/EBITDA, EV/Sales)
 * - 비상장 할인 적용
 * - 한국어 숫자 포맷
 */

import { notFound } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import type { RelativeResult } from '@/types/valuation'

// ---------------------------------------------------------------------------
// 유틸
// ---------------------------------------------------------------------------

function fmt(value: number): string {
  return Math.round(value).toLocaleString('ko-KR')
}

function fmtWon(value: number): string {
  return `${fmt(value)}원`
}

function fmtMillions(value: number): string {
  return `${fmt(value)}백만원`
}

// ---------------------------------------------------------------------------
// Page (Server Component)
// ---------------------------------------------------------------------------

interface PageProps {
  searchParams: Promise<{ project_id?: string }>
}

export default async function RelativeResultsPage({ searchParams }: PageProps) {
  const { project_id } = await searchParams

  if (!project_id) {
    notFound()
  }

  const supabase = await createClient()

  const { data, error } = await supabase
    .from('valuation_results')
    .select(
      'result_id, project_id, company_name, valuation_method, valuation_date, shares_outstanding, enterprise_value, equity_value, value_per_share, created_at, updated_at, target_financials, comparable_companies, average_multiples, calc_method, weights, per_share_values, weighted_market_cap, liquidity_discount, discounted_value_per_share'
    )
    .eq('project_id', project_id)
    .eq('valuation_method', 'relative')
    .order('created_at', { ascending: false })
    .limit(1)
    .single()

  if (error || !data) {
    notFound()
  }

  const result = data as unknown as RelativeResult
  const { target_financials, comparable_companies, average_multiples, weights, per_share_values } = result

  return (
    <ValuationResultsTemplate
      method="relative"
      projectId={result.project_id}
      companyName={result.company_name}
      valuationDate={result.valuation_date}
    >
      {/* =============================== */}
      {/* 요약 카드                        */}
      {/* =============================== */}
      <section aria-label="상대가치 평가 요약">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          <ResultCard
            label="가중평균 주당가치"
            value={fmtWon(result.value_per_share)}
            highlight
          />
          {result.discounted_value_per_share != null &&
            result.liquidity_discount > 0 && (
              <ResultCard
                label={`비상장 할인 적용 (${result.liquidity_discount}%)`}
                value={fmtWon(result.discounted_value_per_share)}
                highlight
              />
            )}
          <ResultCard
            label="시가총액 (가중평균)"
            value={fmtMillions(result.weighted_market_cap)}
          />
        </div>
      </section>

      {/* =============================== */}
      {/* 멀티플별 주당가치                */}
      {/* =============================== */}
      <section aria-label="멀티플별 주당가치" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              멀티플별 주당가치
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              <MultipleValueCard
                name="PER"
                desc="주가수익비율"
                multiple={`${average_multiples.per.toFixed(1)}x`}
                perShare={fmtWon(per_share_values.per_value)}
                weight={`${(weights.per * 100).toFixed(0)}%`}
                active={weights.per > 0}
              />
              <MultipleValueCard
                name="PBR"
                desc="주가순자산비율"
                multiple={`${average_multiples.pbr.toFixed(1)}x`}
                perShare={fmtWon(per_share_values.pbr_value)}
                weight={`${(weights.pbr * 100).toFixed(0)}%`}
                active={weights.pbr > 0}
              />
              <MultipleValueCard
                name="PSR"
                desc="주가매출비율"
                multiple={`${average_multiples.psr.toFixed(1)}x`}
                perShare={fmtWon(per_share_values.psr_value)}
                weight={`${(weights.psr * 100).toFixed(0)}%`}
                active={weights.psr > 0}
              />
              <MultipleValueCard
                name="EV/EBITDA"
                desc="기업가치/EBITDA"
                multiple={`${average_multiples.ev_ebitda.toFixed(1)}x`}
                perShare={fmtWon(per_share_values.ev_ebitda_value)}
                weight={`${(weights.ev_ebitda * 100).toFixed(0)}%`}
                active={weights.ev_ebitda > 0}
              />
              <MultipleValueCard
                name="EV/Sales"
                desc="기업가치/매출"
                multiple={`${average_multiples.ev_sales.toFixed(1)}x`}
                perShare={fmtWon(per_share_values.ev_sales_value)}
                weight={`${(weights.ev_sales * 100).toFixed(0)}%`}
                active={weights.ev_sales > 0}
              />
            </div>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 유사기업 비교 테이블             */}
      {/* =============================== */}
      <section aria-label="유사기업 비교" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <h2 className="text-lg font-semibold text-gray-900">
              유사기업 (Peer Group)
            </h2>
            <span className="text-sm text-gray-500">
              산출 방식:{' '}
              {result.calc_method === 'median' ? '중앙값' : '산술평균'}
            </span>
          </div>
          <div className="p-6 overflow-x-auto">
            <table
              className="min-w-full text-sm"
              aria-label="유사기업 멀티플 비교"
            >
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="py-3 px-3 text-left font-semibold text-gray-600">
                    기업명
                  </th>
                  <th className="py-3 px-3 text-right font-semibold text-gray-600">
                    시가총액
                  </th>
                  <th className="py-3 px-3 text-center font-semibold text-gray-600">
                    PER
                  </th>
                  <th className="py-3 px-3 text-center font-semibold text-gray-600">
                    PBR
                  </th>
                  <th className="py-3 px-3 text-center font-semibold text-gray-600">
                    PSR
                  </th>
                  <th className="py-3 px-3 text-center font-semibold text-gray-600">
                    EV/EBITDA
                  </th>
                  <th className="py-3 px-3 text-center font-semibold text-gray-600">
                    EV/Sales
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparable_companies.map((co, i) => (
                  <tr
                    key={i}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="py-3 px-3 font-medium text-gray-900">
                      {co.name}
                    </td>
                    <td className="py-3 px-3 text-right text-gray-700">
                      {fmt(co.market_cap)}
                    </td>
                    <td className="py-3 px-3 text-center text-gray-700">
                      {co.per.toFixed(1)}
                    </td>
                    <td className="py-3 px-3 text-center text-gray-700">
                      {co.pbr.toFixed(1)}
                    </td>
                    <td className="py-3 px-3 text-center text-gray-700">
                      {co.psr.toFixed(1)}
                    </td>
                    <td className="py-3 px-3 text-center text-gray-700">
                      {co.ev_ebitda.toFixed(1)}
                    </td>
                    <td className="py-3 px-3 text-center text-gray-700">
                      {co.ev_sales.toFixed(1)}
                    </td>
                  </tr>
                ))}
                {/* 평균 행 */}
                <tr className="bg-blue-50 font-semibold">
                  <td className="py-3 px-3 text-blue-800">평균</td>
                  <td className="py-3 px-3 text-right text-blue-400">-</td>
                  <td className="py-3 px-3 text-center text-blue-800">
                    {average_multiples.per.toFixed(1)}
                  </td>
                  <td className="py-3 px-3 text-center text-blue-800">
                    {average_multiples.pbr.toFixed(1)}
                  </td>
                  <td className="py-3 px-3 text-center text-blue-800">
                    {average_multiples.psr.toFixed(1)}
                  </td>
                  <td className="py-3 px-3 text-center text-blue-800">
                    {average_multiples.ev_ebitda.toFixed(1)}
                  </td>
                  <td className="py-3 px-3 text-center text-blue-800">
                    {average_multiples.ev_sales.toFixed(1)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 평가 대상 재무지표               */}
      {/* =============================== */}
      <section aria-label="평가대상 재무지표">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              평가대상 기업 재무지표
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-6">
              <div>
                <p className="text-xs text-gray-500 mb-1">순이익</p>
                <p className="text-lg font-semibold text-gray-900">
                  {fmtMillions(target_financials.net_income)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">자기자본</p>
                <p className="text-lg font-semibold text-gray-900">
                  {fmtMillions(target_financials.equity)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">매출액</p>
                <p className="text-lg font-semibold text-gray-900">
                  {fmtMillions(target_financials.revenue)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">EBITDA</p>
                <p className="text-lg font-semibold text-gray-900">
                  {fmtMillions(target_financials.ebitda)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">순차입금</p>
                <p className="text-lg font-semibold text-gray-900">
                  {fmtMillions(target_financials.net_debt)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </ValuationResultsTemplate>
  )
}

// ---------------------------------------------------------------------------
// 서브 컴포넌트
// ---------------------------------------------------------------------------

function ResultCard({
  label,
  value,
  highlight = false,
}: {
  label: string
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
        className={`text-sm mb-2 ${
          highlight ? 'text-blue-200' : 'text-gray-500'
        }`}
      >
        {label}
      </p>
      <p
        className={`text-2xl font-bold ${
          highlight ? 'text-white' : 'text-gray-900'
        }`}
      >
        {value}
      </p>
    </div>
  )
}

function MultipleValueCard({
  name,
  desc,
  multiple,
  perShare,
  weight,
  active,
}: {
  name: string
  desc: string
  multiple: string
  perShare: string
  weight: string
  active: boolean
}) {
  return (
    <div
      className={`rounded-xl p-4 text-center border-2 ${
        active
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 bg-gray-50 opacity-60'
      }`}
    >
      <p className="font-bold text-gray-900">{name}</p>
      <p className="text-xs text-gray-500">{desc}</p>
      <p className="text-lg font-bold text-blue-700 mt-2">{multiple}</p>
      <p className="text-sm text-gray-700 mt-1">{perShare}</p>
      <p className="text-xs text-gray-500 mt-1">가중치: {weight}</p>
    </div>
  )
}
