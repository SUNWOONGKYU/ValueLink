# S2F6: Project Management Pages

## Task 정보

- **Task ID**: S2F6
- **Task Name**: 프로젝트 관리 페이지 (목록, 상세, 생성)
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S2BA1 (프로젝트 API)
- **Task Agent**: frontend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

프로젝트 목록, 상세, 생성 페이지를 구현하여 사용자가 프로젝트를 관리할 수 있도록 함

---

## 상세 지시사항

### 0. 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase 클라이언트 설정 완료

---

### 1. 프로젝트 목록 페이지

**파일**: `app/projects/list/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import Link from 'next/link'
import {
  Plus,
  Filter,
  Search,
  FolderOpen,
  Clock,
  CheckCircle,
} from 'lucide-react'

interface Project {
  project_id: string
  project_name: string
  valuation_method: string
  status: string
  current_step: number
  created_at: string
  updated_at: string
}

export default function ProjectListPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  useEffect(() => {
    async function loadProjects() {
      const supabase = createClient()

      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      let query = supabase
        .from('projects')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })

      if (filterStatus !== 'all') {
        query = query.eq('status', filterStatus)
      }

      const { data } = await query

      setProjects(data || [])
      setLoading(false)
    }

    loadProjects()
  }, [filterStatus])

  const filteredProjects = projects.filter((project) =>
    project.project_name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const statusIcons: Record<string, any> = {
    pending: <Clock className="w-5 h-5 text-yellow-500" />,
    in_progress: <Clock className="w-5 h-5 text-blue-500" />,
    completed: <CheckCircle className="w-5 h-5 text-green-500" />,
  }

  const statusNames: Record<string, string> = {
    pending: '대기 중',
    in_progress: '진행 중',
    completed: '완료',
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">내 프로젝트</h1>
            <p className="text-gray-500 mt-1">
              총 {filteredProjects.length}개 프로젝트
            </p>
          </div>
          <Link
            href="/projects/create"
            className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            <span>새 프로젝트</span>
          </Link>
        </div>

        {/* 필터 & 검색 */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* 검색 */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="프로젝트 이름 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>

            {/* 필터 */}
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <option value="all">전체</option>
                <option value="pending">대기 중</option>
                <option value="in_progress">진행 중</option>
                <option value="completed">완료</option>
              </select>
            </div>
          </div>
        </div>

        {/* 프로젝트 그리드 */}
        {filteredProjects.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <FolderOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              프로젝트가 없습니다.
            </h3>
            <p className="text-gray-500 mb-6">
              첫 번째 프로젝트를 시작해보세요.
            </p>
            <Link
              href="/projects/create"
              className="inline-flex items-center gap-2 px-6 py-3 text-white bg-red-600 rounded-lg hover:bg-red-700"
            >
              <Plus className="w-5 h-5" />
              <span>프로젝트 만들기</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <Link
                key={project.project_id}
                href={`/projects/${project.project_id}`}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2">
                    {statusIcons[project.status]}
                    <span className="text-sm font-medium text-gray-700">
                      {statusNames[project.status] || project.status}
                    </span>
                  </div>
                  <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded">
                    {project.valuation_method.toUpperCase()}
                  </span>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {project.project_name}
                </h3>

                <div className="space-y-2 text-sm text-gray-500">
                  <div className="flex items-center justify-between">
                    <span>진행 단계</span>
                    <span className="font-medium text-gray-900">
                      {project.current_step}/14
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-red-600 h-2 rounded-full"
                      style={{
                        width: `${(project.current_step / 14) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t">
                    <span>생성일</span>
                    <span>
                      {new Date(project.created_at).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

---

### 2. 프로젝트 상세 페이지

**파일**: `app/projects/[id]/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import Link from 'next/link'
import {
  ArrowLeft,
  Calendar,
  User,
  FileText,
  TrendingUp,
} from 'lucide-react'

interface Project {
  project_id: string
  project_name: string
  valuation_method: string
  status: string
  current_step: number
  created_at: string
  updated_at: string
}

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.id as string

  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadProject() {
      const supabase = createClient()

      const { data, error } = await supabase
        .from('projects')
        .select('*')
        .eq('project_id', projectId)
        .single()

      if (error) {
        router.push('/projects/list')
        return
      }

      setProject(data)
      setLoading(false)
    }

    loadProject()
  }, [projectId, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  if (!project) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="mb-8">
          <Link
            href="/projects/list"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>프로젝트 목록으로</span>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">
            {project.project_name}
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 메인 정보 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 프로젝트 정보 카드 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                프로젝트 정보
              </h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">평가 방법</span>
                  <span className="px-3 py-1 text-sm font-medium bg-red-100 text-red-700 rounded">
                    {project.valuation_method.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">상태</span>
                  <span className="text-sm font-medium text-gray-900">
                    {project.status}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">현재 단계</span>
                  <span className="text-sm font-medium text-gray-900">
                    {project.current_step}/14
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">생성일</span>
                  <span className="text-sm text-gray-700">
                    {new Date(project.created_at).toLocaleDateString('ko-KR')}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">수정일</span>
                  <span className="text-sm text-gray-700">
                    {new Date(project.updated_at).toLocaleDateString('ko-KR')}
                  </span>
                </div>
              </div>
            </div>

            {/* 진행 상황 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                진행 상황
              </h2>
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">
                    {project.current_step}/14 단계 완료
                  </span>
                  <span className="text-sm font-semibold text-red-600">
                    {((project.current_step / 14) * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-red-600 h-3 rounded-full transition-all"
                    style={{
                      width: `${(project.current_step / 14) * 100}%`,
                    }}
                  />
                </div>
              </div>
              <Link
                href={`/valuation/evaluation-progress?project_id=${project.project_id}`}
                className="w-full px-6 py-3 text-white bg-red-600 rounded-lg hover:bg-red-700 flex items-center justify-center gap-2 font-semibold"
              >
                <TrendingUp className="w-5 h-5" />
                <span>진행 상황 보기</span>
              </Link>
            </div>
          </div>

          {/* 사이드바 */}
          <div className="space-y-6">
            {/* 빠른 액션 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                빠른 액션
              </h2>
              <div className="space-y-2">
                <Link
                  href={`/valuation/results/${project.valuation_method}?project_id=${project.project_id}`}
                  className="block px-4 py-3 text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 flex items-center gap-3"
                >
                  <FileText className="w-5 h-5 text-gray-600" />
                  <span>평가 결과 보기</span>
                </Link>
                <Link
                  href={`/valuation/report-download?project_id=${project.project_id}`}
                  className="block px-4 py-3 text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 flex items-center gap-3"
                >
                  <Calendar className="w-5 h-5 text-gray-600" />
                  <span>보고서 다운로드</span>
                </Link>
              </div>
            </div>

            {/* 담당자 정보 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                담당 회계사
              </h2>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-gray-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    배정 대기 중
                  </p>
                  <p className="text-xs text-gray-500">
                    회계사 배정 후 알림 발송
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

### 3. 프로젝트 생성 페이지

**파일**: `app/projects/create/page.tsx`

```typescript
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import Link from 'next/link'
import { ArrowLeft, CheckCircle } from 'lucide-react'

export default function ProjectCreatePage() {
  const router = useRouter()
  const [projectName, setProjectName] = useState('')
  const [valuationMethod, setValuationMethod] = useState<string>('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const methods = [
    {
      id: 'dcf',
      name: 'DCF (현금흐름할인법)',
      description: '미래 현금흐름을 현재가치로 할인하여 평가',
      price: '800만원',
    },
    {
      id: 'relative',
      name: 'Relative (상대가치평가)',
      description: '유사기업의 배수를 활용하여 평가',
      price: '500만원',
    },
    {
      id: 'asset',
      name: 'Asset (자산가치평가)',
      description: '자산과 부채를 기반으로 평가',
      price: '600만원',
    },
    {
      id: 'intrinsic',
      name: 'Intrinsic (내재가치평가)',
      description: 'ROE와 성장률을 기반으로 평가',
      price: '600만원',
    },
    {
      id: 'tax',
      name: 'Tax (세법상평가)',
      description: '세법 기준에 따라 평가',
      price: '1,000만원',
    },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!projectName || !valuationMethod) {
      alert('모든 필드를 입력해주세요.')
      return
    }

    setIsSubmitting(true)

    try {
      const supabase = createClient()

      const { data: project, error } = await supabase
        .from('projects')
        .insert({
          project_name: projectName,
          valuation_method: valuationMethod,
          status: 'pending',
          current_step: 1,
        })
        .select()
        .single()

      if (error) throw error

      router.push(`/projects/${project.project_id}`)
    } catch (error) {
      console.error('프로젝트 생성 실패:', error)
      alert('프로젝트 생성에 실패했습니다.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="mb-8">
          <Link
            href="/projects/list"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>뒤로</span>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">
            새 프로젝트 만들기
          </h1>
          <p className="text-gray-500 mt-2">
            평가 방법을 선택하고 프로젝트를 시작하세요.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 프로젝트명 */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              프로젝트명 <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="예: ABC 스타트업 기업가치평가"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              required
            />
          </div>

          {/* 평가 방법 선택 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              평가 방법 선택 <span className="text-red-600">*</span>
            </h2>
            <div className="space-y-3">
              {methods.map((method) => (
                <label
                  key={method.id}
                  className={`block p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                    valuationMethod === method.id
                      ? 'border-red-600 bg-red-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <input
                      type="radio"
                      name="valuation_method"
                      value={method.id}
                      checked={valuationMethod === method.id}
                      onChange={(e) => setValuationMethod(e.target.value)}
                      className="mt-1"
                      required
                    />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold text-gray-900">
                          {method.name}
                        </h3>
                        <span className="text-sm font-medium text-red-600">
                          {method.price}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        {method.description}
                      </p>
                    </div>
                    {valuationMethod === method.id && (
                      <CheckCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
                    )}
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* 액션 버튼 */}
          <div className="flex justify-end gap-3">
            <Link
              href="/projects/list"
              className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              취소
            </Link>
            <button
              type="submit"
              disabled={isSubmitting || !projectName || !valuationMethod}
              className="px-6 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '생성 중...' : '프로젝트 생성'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `app/projects/list/page.tsx` | 프로젝트 목록 | ~250줄 |
| `app/projects/[id]/page.tsx` | 프로젝트 상세 | ~280줄 |
| `app/projects/create/page.tsx` | 프로젝트 생성 | ~230줄 |

**총 파일 수**: 3개
**총 라인 수**: ~760줄

---

## 기술 스택

- **Framework**: Next.js 14 (App Router, Dynamic Routes)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **Database**: Supabase (projects 테이블)
- **Icons**: lucide-react

---

## 완료 기준

### 필수 (Must Have)

- [ ] 프로젝트 목록 페이지 구현
- [ ] 프로젝트 상세 페이지 구현
- [ ] 프로젝트 생성 페이지 구현
- [ ] 검색 및 필터 기능
- [ ] Supabase에 프로젝트 생성
- [ ] 반응형 디자인

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 프로젝트 CRUD 정상 동작
- [ ] 페이지 간 링크 동작 확인

### 권장 (Nice to Have)

- [ ] 페이지네이션
- [ ] 정렬 기능
- [ ] 프로젝트 삭제 기능

---

## 참조

### 기존 프로토타입

- `Valuation_Company/valuation-platform/frontend/app/core/project-list.html`
- `Valuation_Company/valuation-platform/frontend/app/core/project-detail.html`

### 관련 Task

- **S1BI1**: Next.js 초기화
- **S1D1**: projects 테이블
- **S2BA2**: Projects API

---

## 주의사항

1. **RLS 보안**
   - 본인 프로젝트만 조회/생성
   - user_id 자동 연결

2. **Dynamic Routes**
   - `[id]` 폴더로 동적 라우팅
   - params.id로 project_id 접근

3. **사용자 경험**
   - 빈 상태 명확히 표시
   - 로딩 상태 표시
   - 에러 핸들링

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 3개
**라인 수**: ~760줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
