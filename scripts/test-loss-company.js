/**
 * @description 손실 기업 Tax 평가 테스트 (NAV 100% 가중치 확인)
 */

const fs = require('fs');
const path = require('path');

// 색상 출력
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Tax 엔진 (간소화 버전)
class TaxEngine {
  calculate(data) {
    const startTime = Date.now();

    // 순자산가치
    const netAssetValue = data.assets - data.liabilities;

    // 수익가치 (손실 기업 처리)
    let earningsValue = 0;
    let effectiveNavWeight = data.navWeight || 0.6;
    let effectiveEarningsWeight = 1 - effectiveNavWeight;
    let lossCompanyWarning;

    if (data.earnings <= 0) {
      earningsValue = 0;
      effectiveNavWeight = 1.0;
      effectiveEarningsWeight = 0.0;
      lossCompanyWarning = '적자 기업으로 순자산가치(NAV) 100%로 평가되었습니다.';
    } else {
      earningsValue = data.earnings / data.discountRate;
    }

    // 가중평균
    const weightedValue = netAssetValue * effectiveNavWeight + earningsValue * effectiveEarningsWeight;

    // 주당가치
    const sharePrice = weightedValue / data.sharesOutstanding;

    return {
      method: 'Tax',
      enterpriseValue: Math.round(weightedValue),
      equityValue: Math.round(weightedValue),
      sharePrice: Math.round(sharePrice * 100) / 100,
      details: {
        netAssetValue: Math.round(netAssetValue),
        earningsValue: Math.round(earningsValue),
        navWeight: effectiveNavWeight,
        earningsWeight: effectiveEarningsWeight,
        weightedValue: Math.round(weightedValue),
        discountRate: data.discountRate,
        assets: Math.round(data.assets),
        liabilities: Math.round(data.liabilities),
        earnings: Math.round(data.earnings),
        sharesOutstanding: data.sharesOutstanding,
        lossCompanyWarning,
      },
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString(),
    };
  }
}

// 테스트 케이스
const testCases = [
  {
    name: '흑자 기업 (정상)',
    input: {
      assets: 15000000000,
      liabilities: 5000000000,
      earnings: 1233333333, // 흑자
      discountRate: 0.1,
      navWeight: 0.6,
      sharesOutstanding: 10000000,
    },
    expectedNavWeight: 0.6,
    expectedEarningsWeight: 0.4,
  },
  {
    name: '손실 기업 (적자)',
    input: {
      assets: 15000000000,
      liabilities: 5000000000,
      earnings: -500000000, // 적자
      discountRate: 0.1,
      navWeight: 0.6,
      sharesOutstanding: 10000000,
    },
    expectedNavWeight: 1.0,
    expectedEarningsWeight: 0.0,
  },
  {
    name: '손익분기점 (0원)',
    input: {
      assets: 15000000000,
      liabilities: 5000000000,
      earnings: 0, // 0원
      discountRate: 0.1,
      navWeight: 0.6,
      sharesOutstanding: 10000000,
    },
    expectedNavWeight: 1.0,
    expectedEarningsWeight: 0.0,
  },
];

// 테스트 실행
function runTests() {
  log('\n🧪 Tax 엔진 손실 기업 처리 테스트\n', 'cyan');

  const engine = new TaxEngine();
  let passCount = 0;
  let failCount = 0;

  testCases.forEach((testCase, index) => {
    log(`\n${'='.repeat(60)}`, 'cyan');
    log(`테스트 ${index + 1}: ${testCase.name}`, 'cyan');
    log('='.repeat(60), 'cyan');

    log('\n입력 데이터:', 'yellow');
    log(`  자산: ${testCase.input.assets.toLocaleString()}원`, 'yellow');
    log(`  부채: ${testCase.input.liabilities.toLocaleString()}원`, 'yellow');
    log(`  순이익: ${testCase.input.earnings.toLocaleString()}원`, testCase.input.earnings < 0 ? 'red' : 'green');
    log(`  할인율: ${testCase.input.discountRate * 100}%`, 'yellow');
    log(`  NAV 가중치: ${testCase.input.navWeight * 100}%`, 'yellow');
    log(`  발행주식수: ${testCase.input.sharesOutstanding.toLocaleString()}주`, 'yellow');

    try {
      const result = engine.calculate(testCase.input);

      log('\n평가 결과:', 'blue');
      log(`  기업가치: ${result.enterpriseValue.toLocaleString()}원`, 'green');
      log(`  주당가치: ${result.sharePrice.toLocaleString()}원`, 'green');
      log(`  실제 NAV 가중치: ${result.details.navWeight * 100}%`, result.details.navWeight === testCase.expectedNavWeight ? 'green' : 'red');
      log(`  실제 수익 가중치: ${result.details.earningsWeight * 100}%`, result.details.earningsWeight === testCase.expectedEarningsWeight ? 'green' : 'red');

      if (result.details.lossCompanyWarning) {
        log(`  ⚠️  ${result.details.lossCompanyWarning}`, 'yellow');
      }

      // 검증
      const navWeightCorrect = result.details.navWeight === testCase.expectedNavWeight;
      const earningsWeightCorrect = result.details.earningsWeight === testCase.expectedEarningsWeight;

      if (navWeightCorrect && earningsWeightCorrect) {
        log('\n✅ 테스트 통과!', 'green');
        passCount++;
      } else {
        log('\n❌ 테스트 실패!', 'red');
        log(`  예상 NAV 가중치: ${testCase.expectedNavWeight * 100}%, 실제: ${result.details.navWeight * 100}%`, 'red');
        log(`  예상 수익 가중치: ${testCase.expectedEarningsWeight * 100}%, 실제: ${result.details.earningsWeight * 100}%`, 'red');
        failCount++;
      }

      log('\n상세 내역:', 'blue');
      log(JSON.stringify(result.details, null, 2), 'yellow');

    } catch (error) {
      log(`\n❌ 오류 발생: ${error.message}`, 'red');
      failCount++;
    }
  });

  // 최종 요약
  log('\n' + '='.repeat(60), 'cyan');
  log('📋 테스트 결과 요약', 'cyan');
  log('='.repeat(60), 'cyan');
  log(`✅ 통과: ${passCount}/${testCases.length}`, passCount === testCases.length ? 'green' : 'yellow');
  log(`❌ 실패: ${failCount}/${testCases.length}`, failCount === 0 ? 'green' : 'red');

  if (passCount === testCases.length) {
    log('\n🎉 모든 테스트 통과! Tax 엔진이 손실 기업을 올바르게 처리합니다.', 'green');
  } else {
    log('\n⚠️  일부 테스트 실패. 코드를 확인해주세요.', 'yellow');
  }
}

// 실행
runTests();
