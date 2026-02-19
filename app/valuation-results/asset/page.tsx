/**
 * @task S2F1
 * @description 자산가치 평가 (순자산가치법 NAV) 결과 페이지
 *
 * - React Server Component (async, NO 'use client')
 * - 자산/부채 항목별 장부가-시가조정-시가 테이블
 * - 순자산 요약, NAVPS 결과
 * - 할인/할증율 적용
 */

import { notFound } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import type { AssetResult, BalanceSheetItem } from '@/types/valuation'

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

export default async function AssetResultsPage({ searchParams }: PageProps) {
  const { project_id } = await searchParams

  if (!project_id) {
    notFound()
  }

  const supabase = await createClient()

  const { data, error } = await supabase
    .from('valuation_results')
    .select(
      'result_id, project_id, company_name, valuation_method, valuation_date, shares_outstanding, enterprise_value, equity_value, value_per_share, created_at, updated_at, current_assets, non_current_assets, current_liabilities, non_current_liabilities, totals, nav_discount_rate, navps_original, navps_adjusted'
    )
    .eq('project_id', project_id)
    .eq('valuation_method', 'asset')
    .order('created_at', { ascending: false })
    .limit(1)
    .single()

  if (error || !data) {
    notFound()
  }

  const result = data as unknown as AssetResult
  const { totals } = result

  return (
    <ValuationResultsTemplate
      method="asset"
      projectId={result.project_id}
      companyName={result.company_name}
      valuationDate={result.valuation_date}
    >
      {/* =============================== */}
      {/* 요약 카드                        */}
      {/* =============================== */}
      <section aria-label="자산가치 평가 요약">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <SummaryCard
            label="장부가 순자산"
            value={`${fmt(totals.nav_book)}백만원`}
          />
          <SummaryCard
            label="시가조정 합계"
            value={`${fmt(totals.total_assets_adjustment - totals.total_liabilities_adjustment)}백만원`}
          />
          <SummaryCard
            label="시가 순자산 (NAV)"
            value={`${fmt(totals.nav_market)}백만원`}
          />
          <SummaryCard
            label="조정 후 NAVPS"
            value={fmtWon(result.navps_adjusted)}
            highlight
          />
        </div>
      </section>

      {/* =============================== */}
      {/* 자산 평가 테이블                 */}
      {/* =============================== */}
      <section aria-label="자산 평가" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">자산 평가</h2>
          </div>
          <div className="p-6 overflow-x-auto">
            <table
              className="min-w-full text-sm"
              aria-label="자산 항목별 장부가/시가"
            >
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="py-3 px-4 text-left font-semibold text-gray-600 w-[35%]">
                    항목
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    장부가액
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    시가조정액
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    시가
                  </th>
                </tr>
              </thead>
              <tbody>
                {/* 유동자산 */}
                <CategoryHeader label="I. 유동자산" />
                {result.current_assets.map((item, i) => (
                  <BalanceRow key={`ca-${i}`} item={item} indent />
                ))}
                <SubtotalRow
                  label="유동자산 소계"
                  items={result.current_assets}
                />

                {/* 비유동자산 */}
                <CategoryHeader label="II. 비유동자산" />
                {result.non_current_assets.map((item, i) => (
                  <BalanceRow key={`nca-${i}`} item={item} indent />
                ))}
                <SubtotalRow
                  label="비유동자산 소계"
                  items={result.non_current_assets}
                />

                {/* 자산총계 */}
                <tr className="bg-blue-800 text-white font-bold">
                  <td className="py-3 px-4">자산총계</td>
                  <td className="py-3 px-4 text-right">
                    {fmt(totals.total_assets_book)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    {fmt(totals.total_assets_adjustment)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    {fmt(totals.total_assets_market)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 부채 평가 테이블                 */}
      {/* =============================== */}
      <section aria-label="부채 평가" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">부채 평가</h2>
          </div>
          <div className="p-6 overflow-x-auto">
            <table
              className="min-w-full text-sm"
              aria-label="부채 항목별 장부가/시가"
            >
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="py-3 px-4 text-left font-semibold text-gray-600 w-[35%]">
                    항목
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    장부가액
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    시가조정액
                  </th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">
                    시가
                  </th>
                </tr>
              </thead>
              <tbody>
                {/* 유동부채 */}
                <CategoryHeader label="I. 유동부채" />
                {result.current_liabilities.map((item, i) => (
                  <BalanceRow key={`cl-${i}`} item={item} indent />
                ))}
                <SubtotalRow
                  label="유동부채 소계"
                  items={result.current_liabilities}
                />

                {/* 비유동부채 */}
                <CategoryHeader label="II. 비유동부채" />
                {result.non_current_liabilities.map((item, i) => (
                  <BalanceRow key={`ncl-${i}`} item={item} indent />
                ))}
                <SubtotalRow
                  label="비유동부채 소계"
                  items={result.non_current_liabilities}
                />

                {/* 부채총계 */}
                <tr className="bg-blue-800 text-white font-bold">
                  <td className="py-3 px-4">부채총계</td>
                  <td className="py-3 px-4 text-right">
                    {fmt(totals.total_liabilities_book)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    {fmt(totals.total_liabilities_adjustment)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    {fmt(totals.total_liabilities_market)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 순자산 요약                      */}
      {/* =============================== */}
      <section aria-label="순자산 요약" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              순자산 요약
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <NavSummaryCard
                label="장부가 자산총계"
                value={fmt(totals.total_assets_book)}
              />
              <NavSummaryCard
                label="장부가 부채총계"
                value={fmt(totals.total_liabilities_book)}
              />
              <NavSummaryCard
                label="장부가 순자산"
                value={fmt(totals.nav_book)}
              />
              <NavSummaryCard
                label="시가 자산총계"
                value={fmt(totals.total_assets_market)}
              />
              <NavSummaryCard
                label="시가 부채총계"
                value={fmt(totals.total_liabilities_market)}
              />
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
                <p className="text-xs text-blue-600 mb-1">
                  시가 순자산 (NAV)
                </p>
                <p className="text-xl font-bold text-blue-800">
                  {fmt(totals.nav_market)}
                </p>
                <p className="text-xs text-blue-500">백만원</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* NAVPS 결과                       */}
      {/* =============================== */}
      <section aria-label="NAVPS 결과">
        <div className="bg-gradient-to-br from-blue-700 to-blue-900 rounded-xl p-6 sm:p-8 text-white">
          <h2 className="text-lg font-bold mb-6">자산가치 평가 결과</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <ResultWhiteCard label="장부가 순자산" value={`${fmt(totals.nav_book)}백만원`} />
            <ResultWhiteCard
              label="시가조정액 합계"
              value={`${fmt(totals.total_assets_adjustment - totals.total_liabilities_adjustment)}백만원`}
            />
            <ResultWhiteCard label="시가 순자산 (NAV)" value={`${fmt(totals.nav_market)}백만원`} />
            <ResultWhiteCard label="발행주식수" value={`${result.shares_outstanding.toLocaleString('ko-KR')}주`} />
          </div>
          <div className="bg-white/10 rounded-xl p-5 text-center mb-4">
            <p className="text-sm text-blue-200 mb-1">조정 전 NAVPS</p>
            <p className="text-3xl font-bold">{fmtWon(result.navps_original)}</p>
          </div>
          {result.nav_discount_rate !== 0 && (
            <div className="bg-white/15 rounded-xl p-5 text-center">
              <p className="text-sm text-blue-200 mb-1">
                조정 후 NAVPS (할인율 {result.nav_discount_rate}%)
              </p>
              <p className="text-4xl font-bold">
                {fmtWon(result.navps_adjusted)}
              </p>
            </div>
          )}
          {result.nav_discount_rate === 0 && (
            <div className="bg-white/15 rounded-xl p-5 text-center">
              <p className="text-sm text-blue-200 mb-1">최종 NAVPS</p>
              <p className="text-4xl font-bold">
                {fmtWon(result.navps_adjusted)}
              </p>
            </div>
          )}
        </div>
      </section>
    </ValuationResultsTemplate>
  )
}

// ---------------------------------------------------------------------------
// 서브 컴포넌트
// ---------------------------------------------------------------------------

function SummaryCard({
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
      <p className={`text-xs mb-1 ${highlight ? 'text-blue-200' : 'text-gray-500'}`}>
        {label}
      </p>
      <p className={`text-xl font-bold ${highlight ? 'text-white' : 'text-gray-900'}`}>
        {value}
      </p>
    </div>
  )
}

function CategoryHeader({ label }: { label: string }) {
  return (
    <tr className="bg-gray-50">
      <td colSpan={4} className="py-2 px-4 font-bold text-gray-800">
        {label}
      </td>
    </tr>
  )
}

function BalanceRow({
  item,
  indent = false,
}: {
  item: BalanceSheetItem
  indent?: boolean
}) {
  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50">
      <td className={`py-2 px-4 text-gray-700 ${indent ? 'pl-8' : ''}`}>
        {item.name}
      </td>
      <td className="py-2 px-4 text-right text-gray-900">
        {fmt(item.book_value)}
      </td>
      <td
        className={`py-2 px-4 text-right ${
          item.adjustment > 0
            ? 'text-green-600'
            : item.adjustment < 0
              ? 'text-red-600'
              : 'text-gray-500'
        }`}
      >
        {fmt(item.adjustment)}
      </td>
      <td className="py-2 px-4 text-right font-medium text-blue-700">
        {fmt(item.market_value)}
      </td>
    </tr>
  )
}

function SubtotalRow({
  label,
  items,
}: {
  label: string
  items: BalanceSheetItem[]
}) {
  const book = items.reduce((s, i) => s + i.book_value, 0)
  const adj = items.reduce((s, i) => s + i.adjustment, 0)
  const market = items.reduce((s, i) => s + i.market_value, 0)

  return (
    <tr className="bg-blue-50 font-semibold">
      <td className="py-2 px-4 text-blue-800">{label}</td>
      <td className="py-2 px-4 text-right text-blue-800">{fmt(book)}</td>
      <td className="py-2 px-4 text-right text-blue-800">{fmt(adj)}</td>
      <td className="py-2 px-4 text-right text-blue-800">{fmt(market)}</td>
    </tr>
  )
}

function NavSummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-xl p-4 text-center">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-400">백만원</p>
    </div>
  )
}

function ResultWhiteCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white/10 rounded-xl p-4 text-center">
      <p className="text-xs text-blue-200 mb-1">{label}</p>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  )
}
