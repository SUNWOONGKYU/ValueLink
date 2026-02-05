# S4F1: Deal News Tracker & Investment Monitor

## Task 정보

- **Task ID**: S4F1
- **Task Name**: Deal 뉴스 트래커 및 투자 모니터
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S4E2 (News Parser)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

투자 뉴스 및 Deal 정보를 시각화하고, 투자 생태계 네트워크를 표시하는 페이지 구현

---

## 상세 지시사항

### 1. Deal 뉴스 페이지

**파일**: `app/deal/page.tsx`

```typescript
'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { Search, Filter, TrendingUp, Building2, Calendar } from 'lucide-react'

interface DealNews {
  id: string
  company_name: string
  investment_stage: string
  investment_amount: string
  investors: string[]
  industry: string
  published_date: string
  article_url: string
  source: string
}

export default function DealPage() {
  const [deals, setDeals] = useState<DealNews[]>([])
  const [filteredDeals, setFilteredDeals] = useState<DealNews[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStage, setSelectedStage] = useState<string>('all')
  const [selectedIndustry, setSelectedIndustry] = useState<string>('all')

  useEffect(() => {
    fetchDeals()
  }, [])

  useEffect(() => {
    filterDeals()
  }, [deals, searchTerm, selectedStage, selectedIndustry])

  async function fetchDeals() {
    try {
      const supabase = createClient()

      const { data, error } = await supabase
        .from('investment_tracker')
        .select('*')
        .order('published_date', { ascending: false })
        .limit(100)

      if (error) throw error

      setDeals(data || [])
    } catch (error) {
      console.error('Error fetching deals:', error)
    } finally {
      setLoading(false)
    }
  }

  function filterDeals() {
    let filtered = deals

    // 검색어 필터
    if (searchTerm) {
      filtered = filtered.filter((deal) =>
        deal.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        deal.investors.some((inv) => inv.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }

    // 투자 단계 필터
    if (selectedStage !== 'all') {
      filtered = filtered.filter((deal) => deal.investment_stage === selectedStage)
    }

    // 업종 필터
    if (selectedIndustry !== 'all') {
      filtered = filtered.filter((deal) => deal.industry === selectedIndustry)
    }

    setFilteredDeals(filtered)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Deal 뉴스 로딩 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Deal 뉴스 트래커
          </h1>
          <p className="text-gray-600">
            스타트업 투자 소식 및 Deal 정보를 실시간으로 확인하세요
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 검색 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                검색
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="기업명 또는 투자자 검색"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* 투자 단계 필터 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                투자 단계
              </label>
              <select
                value={selectedStage}
                onChange={(e) => setSelectedStage(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="all">전체</option>
                <option value="시드">시드</option>
                <option value="프리A">프리A</option>
                <option value="시리즈A">시리즈A</option>
                <option value="시리즈B">시리즈B</option>
                <option value="시리즈C">시리즈C</option>
                <option value="브릿지">브릿지</option>
              </select>
            </div>

            {/* 업종 필터 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                업종
              </label>
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="all">전체</option>
                <option value="AI">AI</option>
                <option value="헬스케어">헬스케어</option>
                <option value="핀테크">핀테크</option>
                <option value="이커머스">이커머스</option>
                <option value="푸드테크">푸드테크</option>
                <option value="기타">기타</option>
              </select>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">총 Deal 수</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {filteredDeals.length}건
                </p>
              </div>
              <TrendingUp className="h-10 w-10 text-red-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">이번 주 투자</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {
                    filteredDeals.filter((d) => {
                      const publishedDate = new Date(d.published_date)
                      const weekAgo = new Date()
                      weekAgo.setDate(weekAgo.getDate() - 7)
                      return publishedDate >= weekAgo
                    }).length
                  }
                  건
                </p>
              </div>
              <Calendar className="h-10 w-10 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">참여 기업</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {new Set(filteredDeals.map((d) => d.company_name)).size}개
                </p>
              </div>
              <Building2 className="h-10 w-10 text-green-600" />
            </div>
          </div>
        </div>

        {/* Deal List */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              최신 Deal 목록
            </h2>
          </div>

          <div className="divide-y divide-gray-200">
            {filteredDeals.length === 0 ? (
              <div className="p-12 text-center">
                <p className="text-gray-500">검색 결과가 없습니다.</p>
              </div>
            ) : (
              filteredDeals.map((deal) => (
                <div key={deal.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {deal.company_name}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                        <span className="inline-flex items-center px-3 py-1 rounded-full bg-red-100 text-red-800">
                          {deal.investment_stage}
                        </span>
                        <span className="font-semibold text-red-600">
                          {deal.investment_amount}
                        </span>
                        <span>{deal.industry}</span>
                      </div>
                      <div className="mb-2">
                        <span className="text-sm text-gray-600">투자자: </span>
                        <span className="text-sm text-gray-900">
                          {deal.investors.join(', ')}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span>{deal.source}</span>
                        <span>{new Date(deal.published_date).toLocaleDateString('ko-KR')}</span>
                      </div>
                    </div>
                    <a
                      href={deal.article_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      기사 보기
                    </a>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

### 2. 네트워크/연결 페이지

**파일**: `app/link/page.tsx`

```typescript
'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'

