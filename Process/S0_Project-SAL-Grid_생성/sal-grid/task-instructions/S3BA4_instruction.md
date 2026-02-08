# S3BA4: Other Valuation Engines (신규 구현)

## Task 정보

- **Task ID**: S3BA4
- **Task Name**: 4개 평가 엔진 구현 (Relative, Asset, Intrinsic, Tax)
- **Stage**: S3 (AI Integration - 개발 2차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S3BA1 (Orchestrator), S3BA2 (Financial Math), S3BA3 (DCF Engine)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**DCF 외 4개 평가 방법 엔진 구현**

- **Relative**: 상대가치평가 (Multiples 기반)
- **Asset**: 자산가치평가 (Net Asset Value)
- **Intrinsic**: 내재가치평가 (ROE 기반)
- **Tax**: 세법상평가 (보충적 평가 방법)
- **4가지 측면에서 구현** (정확성, 성능, 코드 품질, 확장성)

---

## 🎯 구현 필수 영역 (4가지)

### 1️⃣ 계산 정확성 (Accuracy)
- ✅ 각 평가 방법의 수식 정확히 구현
- ✅ Multiples (P/S, EV/EBITDA) 정확한 계산
- ✅ 유사기업 평균/중앙값 계산
- ✅ 입력 데이터 검증 (필수 필드, 범위)

### 2️⃣ 성능 최적화 (Performance)
- ✅ Relative 엔진: 유사기업 병렬 조회
- ✅ 불필요한 배열 복사 방지
- ✅ Multiples 계산 최적화
- ✅ 타임아웃 설정 (무한 루프 방지)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ ValuationEngine 인터페이스 준수
- ✅ JSDoc 주석 (수식, 파라미터 설명)
- ✅ 에러 핸들링 강화

### 4️⃣ 확장성 (Extensibility)
- ✅ 새 평가 방법 추가 용이
- ✅ 엔진별 독립적 테스트 가능
- ✅ 설정 파일로 엔진 파라미터 관리
- ✅ 중간 계산 결과 반환

---

## 작업 방식

### Step 1: 평가 이론 검증

**4가지 평가 방법 수식:**

```
1. Relative (상대가치평가)
   - P/S Multiple: 시가총액 / 매출액
   - EV/EBITDA Multiple: 기업가치 / EBITDA

   단계:
   1) 유사기업들의 P/S 평균 계산
   2) 대상기업 매출액 × P/S 평균 = 시가총액
   3) 시가총액 / 발행주식수 = 주당가치

   또는:
   1) 유사기업들의 EV/EBITDA 평균 계산
   2) 대상기업 EBITDA × EV/EBITDA 평균 = 기업가치
   3) 기업가치 - 순차입금 = 주주가치

2. Asset (자산가치평가)
   Equity Value = 자산 - 부채
   Share Price = Equity Value / 발행주식수

   보정:
   - 재고자산 감가: -10%
   - 무형자산 감가: -20%
   - 유형자산: 공정가치 반영

3. Intrinsic (내재가치평가)
   Equity Value = ROE × Book Value
   Share Price = Equity Value / 발행주식수

   ROE = 당기순이익 / 자기자본

4. Tax (세법상평가) - 보충적 평가방법
   순자산가치 = 자산 - 부채
   수익가치 = 당기순이익 / 할인율

   가중평균:
   - 순자산가치 60% + 수익가치 40% (일반)
   - 순자산가치 80% + 수익가치 20% (자산 중심)
```

### Step 2: ValuationEngine 상속

**공통 구조:**

```typescript
class RelativeEngine extends ValuationEngine {
  getName(): string { return 'Relative' }
  validate(data: ValuationInput): ValidationResult { ... }
  async calculate(data: ValuationInput): Promise<ValuationResult> { ... }
}

class AssetEngine extends ValuationEngine {
  getName(): string { return 'Asset' }
  validate(data: ValuationInput): ValidationResult { ... }
  async calculate(data: ValuationInput): Promise<ValuationResult> { ... }
}

class IntrinsicEngine extends ValuationEngine {
  getName(): string { return 'Intrinsic' }
  validate(data: ValuationInput): ValidationResult { ... }
  async calculate(data: ValuationInput): Promise<ValuationResult> { ... }
}

class TaxEngine extends ValuationEngine {
  getName(): string { return 'Tax' }
  validate(data: ValuationInput): ValidationResult { ... }
  async calculate(data: ValuationInput): Promise<ValuationResult> { ... }
}
```

### Step 3: 구현 사항 적용

**예시 1: Relative Engine**

```typescript
// ❌ 단순 구현: 검증 없음, 중앙값 미사용
class RelativeEngine extends ValuationEngine {
  async calculate(data: any) {
    const avgPS = data.comparables.reduce((sum, c) => sum + c.ps, 0) / data.comparables.length
    return { value: data.revenue * avgPS }
  }
}

// ✅ 개선: 검증 + 중앙값 + 복수 Multiples
class RelativeEngine extends ValuationEngine {
  getName(): string {
    return 'Relative'
  }

  validate(data: ValuationInput): ValidationResult {
    const baseValidation = super.validate(data)
    if (!baseValidation.valid) return baseValidation

    // Relative 필수 필드 검증
    if (!data.revenue || data.revenue <= 0) {
      return {
        valid: false,
        error: '매출액이 필요합니다.'
      }
    }

    if (!data.comparableCompanies || data.comparableCompanies.length < 3) {
      return {
        valid: false,
        error: '유사기업은 최소 3개 이상이어야 합니다.'
      }
    }

    return { valid: true }
  }

  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const validation = this.validate(data)
    if (!validation.valid) {
      throw new Error(validation.error)
    }

    try {
      const comparables = data.comparableCompanies!

      // 1. P/S Multiple 계산
      const psMultiples = comparables.map((c) => c.marketCap / c.revenue)
      const medianPS = median(psMultiples)
      const avgPS = average(psMultiples)

      // 중앙값 사용 (이상치 제거)
      const marketCapByPS = data.revenue! * medianPS
      const sharePriceByPS = marketCapByPS / (data.sharesOutstanding || 1)

      // 2. EV/EBITDA Multiple 계산 (선택)
      let marketCapByEVEBITDA = 0
      let sharePriceByEVEBITDA = 0

      if (data.ebitda && data.ebitda > 0) {
        const evEbitdaMultiples = comparables.map(
          (c) => c.enterpriseValue / c.ebitda
        )
        const medianEVEBITDA = median(evEbitdaMultiples)

        const enterpriseValue = data.ebitda * medianEVEBITDA
        const equityValue = enterpriseValue - (data.netDebt || 0)
        marketCapByEVEBITDA = equityValue
        sharePriceByEVEBITDA = equityValue / (data.sharesOutstanding || 1)
      }

      // 3. 두 방법의 평균 (EBITDA가 있으면)
      let finalMarketCap = marketCapByPS
      let finalSharePrice = sharePriceByPS

      if (marketCapByEVEBITDA > 0) {
        finalMarketCap = (marketCapByPS + marketCapByEVEBITDA) / 2
        finalSharePrice = (sharePriceByPS + sharePriceByEVEBITDA) / 2
      }

      return {
        method: 'Relative',
        enterpriseValue: Math.round(finalMarketCap),
        equityValue: Math.round(finalMarketCap),
        sharePrice: Math.round(finalSharePrice * 100) / 100,
        details: {
          medianPS,
          avgPS,
          marketCapByPS: Math.round(marketCapByPS),
          sharePriceByPS: Math.round(sharePriceByPS * 100) / 100,
          marketCapByEVEBITDA: Math.round(marketCapByEVEBITDA),
          sharePriceByEVEBITDA: Math.round(sharePriceByEVEBITDA * 100) / 100,
          comparablesCount: comparables.length
        },
        timestamp: new Date().toISOString()
      }
    } catch (error: any) {
      throw new Error(`Relative 계산 실패: ${error.message}`)
    }
  }
}
```

**예시 2: Asset Engine**

```typescript
// ❌ 단순 구현: 보정 없음
class AssetEngine extends ValuationEngine {
  async calculate(data: any) {
    return { value: (data.assets - data.liabilities) / data.shares }
  }
}

// ✅ 개선: 자산 보정 + 검증
class AssetEngine extends ValuationEngine {
  getName(): string {
    return 'Asset'
  }

  validate(data: ValuationInput): ValidationResult {
    const baseValidation = super.validate(data)
    if (!baseValidation.valid) return baseValidation

    if (!data.assets || data.assets <= 0) {
      return {
        valid: false,
        error: '자산 정보가 필요합니다.'
      }
    }

    if (!data.liabilities || data.liabilities < 0) {
      return {
        valid: false,
        error: '부채 정보가 필요합니다.'
      }
    }

    return { valid: true }
  }

  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const validation = this.validate(data)
    if (!validation.valid) {
      throw new Error(validation.error)
    }

    try {
      // 자산 보정 (선택사항)
      let adjustedAssets = data.assets!

      if (data.assetAdjustments) {
        // 재고자산 감가 (-10%)
        if (data.assetAdjustments.inventory) {
          adjustedAssets -= data.assetAdjustments.inventory * 0.1
        }

        // 무형자산 감가 (-20%)
        if (data.assetAdjustments.intangibles) {
          adjustedAssets -= data.assetAdjustments.intangibles * 0.2
        }
      }

      // 순자산가치 (NAV)
      const netAssetValue = adjustedAssets - data.liabilities!

      // 주당가치
      const sharePrice = netAssetValue / (data.sharesOutstanding || 1)

      return {
        method: 'Asset',
        enterpriseValue: Math.round(netAssetValue),
        equityValue: Math.round(netAssetValue),
        sharePrice: Math.round(sharePrice * 100) / 100,
        details: {
          totalAssets: Math.round(data.assets!),
          adjustedAssets: Math.round(adjustedAssets),
          totalLiabilities: Math.round(data.liabilities!),
          netAssetValue: Math.round(netAssetValue),
          adjustments: data.assetAdjustments || {}
        },
        timestamp: new Date().toISOString()
      }
    } catch (error: any) {
      throw new Error(`Asset 계산 실패: ${error.message}`)
    }
  }
}
```

**예시 3: Intrinsic Engine**

```typescript
// ❌ 단순 구현: ROE 계산 없음
class IntrinsicEngine extends ValuationEngine {
  async calculate(data: any) {
    return { value: data.bookValue * data.roe / data.shares }
  }
}

// ✅ 개선: ROE 계산 + 검증
class IntrinsicEngine extends ValuationEngine {
  getName(): string {
    return 'Intrinsic'
  }

  validate(data: ValuationInput): ValidationResult {
    const baseValidation = super.validate(data)
    if (!baseValidation.valid) return baseValidation

    // ROE 또는 (netIncome + equity) 필요
    if (!data.roe && !(data.netIncome && data.equity)) {
      return {
        valid: false,
        error: 'ROE 또는 당기순이익과 자기자본이 필요합니다.'
      }
    }

    if (!data.bookValue && !data.equity) {
      return {
        valid: false,
        error: '장부가치 또는 자기자본이 필요합니다.'
      }
    }

    return { valid: true }
  }

  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const validation = this.validate(data)
    if (!validation.valid) {
      throw new Error(validation.error)
    }

    try {
      // ROE 계산 (없으면 직접 계산)
      let roe = data.roe || 0

      if (!roe && data.netIncome && data.equity) {
        roe = data.netIncome / data.equity
      }

      // Book Value (없으면 equity 사용)
      const bookValue = data.bookValue || data.equity || 0

      // 내재가치 = ROE × Book Value
      const intrinsicValue = roe * bookValue

      // 주당가치
      const sharePrice = intrinsicValue / (data.sharesOutstanding || 1)

      return {
        method: 'Intrinsic',
        enterpriseValue: Math.round(intrinsicValue),
        equityValue: Math.round(intrinsicValue),
        sharePrice: Math.round(sharePrice * 100) / 100,
        details: {
          roe: Math.round(roe * 10000) / 10000, // 소수점 4자리
          bookValue: Math.round(bookValue),
          intrinsicValue: Math.round(intrinsicValue),
          netIncome: data.netIncome ? Math.round(data.netIncome) : undefined,
          equity: data.equity ? Math.round(data.equity) : undefined
        },
        timestamp: new Date().toISOString()
      }
    } catch (error: any) {
      throw new Error(`Intrinsic 계산 실패: ${error.message}`)
    }
  }
}
```

**예시 4: Tax Engine**

```typescript
// ❌ 단순 구현: 가중평균 없음
class TaxEngine extends ValuationEngine {
  async calculate(data: any) {
    const nav = data.assets - data.liabilities
    const earningsValue = data.earnings / 0.1
    return { value: (nav + earningsValue) / 2 / data.shares }
  }
}

// ✅ 개선: 가중평균 + 검증
class TaxEngine extends ValuationEngine {
  getName(): string {
    return 'Tax'
  }

  validate(data: ValuationInput): ValidationResult {
    const baseValidation = super.validate(data)
    if (!baseValidation.valid) return baseValidation

    if (!data.assets || data.assets <= 0) {
      return {
        valid: false,
        error: '자산 정보가 필요합니다.'
      }
    }

    if (!data.liabilities || data.liabilities < 0) {
      return {
        valid: false,
        error: '부채 정보가 필요합니다.'
      }
    }

    if (!data.earnings || data.earnings <= 0) {
      return {
        valid: false,
        error: '수익 정보가 필요합니다.'
      }
    }

    if (!data.discountRate || data.discountRate <= 0 || data.discountRate >= 1) {
      return {
        valid: false,
        error: '할인율은 0과 1 사이여야 합니다.'
      }
    }

    return { valid: true }
  }

  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const validation = this.validate(data)
    if (!validation.valid) {
      throw new Error(validation.error)
    }

    try {
      // 1. 순자산가치
      const netAssetValue = data.assets! - data.liabilities!

      // 2. 수익가치
      const earningsValue = data.earnings! / data.discountRate!

      // 3. 가중평균 (기본: 60% NAV + 40% Earnings)
      const navWeight = data.navWeight || 0.6
      const earningsWeight = 1 - navWeight

      const weightedValue =
        netAssetValue * navWeight + earningsValue * earningsWeight

      // 주당가치
      const sharePrice = weightedValue / (data.sharesOutstanding || 1)

      return {
        method: 'Tax',
        enterpriseValue: Math.round(weightedValue),
        equityValue: Math.round(weightedValue),
        sharePrice: Math.round(sharePrice * 100) / 100,
        details: {
          netAssetValue: Math.round(netAssetValue),
          earningsValue: Math.round(earningsValue),
          navWeight,
          earningsWeight,
          weightedValue: Math.round(weightedValue),
          discountRate: data.discountRate
        },
        timestamp: new Date().toISOString()
      }
    } catch (error: any) {
      throw new Error(`Tax 계산 실패: ${error.message}`)
    }
  }
}
```

### Step 4: Best Practice 적용

**TypeScript 타입 정의:**
```typescript
// Relative
export interface ComparableCompany {
  name: string
  marketCap: number
  revenue: number
  ebitda: number
  enterpriseValue: number
}

export interface RelativeInput extends ValuationInput {
  revenue: number
  ebitda?: number
  comparableCompanies: ComparableCompany[]
  netDebt?: number
  sharesOutstanding?: number
}

// Asset
export interface AssetAdjustments {
  inventory?: number
  intangibles?: number
}

export interface AssetInput extends ValuationInput {
  assets: number
  liabilities: number
  assetAdjustments?: AssetAdjustments
  sharesOutstanding?: number
}

// Intrinsic
export interface IntrinsicInput extends ValuationInput {
  roe?: number
  netIncome?: number
  equity?: number
  bookValue?: number
  sharesOutstanding?: number
}

// Tax
export interface TaxInput extends ValuationInput {
  assets: number
  liabilities: number
  earnings: number
  discountRate: number
  navWeight?: number // 기본 0.6
  sharesOutstanding?: number
}
```

---

## 전제조건 확인

**S3BA1 완료 확인:**
- ValuationEngine abstract class 구현됨

**S3BA2 완료 확인:**
- average(), median() 유틸리티 함수 구현됨

**S3BA3 완료 확인:**
- DCFEngine 구현 및 테스트 완료

---

## 생성 파일 (4개)

### 1. api/Backend_APIs/valuation/engines/relative-engine.ts
**목표:** 상대가치평가 엔진

**개선 사항:**
- ✅ P/S, EV/EBITDA Multiples 계산
- ✅ 유사기업 중앙값 사용 (이상치 제거)
- ✅ 복수 Multiples 평균
- ✅ 유사기업 최소 3개 검증

### 2. api/Backend_APIs/valuation/engines/asset-engine.ts
**목표:** 자산가치평가 엔진

**개선 사항:**
- ✅ 순자산가치 (NAV) 계산
- ✅ 자산 보정 (재고 -10%, 무형 -20%)
- ✅ 자산/부채 검증
- ✅ 주당가치 계산

### 3. api/Backend_APIs/valuation/engines/intrinsic-engine.ts
**목표:** 내재가치평가 엔진

**개선 사항:**
- ✅ ROE × Book Value 계산
- ✅ ROE 자동 계산 (netIncome/equity)
- ✅ Book Value 대체 (equity 사용)
- ✅ 주당가치 계산

### 4. api/Backend_APIs/valuation/engines/tax-engine.ts
**목표:** 세법상평가 엔진

**개선 사항:**
- ✅ 순자산가치 + 수익가치 가중평균
- ✅ 가중치 설정 (기본 60:40)
- ✅ 할인율 검증
- ✅ 주당가치 계산

---

## 완료 기준

### 필수 (Must Have)
- [ ] 4개 엔진 클래스 구현
- [ ] ValuationEngine 상속 확인
- [ ] 각 엔진의 calculate() 메서드
- [ ] 입력 검증 로직
- [ ] 타입 정의

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 엔진 계산 결과 확인
- [ ] 유사기업 중앙값 계산 확인
- [ ] 자산 보정 계산 확인

### 구현 항목 (Implementation)
- [ ] 정확성: 각 평가 방법 수식 정확
- [ ] 성능: Multiples 계산 최적화
- [ ] 코드 품질: JSDoc, 타입 안전성
- [ ] 확장성: 중간 결과 반환, 보정 파라미터

---

## 참조

### 평가 방법 수식

**Relative:**
- P/S = 시가총액 / 매출액
- EV/EBITDA = 기업가치 / EBITDA
- 중앙값 사용 (이상치 제거)

**Asset:**
- NAV = 자산 - 부채
- 보정: 재고 -10%, 무형 -20%

**Intrinsic:**
- 내재가치 = ROE × Book Value
- ROE = 당기순이익 / 자기자본

**Tax:**
- 가중평균 = NAV × 60% + 수익가치 × 40%
- 수익가치 = 수익 / 할인율

### 관련 Task
- **S3BA1**: Valuation Engine (Abstract class)
- **S3BA2**: Financial Math (average, median)
- **S3BA3**: DCF Engine (참고용)

---

## 주의사항

### 🔢 계산 정확성

1. **Relative: 중앙값 사용**
   - 평균값은 이상치에 민감
   - 중앙값으로 이상치 제거

2. **Asset: 자산 보정**
   - 재고자산 감가 -10%
   - 무형자산 감가 -20%
   - 보정은 선택사항

3. **Intrinsic: ROE 계산**
   - ROE 없으면 netIncome/equity로 계산
   - 음수 ROE 가능 (적자)

4. **Tax: 가중평균**
   - 일반: NAV 60% + 수익 40%
   - 자산 중심: NAV 80% + 수익 20%

### ⚡ 성능

1. **Relative: 유사기업 조회**
   - 병렬 조회 가능
   - 최소 3개 이상 권장

2. **불필요한 복사 방지**
   - 배열 직접 map/reduce
   - 중간 변수 최소화

### 📝 코드 품질

1. **ValuationEngine 인터페이스**
   - 모든 엔진 동일한 구조
   - 일관된 반환 타입

2. **중간 결과 반환**
   - Multiples, NAV, ROE 등 반환
   - 디버깅 및 검증 용이

---

## 예상 소요 시간

**작업 복잡도**: Medium-High
**파일 수**: 4개
**라인 수**: ~700줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 신규 구현 방식으로 변경
