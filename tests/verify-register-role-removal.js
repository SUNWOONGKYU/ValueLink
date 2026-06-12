/**
 * 백호 Phase 5 후속 — register.html 회계사/관리자 역할 선택지 제거 실브라우저 검증
 * 판정: ① 역할 카드 4개(고객/투자자/제휴자/서포터)만 존재 ② accountant/admin 라디오 없음
 *       ③ 고객 선택 → 다음 단계 이동 정상 ④ JS 페이지 에러 0건
 */
const { chromium } = require('@playwright/test');

const URL = 'http://localhost:5500/Valuation_Company/valuation-platform/frontend/app/register.html';

let pass = 0, fail = 0;
function check(name, ok, detail) {
  console.log(`${ok ? '✅ PASS' : '❌ FAIL'} | ${name}${detail ? ' — ' + detail : ''}`);
  ok ? pass++ : fail++;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', (e) => pageErrors.push(e.message));

  await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(1500);

  const radios = await page.$$eval('input[name="role"]', els => els.map(e => e.value));
  check('역할 라디오 4개만 존재', radios.length === 4, `values=[${radios.join(', ')}]`);
  check('accountant 선택지 제거됨', !radios.includes('accountant'));
  check('admin 선택지 제거됨', !radios.includes('admin'));
  check('잔존 역할 = customer/investor/partner/supporter',
    ['customer', 'investor', 'partner', 'supporter'].every(r => radios.includes(r)));

  // Step1 채우고 Step2 진입 → 고객 선택 → Step3 이동
  await page.fill('#userName', 'RLS검증');
  await page.fill('#userEmail', 'rls-ui-test@test.invalid');
  await page.fill('#userPassword', 'Test1234!@#');
  await page.fill('#userPasswordConfirm', 'Test1234!@#');
  await page.click('button:has-text("다음 단계")');
  await page.waitForTimeout(300);
  const step2Visible = await page.$eval('#step2', el => getComputedStyle(el).display !== 'none').catch(() => false);
  check('Step2(역할 선택) 진입', step2Visible);

  await page.click('label[for="roleCustomer"]'); // input은 카드 UI로 숨겨져 있어 label 클릭
  await page.click('#step2 button:has-text("다음 단계")');
  await page.waitForTimeout(300);
  const step3Visible = await page.$eval('#step3', el => getComputedStyle(el).display !== 'none').catch(() => false);
  const customerFieldsVisible = await page.$eval('#customerFields', el => getComputedStyle(el).display !== 'none').catch(() => false);
  check('고객 선택 → Step3 진입 + 고객 필드 표시', step3Visible && customerFieldsVisible, `step3=${step3Visible}, customerFields=${customerFieldsVisible}`);

  check('JS 페이지 에러 0건', pageErrors.length === 0, pageErrors.slice(0, 3).join(' | ') || '에러 없음');

  await browser.close();
  console.log(`\n=== 결과: ${pass} PASS / ${fail} FAIL ===`);
  process.exit(fail > 0 ? 1 : 0);
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
