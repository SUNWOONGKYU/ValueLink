# S2BA2: Projects & Evaluation Requests API

## Task 정보

- **Task ID**: S2BA2
- **Task Name**: 프로젝트 및 평가 요청 API
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (Supabase 설정), S1D1 (DB 스키마)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

3단계 프로젝트 라이프사이클 API 구현:
1. **evaluation_requests**: 고객 평가 요청 → 관리자 승인/거절
2. **projects**: 승인된 프로젝트 진행
3. **project_history**: 완료된 프로젝트 아카이브

---

## 상세 지시사항

### 1. 평가 요청 API

**파일**: `app/api/evaluation-requests/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// GET: 평가 요청 목록 조회
export async function GET(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status')

    let query = supabase
      .from('evaluation_requests')
      .select('*')
      .order('created_at', { ascending: false })

    // 고객: 본인 요청만
    // 관리자: 전체 요청
    const { data: userData } = await supabase
      .from('users')
      .select('role')
      .eq('id', user.id)
      .single()

    if (userData?.role !== 'admin') {
      query = query.eq('user_id', user.id)
    }

    if (status) {
      query = query.eq('status', status)
    }

    const { data, error } = await query

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ evaluation_requests: data })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// POST: 평가 요청 생성 (고객)
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const {
      company_name,
      company_name_en,
      valuation_method,
      company_website,
      address,
      phone,
      fax,
      requirements,
      budget_min,
      budget_max
    } = body

    if (!company_name || !valuation_method) {
      return NextResponse.json(
        { error: 'company_name and valuation_method are required' },
        { status: 400 }
      )
    }

    const { data, error } = await supabase
      .from('evaluation_requests')
      .insert({
        user_id: user.id,
        company_name,
        company_name_en,
        valuation_method,
        company_website,
        address,
        phone,
        fax,
        requirements,
        budget_min,
        budget_max,
        status: 'pending', // 관리자 승인 대기
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ evaluation_request: data }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// PUT: 평가 요청 승인/거절 (관리자)
export async function PUT(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // 관리자 권한 확인
    const { data: userData } = await supabase
      .from('users')
      .select('role')
      .eq('id', user.id)
      .single()

    if (userData?.role !== 'admin') {
      return NextResponse.json({ error: 'Admin access required' }, { status: 403 })
    }

    const body = await request.json()
    const { request_id, action, accountant_id, rejection_reason } = body

    if (!request_id || !action) {
      return NextResponse.json(
        { error: 'request_id and action are required' },
        { status: 400 }
      )
    }

    if (action === 'approve') {
      // 승인: evaluation_requests 상태 변경 + projects 테이블에 복사
      const { data: requestData, error: fetchError } = await supabase
        .from('evaluation_requests')
        .select('*')
        .eq('request_id', request_id)
        .single()

      if (fetchError) {
        return NextResponse.json({ error: fetchError.message }, { status: 500 })
      }

      // projects 테이블에 생성
      const { data: projectData, error: projectError } = await supabase
        .from('projects')
        .insert({
          user_id: requestData.user_id,
          company_name: requestData.company_name,
          company_name_en: requestData.company_name_en,
          valuation_method: requestData.valuation_method,
          company_website: requestData.company_website,
          address: requestData.address,
          phone: requestData.phone,
          fax: requestData.fax,
          requirements: requestData.requirements,
          budget_min: requestData.budget_min,
          budget_max: requestData.budget_max,
          accountant_id: accountant_id,
          status: 'in_progress',
          current_step: 1,
        })
        .select()
        .single()

      if (projectError) {
        return NextResponse.json({ error: projectError.message }, { status: 500 })
      }

      // evaluation_requests 상태 업데이트
      await supabase
        .from('evaluation_requests')
        .update({
          status: 'approved',
          approved_at: new Date().toISOString(),
          approved_by: user.id,
        })
        .eq('request_id', request_id)

      return NextResponse.json({ project: projectData })
    } else if (action === 'reject') {
      const { error } = await supabase
        .from('evaluation_requests')
        .update({
          status: 'rejected',
          rejection_reason: rejection_reason || 'No reason provided',
        })
        .eq('request_id', request_id)

      if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 })
      }

      return NextResponse.json({ message: 'Request rejected' })
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

### 2. 프로젝트 API

**파일**: `app/api/projects/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// GET: 프로젝트 목록 조회
export async function GET(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status')

    let query = supabase
      .from('projects')
      .select('*, accountants(name, email)')
      .order('created_at', { ascending: false })

    // 역할별 필터링
    const { data: userData } = await supabase
      .from('users')
      .select('role')
      .eq('id', user.id)
      .single()

    if (userData?.role === 'customer') {
      query = query.eq('user_id', user.id)
    } else if (userData?.role === 'accountant') {
      query = query.eq('accountant_id', user.id)
    }
    // admin: 전체 조회

    if (status) {
      query = query.eq('status', status)
    }

    const { data, error } = await query

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ projects: data })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// PUT: 프로젝트 상태/단계 업데이트
export async function PUT(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { project_id, ...updates } = body

    if (!project_id) {
      return NextResponse.json({ error: 'project_id is required' }, { status: 400 })
    }

    const { data, error } = await supabase
      .from('projects')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('project_id', project_id)
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ project: data })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

