// 백호 작전 Phase 5 — RLS 보완 SQL 실행 (Management API, 단일 트랜잭션)
const fs = require('fs');
const os = require('os');
const path = require('path');

const PAT = fs.readFileSync(path.join(os.tmpdir(), 'sb_token.txt'), 'utf-8').trim();
const REF = 'arxrfetgaitkgiiqabap';
const SQL_PATH = process.argv[2] || 'C:/ValueLink/Valuation_Company/valuation-platform/backend/database/rls_remediation_delta_v2.sql';

(async () => {
  const sql = fs.readFileSync(SQL_PATH, 'utf-8');
  console.log(`SQL 파일: ${SQL_PATH} (${sql.length}자)`);

  const res = await fetch(`https://api.supabase.com/v1/projects/${REF}/database/query`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${PAT}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: sql }),
  });
  const body = await res.text();
  if (!res.ok) {
    console.error(`실행 실패 (${res.status}):`, body.slice(0, 1000));
    process.exit(1);
  }
  console.log('실행 성공:', body.slice(0, 300));
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
