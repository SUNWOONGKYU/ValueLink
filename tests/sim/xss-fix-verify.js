/**
 * xss-fix-verify.js
 *
 * 저장형 XSS 수정 검증 — Playwright (Chromium, 헤드리스)
 * 대상:
 *   A) link.html          — window.supabase 전역 스텁
 *   B) report-summary.html — ES-module import 차단 + window.supabase 스텁
 *
 * 실행: node tests/sim/xss-fix-verify.js
 */

'use strict';

const { chromium } = require('playwright');
const path = require('path');

// ─── 경로 ────────────────────────────────────────────────────────────────────
const BASE = 'C:/ValueLink/Valuation_Company/valuation-platform/frontend/app';
const LINK_URL         = `file:///${BASE}/link.html`;
const REPORT_URL       = `file:///${BASE}/report-summary.html?company=%ED%85%8C%EC%8A%A4%ED%8A%B8`;

// ─── 페이로드 행 ─────────────────────────────────────────────────────────────
const LINK_ROW = {
  company_name:            '<img src=x onerror="window.__xss=1">A코',
  ceo_name:                '<script>window.__xss=1<\/script>',
  industry:                '<svg onload="window.__xss=1">',
  founded_year:            '2020',
  location:                '서울',
  valuation_method:        'dcf',
  valuation_amount_display:'<b>100억</b>',
  valuation_date:          '2026-01-01',
};

const REPORT_ROW = {
  company_name:              '<img src=x onerror="window.__xss=1">',
  industry:                  '<b>x</b>',
  ceo_name:                  't',
  location:                  '서울',
  valuation_method:          'dcf',
  valuation_amount_display:  '100억',
  valuation_date:            '2026-01-01',
  executive_summary:         '<img src=y onerror="window.__xss=1">요약',
  report_url:                'javascript:window.__xss=1',
  tags:                      ['<i>tag</i>'],
};

// ─── Supabase 스텁 (link.html — window.supabase 전역) ───────────────────────
// link.html 은 <script src="cdn supabase"> 로드 후 window.supabase.createClient() 를 호출.
// addInitScript 는 CDN 스크립트보다 먼저 실행되므로, CDN 이 window.supabase 를 덮어쓸 수 있다.
// 따라서 스텁을 CDN 로드 뒤에 심기 위해 route 로 CDN 요청을 빈 JS 로 대체한다.
const LINK_STUB_SCRIPT = `
(function() {
  const ROW = ${JSON.stringify(LINK_ROW)};
  window.supabase = {
    createClient: function() {
      return {
        from: function() {
          return {
            select: function() {
              return {
                order: function() {
                  return Promise.resolve({ data: [ROW], error: null });
                }
              };
            }
          };
        },
        auth: {
          getUser:           async function() { return { data: { user: null } }; },
          getSession:        async function() { return { data: { session: null } }; },
          onAuthStateChange: function()       { return { data: { subscription: { unsubscribe: function(){} } } }; }
        }
      };
    }
  };
})();
`;

// ─── Supabase 스텁 (report-summary.html — ES module createClient 패치) ───────
// report-summary.html 은 type="module" + import { createClient } from CDN.
// CDN 요청을 route 로 가로채 stub 모듈을 반환한다.
// window.__supabaseStubInstalled = true 로 패치 성공 여부 확인.
const REPORT_STUB_MODULE = (reportRowJson) => `
const ROW = ${reportRowJson};
export function createClient() {
  return {
    from: function() {
      return {
        select: function() {
          return {
            eq: function() {
              return {
                single: async function() {
                  return { data: ROW, error: null };
                }
              };
            }
          };
        }
      };
    },
    auth: {
      getUser:           async function() { return { data: { user: null } }; },
      getSession:        async function() { return { data: { session: null } }; },
      onAuthStateChange: function()       { return { data: { subscription: { unsubscribe: function(){} } } }; }
    }
  };
}
`;

// ─── 결과 수집 ────────────────────────────────────────────────────────────────
const results = [];
const consoleErrors = { A: [], B: [] };

function pass(label, detail) {
  results.push({ label, result: 'PASS', detail });
}
function fail(label, detail) {
  results.push({ label, result: 'FAIL', detail });
}

