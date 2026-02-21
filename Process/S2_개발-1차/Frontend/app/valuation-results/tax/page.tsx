/**
 * @task S2F1
 * @description 상증세법 평가 (비상장주식 보충적 평가) 결과 페이지
 *
 * - React Server Component (async, NO 'use client')
 * - 일반법인: (순손익가치 x 3 + 순자산가치 x 2) / 5
 * - 부동산과다보유법인: (순손익가치 x 2 + 순자산가치 x 3) / 5
 * - 가중평균 순손익액 (1:2:3 가중)
 */

import { notFound } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import ValuationResultsTemplate from '@/components/valuation-results-template'
import type { TaxResult } from '@/types/valuation'

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

export default async function TaxResultsPage({ searchParams }: PageProps) {
  const { project_id } = await searchParams

  if (!project_id) {
    notFound()
  }

  const supabase = await createClient()

  const { data, error } = await supabase
    .from('valuation_results')
    .select(
      'result_id, project_id, company_name, valuation_method, valuation_date, shares_outstanding, enterprise_value, equity_value, value_per_share, created_at, updated_at, company_type, yearly_profits, weighted_avg_profit, discount_rate, profit_value_per_share, total_assets, total_liabilities, net_assets, asset_value_per_share, profit_weight, asset_weight, final_value_per_share'
    )
    .eq('project_id', project_id)
    .eq('valuation_method', 'tax')
    .order('created_at', { ascending: false })
    .limit(1)
    .single()

  if (error || !data) {
    notFound()
  }

  const result = data as unknown as TaxResult
  const isGeneral = result.company_type === 'general'

  return (
    <ValuationResultsTemplate
      method="tax"
      projectId={result.project_id}
      companyName={result.company_name}
      valuationDate={result.valuation_date}
    >
      {/* =============================== */}
      {/* 안내 박스                        */}
      {/* =============================== */}
      <div className="bg-blue-50 rounded-xl p-5 mb-6">
        <h3 className="text-sm font-semibold text-blue-800 mb-1">
          상증세법 보충적 평가방법
        </h3>
        <p className="text-sm text-blue-700 leading-relaxed">
          상속세 및 증여세법 제63조에 따른 비상장주식의 보충적 평가방법입니다.
          순손익가치와 순자산가치를 가중평균하여 1주당 가액을 산정합니다.
        </p>
      </div>

      <div className="bg-amber-50 rounded-xl p-5 mb-8">
        <h3 className="text-sm font-semibold text-amber-800 mb-1">
          적용 시 유의사항
        </h3>
        <p className="text-sm text-amber-700 leading-relaxed">
          본 평가방법은 세법상 보충적 평가방법으로, 시가가 있는 경우 시가를
          우선 적용합니다. 평가기준일 전후 3개월 이내 거래가액이 있는 경우
          해당 가액을 참고해야 합니다.
        </p>
      </div>

      {/* =============================== */}
      {/* 법인 유형                        */}
      {/* =============================== */}
      <section aria-label="법인 유형" className="mb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <TypeCard
            title="일반법인"
            formula="(순손익가치 x 3 + 순자산가치 x 2) / 5"
            active={isGeneral}
          />
          <TypeCard
            title="부동산과다보유법인 등"
            formula="(순손익가치 x 2 + 순자산가치 x 3) / 5"
            active={!isGeneral}
          />
        </div>
      </section>

      {/* =============================== */}
      {/* 순손익가치 산정                   */}
      {/* =============================== */}
      <section aria-label="순손익가치 산정" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              1주당 순손익가치 산정
            </h2>
          </div>
          <div className="p-6 overflow-x-auto">
            <table
              className="min-w-full text-sm"
              aria-label="연도별 순손익 데이터"
            >
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="py-3 px-4 text-left font-semibold text-gray-600">
                    항목
                  </th>
                  {result.yearly_profits.map((yp, i) => (
                    <th
                      key={i}
                      className="py-3 px-4 text-center font-semibold text-gray-600"
                    >
                      {yp.year_label}
                    </th>
                  ))}
                  <th className="py-3 px-4 text-center font-semibold text-gray-600">
                    가중치
                  </th>
                </tr>
              </thead>
              <tbody>
                {/* 소득금액 */}
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4 text-gray-700">
                    각 사업연도 소득금액
                  </td>
                  {result.yearly_profits.map((yp, i) => (
                    <td key={i} className="py-3 px-4 text-center text-gray-900">
                      {fmt(yp.income)}
                    </td>
                  ))}
                  <td className="py-3 px-4 text-center text-gray-400">-</td>
                </tr>
                {/* 비과세소득 */}
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4 text-gray-700">
                    (+) 비과세소득 등
                  </td>
                  {result.yearly_profits.map((yp, i) => (
                    <td key={i} className="py-3 px-4 text-center text-gray-900">
                      {fmt(yp.non_taxable)}
                    </td>
                  ))}
                  <td className="py-3 px-4 text-center text-gray-400">-</td>
                </tr>
                {/* 법인세 */}
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4 text-gray-700">(-) 법인세 등</td>
                  {result.yearly_profits.map((yp, i) => (
                    <td key={i} className="py-3 px-4 text-center text-gray-900">
                      {fmt(yp.tax)}
                    </td>
                  ))}
                  <td className="py-3 px-4 text-center text-gray-400">-</td>
                </tr>
                {/* 순손익액 */}
                <tr className="bg-blue-50 font-semibold">
                  <td className="py-3 px-4 text-blue-800">각 연도 순손익액</td>
                  {result.yearly_profits.map((yp, i) => (
                    <td
                      key={i}
                      className="py-3 px-4 text-center text-blue-800"
                    >
                      {fmt(yp.net_profit)}
                    </td>
                  ))}
                  <td className="py-3 px-4 text-center text-blue-800">
                    {result.yearly_profits.map((yp) => yp.weight).join(' : ')}
                  </td>
                </tr>
              </tbody>
            </table>

            {/* 가중평균 계산식 */}
            <div className="bg-gray-50 rounded-lg p-4 mt-4">
              <p className="text-sm text-gray-600 mb-1">
                가중평균 순손익액 계산
              </p>
              <p className="text-base font-semibold text-gray-900">
                가중평균 순손익액 ={' '}
                {result.yearly_profits
                  .map((yp) => `${fmt(yp.net_profit)} x ${yp.weight}`)
                  .join(' + ')}{' '}
                ) /{' '}
                {result.yearly_profits.reduce((s, yp) => s + yp.weight, 0)} ={' '}
                <span className="text-blue-700 text-xl">
                  {fmt(result.weighted_avg_profit)}백만원
                </span>
              </p>
            </div>

            {/* 1주당 순손익가치 */}
            <div className="bg-gray-50 rounded-lg p-4 mt-3">
              <p className="text-sm text-gray-600 mb-1">1주당 순손익가치</p>
              <p className="text-base font-semibold text-gray-900">
                {fmt(result.weighted_avg_profit)}백만원 /{' '}
                {(result.discount_rate * 100).toFixed(0)}% /{' '}
                {result.shares_outstanding.toLocaleString('ko-KR')}주 ={' '}
                <span className="text-blue-700 text-xl">
                  {fmtWon(result.profit_value_per_share)}
                </span>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 순자산가치 산정                   */}
      {/* =============================== */}
      <section aria-label="순자산가치 산정" className="mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">
              1주당 순자산가치 산정
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">
                  자산총액 (상증세법 평가액)
                </p>
                <p className="text-lg font-semibold text-gray-900">
                  {fmt(result.total_assets)}백만원
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">부채총액</p>
                <p className="text-lg font-semibold text-gray-900">
                  {fmt(result.total_liabilities)}백만원
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">순자산가액</p>
                <p className="text-lg font-semibold text-blue-700">
                  {fmt(result.net_assets)}백만원
                </p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">1주당 순자산가치</p>
              <p className="text-base font-semibold text-gray-900">
                {fmt(result.net_assets)}백만원 /{' '}
                {result.shares_outstanding.toLocaleString('ko-KR')}주 ={' '}
                <span className="text-blue-700 text-xl">
                  {fmtWon(result.asset_value_per_share)}
                </span>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* =============================== */}
      {/* 최종 결과                        */}
      {/* =============================== */}
      <section aria-label="상증세법 평가 결과">
        <div className="bg-gradient-to-br from-blue-700 to-blue-900 rounded-xl p-6 sm:p-8 text-white">
          <h2 className="text-lg font-bold mb-6">상증세법 평가 결과</h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-xs text-blue-200 mb-1">1주당 순손익가치</p>
              <p className="text-2xl font-bold">
                {fmtWon(result.profit_value_per_share)}
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-xs text-blue-200 mb-1">1주당 순자산가치</p>
              <p className="text-2xl font-bold">
                {fmtWon(result.asset_value_per_share)}
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-xs text-blue-200 mb-1">적용 법인 유형</p>
              <p className="text-lg font-bold">
                {isGeneral ? '일반법인' : '부동산과다보유법인'}
              </p>
              <p className="text-xs text-blue-300">
                순손익 {result.profit_weight} : 순자산 {result.asset_weight}
              </p>
            </div>
          </div>

          {/* 계산식 */}
          <div className="bg-white/10 rounded-xl p-5 mb-6 text-center">
            <p className="text-sm text-blue-200 mb-2">계산식</p>
            <p className="text-base leading-loose">
              ({fmtWon(result.profit_value_per_share)} x {result.profit_weight}{' '}
              + {fmtWon(result.asset_value_per_share)} x {result.asset_weight})
              / {result.profit_weight + result.asset_weight}
            </p>
            <p className="text-base leading-loose">
              = (
              {fmt(
                Math.round(
                  result.profit_value_per_share * result.profit_weight
                )
              )}{' '}
              +{' '}
              {fmt(
                Math.round(result.asset_value_per_share * result.asset_weight)
              )}
              ) / {result.profit_weight + result.asset_weight}
            </p>
            <p className="text-lg font-bold mt-1">
              = {fmtWon(result.final_value_per_share)}
            </p>
          </div>

          {/* 최종 */}
          <div className="bg-white/15 rounded-xl p-6 text-center">
            <p className="text-sm text-blue-200 mb-2">1주당 평가액</p>
            <p className="text-4xl sm:text-5xl font-bold">
              {fmtWon(result.final_value_per_share)}
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

function TypeCard({
  title,
  formula,
  active,
}: {
  title: string
  formula: string
  active: boolean
}) {
  return (
    <div
      className={`rounded-xl p-5 border-2 ${
        active
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 bg-gray-50 opacity-60'
      }`}
    >
      <p className="font-bold text-gray-900 mb-1">{title}</p>
      <p
        className={`text-sm font-semibold ${
          active ? 'text-blue-700' : 'text-gray-500'
        }`}
      >
        {formula}
      </p>
      {active && (
        <span className="inline-block mt-2 text-xs bg-blue-700 text-white px-2 py-0.5 rounded-full">
          적용 중
        </span>
      )}
    </div>
  )
}
