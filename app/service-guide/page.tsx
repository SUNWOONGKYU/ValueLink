/**
 * @task S2F7
 * @description Service Guide Page - Valuation service overview
 *
 * Content:
 * - Service overview (what is enterprise valuation?)
 * - 5 valuation methods explanation with pricing table
 * - Process overview (14 steps simplified)
 * - FAQ highlights
 * - CTA to register
 * - Korean language UI, responsive Tailwind CSS
 */

import Link from 'next/link'

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

interface MethodDetail {
  name: string
  nameEn: string
  description: string
  when: string
  deliverables: string[]
  price: string
  duration: string
}

const METHODS: MethodDetail[] = [
  {
    name: 'DCF 평가',
    nameEn: 'Discounted Cash Flow',
    description:
      '미래 현금흐름을 예측하고, 적절한 할인율로 현재가치를 산출합니다. 가장 이론적이고 정교한 평가 방법입니다.',
    when: '투자 유치, M&A, IPO 준비',
    deliverables: ['DCF 평가 보고서', '현금흐름 예측표', '민감도 분석'],
    price: '협의',
    duration: '2-3주',
  },
  {
    name: '상대가치 평가',
    nameEn: 'Relative Valuation',
    description:
      'PER, PBR, EV/EBITDA 등의 배수를 통해 유사기업과 비교하여 기업가치를 산출합니다.',
    when: '빠른 가치 추정, 시장 비교',
    deliverables: ['상대가치 평가 보고서', '유사기업 비교 분석'],
    price: '협의',
    duration: '1-2주',
  },
  {
    name: '자산가치 평가',
    nameEn: 'Asset-based Valuation',
    description:
      '기업의 순자산(자산 - 부채)을 기반으로 기업가치를 산출합니다. 실물자산이 많은 기업에 적합합니다.',
    when: '청산 가치 산정, 실물자산 기업',
    deliverables: ['자산가치 평가 보고서', '자산 재평가 내역'],
    price: '협의',
    duration: '1-2주',
  },
  {
    name: '본질가치 평가',
    nameEn: 'Intrinsic Value',
    description:
      '수익가치와 자산가치를 가중평균하여 기업의 본질적 가치를 산출합니다. 균형 잡힌 평가가 가능합니다.',
    when: '합병 비율 산정, 종합적 평가',
    deliverables: ['본질가치 평가 보고서', '수익/자산 가중평균표'],
    price: '협의',
    duration: '2-3주',
  },
  {
    name: '세무평가',
    nameEn: 'Tax Valuation',
    description:
      '상속세 및 증여세법에 따른 비상장주식의 보충적 평가방법입니다. 세무 목적으로 사용됩니다.',
    when: '상속/증여, 세무 신고',
    deliverables: ['세무평가 보고서', '주당 가치 산출표'],
    price: '협의',
    duration: '1-2주',
  },
]

interface ProcessItem {
  step: number
  title: string
  description: string
}

const PROCESS_OVERVIEW: ProcessItem[] = [
  { step: 1, title: '회원가입 및 로그인', description: '기본 정보를 입력하고 계정을 생성합니다.' },
  { step: 2, title: '평가 신청', description: '기업 정보, 평가 목적, 평가 방법을 선택합니다.' },
  { step: 3, title: '자료 제출', description: '재무제표, 사업계획서 등 필요 자료를 업로드합니다.' },
  { step: 4, title: '담당자 배정', description: '전문 공인회계사가 프로젝트에 배정됩니다.' },
  { step: 5, title: 'AI 사전 분석', description: 'AI가 재무 데이터를 분석하고 초기 결과를 생성합니다.' },
  { step: 6, title: '전문가 검토', description: '공인회계사가 AI 분석 결과를 검토하고 보완합니다.' },
  { step: 7, title: '보고서 수령', description: '상세 평가 보고서를 수령하고 결과를 확인합니다.' },
]

interface FAQItem {
  question: string
  answer: string
}

const FAQ_ITEMS: FAQItem[] = [
  {
    question: '기업가치평가란 무엇인가요?',
    answer:
      '기업가치평가는 기업의 경제적 가치를 정량적으로 산정하는 과정입니다. 투자, M&A, IPO, 상속/증여, 세무 등 다양한 목적으로 활용됩니다.',
  },
  {
    question: '평가 결과는 얼마나 걸리나요?',
    answer:
      '평가 방법에 따라 1주에서 3주 정도 소요됩니다. 상대가치/자산가치 평가는 비교적 빠르고, DCF/본질가치 평가는 더 정교한 분석이 필요합니다.',
  },
  {
    question: 'AI 분석은 어떻게 활용되나요?',
    answer:
      'AI가 재무 데이터의 패턴을 분석하고, 유사기업 비교, 현금흐름 예측 등을 수행합니다. 이후 공인회계사가 결과를 전문적으로 검토하고 보완합니다.',
  },
  {
    question: '비상장기업도 평가 가능한가요?',
    answer:
      '네, 비상장기업 평가를 주요 서비스로 제공합니다. 상속세 및 증여세법에 따른 보충적 평가방법(세무평가)도 지원합니다.',
  },
]

// ---------------------------------------------------------------------------
// Page Component (Server Component)
// ---------------------------------------------------------------------------

