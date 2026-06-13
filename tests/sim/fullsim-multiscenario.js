/**
 * 5개 가치평가 계산기 — 실브라우저 다중 시나리오 풀시뮬레이션
 *
 * 각 방식에 정상/경계/극단/빈값/음수 시나리오를 투입하고:
 *  - 입력값 주입(input 이벤트 dispatch) → 계산 버튼 클릭
 *  - pageerror / console.error / alert(가드) 캡처
 *  - 헤드라인 결과를 독립 오라클(아래 expected* 함수, 공식 재구현)과 대조
 *  - 결과 영역 텍스트에서 NaN/Infinity/undefined 스캔
 *
 * 실행: node tests/sim/fullsim-multiscenario.js
 * 사전: 없음 (정적 서버를 자식 프로세스로 자동 기동)
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FRONTEND_ROOT = path.resolve(__dirname, '../../Valuation_Company/valuation-platform/frontend');
const PORT = 8137;
const BASE = `http://localhost:${PORT}/app/valuation/results`;
const REPORT = path.join(__dirname, 'fullsim-multiscenario-report.json');

// ---------- 숫자 유틸 ----------
const num = (s) => {
  if (s === null || s === undefined) return NaN;
  const cleaned = String(s).replace(/[^0-9.\-]/g, '');
  return cleaned === '' || cleaned === '-' ? NaN : parseFloat(cleaned);
};
const tolEq = (disp, oracle) => Number.isFinite(disp) && Number.isFinite(oracle) &&
  Math.abs(disp - oracle) <= Math.max(2, Math.abs(oracle) * 0.001);

// ============================================================
//  독립 오라클 (각 계산기 공식을 별도 재구현)
// ============================================================
function expectedDCF(v) {
  const pct = (x) => x / 100;
  const costOfEquity = pct(v.riskFreeRate) + v.leveredBeta * pct(v.marketRiskPremium) + pct(v.sizePremium);
  const afterTaxKd = pct(v.costOfDebt) * (1 - pct(v.taxRate));
  const sum = v.equityRatio + v.debtRatio;
  const eW = sum > 0 ? v.equityRatio / sum : 0;
  const dW = sum > 0 ? v.debtRatio / sum : 0;
  const wacc = eW * costOfEquity + dW * afterTaxKd;
  const tg = pct(v.terminalGrowth);
  if (!v.sharesOutstanding || v.sharesOutstanding <= 0) return { guard: '발행주식수' };
  if (tg >= wacc) return { guard: '영구성장률' };
  let pvSum = 0, fcff = 0;
  for (let i = 1; i <= 5; i++) {
    const nopat = v['ebit' + i] * (1 - pct(v.taxRate));
    fcff = nopat + v['dep' + i] - v['capex' + i] - v['wc' + i];
    pvSum += fcff / Math.pow(1 + wacc, i);
  }
  const tFcff = fcff * (1 + tg);
  const tv = tFcff / (wacc - tg);
  const pvTv = tv / Math.pow(1 + wacc, 5);
  const operating = pvSum + pvTv;
  const enterprise = operating + v.nonOperatingAssets;
  const equity = enterprise - v.interestBearingDebt;
  return { value: Math.round(equity / v.sharesOutstanding) };
}

function expectedTax(v) {
  if (!v.shares || v.shares <= 0) return { guard: '발행주식총수' };
  const p3 = v.income3 + v.nontax3 - v.tax3;
  const p2 = v.income2 + v.nontax2 - v.tax2;
  const p1 = v.income1 + v.nontax1 - v.tax1;
  const weighted = Math.max(0, (p3 * 1 + p2 * 2 + p1 * 3) / 6);
  const dr = v.discountRate / 100;
  const profitPS = (v.shares > 0 && dr > 0) ? (weighted * 1e6 / dr) / v.shares : 0;
  const netAssets = v.totalAssets - v.totalLiabilities;
  const assetPS = v.shares > 0 ? (netAssets * 1e6) / v.shares : 0;
  let final = Math.floor((profitPS * 3 + assetPS * 2) / 5); // 일반법인
  const floor = assetPS * 0.8;
  if (final < floor) final = Math.floor(floor);
  return { value: final };
}

function expectedIntrinsic(v) {
  if (!v.totalShares || v.totalShares <= 0) return { guard: '발행주식수' };
  if (!v.capRate || v.capRate <= 0) return { guard: '자본환원율' };
  if (!v.nav || v.nav <= 0) return { guard: '순자산가치' };
  const years = [v.y1, v.y2, v.y3].filter((x) => x !== null && x !== undefined);
  const avg = years.length ? years.reduce((a, b) => a + b, 0) / years.length : 0;
  const incomeValue = Math.max(0, avg) / (v.capRate / 100); // 백만원
  const psIncome = (incomeValue * 1e6) / v.totalShares;
  const psAsset = (v.nav * 1e6) / v.totalShares;
  return { value: Math.round((psAsset * 1 + psIncome * 1.5) / 2.5) };
}

// 기본 비교기업 멀티플 (HTML 고정 3개 행, toFixed(1) 반영)
const REL_AVG = (() => {
  const mean1 = (arr) => parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1));
  return {
    per: mean1([24.3, 25.7, 22.6]),
    pbr: mean1([2.7, 2.9, 2.4]),
    psr: mean1([3.0, 3.3, 2.7]),
    evEbitda: mean1([16.7, 17.9, 15.1]),
    evSales: mean1([3.1, 3.3, 2.8]),
  };
})();
function expectedRelative(v) {
  const wTot = v.wPer + v.wPbr + v.wPsr + v.wEvEbitda + v.wEvSales;
  if (Math.abs(wTot / 100 - 1) > 0.01) return { guard: '가중치' };
  if (!v.shares || v.shares <= 0) return { guard: '발행주식수' };
  const ps = (mc) => Math.round((mc * 1e6) / v.shares);
  const perPS = ps(v.netIncome * REL_AVG.per);
  const pbrPS = ps(v.equity * REL_AVG.pbr);
  const psrPS = ps(v.revenue * REL_AVG.psr);
  const evEbitdaPS = ps(v.ebitda * REL_AVG.evEbitda - v.netDebt);
  const evSalesPS = ps(v.revenue * REL_AVG.evSales - v.netDebt);
  const weighted = perPS * (v.wPer / 100) + pbrPS * (v.wPbr / 100) + psrPS * (v.wPsr / 100) +
    evEbitdaPS * (v.wEvEbitda / 100) + evSalesPS * (v.wEvSales / 100);
  const liq = Math.min(Math.max(v.liquidity || 0, 0), 50) / 100;
  return { value: Math.round(weighted), discounted: Math.round(weighted * (1 - liq)) }; // value=비할인, discounted=할인적용
}

const ASSET_ASSET_ROWS = ['cash', 'ar', 'inventory', 'other-current', 'investment', 'land',
  'building', 'equipment', 'intangible', 'other-noncurrent'];
const ASSET_LIAB_ROWS = ['ap', 'short-debt', 'other-current-liability', 'long-debt', 'pension',
  'other-noncurrent-liability'];
function expectedAsset(v) {
  if (!v.shares || v.shares <= 0) return { guard: '발행주식수' };
  let assetsMkt = 0, liabMkt = 0;
  for (const r of ASSET_ASSET_ROWS) assetsMkt += (v[r + '-book'] || 0) + (v[r + '-adj'] || 0);
  for (const r of ASSET_LIAB_ROWS) liabMkt += (v[r + '-book'] || 0) + (v[r + '-adj'] || 0);
  const navMarket = assetsMkt - liabMkt; // 백만원
  const navps = (navMarket * 1e6) / v.shares;
  return { value: Math.round(navps * (1 + v.navDiscount / 100)) };
}

// ============================================================
//  시나리오 정의
//  inputs: {id: value} (text/number 입력) — 미지정 필드는 HTML 기본값(또는 0 세팅) 유지
//  v: 오라클 입력 객체
// ============================================================
const SCEN = {};

// ---- DCF ----
const dcfBase = {
  sharesOutstanding: 5000000, riskFreeRate: 3.5, marketRiskPremium: 7.0, leveredBeta: 1.25,
  sizePremium: 2.0, costOfDebt: 4.8, taxRate: 25.0, equityRatio: 75.0, debtRatio: 25.0,
  terminalGrowth: 2.5, nonOperatingAssets: 8000000000, interestBearingDebt: 7000000000,
  ebit1: 5488000000, ebit2: 7134000000, ebit3: 8704000000, ebit4: 10010000000, ebit5: 11011000000,
  dep1: 515000000, dep2: 669000000, dep3: 816000000, dep4: 938000000, dep5: 1032000000,
  capex1: 858000000, capex2: 1115000000, capex3: 1360000000, capex4: 1564000000, capex5: 1720000000,
  wc1: 784000000, wc2: 823000000, wc3: 785000000, wc4: 653000000, wc5: 500000000,
};
const dcfIds = (v) => ({
  sharesOutstanding: v.sharesOutstanding, riskFreeRate: v.riskFreeRate, marketRiskPremium: v.marketRiskPremium,
  leveredBeta: v.leveredBeta, sizePremium: v.sizePremium, costOfDebt: v.costOfDebt, taxRate: v.taxRate,
  equityRatio: v.equityRatio, debtRatio: v.debtRatio, terminalGrowth: v.terminalGrowth,
  nonOperatingAssets: v.nonOperatingAssets, interestBearingDebt: v.interestBearingDebt,
  ebit1: v.ebit1, ebit2: v.ebit2, ebit3: v.ebit3, ebit4: v.ebit4, ebit5: v.ebit5,
  dep1: v.dep1, dep2: v.dep2, dep3: v.dep3, dep4: v.dep4, dep5: v.dep5,
  capex1: v.capex1, capex2: v.capex2, capex3: v.capex3, capex4: v.capex4, capex5: v.capex5,
  wc1: v.wc1, wc2: v.wc2, wc3: v.wc3, wc4: v.wc4, wc5: v.wc5,
});
SCEN.dcf = {
  file: 'dcf-valuation.html', headline: 'resultPerShare', section: 'resultSection', expect: expectedDCF,
  scenarios: [
    { name: '정상(기본값)', v: { ...dcfBase } },
    { name: '경계: 영구성장률≈WACC-0.1', v: { ...dcfBase, terminalGrowth: 7.0 } },
    { name: '극단: 대형 FCFF', v: { ...dcfBase, ebit1: 5e10, ebit2: 6e10, ebit3: 7e10, ebit4: 8e10, ebit5: 9e10 } },
    { name: '음수 FCFF(적자기업)', v: { ...dcfBase, ebit1: -2e9, ebit2: -1e9, ebit3: -5e8, ebit4: 0, ebit5: 5e8 } },
    { name: '가드: 발행주식수 0', v: { ...dcfBase, sharesOutstanding: 0 }, guard: '발행주식수' },
    { name: '가드: 영구성장률>WACC', v: { ...dcfBase, terminalGrowth: 30 }, guard: '영구성장률' },
  ].map((s) => ({ name: s.name, ids: dcfIds(s.v), v: s.v, guard: s.guard })),
};

// ---- TAX ----
const taxBase = {
  shares: 100000, discountRate: 10, income1: 1200, income2: 1000, income3: 800,
  nontax1: 0, nontax2: 0, nontax3: 0, tax1: 0, tax2: 0, tax3: 0,
  totalAssets: 5000, totalLiabilities: 2000,
};
const taxIds = (v) => ({
  'shares-outstanding': v.shares, 'discount-rate': v.discountRate,
  'income-1': v.income1, 'income-2': v.income2, 'income-3': v.income3,
  'nontax-1': v.nontax1, 'nontax-2': v.nontax2, 'nontax-3': v.nontax3,
  'tax-1': v.tax1, 'tax-2': v.tax2, 'tax-3': v.tax3,
  'total-assets': v.totalAssets, 'total-liabilities': v.totalLiabilities,
});
SCEN.tax = {
  file: 'tax-valuation.html', headline: 'result-final-value', section: 'result-section', expect: expectedTax,
  scenarios: [
    { name: '정상', v: { ...taxBase } },
    { name: '경계: 순자산80% 하한 발동(저수익)', v: { ...taxBase, income1: 50, income2: 40, income3: 30 } },
    { name: '적자연도+하한미발동(가중평균 손실반영 경로)', v: { ...taxBase, income1: 2000, income2: 1500, income3: -500 } },
    { name: '전연도 적자(가중평균 0 바닥)', v: { ...taxBase, income1: -800, income2: -600, income3: -400 } },
    { name: '극단: 대형 순이익', v: { ...taxBase, income1: 500000, income2: 450000, income3: 400000, totalAssets: 2000000, totalLiabilities: 500000 } },
    { name: '가드: 주식수 0', v: { ...taxBase, shares: 0 }, guard: '발행주식총수' },
  ].map((s) => ({ name: s.name, ids: taxIds(s.v), v: s.v, guard: s.guard })),
};

// ---- INTRINSIC ----
const intBase = { totalShares: 1000000, capRate: 10, nav: 30000, y1: 5000, y2: 4500, y3: 4000 };
const intIds = (v) => ({
  'total-shares': v.totalShares, 'capitalization-rate': v.capRate, 'nav-value': v.nav,
  'income-year1': v.y1, 'income-year2': v.y2, 'income-year3': v.y3,
});
SCEN.intrinsic = {
  file: 'intrinsic-valuation.html', headline: 'result-final', section: 'result-section', expect: expectedIntrinsic,
  scenarios: [
    { name: '정상(3개년)', v: { ...intBase } },
    { name: '극단: 고수익', v: { ...intBase, y1: 5e5, y2: 4.5e5, y3: 4e5 } },
    { name: '적자기업(수익가치 0 바닥)', v: { ...intBase, y1: -2000, y2: -1500, y3: -1000 }, expectAlertOk: true },
    { name: '경계: 낮은 자본환원율', v: { ...intBase, capRate: 1 } },
    { name: '가드: 주식수 0', v: { ...intBase, totalShares: 0 }, guard: '발행주식수' },
    { name: '가드: NAV 0', v: { ...intBase, nav: 0 }, guard: '순자산가치' },
  ].map((s) => ({ name: s.name, ids: intIds(s.v), v: s.v, guard: s.guard, expectAlertOk: s.expectAlertOk })),
};

// ---- RELATIVE ----
const relBase = {
  shares: 5000000, netIncome: 2575, equity: 28000, revenue: 24500, ebitda: 3730, netDebt: -1000,
  wPer: 40, wPbr: 30, wPsr: 0, wEvEbitda: 30, wEvSales: 0, liquidity: 0,
};
const relIds = (v) => ({
  'shares-outstanding': v.shares, 'net-income': v.netIncome, equity: v.equity, revenue: v.revenue,
  ebitda: v.ebitda, 'net-debt': v.netDebt, 'weight-per': v.wPer, 'weight-pbr': v.wPbr,
  'weight-psr': v.wPsr, 'weight-ev-ebitda': v.wEvEbitda, 'weight-ev-sales': v.wEvSales,
  'liquidity-discount': v.liquidity,
});
SCEN.relative = {
  file: 'relative-valuation.html', headline: 'result-final-value', section: 'result-section', expect: expectedRelative,
  scenarios: [
    { name: '정상(PER40/PBR30/EVEBITDA30)', v: { ...relBase } },
    { name: '비유동성할인 30%(할인적용값 검증)', v: { ...relBase, liquidity: 30 }, checkDiscount: true },
    { name: '비유동성할인 클램프(>50→50)', v: { ...relBase, liquidity: 80 }, checkDiscount: true },
    { name: '5개 멀티플 균등(20%×5)', v: { ...relBase, wPer: 20, wPbr: 20, wPsr: 20, wEvEbitda: 20, wEvSales: 20 } },
    { name: '극단: 대형 순이익/매출', v: { ...relBase, netIncome: 500000, equity: 2000000, revenue: 3000000, ebitda: 600000 } },
    { name: '적자기업(음수 순이익)', v: { ...relBase, netIncome: -3000 } },
    { name: '가드: 가중치합≠100', v: { ...relBase, wPer: 50 }, guard: '가중치' },
    { name: '가드: 주식수 0', v: { ...relBase, shares: 0 }, guard: '발행주식수' },
  ].map((s) => ({
    name: s.name, ids: relIds(s.v), v: s.v, guard: s.guard,
    extra: s.checkDiscount ? [{ id: 'result-discounted-value', expected: expectedRelative(s.v).discounted, label: '할인적용 주당가치' }] : undefined,
  })),
};

// ---- ASSET ----
const ASSET_ALL_IDS = [...ASSET_ASSET_ROWS, ...ASSET_LIAB_ROWS].flatMap((r) => [r + '-book', r + '-adj']);
const assetBase = {
  shares: 5000000, navDiscount: 0,
  'cash-book': 3000, 'cash-adj': 0, 'ar-book': 5000, 'ar-adj': -200,
  'inventory-book': 4000, 'inventory-adj': -500, 'land-book': 10000, 'land-adj': 8000,
  'building-book': 6000, 'building-adj': 2000, 'equipment-book': 3000, 'equipment-adj': -500,
  'ap-book': 4000, 'ap-adj': 0, 'short-debt-book': 5000, 'short-debt-adj': 0,
  'long-debt-book': 7000, 'long-debt-adj': 0,
};
const assetIds = (v) => {
  const o = { 'shares-outstanding': v.shares, 'nav-discount': v.navDiscount };
  for (const id of ASSET_ALL_IDS) o[id] = (v[id] !== undefined ? v[id] : 0); // 미지정 필드 0으로 명시
  return o;
};
const assetV = (v) => { const o = { shares: v.shares, navDiscount: v.navDiscount }; for (const id of ASSET_ALL_IDS) o[id] = (v[id] !== undefined ? v[id] : 0); return o; };
SCEN.asset = {
  file: 'asset-valuation.html', headline: 'result-navps-adjusted', section: 'result-section', expect: expectedAsset,
  scenarios: [
    { name: '정상', v: { ...assetBase } },
    { name: '할증 +20%', v: { ...assetBase, navDiscount: 20 } },
    { name: '할인 -30%', v: { ...assetBase, navDiscount: -30 } },
    { name: '극단: 대형 자산', v: { ...assetBase, 'land-book': 5e6, 'land-adj': 3e6, 'building-book': 2e6 } },
    { name: '자본잠식(부채>자산, 음수 NAV)', v: { ...assetBase, 'long-debt-book': 60000, 'short-debt-book': 40000 } },
    { name: '가드: 주식수 0', v: { ...assetBase, shares: 0 }, guard: '발행주식수' },
  ].map((s) => ({ name: s.name, ids: assetIds(s.v), v: assetV(s.v), guard: s.guard })),
};

// ============================================================
//  실행
// ============================================================
function bad(t) { return /NaN|Infinity|undefined/.test(t || ''); }

async function runMethod(browser, key, def, report) {
  for (const sc of def.scenarios) {
    const rec = { method: key, scenario: sc.name, ok: true, issues: [], headline: '', expected: null };
    const page = await browser.newPage();
    const dialogs = [];
    page.on('pageerror', (e) => rec.issues.push('PAGEERROR: ' + e.message.split('\n')[0]));
    page.on('console', (e) => { if (e.type() === 'error') rec.issues.push('CONSOLE: ' + e.text().slice(0, 140)); });
    page.on('dialog', (d) => { dialogs.push(d.message()); d.dismiss().catch(() => {}); });
    try {
      await page.goto(`${BASE}/${def.file}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(400);
      // 입력값 주입
      await page.evaluate((ids) => {
        for (const [id, val] of Object.entries(ids)) {
          const el = document.getElementById(id);
          if (!el) { window.__missing = (window.__missing || []); window.__missing.push(id); continue; }
          el.value = String(val);
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }, sc.ids);
      const missing = await page.evaluate(() => window.__missing || []);
      if (missing.length) rec.issues.push('MISSING_INPUT_IDS: ' + missing.join(','));

      await page.click('.btn-calculate', { timeout: 8000 });
      await page.waitForTimeout(400);

      const oracle = def.expect(sc.v);
      rec.expected = oracle;

      if (sc.guard || oracle.guard) {
        const want = sc.guard || oracle.guard;
        const fired = dialogs.some((d) => d.includes(want));
        if (!fired) { rec.ok = false; rec.issues.push(`가드 미발동(기대:"${want}") alerts=[${dialogs.join('|')}]`); }
        else rec.note = `가드 정상 발동: ${want}`;
        rec.headline = '(guard)';
      } else {
        // 정상/로버스트 시나리오: alert 떠도 expectAlertOk면 허용(적자 경고)
        const unexpectedAlert = dialogs.filter((d) => !sc.expectAlertOk);
        if (unexpectedAlert.length) { rec.ok = false; rec.issues.push('예상치 못한 alert: ' + dialogs.join(' | ')); }
        const headline = await page.$eval('#' + def.headline, (el) => el.textContent.trim()).catch(() => '(headline 누락)');
        rec.headline = headline;
        // 결과 섹션이 실제로 표시됐는지 확인 (숨김/누락이면 거짓통과 방지)
        const sectionTxt = await page.$eval('#' + def.section, (el) => {
          const cs = getComputedStyle(el);
          return (cs.display === 'none' || cs.visibility === 'hidden') ? '__HIDDEN__' : el.innerText;
        }).catch(() => '__MISSING__');
        if (sectionTxt === '__MISSING__') { rec.ok = false; rec.issues.push(`결과 섹션(#${def.section}) 없음`); }
        else if (sectionTxt === '__HIDDEN__') { rec.ok = false; rec.issues.push(`결과 섹션이 표시되지 않음(display:none)`); }
        if (bad(headline) || bad(sectionTxt)) { rec.ok = false; rec.issues.push('NaN/Infinity/undefined 노출'); }
        // 오라클 대조 (헤드라인)
        const disp = num(headline);
        if (!Number.isFinite(disp)) { rec.ok = false; rec.issues.push('헤드라인 파싱 불가: "' + headline + '"'); }
        else if (!tolEq(disp, oracle.value)) {
          rec.ok = false;
          rec.issues.push(`오라클 불일치: 화면=${disp.toLocaleString()} vs 기대=${Math.round(oracle.value).toLocaleString()}`);
        }
        // 추가 출력 검증 (예: relative 할인적용값)
        for (const ex of (sc.extra || [])) {
          const txt = await page.$eval('#' + ex.id, (el) => el.textContent.trim()).catch(() => '(누락)');
          const d = num(txt);
          if (!Number.isFinite(d) || !tolEq(d, ex.expected)) {
            rec.ok = false;
            rec.issues.push(`${ex.label}(#${ex.id}) 불일치: 화면=${txt} vs 기대=${Math.round(ex.expected).toLocaleString()}`);
          } else {
            rec.note = (rec.note ? rec.note + '; ' : '') + `${ex.label}=${txt} ✓`;
          }
        }
      }
    } catch (e) {
      rec.ok = false; rec.issues.push('EXCEPTION: ' + e.message.split('\n')[0]);
    } finally {
      await page.close();
    }
    report.records.push(rec);
    const icon = rec.ok ? '✅' : '❌';
    console.log(`${icon} [${key}] ${sc.name}` +
      (rec.headline && rec.headline !== '(guard)' ? ` → ${rec.headline}` : '') +
      (rec.note ? ` (${rec.note})` : '') +
      (rec.issues.length ? `\n     ${rec.issues.join('\n     ')}` : ''));
  }
}

(async () => {
  // 정적 서버 기동
  const server = spawn('node', [path.join(__dirname, '..', 'static-server.js'), FRONTEND_ROOT, String(PORT)], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 1200));

  const report = { timestamp: new Date().toISOString(), base: BASE, records: [] };
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'] });
  try {
    for (const key of ['dcf', 'tax', 'intrinsic', 'relative', 'asset']) {
      console.log(`\n===== ${key.toUpperCase()} =====`);
      await runMethod(browser, key, SCEN[key], report);
    }
  } finally {
    await browser.close();
    server.kill();
  }

  const pass = report.records.filter((r) => r.ok).length;
  const fail = report.records.length - pass;
  report.summary = { total: report.records.length, pass, fail };
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 2), 'utf-8');
  console.log(`\n=== 풀시뮬레이션 완료: ${pass}/${report.records.length} PASS, ${fail} FAIL ===`);
  console.log('리포트: ' + REPORT);
  process.exit(fail ? 1 : 0);
})();
