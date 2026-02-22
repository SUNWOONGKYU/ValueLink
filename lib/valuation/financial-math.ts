/**
 * @task S3BA2
 * @description 재무 수학 라이브러리 (Financial Math Library)
 *
 * 기업 가치평가에 필요한 순수 수학 함수 모음입니다.
 * 모든 함수는 부수효과(side effect) 없는 순수 함수이며,
 * 입력 유효성 검증과 적절한 반올림을 포함합니다.
 *
 * 포함 함수:
 * - WACC, NPV, IRR 계산
 * - 영구가치(Terminal Value) 산출
 * - 기업가치, 주주가치, 주당가치 산출
 * - 멀티플 (PER, PSR, EV/EBITDA)
 * - 통계 (평균, 중앙값, CAGR)
 * - FCF (잉여현금흐름)
 */

// ---------------------------------------------------------------------------
// Helper: 입력 유효성 검증
// ---------------------------------------------------------------------------

/**
 * 숫자 유효성을 검증합니다.
 *
 * @param value - 검증할 값
 * @param name - 변수명 (에러 메시지용)
 * @throws {Error} NaN, Infinity, undefined, null인 경우
 */
function assertFiniteNumber(value: number, name: string): void {
  if (value === undefined || value === null) {
    throw new Error(`${name} 값이 제공되지 않았습니다.`);
  }
  if (typeof value !== 'number' || Number.isNaN(value)) {
    throw new Error(`${name} 값이 유효한 숫자가 아닙니다. (NaN)`);
  }
  if (!Number.isFinite(value)) {
    throw new Error(`${name} 값이 무한(Infinity)입니다.`);
  }
}

/**
 * 숫자가 양수인지 검증합니다.
 *
 * @param value - 검증할 값
 * @param name - 변수명 (에러 메시지용)
 * @throws {Error} 0 이하인 경우
 */
function assertPositive(value: number, name: string): void {
  assertFiniteNumber(value, name);
  if (value <= 0) {
    throw new Error(`${name} 값은 0보다 커야 합니다. (입력값: ${value})`);
  }
}

/**
 * 숫자가 음수가 아닌지 검증합니다.
 *
 * @param value - 검증할 값
 * @param name - 변수명 (에러 메시지용)
 * @throws {Error} 음수인 경우
 */
function assertNonNegative(value: number, name: string): void {
  assertFiniteNumber(value, name);
  if (value < 0) {
    throw new Error(`${name} 값은 0 이상이어야 합니다. (입력값: ${value})`);
  }
}

// ---------------------------------------------------------------------------
// 1. WACC (가중평균자본비용)
// ---------------------------------------------------------------------------

/**
 * WACC(가중평균자본비용)를 계산합니다.
 *
 * **공식:** WACC = (E/V) × Re + (D/V) × Rd × (1 - Tc)
 *
 * - E: 자기자본 시장가치
 * - D: 타인자본 시장가치
 * - V = E + D: 총 자본
 * - Re: 자기자본비용 (Cost of Equity)
 * - Rd: 타인자본비용 (Cost of Debt)
 * - Tc: 법인세율
 *
 * @param equity - 자기자본 시장가치 (원, 양수)
 * @param debt - 타인자본 시장가치 (원, 0 이상)
 * @param costOfEquity - 자기자본비용 (소수, 예: 0.12 = 12%)
 * @param costOfDebt - 타인자본비용 (소수, 예: 0.05 = 5%)
 * @param taxRate - 법인세율 (소수, 예: 0.22 = 22%)
 * @returns WACC (소수, 소수점 6자리 반올림)
 *
 * @throws {Error} equity가 0 이하, taxRate가 0~1 범위 밖인 경우
 *
 * @example
 * ```typescript
 * const wacc = calculateWACC(70000000, 30000000, 0.12, 0.05, 0.22);
 * // (70/100) × 0.12 + (30/100) × 0.05 × (1 - 0.22)
 * // = 0.084 + 0.0117 = 0.0957
 * ```
 */
