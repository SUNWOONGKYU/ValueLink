/**
 * @task S2F1
 * @description 평가 결과 페이지 공통 템플릿 (5개 방법론 공유)
 *
 * - 'use client': PDF 다운로드, 공유, 인쇄 등 인터랙티브 버튼 포함
 * - 헤더(프로젝트 정보, 뒤로가기, 방법론 뱃지)
 * - 액션 버튼 (PDF, 공유, 인쇄)
 * - 푸터 (면책 조항)
 * - 반응형 모바일 우선 Tailwind CSS
 */

'use client'

import { ReactNode } from 'react'
import Link from 'next/link'
import type { ValuationMethod } from '@/types/valuation'

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface ValuationResultsTemplateProps {
  /** 평가 방법론 */
  method: ValuationMethod
  /** 프로젝트 ID (URL용) */
  projectId: string
  /** 회사명 */
  companyName: string
  /** 평가 기준일 */
  valuationDate?: string
  /** 페이지 본문 (Server Component children) */
  children: ReactNode
}

// ---------------------------------------------------------------------------
// 방법론 메타데이터
// ---------------------------------------------------------------------------

const METHOD_META: Record<
  ValuationMethod,
  { label: string; description: string; badgeColor: string }
> = {
  dcf: {
    label: 'DCF',
    description: '현금흐름할인법',
    badgeColor: 'bg-blue-100 text-blue-800',
  },
  relative: {
    label: '상대가치',
    description: '유사기업 비교법',
    badgeColor: 'bg-green-100 text-green-800',
  },
  asset: {
    label: '자산가치',
    description: '순자산가치법 (NAV)',
    badgeColor: 'bg-amber-100 text-amber-800',
  },
  intrinsic: {
    label: '본질가치',
    description: '자본시장법',
    badgeColor: 'bg-purple-100 text-purple-800',
  },
  tax: {
    label: '상증세법',
    description: '보충적 평가방법',
    badgeColor: 'bg-red-100 text-red-800',
  },
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ValuationResultsTemplate({
  method,
  projectId,
  companyName,
  valuationDate,
  children,
}: ValuationResultsTemplateProps) {
  const meta = METHOD_META[method]

  // --- 액션 핸들러 ---

  const handleDownloadPDF = () => {
    // TODO: S2BA3에서 구현될 PDF 다운로드 API 호출
    window.alert('PDF 다운로드 기능은 추후 제공됩니다.')
  }

  const handleShare = async () => {
    const url = window.location.href
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${companyName} - ${meta.label} 평가 결과`,
          url,
        })
      } catch {
        // 사용자가 공유 취소 - 무시
      }
    } else {
      await navigator.clipboard.writeText(url)
      window.alert('링크가 클립보드에 복사되었습니다.')
    }
  }

  const handlePrint = () => {
    window.print()
  }

  // --- Render ---

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ============================================================= */}
      {/* 헤더                                                          */}
      {/* ============================================================= */}
      <header className="bg-white border-b border-gray-200 print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          {/* 상단: 뒤로가기 + 액션 버튼 */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            {/* 좌측: 네비게이션 + 제목 */}
            <div className="flex items-center gap-4">
              <Link
                href={`/projects/${projectId}`}
                className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                aria-label="프로젝트 목록으로 돌아가기"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                <span className="hidden sm:inline">돌아가기</span>
              </Link>

              <div className="border-l border-gray-300 pl-4">
                <div className="flex items-center gap-2">
                  <h1 className="text-lg sm:text-xl font-bold text-gray-900">
                    {meta.label} 평가 결과
                  </h1>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${meta.badgeColor}`}
                  >
                    {meta.description}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-0.5">
                  {companyName}
                  {valuationDate && (
                    <span className="ml-2 text-gray-400">
                      | 기준일: {valuationDate}
                    </span>
                  )}
                </p>
              </div>
            </div>

            {/* 우측: 액션 버튼 */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handlePrint}
                className="px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1.5"
                aria-label="인쇄"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2z"
                  />
                </svg>
                <span className="hidden sm:inline">인쇄</span>
              </button>
              <button
                type="button"
                onClick={handleShare}
                className="px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1.5"
                aria-label="결과 공유"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
                  />
                </svg>
                <span className="hidden sm:inline">공유</span>
              </button>
              <button
                type="button"
                onClick={handleDownloadPDF}
                className="px-3 py-2 text-sm text-white bg-blue-700 rounded-lg hover:bg-blue-800 transition-colors flex items-center gap-1.5"
                aria-label="PDF 다운로드"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <span>PDF</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ============================================================= */}
      {/* 메인 콘텐츠                                                    */}
      {/* ============================================================= */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {children}
      </main>

      {/* ============================================================= */}
      {/* 푸터 (면책 조항)                                               */}
      {/* ============================================================= */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500 space-y-1">
            <p>
              본 평가 결과는 입력된 데이터에 기반한 참고 자료이며, 법적 효력이
              있는 공식 평가 보고서가 아닙니다.
            </p>
            <p>
              최종 투자 또는 세무 의사결정 시 공인된 평가기관 및 전문가 상담을
              권장합니다.
            </p>
            <p className="mt-3 text-gray-400">
              &copy; {new Date().getFullYear()} ValueLink. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
