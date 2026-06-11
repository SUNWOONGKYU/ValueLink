/**
 * @task S5T1 (수동 검증 보조)
 * @description 로그아웃 POST 폼 전환 검증 — ① 페이지 체류 중 세션 유지(프리페치 무해) ② 로그아웃 클릭 시 정상 로그아웃
 * 실행: node tests/check-logout-click.js
 */
const { chromium } = require('playwright')

const BASE = process.env.VERIFY_BASE_URL || 'https://valuelink-two.vercel.app'
const EMAIL = process.env.E2E_EMAIL || 'e2e-customer@valuelink.test'
const PASSWORD = process.env.E2E_PASSWORD || 'E2ETest123!@#'

const results = []
function record(step, pass, detail) {
  results.push({ step, pass, detail })
  console.log(`${pass ? '✅ PASS' : '❌ FAIL'} | ${step} | ${detail}`)
}

async function main() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  // 로그인
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' })
  await page.waitForSelector('#email', { timeout: 15000 })
  await page.fill('#email', EMAIL)
  await page.fill('input[type="password"]', PASSWORD)
  await page.click('button[type="submit"]')
  await page.waitForURL(/\/mypage\//, { timeout: 30000 })

  // ① 마이페이지에서 15초 체류(프리페치 발생 시간) 후 새로고침 — 세션 유지돼야 함
  await page.waitForTimeout(15000)
  await page.reload({ waitUntil: 'domcontentloaded' })
  try {
    await page.waitForSelector('text=프로젝트 현황', { timeout: 20000 })
    const onMypage = /\/mypage\//.test(page.url())
    record('L1 체류 후 세션 유지', onMypage, `15초 체류 + 새로고침 후 URL: ${page.url().split('?')[0]}`)
  } catch (e) {
    record('L1 체류 후 세션 유지', false, `URL: ${page.url()} — ${e.message.split('\n')[0]}`)
  }

  // ② 로그아웃 버튼 클릭 → /login 이동
  try {
    const logoutBtn = page
      .locator('form[action="/api/auth/logout"] button[type="submit"]')
      .filter({ visible: true })
      .first()
    await logoutBtn.waitFor({ timeout: 15000 })
    await logoutBtn.click()
    await page.waitForURL(/\/login/, { timeout: 20000 })
    record('L2 로그아웃 클릭', true, `최종 URL: ${page.url().split('?')[0]}`)
  } catch (e) {
    await page.screenshot({ path: 'tests/screenshots/logout-fail.png', fullPage: true }).catch(() => {})
    record('L2 로그아웃 클릭', false, `URL: ${page.url()} — ${e.message.split('\n')[0]}`)
  }

  // ③ 로그아웃 후 보호 페이지 접근 → /login 리다이렉트 (세션 실제 파괴 확인)
  try {
    await page.goto(`${BASE}/projects/list`, { waitUntil: 'domcontentloaded' })
    await page.waitForURL(/\/login/, { timeout: 20000 })
    record('L3 로그아웃 후 세션 파괴 확인', true, `보호 페이지 접근 → ${page.url().split('?')[0]}`)
  } catch (e) {
    record('L3 로그아웃 후 세션 파괴 확인', false, `URL: ${page.url()} — ${e.message.split('\n')[0]}`)
  }

  await browser.close()
  const passed = results.filter(r => r.pass).length
  console.log(`\n=== 결과: ${passed}/${results.length} PASS ===`)
  process.exit(passed === results.length ? 0 : 1)
}

main().catch(e => { console.error('FATAL:', e); process.exit(2) })
