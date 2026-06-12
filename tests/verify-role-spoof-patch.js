/**
 * localStorage 역할 위조 패치 검증
 * 공격 재현: 세션 없이 localStorage.userRole='admin' 설정 후 보호 페이지 접근
 * 기대: 2차 검증이 위조를 탐지 → access-denied 표시 + 콘텐츠 숨김 + userRole 제거
 * 대조군: 패치 전엔 콘텐츠가 그대로 노출됐음
 */
const { chromium } = require('@playwright/test');

const BASE = 'http://localhost:5500/Valuation_Company/valuation-platform/frontend/app/valuation';
const PAGES = [
  'accountant-review.html',
  'data-collection.html',
  'draft-generation.html',
  'final-preparation.html',
  'evaluation-progress.html',
];

(async () => {
  const browser = await chromium.launch();
  let fail = 0;

  for (const p of PAGES) {
    const context = await browser.newContext();
    const page = await context.newPage();
    const jsErrors = [];
    page.on('pageerror', (e) => jsErrors.push(e.message));

    // 1) 위조: 페이지 진입 전 localStorage 에 admin 심기
    await page.goto(`${BASE}/${p}`, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => localStorage.setItem('userRole', 'admin'));
    // 2) 재진입 (위조 상태로 게이트 통과 시도)
    await page.goto(`${BASE}/${p}`, { waitUntil: 'domcontentloaded' });
    // 2차 검증(Supabase 왕복) 대기
    await page.waitForTimeout(6000);

    const denied = await page
      .locator('#access-denied')
      .evaluate((el) => getComputedStyle(el).display !== 'none')
      .catch(() => false);
    const roleAfter = await page.evaluate(() => localStorage.getItem('userRole'));
    const syntaxErr = jsErrors.filter((m) => /SyntaxError|Unexpected/i.test(m));

    const pass = denied && roleAfter === null && syntaxErr.length === 0;
    if (!pass) fail++;
    console.log(
      `${pass ? '✅' : '❌'} ${p} — denied:${denied} userRole:${roleAfter === null ? 'cleared' : roleAfter} jsErr:${syntaxErr.length}`
    );
    syntaxErr.forEach((e) => console.log('    [JS] ' + e.slice(0, 160)));
    await context.close();
  }

  await browser.close();
  console.log(`\n결과: ${PAGES.length - fail}/${PAGES.length} PASS (위조 차단 기준)`);
  process.exit(fail ? 1 : 0);
})();
