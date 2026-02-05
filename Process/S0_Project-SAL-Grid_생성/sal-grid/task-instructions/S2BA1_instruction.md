# S2BA1: Valuation Process API & 14-Step Workflow

## Task 정보

- **Task ID**: S2BA1
- **Task Name**: 평가 프로세스 API 및 14단계 워크플로우
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (Supabase 설정), S1D1 (DB 스키마)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

14단계 평가 워크플로우를 관리하는 API와 22개 AI 승인 포인트 시스템을 구현

---

## 상세 지시사항

### 0. 전제조건 확인

**S1BI1 완료 확인:**
- Supabase 클라이언트 설정 완료

**S1D1 완료 확인:**
- projects, approval_points 테이블 존재

---

### 1. 워크플로우 관리자

**파일**: `lib/workflow/workflow-manager.ts`

```typescript
import { createClient } from '@/lib/supabase/server'

export type WorkflowStep = {
  step_number: number
  step_name: string
  description: string
  required_role?: 'customer' | 'accountant' | 'admin'
  approval_required: boolean
}

export const WORKFLOW_STEPS: WorkflowStep[] = [
  { step_number: 1, step_name: 'project_creation', description: '프로젝트 생성', approval_required: false },
  { step_number: 2, step_name: 'quote_request', description: '견적 요청', approval_required: false },
  { step_number: 3, step_name: 'negotiation', description: '협상', approval_required: false },
  { step_number: 4, step_name: 'document_upload', description: '문서 업로드', approval_required: false },
  { step_number: 5, step_name: 'evaluation_progress', description: '평가 진행', approval_required: true, required_role: 'accountant' },
  { step_number: 6, step_name: 'data_collection', description: '데이터 수집', approval_required: true, required_role: 'accountant' },
  { step_number: 7, step_name: 'accountant_review', description: '회계사 검토', approval_required: true, required_role: 'accountant' },
  { step_number: 8, step_name: 'draft_generation', description: '초안 생성', approval_required: true },
  { step_number: 9, step_name: 'report_draft', description: '초안 확인', approval_required: true, required_role: 'customer' },
  { step_number: 10, step_name: 'revision_request', description: '수정 요청', approval_required: false },
  { step_number: 11, step_name: 'final_preparation', description: '최종 준비', approval_required: true, required_role: 'accountant' },
  { step_number: 12, step_name: 'report_final', description: '최종 보고서', approval_required: true, required_role: 'customer' },
  { step_number: 13, step_name: 'payment', description: '결제', approval_required: false },
  { step_number: 14, step_name: 'report_download', description: '보고서 다운로드', approval_required: false },
]

export class WorkflowManager {
  constructor(private projectId: string) {}

  async getCurrentStep(): Promise<number> {
    const supabase = createClient()

    const { data } = await supabase
      .from('projects')
      .select('current_step')
      .eq('project_id', this.projectId)
      .single()

    return data?.current_step || 1
  }

  async advanceStep(): Promise<{ success: boolean; nextStep: number }> {
    const supabase = createClient()
    const currentStep = await this.getCurrentStep()

    if (currentStep >= 14) {
      return { success: false, nextStep: 14 }
    }

    const nextStep = currentStep + 1

    const { error } = await supabase
      .from('projects')
      .update({
        current_step: nextStep,
        updated_at: new Date().toISOString(),
      })
      .eq('project_id', this.projectId)

    if (error) {
      console.error('Failed to advance step:', error)
      return { success: false, nextStep: currentStep }
    }

    return { success: true, nextStep }
  }

  async canAdvanceToStep(stepNumber: number): Promise<boolean> {
    const currentStep = await this.getCurrentStep()

    // 현재 단계보다 1단계 앞으로만 이동 가능
    if (stepNumber !== currentStep + 1) {
      return false
    }

    // 승인이 필요한 단계인지 확인
    const step = WORKFLOW_STEPS.find((s) => s.step_number === currentStep)
    if (step?.approval_required) {
      // 승인이 필요한 경우 approval_points 확인
      const approved = await this.isStepApproved(currentStep)
      return approved
    }

    return true
  }

  async isStepApproved(stepNumber: number): Promise<boolean> {
    const supabase = createClient()

    const { data } = await supabase
      .from('approval_points')
      .select('approved')
      .eq('project_id', this.projectId)
      .eq('step_number', stepNumber)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    return data?.approved === true
  }

  async getStepInfo(stepNumber: number): Promise<WorkflowStep | undefined> {
    return WORKFLOW_STEPS.find((s) => s.step_number === stepNumber)
  }

  async getAllSteps(): Promise<WorkflowStep[]> {
    return WORKFLOW_STEPS
  }
}
```

