/**
 * 정상 경로 회귀 확인 — 실제 세션 보유한 accountant/admin은 보호 페이지 접근 유지돼야 함
 * 절차: e2e 계정으로 signInWithPassword → localStorage.userRole 설정 → 보호 페이지 진입
 * 기대: access-denied 미표시, userRole 유지
 */
const { chromium } = require('@playwright/test');

const APP = 'http://localhost:5500/Valuation_Company/valuation-platform/frontend/app';
const SUPABASE_URL = 'https://arxrfetgaitkgiiqabap.supabase.co';
const ANON_KEY =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0';

const CASES = [
  { email: 'e2e-admin@valuelink.test', role: 'admin', page: 'valuation/accountant-review.html' },
  { email: 'e2e-accountant@valuelink.test', role: 'accountant', page: 'valuation/data-collection.html' },
  { email: 'e2e-admin@valuelink.test', role: 'admin', page: 'valuation/final-preparation.html' },
];
const PASSWORD = 'E2ETest123!@#';

(async () => {
  const browser = await chromium.launch();
  let fail = 0;

  for (const c of CASES) {
    const context = await browser.newContext();
    const page = await context.newPage();

    // login.html 로드 (supabase UMD 사용 가능)
    await page.goto(`${APP}/login.html`, { waitUntil: 'domcontentloaded' });
    const loginResult = await page.evaluate(
      async ({ url, key, email, password }) => {
        const client = window.supabase.createClient(url, key);
        const { data, error } = await client.auth.signInWithPassword({ email, password });
        return { ok: !!data?.session, error: error?.message || null };
      },
      { url: SUPABASE_URL, key: ANON_KEY, email: c.email, password: PASSWORD }
    );
    if (!loginResult.ok) {
      console.log(`❌ ${c.page} — 로그인 실패(${c.email}): ${loginResult.error}`);
      fail++;
      await context.close();
      continue;
    }

    await page.evaluate((role) => localStorage.setItem('userRole', role), c.role);
    await page.goto(`${APP}/${c.page}`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(6000); // 2차 검증 왕복 대기

    const denied = await page
      .locator('#access-denied')
      .evaluate((el) => getComputedStyle(el).display !== 'none')
      .catch(() => false);
    const roleAfter = await page.evaluate(() => localStorage.getItem('userRole'));

    const pass = !denied && roleAfter === c.role;
    if (!pass) fail++;
    console.log(`${pass ? '✅' : '❌'} ${c.page} (${c.role}) — denied:${denied} userRole:${roleAfter}`);
    await context.close();
  }

  await browser.close();
  console.log(`\n결과: ${CASES.length - fail}/${CASES.length} PASS (정상 접근 유지 기준)`);
  process.exit(fail ? 1 : 0);
})();
