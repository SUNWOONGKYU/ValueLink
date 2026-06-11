/**
 * @task S5T1 (수동 검증 보조)
 * @description 실브라우저 사용자 여정 클릭 검증 — 데드링크 작전 마무리 검증용
 *   여정: 미인증 /projects/list 리다이렉트 → 로그인 → 마이페이지 → 프로젝트 목록 → 상세 → "프로세스 진행" 클릭
 * 실행: node tests/user-journey-verify.js
 * 환경변수: VERIFY_BASE_URL, VERCEL_BYPASS_TOKEN, E2E_EMAIL, E2E_PASSWORD
 */
const { chromium } = require('playwright')

const BASE = process.env.VERIFY_BASE_URL || 'https://valuelink-mxtnqrtxx-finder-world.vercel.app'
const BYPASS = process.env.VERCEL_BYPASS_TOKEN || ''
const EMAIL = process.env.E2E_EMAIL || 'e2e-customer@valuelink.test'
const PASSWORD = process.env.E2E_PASSWORD || 'E2ETest123!@#'

const results = []
function record(step, pass, detail) {
  results.push({ step, pass, detail })
  console.log(`${pass ? '✅ PASS' : '❌ FAIL'} | ${step} | ${detail}`)
}

function bypassUrl(path) {
  const sep = path.includes('?') ? '&' : '?'
  return `${BASE}${path}${BYPASS ? `${sep}x-vercel-protection-bypass=${BYPASS}&x-vercel-set-bypass-cookie=true` : ''}`
}

