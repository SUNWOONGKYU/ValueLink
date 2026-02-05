# S3BA1: Valuation Engine Orchestrator

## Task 정보

- **Task ID**: S3BA1
- **Task Name**: 평가 엔진 오케스트레이터
- **Stage**: S3 (Valuation Engines - 개발 2차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S2BA1 (Workflow API)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

5개 평가 엔진(DCF, Relative, Asset, Intrinsic, Tax)의 실행을 관리하고 조율하는 오케스트레이터 구현

---

## 상세 지시사항

### 1. 평가 엔진 공통 인터페이스

**파일**: `lib/valuation/engine-interface.ts`

```typescript
export type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'

export interface ValuationInput {
  project_id: string
  method: ValuationMethod
  financial_data: Record<string, any>
  assumptions: Record<string, any>
}

export interface ValuationResult {
  project_id: string
  method: ValuationMethod
  enterprise_value: number
  equity_value: number
  share_price: number
  calculation_details: Record<string, any>
  sensitivity_data?: Record<string, any>
  created_at: string
}

export abstract class ValuationEngine {
  protected method: ValuationMethod

  constructor(method: ValuationMethod) {
    this.method = method
  }

  abstract calculate(input: ValuationInput): Promise<ValuationResult>

  abstract validate(input: ValuationInput): { valid: boolean; errors: string[] }

  protected async saveResult(result: ValuationResult): Promise<void> {
    // Supabase에 결과 저장 로직
  }
}
```

---

### 2. 평가 엔진 오케스트레이터

**파일**: `lib/valuation/orchestrator.ts`

```typescript
import { createClient } from '@/lib/supabase/server'
import type { ValuationEngine, ValuationInput, ValuationResult, ValuationMethod } from './engine-interface'

export class ValuationOrchestrator {
  private engines: Map<ValuationMethod, ValuationEngine> = new Map()

  registerEngine(method: ValuationMethod, engine: ValuationEngine) {
    this.engines.set(method, engine)
  }

  async executeValuation(input: ValuationInput): Promise<ValuationResult> {
    // 1. 엔진 존재 확인
    const engine = this.engines.get(input.method)
    if (!engine) {
      throw new Error(`Valuation engine not found for method: ${input.method}`)
    }

    // 2. 입력 검증
    const validation = engine.validate(input)
    if (!validation.valid) {
      throw new Error(`Validation failed: ${validation.errors.join(', ')}`)
    }

    // 3. 평가 실행
    try {
      const result = await engine.calculate(input)

      // 4. 결과 저장 (Supabase)
      await this.saveValuationResult(result)

      // 5. 프로젝트 상태 업데이트
      await this.updateProjectStatus(input.project_id, 'valuation_completed')

      return result
    } catch (error) {
      // 에러 로깅
      await this.logError(input.project_id, input.method, error)
      throw error
    }
  }

  private async saveValuationResult(result: ValuationResult): Promise<void> {
    const supabase = createClient()

    const { error } = await supabase
      .from('valuation_results')
      .insert({
        project_id: result.project_id,
        valuation_method: result.method,
        enterprise_value: result.enterprise_value,
        equity_value: result.equity_value,
        share_price: result.share_price,
        calculation_details: result.calculation_details,
        sensitivity_data: result.sensitivity_data,
      })

    if (error) {
      throw new Error(`Failed to save valuation result: ${error.message}`)
    }
  }

  private async updateProjectStatus(
    project_id: string,
    status: string
  ): Promise<void> {
    const supabase = createClient()

    const { error } = await supabase
      .from('projects')
      .update({ status, updated_at: new Date().toISOString() })
      .eq('id', project_id)

    if (error) {
      console.error('Failed to update project status:', error)
    }
  }

  private async logError(
    project_id: string,
    method: ValuationMethod,
    error: any
  ): Promise<void> {
    console.error(`Valuation error for ${project_id} (${method}):`, error)
    // TODO: 에러 로그를 별도 테이블에 저장
  }

  async getAvailableEngines(): ValuationMethod[] {
    return Array.from(this.engines.keys())
  }

  async getEngineStatus(method: ValuationMethod): Promise<{
    available: boolean
    version?: string
  }> {
    const engine = this.engines.get(method)
    return {
      available: !!engine,
      version: '1.0.0',
    }
  }
}

// 싱글톤 인스턴스 export
export const orchestrator = new ValuationOrchestrator()
```

---

### 3. 평가 실행 API

**파일**: `app/api/valuation/execute/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { orchestrator } from '@/lib/valuation/orchestrator'
import type { ValuationInput } from '@/lib/valuation/engine-interface'

// POST: 평가 실행
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { project_id, method, financial_data, assumptions } = body

    if (!project_id || !method || !financial_data) {
      return NextResponse.json(
        { error: 'project_id, method, and financial_data are required' },
        { status: 400 }
      )
    }

    // 프로젝트 소유권 확인
    const { data: project } = await supabase
      .from('projects')
      .select('id, user_id')
      .eq('id', project_id)
      .eq('user_id', user.id)
      .single()

    if (!project) {
      return NextResponse.json(
        { error: 'Project not found or access denied' },
        { status: 404 }
      )
    }

    // 평가 실행
    const input: ValuationInput = {
      project_id,
      method,
      financial_data,
      assumptions,
    }

    const result = await orchestrator.executeValuation(input)

    return NextResponse.json({ result }, { status: 200 })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Valuation execution failed' },
      { status: 500 }
    )
  }
}

// GET: 평가 결과 조회
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
      .from('valuation_results')
      .select('*')
      .eq('project_id', project_id)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ result: data })
  } catch (error: any) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/valuation/engine-interface.ts` | 공통 인터페이스 | ~80줄 |
| `lib/valuation/orchestrator.ts` | 오케스트레이터 | ~150줄 |
| `app/api/valuation/execute/route.ts` | 평가 실행 API | ~100줄 |

**총 파일 수**: 3개
**총 라인 수**: ~330줄

---

## 기술 스택

- **TypeScript 5.x**: 타입 안전성
- **Next.js 14 Route Handlers**: API 엔드포인트
- **Supabase**: 데이터베이스
- **Abstract Class Pattern**: 엔진 인터페이스
- **Singleton Pattern**: 오케스트레이터 인스턴스

---

## 완료 기준

### 필수 (Must Have)

- [ ] 공통 인터페이스 정의 (`ValuationEngine` 추상 클래스)
- [ ] 오케스트레이터 구현 (엔진 등록, 실행 관리)
- [ ] 평가 실행 API 구현 (POST, GET)
- [ ] Supabase 결과 저장
- [ ] 에러 핸들링

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] 엔진 등록/조회 동작 확인
- [ ] 평가 실행 흐름 검증
- [ ] 결과 저장 확인

### 권장 (Nice to Have)

- [ ] 엔진 버전 관리
- [ ] 실행 큐 시스템
- [ ] 재시도 로직

---

## 참조

### 기존 프로토타입
- `backend/app/services/valuation_orchestrator.py` (Python FastAPI 버전)
- `Process/P3_프로토타입_제작/Documentation/valuation-engines.md`

### 의존성
- S2BA1: Workflow API (14단계 워크플로우)

---

**작업 복잡도**: High
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
