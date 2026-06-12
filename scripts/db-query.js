// 후속과제 진단 — 실DB 스키마 조회 (Management API, 읽기 전용)
const fs = require('fs');
const os = require('os');
const path = require('path');

const PAT = fs.readFileSync(path.join(os.tmpdir(), 'sb_token.txt'), 'utf-8').trim();
const REF = 'arxrfetgaitkgiiqabap';
const query = process.argv[2];

(async () => {
  const res = await fetch(`https://api.supabase.com/v1/projects/${REF}/database/query`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${PAT}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  const body = await res.text();
  if (!res.ok) {
    console.error(`실행 실패 (${res.status}):`, body.slice(0, 1000));
    process.exit(1);
  }
  console.log(JSON.stringify(JSON.parse(body), null, 2));
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
