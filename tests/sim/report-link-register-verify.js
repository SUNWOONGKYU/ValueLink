/**
 * report-link-register-verify.js
 *
 * 평가보고서 "Link에 공개 등록" 버튼 Playwright 검증
 *
 * 검증 1: regBtn 렌더 확인
 * 검증 2: 샘플(템플릿) 상태에서 alert 가드 확인
 * 검증 3: 실데이터 + 비로그인 상태에서 confirm 로그인 게이트 확인
 */

const { chromium } = require('@playwright/test');
const path = require('path');

const FILE_URL = 'file:///C:/ValueLink/Valuation_Company/valuation-platform/frontend/app/valuation/report-auto.html';
const FILE_URL_DCF = FILE_URL + '?method=dcf';

// 결과 수집
const results = [];
const consoleErrors = [];

function pass(name, detail) {
  results.push({ name, status: 'PASS', detail });
  console.log(`[PASS] ${name}`);
  if (detail) console.log(`       ${detail}`);
}

function fail(name, detail) {
  results.push({ name, status: 'FAIL', detail });
  console.error(`[FAIL] ${name}`);
  if (detail) console.error(`       ${detail}`);
}

async function run() {
  const browser = await chromium.launch({ headless: true });

  // ─────────────────────────────────────────
  // 검증 1: regBtn 렌더
  // ─────────────────────────────────────────
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();

    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(`[V1] ${msg.text()}`);
    });

    await page.goto(FILE_URL_DCF, { waitUntil: 'domcontentloaded' });

    try {
      const btn = await page.$('#regBtn');
      if (!btn) {
        fail('검증 1: 버튼 렌더', 'id="regBtn" 요소가 존재하지 않음');
      } else {
        const txt = (await btn.innerText()).trim();
        if (txt.includes('Link에 공개 등록')) {
          pass('검증 1: 버튼 렌더', `버튼 텍스트: "${txt}"`);
        } else {
          fail('검증 1: 버튼 렌더', `버튼 텍스트에 "Link에 공개 등록" 미포함: "${txt}"`);
        }
      }
    } catch (e) {
      fail('검증 1: 버튼 렌더', `예외: ${e.message}`);
    }

    await ctx.close();
  }

  // ─────────────────────────────────────────
  // 검증 2: 샘플(템플릿) 가드 — alert 확인
  // ─────────────────────────────────────────
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();

    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(`[V2] ${msg.text()}`);
    });

    // localStorage 비어있는 상태 — 샘플 모드
    await page.goto(FILE_URL_DCF, { waitUntil: 'domcontentloaded' });

    // render() 완료 대기 (doc 콘텐츠 채워지길 기다림)
    await page.waitForSelector('#doc .cover', { timeout: 5000 }).catch(() => {});

    let dialogText = null;
    let dialogType = null;

    page.on('dialog', async dialog => {
      dialogType = dialog.type();
      dialogText = dialog.message();
      await dialog.dismiss(); // alert/confirm 모두 dismiss
    });

    try {
      await page.click('#regBtn');
      // dialog 이벤트가 동기적으로 발생하므로 짧게 대기
      await page.waitForTimeout(300);

      if (dialogType === null) {
        fail('검증 2: 샘플 가드', 'alert/dialog가 발생하지 않음');
      } else if (dialogText && dialogText.includes('예시(템플릿) 데이터는 공개 등록할 수 없습니다')) {
        pass('검증 2: 샘플 가드', `dialog 타입: ${dialogType}, 메시지: "${dialogText.slice(0, 80)}..."`);
      } else {
        fail('검증 2: 샘플 가드', `예상 문구 미포함. 실제 메시지: "${dialogText}"`);
      }
    } catch (e) {
      fail('검증 2: 샘플 가드', `예외: ${e.message}`);
    }

    await ctx.close();
  }

  // ─────────────────────────────────────────
  // 검증 3: 실데이터 + 비로그인 → 로그인 게이트 confirm
  // ─────────────────────────────────────────
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();

    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(`[V3] ${msg.text()}`);
    });

    // addInitScript: 페이지 로드 전 localStorage 에 실데이터 주입
    await ctx.addInitScript(() => {
      localStorage.setItem('vl_report_co_dcf', JSON.stringify({ name: '테스트컴퍼니' }));
    });

    await page.goto(FILE_URL_DCF, { waitUntil: 'domcontentloaded' });

    // render() 완료 대기
    await page.waitForSelector('#doc .cover', { timeout: 5000 }).catch(() => {});

    // localStorage 실제 반영 확인 (디버그)
    const stored = await page.evaluate(() => localStorage.getItem('vl_report_co_dcf'));
    console.log(`[V3] localStorage vl_report_co_dcf: ${stored}`);

    let dialogText = null;
    let dialogType = null;
    let navigationHappened = false;

    page.on('dialog', async dialog => {
      dialogType = dialog.type();
      dialogText = dialog.message();
      await dialog.dismiss(); // confirm → 취소 (login.html 이동 방지)
    });

    page.on('framenavigated', frame => {
      if (frame === page.mainFrame() && !frame.url().startsWith('file:///C:/ValueLink/Valuation_Company/valuation-platform/frontend/app/valuation/report-auto.html')) {
        navigationHappened = true;
        console.log(`[V3] 네비게이션 감지: ${frame.url()}`);
      }
    });

    try {
      await page.click('#regBtn');

      // supabase getUser는 네트워크 호출 → 최대 10초 대기
      const deadline = Date.now() + 10000;
      while (dialogText === null && Date.now() < deadline) {
        await page.waitForTimeout(300);
      }

      if (dialogText === null) {
        fail('검증 3: 로그인 게이트', '10초 내 dialog(confirm)가 발생하지 않음');
      } else {
        const hasLogin = dialogText.includes('로그인');
        const hasCustomer = dialogText.includes('고객');
        const noNavigation = !navigationHappened;

        if (hasLogin && hasCustomer && noNavigation && dialogType === 'confirm') {
          pass('검증 3: 로그인 게이트',
            `dialog 타입: ${dialogType} / 메시지: "${dialogText.slice(0, 100)}" / 페이지 이동 없음: ${noNavigation}`);
        } else {
          const issues = [];
          if (!hasLogin)    issues.push('"로그인" 단어 미포함');
          if (!hasCustomer) issues.push('"고객" 단어 미포함');
          if (dialogType !== 'confirm') issues.push(`dialog 타입이 confirm이 아님: ${dialogType}`);
          if (navigationHappened) issues.push('페이지 이동 발생 (confirm dismiss 실패)');
          fail('검증 3: 로그인 게이트',
            `이슈: ${issues.join(', ')} / 메시지: "${dialogText}"`);
        }
      }
    } catch (e) {
      fail('검증 3: 로그인 게이트', `예외: ${e.message}`);
    }

    await ctx.close();
  }

  await browser.close();

  // ─────────────────────────────────────────
  // 최종 보고
  // ─────────────────────────────────────────
  console.log('\n========== 검증 결과 ==========');
  for (const r of results) {
    const mark = r.status === 'PASS' ? 'PASS' : 'FAIL';
    console.log(`[${mark}] ${r.name}`);
    if (r.detail) console.log(`       ${r.detail}`);
  }

  if (consoleErrors.length > 0) {
    console.log('\n========== 콘솔 에러 ==========');
    consoleErrors.forEach(e => console.log(e));
  } else {
    console.log('\n[콘솔 에러] 없음');
  }

  const failCount = results.filter(r => r.status === 'FAIL').length;
  console.log(`\n총 ${results.length}건 중 FAIL: ${failCount}건`);
  process.exit(failCount > 0 ? 1 : 0);
}

run().catch(e => {
  console.error('실행 오류:', e);
  process.exit(1);
});
