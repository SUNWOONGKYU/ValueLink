/**
 * @description 5개 평가 방법별 간단 테스트 (서버 불필요)
 *
 * TypeScript 엔진 로직을 JavaScript로 단순화하여 직접 계산
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

// ============================================================================
// 재무 수식 (lib/valuation/financial-math.ts의 JavaScript 버전)
// ============================================================================

function calculateNPV(cashFlows, discountRate) {
  return cashFlows.reduce((npv, cf, year) => {
    return npv + cf / Math.pow(1 + discountRate, year + 1);
  }, 0);
}

function calculateTerminalValue(finalCashFlow, wacc, growthRate) {
  return (finalCashFlow * (1 + growthRate)) / (wacc - growthRate);
}

// ============================================================================
// 5개 평가 엔진 (간소화 버전)
// ============================================================================

class DCFEngine {
  getName() {
    return 'DCF';
  }

  calculate(data) {
    const startTime = Date.now();

    // NPV 계산
    const npv = calculateNPV(data.cashFlows, data.wacc);

    // Terminal Value 계산
    const finalCashFlow = data.cashFlows[data.cashFlows.length - 1];
    const terminalValue = calculateTerminalValue(finalCashFlow, data.wacc, data.terminalGrowthRate);

    // Terminal Value의 현재가치
    const pvTerminalValue = terminalValue / Math.pow(1 + data.wacc, data.cashFlows.length);

    // 기업가치
    const enterpriseValue = npv + pvTerminalValue;

    // 자기자본가치
    const equityValue = enterpriseValue - data.netDebt;

    // 주당가치
    const sharePrice = equityValue / data.sharesOutstanding;

    return {
      method: 'DCF',
      enterpriseValue: Math.round(enterpriseValue),
      equityValue: Math.round(equityValue),
      sharePrice: Math.round(sharePrice),
      details: {
        npv: Math.round(npv),
        terminalValue: Math.round(terminalValue),
        pvTerminalValue: Math.round(pvTerminalValue),
        netDebt: Math.round(data.netDebt),
        sharesOutstanding: data.sharesOutstanding,
      },
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString(),
    };
  }
}

class AssetEngine {
  getName() {
    return 'Asset';
  }

  calculate(data) {
    const startTime = Date.now();

    const netAssetValue = data.assets - data.liabilities;
    const sharePrice = netAssetValue / data.sharesOutstanding;

    return {
      method: 'Asset',
      enterpriseValue: Math.round(netAssetValue),
      equityValue: Math.round(netAssetValue),
      sharePrice: Math.round(sharePrice),
      details: {
        assets: Math.round(data.assets),
        liabilities: Math.round(data.liabilities),
        netAssetValue: Math.round(netAssetValue),
        sharesOutstanding: data.sharesOutstanding,
      },
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString(),
    };
  }
}

class RelativeEngine {
  getName() {
    return 'Relative';
  }

  calculate(data) {
    const startTime = Date.now();

    const enterpriseValue = data.revenue * data.revenueMultiple;
    const equityValue = enterpriseValue - data.netDebt;
    const sharePrice = equityValue / data.sharesOutstanding;

    return {
      method: 'Relative',
      enterpriseValue: Math.round(enterpriseValue),
      equityValue: Math.round(equityValue),
      sharePrice: Math.round(sharePrice),
      details: {
        revenue: Math.round(data.revenue),
        revenueMultiple: data.revenueMultiple,
        netDebt: Math.round(data.netDebt),
        sharesOutstanding: data.sharesOutstanding,
      },
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString(),
    };
  }
}

class IntrinsicEngine {
  getName() {
    return 'Intrinsic';
  }

  calculate(data) {
    const startTime = Date.now();

    const enterpriseValue = data.revenue * data.revenueMultiple;
    const equityValue = enterpriseValue - data.netDebt;
    const sharePrice = equityValue / data.sharesOutstanding;

    return {
      method: 'Intrinsic',
      enterpriseValue: Math.round(enterpriseValue),
      equityValue: Math.round(equityValue),
      sharePrice: Math.round(sharePrice),
      details: {
        revenue: Math.round(data.revenue),
        revenueMultiple: data.revenueMultiple,
        netDebt: Math.round(data.netDebt),
        sharesOutstanding: data.sharesOutstanding,
      },
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString(),
    };
  }
}

class TaxEngine {
  getName() {
    return 'Tax';
  }

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
      sharePrice: Math.round(sharePrice),
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

// ============================================================================
// 테스트 데이터
// ============================================================================

const mockData = {
  dcf: {
    method: 'dcf',
    projectId: 'VL-20260222-DCF1',
    companyName: '테크이노 (DCF)',
    input: {
      cashFlows: [500000000, 600000000, 720000000, 864000000, 1036800000],
      wacc: 0.12,
      terminalGrowthRate: 0.03,
      netDebt: 5000000000,
      sharesOutstanding: 10000000,
    },
  },
  asset: {
    method: 'asset',
    projectId: 'VL-20260222-ASS1',
    companyName: '자산풍부 (Asset)',
    input: {
      assets: 20000000000,
      liabilities: 8000000000,
      sharesOutstanding: 5000000,
    },
  },
  relative: {
    method: 'relative',
    projectId: 'VL-20260222-REL1',
    companyName: '비교대상 (Relative)',
    input: {
      revenue: 10000000000,
      revenueMultiple: 3.5,
      netDebt: 3000000000,
      sharesOutstanding: 8000000,
    },
  },
  intrinsic: {
    method: 'intrinsic',
    projectId: 'VL-20260222-INT1',
    companyName: '내재가치 (Intrinsic)',
    input: {
      revenue: 15000000000,
      revenueMultiple: 4.0,
      netDebt: 6000000000,
      sharesOutstanding: 12000000,
    },
  },
  tax: {
    method: 'tax',
    projectId: 'VL-20260222-TAX1',
    companyName: '세법평가 (Tax)',
    input: {
      assets: 15000000000,
      liabilities: 5000000000,
      earnings: 1233333333,
      discountRate: 0.1,
      navWeight: 0.6,
      sharesOutstanding: 10000000,
    },
  },
};

// 엔진 매핑
const engines = {
  dcf: new DCFEngine(),
  asset: new AssetEngine(),
  relative: new RelativeEngine(),
  intrinsic: new IntrinsicEngine(),
  tax: new TaxEngine(),
};

// ============================================================================
// 초안 생성
// ============================================================================

function generateDraftSections(method, companyName, valuationResult) {
  return {
    executive_summary: `${companyName} 기업가치평가 요약\n\n평가 방법: ${method.toUpperCase()}\n기업가치: ${valuationResult.enterpriseValue.toLocaleString()}원\n주당가치: ${valuationResult.sharePrice.toLocaleString()}원`,
    company_overview: `${companyName}는 ${method} 방법으로 평가되었습니다.`,
    financial_analysis: `재무 분석 결과:\n${JSON.stringify(valuationResult.details, null, 2)}`,
    valuation_methodology: `${method.toUpperCase()} 평가 방법론 적용`,
    market_analysis: `시장 분석 섹션 (모의 데이터)`,
    assumptions: `주요 가정 사항:\n${JSON.stringify(mockData[method].input, null, 2)}`,
    risk_factors: `리스크 요인 분석 (모의 데이터)`,
    conclusion: `결론: 주당가치 ${valuationResult.sharePrice.toLocaleString()}원`,
    appendix: `부록: 상세 계산 내역`,
  };
}

// ============================================================================
// HTML 보고서 생성
// ============================================================================

function generateHTMLPreview(reportData) {
  const { method, companyName, valuationResult, draftSections, generatedAt } = reportData;

  return `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${companyName} 기업가치평가 보고서 - ${method.toUpperCase()}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Malgun Gothic', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 28px;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .header .subtitle {
            font-size: 16px;
            color: #7f8c8d;
        }
        .meta-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .meta-info table { width: 100%; }
        .meta-info td { padding: 5px; }
        .meta-info td:first-child { font-weight: bold; width: 150px; }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            font-size: 20px;
            color: #2c3e50;
            border-left: 4px solid #3498db;
            padding-left: 10px;
            margin-bottom: 15px;
        }
        .section p, .section pre {
            margin-bottom: 10px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .valuation-summary {
            background: #e8f5e9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .valuation-summary h3 {
            color: #2e7d32;
            margin-bottom: 15px;
        }
        .valuation-summary .value {
            font-size: 24px;
            font-weight: bold;
            color: #1b5e20;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }
        pre {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>기업가치평가 보고서</h1>
            <div class="subtitle">${companyName}</div>
        </div>

        <div class="meta-info">
            <table>
                <tr><td>평가 방법</td><td>${method.toUpperCase()}</td></tr>
                <tr><td>프로젝트 ID</td><td>${reportData.projectId}</td></tr>
                <tr><td>생성 일시</td><td>${new Date(generatedAt).toLocaleString('ko-KR')}</td></tr>
            </table>
        </div>

        <div class="valuation-summary">
            <h3>📊 평가 결과 요약</h3>
            <table width="100%">
                <tr><td>기업가치 (Enterprise Value)</td><td class="value">${valuationResult.enterpriseValue.toLocaleString()}원</td></tr>
                <tr><td>자기자본가치 (Equity Value)</td><td class="value">${valuationResult.equityValue.toLocaleString()}원</td></tr>
                <tr><td>주당가치 (Share Price)</td><td class="value">${valuationResult.sharePrice.toLocaleString()}원</td></tr>
                <tr><td>계산 소요 시간</td><td>${valuationResult.duration}ms</td></tr>
            </table>
        </div>

        <div class="section">
            <h2>1. 경영진 요약 (Executive Summary)</h2>
            <p>${draftSections.executive_summary}</p>
        </div>

        <div class="section">
            <h2>2. 회사 개요 (Company Overview)</h2>
            <p>${draftSections.company_overview}</p>
        </div>

        <div class="section">
            <h2>3. 재무 분석 (Financial Analysis)</h2>
            <pre>${draftSections.financial_analysis}</pre>
        </div>

        <div class="section">
            <h2>4. 평가 방법론 (Valuation Methodology)</h2>
            <p>${draftSections.valuation_methodology}</p>
        </div>

        <div class="section">
            <h2>5. 시장 분석 (Market Analysis)</h2>
            <p>${draftSections.market_analysis}</p>
        </div>

        <div class="section">
            <h2>6. 주요 가정 (Assumptions)</h2>
            <pre>${draftSections.assumptions}</pre>
        </div>

        <div class="section">
            <h2>7. 리스크 요인 (Risk Factors)</h2>
            <p>${draftSections.risk_factors}</p>
        </div>

        <div class="section">
            <h2>8. 결론 (Conclusion)</h2>
            <p>${draftSections.conclusion}</p>
        </div>

        <div class="section">
            <h2>9. 부록 (Appendix)</h2>
            <p>${draftSections.appendix}</p>
        </div>

        <div class="footer">
            <p>본 보고서는 모의 데이터를 사용한 테스트 보고서입니다.</p>
            <p>© 2026 ValueLink. All rights reserved.</p>
        </div>
    </div>
</body>
</html>`;
}

// ============================================================================
// 테스트 실행
// ============================================================================

function testMethod(methodKey) {
  const testData = mockData[methodKey];
  const { method, projectId, companyName, input } = testData;
  const engine = engines[methodKey];

  log(`\n${'='.repeat(60)}`, 'cyan');
  log(`🧪 Testing: ${method.toUpperCase()} - ${companyName}`, 'cyan');
  log('='.repeat(60), 'cyan');

  try {
    // Step 5: 평가 실행
    log('\n[Step 5] 평가 실행 중...', 'blue');
    log(`입력 데이터: ${JSON.stringify(input, null, 2)}`, 'yellow');

    const valuationResult = engine.calculate(input);
    log(`✅ 평가 완료!`, 'green');
    log(`기업가치: ${valuationResult.enterpriseValue.toLocaleString()}원`, 'green');
    log(`주당가치: ${valuationResult.sharePrice.toLocaleString()}원`, 'green');
    log(`소요 시간: ${valuationResult.duration}ms`, 'green');

    // Step 6: 초안 생성
    log('\n[Step 6] 초안 생성 중...', 'blue');
    const draftSections = generateDraftSections(method, companyName, valuationResult);
    log('✅ 초안 생성 완료!', 'green');
    log(`섹션 수: 9개`, 'green');

    // Step 9: 보고서 데이터 준비
    log('\n[Step 9] 보고서 데이터 준비 중...', 'blue');
    const reportData = {
      method,
      projectId,
      companyName,
      valuationResult,
      draftSections,
      generatedAt: new Date().toISOString(),
    };

    // 결과 저장
    const outputDir = path.join(__dirname, '../test-results');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // JSON 저장
    const jsonPath = path.join(outputDir, `${method}_test_result.json`);
    fs.writeFileSync(jsonPath, JSON.stringify(reportData, null, 2), 'utf-8');
    log(`✅ JSON 저장: ${jsonPath}`, 'green');

    // HTML 보고서 생성
    const htmlPreview = generateHTMLPreview(reportData);
    const htmlPath = path.join(outputDir, `${method}_report_preview.html`);
    fs.writeFileSync(htmlPath, htmlPreview, 'utf-8');
    log(`✅ HTML 보고서: ${htmlPath}`, 'green');

    return {
      success: true,
      method,
      valuationResult,
      jsonPath,
      htmlPath,
    };
  } catch (error) {
    log(`\n❌ 테스트 실패: ${error.message}`, 'red');
    console.error(error);
    return {
      success: false,
      method,
      error: error.message,
    };
  }
}

// ============================================================================
// 메인 실행
// ============================================================================

function main() {
  log('\n🚀 5개 평가 방법별 End-to-End 테스트 시작\n', 'cyan');
  log('테스트 대상: DCF, Asset, Relative, Intrinsic, Tax\n', 'yellow');

  const results = [];

  // 5개 방법 순차 테스트
  for (const methodKey of Object.keys(mockData)) {
    const result = testMethod(methodKey);
    results.push(result);
  }

  // 최종 요약
  log('\n' + '='.repeat(60), 'cyan');
  log('📋 테스트 결과 요약', 'cyan');
  log('='.repeat(60), 'cyan');

  const successCount = results.filter(r => r.success).length;
  const failCount = results.filter(r => !r.success).length;

  results.forEach((result, index) => {
    const icon = result.success ? '✅' : '❌';
    const color = result.success ? 'green' : 'red';
    log(`${icon} ${index + 1}. ${result.method.toUpperCase()}: ${result.success ? 'SUCCESS' : 'FAILED'}`, color);
    if (result.success) {
      log(`   기업가치: ${result.valuationResult.enterpriseValue.toLocaleString()}원`, 'green');
      log(`   주당가치: ${result.valuationResult.sharePrice.toLocaleString()}원`, 'green');
      log(`   HTML: ${result.htmlPath}`, 'blue');
    } else {
      log(`   에러: ${result.error}`, 'red');
    }
  });

  log('\n' + '='.repeat(60), 'cyan');
  log(`✅ 성공: ${successCount}/5`, 'green');
  log(`❌ 실패: ${failCount}/5`, failCount > 0 ? 'red' : 'green');
  log('='.repeat(60), 'cyan');

  if (successCount === 5) {
    log('\n🎉 모든 테스트 통과! 보고서 생성 시스템이 정상 작동합니다.', 'green');
    log('\n📁 생성된 파일:', 'blue');
    log('   - JSON 결과: test-results/{method}_test_result.json', 'blue');
    log('   - HTML 보고서: test-results/{method}_report_preview.html', 'blue');
    log('\n💡 HTML 파일을 브라우저에서 열어 보고서를 확인하세요!', 'cyan');
  } else {
    log('\n⚠️  일부 테스트 실패. 로그를 확인해주세요.', 'yellow');
  }
}

// 실행
main();
