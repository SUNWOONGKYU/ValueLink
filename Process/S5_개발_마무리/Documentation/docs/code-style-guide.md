# ValueLink 코드 스타일 가이드

**작성일**: 2026-02-23
**버전**: 1.0
**목적**: 일관된 코드 품질과 가독성 향상을 위한 표준화된 스타일 규칙

---

## 1. 파일 헤더 주석

모든 파일은 Task ID와 설명을 포함하는 파일 헤더 주석으로 시작해야 합니다.

### 1.1 TypeScript/JavaScript 파일

✅ **올바른 형식:**
```typescript
/**
 * @task S2BA1
 * @description 프로젝트 생성 API - 14단계 워크플로우 Step 1
 *
 * @endpoint POST /api/projects
 * @auth Required (JWT token)
 * @role customer, admin
 * @method 기본 요율 500만원 + 평가 방법별 가중치 적용
 */

'use client'

import { useState } from 'react'
import type { Project } from '@/types/project'

export default function CreateProject() {
  // ...
}
```

**필수 항목:**
- `@task`: Task ID (예: S2BA1, S2F1)
- `@description`: 파일의 주요 기능 설명
- `@endpoint`: API 엔드포인트 (API 파일만)
- `@auth`: 인증 요구 여부 (API 파일만)
- `@role`: 접근 권한 (API 파일만)

### 1.2 HTML 파일

✅ **올바른 형식:**
```html
<!--
@task S2F1
@description Google 로그인 페이지 - 14단계 워크플로우 Step 3
@screen 로그인 화면
@dependencies S2S1 (Google OAuth)
-->

<!DOCTYPE html>
<html lang="ko">
<head>
  <title>ValueLink - 기업 평가 서비스</title>
</head>
<body>
  <!-- ... -->
</body>
</html>
```

### 1.3 SQL 파일

✅ **올바른 형식:**
```sql
-- @task S1D1
-- @description 기본 데이터베이스 스키마 생성
-- @tables projects, users, documents, drafts, reports

CREATE TABLE projects (
  project_id VARCHAR(50) PRIMARY KEY,
  project_name VARCHAR(255) NOT NULL,
  -- ...
);
```

❌ **잘못된 형식:**
```typescript
// 헤더 주석 없음 - Task ID 추적 불가
import { calculateDCF } from '@/lib/valuation/dcf-engine'

export function Process() { ... }
```

---

## 2. 변수명 규칙

명확하고 일관된 변수명은 코드 가독성의 핵심입니다.

### 2.1 camelCase (변수, 함수, 메서드)

✅ **올바른 형식:**
```typescript
// 변수
const projectId = 'VL-20260223-0001'
const evaluationRequest = await fetchRequest()
const totalEvaluationCost = estimatedCost + additionalFee

// 함수
function calculateDCF(params: DCFParams): ValuationResult { ... }
async function fetchProjectDetails(id: string) { ... }
const discountRate = (wacc: number): number => wacc * 1.2

// 메서드
class ValuationEngine {
  calculateEnterpriseValue() { ... }
  applyMarginOfSafety() { ... }
}
```

❌ **잘못된 형식:**
```typescript
// snake_case 금지 (Python 스타일)
const project_id = 'VL-20260223-0001'
const evaluation_request = await fetch_request()

// PascalCase 금지 (클래스 아님)
const ProjectId = 'VL-20260223-0001'
const EvaluationRequest = ...

// 축약어 남용 금지
const pID = 'VL-20260223-0001' // 축약어
const er = await fetchRequest() // 불명확
```

### 2.2 PascalCase (컴포넌트, 클래스, 인터페이스, 타입)

✅ **올바른 형식:**
```typescript
// React 컴포넌트
function ProjectCard(props: ProjectCardProps) { ... }
const EvaluationForm: React.FC<FormProps> = ({ data }) => { ... }

// 클래스
class DCFValuationEngine {
  constructor(params: DCFParams) { ... }
  calculate(): ValuationResult { ... }
}

// 인터페이스
interface ProjectDetails {
  projectId: string
  companyNameKr: string
  valuationMethod: ValuationMethod
}

// 타입
type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
type DocumentStatus = 'pending' | 'reviewed' | 'approved' | 'rejected'
```

❌ **잘못된 형식:**
```typescript
// camelCase 금지 (변수 아님)
interface projectDetails { ... }
class dcfValuationEngine { ... }
function ProjectCard() { ... } // 함수는 camelCase 사용 (커스텀 훅 제외)

// custom hook은 예외: useProjectData는 camelCase 유지
function useProjectData(id: string) { ... } // 올바름
```