export function calculateWACC(
  equity: number,
  debt: number,
  costOfEquity: number,
  costOfDebt: number,
  taxRate: number
): number {
  assertPositive(equity, '자기자본(equity)');
  assertNonNegative(debt, '타인자본(debt)');
  assertFiniteNumber(costOfEquity, '자기자본비용(costOfEquity)');
  assertFiniteNumber(costOfDebt, '타인자본비용(costOfDebt)');
  assertFiniteNumber(taxRate, '법인세율(taxRate)');

  if (taxRate < 0 || taxRate >= 1) {
    throw new Error(
      `법인세율(taxRate)은 0 이상 1 미만이어야 합니다. (입력값: ${taxRate})`
    );
  }

  const totalValue = equity + debt;
  const equityWeight = equity / totalValue;
  const debtWeight = debt / totalValue;

  const wacc =
    equityWeight * costOfEquity + debtWeight * costOfDebt * (1 - taxRate);

  return Math.round(wacc * 1_000_000) / 1_000_000;
}

// ---------------------------------------------------------------------------
// 2. NPV (순현재가치)
// ---------------------------------------------------------------------------

/**
 * NPV(순현재가치)를 계산합니다.
 *
 * **공식:** NPV = Σ(CFt / (1 + r)^t), t = 1, 2, ..., n
 *
 * 0번째 현금흐름(초기 투자금)은 할인하지 않고, 1번째부터 할인합니다.
 *
 * @param cashFlows - 현금흐름 배열 (원). cashFlows[0]은 초기 투자(보통 음수), 이후는 연도별 수익
 * @param discountRate - 할인율 (소수, 예: 0.10 = 10%, 양수)
 * @returns NPV (원, 정수 반올림)
 *
 * @throws {Error} 빈 배열, 할인율이 0 이하이거나 -1 이하인 경우
 *
 * @example
 * ```typescript
 * const npv = calculateNPV([-1000000, 400000, 400000, 400000], 0.10);
 * // = -1000000 + 400000/1.1 + 400000/1.21 + 400000/1.331
 * // ≈ -5259 (원)
 * ```
 */
export function calculateNPV(
  cashFlows: number[],
  discountRate: number
): number {
  if (!Array.isArray(cashFlows) || cashFlows.length === 0) {
    throw new Error('현금흐름(cashFlows) 배열이 비어있습니다.');
  }

  assertFiniteNumber(discountRate, '할인율(discountRate)');

  if (discountRate <= -1) {
    throw new Error(
      `할인율(discountRate)은 -1보다 커야 합니다. (입력값: ${discountRate})`
    );
  }

  for (let i = 0; i < cashFlows.length; i++) {
    assertFiniteNumber(cashFlows[i], `cashFlows[${i}]`);
  }

  let npv = 0;
  for (let t = 0; t < cashFlows.length; t++) {
    npv += cashFlows[t] / Math.pow(1 + discountRate, t);
  }

  return Math.round(npv);
}

// ---------------------------------------------------------------------------
// 3. IRR (내부수익률)
// ---------------------------------------------------------------------------

/**
 * IRR(내부수익률)을 뉴턴-랩슨법으로 계산합니다.
 *
 * **정의:** NPV(IRR) = 0을 만족하는 할인율 IRR
 *
 * 뉴턴-랩슨 반복법:
 *   r_{n+1} = r_n - NPV(r_n) / NPV'(r_n)
 *
 * @param cashFlows - 현금흐름 배열. 첫 번째 값은 반드시 음수(초기 투자)
 * @param initialGuess - IRR 초기 추정값 (기본값: 0.1 = 10%)
 * @param maxIterations - 최대 반복 횟수 (기본값: 100)
 * @param tolerance - 수렴 허용 오차 (기본값: 0.0001)
 * @returns IRR (소수, 소수점 6자리 반올림)
 *
 * @throws {Error} 첫 현금흐름이 양수, 수렴 실패 시
 *
 * @example
 * ```typescript
 * const irr = calculateIRR([-1000000, 400000, 400000, 400000]);
 * // ≈ 0.097310 (약 9.73%)
 * ```
 */
