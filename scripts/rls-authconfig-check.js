// 백호 Phase 5 — 이메일 자동확인(autoconfirm) 설정 확인 (읽기 전용)
const fs = require('fs');
const os = require('os');
const path = require('path');

const PAT = fs.readFileSync(path.join(os.tmpdir(), 'sb_token.txt'), 'utf-8').trim();
const REF = 'arxrfetgaitkgiiqabap';

(async () => {
  const res = await fetch(`https://api.supabase.com/v1/projects/${REF}/config/auth`, {
    headers: { 'Authorization': `Bearer ${PAT}` },
  });
  const body = await res.json();
  if (!res.ok) { console.error('ERR', res.status, JSON.stringify(body).slice(0, 200)); process.exit(1); }
  console.log('mailer_autoconfirm (이메일 인증 없이 즉시 세션):', body.mailer_autoconfirm);
  console.log('external_email_enabled:', body.external_email_enabled);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
