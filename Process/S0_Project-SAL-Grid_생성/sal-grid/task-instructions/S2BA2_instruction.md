# S2BA2: Projects & Quotes API

## Task 정보

- **Task ID**: S2BA2
- **Task Name**: 프로젝트 및 견적 API
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (Supabase 설정), S1D1 (DB 스키마)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

프로젝트 생성/조회/수정/삭제 (CRUD) 및 견적/협상 API 구현

---

## 상세 지시사항

### 1. 프로젝트 API

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
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

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

// POST: 프로젝트 생성
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { project_name, valuation_method } = body

    if (!project_name || !valuation_method) {
      return NextResponse.json(
        { error: 'project_name and valuation_method are required' },
        { status: 400 }
      )
    }

    const { data, error } = await supabase
      .from('projects')
      .insert({
        user_id: user.id,
        project_name,
        valuation_method,
        status: 'pending',
        current_step: 1,
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ project: data }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// PUT: 프로젝트 수정
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
      .eq('user_id', user.id)
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

### 2. 견적 API

**파일**: `app/api/quotes/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// POST: 견적 생성
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const body = await request.json()
    const { project_id, amount, deposit_amount, delivery_days, description } = body

    if (!project_id || !amount) {
      return NextResponse.json(
        { error: 'project_id and amount are required' },
        { status: 400 }
      )
    }

    const balance_amount = amount - (deposit_amount || 0)

    const { data, error } = await supabase
      .from('quotes')
      .insert({
        project_id,
        amount,
        deposit_amount: deposit_amount || amount / 2,
        balance_amount,
        delivery_days: delivery_days || 10,
        description,
        status: 'pending',
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ quote: data }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

### 3. 협상 API

**파일**: `app/api/negotiations/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// POST: 협상 제안 생성
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const body = await request.json()
    const { quote_id, negotiation_type, proposed_amount, message } = body

    if (!quote_id || !negotiation_type) {
      return NextResponse.json(
        { error: 'quote_id and negotiation_type are required' },
        { status: 400 }
      )
    }

    const { data, error } = await supabase
      .from('negotiations')
      .insert({
        quote_id,
        negotiation_type,
        proposed_amount,
        message,
        status: 'pending',
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ negotiation: data }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `app/api/projects/route.ts` | 프로젝트 CRUD API | ~150줄 |
| `app/api/quotes/route.ts` | 견적 API | ~80줄 |
| `app/api/negotiations/route.ts` | 협상 API | ~70줄 |

**총 파일 수**: 3개
**총 라인 수**: ~300줄

---

## 완료 기준

### 필수
- [ ] 프로젝트 CRUD API 구현
- [ ] 견적 생성 API 구현
- [ ] 협상 API 구현
- [ ] RLS 보안 적용
- [ ] 에러 핸들링

### 검증
- [ ] TypeScript 빌드 성공
- [ ] API 호출 시 200/201 응답
- [ ] 본인 프로젝트만 접근 확인

---

**작업 복잡도**: Medium
**작성일**: 2026-02-05
