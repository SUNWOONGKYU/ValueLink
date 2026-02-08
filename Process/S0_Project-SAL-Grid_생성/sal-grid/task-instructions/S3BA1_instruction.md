# S3BA1: Valuation Engine Orchestrator (신규 구현)

## Task 정보

- **Task ID**: S3BA1
- **Task Name**: 평가 엔진 오케스트레이터 구현
- **Stage**: S3 (AI Integration - 개발 2차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S2BA2 (Projects API), S1D1 (Database 스키마)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**5개 평가 방법을 관리하는 오케스트레이터 패턴 구현**

- Abstract class로 평가 엔진 인터페이스 정의
- 평가 방법별 엔진 클래스 구현 (DCF, Relative, Asset, Intrinsic, Tax)
- 싱글톤 패턴으로 오케스트레이터 구현
- **4가지 측면에서 구현** (정확성, 성능, 코드 품질, 확장성)

---

## 🎯 구현 필수 영역 (4가지)

### 1️⃣ 계산 정확성 (Accuracy)
- ✅ 재무 이론 정확히 구현
- ✅ 부동소수점 오차 최소화
- ✅ 입력 값 검증 (음수, 0, NaN 처리)
- ✅ 예외 상황 명확한 에러 메시지

### 2️⃣ 성능 최적화 (Performance)
- ✅ 싱글톤 패턴 (엔진 재사용)
- ✅ 메모이제이션 (반복 계산 캐싱)
- ✅ 비동기 처리 (Promise 기반)
- ✅ 타임아웃 설정 (무한 루프 방지)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ Abstract class로 엔진 인터페이스 통일
- ✅ JSDoc 주석 (파라미터/반환값 설명)
- ✅ 에러 핸들링 강화

### 4️⃣ 확장성 (Extensibility)
- ✅ 새 평가 방법 추가 용이
- ✅ 엔진별 독립적 테스트 가능
- ✅ 설정 파일로 엔진 파라미터 관리
- ✅ 플러그인 패턴 지원

---

## 작업 방식

### Step 1: 재무 이론 검증

**참고 자료:**
```
재무 이론:
- DCF: 현금흐름할인법 (Discounted Cash Flow)
- Relative: 상대가치평가 (Multiples)
- Asset: 자산가치평가 (Net Asset Value)
- Intrinsic: 내재가치평가 (ROE-based)
- Tax: 세법상평가 (보충적 평가 방법)
```

**검증 항목:**
1. 각 평가 방법의 수식 정확성
2. 입력 데이터 범위 (유효값)
3. 엣지 케이스 (0, 음수, 무한대)
4. 계산 순서 (의존성)

### Step 2: Abstract Class 설계

**인터페이스 정의:**

| 메서드 | 설명 | 반환값 |
|--------|------|--------|
| `calculate()` | 평가 수행 | `Promise<ValuationResult>` |
| `validate()` | 입력 검증 | `ValidationResult` |
| `getName()` | 엔진 이름 | `string` |

**주의사항:**
- 모든 엔진이 동일한 인터페이스 구현
- 입력/출력 타입 통일
- 에러 처리 일관성

### Step 3: 구현 사항 적용

**목표:**

```typescript
// ❌ 단순 구현: 입력 검증 없음
async function valuateDCF(data: any) {
  const npv = calculateNPV(data.cashFlows, data.wacc)
  return { value: npv }
}

// ✅ 개선: Abstract class + 검증
abstract class ValuationEngine {
  abstract getName(): string
  abstract calculate(data: ValuationInput): Promise<ValuationResult>

  validate(data: ValuationInput): ValidationResult {
    if (!data || typeof data !== 'object') {
      return { valid: false, error: '입력 데이터가 유효하지 않습니다.' }
    }
    return { valid: true }
  }
}

class DCFEngine extends ValuationEngine {
  getName(): string {
    return 'DCF'
  }

  validate(data: ValuationInput): ValidationResult {
    const baseValidation = super.validate(data)
    if (!baseValidation.valid) return baseValidation

    if (!data.cashFlows || data.cashFlows.length === 0) {
      return { valid: false, error: '현금흐름 데이터가 필요합니다.' }
    }

    if (!data.wacc || data.wacc <= 0 || data.wacc >= 1) {
      return { valid: false, error: 'WACC는 0과 1 사이여야 합니다.' }
    }

    return { valid: true }
  }

  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const validation = this.validate(data)
    if (!validation.valid) {
      throw new Error(validation.error)
    }

    try {
      const npv = await calculateNPV(data.cashFlows, data.wacc)
      const terminalValue = await calculateTerminalValue(data)
      const enterpriseValue = npv + terminalValue

      return {
        method: 'DCF',
        enterpriseValue,
        equityValue: enterpriseValue - data.netDebt,
        sharePrice: (enterpriseValue - data.netDebt) / data.sharesOutstanding,
        details: { npv, terminalValue }
      }
    } catch (error) {
      throw new Error(`DCF 계산 실패: ${error.message}`)
    }
  }
}
```

```typescript
// ❌ 단순 구현: 하드코딩된 엔진 선택
function getEngine(method: string) {
  if (method === 'DCF') return new DCFEngine()
  if (method === 'Relative') return new RelativeEngine()
  // ...
}

// ✅ 개선: 싱글톤 오케스트레이터
class ValuationOrchestrator {
  private static instance: ValuationOrchestrator
  private engines: Map<string, ValuationEngine>

  private constructor() {
    this.engines = new Map()
    this.engines.set('DCF', new DCFEngine())
    this.engines.set('Relative', new RelativeEngine())
    this.engines.set('Asset', new AssetEngine())
    this.engines.set('Intrinsic', new IntrinsicEngine())
    this.engines.set('Tax', new TaxEngine())
  }

  static getInstance(): ValuationOrchestrator {
    if (!ValuationOrchestrator.instance) {
      ValuationOrchestrator.instance = new ValuationOrchestrator()
    }
    return ValuationOrchestrator.instance
  }

  async valuate(
    method: string,
    data: ValuationInput
  ): Promise<ValuationResult> {
    const engine = this.engines.get(method)

    if (!engine) {
      throw new Error(`지원하지 않는 평가 방법: ${method}`)
    }

    console.log(`[Orchestrator] ${engine.getName()} 엔진 실행 중...`)

    const startTime = Date.now()
    const result = await engine.calculate(data)
    const duration = Date.now() - startTime

    console.log(`[Orchestrator] ${engine.getName()} 완료 (${duration}ms)`)

    return {
      ...result,
      duration
    }
  }

  getSupportedMethods(): string[] {
    return Array.from(this.engines.keys())
  }
}
```

```typescript
// ❌ 단순 구현: 부동소수점 오차 무시
const npv = cashFlows.reduce((sum, cf, i) => {
  return sum + cf / Math.pow(1 + wacc, i + 1)
}, 0)

// ✅ 개선: 소수점 반올림 + 오차 최소화
function calculateNPV(
  cashFlows: number[],
  wacc: number
): number {
  let npv = 0

  for (let i = 0; i < cashFlows.length; i++) {
    const discountFactor = Math.pow(1 + wacc, i + 1)
    const presentValue = cashFlows[i] / discountFactor

    // 소수점 2자리 반올림 (원 단위)
    npv += Math.round(presentValue * 100) / 100
  }

  return Math.round(npv * 100) / 100
}
```

### Step 4: Best Practice 적용

**TypeScript 타입 정의:**
```typescript
// ✅ 입력 타입
export interface ValuationInput {
  method: 'DCF' | 'Relative' | 'Asset' | 'Intrinsic' | 'Tax'
  projectId: string

  // DCF 관련
  cashFlows?: number[]
  wacc?: number
  terminalGrowthRate?: number
  netDebt?: number
  sharesOutstanding?: number

  // Relative 관련
  revenue?: number
  ebitda?: number
  comparableCompanies?: ComparableCompany[]

  // Asset 관련
  assets?: number
  liabilities?: number

  // Intrinsic 관련
  roe?: number
  bookValue?: number

  // Tax 관련
  nav?: number
  earnings?: number
}

// ✅ 출력 타입
export interface ValuationResult {
  method: string
  enterpriseValue: number
  equityValue: number
  sharePrice: number
  details?: Record<string, any>
  duration?: number
  timestamp: string
}

// ✅ 검증 결과
export interface ValidationResult {
  valid: boolean
  error?: string
}
```

**싱글톤 패턴:**
- 오케스트레이터는 앱당 1개 인스턴스만 존재
- 엔진 객체 재사용으로 메모리 절약
- 설정 변경 시 전역 적용

**에러 핸들링:**
```typescript
// ✅ 명확한 에러 메시지
class ValuationError extends Error {
  constructor(
    public method: string,
    public code: string,
    message: string
  ) {
    super(`[${method}] ${message}`)
    this.name = 'ValuationError'
  }
}

throw new ValuationError('DCF', 'INVALID_WACC', 'WACC는 0과 1 사이여야 합니다.')
```

---

## 전제조건 확인

**S2BA2 완료 확인:**
- Projects API 구현됨 (프로젝트 데이터 조회)

**S1D1 완료 확인:**
- valuation_results 테이블 존재

---

## 생성 파일 (4개)

### 1. api/Backend_APIs/valuation/valuation-engine.ts
**목표:** Abstract class 정의

**개선 사항:**
- ✅ 모든 엔진의 공통 인터페이스
- ✅ 입력 검증 메서드
- ✅ 에러 처리 메서드
- ✅ JSDoc 주석

### 2. api/Backend_APIs/valuation/valuation-orchestrator.ts
**목표:** 싱글톤 오케스트레이터

**개선 사항:**
- ✅ 엔진 등록 및 관리
- ✅ 평가 실행 및 로깅
- ✅ 지원 방법 목록 조회
- ✅ 성능 측정 (duration)

### 3. api/Backend_APIs/valuation/engines/index.ts
**목표:** 엔진 export (스켈레톤만)

**개선 사항:**
- ✅ 5개 엔진 클래스 placeholder
- ✅ 각 엔진의 `getName()` 구현
- ✅ `calculate()` 메서드 TODO 주석

### 4. api/Backend_APIs/valuation/types.ts
**목표:** 타입 정의

**개선 사항:**
- ✅ ValuationInput 인터페이스
- ✅ ValuationResult 인터페이스
- ✅ ValidationResult 인터페이스
- ✅ ValuationError 클래스

---

## 완료 기준

### 필수 (Must Have)
- [ ] ValuationEngine abstract class 구현
- [ ] ValuationOrchestrator 싱글톤 구현
- [ ] 5개 엔진 클래스 스켈레톤
- [ ] 타입 정의 완료
- [ ] 입력 검증 로직

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 오케스트레이터 싱글톤 테스트
- [ ] 엔진 등록/조회 테스트
- [ ] 잘못된 입력 시 에러 처리

### 구현 항목 (Implementation)
- [ ] 정확성: 입력 검증, 에러 메시지
- [ ] 성능: 싱글톤, 메모이제이션 준비
- [ ] 코드 품질: TypeScript strict, JSDoc
- [ ] 확장성: Abstract class, 플러그인 패턴

---

## 참조

### 재무 이론
- **DCF**: 현금흐름할인법 (NPV + Terminal Value)
- **Relative**: 상대가치평가 (P/E, P/S, EV/EBITDA)
- **Asset**: 자산가치평가 (자산 - 부채)
- **Intrinsic**: 내재가치평가 (ROE × Book Value)
- **Tax**: 세법상평가 (순자산가치 + 수익가치)

### 디자인 패턴
- **Abstract class**: 엔진 인터페이스 통일
- **Singleton**: 오케스트레이터 1개 인스턴스
- **Strategy**: 평가 방법별 알고리즘 교체

### 관련 Task
- **S3BA2**: Financial Math Library (수학 함수)
- **S3BA3**: DCF Engine (DCF 구현)
- **S3BA4**: Other Engines (나머지 4개 엔진)

---

## 주의사항

### 🔢 계산 정확성

1. **부동소수점 오차**
   - 소수점 2자리 반올림 (원 단위)
   - 큰 숫자 먼저 더하기 (오차 누적 방지)

2. **입력 검증**
   - 음수, 0, NaN, Infinity 체크
   - 필수 필드 누락 체크

### ⚡ 성능

1. **싱글톤 패턴**
   - 오케스트레이터는 앱당 1개
   - 엔진 객체 재사용

2. **비동기 처리**
   - 모든 calculate() 메서드는 Promise 반환
   - 타임아웃 설정 (무한 루프 방지)

### 📝 코드 품질

1. **Abstract class**
   - 모든 엔진이 동일한 인터페이스
   - 공통 로직은 부모 클래스에

2. **에러 처리**
   - ValuationError 클래스 사용
   - 명확한 에러 메시지

---

## 예상 소요 시간

**작업 복잡도**: Medium-High
**파일 수**: 4개
**라인 수**: ~400줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 신규 구현 방식으로 변경