export function calculateIRR(
  cashFlows: number[],
  initialGuess: number = 0.1,
  maxIterations: number = 100,
  tolerance: number = 0.0001
): number {
  if (!Array.isArray(cashFlows) || cashFlows.length < 2) {
    throw new Error(
      '현금흐름(cashFlows) 배열에 최소 2개 항목이 필요합니다.'
    );
  }

  for (let i = 0; i < cashFlows.length; i++) {
    assertFiniteNumber(cashFlows[i], `cashFlows[${i}]`);
  }

  if (cashFlows[0] >= 0) {
    throw new Error(
      '첫 번째 현금흐름(초기 투자)은 음수여야 합니다. ' +
        `(입력값: ${cashFlows[0]})`
    );
  }

  let rate = initialGuess;

  for (let iteration = 0; iteration < maxIterations; iteration++) {
    // NPV 및 NPV의 1차 도함수 계산
    let npv = 0;
    let dnpv = 0;

    for (let t = 0; t < cashFlows.length; t++) {
      const discountFactor = Math.pow(1 + rate, t);
      npv += cashFlows[t] / discountFactor;
      if (t > 0) {
        dnpv -= (t * cashFlows[t]) / Math.pow(1 + rate, t + 1);
      }
    }

    // 수렴 확인
    if (Math.abs(npv) < tolerance) {
      return Math.round(rate * 1_000_000) / 1_000_000;
    }

    // 도함수가 0에 가까우면 수렴 불가
    if (Math.abs(dnpv) < 1e-12) {
      throw new Error(
        'IRR 계산이 수렴하지 못했습니다. 도함수가 0에 근접합니다. ' +
          '현금흐름 패턴을 확인해주세요.'
      );
    }

    // 뉴턴-랩슨 업데이트
    rate = rate - npv / dnpv;
  }

  throw new Error(
    `IRR 계산이 ${maxIterations}회 반복 내에 수렴하지 못했습니다. ` +
      `마지막 추정값: ${rate}. 초기 추정값(initialGuess)을 조정해보세요.`
  );
}

// ---------------------------------------------------------------------------
// 4. Terminal Value (영구가치)
// ---------------------------------------------------------------------------

/**
 * Gordon Growth Model로 영구가치(Terminal Value)를 계산합니다.
 *
 * **공식:** TV = FCF × (1 + g) / (WACC - g)
 *
 * @param lastCashFlow - 추정기간 마지막 연도 잉여현금흐름 (원)
 * @param growthRate - 영구성장률 (소수, 예: 0.02 = 2%)
 * @param wacc - 가중평균자본비용 (소수, 예: 0.10 = 10%)
 * @returns 영구가치 (원, 정수 반올림)
 *
 * @throws {Error} growthRate >= wacc인 경우 (모델 전제 위반)
 *
 * @example
 * ```typescript
 * const tv = calculateTerminalValue(5000000, 0.02, 0.10);
 * // = 5000000 × (1 + 0.02) / (0.10 - 0.02)
 * // = 5000000 × 1.02 / 0.08
 * // = 63,750,000원
 * ```
 */
export function calculateTerminalValue(
  lastCashFlow: number,
  growthRate: number,
  wacc: number
): number {
  assertFiniteNumber(lastCashFlow, '마지막 현금흐름(lastCashFlow)');
  assertFiniteNumber(growthRate, '영구성장률(growthRate)');
  assertFiniteNumber(wacc, 'WACC');

  if (growthRate >= wacc) {
    throw new Error(
      '영구성장률(growthRate)은 WACC보다 작아야 합니다. ' +
        `(growthRate: ${growthRate}, WACC: ${wacc}). ` +
        'Gordon Growth Model의 전제 조건입니다.'
    );
  }

  const terminalValue =
    (lastCashFlow * (1 + growthRate)) / (wacc - growthRate);

  return Math.round(terminalValue);
}

