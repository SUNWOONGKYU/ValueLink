import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          기업가치평가 플랫폼
        </h1>
        <p className="text-center text-lg mb-4">
          AI 기반 기업가치평가 시스템 (Phase 1 MVP)
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className="p-6 border rounded-lg hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold mb-2">DCF 평가</h2>
            <p className="text-gray-600">현금흐름할인법 기반 기업가치 평가</p>
          </div>
          <div className="p-6 border rounded-lg hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold mb-2">상대가치 평가</h2>
            <p className="text-gray-600">비교기업 기반 상대가치 평가</p>
          </div>
          <Link href="/investment-tracker" className="p-6 border rounded-lg hover:shadow-md transition-shadow bg-blue-50 border-blue-200">
            <h2 className="text-xl font-semibold mb-2 text-blue-700">투자 트래커</h2>
            <p className="text-blue-600">스타트업 투자 유치 뉴스 자동 수집</p>
          </Link>
        </div>
      </div>
    </main>
  )
}
