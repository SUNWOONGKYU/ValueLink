/**
 * role-gate-verify.js
 *
 * 평가보고서 페이지 "역할 사전 게이트" Playwright(Chromium, 헤드리스) 검증
 * — CDN(@supabase/supabase-js)을 route intercept로 차단 후
 *   addInitScript로 window.supabase 스텁을 설치한다.
 *   프로덕션 DB에 접근하지 않는다.
 *
 * 시나리오:
 *   [1] 비로그인             → #regBtn disabled === false  (버튼 유지)
 *   [2] 로그인 고객(customer) → #regBtn disabled === false  (활성)
 *   [3] 로그인 비고객(accnt)  → #regBtn disabled === true, title에 "고객 계정만" 포함
 *
 * 실행: node tests/sim/role-gate-verify.js
 */

'use strict';

const { chromium } = require('@playwright/test');

const FILE_URL =
  'file:///C:/ValueLink/Valuation_Company/valuation-platform/frontend/app/valuation/report-auto.html';

// CDN URL 패턴 — route intercept로 빈 JS 응답 대체
const CDN_PATTERN = '**/@supabase/supabase-js*';

// 역할 게이트 async IIFE 완료 대기 (밀리초)
const GATE_WAIT_MS = 2000;

const results = [];
const consoleErrors = [];

function pass(name, detail) {
  results.push({ name, status: 'PASS', detail: detail || '' });
  console.log(`[PASS] ${name}`);
  if (detail) console.log(`       ${detail}`);
}

function fail(name, detail) {
  results.push({ name, status: 'FAIL', detail: detail || '' });
  console.error(`[FAIL] ${name}`);
  if (detail) console.error(`       ${detail}`);
}

/**
 * window.supabase 스텁 스크립트 문자열 생성
 *
 * @param {object} userResult  — auth.getUser() 반환값   {data:{user:...}}
 * @param {object|null} roleResult — from().select().eq().single() 반환값
 */
function buildStub(userResult, roleResult) {
  const userJson = JSON.stringify(userResult);
  const roleJson = JSON.stringify(roleResult);
  return `
(function(){
  var USER_RESULT = ${userJson};
  var ROLE_RESULT = ${roleJson};

  window.supabase = {
    createClient: function() {
      return {
        auth: {
          getUser: async function() { return USER_RESULT; },
          onAuthStateChange: function() {
            return { data: { subscription: { unsubscribe: function(){} } } };
          },
          getSession: async function() { return { data: { session: null } }; }
        },
        from: function(t) {
          return {
            select: function() {
              return {
                eq: function() {
                  return {
                    single: async function() { return ROLE_RESULT; },
                    limit: function() { return Promise.resolve({ data: [], error: null }); }
                  };
                },
                order: function() { return Promise.resolve({ data: [], error: null }); }
              };
            }
          };
        }
      };
    }
  };
})();
`;
}

/**
 * 단일 시나리오 실행
 *
 * @param {object}  browser
 * @param {string}  scenarioName
 * @param {string}  stubScript     addInitScript 에 전달할 스크립트 문자열
 * @param {boolean} expectDisabled #regBtn 이 disabled 여야 하면 true
 */
