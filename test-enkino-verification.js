/**
 * Enkino Verification 테스트
 * WACC 12.41%로 DCF 계산 시 실제 보고서와 일치하는지 확인
 */

// 간단한 NPV 계산 함수
function calculateNPV(cashFlows, discountRate) {
  return cashFlows.reduce((npv, cf, index) => {
    const period = index + 1;
    const pv = cf / Math.pow(1 + discountRate, period);
    return npv + pv;
  }, 0);
}

// 터미널 밸류 계산
function calculateTerminalValue(lastCashFlow, growthRate, wacc) {
  return (lastCashFlow * (1 + growthRate)) / (wacc - growthRate);
}

// 입력 데이터 (현재 코드값)
const cashFlows = [
  1_117_134_000, // FY26
  1_323_608_000, // FY27
  1_556_760_000, // FY28
  1_820_434_000, // FY29
  2_118_732_000, // FY30
];

const wacc = 0.1241; // 12.41%
const terminalGrowthRate = 0.01; // 1.0%
const netDebt = 616_929_334;
const sharesOutstanding = 7_350_000;

// 실제 보고서 값
const actualData = {
  operatingValue: 16_216_378_227,
  pvCumulative: 5_605_401_153,
  pvTerminal: 10_610_977_073,
  enterpriseValue: 16_346_048_693,
  equityValue: 15_729_119_359,
  valuePerShare: 2_140,
};

console.log('========================================');
console.log('Enkino Verification Test (WACC 12.41%)');
console.log('========================================\n');

// 1. NPV 계산
const npv = calculateNPV(cashFlows, wacc);
console.log('1. PV Cumulative (NPV):');
console.log(`   계산값: ${Math.round(npv).toLocaleString()}`);
console.log(`   실제값: ${actualData.pvCumulative.toLocaleString()}`);
console.log(`   오차율: ${(((npv - actualData.pvCumulative) / actualData.pvCumulative) * 100).toFixed(2)}%\n`);

// 2. Terminal Value 계산
const terminalValue = calculateTerminalValue(cashFlows[cashFlows.length - 1], terminalGrowthRate, wacc);
const pvTerminal = terminalValue / Math.pow(1 + wacc, cashFlows.length);
console.log('2. PV Terminal:');
console.log(`   계산값: ${Math.round(pvTerminal).toLocaleString()}`);
console.log(`   실제값: ${actualData.pvTerminal.toLocaleString()}`);
console.log(`   오차율: ${(((pvTerminal - actualData.pvTerminal) / actualData.pvTerminal) * 100).toFixed(2)}%\n`);

// 3. Operating Value (Enterprise Value)
const operatingValue = npv + pvTerminal;
console.log('3. Operating Value:');
console.log(`   계산값: ${Math.round(operatingValue).toLocaleString()}`);
console.log(`   실제값: ${actualData.operatingValue.toLocaleString()}`);
console.log(`   오차율: ${(((operatingValue - actualData.operatingValue) / actualData.operatingValue) * 100).toFixed(2)}%\n`);

// 4. Enterprise Value (Operating Value + Non-operating)
const nonOperatingAssets = 129_670_466;
const enterpriseValue = operatingValue + nonOperatingAssets;
console.log('4. Enterprise Value:');
console.log(`   계산값: ${Math.round(enterpriseValue).toLocaleString()}`);
console.log(`   실제값: ${actualData.enterpriseValue.toLocaleString()}`);
console.log(`   오차율: ${(((enterpriseValue - actualData.enterpriseValue) / actualData.enterpriseValue) * 100).toFixed(2)}%\n`);

// 5. Equity Value
const equityValue = enterpriseValue - netDebt;
console.log('5. Equity Value:');
console.log(`   계산값: ${Math.round(equityValue).toLocaleString()}`);
console.log(`   실제값: ${actualData.equityValue.toLocaleString()}`);
console.log(`   오차율: ${(((equityValue - actualData.equityValue) / actualData.equityValue) * 100).toFixed(2)}%\n`);

// 6. Value Per Share
const valuePerShare = Math.round(equityValue / sharesOutstanding);
console.log('6. Value Per Share:');
console.log(`   계산값: ${valuePerShare.toLocaleString()}원`);
console.log(`   실제값: ${actualData.valuePerShare.toLocaleString()}원`);
console.log(`   오차율: ${(((valuePerShare - actualData.valuePerShare) / actualData.valuePerShare) * 100).toFixed(2)}%\n`);

// 최대 오차율 계산
const errors = [
  Math.abs(((npv - actualData.pvCumulative) / actualData.pvCumulative) * 100),
  Math.abs(((pvTerminal - actualData.pvTerminal) / actualData.pvTerminal) * 100),
  Math.abs(((operatingValue - actualData.operatingValue) / actualData.operatingValue) * 100),
  Math.abs(((enterpriseValue - actualData.enterpriseValue) / actualData.enterpriseValue) * 100),
  Math.abs(((equityValue - actualData.equityValue) / actualData.equityValue) * 100),
  Math.abs(((valuePerShare - actualData.valuePerShare) / actualData.valuePerShare) * 100),
];

const maxError = Math.max(...errors);

console.log('========================================');
console.log('검증 결과');
console.log('========================================');
console.log(`최대 오차율: ${maxError.toFixed(2)}%`);
console.log(`허용 범위: ±5.00%`);
console.log(`판정: ${maxError <= 5.0 ? '✅ PASS' : '❌ FAIL'}`);
console.log('========================================');