### 3. 프로젝트 히스토리 API

**파일**: `app/api/project-history/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// GET: 완료된 프로젝트 조회
export async function GET(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const year = searchParams.get('year')

    let query = supabase
      .from('project_history')
      .select('*')
      .order('completed_at', { ascending: false })

    // 역할별 필터링
    const { data: userData } = await supabase
      .from('users')
      .select('role')
      .eq('id', user.id)
      .single()

    if (userData?.role === 'customer') {
      query = query.eq('user_id', user.id)
    } else if (userData?.role === 'accountant') {
      query = query.eq('accountant_id', user.id)
    }

    if (year) {
      query = query.gte('completed_at', `${year}-01-01`)
               .lte('completed_at', `${year}-12-31`)
    }

    const { data, error } = await query

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ history: data })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// POST: 프로젝트 완료 → 히스토리로 이동
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { project_id, final_amount } = body

    if (!project_id) {
      return NextResponse.json({ error: 'project_id is required' }, { status: 400 })
    }

    // 프로젝트 데이터 조회
    const { data: projectData, error: fetchError } = await supabase
      .from('projects')
      .select('*')
      .eq('project_id', project_id)
      .single()

    if (fetchError) {
      return NextResponse.json({ error: fetchError.message }, { status: 500 })
    }

    // project_history에 추가
    const { data: historyData, error: historyError } = await supabase
      .from('project_history')
      .insert({
        original_project_id: project_id,
        user_id: projectData.user_id,
        accountant_id: projectData.accountant_id,
        company_name: projectData.company_name,
        company_name_en: projectData.company_name_en,
        valuation_method: projectData.valuation_method,
        company_website: projectData.company_website,
        address: projectData.address,
        phone: projectData.phone,
        fax: projectData.fax,
        final_amount: final_amount || projectData.total_amount,
        completed_at: new Date().toISOString(),
      })
      .select()
      .single()

    if (historyError) {
      return NextResponse.json({ error: historyError.message }, { status: 500 })
    }

    // 원본 프로젝트 상태 변경
    await supabase
      .from('projects')
      .update({ status: 'completed' })
      .eq('project_id', project_id)

    return NextResponse.json({ history: historyData }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `app/api/evaluation-requests/route.ts` | 평가 요청 CRUD + 승인/거절 | ~180줄 |
| `app/api/projects/route.ts` | 프로젝트 조회/업데이트 | ~100줄 |
| `app/api/project-history/route.ts` | 히스토리 조회 + 완료 처리 | ~120줄 |

**총 파일 수**: 3개
**총 라인 수**: ~400줄

---

## 완료 기준

### 필수
- [ ] 평가 요청 생성 API 구현 (고객)
- [ ] 평가 요청 승인/거절 API 구현 (관리자)
- [ ] 프로젝트 목록 조회 API 구현 (역할별 필터링)
- [ ] 프로젝트 상태 업데이트 API 구현
- [ ] 프로젝트 완료 → 히스토리 이동 API 구현
- [ ] RLS 보안 적용
- [ ] 에러 핸들링

### 검증
- [ ] TypeScript 빌드 성공
- [ ] API 호출 시 200/201 응답
- [ ] 역할별 접근 제어 확인
- [ ] 3단계 라이프사이클 테스트 (요청 → 승인 → 완료)

---

## 데이터 흐름

```
고객 요청 생성
     ↓
evaluation_requests (status: pending)
     ↓
관리자 승인
     ↓
projects (status: in_progress)
     ↓
14단계 워크플로우 진행
     ↓
프로젝트 완료
     ↓
project_history (아카이브)
```

---

**작업 복잡도**: Medium-High
**작성일**: 2026-02-07
**수정일**: 2026-02-07 (v4 스키마 반영: quotes/negotiations 삭제)
