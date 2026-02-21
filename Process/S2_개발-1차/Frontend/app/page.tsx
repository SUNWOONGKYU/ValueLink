/**
 * @task S2F7
 * @description Landing Page (Home) - ValueLink platform introduction
 *
 * Sections:
 * - Hero: Title, subtitle, CTA buttons (login, register)
 * - Features: 5 valuation methods (DCF, Relative, Asset, Intrinsic, Tax)
 * - How it works: 3 steps (apply -> AI + accountant review -> report)
 * - CTA: "Start now" button
 * - Responsive, modern Tailwind CSS design
 * - Korean language UI
 */

import Link from 'next/link'

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

interface ValuationMethod {
  name: string
  nameEn: string
  description: string
  icon: string
}

const VALUATION_METHODS: ValuationMethod[] = [
  {
    name: 'DCF 평가',
    nameEn: 'Discounted Cash Flow',
    description: '미래 현금흐름을 현재가치로 할인하여 기업가치를 산정합니다.',
    icon: 'M9 19v-6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2zm0 0V9a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v10m-6 0a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2m0 0V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2z',
  },
  {
    name: '상대가치 평가',
    nameEn: 'Relative Valuation',
    description: '유사기업 비교를 통해 PER, PBR, EV/EBITDA 등의 배수로 평가합니다.',
    icon: 'M3 6l3 1m0 0l-3 9a5.002 5.002 0 0 0 6.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 0 0 6.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3',
  },
  {
    name: '자산가치 평가',
    nameEn: 'Asset-based Valuation',
    description: '기업이 보유한 순자산을 기반으로 기업가치를 산정합니다.',
    icon: 'M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v5m-4 0h4',
  },
  {
    name: '본질가치 평가',
    nameEn: 'Intrinsic Value',
    description: '수익가치와 자산가치를 가중평균하여 본질적 기업가치를 산정합니다.',
    icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0 1 12 2.944a11.955 11.955 0 0 1-8.618 3.04A12.02 12.02 0 0 0 3 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  },
  {
    name: '세무평가',
    nameEn: 'Tax Valuation',
    description: '상속세 및 증여세법에 따른 비상장주식 보충적 평가방법입니다.',
    icon: 'M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z',
  },
]

interface ProcessStep {
  step: number
  title: string
  description: string
  icon: string
}

const PROCESS_STEPS: ProcessStep[] = [
  {
    step: 1,
    title: '평가 신청',
    description: '기업 정보와 평가 목적을 입력하고 원하는 평가 방법을 선택합니다.',
    icon: 'M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5m-1.414-9.414a2 2 0 1 1 2.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
  },
  {
    step: 2,
    title: 'AI 분석 + 회계사 검토',
    description: 'AI가 재무 데이터를 분석하고, 공인회계사가 전문적으로 검토합니다.',
    icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 1 1 7.072 0l-.548.547A3.374 3.374 0 0 0 14 18.469V19a2 2 0 1 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
  },
  {
    step: 3,
    title: '보고서 수령',
    description: '상세 평가 보고서를 수령하고, 결과에 대한 전문가 상담을 받을 수 있습니다.',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z',
  },
]