---

### 2. 승인 포인트 관리자

**파일**: `lib/workflow/approval-points.ts`

```typescript
import { createClient } from '@/lib/supabase/server'

export type ApprovalPoint = {
  approval_id: string
  project_id: string
  step_number: number
  approved_by?: string
  approved: boolean
  approval_type: 'auto' | 'manual' | 'ai'
  approval_message?: string
  created_at: string
}

export class ApprovalPointManager {
  constructor(private projectId: string) {}

  async createApprovalPoint(
    stepNumber: number,
    approvalType: 'auto' | 'manual' | 'ai',
    approvedBy?: string,
    message?: string
  ): Promise<ApprovalPoint | null> {
    const supabase = createClient()

    const { data, error } = await supabase
      .from('approval_points')
      .insert({
        project_id: this.projectId,
        step_number: stepNumber,
        approved: false,
        approval_type: approvalType,
        approved_by: approvedBy,
        approval_message: message,
      })
      .select()
      .single()

    if (error) {
      console.error('Failed to create approval point:', error)
      return null
    }

    return data as ApprovalPoint
  }

  async approveStep(
    stepNumber: number,
    userId: string,
    message?: string
  ): Promise<boolean> {
    const supabase = createClient()

    // 기존 승인 포인트 찾기
    const { data: existing } = await supabase
      .from('approval_points')
      .select('*')
      .eq('project_id', this.projectId)
      .eq('step_number', stepNumber)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    if (existing) {
      // 기존 승인 포인트 업데이트
      const { error } = await supabase
        .from('approval_points')
        .update({
          approved: true,
          approved_by: userId,
          approval_message: message,
          updated_at: new Date().toISOString(),
        })
        .eq('approval_id', existing.approval_id)

      if (error) {
        console.error('Failed to approve step:', error)
        return false
      }
    } else {
      // 새 승인 포인트 생성
      const { error } = await supabase.from('approval_points').insert({
        project_id: this.projectId,
        step_number: stepNumber,
        approved: true,
        approval_type: 'manual',
        approved_by: userId,
        approval_message: message,
      })

      if (error) {
        console.error('Failed to create approval:', error)
        return false
      }
    }

    return true
  }

  async getApprovalHistory(
    stepNumber?: number
  ): Promise<ApprovalPoint[]> {
    const supabase = createClient()

    let query = supabase
      .from('approval_points')
      .select('*')
      .eq('project_id', this.projectId)
      .order('created_at', { ascending: false })

    if (stepNumber) {
      query = query.eq('step_number', stepNumber)
    }

    const { data } = await query

    return (data as ApprovalPoint[]) || []
  }

  async getPendingApprovals(): Promise<ApprovalPoint[]> {
    const supabase = createClient()

    const { data } = await supabase
      .from('approval_points')
      .select('*')
      .eq('project_id', this.projectId)
      .eq('approved', false)
      .order('created_at', { ascending: false })

    return (data as ApprovalPoint[]) || []
  }

  async isStepApproved(stepNumber: number): Promise<boolean> {
    const supabase = createClient()

    const { data } = await supabase
      .from('approval_points')
      .select('approved')
      .eq('project_id', this.projectId)
      .eq('step_number', stepNumber)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    return data?.approved === true
  }
}
```

---

### 3. 워크플로우 API 엔드포인트