async function main() {
  const browser = await chromium.launch({ headless: true })

  // ---- Journey 0: 미인증 /projects/list → /login 리다이렉트 (커밋 973702d 검증) ----
  {
    const ctx = await browser.newContext()
    const page = await ctx.newPage()
    try {
      await page.goto(bypassUrl('/projects/list'), { waitUntil: 'domcontentloaded', timeout: 30000 })
      await page.waitForURL(/\/login/, { timeout: 15000 })
      record('J0 미인증 리다이렉트', true, `최종 URL: ${page.url().split('?')[0]}`)
    } catch (e) {
      await page.screenshot({ path: 'tests/screenshots/j0-fail.png', fullPage: true }).catch(() => {})
      record('J0 미인증 리다이렉트', false, `현재 URL: ${page.url()} — ${e.message.split('\n')[0]}`)
    }
    await ctx.close()
  }

  // ---- Journey 1~5: 로그인 → 마이페이지 → 목록 → 상세 → 프로세스 진행 ----
  const ctx = await browser.newContext()
  const page = await ctx.newPage()

  // J1: 로그인 페이지 렌더 + 로그인
  try {
    await page.goto(bypassUrl('/login'), { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.waitForSelector('#email', { timeout: 15000 })
    await page.fill('#email', EMAIL)
    await page.fill('input[type="password"]', PASSWORD)
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/mypage\//, { timeout: 30000 })
    record('J1 로그인 → 마이페이지', true, `최종 URL: ${page.url().split('?')[0]}`)
  } catch (e) {
    await page.screenshot({ path: 'tests/screenshots/j1-fail.png', fullPage: true }).catch(() => {})
    record('J1 로그인 → 마이페이지', false, `현재 URL: ${page.url()} — ${e.message.split('\n')[0]}`)
    await finish(browser)
    return
  }

  // J2: 마이페이지에서 프로젝트 목록 진입 (링크 클릭 우선, 없으면 직접 이동)
  // 주의: 클라이언트 렌더링이라 hydration 대기 필수 + 반응형 중복 nav 중 '보이는' 링크만 클릭
  try {
    const visibleListLink = page
      .locator('a[href*="/projects/list"], a[href="/projects"]')
      .filter({ visible: true })
      .first()
    const found = await visibleListLink
      .waitFor({ timeout: 15000 })
      .then(() => true)
      .catch(() => false)
    if (found) {
      const text = (await visibleListLink.textContent() || '').trim()
      await visibleListLink.click()
      await page.waitForURL(/\/projects/, { timeout: 15000 })
      record('J2 프로젝트 목록 진입', true, `링크("${text}") 클릭으로 이동: ${page.url().split('?')[0]}`)
    } else {
      await page.goto(bypassUrl('/projects/list'), { waitUntil: 'domcontentloaded', timeout: 30000 })
      record('J2 프로젝트 목록 진입', true, `마이페이지에 목록 링크 없음 → 직접 이동: ${page.url().split('?')[0]}`)
    }
  } catch (e) {
    await page.screenshot({ path: 'tests/screenshots/j2-fail.png', fullPage: true }).catch(() => {})
    record('J2 프로젝트 목록 진입', false, e.message.split('\n')[0])
  }

  // J3: 목록에서 프로젝트 상세 진입
  let detailReached = false
  try {
    // 클라이언트 네비게이션 직후 목록 데이터 fetch가 진행 중일 수 있음 — 보이는 링크를 명시적으로 대기
    const detailLink = page
      .locator('a[href^="/projects/"]:not([href*="list"]):not([href*="create"])')
      .filter({ visible: true })
      .first()
    const projectCard = page.locator('text=E2E 검증용 테스트기업').first()
    const detailFound = await detailLink
      .waitFor({ timeout: 20000 })
      .then(() => true)
      .catch(() => false)
    if (detailFound) {
      const href = await detailLink.getAttribute('href')
      await detailLink.click()
      await page.waitForURL(/\/projects\/(?!list$|create$)[^/]+$/, { timeout: 20000 })
      detailReached = true
      record('J3 프로젝트 상세 진입', true, `클릭한 링크: ${href}`)
    } else if (await projectCard.count() > 0) {
      // 카드가 <a>가 아닌 onClick(router.push) 방식 — 카드 클릭으로 진입
      await projectCard.click()
      await page.waitForURL(/\/projects\/(?!list$|create$)[^/]+$/, { timeout: 20000 })
      detailReached = true
      record('J3 프로젝트 상세 진입', true, `onClick 카드 클릭으로 이동: ${page.url().split('?')[0]}`)
    } else {
      const bodyText = (await page.textContent('body')) || ''
      record('J3 프로젝트 상세 진입', false, `목록에 프로젝트 링크 없음 (본문 일부: ${bodyText.replace(/\s+/g, ' ').slice(0, 120)})`)
    }
  } catch (e) {
    await page.screenshot({ path: 'tests/screenshots/j3-fail.png', fullPage: true }).catch(() => {})
    record('J3 프로젝트 상세 진입', false, e.message.split('\n')[0])
  }

  // J4: 상세 페이지에서 "프로세스 진행" 클릭 → step 경로 검증 (클램프 1~12 검증)
  if (detailReached) {
    try {
      await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {})
      // QuickActionButton은 <button> + router.push(href) 방식 — DOM에 href 속성 없음
      const processBtn = page.locator('a:has-text("프로세스 진행"), button:has-text("프로세스 진행")').first()
      await processBtn.waitFor({ timeout: 15000 })
      await processBtn.click()
      await page.waitForURL(/\/valuation\/process\/step-\d+/, { timeout: 20000 })
      const stepMatch = page.url().match(/step-(\d+)/)
      const stepNum = stepMatch ? parseInt(stepMatch[1], 10) : null
      const clampOk = stepNum !== null && stepNum >= 1 && stepNum <= 12
      const notFound = await page.locator('text=/404|not found|찾을 수 없/i').count()
      record('J4 프로세스 진행 클릭', notFound === 0 && clampOk,
        `step=${stepNum} (클램프 1~12: ${clampOk ? 'OK' : 'VIOLATION'}), 404표시: ${notFound > 0 ? '있음' : '없음'}, 최종: ${page.url().split('?')[0]}`)
    } catch (e) {
      await page.screenshot({ path: 'tests/screenshots/j4-fail.png', fullPage: true }).catch(() => {})
      record('J4 프로세스 진행 클릭', false, e.message.split('\n')[0])
    }
  } else {
    record('J4 프로세스 진행 클릭', false, 'J3 실패로 스킵')
  }

  await finish(browser)
}

async function finish(browser) {
  await browser.close()
  const passed = results.filter(r => r.pass).length
  console.log(`\n=== 결과: ${passed}/${results.length} PASS ===`)
  console.log(JSON.stringify(results, null, 2))
  process.exit(passed === results.length ? 0 : 1)
}

main().catch(e => { console.error('FATAL:', e); process.exit(2) })
