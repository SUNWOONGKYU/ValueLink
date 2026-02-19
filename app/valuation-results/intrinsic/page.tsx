/**
 * @task S2F1
 * @description 본질가치 (자본시장법) 평가 결과 페이지
 *
 * - React Server Component (async, NO 'use client')
 * - 자산가치와 수익가치의 가중평균 (1 : 1.5)
 * - 본질가치 = (자산가치 x 1 + 수익가치 x 1.5) / 2.5
 * - 산출 내역 breakdown 테이블
 */

import { notFound } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import type { IntrinsicResult } from '@/types/valuation'

// ---------------------------------------------------------------------------
// 유틸
// ---------------------------------------------------------------------------

function fmt(value: number): string {
  return Math.round(value).toLocaleString('ko-KR')
}

function fmtWon(value: number): string {
  return `${fmt(value)}원`
}

// ---------------------------------------------------------------------------
// Page (Server Component)
// ---------------------------------------------------------------------------

interface PageProps {
  searchParams: Promise<{ project_id?: string }>
}

export default async function IntrinsicResultsPage({ searchParams }: PageProps) {
  const { project_id } = await searchParams

  if (!project_id) {
    notFound()
  }

  const supabase = await createClient()

  const { data, error } = await supabase
    .from('valuation_results')
    .select(
      'result_id, project_id, company_name, valuation_method, valuation_date, shares_outstanding, enterprise_value, equity_value, value_per_share, created_at, updated_at, industry, capitalization_rate, income_3years, nav_value, income_value, per_share_income_value, per_share_asset_value, asset_weight, income_weight, intrinsic_value_per_share'
    )
    .eq('project_id', project_id)
    .eq('valuation_method', 'intrinsic')
    .order('created_at', { ascending: false })
    .limit(1)
    .single()

  if (error || !data) {
    notFound()
  }

  const result = data as unknown as IntrinsicResult

  return (
    <ValuationResultsTemplate
      method="intrinsic"
      projectId={result.project_id}
      companyName={result.company_name}
      valuationDate={result.valuation_date}
    >
      {/* =============================== */}
      {/* 공식                            */}
      {/* =============================== */}
      <div className="bg-green-50 border-2 border-green-300 rounded-xl p-6 text-center mb-8">
        <p className="text-lg font-bold text-green-800 mb-1">
          본질가치 = (자산가치 x {result.asset_weight} + 수익가치 x{' '}
          {result.income_weight}) / {result.asset_weight + result.income_weight}
        </p>
        <p className="text-sm text-green-600">
          자본시장법 시행령 제176조의5에 따른 비상장주식 평가 공식
        </p>
      </div>

      {/* =============================== */}
      {/* 요약 카드                        */}
      {/* =============================== */}
      <section aria-label="본질가치 평가 요약">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <ResultCard
            label="1주당 수익가치"
            value={fmtWon(result.per_share_income_value)}
            sublabel={`가중치 ${result.income_weight}`}
          />
          <ResultCard
            label="1주당 자산가치"
            value={fmtWon(result.per_share_asset_value)}
            sublabel={`가중치 ${result.asset_weight}`}
          />
          <ResultCard
            label="1주당 본질가치"
            value={fmtWon(result.intrinsic_value_per_share)}
            sublabel={`= (자산 x ${result.asset_weight} + 수익 x ${result.income_weight}) / ${result.asset_weight + result.income_weight}`}
            highlight
          />
        </div>
      </section>

      {/* =============================== */}
      {/* 최근 3개년 순이익                */}
      {/* =============================== */}
      <section aria-label="최근 3개년 순이익" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              최근 3개년 순이익
            </h2>
          </div>
          <div className="p-6 overflow-x-auto">
            <table
              className="min-w-full text-sm"
              aria-label="3개년 순이익 데이터"
            >
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="py-3 px-4 text-left font-semibold text-gray-600">
                    구분
                  </th>
                  <th className="py-3 px-4 text-center font-semibold text-gray-600">
                    3년 전
                  </th>
                  <th className="py-3 px-4 text-center font-semibold text-gray-600">
                    2년 전
                  </th>
                  <th className="py-3 px-4 text-center font-semibold text-gray-600">
                    직전 연도
                  </th>
                  <th className="py-3 px-4 text-center font-semibold text-gray-600">
                    단순평균
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4 font-medium text-gray-900">
                    당기순이익
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700">
                    {fmt(result.income_3years.year1)}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700">
                    {fmt(result.income_3years.year2)}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700">
                    {fmt(result.income_3years.year3)}
                  </td>
                  <td className="py-3 px-4 text-center font-bold text-blue-700 bg-gray-50">
                    {fmt(result.income_3years.average)}
                  </td>
                </tr>
              </tbody>
            </table>
            <p className="text-xs text-gray-500 mt-2">단위: 백만원</p>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 산출 내역 (Breakdown)            */}
      {/* =============================== */}
      <section aria-label="본질가치 산출 내역" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              본질가치 산출 내역
            </h2>
          </div>
          <div className="p-6 overflow-x-auto">
            <table className="min-w-full text-sm" aria-label="산출 내역">
              <tbody>
                <BreakdownRow
                  label="3년 평균 순이익"
                  value={`${fmt(result.income_3years.average)}백만원`}
                />
                <BreakdownRow
                  label="자본환원율"
                  value={`${(result.capitalization_rate * 100).toFixed(1)}%`}
                />
                <BreakdownRow
                  label="수익가치 (평균순이익 / 자본환원율)"
                  value={`${fmt(result.income_value)}백만원`}
                />
                <BreakdownRow
                  label="순자산가치 (자산가치)"
                  value={`${fmt(result.nav_value)}백만원`}
                />
                <BreakdownRow
                  label="발행주식수"
                  value={`${result.shares_outstanding.toLocaleString('ko-KR')}주`}
                />
                <BreakdownRow
                  label="1주당 수익가치"
                  value={fmtWon(result.per_share_income_value)}
                  highlight
                />
                <BreakdownRow
                  label="1주당 자산가치"
                  value={fmtWon(result.per_share_asset_value)}
                  highlight
                />
                <BreakdownRow
                  label="가중치 (자산 : 수익)"
                  value={`${result.asset_weight} : ${result.income_weight}`}
                />
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 최종 결과                        */}
      {/* =============================== */}
      <section aria-label="최종 본질가치">
        <div className="bg-gradient-to-br from-blue-700 to-blue-900 rounded-xl p-6 sm:p-8 text-white">
          <h2 className="text-lg font-bold mb-6">
            본질가치(자본시장법) 평가 결과
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-xs text-blue-200 mb-1">
                1주당 수익가치 (가중치 {result.income_weight})
              </p>
              <p className="text-2xl font-bold">
                {fmtWon(result.per_share_income_value)}
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-xs text-blue-200 mb-1">
                1주당 자산가치 (가중치 {result.asset_weight})
              </p>
              <p className="text-2xl font-bold">
                {fmtWon(result.per_share_asset_value)}
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-xs text-blue-200 mb-1">수익가치 총액</p>
              <p className="text-2xl font-bold">
                {fmt(result.income_value)}백만원
              </p>
            </div>
          </div>
          <div className="bg-white/15 rounded-xl p-6 text-center">
            <p className="text-sm text-blue-200 mb-2">1주당 본질가치</p>
            <p className="text-4xl sm:text-5xl font-bold">
              {fmtWon(result.intrinsic_value_per_share)}
            </p>
            <p className="text-sm text-blue-300 mt-2">
              = (자산가치 x {result.asset_weight} + 수익가치 x{' '}
              {result.income_weight}) / {result.asset_weight + result.income_weight}
            </p>
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
  sublabel,
  highlight = false,
}: {
  label: string
  value: string
  sublabel: string
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
        className={`text-2xl font-bold ${
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

function BreakdownRow({
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
          ? 'bg-blue-50'
          : 'border-b border-gray-100 hover:bg-gray-50'
      }
    >
      <th
        className={`py-3 px-4 text-left font-medium ${
          highlight ? 'text-blue-800 font-semibold' : 'text-gray-700'
        }`}
      >
        {label}
      </th>
      <td
        className={`py-3 px-4 text-right font-medium ${
          highlight ? 'text-blue-800 font-bold' : 'text-gray-900'
        }`}
      >
        {value}
      </td>
    </tr>
  )
}