### 2.3 UPPER_SNAKE_CASE (상수)

✅ **올바른 형식:**
```typescript
// 설정 상수
const MAX_RETRIES = 3
const API_TIMEOUT_MS = 5000
const MAX_FILE_SIZE_MB = 50

// 비즈니스 로직 상수
const DEFAULT_WACC = 0.12 // 기본 가중평균자본비용
const PERPETUAL_GROWTH_RATE = 0.03 // 영속 성장률
const TAX_RATE_DEFAULT = 0.22 // 기본 법인세율

// 열거형 상수
const VALUATION_METHODS = {
  DCF: 'dcf',
  RELATIVE: 'relative',
  ASSET: 'asset',
  INTRINSIC: 'intrinsic',
  TAX: 'tax'
} as const

// 에러 메시지 (국제화 고려)
const ERROR_MESSAGES = {
  INVALID_PROJECT_ID: 'Invalid project ID format',
  MISSING_REQUIRED_FIELD: 'Missing required field: {field}',
  CALCULATION_FAILED: 'Valuation calculation failed'
} as const
```

❌ **잘못된 형식:**
```typescript
// camelCase 금지
const maxRetries = 3
const defaultWACC = 0.12

// PascalCase 금지
const MaxRetries = 3
const DefaultWACC = 0.12

// 약어 남용 금지 - 명확한 이름 사용
const DR = 0.12 // 불명확
const SGR = 0.03 // 불명확
```

### 2.4 의미 있는 변수명

의도와 용도가 명확한 변수명을 사용합니다. 축약어나 한 글자 변수명은 최소한으로 제한합니다.

✅ **올바른 형식:**
```typescript
// 명확한 이름 사용
const discountedCashFlows = years.map(
  year => year.freeCashFlow / Math.pow(1 + weightedAverageCapitalCost, year.index)
)

const enterpriseValue = terminalValue + discountedCashFlowSum
const equityValue = enterpriseValue + availableCash - totalDebt

// 루프 변수도 명확하게
const evaluationRequests = await database.requests.findMany({
  where: { status: 'pending' }
})

for (const request of evaluationRequests) {
  const estimate = calculateEstimate(request)
  // ...
}

// boolean 변수는 is/has/can 접두어 사용
const isProjectApproved = project.status === 'approved'
const hasRequiredDocuments = documents.length >= minimumRequired
const canProceedWithEvaluation = hasAllDocuments && isApproved
```

❌ **잘못된 형식:**
```typescript
// 불명확한 약어
const dcf = years.map(y => y.fcf / Math.pow(1 + w, y.y))
const ev = tv + ds // ev, tv, ds 불명확
const val = ev + c - d // val, c, d 의미 불명

// 한 글자 변수 (루프 제외)
const r = 0.12 // rate?
const s = status === 'active' // status?
const t = getCurrentTime() // time?

// boolean 변수가 명확하지 않음
const project = project.approved // true/false 불명확
const document = 'reviewed' // 상태 불명확
const evaluation = '2026-02-23' // 날짜인지 상태인지 불명확
```

---

## 3. 함수 주석

함수 주석은 **복잡한 로직**에만 추가합니다. 자명한 코드는 주석하지 않습니다.

### 3.1 복잡한 로직에만 주석 추가

