/**
 * @task S1BI1
 * @description 홈페이지
 */

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          ValueLink
        </h1>
        <p className="text-center text-lg">
          기업가치평가를 넘어 투자 생태계를 연결하는 플랫폼
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <div className="rounded-lg border border-gray-300 p-4">
            <h2 className="font-semibold mb-2">✅ Next.js 14</h2>
            <p className="text-sm text-gray-600">App Router 사용</p>
          </div>
          <div className="rounded-lg border border-gray-300 p-4">
            <h2 className="font-semibold mb-2">✅ TypeScript</h2>
            <p className="text-sm text-gray-600">타입 안전성 보장</p>
          </div>
          <div className="rounded-lg border border-gray-300 p-4">
            <h2 className="font-semibold mb-2">✅ Tailwind CSS</h2>
            <p className="text-sm text-gray-600">유틸리티 우선 스타일</p>
          </div>
          <div className="rounded-lg border border-gray-300 p-4">
            <h2 className="font-semibold mb-2">✅ Supabase</h2>
            <p className="text-sm text-gray-600">인증 및 데이터베이스</p>
          </div>
        </div>
      </div>
    </main>
  )
}
