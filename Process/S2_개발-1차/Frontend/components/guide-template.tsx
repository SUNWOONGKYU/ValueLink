/**
 * @task S2F3
 * @description Educational Guide Template - Shared layout for all 5 valuation method guide pages
 */

import Link from 'next/link'

interface GuideMethod {
  slug: string
  name: string
  shortName: string
}

const GUIDE_METHODS: GuideMethod[] = [
  { slug: 'dcf', name: 'DCF (현금흐름할인법)', shortName: 'DCF' },
  { slug: 'relative', name: '상대가치평가', shortName: '상대가치' },
  { slug: 'asset', name: '자산가치평가', shortName: '자산가치' },
  { slug: 'intrinsic', name: '내재가치평가 (자본시장법)', shortName: '내재가치' },
  { slug: 'tax', name: '세법상 평가 (상속세법)', shortName: '세법상 평가' },
]

interface GuideTemplateProps {
  methodName: string
  title: string
  description: string
  children: React.ReactNode
}

export default function GuideTemplate({
  methodName,
  title,
  description,
  children,
}: GuideTemplateProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-10">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Navigation */}
          <aside className="w-full lg:w-72 flex-shrink-0" aria-label="평가법 안내 네비게이션">
            {/* Mobile: Horizontal scrollable nav */}
            <nav className="lg:hidden" aria-label="평가법 목록 (모바일)">
              <div className="flex gap-2 overflow-x-auto pb-3 scrollbar-hide">
                {GUIDE_METHODS.map((method) => (
                  <Link
                    key={method.slug}
                    href={`/valuation/guides/${method.slug}`}
                    className={`flex-shrink-0 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${
                      method.slug === methodName
                        ? 'bg-blue-700 text-white shadow-sm'
                        : 'bg-white text-gray-700 border border-gray-200 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300'
                    }`}
                    aria-current={method.slug === methodName ? 'page' : undefined}
                  >
                    {method.shortName}
                  </Link>
                ))}
              </div>
            </nav>

            {/* Desktop: Vertical sidebar */}
            <div className="hidden lg:block sticky top-8">
              <nav aria-label="평가법 목록">
                <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3 px-3">
                  평가법 안내
                </h2>
                <ul className="space-y-1" role="list">
                  {GUIDE_METHODS.map((method) => (
                    <li key={method.slug}>
                      <Link
                        href={`/valuation/guides/${method.slug}`}
                        className={`block rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                          method.slug === methodName
                            ? 'bg-blue-700 text-white shadow-sm'
                            : 'text-gray-700 hover:bg-blue-50 hover:text-blue-700'
                        }`}
                        aria-current={method.slug === methodName ? 'page' : undefined}
                      >
                        {method.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </nav>

              {/* CTA Button */}
              <div className="mt-8 px-3">
                <Link
                  href="/valuation/request"
                  className="block w-full rounded-lg bg-emerald-600 px-4 py-3 text-center text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600"
                >
                  평가 신청하기
                </Link>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 min-w-0">
            {/* Page Header */}
            <header className="mb-8">
              <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                {title}
              </h1>
              <p className="mt-3 text-lg text-gray-600 leading-relaxed">
                {description}
              </p>
            </header>

            {/* Article Content */}
            <article className="prose prose-gray max-w-none prose-headings:scroll-mt-20 prose-h2:text-2xl prose-h2:font-bold prose-h2:border-b prose-h2:border-gray-200 prose-h2:pb-3 prose-h2:mt-12 prose-h2:mb-6 prose-h3:text-xl prose-h3:font-semibold prose-h3:mt-8 prose-h3:mb-4 prose-p:leading-relaxed prose-li:leading-relaxed prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:rounded-xl prose-pre:shadow-sm prose-code:text-blue-700 prose-code:bg-blue-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:before:content-[''] prose-code:after:content-[''] prose-table:border-collapse prose-th:bg-gray-100 prose-th:border prose-th:border-gray-300 prose-th:px-4 prose-th:py-2 prose-td:border prose-td:border-gray-300 prose-td:px-4 prose-td:py-2 prose-strong:text-gray-900">
              {children}
            </article>

            {/* Mobile CTA Button */}
            <div className="mt-12 lg:hidden">
              <Link
                href="/valuation/request"
                className="block w-full rounded-lg bg-emerald-600 px-4 py-3 text-center text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-700"
              >
                평가 신청하기
              </Link>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
