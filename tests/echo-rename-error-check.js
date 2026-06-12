/**
 * Echo — supabase→supabaseClient 리네임 런타임 검증
 * 수정된 22개 HTML 전체를 로드해 JS 에러(특히 ReferenceError: supabase…)를 수집.
 * 판정: 식별자 관련 에러 0건이면 PASS.
 */
const { chromium } = require('@playwright/test');

const BASE = 'http://localhost:5500/Valuation_Company/valuation-platform/frontend/app';
const PAGES = [
  '/accountant-profile.html',
  '/core/mypage-admin.html',
  '/core/mypage-investor.html',
  '/core/mypage-partner.html',
  '/core/mypage-supporter.html',
  '/core/mypage.html',
  '/core/valuation-list.html',
  '/login.html',
  '/projects/project-create.html',
  '/projects/project-detail.html',
  '/projects/valuation-list.html',
  '/register.html',
  '/valuation/final-preparation.html',
  '/valuation/report-download.html',
  '/valuation/report-draft.html',
  '/valuation/report-final.html',
  '/valuation/revision-request.html',
  '/valuation/submissions/asset-submission.html',
  '/valuation/submissions/dcf-submission.html',
  '/valuation/submissions/intrinsic-submission.html',
  '/valuation/submissions/relative-submission.html',
  '/valuation/submissions/tax-submission.html',
];

(async () => {
  const browser = await chromium.launch();
  const results = [];

  for (const p of PAGES) {
    const page = await browser.newPage();
    const pageErrors = [];
    const consoleErrors = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('console', (m) => {
      if (m.type() === 'error') consoleErrors.push(m.text());
    });

    let finalUrl = '';
    try {
      await page.goto(BASE + p, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2500); // 스크립트 실행/리다이렉트 대기
      finalUrl = page.url();
    } catch (e) {
      pageErrors.push('NAVIGATION: ' + e.message);
    }

    // 식별자 에러(리네임 회귀)만 골라냄
    const identifierErrors = pageErrors.filter((m) =>
      /ReferenceError|is not defined|is not a function|Cannot read|Identifier .* has already been declared/i.test(m)
    );
    // 네트워크/외부 API 에러는 무시 (정적 검증 범위 밖)
    const supabaseRefErrors = [...pageErrors, ...consoleErrors].filter((m) =>
      /supabase(Client)? is not defined|supabase\b.*not a function/i.test(m)
    );

    results.push({
      page: p,
      redirected: finalUrl && !finalUrl.includes(p.split('/').pop()) ? finalUrl : null,
      identifierErrors,
      supabaseRefErrors,
      allPageErrors: pageErrors,
    });
    await page.close();
  }

  await browser.close();

  let fail = 0;
  for (const r of results) {
    const bad = r.identifierErrors.length + r.supabaseRefErrors.length;
    const mark = bad ? '❌' : '✅';
    if (bad) fail++;
    console.log(`${mark} ${r.page}${r.redirected ? '  → redirect: ' + r.redirected.replace(/^.*\/app/, '') : ''}`);
    r.identifierErrors.forEach((e) => console.log('    [ID-ERR] ' + e));
    r.supabaseRefErrors.forEach((e) => console.log('    [SB-ERR] ' + e));
    if (!bad && r.allPageErrors.length)
      r.allPageErrors.forEach((e) => console.log('    [info, non-blocking] ' + e.slice(0, 140)));
  }
  console.log(`\n결과: ${results.length - fail}/${results.length} PASS (식별자/supabase 참조 에러 기준)`);
  process.exit(fail ? 1 : 0);
})();