✅ **올바른 형식:**
```typescript
/**
 * DCF(Discounted Cash Flow) 평가 엔진
 *
 * 현재 매출, 성장률, WACC를 기반으로 기업 가치를 계산합니다.
 * Terminal Value는 Gordon Growth Model을 사용합니다.
 *
 * @param revenue - 현재 연간 매출 (원)
 * @param growthRate - 연평균 성장률 (0.1 = 10%)
 * @param wacc - 가중평균자본비용 (0.12 = 12%)
 * @param margin - EBITDA 마진율 (0.3 = 30%)
 * @returns { enterpriseValue, equityValue } 평가 결과
 *
 * @throws {ValidationError} - 입력값이 유효하지 않을 때
 * @example
 * const result = calculateDCF(5000000000, 0.3, 0.15, 0.25)
 * console.log(result.enterpriseValue) // 91400000000
 */
async function calculateDCF(
  revenue: number,
  growthRate: number,
  wacc: number,
  margin: number
): Promise<ValuationResult> {
  // 1. FCF 예측: 5년 이상 현금흐름 예측
  // Gordon Growth Model에서 정상 상태 가정
  const fcfProjections = projectFreeCashFlow(revenue, growthRate, margin, 5)

  // 2. Terminal Value 계산
  // TV = FCF_Year5 × (1 + g) / (WACC - g)
  // 영속 성장률은 장기 GDP 성장률과 유사하게 설정
  const year5FCF = fcfProjections[4]
  const perpetualGrowth = 0.03 // 3% (장기 평균)
  const terminalValue = (year5FCF * (1 + perpetualGrowth)) /
                        (wacc - perpetualGrowth)

  // 3. DCF 합계: 각 연도 FCF를 현재가치로 할인
  // PV = FCF / (1 + WACC)^n
  let dcfSum = 0
  for (let year = 0; year < 5; year++) {
    const presentValue = fcfProjections[year] / Math.pow(1 + wacc, year + 1)
    dcfSum += presentValue
  }

  // 4. Terminal Value 할인
  const pvTerminalValue = terminalValue / Math.pow(1 + wacc, 5)

  // 5. 기업 가치 계산
  const enterpriseValue = dcfSum + pvTerminalValue

  // 6. 주주 가치 = 기업 가치 + 현금 - 부채
  const equityValue = enterpriseValue + cash - debt

  return {
    enterpriseValue,
    equityValue,
    dcfSum,
    terminalValue: pvTerminalValue,
    methodology: 'DCF'
  }
}
```

✅ **자명한 코드는 주석하지 않음:**
```typescript
// 불필요한 주석 제거

// ❌ 주석 불필요 - 코드 자체가 명확
const projectId = req.params.id // 프로젝트 ID를 가져옴
console.log(user.name) // 사용자 이름을 출력
const total = items.reduce((sum, item) => sum + item.price, 0) // 합계 계산

// ✅ 불필요한 주석 제거한 형태
const projectId = req.params.id
console.log(user.name)
const total = items.reduce((sum, item) => sum + item.price, 0)
```

### 3.2 JSDoc 형식 (API, 공개 함수)

✅ **올바른 형식:**
```typescript
/**
 * 프로젝트 생성 API 엔드포인트
 *
 * 새로운 평가 프로젝트를 생성합니다. 클라이언트의 기본 정보를 저장하고,
 * 자동으로 단계 1(평가 의뢰)로 초기화됩니다.
 *
 * @param req - Next.js Request 객체
 *   Body:
 *   - project_name: string - 프로젝트명 (필수)
 *   - company_name_kr: string - 회사명(한글) (필수)
 *   - valuation_method: 'dcf'|'relative'|'asset'|'intrinsic'|'tax' (필수)
 *   - industry: string - 산업 분류 (필수)
 *
 * @returns Response 객체
 *   - status: 201 Created
 *   - body: {
 *       project_id: 'VL-20260223-0001',
 *       created_at: '2026-02-23T12:34:56Z',
 *       step: 1,
 *       status: 'pending'
 *     }
 *
 * @throws {ValidationError} - 필수 필드 누락 시 (400)
 * @throws {AuthenticationError} - JWT 토큰 없음 시 (401)
 * @throws {DatabaseError} - DB 저장 실패 시 (500)
 *
 * @example
 * // Request
 * POST /api/projects
 * Content-Type: application/json
 * Authorization: Bearer {jwt_token}
 *
 * {
 *   "project_name": "ABC 기업 DCF 평가",
 *   "company_name_kr": "ABC 주식회사",
 *   "valuation_method": "dcf",
 *   "industry": "제조업 - 반도체"
 * }
 *
 * // Response (201)
 * {
 *   "project_id": "VL-20260223-0001",
 *   "created_at": "2026-02-23T12:34:56Z",
 *   "step": 1,
 *   "status": "pending"
 * }
 */
export async function POST(req: Request): Promise<Response> {
  try {
    const body = await req.json()

    // 입력값 검증
    const { project_name, company_name_kr, valuation_method, industry } = body

    if (!project_name || !company_name_kr || !valuation_method || !industry) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // DB에 저장
    const projectId = generateProjectId()
    await database.projects.create({
      project_id: projectId,
      project_name,
      company_name_kr,
      valuation_method,
      industry,
      step: 1,
      status: 'pending',
      created_at: new Date()
    })

    return new Response(
      JSON.stringify({
        project_id: projectId,
        created_at: new Date().toISOString(),
        step: 1,
        status: 'pending'
      }),
      { status: 201, headers: { 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    return handleAPIError(error)
  }
}
```

