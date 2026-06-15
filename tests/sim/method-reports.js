/**
 * 5개 평가방법별 — 샘플 회사 1개씩 만들어 계산기 실행 → 결과 보고서 캡처
 * 실행: node tests/sim/method-reports.js
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const BASE = 'https://valuelink-platform.vercel.app/app/valuation/results';
const OUT = path.join(__dirname, 'screenshots', 'reports');

// 방법별 샘플 회사 + 입력값 + 결과 추출 대상
const METHODS = [
  {
    id: 'dcf', file: 'dcf-valuation.html', company: '넥스트클라우드',
    section: 'resultSection',
    ids: {
      companyName: '넥스트클라우드', sharesOutstanding: 10000000,
      riskFreeRate: 3.5, marketRiskPremium: 7.0, leveredBeta: 1.3, sizePremium: 2.0,
      costOfDebt: 5.0, taxRate: 22.0, equityRatio: 80.0, debtRatio: 20.0, terminalGrowth: 2.5,
      nonOperatingAssets: 5000000000, interestBearingDebt: 3000000000,
      ebit1: 6000000000, ebit2: 7800000000, ebit3: 9500000000, ebit4: 11000000000, ebit5: 12000000000,
      dep1: 600000000, dep2: 750000000, dep3: 900000000, dep4: 1000000000, dep5: 1100000000,
      capex1: 900000000, capex2: 1100000000, capex3: 1300000000, capex4: 1400000000, capex5: 1500000000,
      wc1: 500000000, wc2: 550000000, wc3: 600000000, wc4: 500000000, wc5: 400000000,
    },
    reads: { 영업가치: 'resultOperatingValue', 기업가치: 'resultEnterpriseValue', 주식가치: 'resultEquityValue', 주당가치: 'resultPerShare' },
  },
  {
    id: 'tax', file: 'tax-valuation.html', company: '한울푸드',
    section: 'result-section',
    ids: {
      'company-name': '한울푸드', 'shares-outstanding': 200000, 'discount-rate': 10,
      'income-1': 1800, 'income-2': 1500, 'income-3': 1200,
      'nontax-1': 0, 'nontax-2': 0, 'nontax-3': 0, 'tax-1': 0, 'tax-2': 0, 'tax-3': 0,
      'total-assets': 9000, 'total-liabilities': 3500,
    },
    reads: { '1주당 순손익가치': 'result-profit-value', '1주당 순자산가치': 'result-asset-value', 법인구분: 'result-type', 최종평가액: 'result-final-value' },
  },
  {
    id: 'intrinsic', file: 'intrinsic-valuation.html', company: '메디코어',
    section: 'result-section',
    ids: {
      'company-name': '메디코어', 'total-shares': 2000000, 'capitalization-rate': 10, 'nav-value': 45000,
      'income-year1': 6000, 'income-year2': 5200, 'income-year3': 4500,
    },
    reads: { '1주당 수익가치': 'result-income', '1주당 자산가치': 'result-asset', 수익가치총액: 'result-income-total', 본질가치: 'result-final' },
  },
  {
    id: 'relative', file: 'relative-valuation.html', company: '핀테크원',
    section: 'result-section',
    ids: {
      'company-name': '핀테크원', 'shares-outstanding': 8000000,
      'net-income': 4500, equity: 42000, revenue: 38000, ebitda: 6800, 'net-debt': 2000,
      'weight-per': 40, 'weight-pbr': 30, 'weight-psr': 0, 'weight-ev-ebitda': 30, 'weight-ev-sales': 0,
      'liquidity-discount': 20,
    },
    reads: { 'PER 기준': 'result-per-value', 'PBR 기준': 'result-pbr-value', 'EV/EBITDA 기준': 'result-ev-ebitda-value', 시가총액: 'result-market-cap', '가중평균 주당가치': 'result-final-value', '할인적용 주당가치': 'result-discounted-value' },
  },
  {
    id: 'asset', file: 'asset-valuation.html', company: '대한실업',
    section: 'result-section',
    ids: {
      'company-name': '대한실업', 'shares-outstanding': 5000000, 'nav-discount': -10,
      'cash-book': 4000, 'cash-adj': 0, 'ar-book': 6000, 'ar-adj': -300,
      'inventory-book': 5000, 'inventory-adj': -600, 'land-book': 20000, 'land-adj': 12000,
      'building-book': 9000, 'building-adj': 1500, 'equipment-book': 4000, 'equipment-adj': -800,
      'ap-book': 5000, 'ap-adj': 0, 'short-debt-book': 7000, 'short-debt-adj': 0,
      'long-debt-book': 12000, 'long-debt-adj': 0,
    },
    reads: { '장부 NAV': 'result-book-nav', 조정액: 'result-adjustment', '시가 NAV': 'result-market-nav', '주당가치(원)': 'result-navps-original', '할인적용 주당가치': 'result-navps-adjusted' },
  },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'] });
  const out = [];
  for (const m of METHODS) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
    page.on('dialog', (d) => d.dismiss().catch(() => {}));
    const rec = { id: m.id, company: m.company, results: {}, errors: [] };
    page.on('pageerror', (e) => rec.errors.push(e.message.split('\n')[0]));
    try {
      await page.goto(`${BASE}/${m.file}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(500);
      await page.evaluate((ids) => {
        for (const [id, val] of Object.entries(ids)) {
          const el = document.getElementById(id);
          if (el) { el.value = String(val); el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }
        }
      }, m.ids);
      await page.click('.btn-calculate', { timeout: 8000 });
      await page.waitForTimeout(700);
      for (const [label, eid] of Object.entries(m.reads)) {
        rec.results[label] = await page.$eval('#' + eid, (el) => el.textContent.trim()).catch(() => '(N/A)');
      }
      const sec = await page.$('#' + m.section);
      const shot = path.join(OUT, `${m.id}.png`);
      if (sec) await sec.screenshot({ path: shot }); else await page.screenshot({ path: shot, fullPage: true });
      rec.shot = shot;
    } catch (e) { rec.errors.push('EXC: ' + e.message.split('\n')[0]); }
    await page.close();
    out.push(rec);
    console.log(`\n===== ${m.id.toUpperCase()} — ${m.company} =====`);
    for (const [k, v] of Object.entries(rec.results)) console.log(`  ${k}: ${v}`);
    if (rec.errors.length) console.log('  ERR:', rec.errors.join(' | '));
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'reports.json'), JSON.stringify(out, null, 2), 'utf-8');
  console.log('\n저장:', OUT);
})();