**파일**: `app/api/valuation/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { WorkflowManager } from '@/lib/workflow/workflow-manager'
import { ApprovalPointManager } from '@/lib/workflow/approval-points'

// GET: 현재 워크플로우 상태 조회
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const projectId = searchParams.get('project_id')

    if (!projectId) {
      return NextResponse.json(
        { error: 'project_id is required' },
        { status: 400 }
      )
    }

    const workflow = new WorkflowManager(projectId)
    const currentStep = await workflow.getCurrentStep()
    const allSteps = await workflow.getAllSteps()
    const currentStepInfo = await workflow.getStepInfo(currentStep)

    const approvalManager = new ApprovalPointManager(projectId)
    const pendingApprovals = await approvalManager.getPendingApprovals()

    return NextResponse.json({
      project_id: projectId,
      current_step: currentStep,
      current_step_info: currentStepInfo,
      all_steps: allSteps,
      pending_approvals: pendingApprovals,
    })
  } catch (error) {
    console.error('Workflow GET error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// POST: 다음 단계로 진행
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { project_id, action } = body

    if (!project_id) {
      return NextResponse.json(
        { error: 'project_id is required' },
        { status: 400 }
      )
    }

    const workflow = new WorkflowManager(project_id)
    const approvalManager = new ApprovalPointManager(project_id)

    switch (action) {
      case 'advance': {
        const currentStep = await workflow.getCurrentStep()
        const canAdvance = await workflow.canAdvanceToStep(currentStep + 1)

        if (!canAdvance) {
          return NextResponse.json(
            { error: 'Cannot advance: approval required or invalid step' },
            { status: 400 }
          )
        }

        const result = await workflow.advanceStep()

        return NextResponse.json({
          success: result.success,
          next_step: result.nextStep,
        })
      }

      case 'approve': {
        const { step_number, user_id, message } = body

        if (!step_number || !user_id) {
          return NextResponse.json(
            { error: 'step_number and user_id are required' },
            { status: 400 }
          )
        }

        const approved = await approvalManager.approveStep(
          step_number,
          user_id,
          message
        )

        if (!approved) {
          return NextResponse.json(
            { error: 'Failed to approve step' },
            { status: 500 }
          )
        }

        return NextResponse.json({
          success: true,
          step_number,
          approved: true,
        })
      }

      case 'create_approval_point': {
        const { step_number, approval_type, approved_by, message } = body

        if (!step_number || !approval_type) {
          return NextResponse.json(
            { error: 'step_number and approval_type are required' },
            { status: 400 }
          )
        }

        const approvalPoint = await approvalManager.createApprovalPoint(
          step_number,
          approval_type,
          approved_by,
          message
        )

        if (!approvalPoint) {
          return NextResponse.json(
            { error: 'Failed to create approval point' },
            { status: 500 }
          )
        }

        return NextResponse.json({
          success: true,
          approval_point: approvalPoint,
        })
      }

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('Workflow POST error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/workflow/workflow-manager.ts` | 워크플로우 관리 로직 | ~150줄 |
| `lib/workflow/approval-points.ts` | 승인 포인트 관리 로직 | ~180줄 |
| `app/api/valuation/route.ts` | 워크플로우 API 엔드포인트 | ~170줄 |

**총 파일 수**: 3개
**총 라인 수**: ~500줄

---

## 기술 스택

- **Runtime**: Next.js 14 Route Handlers
- **Language**: TypeScript 5.x
- **Database**: Supabase (projects, approval_points 테이블)
- **Pattern**: Class-based Service Layer

---

## 완료 기준

### 필수 (Must Have)

- [ ] 워크플로우 관리자 구현
- [ ] 승인 포인트 관리자 구현
- [ ] API 엔드포인트 구현 (GET, POST)
- [ ] 단계 진행 로직 구현
- [ ] 승인 로직 구현

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] API 호출 시 200 응답
- [ ] 워크플로우 단계 진행 동작
- [ ] 승인 로직 동작 확인

### 권장 (Nice to Have)

- [ ] 롤백 기능
- [ ] 단계 건너뛰기 (관리자 전용)
- [ ] 알림 발송 연동

---

## 참조

### 기존 프로토타입

- `Valuation_Company/valuation-platform/backend/app/api/v1/endpoints/valuation.py`
- `Valuation_Company/valuation-platform/backend/app/services/valuation_orchestrator.py`

### 관련 Task

- **S1BI1**: Supabase 설정
- **S1D1**: projects, approval_points 테이블
- **S2F5**: 프로세스 단계 페이지 (API 호출)

---

## 주의사항

1. **단계 순서**
   - 반드시 순서대로 진행 (건너뛰기 불가)
   - 이전 단계 완료 확인 필수

2. **승인 로직**
   - 승인이 필요한 단계만 approval_points 생성
   - 승인 완료 후 다음 단계 진행 가능

3. **RLS 보안**
   - 본인 프로젝트만 조회/수정
   - 역할 기반 승인 권한 확인

4. **에러 처리**
   - 명확한 에러 메시지
   - 트랜잭션 고려 (향후)

---

## 예상 소요 시간

**작업 복잡도**: High
**파일 수**: 3개
**라인 수**: ~500줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