### 3.3 주석 작성 체크리스트

- [ ] 복잡한 알고리즘 또는 비즈니스 로직만 주석
- [ ] 자명한 코드는 주석하지 않음
- [ ] 공개 함수/API는 JSDoc 형식 사용
- [ ] @param, @returns, @throws, @example 포함
- [ ] 주석은 코드와 일치 (코드 변경 시 주석도 수정)

---

## 4. 파일 구조 규칙

일관된 파일 구조는 코드 이해와 유지보수를 용이하게 합니다.

### 4.1 Import 순서

모듈 import는 다음 순서로 정렬합니다:

✅ **올바른 순서:**
```typescript
// 1. React/Next.js 코어
import { useState, useEffect, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { headers } from 'next/headers'

// 2. 외부 라이브러리
import { createClient } from '@supabase/supabase-js'
import axios from 'axios'
import { format } from 'date-fns'

// 3. 내부 라이브러리 (@/ alias)
import { calculateDCF } from '@/lib/valuation/dcf-engine'
import { validateProjectData } from '@/lib/validation/project-validator'
import { Toast } from '@/app/components/ui/toast'
import { ProjectCard } from '@/app/components/project/project-card'

// 4. 타입 정의
import type { Project, DCFParams, ValuationResult } from '@/types/valuation'
import type { ApiResponse } from '@/types/api'

// 5. 스타일 (마지막)
import './styles.css'
```

❌ **잘못된 순서:**
```typescript
// 섞여 있는 import
import './styles.css' // 스타일이 위에 있음
import { useState } from 'react' // React 다음에 와야 함
import { calculateDCF } from '@/lib/valuation/dcf-engine'
import axios from 'axios' // 외부 라이브러리 순서 뒤바뀜
import type { Project } from '@/types/valuation' // 타입이 먼저
import { Toast } from '@/app/components/ui/toast'
```

### 4.2 파일 내 구성 순서

✅ **올바른 순서:**
```typescript
/**
 * @task S2BA1
 * @description 프로젝트 생성 API
 */

// Directive
'use client'

// Import
import { useState } from 'react'
import type { Project } from '@/types/project'

// 상수 정의
const MAX_PROJECT_NAME_LENGTH = 100
const REQUIRED_FIELDS = ['project_name', 'company_name_kr'] as const

// 타입 정의
interface FormData {
  project_name: string
  company_name_kr: string
  valuation_method: string
}

interface ApiRequest {
  data: FormData
  timestamp: Date
}

// Enum (상수와 유사)
enum ValuationMethod {
  DCF = 'dcf',
  RELATIVE = 'relative',
  ASSET = 'asset'
}

// Helper 함수들
function validateFormData(data: FormData): { valid: boolean; error?: string } {
  if (!data.project_name) return { valid: false, error: 'Project name required' }
  if (data.project_name.length > MAX_PROJECT_NAME_LENGTH) {
    return { valid: false, error: 'Project name too long' }
  }
  return { valid: true }
}

async function submitProject(data: FormData): Promise<ApiRequest> {
  return {
    data,
    timestamp: new Date()
  }
}

// Main 컴포넌트/함수
export default function CreateProjectPage() {
  const [formData, setFormData] = useState<FormData>({
    project_name: '',
    company_name_kr: '',
    valuation_method: 'dcf'
  })

  const handleSubmit = async () => {
    const validation = validateFormData(formData)
    if (!validation.valid) {
      console.error(validation.error)
      return
    }

    await submitProject(formData)
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Form JSX */}
    </form>
  )
}

// Export (마지막)
export { validateFormData }
```

❌ **잘못된 순서:**
```typescript
// 컴포넌트가 먼저 옴
export default function CreateProjectPage() { ... }

// Helper 함수가 나중에 정의됨
function validateFormData(data: FormData) { ... }

// Import가 마지막에 옴 (위에 와야 함)
import { useState } from 'react'
```

---

## 5. TypeScript 타입 규칙

타입 안정성은 런타임 에러를 줄이고 코드 품질을 향상시킵니다.

### 5.1 any 타입 금지

