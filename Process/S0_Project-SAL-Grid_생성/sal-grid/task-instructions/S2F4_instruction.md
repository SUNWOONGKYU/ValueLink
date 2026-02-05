# S2F4: Role-Based My Page Template & 6 Role Variants

## Task 정보

- **Task ID**: S2F4
- **Task Name**: 역할별 마이페이지 템플릿 및 6개 역할 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S1D1 (users 테이블)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

6개 사용자 역할(기업, 회계사, 투자자, 파트너, 서포터, 관리자)별 마이페이지를 구현하여 역할별 대시보드 및 프로필 관리 기능 제공

---

## 상세 지시사항

### 0. 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase Auth 설정 완료

**S1D1 완료 확인:**
- users 테이블에 role 컬럼 존재

---

### 1. 공통 마이페이지 템플릿

**파일**: `components/mypage-template.tsx`

```typescript
'use client'

import { ReactNode } from 'react'
import Link from 'next/link'
import { User, Settings, LogOut } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'

interface MyPageTemplateProps {
  role: 'customer' | 'accountant' | 'investor' | 'partner' | 'supporter' | 'admin'
  userName: string
  userEmail: string
  children: ReactNode
}

export default function MyPageTemplate({
  role,
  userName,
  userEmail,
  children,
}: MyPageTemplateProps) {
  const router = useRouter()

  const roleNames: Record<string, string> = {
    customer: '기업 (고객)',
    accountant: '회계사',
    investor: '투자자',
    partner: '파트너',
    supporter: '서포터',
    admin: '관리자',
  }

  const handleLogout = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <User className="w-8 h-8 text-red-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">{userName}</h1>
                <p className="text-sm text-gray-500">
                  {roleNames[role]} • {userEmail}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link
                href="/mypage/settings"
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
              >
                <Settings className="w-4 h-4" />
                <span>설정</span>
              </Link>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                <span>로그아웃</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
```

---

### 2. 기업 (Customer) 마이페이지

**파일**: `app/mypage/company/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import MyPageTemplate from '@/components/mypage-template'
import Link from 'next/link'
import {
  FolderOpen,
  Clock,
  CheckCircle,
  XCircle,
  Plus,
} from 'lucide-react'

interface Project {
  project_id: string
  project_name: string
  valuation_method: string
  status: string
  current_step: number
  created_at: string
}

export default function CompanyMyPage() {
  const [user, setUser] = useState<any>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      const supabase = createClient()

      // 사용자 정보 로드
      const { data: { user: authUser } } = await supabase.auth.getUser()
      if (!authUser) return

      const { data: userData } = await supabase
        .from('users')
        .select('*')
        .eq('user_id', authUser.id)
        .single()

      setUser(userData)

      // 프로젝트 목록 로드
      const { data: projectData } = await supabase
        .from('projects')
        .select('*')
        .eq('user_id', authUser.id)
        .order('created_at', { ascending: false })

      setProjects(projectData || [])
      setLoading(false)
    }

    loadData()
  }, [])

  if (loading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    )
  }

  const statusIcons: Record<string, any> = {
    pending: <Clock className="w-5 h-5 text-yellow-500" />,
    in_progress: <Clock className="w-5 h-5 text-blue-500" />,
    completed: <CheckCircle className="w-5 h-5 text-green-500" />,
    rejected: <XCircle className="w-5 h-5 text-red-500" />,
  }

  const statusNames: Record<string, string> = {
    pending: '대기 중',
    in_progress: '진행 중',
    completed: '완료',
    rejected: '반려',
  }

  return (
    <MyPageTemplate
      role="customer"
      userName={user.full_name}
      userEmail={user.email}
    >
      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">
            전체 프로젝트
          </h3>
          <p className="text-3xl font-bold text-gray-900">{projects.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">진행 중</h3>
          <p className="text-3xl font-bold text-blue-600">
            {projects.filter((p) => p.status === 'in_progress').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">완료</h3>
          <p className="text-3xl font-bold text-green-600">
            {projects.filter((p) => p.status === 'completed').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">대기 중</h3>
          <p className="text-3xl font-bold text-yellow-600">
            {projects.filter((p) => p.status === 'pending').length}
          </p>
        </div>
      </div>

      {/* 프로젝트 목록 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">내 프로젝트</h2>
          <Link
            href="/projects/create"
            className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            <span>새 프로젝트</span>
          </Link>
        </div>
        <div className="divide-y">
          {projects.length === 0 ? (
            <div className="p-12 text-center">
              <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">
                아직 생성된 프로젝트가 없습니다.
              </p>
              <Link
                href="/projects/create"
                className="inline-flex items-center gap-2 px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700"
              >
                <Plus className="w-4 h-4" />
                <span>첫 프로젝트 만들기</span>
              </Link>
            </div>
          ) : (
            projects.map((project) => (
              <Link
                key={project.project_id}
                href={`/projects/${project.project_id}`}
                className="block px-6 py-4 hover:bg-gray-50"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {statusIcons[project.status]}
                      <h3 className="text-lg font-semibold text-gray-900">
                        {project.project_name}
                      </h3>
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                        {project.valuation_method.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>
                        상태: {statusNames[project.status] || project.status}
                      </span>
                      <span>단계: {project.current_step}/14</span>
                      <span>
                        생성: {new Date(project.created_at).toLocaleDateString('ko-KR')}
                      </span>
                    </div>
                  </div>
                  <div className="text-red-600">→</div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </MyPageTemplate>
  )
}
```

