/**
 * @task S1BI1
 * @description 루트 레이아웃
 */

import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ValueLink - 기업가치평가 플랫폼',
  description: '기업가치평가를 넘어 투자 생태계를 연결하는 플랫폼',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