// ---------------------------------------------------------------------------
// 5. Enterprise Value (기업가치)
// ---------------------------------------------------------------------------

/**
 * 기업가치(Enterprise Value)를 계산합니다.
 *
 * **공식:** EV = NPV(현금흐름) + TV(영구가치의 현재가치)
 *
 * @param npv - 예측기간 현금흐름의 순현재가치 (원)
 * @param terminalValue - 영구가치의 현재가치 (원)
 * @returns 기업가치 (원, 정수 반올림)
 *
 * @example
 * ```typescript
 * const ev = calculateEnterpriseValue(15000000, 45000000);
 * // = 60,000,000원
 * ```
 */
export function calculateEnterpriseValue(
  npv: number,
  terminalValue: number
): number {
  assertFiniteNumber(npv, 'NPV');
  assertFiniteNumber(terminalValue, '영구가치(terminalValue)');

  return Math.round(npv + terminalValue);
}

// ---------------------------------------------------------------------------
// 6. Equity Value (주주가치)
// ---------------------------------------------------------------------------

/**
 * 주주가치(Equity Value)를 계산합니다.
 *
 * **공식:** Equity Value = Enterprise Value - Net Debt
 *
 * Net Debt = 유이자부채 - 현금성자산 (양수이면 부채가 많음)
 *
 * @param enterpriseValue - 기업가치 (원)
 * @param netDebt - 순차입금 (원, 음수 가능: 현금이 부채보다 많은 경우)
 * @returns 주주가치 (원, 정수 반올림)
 *
 * @example
 * ```typescript
 * const equity = calculateEquityValue(60000000, 10000000);
 * // = 50,000,000원
 * ```
 */
export function calculateEquityValue(
  enterpriseValue: number,
  netDebt: number
): number {
  assertFiniteNumber(enterpriseValue, '기업가치(enterpriseValue)');
  assertFiniteNumber(netDebt, '순차입금(netDebt)');

  return Math.round(enterpriseValue - netDebt);
}

// ---------------------------------------------------------------------------
// 7. Share Price (1주당 가치)
// ---------------------------------------------------------------------------

/**
 * 1주당 가치(Share Price)를 계산합니다.
 *
 * **공식:** Share Price = Equity Value / Shares Outstanding
 *
 * @param equityValue - 주주가치 (원)
 * @param sharesOutstanding - 발행주식수 (주, 양수)
 * @returns 1주당 가치 (원, 정수 반올림)
 *
 * @throws {Error} 발행주식수가 0 이하인 경우
 *
 * @example
 * ```typescript
 * const price = calculateSharePrice(50000000, 10000);
 * // = 5,000원
 * ```
 */
export function calculateSharePrice(
  equityValue: number,
  sharesOutstanding: number
): number {
  assertFiniteNumber(equityValue, '주주가치(equityValue)');
  assertPositive(sharesOutstanding, '발행주식수(sharesOutstanding)');

  return Math.round(equityValue / sharesOutstanding);
}

// ---------------------------------------------------------------------------
// 8. PER (주가수익비율)
// ---------------------------------------------------------------------------

/**
 * PER(주가수익비율)을 계산합니다.
 *
 * **공식:** PER = Market Cap / Net Income
 *
 * @param marketCap - 시가총액 (원, 양수)
 * @param netIncome - 당기순이익 (원, 양수)
 * @returns PER (배, 소수점 2자리 반올림)
 *
 * @throws {Error} 당기순이익이 0 이하인 경우 (의미 없는 PER)
 *
 * @example
 * ```typescript
 * const per = calculatePE(100000000, 10000000);
 * // = 10.00 (배)
 * ```
 */