---

### 3. 나머지 5개 역할별 마이페이지

**파일**:
- `app/mypage/accountant/page.tsx` - 회계사 (담당 프로젝트 목록)
- `app/mypage/investor/page.tsx` - 투자자 (Deal 뉴스, 투자 관심 기업)
- `app/mypage/partner/page.tsx` - 파트너 (추천 현황)
- `app/mypage/supporter/page.tsx` - 서포터 (지원 통계)
- `app/mypage/admin/page.tsx` - 관리자 (전체 통계, 사용자 관리)

**공통 구조**:
1. 역할별 통계 카드
2. 역할별 주요 데이터 목록 (프로젝트, 뉴스, 사용자 등)
3. 역할별 액션 버튼

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `components/mypage-template.tsx` | 공통 마이페이지 템플릿 | ~100줄 |
| `app/mypage/company/page.tsx` | 기업 마이페이지 | ~200줄 |
| `app/mypage/accountant/page.tsx` | 회계사 마이페이지 | ~180줄 |
| `app/mypage/investor/page.tsx` | 투자자 마이페이지 | ~180줄 |
| `app/mypage/partner/page.tsx` | 파트너 마이페이지 | ~150줄 |
| `app/mypage/supporter/page.tsx` | 서포터 마이페이지 | ~150줄 |
| `app/mypage/admin/page.tsx` | 관리자 마이페이지 | ~300줄 |

**총 파일 수**: 7개
**총 라인 수**: ~1,260줄

---

## 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **Database**: Supabase (users, projects 테이블)
- **Icons**: lucide-react

---

## 완료 기준

### 필수 (Must Have)

- [ ] 공통 템플릿 컴포넌트 구현
- [ ] 6개 역할별 마이페이지 구현
- [ ] 역할 기반 데이터 로드 (RLS)
- [ ] 로그아웃 기능
- [ ] 반응형 디자인

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 역할별 페이지 정상 렌더링
- [ ] 데이터 정상 로드
- [ ] 로그아웃 동작 확인

### 권장 (Nice to Have)

- [ ] 프로필 수정 기능
- [ ] 알림 센터
- [ ] 활동 로그

---

## 참조

### 기존 프로토타입

- `Valuation_Company/valuation-platform/frontend/app/core/mypage-admin.html`

### 관련 Task

- **S1BI1**: Next.js 초기화
- **S1D1**: users, projects 테이블
- **S2F6**: 프로젝트 관리 페이지

---

## 주의사항

1. **RLS 보안**
   - 본인 데이터만 조회 가능
   - 역할 기반 접근 제어

2. **성능**
   - 프로젝트 목록 페이지네이션 (10개씩)
   - 관리자 페이지 최적화

3. **UX**
   - 빈 상태 명확히 표시
   - 로딩 상태 표시

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 7개
**라인 수**: ~1,260줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
