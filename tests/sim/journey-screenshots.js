/**
 * 5개 가치평가 방식 — 전체 프로세스(0단계→보고서 산출) 화면 스크린샷 워크스루
 * 단계: 방법선택 → 가이드 → 포털 → 자료제출 → 계산폼(전) → 보고서산출(계산 후)
 * 실행: SIM_BASE=https://valuelink-platform.vercel.app node tests/sim/journey-screenshots.js
 *       (SIM_BASE 미지정 시 로컬 정적 서버)
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FRONTEND_ROOT = path.resolve(__dirname, '../../Valuation_Company/valuation-platform/frontend');
const PORT = 8139;
const LIVE = process.env.SIM_BASE; // 예: https://valuelink-platform.vercel.app
const ORIGIN = LIVE || `http://localhost:${PORT}`;
const OUT = path.join(__dirname, 'screenshots', 'journey');
const METHODS = ['dcf', 'tax', 'intrinsic', 'relative', 'asset'];

// 방법별 단계 경로 (origin 기준 상대경로)
const steps = (m) => [
  { n: 1, key: 'select', url: `/app/valuation.html`, calc: false, label: '방법 선택' },
  { n: 2, key: 'guide', url: `/app/valuation/guides/guide-${m}.html`, calc: false, label: '가이드' },
  { n: 3, key: 'portal', url: `/app/valuation/portals/${m}-portal.html`, calc: false, label: '포털' },
  { n: 4, key: 'submission', url: `/app/valuation/submissions/${m}-submission.html`, calc: false, label: '자료제출' },
  { n: 5, key: 'form', url: `/app/valuation/results/${m}-valuation.html`, calc: false, label: '계산 폼(입력)' },
  { n: 6, key: 'report', url: `/app/valuation/results/${m}-valuation.html`, calc: true, label: '보고서 산출(계산 후)' },
];

(async () => {
  let server = null;
  if (!LIVE) {
    server = spawn('node', [path.join(__dirname, '..', 'static-server.js'), FRONTEND_ROOT, String(PORT)], { stdio: 'ignore' });
    await new Promise((r) => setTimeout(r, 1200));
  }
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'] });
  const manifest = { origin: ORIGIN, timestamp: new Date().toISOString(), shots: [] };

  for (const m of METHODS) {
    const dir = path.join(OUT, m);
    fs.mkdirSync(dir, { recursive: true });
    console.log(`\n===== ${m.toUpperCase()} =====`);
    for (const s of steps(m)) {
      const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
      const errs = [];
      page.on('pageerror', (e) => errs.push('PAGEERROR: ' + e.message.split('\n')[0]));
      page.on('console', (e) => { if (e.type() === 'error') errs.push('CONSOLE: ' + e.text().slice(0, 120)); });
      page.on('dialog', (d) => d.dismiss().catch(() => {}));
      const file = path.join(dir, `${s.n}_${s.key}.png`);
      const rec = { method: m, step: s.n, key: s.key, label: s.label, url: ORIGIN + s.url, file, errors: errs, status: 'ok' };
      try {
        const resp = await page.goto(ORIGIN + s.url, { waitUntil: 'networkidle', timeout: 30000 });
        rec.http = resp ? resp.status() : 0;
        await page.waitForTimeout(900); // 헤더 fetch + 렌더
        if (s.calc) {
          const btn = await page.$('.btn-calculate');
          if (btn) { await btn.click().catch(() => {}); await page.waitForTimeout(900); }
          else rec.status = 'no-calc-button';
        }
        await page.screenshot({ path: file, fullPage: true });
      } catch (e) {
        rec.status = 'error'; rec.errors.push('EXC: ' + e.message.split('\n')[0]);
        try { await page.screenshot({ path: file, fullPage: true }); } catch (_) {}
      } finally {
        await page.close();
      }
      manifest.shots.push(rec);
      console.log(`  [${s.n}] ${s.label}  HTTP ${rec.http || '?'}  ${rec.errors.length ? '⚠ ' + rec.errors.length + ' err' : '✓'}  → ${path.relative(process.cwd(), file)}`);
    }
  }
  await browser.close();
  if (server) server.kill();
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf-8');
  console.log(`\n총 ${manifest.shots.length}컷 캡처 완료. manifest: ${path.join(OUT, 'manifest.json')}`);
})();