// ─── 검증 A: link.html ───────────────────────────────────────────────────────
async function verifyLinkHtml(browser) {
  const context = await browser.newContext();
  const page = await context.newPage();

  // CDN supabase 요청을 빈 모듈로 대체 (window.supabase 가 CDN 에 덮어씌워지는 걸 방지)
  await page.route('**/@supabase/supabase-js**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/javascript',
      body: '// stubbed supabase cdn',
    });
  });

  // 헤더 컴포넌트 fetch 실패 처리 (file:// 환경에서 상대경로 fetch 실패)
  await page.route('**/components/header.html', async (route) => {
    await route.fulfill({ status: 200, contentType: 'text/html', body: '' });
  });

  // window.supabase 스텁을 페이지 스크립트보다 먼저 심는다
  await page.addInitScript(LINK_STUB_SCRIPT);

  // 콘솔 에러 수집
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.A.push(msg.text());
  });
  page.on('pageerror', err => consoleErrors.A.push('[pageerror] ' + err.message));

  await page.goto(LINK_URL, { waitUntil: 'networkidle', timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(3000);

  // 어서션 A-1: window.__xss 미정의
  const xss = await page.evaluate(() => window.__xss);
  if (xss === undefined || xss === null) {
    pass('A-1 window.__xss 미정의 (스크립트 미실행)', `값: ${xss}`);
  } else {
    fail('A-1 window.__xss 미정의 (스크립트 미실행)', `window.__xss = ${xss} — XSS 실행됨!`);
  }

  // 어서션 A-2: img/script/svg 태그가 DOM 요소로 존재하지 않음
  const injectedTag = await page.$('#company-tbody img, #company-tbody script, #company-tbody svg');
  if (!injectedTag) {
    pass('A-2 주입 태그 DOM 미존재 (img/script/svg)', '선택자 결과: null');
  } else {
    const tagName = await injectedTag.evaluate(el => el.tagName);
    fail('A-2 주입 태그 DOM 미존재 (img/script/svg)', `<${tagName}> 요소가 DOM에 존재함`);
  }

  // 어서션 A-3: <img src=x 가 텍스트 노드로 존재 (이스케이프 확인)
  const tbodyText = await page.$eval('#company-tbody', el => el.textContent).catch(() => '');
  if (tbodyText.includes('<img src=x')) {
    pass('A-3 페이로드가 텍스트로 이스케이프됨', '찾은 문자열: "<img src=x"');
  } else {
    fail('A-3 페이로드가 텍스트로 이스케이프됨', `textContent 에 "<img src=x" 없음. 실제: "${tbodyText.slice(0, 200)}"`);
  }

  await context.close();
}

// ─── 검증 B: report-summary.html ─────────────────────────────────────────────
async function verifyReportSummaryHtml(browser) {
  const context = await browser.newContext();
  const page = await context.newPage();

  // supabase CDN (ESM) 요청을 스텁 모듈로 대체
  const stubModule = REPORT_STUB_MODULE(JSON.stringify(REPORT_ROW));
  await page.route('**/@supabase/supabase-js**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/javascript',
      body: stubModule,
    });
  });

  // 헤더 컴포넌트 처리
  await page.route('**/components/header.html', async (route) => {
    await route.fulfill({ status: 200, contentType: 'text/html', body: '' });
  });

  // 콘솔 에러 수집
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.B.push(msg.text());
  });
  page.on('pageerror', err => consoleErrors.B.push('[pageerror] ' + err.message));

  await page.goto(REPORT_URL, { waitUntil: 'networkidle', timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(3000);

  // 어서션 B-1: window.__xss 미정의
  const xss = await page.evaluate(() => window.__xss);
  if (xss === undefined || xss === null) {
    pass('B-1 window.__xss 미정의 (스크립트 미실행)', `값: ${xss}`);
  } else {
    fail('B-1 window.__xss 미정의 (스크립트 미실행)', `window.__xss = ${xss} — XSS 실행됨!`);
  }

  // 어서션 B-2: javascript: href 없음
  const hasJsHref = await page.evaluate(() => {
    return [...document.querySelectorAll('a')].some(a => {
      const href = a.getAttribute('href');
      return href && href.toLowerCase().startsWith('javascript:');
    });
  });
  if (!hasJsHref) {
    pass('B-2 javascript: href 없음 (safeUrl 차단)', '모든 a[href] 가 javascript: 아님');
  } else {
    fail('B-2 javascript: href 없음 (safeUrl 차단)', 'javascript: href 가 존재함');
  }

  // 어서션 B-3: executive_summary 영역에 <img src=y 가 텍스트로 포함
  const summaryText = await page.$eval('#executiveSummary', el => el.textContent).catch(() => '');
  if (summaryText.includes('<img src=y')) {
    pass('B-3 executive_summary 페이로드 텍스트 이스케이프됨', '찾은 문자열: "<img src=y"');
  } else {
    fail('B-3 executive_summary 페이로드 텍스트 이스케이프됨',
      `textContent 에 "<img src=y" 없음. 실제: "${summaryText.slice(0, 200)}"`);
  }

  await context.close();
}

// ─── 보고서 출력 ──────────────────────────────────────────────────────────────
function printReport() {
  console.log('\n════════════════════════════════════════════════════════════');
  console.log(' XSS 수정 검증 결과 (Playwright / Chromium headless)');
  console.log('════════════════════════════════════════════════════════════');

  const pad = (s, n) => String(s).padEnd(n);
  console.log(pad('어서션', 52) + pad('결과', 6) + '비고');
  console.log('─'.repeat(100));

  let passCount = 0, failCount = 0;
  for (const r of results) {
    const mark = r.result === 'PASS' ? '✓ PASS' : '✗ FAIL';
    console.log(pad(r.label, 52) + pad(mark, 6) + '  ' + r.detail);
    if (r.result === 'PASS') passCount++; else failCount++;
  }

  console.log('─'.repeat(100));
  console.log(`합계: ${passCount} PASS / ${failCount} FAIL`);

  if (consoleErrors.A.length > 0) {
    console.log('\n[A] link.html 콘솔 에러:');
    consoleErrors.A.forEach(e => console.log('  ', e));
  }
  if (consoleErrors.B.length > 0) {
    console.log('\n[B] report-summary.html 콘솔 에러:');
    consoleErrors.B.forEach(e => console.log('  ', e));
  }

  console.log('════════════════════════════════════════════════════════════\n');
  return failCount;
}

// ─── 메인 ─────────────────────────────────────────────────────────────────────
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    console.log('[A] link.html 검증 시작...');
    await verifyLinkHtml(browser);

    console.log('[B] report-summary.html 검증 시작...');
    await verifyReportSummaryHtml(browser);
  } finally {
    await browser.close();
  }

  const failCount = printReport();
  process.exit(failCount > 0 ? 1 : 0);
})();