export function calculatePE(
  marketCap: number,
  netIncome: number
): number {
  assertPositive(marketCap, '시가총액(marketCap)');
  assertPositive(
    netIncome,
    '당기순이익(netIncome). 순이익이 음수이면 PER 계산이 무의미합니다'
  );

  const pe = marketCap / netIncome;
  return Math.round(pe * 100) / 100;
}

// ---------------------------------------------------------------------------
// 9. PSR (주가매출비율)
// ---------------------------------------------------------------------------

/**
 * PSR(주가매출비율)을 계산합니다.
 *
 * **공식:** PSR = Market Cap / Revenue
 *
 * @param marketCap - 시가총액 (원, 양수)
 * @param revenue - 매출액 (원, 양수)
 * @returns PSR (배, 소수점 2자리 반올림)
 *
 * @throws {Error} 매출액이 0 이하인 경우
 *
 * @example
 * ```typescript
 * const psr = calculatePS(100000000, 50000000);
 * // = 2.00 (배)
 * ```
 */
export function calculatePS(
  marketCap: number,
  revenue: number
): number {
  assertPositive(marketCap, '시가총액(marketCap)');
  assertPositive(revenue, '매출액(revenue)');

  const ps = marketCap / revenue;
  return Math.round(ps * 100) / 100;
}

// ---------------------------------------------------------------------------
// 10. EV/EBITDA
// ---------------------------------------------------------------------------

/**
 * EV/EBITDA 멀티플을 계산합니다.
 *
 * **공식:** EV/EBITDA = Enterprise Value / EBITDA
 *
 * @param enterpriseValue - 기업가치 (원, 양수)
 * @param ebitda - EBITDA (원, 양수)
 * @returns EV/EBITDA (배, 소수점 2자리 반올림)
 *
 * @throws {Error} EBITDA가 0 이하인 경우
 *
 * @example
 * ```typescript
 * const evEbitda = calculateEVtoEBITDA(200000000, 20000000);
 * // = 10.00 (배)
 * ```
 */
export function calculateEVtoEBITDA(
  enterpriseValue: number,
  ebitda: number
): number {
  assertPositive(enterpriseValue, '기업가치(enterpriseValue)');
  assertPositive(
    ebitda,
    'EBITDA. EBITDA가 음수이면 EV/EBITDA 계산이 무의미합니다'
  );

  const ratio = enterpriseValue / ebitda;
  return Math.round(ratio * 100) / 100;
}

// ---------------------------------------------------------------------------
// 11. Average (산술평균)
// ---------------------------------------------------------------------------

/**
 * 산술평균을 계산합니다.
 *
 * **공식:** average = Σ(xi) / n
 *
 * @param numbers - 숫자 배열 (1개 이상)
 * @returns 산술평균 (소수점 2자리 반올림)
 *
 * @throws {Error} 빈 배열인 경우
 *
 * @example
 * ```typescript
 * const avg = average([10, 20, 30]);
 * // = 20.00
 * ```
 */
export function average(numbers: number[]): number {
  if (!Array.isArray(numbers) || numbers.length === 0) {
    throw new Error('평균 계산을 위한 숫자 배열이 비어있습니다.');
  }

  for (let i = 0; i < numbers.length; i++) {
    assertFiniteNumber(numbers[i], `numbers[${i}]`);
  }

  const sum = numbers.reduce((acc, val) => acc + val, 0);
  const avg = sum / numbers.length;

  return Math.round(avg * 100) / 100;
}

// ---------------------------------------------------------------------------
// 12. Median (중앙값)
// ---------------------------------------------------------------------------

/**
 * 중앙값을 계산합니다.
 *
 * 배열을 정렬한 후:
 * - 홀수 개: 가운데 값
 * - 짝수 개: 가운데 두 값의 평균
 *
 * @param numbers - 숫자 배열 (1개 이상)
 * @returns 중앙값 (소수점 2자리 반올림)
 *
 * @throws {Error} 빈 배열인 경우
 *
 * @example
 * ```typescript
 * median([3, 1, 2]);     // = 2.00
 * median([1, 2, 3, 4]);  // = 2.50
 * ```
 */
