/**
 * 5개 가치평가법 — 처음 입력 → 계산 → 평가보고서 발행 전과정 여정 테스트
 *
 * 각 방법마다 "모의 기업" 데이터를 만들어 실제 브라우저로:
 *  1) 결과/입력 페이지(results/{method}-valuation.html)에 모의 데이터 입력(input 이벤트)
 *  2) "계산하기"(.btn-calculate) 클릭 → 결과 섹션 표시·NaN 스캔
 *  3) "평가보고서 생성" 버튼 클릭 → report-auto.html 팝업 발행(window.open)
 *  4) 발행된 보고서 검증:
 *     - "계산기 입력값 반영" 배지(=모의 입력이 샘플 폴백 아닌 실제 반영)
 *     - 모의 회사명이 표지/평가의견서에 노출
 *     - 평가기준 결과액(s.full)이 정상 서식(원/억/백만)으로 발행, NaN/Infinity/undefined 없음
 *     - 9개 섹션(요약~부록) 전부 렌더
 *     - 표지 발행기관 = 선명회계법인
 *  5) 최종 보고서 스크린샷 저장
 *
 * 실행: node tests/sim/journey-report-issue.js
 *       SIM_BASE=https://valuelink-platform.vercel.app/app/valuation node tests/sim/journey-report-issue.js  (라이브)
 * 사전: 없음 (로컬 모드는 정적 서버 자동 기동)
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FRONTEND_ROOT = path.resolve(__dirname, '../../Valuation_Company/valuation-platform/frontend');
const PORT = 8139;
const LIVE_BASE = process.env.SIM_BASE; // 예: https://valuelink-platform.vercel.app/app/valuation
const BASE = LIVE_BASE || `http://localhost:${PORT}/app/valuation`;
const SHOTS = path.join(__dirname, 'screenshots', 'journey-report');
const REPORT = path.join(__dirname, LIVE_BASE ? 'journey-report-live.json' : 'journey-report-issue-report.json');
fs.mkdirSync(SHOTS, { recursive: true });

const bad = (t) => /NaN|Infinity|undefined/.test(t || '');

// ============================================================
//  모의 기업 데이터 (5개 평가법 각각 별도 가상기업)
//  값은 가드(주식수>0, 가중치합100, 성장률<WACC 등) 미발동 유효범위
// ============================================================
const CASES = {
  dcf: {
    company: '(주)미래성장테크',
    companyField: 'companyName',
    ids: {
      sharesOutstanding: 3200000, riskFreeRate: 3.2, marketRiskPremium: 6.5, leveredBeta: 1.10,
      sizePremium: 2.5, costOfDebt: 5.0, taxRate: 22.0, equityRatio: 70.0, debtRatio: 30.0,
      terminalGrowth: 2.0, nonOperatingAssets: 5000000000, interestBearingDebt: 4000000000,
      ebit1: 4200000000, ebit2: 5100000000, ebit3: 6000000000, ebit4: 6800000000, ebit5: 7500000000,
      dep1: 420000000, dep2: 510000000, dep3: 600000000, dep4: 680000000, dep5: 750000000,
      capex1: 700000000, capex2: 850000000, capex3: 1000000000, capex4: 1130000000, capex5: 1250000000,
      wc1: 300000000, wc2: 320000000, wc3: 300000000, wc4: 250000000, wc5: 200000000,
    },
  },
  tax: {
    company: '대한정밀공업(주)',
    companyField: 'company-name',
    ids: {
      'shares-outstanding': 200000, 'discount-rate': 10,
      'income-1': 1500, 'income-2': 1300, 'income-3': 1100,
      'nontax-1': 0, 'nontax-2': 0, 'nontax-3': 0, 'tax-1': 0, 'tax-2': 0, 'tax-3': 0,
      'total-assets': 8000, 'total-liabilities': 3000,
    },
  },
  intrinsic: {
    company: '한빛바이오(주)',
    companyField: 'company-name',
    ids: {
      'total-shares': 1500000, 'capitalization-rate': 12, 'nav-value': 45000,
      'income-year1': 6000, 'income-year2': 5400, 'income-year3': 4800,
    },
  },
  relative: {
    company: '스마트커머스(주)',
    companyField: 'company-name',
    ids: {
      'shares-outstanding': 4000000, 'net-income': 3200, equity: 32000, revenue: 28000,
      ebitda: 4500, 'net-debt': -800,
      'weight-per': 35, 'weight-pbr': 25, 'weight-psr': 0, 'weight-ev-ebitda': 40, 'weight-ev-sales': 0,
      'liquidity-discount': 25,
    },
  },
  asset: {
    company: '유진자산개발(주)',
    companyField: 'company-name',
    ids: {
      'shares-outstanding': 2500000, 'nav-discount': 10,
      'cash-book': 4000, 'cash-adj': 0, 'ar-book': 6000, 'ar-adj': -300,
      'inventory-book': 5000, 'inventory-adj': -400, 'land-book': 15000, 'land-adj': 9000,
      'building-book': 8000, 'building-adj': 1500, 'equipment-book': 3500, 'equipment-adj': -600,
      'intangible-book': 0, 'intangible-adj': 0, 'investment-book': 0, 'investment-adj': 0,
      'ap-book': 5000, 'ap-adj': 0, 'short-debt-book': 6000, 'short-debt-adj': 0,
      'long-debt-book': 9000, 'long-debt-adj': 0, 'pension-book': 1200, 'pension-adj': 200,
    },
  },
};

async function runJourney(browser, method, def, report) {
  const rec = { method, company: def.company, ok: true, steps: {}, issues: [] };
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const dialogs = [];
  page.on('pageerror', (e) => rec.issues.push('PAGEERROR: ' + e.message.split('\n')[0]));
  page.on('console', (e) => { if (e.type() === 'error') rec.issues.push('CONSOLE: ' + e.text().slice(0, 140)); });
  page.on('dialog', (d) => { dialogs.push(d.message()); d.dismiss().catch(() => {}); });

  try {
    // ── STEP 1: 입력 페이지 로드 + 모의 데이터 주입 ──────────────
    await page.goto(`${BASE}/results/${method}-valuation.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(400);
    const inject = { ...def.ids, [def.companyField]: def.company };
    await page.evaluate((ids) => {
      window.__missing = [];
      for (const [id, val] of Object.entries(ids)) {
        const el = document.getElementById(id);
        if (!el) { window.__missing.push(id); continue; }
        el.value = String(val);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }, inject);
    const missing = await page.evaluate(() => window.__missing || []);
    // 회사명 필드 누락은 치명 아님(보고서는 둘 다 시도), 핵심 재무필드 누락만 실패
    const critMissing = missing.filter((m) => m !== def.companyField);
    rec.steps.input = critMissing.length ? `필드누락:${critMissing.join(',')}` : 'OK';
    if (critMissing.length) { rec.ok = false; rec.issues.push('입력필드 누락: ' + critMissing.join(',')); }

    // ── STEP 2: 계산 ────────────────────────────────────────────
    await page.click('.btn-calculate', { timeout: 8000 });
    await page.waitForTimeout(500);
    const calcTxt = await page.$eval('.result-section, #result-section, #resultSection', (el) => {
      const cs = getComputedStyle(el);
      return (cs.display === 'none' || cs.visibility === 'hidden') ? '__HIDDEN__' : el.innerText;
    }).catch(() => '__MISSING__');
    if (calcTxt === '__MISSING__' || calcTxt === '__HIDDEN__') {
      rec.ok = false; rec.issues.push('계산 결과 섹션 미표시: ' + calcTxt);
      rec.steps.calc = calcTxt;
    } else if (bad(calcTxt)) {
      rec.ok = false; rec.issues.push('계산 결과에 NaN/Infinity/undefined');
      rec.steps.calc = 'NaN노출';
    } else {
      rec.steps.calc = 'OK';
    }

    // ── STEP 3: 평가보고서 생성 버튼 클릭 → 팝업 발행 ────────────
    const [popup] = await Promise.all([
      ctx.waitForEvent('page', { timeout: 15000 }),
      page.click('button:has-text("평가보고서 생성")', { timeout: 8000 }),
    ]);
    await popup.waitForLoadState('domcontentloaded');
    await popup.waitForTimeout(700);
    const popErrors = [];
    popup.on('pageerror', (e) => popErrors.push(e.message.split('\n')[0]));

    const url = popup.url();
    rec.steps.popup = url.includes(`report-auto.html?method=${method}`) ? 'OK' : `URL이상:${url}`;
    if (!url.includes('report-auto.html')) { rec.ok = false; rec.issues.push('보고서 팝업 URL 이상: ' + url); }

    // ── STEP 4: 발행 보고서 검증 ────────────────────────────────
    const v = await popup.evaluate((companyName) => {
      const doc = document.getElementById('doc');
      const txt = doc ? doc.innerText : '';
      const html = doc ? doc.innerHTML : '';
      const sections = doc ? doc.querySelectorAll('.body section').length : 0;
      const badge = /계산기 입력값 반영/.test(html);
      const firm = /선명회계법인/.test(html);
      const coName = (document.querySelector('.cover .co') || {}).textContent || '';
      const opinion = (document.querySelector('.opinion') || {}).innerText || '';
      const fullM = opinion.match(/기업가치를\s*([^으]+?)으로 평가/);
      return {
        sections, badge, firm,
        coNameMatch: coName.includes(companyName),
        opinionMatch: opinion.includes(companyName),
        fullValue: fullM ? fullM[1].trim() : '',
        hasBad: /NaN|Infinity|undefined/.test(txt),
        len: txt.length,
      };
    }, def.company);

    if (popErrors.length) { rec.ok = false; rec.issues.push('보고서 pageerror: ' + popErrors.join('|')); }
    rec.steps.report = {
      sections9: v.sections === 9,
      badge: v.badge,
      firm선명: v.firm,
      회사명_표지: v.coNameMatch,
      회사명_의견서: v.opinionMatch,
      평가액: v.fullValue,
      noNaN: !v.hasBad,
      길이: v.len,
    };
    if (v.sections !== 9) { rec.ok = false; rec.issues.push(`섹션 ${v.sections}/9`); }
    if (!v.badge) { rec.ok = false; rec.issues.push('"계산기 입력값 반영" 배지 없음(모의입력 미반영=샘플폴백)'); }
    if (!v.firm) { rec.ok = false; rec.issues.push('발행기관(선명회계법인) 누락'); }
    if (!v.coNameMatch) { rec.ok = false; rec.issues.push('표지 회사명 불일치: 기대 ' + def.company); }
    if (!v.opinionMatch) { rec.ok = false; rec.issues.push('의견서 회사명 불일치'); }
    if (!v.fullValue || bad(v.fullValue)) { rec.ok = false; rec.issues.push('평가액 발행 이상: "' + v.fullValue + '"'); }
    if (v.hasBad) { rec.ok = false; rec.issues.push('보고서에 NaN/Infinity/undefined 노출'); }

    // ── STEP 5: 스크린샷 ────────────────────────────────────────
    await popup.screenshot({ path: path.join(SHOTS, `${method}.png`), fullPage: true }).catch(() => {});
    rec.steps.screenshot = `screenshots/journey-report/${method}.png`;

    await popup.close();
  } catch (e) {
    rec.ok = false; rec.issues.push('EXCEPTION: ' + e.message.split('\n')[0]);
  } finally {
    await ctx.close();
  }
  report.records.push(rec);
  const icon = rec.ok ? '✅' : '❌';
  console.log(`${icon} [${method}] ${rec.company} → 평가액 ${rec.steps.report ? rec.steps.report.평가액 || '?' : '?'}` +
    (rec.issues.length ? `\n     ${rec.issues.join('\n     ')}` : ''));
}

(async () => {
  let server = null;
  if (!LIVE_BASE) {
    server = spawn('node', [path.join(__dirname, '..', 'static-server.js'), FRONTEND_ROOT, String(PORT)], { stdio: 'ignore' });
    await new Promise((r) => setTimeout(r, 1200));
  } else {
    console.log('🌐 LIVE 모드: ' + BASE);
  }
  const report = { timestamp: new Date().toISOString(), base: BASE, records: [] };
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'] });
  try {
    for (const m of ['dcf', 'tax', 'intrinsic', 'relative', 'asset']) {
      console.log(`\n===== ${m.toUpperCase()} =====`);
      await runJourney(browser, m, CASES[m], report);
    }
  } finally {
    await browser.close();
    if (server) server.kill();
  }
  const pass = report.records.filter((r) => r.ok).length;
  const fail = report.records.length - pass;
  report.summary = { total: report.records.length, pass, fail };
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 2), 'utf-8');
  console.log(`\n=== 여정(입력→계산→보고서 발행) 완료: ${pass}/${report.records.length} PASS, ${fail} FAIL ===`);
  console.log('리포트: ' + REPORT);
  console.log('스크린샷: ' + SHOTS);
  process.exit(fail ? 1 : 0);
})();
