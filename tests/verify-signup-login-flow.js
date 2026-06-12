/**
 * 가입/로그인 수정 — 실브라우저 E2E 검증 (Playwright)
 * 플로우: register.html 가입 → "확인 메일" 안내 + 보류 프로필 저장 → (메일 링크 클릭을 admin API로 재현)
 *        → login.html 로그인 → 보류 프로필 DB 저장 → mypage 리다이렉트
 */
const { chromium } = require('@playwright/test');
const fs = require('fs');
const os = require('os');
const path = require('path');

const BASE = 'http://localhost:5500/Valuation_Company/valuation-platform/frontend/app';
const REF = 'arxrfetgaitkgiiqabap';
const SB = `https://${REF}.supabase.co`;
const SERVICE = fs.readFileSync(path.join(os.tmpdir(), 'sb_service.txt'), 'utf-8').trim();
const PAT = fs.readFileSync(path.join(os.tmpdir(), 'sb_token.txt'), 'utf-8').trim();

let pass = 0, fail = 0;
function check(name, ok, detail) {
  console.log(`${ok ? '✅ PASS' : '❌ FAIL'} | ${name}${detail ? ' — ' + detail : ''}`);
  ok ? pass++ : fail++;
}

async function mgmt(sql) {
  const res = await fetch(`https://api.supabase.com/v1/projects/${REF}/database/query`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${PAT}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: sql }),
  });
  return res.json();
}

(async () => {
  const stamp = Date.now();
  const email = `wksun999+vlui${stamp}@gmail.com`;
  const password = 'UiFlow123!@#';

  const browser = await chromium.launch();
  const page = await browser.newPage();
  const pageErrors = [];
  const dialogs = [];
  page.on('pageerror', (e) => pageErrors.push(e.message));
  page.on('dialog', async (d) => { dialogs.push(d.message()); await d.accept(); });

  // ===== 1) register.html — 가입 =====
  await page.goto(`${BASE}/register.html`, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(1000);

  await page.fill('#userName', 'UI플로우검증');
  await page.fill('#userEmail', email);
  await page.fill('#userPassword', password);
  await page.fill('#userPasswordConfirm', password);
  await page.click('button:has-text("다음 단계")');
  await page.waitForTimeout(300);
  await page.click('label[for="roleCustomer"]');
  await page.click('#step2 button:has-text("다음 단계")');
  await page.waitForTimeout(300);

  await page.fill('#companyName', 'UI검증주식회사');
  await page.fill('#companyNameEn', 'UI Verify Inc.');
  await page.fill('#businessNumber', '333-33-33333');
  await page.fill('#ceoName', 'UI대표');

  // 가입 제출 (버튼 텍스트는 페이지에 따라 다를 수 있어 step3의 마지막 제출 버튼 탐색)
  await page.click('#step3 button[onclick*="submitRegistration"], #step3 button:has-text("가입"), #step3 button:has-text("완료")');
  await page.waitForTimeout(4000);

  check('1. 가입 제출 → "확인 메일" 안내 표시', dialogs.some(d => d.includes('확인 메일')), dialogs.slice(-1)[0] || '다이얼로그 없음');
  check('2. login.html로 이동', page.url().includes('login.html'), page.url());

  const pendingRaw = await page.evaluate(() => localStorage.getItem('vl_pending_profile'));
  let pending = null;
  try { pending = JSON.parse(pendingRaw); } catch {}
  check('3. 보류 프로필 localStorage 저장', !!pending && pending.email === email && pending.customer?.company_name === 'UI검증주식회사', pendingRaw ? `role=${pending?.role}, company=${pending?.customer?.company_name}` : '없음');

  // ===== 2) 메일 링크 클릭 재현 (admin API로 이메일 확인 처리) =====
  const lookup = await mgmt(`SELECT id FROM auth.users WHERE email = '${email}'`);
  const userId = Array.isArray(lookup) ? lookup[0]?.id : null;
  let confirmed = false;
  if (userId) {
    const res = await fetch(`${SB}/auth/v1/admin/users/${userId}`, {
      method: 'PUT',
      headers: { apikey: SERVICE, Authorization: `Bearer ${SERVICE}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ email_confirm: true }),
    });
    confirmed = res.ok;
  }
  check('4. 이메일 확인 처리 (메일 링크 클릭 재현)', confirmed, `userId=${userId || '조회 실패'}`);

  // ===== 3) login.html — 첫 로그인 → 보류 프로필 저장 =====
  await page.fill('#email', email);
  await page.fill('#password', password);
  await page.click('#loginBtn');
  await page.waitForTimeout(5000);

  check('5. 로그인 후 mypage 리다이렉트', page.url().includes('mypage'), page.url());

  // ===== 4) DB 확인 =====
  const userRow = await mgmt(`SELECT role, name, is_active FROM users WHERE email = '${email}'`);
  check('6. users 행 생성 (role=customer)', Array.isArray(userRow) && userRow[0]?.role === 'customer' && userRow[0]?.is_active === true, JSON.stringify(userRow?.[0] || {}));

  const custRow = await mgmt(`SELECT company_name, company_name_en, business_number FROM customers WHERE email = '${email}'`);
  check('7. customers 행 생성 (회사 정보 저장됨) ⭐핵심', Array.isArray(custRow) && custRow[0]?.company_name === 'UI검증주식회사' && custRow[0]?.company_name_en === 'UI Verify Inc.', JSON.stringify(custRow?.[0] || {}));

  const pendingAfter = await page.evaluate(() => localStorage.getItem('vl_pending_profile'));
  check('8. 보류 프로필 정리됨', pendingAfter === null, pendingAfter ? '잔존' : '정리 완료');

  check('9. JS 페이지 에러 0건', pageErrors.length === 0, pageErrors.slice(0, 3).join(' | ') || '에러 없음');

  await browser.close();

  // 정리
  await mgmt(`DELETE FROM customers WHERE email = '${email}'`);
  await mgmt(`DELETE FROM users WHERE email = '${email}'`);
  await mgmt(`DELETE FROM auth.users WHERE email = '${email}'`);
  console.log('   (테스트 계정/데이터 정리 완료)');

  console.log(`\n=== 결과: ${pass} PASS / ${fail} FAIL ===`);
  process.exit(fail > 0 ? 1 : 0);
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