export function median(numbers: number[]): number {
  if (!Array.isArray(numbers) || numbers.length === 0) {
    throw new Error('중앙값 계산을 위한 숫자 배열이 비어있습니다.');
  }

  for (let i = 0; i < numbers.length; i++) {
    assertFiniteNumber(numbers[i], `numbers[${i}]`);
  }

  // 원본 배열을 변경하지 않기 위해 복사 후 정렬
  const sorted = [...numbers].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);

  let med: number;
  if (sorted.length % 2 === 0) {
    med = (sorted[mid - 1] + sorted[mid]) / 2;
  } else {
    med = sorted[mid];
  }

  return Math.round(med * 100) / 100;
}

// ---------------------------------------------------------------------------
// 13. CAGR (연평균성장률)
// ---------------------------------------------------------------------------

/**
 * CAGR(연평균성장률)을 계산합니다.
 *
 * **공식:** CAGR = (endValue / startValue)^(1/years) - 1
 *
 * @param startValue - 시작값 (양수)
 * @param endValue - 종료값 (양수)
 * @param years - 기간 (년, 양수)
 * @returns CAGR (소수, 소수점 6자리 반올림, 예: 0.15 = 15%)
 *
 * @throws {Error} startValue 또는 endValue가 0 이하, years가 0 이하
 *
 * @example
 * ```typescript
 * const growth = cagr(1000000, 2000000, 5);
 * // = (2000000/1000000)^(1/5) - 1
 * // ≈ 0.148698 (약 14.87%)
 * ```
 */
export function cagr(
  startValue: number,
  endValue: number,
  years: number
): number {
  assertPositive(startValue, '시작값(startValue)');
  assertPositive(endValue, '종료값(endValue)');
  assertPositive(years, '기간(years)');

  const result = Math.pow(endValue / startValue, 1 / years) - 1;

  return Math.round(result * 1_000_000) / 1_000_000;
}

// ---------------------------------------------------------------------------
// 14. FCF (잉여현금흐름)
// ---------------------------------------------------------------------------

/**
 * FCF(잉여현금흐름)를 계산합니다.
 *
 * **공식:** FCF = NOPAT + 감가상각비 - 자본적지출 - 운전자본 증감
 *
 * - NOPAT: 세후영업이익 (Net Operating Profit After Tax)
 * - 감가상각비: 비현금 비용으로 다시 더함
 * - 자본적지출(CAPEX): 설비투자 등 현금 유출
 * - 운전자본 증감: 양수이면 현금 유출 (운전자본 증가)
 *
 * @param nopat - 세후영업이익 (원)
 * @param depreciation - 감가상각비 (원, 0 이상)
 * @param capex - 자본적지출 (원, 0 이상)
 * @param deltaWorkingCapital - 운전자본 변동액 (원, 양수=증가=현금유출)
 * @returns 잉여현금흐름 (원, 정수 반올림)
 *
 * @example
 * ```typescript
 * const fcf = calculateFCF(8000000, 2000000, 3000000, 500000);
 * // = 8000000 + 2000000 - 3000000 - 500000
 * // = 6,500,000원
 * ```
 */
export function calculateFCF(
  nopat: number,
  depreciation: number,
  capex: number,
  deltaWorkingCapital: number
): number {
  assertFiniteNumber(nopat, '세후영업이익(NOPAT)');
  assertNonNegative(depreciation, '감가상각비(depreciation)');
  assertNonNegative(capex, '자본적지출(CAPEX)');
  assertFiniteNumber(deltaWorkingCapital, '운전자본변동(deltaWorkingCapital)');

  const fcf = nopat + depreciation - capex - deltaWorkingCapital;

  return Math.round(fcf);
}
