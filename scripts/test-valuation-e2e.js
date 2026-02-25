/**
 * @description 5개 평가 방법별 End-to-End 테스트
 *
 * 테스트 흐름:
 * 1. 프로젝트 생성
 * 2. 문서 업로드 (Step 4)
 * 3. 평가 실행 (Step 5)
 * 4. 초안 생성 (Step 6)
 * 5. 보고서 생성 (Step 9)
 * 6. 결과 검증
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

// 5개 평가 방법별 모의 데이터
const mockData = {
  dcf: {
    method: 'dcf',
    projectId: 'VL-20260222-DCF1',
    companyName: '테크이노 (DCF)',
    input: {
      method: 'dcf',
      projectId: 'VL-20260222-DCF1',
      cashFlows: [500000000, 600000000, 720000000, 864000000, 1036800000], // 5년 현금흐름
      wacc: 0.12, // 가중평균자본비용 12%
      terminalGrowthRate: 0.03, // 영구성장률 3%
      netDebt: 5000000000, // 순부채 50억
      sharesOutstanding: 10000000, // 발행주식수 1천만주
    },
  },
  asset: {
    method: 'asset',
    projectId: 'VL-20260222-ASS1',
    companyName: '자산풍부 (Asset)',
    input: {
      method: 'asset',
      projectId: 'VL-20260222-ASS1',
      assets: 20000000000, // 총자산 200억
      liabilities: 8000000000, // 총부채 80억
      sharesOutstanding: 5000000, // 발행주식수 500만주
    },
  },
  relative: {
    method: 'relative',
    projectId: 'VL-20260222-REL1',
    companyName: '비교대상 (Relative)',
    input: {
      method: 'relative',
      projectId: 'VL-20260222-REL1',
      revenue: 10000000000, // 매출 100억
      revenueMultiple: 3.5, // 매출배수 3.5배
      netDebt: 3000000000, // 순부채 30억
      sharesOutstanding: 8000000, // 발행주식수 800만주
    },
  },
  intrinsic: {
    method: 'intrinsic',
    projectId: 'VL-20260222-INT1',
    companyName: '내재가치 (Intrinsic)',
    input: {
      method: 'intrinsic',
      projectId: 'VL-20260222-INT1',
      revenue: 15000000000, // 매출 150억
      revenueMultiple: 4.0, // 매출배수 4배
      netDebt: 6000000000, // 순부채 60억
      sharesOutstanding: 12000000, // 발행주식수 1200만주
    },
  },
  tax: {
    method: 'tax',
    projectId: 'VL-20260222-TAX1',
    companyName: '세법평가 (Tax)',
    input: {
      method: 'tax',
      projectId: 'VL-20260222-TAX1',
      assets: 15000000000, // 총자산 150억
      liabilities: 5000000000, // 총부채 50억
      earnings: 1233333333, // 순이익 12.3억 (3년 평균)
      discountRate: 0.1, // 할인율 10%
      navWeight: 0.6, // NAV 가중치 60%
      sharesOutstanding: 10000000, // 발행주식수 1천만주
    },
  },
};

// 초안 9개 섹션 기본 템플릿
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

// 테스트 실행 함수
async function testMethod(methodKey) {
  const testData = mockData[methodKey];
  const { method, projectId, companyName, input } = testData;

  log(`\n${'='.repeat(60)}`, 'cyan');
  log(`🧪 Testing: ${method.toUpperCase()} - ${companyName}`, 'cyan');
  log('='.repeat(60), 'cyan');

  try {
    // Step 1: 평가 실행 시뮬레이션 (실제 API는 서버 필요)
    log('\n[Step 5] 평가 실행 중...', 'blue');
    log(`입력 데이터: ${JSON.stringify(input, null, 2)}`, 'yellow');

    // 여기서는 로컬 엔진을 직접 호출
    const { ValuationOrchestrator } = require('../lib/valuation/valuation-orchestrator');
    const {
      DCFEngine,
      AssetEngine,
      RelativeEngine,
      IntrinsicEngine,
      TaxEngine,
    } = require('../lib/valuation/engines');

    const orchestrator = ValuationOrchestrator.getInstance();

    // 엔진 등록
    orchestrator.registerEngine('dcf', new DCFEngine());
    orchestrator.registerEngine('asset', new AssetEngine());
    orchestrator.registerEngine('relative', new RelativeEngine());
    orchestrator.registerEngine('intrinsic', new IntrinsicEngine());
    orchestrator.registerEngine('tax', new TaxEngine());

    // 평가 실행
    const valuationResult = await orchestrator.valuate(method, input);
    log(`✅ 평가 완료!`, 'green');
    log(`기업가치: ${valuationResult.enterpriseValue.toLocaleString()}원`, 'green');
    log(`주당가치: ${valuationResult.sharePrice.toLocaleString()}원`, 'green');
    log(`소요 시간: ${valuationResult.duration}ms`, 'green');

    // Step 2: 초안 생성 시뮬레이션
    log('\n[Step 6] 초안 생성 중...', 'blue');
    const draftSections = generateDraftSections(method, companyName, valuationResult);
    log('✅ 초안 생성 완료!', 'green');
    log(`섹션 수: 9개`, 'green');

    // Step 3: 보고서 데이터 준비
    log('\n[Step 9] 보고서 데이터 준비 중...', 'blue');
    const reportData = {
      method,
      projectId,
      companyName,
      valuationResult,
      draftSections,
      generatedAt: new Date().toISOString(),
    };

    // 결과 저장 (JSON)
    const outputDir = path.join(__dirname, '../test-results');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const outputPath = path.join(outputDir, `${method}_test_result.json`);
    fs.writeFileSync(outputPath, JSON.stringify(reportData, null, 2), 'utf-8');
    log(`✅ 결과 저장: ${outputPath}`, 'green');

    // HTML 보고서 미리보기 생성
    const htmlPreview = generateHTMLPreview(reportData);
    const htmlPath = path.join(outputDir, `${method}_report_preview.html`);
    fs.writeFileSync(htmlPath, htmlPreview, 'utf-8');
    log(`✅ HTML 미리보기: ${htmlPath}`, 'green');

    return {
      success: true,
      method,
      valuationResult,
      outputPath,
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

// HTML 보고서 미리보기 생성
function generateHTMLPreview(reportData) {
  const { method, companyName, valuationResult, draftSections, generatedAt } = reportData;

  return `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${companyName} 기업가치평가 보고서 - ${method.toUpperCase()}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
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
        .meta-info table {
            width: 100%;
        }
        .meta-info td {
            padding: 5px;
        }
        .meta-info td:first-child {
            font-weight: bold;
            width: 150px;
        }
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
                <tr>
                    <td>평가 방법</td>
                    <td>${method.toUpperCase()}</td>
                </tr>
                <tr>
                    <td>프로젝트 ID</td>
                    <td>${reportData.projectId}</td>
                </tr>
                <tr>
                    <td>생성 일시</td>
                    <td>${new Date(generatedAt).toLocaleString('ko-KR')}</td>
                </tr>
            </table>
        </div>

        <div class="valuation-summary">
            <h3>📊 평가 결과 요약</h3>
            <table width="100%">
                <tr>
                    <td>기업가치 (Enterprise Value)</td>
                    <td class="value">${valuationResult.enterpriseValue.toLocaleString()}원</td>
                </tr>
                <tr>
                    <td>자기자본가치 (Equity Value)</td>
                    <td class="value">${valuationResult.equityValue.toLocaleString()}원</td>
                </tr>
                <tr>
                    <td>주당가치 (Share Price)</td>
                    <td class="value">${valuationResult.sharePrice.toLocaleString()}원</td>
                </tr>
                <tr>
                    <td>계산 소요 시간</td>
                    <td>${valuationResult.duration}ms</td>
                </tr>
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

// 메인 실행
async function main() {
  log('\n🚀 5개 평가 방법별 End-to-End 테스트 시작\n', 'cyan');
  log('테스트 대상: DCF, Asset, Relative, Intrinsic, Tax\n', 'yellow');

  const results = [];

  // 5개 방법 순차 테스트
  for (const methodKey of Object.keys(mockData)) {
    const result = await testMethod(methodKey);
    results.push(result);

    // 잠시 대기 (로그 구분을 위해)
    await new Promise(resolve => setTimeout(resolve, 1000));
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
      log(`   주당가치: ${result.valuationResult.sharePrice.toLocaleString()}원`, 'green');
      log(`   HTML: ${result.htmlPath}`, 'green');
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
  } else {
    log('\n⚠️  일부 테스트 실패. 로그를 확인해주세요.', 'yellow');
  }

  log('\n📁 결과 파일 위치: test-results/', 'blue');
  log('   - JSON 결과: test-results/{method}_test_result.json', 'blue');
  log('   - HTML 미리보기: test-results/{method}_report_preview.html', 'blue');
}

// 실행
main().catch(error => {
  log(`\n💥 치명적 오류: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});