async function runScenario(browser, scenarioName, stubScript, expectDisabled) {
  const ctx = await browser.newContext();

  // CDN 차단 — window.supabase 를 스텁이 독점
  await ctx.route(CDN_PATTERN, route =>
    route.fulfill({ status: 200, contentType: 'application/javascript', body: '// cdn-stub-blocked' })
  );

  const page = await ctx.newPage();

  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(`[${scenarioName}] ${msg.text()}`);
    }
  });

  // 스텁 설치 (domcontentloaded 이전 실행)
  await page.addInitScript({ content: stubScript });

  await page.goto(FILE_URL, { waitUntil: 'domcontentloaded' });

  // 역할 게이트 async IIFE 완료 대기
  await page.waitForTimeout(GATE_WAIT_MS);

  // #regBtn 상태 수집
  let isDisabled = false;
  let title      = '';
  let btnExists  = false;

  try {
    const btn = await page.$('#regBtn');
    if (!btn) {
      fail(scenarioName, '#regBtn 요소가 존재하지 않음');
      await ctx.close();
      return;
    }
    btnExists  = true;
    isDisabled = await page.evaluate(el => el.disabled, btn);
    title      = (await btn.getAttribute('title')) || '';
  } catch (e) {
    fail(scenarioName, `요소 접근 예외: ${e.message}`);
    await ctx.close();
    return;
  }

  if (expectDisabled) {
    // 시나리오 [3]: disabled === true, title에 "고객 계정만" 포함
    const titleOk = title.includes('고객 계정만');
    if (isDisabled && titleOk) {
      pass(scenarioName, `disabled=${isDisabled} / title="${title}"`);
    } else {
      const issues = [];
      if (!isDisabled) issues.push(`disabled 미설정 (actual: ${isDisabled})`);
      if (!titleOk)    issues.push(`title에 "고객 계정만" 미포함 (actual: "${title}")`);
      fail(scenarioName, issues.join(' | '));
    }
  } else {
    // 시나리오 [1][2]: disabled === false
    if (!isDisabled) {
      pass(scenarioName, `disabled=${isDisabled} / title="${title || '(없음)'}"`);
    } else {
      fail(scenarioName, `disabled가 true여선 안 됨 (actual: ${isDisabled}) / title: "${title}"`);
    }
  }

  await ctx.close();
}

async function run() {
  const browser = await chromium.launch({ headless: true });

  // ── 시나리오 1: 비로그인 ────────────────────────────────────────
  await runScenario(
    browser,
    '[1] 비로그인 — regBtn 유지',
    buildStub(
      { data: { user: null } },
      null
    ),
    false   // disabled === false 기대
  );

  // ── 시나리오 2: 로그인 고객(customer) ───────────────────────────
  await runScenario(
    browser,
    '[2] 로그인 고객(customer) — regBtn 활성',
    buildStub(
      { data: { user: { id: 'u1' } } },
      { data: { role: 'customer' }, error: null }
    ),
    false   // disabled === false 기대
  );

  // ── 시나리오 3: 로그인 비고객(accountant) ───────────────────────
  await runScenario(
    browser,
    '[3] 로그인 비고객(accountant) — regBtn 비활성',
    buildStub(
      { data: { user: { id: 'u2' } } },
      { data: { role: 'accountant' }, error: null }
    ),
    true    // disabled === true, title에 "고객 계정만" 포함 기대
  );

  await browser.close();

  // ── 결과 표 출력 ────────────────────────────────────────────────
  console.log('\n========== 역할 게이트 검증 결과 ==========\n');
  console.log('| 시나리오                                      | 결과 | disabled | title                                |');
  console.log('|-----------------------------------------------|------|----------|--------------------------------------|');
  for (const r of results) {
    const mark   = r.status === 'PASS' ? 'PASS' : 'FAIL';
    const d      = r.detail || '';
    const disM   = d.match(/disabled=(\S+)/);
    const disVal = disM ? disM[1].replace(',', '') : '-';
    const titM   = d.match(/title="([^"]*)"/);
    const titVal = titM ? (titM[1].slice(0, 34) || '(없음)') : '-';
    console.log(
      `| ${r.name.padEnd(45)} | ${mark} | ${disVal.padEnd(8)} | ${titVal.padEnd(36)} |`
    );
  }

  if (consoleErrors.length > 0) {
    console.log('\n========== 수집된 콘솔 에러 ==========');
    consoleErrors.forEach(e => console.log('  ' + e));
  } else {
    console.log('\n콘솔 에러: 없음');
  }

  const failCount = results.filter(r => r.status === 'FAIL').length;
  console.log(`\n총 ${results.length}건 — PASS: ${results.length - failCount} / FAIL: ${failCount}\n`);
  process.exit(failCount > 0 ? 1 : 0);
}

run().catch(e => {
  console.error('실행 오류:', e);
  process.exit(1);
});