✅ **올바른 형식:**
```typescript
// 명시적 타입 정의
function processValuationData(data: ValuationData): ValuationResult {
  return { ...data, calculated: true }
}

// 타입 불명확할 때는 unknown 사용
function handleResponse(data: unknown): void {
  if (typeof data === 'object' && data !== null) {
    // 타입 좁히기
    const result = data as ValuationResult
    console.log(result.enterpriseValue)
  }
}

// 제네릭 사용
function fetchData<T>(url: string): Promise<T> {
  return fetch(url).then(res => res.json() as Promise<T>)
}

// 유니온 타입으로 대안 제시
function calculateValue(
  method: 'dcf' | 'relative' | 'asset'
): number {
  switch (method) {
    case 'dcf':
      return calculateDCF()
    case 'relative':
      return calculateRelative()
    default:
      return 0
  }
}
```

❌ **잘못된 형식:**
```typescript
// any 타입 금지
function processData(data: any) { // 타입 정보 손실
  return data.value
}

// 함수 반환 타입 없음
function calculate(a, b) { // 반환 타입 불명확
  return a + b
}

// 과도한 any 사용
const config: any = loadConfig() // 런타임 에러 가능성
```

### 5.2 명시적 타입 선언

✅ **올바른 형식:**
```typescript
// 명시적 변수 타입
const revenue: number = 1_000_000_000 // 10억 (언더스코어로 가독성 향상)
const growthRate: number = 0.3 // 30%
const projects: Project[] = await fetchProjects()

// 함수 매개변수와 반환 타입
async function fetchProjectWithDetails(id: string): Promise<ProjectDetail> {
  const response = await fetch(`/api/projects/${id}`)
  return response.json()
}

// 객체 타입 명시
const config: ProjectConfig = {
  projectName: 'ABC 평가',
  valuationMethod: 'dcf',
  industry: 'IT'
}

// 배열 타입 명시
const estimates: Estimate[] = []
const scores: number[] = [85, 90, 78]

// 제네릭으로 재사용 가능한 타입
class Repository<T> {
  async getById(id: string): Promise<T> {
    // ...
  }
}
```

❌ **잘못된 형식:**
```typescript
// 타입 추론만 의존 (불명확)
const revenue = 1000000000 // number로 추론되지만 명시 권장
const projects = await fetchProjects() // 반환 타입 불명확
const estimate = calculateEstimate() // 반환값 불명확

// 함수 타입 누락
function validateData(data) { // 매개변수 타입 없음
  return data.isValid // 불명확
}

// 반환 타입 없음
async function fetchProjects() { // Promise<Project[]>가 무엇인지 불명확
  return fetch('/api/projects').then(r => r.json())
}
```

---

## 6. 에러 처리 규칙

적절한 에러 처리는 애플리케이션의 안정성을 보장합니다.

### 6.1 Try-Catch 필수 (Async 함수)

✅ **올바른 형식:**
```typescript
/**
 * 프로젝트 정보 조회 API
 * 데이터베이스 및 네트워크 에러를 처리합니다.
 */
async function fetchProject(id: string): Promise<Project | null> {
  try {
    // Supabase 조회
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('project_id', id)
      .single()

    // Supabase 에러 처리
    if (error) {
      if (error.code === 'PGRST116') { // 레코드 없음
        return null
      }
      throw new Error(`Database error: ${error.message}`)
    }

    return data as Project
  } catch (error) {
    // 에러 처리 및 로깅
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    console.error(`Failed to fetch project ${id}:`, errorMessage)

    // 재시도 로직 (선택)
    if (isNetworkError(error)) {
      return retryFetch(id)
    }

    throw error
  }
}

/**
 * 결과값 검증과 함께하는 에러 처리
 */
async function calculateAndValidate(
  revenue: number,
  growthRate: number
): Promise<{ success: boolean; result?: ValuationResult; error?: string }> {
  try {
    // 입력값 검증
    if (revenue <= 0) {
      return { success: false, error: 'Revenue must be positive' }
    }
    if (growthRate < 0 || growthRate > 1) {
      return { success: false, error: 'Growth rate must be between 0 and 1' }
    }

    // 계산 실행
    const result = await calculateDCF(revenue, growthRate)

    // 결과 검증
    if (result.enterpriseValue < 0) {
      return { success: false, error: 'Invalid calculation result' }
    }

    return { success: true, result }
  } catch (error) {
    return { success: false, error: 'Calculation failed' }
  }
}
```

### 6.2 HTTP API 에러 처리

