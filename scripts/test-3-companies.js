/**
 * @description 3개 모의 기업 × 5개 평가 방법 = 15개 보고서 생성
 *
 * 기업 1: 성장형 AI 스타트업 (고성장, 적자→흑자 전환)
 * 기업 2: 안정형 제조기업 (저성장, 안정적 현금흐름)
 * 기업 3: 구조조정 기업 (손실, 자산 매각 중)
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
  magenta: '\x1b[35m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// ============================================================================
// 재무 수식
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
// 5개 평가 엔진
// ============================================================================

class DCFEngine {
  calculate(data) {
    const startTime = Date.now();
    const npv = calculateNPV(data.cashFlows, data.wacc);
    const finalCashFlow = data.cashFlows[data.cashFlows.length - 1];
    const terminalValue = calculateTerminalValue(finalCashFlow, data.wacc, data.terminalGrowthRate);
    const pvTerminalValue = terminalValue / Math.pow(1 + data.wacc, data.cashFlows.length);
    const enterpriseValue = npv + pvTerminalValue;
    const equityValue = enterpriseValue - data.netDebt;
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
  calculate(data) {
    const startTime = Date.now();
    const netAssetValue = data.assets - data.liabilities;

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

    const weightedValue = netAssetValue * effectiveNavWeight + earningsValue * effectiveEarningsWeight;
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

const engines = {
  dcf: new DCFEngine(),
  asset: new AssetEngine(),
  relative: new RelativeEngine(),
  intrinsic: new IntrinsicEngine(),
  tax: new TaxEngine(),
};

// ============================================================================
// 3개 모의 기업 데이터
// ============================================================================

const companies = [
  {
    id: 'company1',
    name: '테크이노 (AI 스타트업)',
    description: '성장형 AI 스타트업 - 고성장, 적자→흑자 전환',
    industry: 'AI/ML',
    situation: '고성장 기업',
    valuationData: {
      dcf: {
        cashFlows: [300000000, 500000000, 800000000, 1200000000, 1800000000], // 급성장
        wacc: 0.15, // 높은 할인율 (리스크)
        terminalGrowthRate: 0.05, // 높은 성장률
        netDebt: -2000000000, // 순현금 (마이너스 부채)
        sharesOutstanding: 5000000,
      },
      asset: {
        assets: 8000000000,
        liabilities: 2000000000,
        sharesOutstanding: 5000000,
      },
      relative: {
        revenue: 5000000000,
        revenueMultiple: 8.0, // 높은 배수 (고성장)
        netDebt: -2000000000,
        sharesOutstanding: 5000000,
      },
      intrinsic: {
        revenue: 5000000000,
        revenueMultiple: 8.5,
        netDebt: -2000000000,
        sharesOutstanding: 5000000,
      },
      tax: {
        assets: 8000000000,
        liabilities: 2000000000,
        earnings: 500000000, // 흑자 전환
        discountRate: 0.12,
        navWeight: 0.5, // 성장주 특성
        sharesOutstanding: 5000000,
      },
    },
  },
  {
    id: 'company2',
    name: '한국제철 (제조업)',
    description: '안정형 제조기업 - 저성장, 안정적 현금흐름',
    industry: '철강/제조',
    situation: '안정형 기업',
    valuationData: {
      dcf: {
        cashFlows: [2000000000, 2100000000, 2200000000, 2300000000, 2400000000], // 안정적 성장
        wacc: 0.08, // 낮은 할인율 (안정적)
        terminalGrowthRate: 0.02, // 낮은 성장률
        netDebt: 15000000000, // 부채 있음
        sharesOutstanding: 20000000,
      },
      asset: {
        assets: 50000000000,
        liabilities: 25000000000,
        sharesOutstanding: 20000000,
      },
      relative: {
        revenue: 30000000000,
        revenueMultiple: 1.2, // 낮은 배수 (저성장)
        netDebt: 15000000000,
        sharesOutstanding: 20000000,
      },
      intrinsic: {
        revenue: 30000000000,
        revenueMultiple: 1.5,
        netDebt: 15000000000,
        sharesOutstanding: 20000000,
      },
      tax: {
        assets: 50000000000,
        liabilities: 25000000000,
        earnings: 2500000000, // 안정적 이익
        discountRate: 0.08,
        navWeight: 0.6, // 일반 기업
        sharesOutstanding: 20000000,
      },
    },
  },
  {
    id: 'company3',
    name: '올드패션 (구조조정)',
    description: '구조조정 기업 - 손실, 자산 매각 중, 턴어라운드',
    industry: '소매/유통',
    situation: '구조조정 중',
    valuationData: {
      dcf: {
        cashFlows: [-500000000, -200000000, 100000000, 300000000, 500000000], // 적자→흑자
        wacc: 0.18, // 매우 높은 할인율 (고위험)
        terminalGrowthRate: 0.03,
        netDebt: 8000000000, // 높은 부채
        sharesOutstanding: 10000000,
      },
      asset: {
        assets: 12000000000,
        liabilities: 9000000000, // 부채 비율 높음
        sharesOutstanding: 10000000,
      },
      relative: {
        revenue: 8000000000,
        revenueMultiple: 0.8, // 낮은 배수 (부진)
        netDebt: 8000000000,
        sharesOutstanding: 10000000,
      },
      intrinsic: {
        revenue: 8000000000,
        revenueMultiple: 1.0,
        netDebt: 8000000000,
        sharesOutstanding: 10000000,
      },
      tax: {
        assets: 12000000000,
        liabilities: 9000000000,
        earnings: -800000000, // 적자
        discountRate: 0.15,
        navWeight: 0.6,
        sharesOutstanding: 10000000,
      },
    },
  },
];

// ============================================================================
// 초안 생성
// ============================================================================

function generateDraftSections(company, method, valuationResult) {
  const situationDesc = {
    company1: '급격한 성장세를 보이는 AI 스타트업으로, 최근 흑자 전환에 성공하며 시장의 주목을 받고 있습니다.',
    company2: '오랜 역사를 가진 안정적인 제조기업으로, 꾸준한 현금흐름과 배당으로 투자자들에게 신뢰를 받고 있습니다.',
    company3: '구조조정을 진행 중인 기업으로, 자산 매각과 사업 재편을 통해 턴어라운드를 추진하고 있습니다.',
  };

  return {
    executive_summary: `${company.name} 기업가치평가 요약

평가 방법: ${method.toUpperCase()}
업종: ${company.industry}
기업 상황: ${company.situation}

기업가치: ${valuationResult.enterpriseValue.toLocaleString()}원
자기자본가치: ${valuationResult.equityValue.toLocaleString()}원
주당가치: ${valuationResult.sharePrice.toLocaleString()}원

${situationDesc[company.id]}`,

    company_overview: `${company.name}는 ${company.industry} 업종의 ${company.situation}입니다.

${company.description}

본 평가는 ${method.toUpperCase()} 방법을 사용하여 수행되었습니다.`,

    financial_analysis: `재무 분석 결과:

${JSON.stringify(valuationResult.details, null, 2)}

평가 기준일: ${new Date().toLocaleDateString('ko-KR')}
계산 소요 시간: ${valuationResult.duration}ms`,

    valuation_methodology: `${method.toUpperCase()} 평가 방법론

${getMethodologyDescription(method)}

본 평가는 해당 방법론에 따라 ${company.situation} 특성을 반영하여 수행되었습니다.`,

    market_analysis: `시장 분석

업종: ${company.industry}
기업 유형: ${company.situation}

${getMarketAnalysis(company.id)}`,

    assumptions: `주요 가정 사항

${getAssumptions(company, method)}`,

    risk_factors: `리스크 요인

${getRiskFactors(company.id)}`,

    conclusion: `결론

${company.name}의 ${method.toUpperCase()} 방법 기준 주당가치는 ${valuationResult.sharePrice.toLocaleString()}원으로 평가되었습니다.

${getConclusion(company.id, method, valuationResult)}`,

    appendix: `부록: 상세 계산 내역

평가 일시: ${valuationResult.timestamp}
평가 방법: ${method.toUpperCase()}
계산 소요 시간: ${valuationResult.duration}ms

상세 내역은 위 재무 분석 섹션을 참조하시기 바랍니다.`,
  };
}

function getMethodologyDescription(method) {
  const descriptions = {
    dcf: 'DCF(현금흐름할인법)는 미래 현금흐름을 현재가치로 할인하여 기업가치를 산출하는 방법입니다. 성장성과 현금창출능력을 중시합니다.',
    asset: '자산가치법은 기업의 순자산가치(총자산 - 총부채)를 기준으로 평가합니다. 보수적이고 안정적인 평가 방법입니다.',
    relative: '상대가치법은 유사 기업의 시장 배수를 적용하여 평가합니다. 시장의 평가를 반영합니다.',
    intrinsic: '내재가치법은 기업의 본질적 가치를 추정합니다. 장기 투자 관점의 평가입니다.',
    tax: '세법상 평가는 상속세 및 증여세법에 따른 비상장주식 평가 방법입니다. 순자산가치와 수익가치를 가중평균합니다.',
  };
  return descriptions[method] || '';
}

function getMarketAnalysis(companyId) {
  const analyses = {
    company1: 'AI 시장은 연평균 30% 이상 고성장 중이며, 본 기업은 시장 선도 기업으로 자리매김하고 있습니다.',
    company2: '철강 시장은 성숙기로 안정적이나 성장률은 제한적입니다. 본 기업은 업계 상위권 기업으로 시장 점유율을 유지하고 있습니다.',
    company3: '소매 시장은 온라인 전환으로 구조적 변화 중이며, 본 기업은 오프라인 사업 축소 및 온라인 전환을 추진하고 있습니다.',
  };
  return analyses[companyId] || '';
}

function getAssumptions(company, method) {
  const data = company.valuationData[method];
  let text = `평가 방법: ${method.toUpperCase()}\n\n`;

  if (method === 'dcf') {
    text += `현금흐름 예측: 5개년\nWACC: ${(data.wacc * 100).toFixed(1)}%\n영구성장률: ${(data.terminalGrowthRate * 100).toFixed(1)}%\n순부채: ${data.netDebt.toLocaleString()}원`;
  } else if (method === 'asset') {
    text += `총자산: ${data.assets.toLocaleString()}원\n총부채: ${data.liabilities.toLocaleString()}원`;
  } else if (method === 'relative' || method === 'intrinsic') {
    text += `매출: ${data.revenue.toLocaleString()}원\n매출배수: ${data.revenueMultiple}배\n순부채: ${data.netDebt.toLocaleString()}원`;
  } else if (method === 'tax') {
    text += `총자산: ${data.assets.toLocaleString()}원\n총부채: ${data.liabilities.toLocaleString()}원\n순이익: ${data.earnings.toLocaleString()}원\nNAV 가중치: ${(data.navWeight * 100).toFixed(0)}%`;
  }

  return text;
}

function getRiskFactors(companyId) {
  const risks = {
    company1: '1. 높은 성장률 지속 가능성 불확실\n2. AI 시장 경쟁 심화\n3. 기술 변화 리스크\n4. 규제 리스크',
    company2: '1. 저성장 산업 환경\n2. 원자재 가격 변동성\n3. 글로벌 경쟁 심화\n4. 환율 리스크',
    company3: '1. 턴어라운드 실패 가능성\n2. 높은 부채 비율\n3. 지속적인 영업 손실\n4. 시장 점유율 하락',
  };
  return risks[companyId] || '';
}

function getConclusion(companyId, method, result) {
  const conclusions = {
    company1: '고성장 기업 특성상 미래 성장성이 주가에 크게 반영되었습니다. DCF 및 Relative 평가가 높게 나타났으며, 투자 시 성장성과 리스크를 균형있게 고려해야 합니다.',
    company2: '안정적인 현금흐름과 배당 능력을 보유한 기업입니다. 평가 방법별로 일관된 결과를 보이며, 보수적 투자자에게 적합합니다.',
    company3: '구조조정 진행 중으로 평가에 불확실성이 높습니다. 자산가치법이 가장 보수적인 평가를 제공하며, 턴어라운드 성공 여부가 핵심 변수입니다.',
  };
  return conclusions[companyId] || '';
}

// ============================================================================
// HTML 보고서 생성
// ============================================================================

function generateHTMLReport(company, method, valuationResult, draftSections) {
  return `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${company.name} 기업가치평가 보고서 - ${method.toUpperCase()}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 50px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 4px solid #2c3e50;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 32px;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .header .subtitle {
            font-size: 18px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        .header .company-info {
            font-size: 14px;
            color: #95a5a6;
            margin-top: 10px;
        }
        .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            margin: 5px;
            font-weight: bold;
        }
        .badge.growth { background: #e8f5e9; color: #2e7d32; }
        .badge.stable { background: #e3f2fd; color: #1565c0; }
        .badge.restructure { background: #fff3e0; color: #e65100; }
        .meta-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 40px;
        }
        .meta-info table { width: 100%; color: white; }
        .meta-info td { padding: 8px; }
        .meta-info td:first-child { font-weight: bold; width: 200px; opacity: 0.9; }
        .valuation-summary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 40px;
        }
        .valuation-summary h3 {
            color: white;
            margin-bottom: 20px;
            font-size: 22px;
        }
        .valuation-summary table { width: 100%; color: white; }
        .valuation-summary td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.2); }
        .valuation-summary .value {
            font-size: 28px;
            font-weight: bold;
            text-align: right;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            font-size: 24px;
            color: #2c3e50;
            border-left: 5px solid #3498db;
            padding-left: 15px;
            margin-bottom: 20px;
        }
        .section p, .section pre {
            margin-bottom: 15px;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.8;
        }
        .footer {
            margin-top: 60px;
            padding-top: 30px;
            border-top: 3px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 13px;
        }
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 3px solid #3498db;
        }
        .warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .warning strong {
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>기업가치평가 보고서</h1>
            <div class="subtitle">${company.name}</div>
            <div class="company-info">
                <span class="badge ${company.id === 'company1' ? 'growth' : company.id === 'company2' ? 'stable' : 'restructure'}">
                    ${company.situation}
                </span>
                <span class="badge" style="background: #e0e0e0; color: #424242;">${company.industry}</span>
            </div>
        </div>

        <div class="meta-info">
            <table>
                <tr><td>평가 방법</td><td>${method.toUpperCase()}</td></tr>
                <tr><td>기업명</td><td>${company.name}</td></tr>
                <tr><td>업종</td><td>${company.industry}</td></tr>
                <tr><td>기업 상황</td><td>${company.situation}</td></tr>
                <tr><td>평가 일시</td><td>${new Date(valuationResult.timestamp).toLocaleString('ko-KR')}</td></tr>
            </table>
        </div>

        <div class="valuation-summary">
            <h3>📊 평가 결과 요약</h3>
            <table>
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
                    <td class="value">${valuationResult.duration}ms</td>
                </tr>
            </table>
        </div>

        ${valuationResult.details.lossCompanyWarning ? `
        <div class="warning">
            <strong>⚠️ ${valuationResult.details.lossCompanyWarning}</strong>
        </div>
        ` : ''}

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
            <p><strong>${company.name}</strong> - ${company.description}</p>
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

function runTest() {
  log('\n🌍 3개 모의 기업 × 5개 평가 방법 = 15개 보고서 생성\n', 'cyan');

  const outputDir = path.join(__dirname, '../test-results/companies');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const results = [];
  let totalSuccess = 0;
  let totalFail = 0;

  companies.forEach((company, companyIndex) => {
    log(`\n${'='.repeat(70)}`, 'magenta');
    log(`🏢 기업 ${companyIndex + 1}: ${company.name}`, 'magenta');
    log(`   ${company.description}`, 'yellow');
    log('='.repeat(70), 'magenta');

    const companyResults = [];

    Object.keys(engines).forEach((methodKey, methodIndex) => {
      const engine = engines[methodKey];
      const data = company.valuationData[methodKey];

      try {
        log(`\n  [${methodIndex + 1}/5] ${methodKey.toUpperCase()} 평가 중...`, 'blue');

        // 평가 실행
        const valuationResult = engine.calculate(data);

        // 초안 생성
        const draftSections = generateDraftSections(company, methodKey, valuationResult);

        // HTML 보고서 생성
        const html = generateHTMLReport(company, methodKey, valuationResult, draftSections);

        // 파일 저장
        const companyDir = path.join(outputDir, company.id);
        if (!fs.existsSync(companyDir)) {
          fs.mkdirSync(companyDir, { recursive: true });
        }

        const htmlPath = path.join(companyDir, `${methodKey}_report.html`);
        const jsonPath = path.join(companyDir, `${methodKey}_result.json`);

        fs.writeFileSync(htmlPath, html, 'utf-8');
        fs.writeFileSync(jsonPath, JSON.stringify({
          company: {
            id: company.id,
            name: company.name,
            industry: company.industry,
            situation: company.situation,
          },
          method: methodKey,
          valuationResult,
          draftSections,
        }, null, 2), 'utf-8');

        log(`  ✅ ${methodKey.toUpperCase()}: 주당가치 ${valuationResult.sharePrice.toLocaleString()}원`, 'green');

        companyResults.push({
          method: methodKey,
          success: true,
          sharePrice: valuationResult.sharePrice,
          htmlPath,
        });

        totalSuccess++;

      } catch (error) {
        log(`  ❌ ${methodKey.toUpperCase()}: ${error.message}`, 'red');
        companyResults.push({
          method: methodKey,
          success: false,
          error: error.message,
        });
        totalFail++;
      }
    });

    results.push({
      company,
      results: companyResults,
    });
  });

  // 최종 요약
  log('\n' + '='.repeat(70), 'cyan');
  log('📋 최종 결과 요약', 'cyan');
  log('='.repeat(70), 'cyan');

  results.forEach((result, index) => {
    log(`\n[기업 ${index + 1}] ${result.company.name}`, 'magenta');
    result.results.forEach((r) => {
      const icon = r.success ? '✅' : '❌';
      const color = r.success ? 'green' : 'red';
      log(`  ${icon} ${r.method.toUpperCase()}: ${r.success ? r.sharePrice.toLocaleString() + '원' : r.error}`, color);
    });
  });

  log('\n' + '='.repeat(70), 'cyan');
  log(`총 ${totalSuccess + totalFail}개 보고서 중`, 'cyan');
  log(`✅ 성공: ${totalSuccess}개`, 'green');
  log(`❌ 실패: ${totalFail}개`, totalFail > 0 ? 'red' : 'green');
  log('='.repeat(70), 'cyan');

  if (totalSuccess === 15) {
    log('\n🎉 모든 보고서 생성 완료!', 'green');
    log(`\n📁 결과 위치: ${outputDir}`, 'blue');
    log('   각 기업별 폴더에 5개 평가 보고서가 생성되었습니다.', 'blue');
  }
}

// 실행
runTest();
