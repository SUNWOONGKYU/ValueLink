// 가입/로그인 불능 수정 — Supabase Auth 설정 일괄 적용 (Management API)
// ① Resend SMTP 연결 (내장 SMTP 시간당 2통 한도 해소)
// ② 이메일 발송 한도 상향
// ③ site_url localhost → 실서비스 URL + redirect 허용 목록 등록
const fs = require('fs');
const os = require('os');
const path = require('path');

const PAT = fs.readFileSync(path.join(os.tmpdir(), 'sb_token.txt'), 'utf-8').trim();
const REF = 'arxrfetgaitkgiiqabap';

// RESEND_API_KEY는 .env.local에서 읽음 (하드코딩 금지)
const env = fs.readFileSync('C:/ValueLink/.env.local', 'utf-8');
const RESEND_KEY = env.match(/RESEND_API_KEY=(\S+)/)[1];

const payload = {
  // ① Resend SMTP
  smtp_host: 'smtp.resend.com',
  smtp_port: '465',
  smtp_user: 'resend',
  smtp_pass: RESEND_KEY,
  smtp_admin_email: 'noreply@ssalworks.ai.kr', // Resend 검증 완료 도메인
  smtp_sender_name: 'ValueLink',
  // ② 발송 한도 상향 (커스텀 SMTP 사용 시 상향 가능)
  rate_limit_email_sent: 50,
  // ③ 확인 메일 링크 목적지
  site_url: 'https://valuelink-platform.vercel.app',
  uri_allow_list: [
    'https://valuelink-platform.vercel.app/**',
    'https://sunwoongkyu.github.io/**',
    'http://localhost:3000/**',
  ].join(','),
};

(async () => {
  const res = await fetch(`https://api.supabase.com/v1/projects/${REF}/config/auth`, {
    method: 'PATCH',
    headers: { Authorization: `Bearer ${PAT}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const body = await res.json();
  if (!res.ok) { console.error('실패', res.status, JSON.stringify(body).slice(0, 500)); process.exit(1); }
  console.log('적용 성공:');
  console.log(JSON.stringify({
    smtp_host: body.smtp_host,
    smtp_user: body.smtp_user,
    smtp_admin_email: body.smtp_admin_email,
    smtp_sender_name: body.smtp_sender_name,
    rate_limit_email_sent: body.rate_limit_email_sent,
    site_url: body.site_url,
    uri_allow_list: body.uri_allow_list,
    mailer_autoconfirm: body.mailer_autoconfirm,
  }, null, 2));
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