✅ **올바른 형식:**
```typescript
/**
 * API 에러 핸들러
 * HTTP 상태 코드별로 적절한 응답을 반환합니다.
 */
export async function POST(req: Request): Promise<Response> {
  try {
    // 요청 파싱
    let body: CreateProjectRequest
    try {
      body = await req.json()
    } catch (error) {
      return apiErrorResponse(
        'Invalid JSON format',
        400,
        'INVALID_JSON'
      )
    }

    // 입력값 검증
    const validation = validateProjectInput(body)
    if (!validation.valid) {
      return apiErrorResponse(
        validation.errors.join(', '),
        400,
        'VALIDATION_FAILED'
      )
    }

    // 비즈니스 로직
    const project = await createProject(body)

    // 성공 응답
    return apiSuccessResponse(project, 201)
  } catch (error) {
    if (error instanceof DatabaseError) {
      return apiErrorResponse(
        'Database operation failed',
        500,
        'DATABASE_ERROR'
      )
    }

    if (error instanceof ValidationError) {
      return apiErrorResponse(
        error.message,
        400,
        'VALIDATION_ERROR'
      )
    }

    // 예상 밖의 에러
    console.error('Unexpected error:', error)
    return apiErrorResponse(
      'Internal server error',
      500,
      'INTERNAL_ERROR'
    )
  }
}

// 헬퍼 함수
function apiErrorResponse(
  message: string,
  status: number,
  code: string
): Response {
  return new Response(
    JSON.stringify({
      success: false,
      error: { message, code }
    }),
    { status, headers: { 'Content-Type': 'application/json' } }
  )
}

function apiSuccessResponse(data: unknown, status: number = 200): Response {
  return new Response(
    JSON.stringify({ success: true, data }),
    { status, headers: { 'Content-Type': 'application/json' } }
  )
}
```

### 6.3 에러 타입 정의

✅ **올바른 형식:**
```typescript
// 커스텀 에러 클래스
class ValueLinkError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500
  ) {
    super(message)
    this.name = 'ValueLinkError'
  }
}

class ValidationError extends ValueLinkError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 400)
    this.name = 'ValidationError'
  }
}

class DatabaseError extends ValueLinkError {
  constructor(message: string) {
    super(message, 'DATABASE_ERROR', 500)
    this.name = 'DatabaseError'
  }
}

class AuthenticationError extends ValueLinkError {
  constructor(message: string = 'Authentication required') {
    super(message, 'AUTH_REQUIRED', 401)
    this.name = 'AuthenticationError'
  }
}

// 사용 예시
try {
  if (!token) {
    throw new AuthenticationError()
  }

  if (!isValidData(data)) {
    throw new ValidationError('Invalid project data')
  }

  await saveToDatabase(data)
} catch (error) {
  if (error instanceof ValidationError) {
    // 400 에러 처리
  } else if (error instanceof DatabaseError) {
    // 500 에러 처리
  }
}
```

---

## 7. 종합 체크리스트

코드 작성 시 다음 항목을 확인하세요:

### 파일 헤더
- [ ] Task ID 명시 (@task)
- [ ] 파일 설명 포함 (@description)
- [ ] API인 경우 엔드포인트 명시 (@endpoint)
- [ ] 인증 요구 사항 명시 (@auth)

### 변수명 규칙
- [ ] camelCase (변수, 함수)
- [ ] PascalCase (컴포넌트, 클래스, 타입)
- [ ] UPPER_SNAKE_CASE (상수)
- [ ] 의미 있는 이름 (약어 최소화)
- [ ] Boolean 변수는 is/has/can 접두어 사용

### 함수 주석
- [ ] 복잡한 로직만 주석 추가
- [ ] 자명한 코드는 주석 생략
- [ ] 공개 함수는 JSDoc 형식
- [ ] @param, @returns, @throws, @example 포함
- [ ] 주석은 코드와 일치

### 파일 구조
- [ ] Import 순서 준수 (React → 외부 → 내부 → 타입 → 스타일)
- [ ] 파일 내 구성 순서 준수 (헤더 → directive → import → 상수 → 타입 → 함수 → 컴포넌트)
- [ ] Export는 마지막에 배치

### TypeScript 타입
- [ ] any 타입 금지
- [ ] 명시적 타입 선언
- [ ] 제네릭 활용
- [ ] 유니온 타입 사용

### 에러 처리
- [ ] Async 함수에 try-catch 적용
- [ ] Supabase 에러 처리
- [ ] 입력값 검증
- [ ] 에러 로깅
- [ ] 예상 밖의 에러 처리

---

**다음 문서 참고:**
- `user-guide-enhanced.md` - 사용자 가이드
- `sample-datasets.md` - 샘플 데이터 세트

**문의 및 피드백:**
- 코드 스타일 질문 → GitHub Issues
- 기여하려면 이 가이드를 따르세요
