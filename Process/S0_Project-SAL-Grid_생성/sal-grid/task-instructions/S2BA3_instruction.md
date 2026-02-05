# S2BA3: Documents & Reports API

## Task 정보

- **Task ID**: S2BA3
- **Task Name**: 문서 및 보고서 API
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (Supabase Storage 설정), S1D1 (documents 테이블)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

파일 업로드(Supabase Storage), 초안/수정/최종 보고서 관리 API 구현

---

## 상세 지시사항

### 1. 문서 업로드 API

**파일**: `app/api/documents/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// POST: 파일 업로드
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const formData = await request.formData()
    const file = formData.get('file') as File
    const project_id = formData.get('project_id') as string
    const document_type = formData.get('document_type') as string

    if (!file || !project_id || !document_type) {
      return NextResponse.json(
        { error: 'file, project_id, and document_type are required' },
        { status: 400 }
      )
    }

    // Supabase Storage에 업로드
    const fileName = `${Date.now()}-${file.name}`
    const filePath = `projects/${project_id}/documents/${fileName}`

    const { error: uploadError } = await supabase.storage
      .from('valuation-documents')
      .upload(filePath, file)

    if (uploadError) {
      return NextResponse.json(
        { error: uploadError.message },
        { status: 500 }
      )
    }

    // documents 테이블에 메타데이터 저장
    const { data, error } = await supabase
      .from('documents')
      .insert({
        project_id,
        document_type,
        file_name: file.name,
        file_path: filePath,
        file_size: file.size,
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ document: data }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

### 2. 초안 API

**파일**: `app/api/drafts/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// POST: 초안 생성
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const body = await request.json()
    const { project_id, draft_content, draft_version } = body

    if (!project_id || !draft_content) {
      return NextResponse.json(
        { error: 'project_id and draft_content are required' },
        { status: 400 }
      )
    }

    const { data, error } = await supabase
      .from('drafts')
      .insert({
        project_id,
        draft_content,
        draft_version: draft_version || 1,
        status: 'pending',
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ draft: data }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// GET: 초안 조회
export async function GET(request: NextRequest) {
  try {
    const supabase = createClient()
    const { searchParams } = new URL(request.url)
    const project_id = searchParams.get('project_id')

    if (!project_id) {
      return NextResponse.json(
        { error: 'project_id is required' },
        { status: 400 }
      )
    }

    const { data, error } = await supabase
      .from('drafts')
      .select('*')
      .eq('project_id', project_id)
      .order('draft_version', { ascending: false })

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ drafts: data })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

### 3. 수정 요청 API

**파일**: `app/api/revisions/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// POST: 수정 요청 생성
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const body = await request.json()
    const { draft_id, revision_request } = body

    if (!draft_id || !revision_request) {
      return NextResponse.json(
        { error: 'draft_id and revision_request are required' },
        { status: 400 }
      )
    }

    const { data, error } = await supabase
      .from('revisions')
      .insert({
        draft_id,
        revision_request,
        status: 'pending',
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ revision: data }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

### 4. 최종 보고서 API

**파일**: `app/api/reports/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// POST: 최종 보고서 생성 (PDF)
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const body = await request.json()
    const { project_id, report_content } = body

    if (!project_id || !report_content) {
      return NextResponse.json(
        { error: 'project_id and report_content are required' },
        { status: 400 }
      )
    }

    // TODO: PDF 생성 로직 구현 (향후 라이브러리 사용)
    // 현재는 HTML 저장
    const report_file_path = `projects/${project_id}/reports/final_report.html`

    const { data, error } = await supabase
      .from('reports')
      .insert({
        project_id,
        report_file_path,
        report_content,
        status: 'final',
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ report: data }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// GET: 보고서 다운로드 URL 생성
export async function GET(request: NextRequest) {
  try {
    const supabase = createClient()
    const { searchParams } = new URL(request.url)
    const project_id = searchParams.get('project_id')

    if (!project_id) {
      return NextResponse.json(
        { error: 'project_id is required' },
        { status: 400 }
      )
    }

    const { data: report } = await supabase
      .from('reports')
      .select('report_file_path')
      .eq('project_id', project_id)
      .single()

    if (!report) {
      return NextResponse.json(
        { error: 'Report not found' },
        { status: 404 }
      )
    }

    // Supabase Storage 다운로드 URL 생성 (1시간 유효)
    const { data: signedUrl } = await supabase.storage
      .from('valuation-documents')
      .createSignedUrl(report.report_file_path, 3600)

    return NextResponse.json({ download_url: signedUrl.signedUrl })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `app/api/documents/route.ts` | 파일 업로드 API | ~100줄 |
| `app/api/drafts/route.ts` | 초안 관리 API | ~100줄 |
| `app/api/revisions/route.ts` | 수정 요청 API | ~60줄 |
| `app/api/reports/route.ts` | 최종 보고서 API | ~100줄 |

**총 파일 수**: 4개
**총 라인 수**: ~360줄

---

## 완료 기준

### 필수
- [ ] 파일 업로드 API 구현 (Supabase Storage)
- [ ] 초안 관리 API 구현
- [ ] 수정 요청 API 구현
- [ ] 보고서 다운로드 API 구현
- [ ] Signed URL 생성

### 검증
- [ ] 파일 업로드 동작 확인
- [ ] 초안 생성/조회 동작 확인
- [ ] 보고서 다운로드 URL 생성 확인

### 권장
- [ ] PDF 생성 라이브러리 연동 (puppeteer, jspdf)

---

**작업 복잡도**: High
**작성일**: 2026-02-05