export default function ServiceGuidePage() {
  return (
    <main className="min-h-screen bg-white">
      {/* ================================================================ */}
      {/* Hero */}
      {/* ================================================================ */}
      <section className="bg-gradient-to-br from-blue-700 to-blue-900 text-white py-20 md:py-28">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-6">
            서비스 안내
          </h1>
          <p className="text-base md:text-lg text-blue-200 leading-relaxed max-w-2xl mx-auto">
            ValueLink는 AI 분석과 공인회계사의 전문 검토를 결합하여
            정확하고 신뢰할 수 있는 기업가치평가 서비스를 제공합니다.
          </p>
        </div>
      </section>

      {/* ================================================================ */}
      {/* What is Enterprise Valuation? */}
      {/* ================================================================ */}
      <section className="py-16 md:py-24">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-6 text-center">
            기업가치평가란?
          </h2>
          <div className="bg-gray-50 rounded-2xl p-8 md:p-10">
            <p className="text-base text-gray-700 leading-relaxed mb-6">
              기업가치평가(Business Valuation)는 기업의 경제적 가치를 합리적인 방법론을 통해
              정량적으로 산정하는 전문 서비스입니다.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                '투자 유치 및 M&A',
                'IPO (상장) 준비',
                '상속 및 증여세 신고',
                '주주 간 거래',
                '경영 의사결정',
                '법적 분쟁 해결',
              ].map((item) => (
                <div key={item} className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-3.5 h-3.5 text-blue-700"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <span className="text-sm text-gray-700">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================ */}
      {/* 5 Valuation Methods */}
      {/* ================================================================ */}
      <section className="py-16 md:py-24 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
              5가지 평가 방법
            </h2>
            <p className="text-base text-gray-500 max-w-2xl mx-auto">
              기업의 특성과 평가 목적에 따라 최적의 방법을 선택할 수 있습니다
            </p>
          </div>

          <div className="space-y-6">
            {METHODS.map((method, idx) => (
              <div
                key={method.nameEn}
                className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
              >
                <div className="p-8 md:p-10">
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="w-8 h-8 bg-blue-700 text-white rounded-lg flex items-center justify-center text-sm font-bold">
                          {idx + 1}
                        </span>
                        <h3 className="text-xl font-bold text-gray-900">{method.name}</h3>
                        <span className="text-xs text-gray-400 font-medium">{method.nameEn}</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                        {method.description}
                      </p>
                      <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                        <div>
                          <span className="font-semibold text-gray-700">적합한 상황:</span>{' '}
                          {method.when}
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">소요 기간:</span>{' '}
                          {method.duration}
                        </div>
                      </div>
                    </div>
                    <div className="md:text-right">
                      <div className="text-sm text-gray-500 mb-2">산출물</div>
                      <ul className="space-y-1">
                        {method.deliverables.map((d) => (
                          <li key={d} className="text-sm text-gray-700 flex items-center gap-2 md:justify-end">
                            <svg
                              className="w-3.5 h-3.5 text-blue-600 flex-shrink-0"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 12l2 2 4-4"
                              />
                            </svg>
                            {d}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================ */}
      {/* Process Overview */}
      {/* ================================================================ */}
      <section className="py-16 md:py-24">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
              이용 절차
            </h2>
            <p className="text-base text-gray-500">
              간단하고 체계적인 프로세스로 진행됩니다
            </p>
          </div>

          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-blue-200 hidden md:block" />

            <div className="space-y-8">
              {PROCESS_OVERVIEW.map((item) => (
                <div key={item.step} className="flex gap-6 items-start">
                  <div className="relative z-10 w-12 h-12 bg-blue-700 text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                    {item.step}
                  </div>
                  <div className="pt-2">
                    <h3 className="text-base font-bold text-gray-900 mb-1">{item.title}</h3>
                    <p className="text-sm text-gray-600">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================ */}
      {/* FAQ */}
      {/* ================================================================ */}
      <section className="py-16 md:py-24 bg-gray-50">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
              자주 묻는 질문
            </h2>
          </div>

          <div className="space-y-4">
            {FAQ_ITEMS.map((faq) => (
              <div
                key={faq.question}
                className="bg-white rounded-2xl border border-gray-100 p-6 md:p-8"
              >
                <h3 className="text-base font-bold text-gray-900 mb-3 flex items-start gap-3">
                  <span className="text-blue-700 font-bold text-lg leading-none mt-0.5">Q.</span>
                  {faq.question}
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed pl-7">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================ */}
      {/* CTA */}
      {/* ================================================================ */}
      <section className="py-20 md:py-28 bg-gradient-to-br from-blue-700 to-blue-900 text-white">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            지금 바로 시작하세요
          </h2>
          <p className="text-base md:text-lg text-blue-200 mb-10 leading-relaxed">
            회원가입 후 바로 기업가치평가를 신청할 수 있습니다.
          </p>
          <Link
            href="/register"
            className="inline-block px-10 py-4 text-base font-semibold bg-white text-blue-700 rounded-xl hover:bg-blue-50 hover:-translate-y-0.5 hover:shadow-lg transition-all"
          >
            회원가입
          </Link>
        </div>
      </section>
    </main>
  )
}