// ---------------------------------------------------------------------------
// Page Component (Server Component)
// ---------------------------------------------------------------------------

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white">
      {/* ================================================================ */}
      {/* Hero Section */}
      {/* ================================================================ */}
      <section className="relative bg-gradient-to-br from-blue-700 via-blue-800 to-blue-900 text-white overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-blue-400 rounded-full -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-80 h-80 bg-blue-300 rounded-full translate-x-1/3 translate-y-1/3" />
        </div>

        <div className="relative max-w-6xl mx-auto px-6 py-24 md:py-36 text-center">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6">
            ValueLink
          </h1>
          <p className="text-xl md:text-2xl text-blue-200 mb-4 font-medium">
            프로젝트 평가 플랫폼
          </p>
          <p className="text-base md:text-lg text-blue-300 mb-10 max-w-2xl mx-auto leading-relaxed">
            AI 기반 분석과 공인회계사의 전문 검토를 통해
            <br className="hidden sm:block" />
            정확하고 신뢰할 수 있는 기업가치평가를 제공합니다.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/login"
              className="px-8 py-4 text-base font-semibold bg-white text-blue-700 rounded-xl hover:bg-blue-50 hover:-translate-y-0.5 hover:shadow-lg transition-all"
            >
              로그인
            </Link>
            <Link
              href="/register"
              className="px-8 py-4 text-base font-semibold bg-blue-600 text-white border-2 border-blue-400 rounded-xl hover:bg-blue-500 hover:-translate-y-0.5 hover:shadow-lg transition-all"
            >
              회원가입
            </Link>
          </div>
        </div>
      </section>

      {/* ================================================================ */}
      {/* Features: 5 Valuation Methods */}
      {/* ================================================================ */}
      <section className="py-20 md:py-28 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              5가지 평가 방법
            </h2>
            <p className="text-base md:text-lg text-gray-500 max-w-2xl mx-auto">
              기업의 특성과 평가 목적에 맞는 최적의 평가 방법을 제공합니다
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {VALUATION_METHODS.map((method) => (
              <div
                key={method.nameEn}
                className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-md hover:-translate-y-1 transition-all"
              >
                <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
                  <svg
                    className="w-7 h-7 text-blue-700"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d={method.icon} />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-1">{method.name}</h3>
                <p className="text-xs text-gray-400 mb-3 font-medium">{method.nameEn}</p>
                <p className="text-sm text-gray-600 leading-relaxed">{method.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================ */}
      {/* How It Works: 3 Steps */}
      {/* ================================================================ */}
      <section className="py-20 md:py-28">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              이용 절차
            </h2>
            <p className="text-base md:text-lg text-gray-500 max-w-2xl mx-auto">
              간단한 3단계로 기업가치평가를 받으실 수 있습니다
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {PROCESS_STEPS.map((item, idx) => (
              <div key={item.step} className="relative text-center">
                {/* Connector line */}
                {idx < PROCESS_STEPS.length - 1 && (
                  <div className="hidden md:block absolute top-10 left-[60%] w-[80%] h-0.5 bg-blue-200" />
                )}

                <div className="w-20 h-20 bg-blue-700 rounded-full flex items-center justify-center mx-auto mb-6 relative z-10">
                  <svg
                    className="w-9 h-9 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                  </svg>
                </div>

                <div className="text-sm font-bold text-blue-700 mb-2">STEP {item.step}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{item.title}</h3>
                <p className="text-sm text-gray-600 leading-relaxed max-w-xs mx-auto">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================ */}
      {/* CTA Section */}
      {/* ================================================================ */}
      <section className="py-20 md:py-28 bg-gradient-to-br from-blue-700 to-blue-900 text-white">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            지금 시작하세요
          </h2>
          <p className="text-base md:text-lg text-blue-200 mb-10 leading-relaxed">
            ValueLink와 함께 정확하고 전문적인 기업가치평가를 경험하세요.
            <br className="hidden sm:block" />
            AI 분석과 공인회계사의 검토를 동시에 받을 수 있습니다.
          </p>
          <Link
            href="/register"
            className="inline-block px-10 py-4 text-base font-semibold bg-white text-blue-700 rounded-xl hover:bg-blue-50 hover:-translate-y-0.5 hover:shadow-lg transition-all"
          >
            무료로 시작하기
          </Link>
        </div>
      </section>

      {/* ================================================================ */}
      {/* Footer */}
      {/* ================================================================ */}
      <footer className="py-8 bg-gray-900 text-gray-400 text-center text-sm">
        <div className="max-w-6xl mx-auto px-6">
          <p>&copy; {new Date().getFullYear()} ValueLink. All rights reserved.</p>
        </div>
      </footer>
    </main>
  )
}
