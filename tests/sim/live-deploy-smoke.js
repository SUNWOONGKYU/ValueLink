/**
 * live-deploy-smoke.js
 *
 * 프로덕션 라이브 스모크 검증 — Playwright Chromium 헤드리스
 * 대상: https://valuelink-platform.vercel.app
 *
 * 검증 항목:
 *   [1] link.html — 테이블 렌더, escapeHtml 함수 존재, 회사명 링크 이동
 *   [2] report-auto.html?method=dcf — regBtn 노출, 샘플 가드 alert 동작
 *   [3] report-summary.html?company=<실제회사명> — safeUrl 존재, 렌더 확인
 *
 * 실행: node tests/sim/live-deploy-smoke.js
 */

'use strict';

const { chromium } = require('playwright');

const BASE = 'https://valuelink-platform.vercel.app';

// 결과 수집
const results = [];
const allConsoleErrors = [];

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

function info(msg) {
  console.log(`[INFO] ${msg}`);
}

// ─── 메인 ─────────────────────────────────────────────────────────────────────
async function run() {
  const browser = await chromium.launch({ headless: true });

  let firstCompanyEncoded = null; // [1]에서 [3]으로 전달

  // ═══════════════════════════════════════════════════════════════════════════
  // [1] link.html — 테이블 렌더 + escapeHtml 배포 반영 + 링크 이동
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    const consoleErrors = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
        allConsoleErrors.push(`[1-link] ${msg.text()}`);
      }
    });

    const url = `${BASE}/app/link.html`;
    info(`[1] GET ${url}`);

    try {
      const res = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      info(`[1] HTTP status: ${res ? res.status() : 'N/A'}`);

      // 1-A: "데이터 로드 실패" 미표시 확인 — 테이블 렌더까지 3초 대기
      await page.waitForTimeout(3000);

      const bodyText = await page.innerText('body');
      if (bodyText.includes('데이터 로드 실패')) {
        fail('[1-A] 데이터 로드 실패 미표시', `"데이터 로드 실패" 텍스트가 페이지에 노출됨`);
      } else {
        pass('[1-A] 데이터 로드 실패 미표시', '"데이터 로드 실패" 미포함 확인');
      }

      // 1-B: company-tbody 행 수 ≥ 1
      const rowCount = await page.$$eval('#company-tbody tr', rows => rows.length);
      info(`[1] company-tbody 행 수: ${rowCount}`);
      if (rowCount >= 1) {
        pass('[1-B] 테이블 행 수 ≥1', `행 수: ${rowCount}`);
      } else {
        fail('[1-B] 테이블 행 수 ≥1', `행 수: ${rowCount} (0이면 데이터 미로드 또는 Supabase 오류)`);
      }

      // 1-C: escapeHtml 함수 인라인 스크립트 존재 확인
      const html = await page.content();
      if (html.includes('function escapeHtml')) {
        pass('[1-C] escapeHtml 배포 반영', 'function escapeHtml 소스에 존재');
      } else {
        fail('[1-C] escapeHtml 배포 반영', 'function escapeHtml 소스에 미존재 — 배포 누락 가능');
      }

      // 1-D: 회사명 링크 클릭 → report-summary.html 이동 (404 아님)
      if (rowCount >= 1) {
        // 첫 번째 행의 .company-link href 추출
        const href = await page.$eval('#company-tbody tr:first-child .company-link', el => el.href)
          .catch(() => null);

        if (!href) {
          fail('[1-D] 회사명 링크 이동', '.company-link 요소를 찾을 수 없음');
        } else {
          info(`[1] company-link href: ${href}`);

          // URL에서 company 파라미터 추출 (나중에 [3]에서 사용)
          try {
            const u = new URL(href);
            firstCompanyEncoded = u.searchParams.get('company');
            info(`[1] 추출된 company 파라미터: ${firstCompanyEncoded}`);
          } catch (_) {}

          // 새 탭으로 이동해 404 여부 확인
          const summaryPage = await ctx.newPage();
          try {
            // networkidle 대기 + 추가 2초 — Supabase fetch 완료 후 DOM 반영 보장
            const summaryRes = await summaryPage.goto(href, { waitUntil: 'networkidle', timeout: 30000 });
            await summaryPage.waitForTimeout(2000);
            const status = summaryRes ? summaryRes.status() : 0;
            const title = await summaryPage.title();
            info(`[1] report-summary 이동 status: ${status}, title: ${title}`);

            if (status === 404) {
              fail('[1-D] 회사명 링크 이동', `404 응답 — href: ${href}`);
            } else {
              // 회사 제목 렌더 확인 (Supabase fetch 완료 후 기준 200자)
              const summaryBody = await summaryPage.innerText('body');
              info(`[1] report-summary body 길이: ${summaryBody.length}`);
              if (summaryBody.length > 200) {
                pass('[1-D] 회사명 링크 이동', `status ${status}, body ${summaryBody.length}자, title: "${title}"`);
              } else {
                fail('[1-D] 회사명 링크 이동', `페이지 본문이 너무 짧음 (${summaryBody.length}자) — Supabase 로드 실패 가능`);
              }
            }
          } catch (e) {
            fail('[1-D] 회사명 링크 이동', `이동 중 예외: ${e.message}`);
          } finally {
            await summaryPage.close();
          }
        }
      } else {
        fail('[1-D] 회사명 링크 이동', '테이블 행이 없어 클릭 불가');
      }

      // 1-E: 콘솔 에러 보고 (치명 여부와 관계없이 기록)
      if (consoleErrors.length === 0) {
        pass('[1-E] 콘솔 에러 없음', '콘솔 에러 0건');
      } else {
        // 헤더 fetch 에러 여부 별도 구분
        const headerFetchErr = consoleErrors.filter(e => /header\.html|fetch/i.test(e));
        if (headerFetchErr.length > 0) {
          fail('[1-E] 헤더 fetch 에러', headerFetchErr.join(' | '));
        } else {
          fail('[1-E] 콘솔 에러 없음', `에러 ${consoleErrors.length}건: ${consoleErrors.slice(0, 3).join(' | ')}`);
        }
      }

    } catch (e) {
      fail('[1] link.html 접근', `예외: ${e.message}`);
    }

    await ctx.close();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // [2] report-auto.html?method=dcf — regBtn 노출 + 샘플 가드 alert
  // ═══════════════════════════════════════════════════════════════════════════
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    const consoleErrors = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
        allConsoleErrors.push(`[2-report-auto] ${msg.text()}`);
      }
    });

    const url = `${BASE}/app/valuation/report-auto.html?method=dcf`;
    info(`[2] GET ${url}`);

    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2000);

      // 2-A: regBtn 존재 확인
      const btn = await page.$('#regBtn');
      if (!btn) {
        fail('[2-A] regBtn 존재', 'id="regBtn" 요소 없음');
      } else {
        const txt = (await btn.innerText()).trim();
        if (txt.includes('Link에 공개 등록')) {
          pass('[2-A] regBtn 존재', `버튼 텍스트: "${txt}"`);
        } else {
          fail('[2-A] regBtn 존재', `버튼 텍스트에 "Link에 공개 등록" 미포함: "${txt}"`);
        }
      }

      // 2-B: 샘플 가드 alert 동작 확인
      if (btn) {
        let alertMsg = null;

        // dialog 이벤트 핸들러 등록 후 버튼 클릭
        page.once('dialog', async dialog => {
          alertMsg = dialog.message();
          info(`[2] dialog 수신: "${alertMsg}"`);
          await dialog.dismiss();
        });

        await btn.click();
        // dialog 처리 대기
        await page.waitForTimeout(1500);

        if (alertMsg === null) {
          fail('[2-B] 샘플 가드 alert', 'alert dialog 가 발생하지 않음 (샘플 가드 미동작)');
        } else if (alertMsg.includes('예시(템플릿) 데이터는 공개 등록할 수 없습니다')) {
          pass('[2-B] 샘플 가드 alert', `alert 내용 확인: "${alertMsg.substring(0, 60)}..."`);
        } else {
          fail('[2-B] 샘플 가드 alert', `alert 메시지가 예상과 다름: "${alertMsg}"`);
        }
      } else {
        fail('[2-B] 샘플 가드 alert', 'regBtn 없어서 클릭 불가');
      }

      // 2-C: 콘솔 에러 보고
      if (consoleErrors.length === 0) {
        pass('[2-C] 콘솔 에러 없음', '콘솔 에러 0건');
      } else {
        fail('[2-C] 콘솔 에러 없음', `에러 ${consoleErrors.length}건: ${consoleErrors.slice(0, 3).join(' | ')}`);
      }

    } catch (e) {
      fail('[2] report-auto.html 접근', `예외: ${e.message}`);
    }

    await ctx.close();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // [3] report-summary.html?company=<실제회사명> — safeUrl 존재 + 렌더
  // ═══════════════════════════════════════════════════════════════════════════
  {
    // [1]에서 얻은 회사명 사용; 없으면 폴백
    const companyParam = firstCompanyEncoded || encodeURIComponent('엔키노');
    const url = `${BASE}/app/report-summary.html?company=${companyParam}`;

    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    const consoleErrors = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
        allConsoleErrors.push(`[3-report-summary] ${msg.text()}`);
      }
    });

    info(`[3] GET ${url}`);

    try {
      const res = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      const status = res ? res.status() : 0;
      info(`[3] HTTP status: ${status}`);
      await page.waitForTimeout(2000);

      // 3-A: 404 아님
      if (status === 404) {
        fail('[3-A] 페이지 404 아님', `HTTP 404 — URL: ${url}`);
      } else {
        pass('[3-A] 페이지 404 아님', `HTTP ${status}`);
      }

      // 3-B: safeUrl 함수 소스 존재 (배포 반영)
      const html = await page.content();
      if (html.includes('function safeUrl')) {
        pass('[3-B] safeUrl 배포 반영', 'function safeUrl 소스에 존재');
      } else {
        fail('[3-B] safeUrl 배포 반영', 'function safeUrl 소스에 미존재 — 배포 누락 가능');
      }

      // 3-C: javascript: href 없음 (XSS 가드)
      const jsHrefCount = await page.$$eval('a[href]', links =>
        links.filter(a => a.getAttribute('href').toLowerCase().startsWith('javascript:')).length
      );
      if (jsHrefCount === 0) {
        pass('[3-C] javascript: href 없음', `javascript: href 0건`);
      } else {
        fail('[3-C] javascript: href 없음', `javascript: href ${jsHrefCount}건 발견`);
      }

      // 3-D: 페이지 본문 렌더 확인 (회사 제목/요약 영역)
      const bodyText = await page.innerText('body');
      const hasContent = bodyText.length > 200;
      if (hasContent) {
        pass('[3-D] 본문 렌더', `body 텍스트 ${bodyText.length}자 이상 렌더됨`);
      } else {
        fail('[3-D] 본문 렌더', `body 텍스트가 너무 짧음 (${bodyText.length}자)`);
      }

      // 3-E: 콘솔 에러 보고
      if (consoleErrors.length === 0) {
        pass('[3-E] 콘솔 에러 없음', '콘솔 에러 0건');
      } else {
        const headerFetchErr = consoleErrors.filter(e => /header\.html|fetch/i.test(e));
        if (headerFetchErr.length > 0) {
          fail('[3-E] 헤더 fetch 에러', headerFetchErr.join(' | '));
        } else {
          fail('[3-E] 콘솔 에러 없음', `에러 ${consoleErrors.length}건: ${consoleErrors.slice(0, 3).join(' | ')}`);
        }
      }

    } catch (e) {
      fail('[3] report-summary.html 접근', `예외: ${e.message}`);
    }

    await ctx.close();
  }

  await browser.close();

  // ─── 최종 요약 출력 ─────────────────────────────────────────────────────────
  console.log('\n' + '═'.repeat(70));
  console.log('  LIVE SMOKE TEST 결과 요약');
  console.log('═'.repeat(70));

  const passCount = results.filter(r => r.status === 'PASS').length;
  const failCount = results.filter(r => r.status === 'FAIL').length;

  // 항목별 테이블 출력
  const namePad = 40;
  console.log(`\n${'항목'.padEnd(namePad)} 결과`);
  console.log('─'.repeat(55));
  for (const r of results) {
    const icon = r.status === 'PASS' ? 'PASS' : 'FAIL';
    console.log(`${r.name.padEnd(namePad)} [${icon}]`);
    if (r.detail) console.log(`  ${r.detail}`);
  }

  console.log('─'.repeat(55));
  console.log(`\n총 ${results.length}건 | PASS ${passCount} | FAIL ${failCount}`);

  if (allConsoleErrors.length > 0) {
    console.log('\n[수집된 전체 콘솔 에러]');
    for (const e of allConsoleErrors) console.log(`  ${e}`);
  } else {
    console.log('\n콘솔 에러: 0건');
  }

  console.log('\n' + '═'.repeat(70));

  // 최종 결론
  if (failCount === 0) {
    console.log('결론: 전항목 PASS — 배포 이상 없음');
  } else {
    console.log(`결론: FAIL ${failCount}건 — 상세 내용 확인 필요`);
    process.exitCode = 1;
  }
}

run().catch(err => {
  console.error('[FATAL]', err);
  process.exit(1);
});
