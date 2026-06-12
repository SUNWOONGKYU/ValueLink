// 백호 작전 Phase 5 — RLS 실행 전 실제 DB 상태 점검 (읽기 전용, Management API)
const fs = require('fs');
const os = require('os');
const path = require('path');

const PAT = fs.readFileSync(path.join(os.tmpdir(), 'sb_token.txt'), 'utf-8').trim();
const REF = 'arxrfetgaitkgiiqabap';

async function q(sql) {
  const res = await fetch(`https://api.supabase.com/v1/projects/${REF}/database/query`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${PAT}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: sql }),
  });
  const body = await res.json();
  if (!res.ok) throw new Error(`${res.status}: ${JSON.stringify(body).slice(0, 300)}`);
  return body;
}

const TABLES = ['users','customers','projects','accountants','report_draft_sections','draft_method_status','balance_payments','revision_requests','report_delivery_requests','newsletter_subscribers','quotes','negotiations','documents','approval_points','drafts','revisions','reports','valuation_reports'];

(async () => {
  // 1. 테이블 존재 + RLS 상태
  const rls = await q(`SELECT c.relname AS t, c.relrowsecurity AS rls FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' AND c.relname IN (${TABLES.map(t=>`'${t}'`).join(',')}) ORDER BY 1`);
  console.log('=== 테이블 존재 + RLS ===');
  const existing = new Set(rls.map(r => r.t));
  rls.forEach(r => console.log(`${r.t}: RLS=${r.rls}`));
  TABLES.filter(t => !existing.has(t)).forEach(t => console.log(`${t}: (없음)`));

  // 2. 현재 정책
  const pol = await q(`SELECT tablename, policyname, cmd, qual, with_check FROM pg_policies WHERE schemaname='public' AND tablename IN (${TABLES.map(t=>`'${t}'`).join(',')}) ORDER BY tablename, policyname`);
  console.log('\n=== 현재 정책 ===');
  pol.forEach(r => console.log(`[${r.tablename}] ${r.policyname} | ${r.cmd} | USING: ${(r.qual||'-').slice(0,80)} | CHECK: ${(r.with_check||'-').slice(0,60)}`));

  // 2.5 정책 적용 role 확인
  const polRoles = await q(`SELECT tablename, policyname, roles, cmd FROM pg_policies WHERE schemaname='public' AND tablename IN ('newsletter_subscribers','projects','customers','valuation_reports') ORDER BY tablename, policyname`);
  console.log('\n=== 정책 적용 roles ===');
  polRoles.forEach(r => console.log(`[${r.tablename}] ${r.policyname} | roles=${JSON.stringify(r.roles)} | ${r.cmd}`));

  // 3. 핵심 테이블 컬럼
  for (const t of ['users','customers','projects','accountants']) {
    if (!existing.has(t)) continue;
    const cols = await q(`SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='${t}' ORDER BY ordinal_position`);
    console.log(`\n=== ${t} 컬럼 ===\n${cols.map(c=>c.column_name).join(', ')}`);
  }
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