interface Connection {
  id: string
  investor_name: string
  company_name: string
  investment_count: number
}

export default function LinkPage() {
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchConnections()
  }, [])

  async function fetchConnections() {
    try {
      const supabase = createClient()

      // 투자자-기업 연결 집계
      const { data, error } = await supabase
        .from('investment_tracker')
        .select('investors, company_name')

      if (error) throw error

      // 투자자별 투자 횟수 집계
      const investorMap = new Map<string, Set<string>>()

      data?.forEach((item) => {
        item.investors.forEach((investor: string) => {
          if (!investorMap.has(investor)) {
            investorMap.set(investor, new Set())
          }
          investorMap.get(investor)!.add(item.company_name)
        })
      })

      const connectionData: Connection[] = Array.from(investorMap.entries()).map(
        ([investor, companies], index) => ({
          id: `conn-${index}`,
          investor_name: investor,
          company_name: Array.from(companies).join(', '),
          investment_count: companies.size,
        })
      )

      // 투자 횟수 내림차순 정렬
      connectionData.sort((a, b) => b.investment_count - a.investment_count)

      setConnections(connectionData)
    } catch (error) {
      console.error('Error fetching connections:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">네트워크 로딩 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            투자 네트워크
          </h1>
          <p className="text-gray-600">
            투자자와 스타트업의 연결 관계를 확인하세요
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              투자자별 포트폴리오
            </h2>
          </div>

          <div className="divide-y divide-gray-200">
            {connections.map((conn) => (
              <div key={conn.id} className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {conn.investor_name}
                  </h3>
                  <span className="px-3 py-1 rounded-full bg-red-100 text-red-800 text-sm font-medium">
                    {conn.investment_count}개 투자
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  {conn.company_name}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `app/deal/page.tsx` | Deal 뉴스 페이지 | ~280줄 |
| `app/link/page.tsx` | 네트워크 페이지 | ~140줄 |

**총 파일 수**: 2개
**총 라인 수**: ~420줄

---

## 기술 스택

- **Next.js 14 App Router**: Client Component
- **Supabase**: `investment_tracker` 테이블 조회
- **Lucide React**: 아이콘
- **Tailwind CSS**: 스타일링

---

## 완료 기준

### 필수 (Must Have)

- [ ] Deal 뉴스 페이지 구현
- [ ] 검색 및 필터 기능
- [ ] 통계 카드 (총 Deal 수, 이번 주 투자, 참여 기업)
- [ ] Deal 목록 표시
- [ ] 네트워크 페이지 구현
- [ ] 투자자별 포트폴리오 표시

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] Deal 목록 조회 확인
- [ ] 필터링 동작 확인
- [ ] 네트워크 집계 확인

### 권장 (Nice to Have)

- [ ] 네트워크 그래프 시각화
- [ ] 투자 트렌드 차트
- [ ] 엑셀 내보내기

---

## 참조

### 기존 프로토타입
- `frontend/app/deal.html` (2497줄)
- `frontend/app/link.html` (959줄)

### 의존성
- S1BI1: Next.js 초기화
- S4E2: News Parser (데이터 수집)

---

**작업 복잡도**: Medium
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
