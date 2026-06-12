// 가입/로그인 수정 검증 — 이메일 확인 흐름 전체를 API로 재현
// (브라우저 플로우와 동일한 순서: signup → 메일확인 → 로그인 → 보류 프로필 저장)
const fs = require('fs');
const os = require('os');
const path = require('path');

const REF = 'arxrfetgaitkgiiqabap';
const SB = `https://${REF}.supabase.co`;
const ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0';
const SERVICE = fs.readFileSync(path.join(os.tmpdir(), 'sb_service.txt'), 'utf-8').trim();
const PAT = fs.readFileSync(path.join(os.tmpdir(), 'sb_token.txt'), 'utf-8').trim();

let pass = 0, fail = 0;
function check(name, ok, detail) {
  console.log(`${ok ? '✅ PASS' : '❌ FAIL'} | ${name}${detail ? ' — ' + detail : ''}`);
  ok ? pass++ : fail++;
}

async function rest(token, method, pathname, body) {
  const res = await fetch(`${SB}${pathname}`, {
    method,
    headers: { apikey: ANON, Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = null;
  try { data = await res.json(); } catch {}
  return { status: res.status, data };
}

async function mgmt(sql) {
  const res = await fetch(`https://api.supabase.com/v1/projects/${REF}/database/query`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${PAT}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: sql }),
  });
  return res.json();
}

(async () => {
  const stamp = Date.now();
  // 실존 수신함(+태그)으로 발송 — 바운스 방지. 테스트 후 계정 삭제.
  const email = `wksun999+vlflow${stamp}@gmail.com`;
  const password = 'FlowTest123!@#';

  console.log('=== [S] 가입 → 메일확인 → 로그인 → 프로필 저장 플로우 ===');

  // S1. 가입 (register.html과 동일: emailRedirectTo 포함)
  let res = await fetch(`${SB}/auth/v1/signup`, {
    method: 'POST',
    headers: { apikey: ANON, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email, password,
      options: { email_redirect_to: 'https://valuelink-platform.vercel.app/app/login.html' },
    }),
  });
  let body = await res.json();
  const userId = body.id || (body.user && body.user.id);
  const sentAt = body.confirmation_sent_at || (body.user && body.user.confirmation_sent_at);
  check('S1. 가입 성공 + 확인메일 발송 (429 없음)', res.status === 200 && !!sentAt, `status=${res.status}, sent_at=${sentAt || '-'}, error=${body.error_code || '-'}`);
  check('S2. 가입 직후 세션 없음 (이메일 확인 대기)', !body.access_token, body.access_token ? '예상과 달리 세션 발급됨' : '정상');

  // S3. 확인 전 로그인 → 거부 확인
  res = await fetch(`${SB}/auth/v1/token?grant_type=password`, {
    method: 'POST',
    headers: { apikey: ANON, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  body = await res.json();
  check('S3. 메일 확인 전 로그인 거부', res.status === 400 && (body.error_code === 'email_not_confirmed' || /not confirmed/i.test(body.msg || body.error_description || '')), `status=${res.status}, code=${body.error_code || '-'}`);

  // S4. 메일 링크 클릭을 admin API로 재현 (이메일 확인 처리)
  res = await fetch(`${SB}/auth/v1/admin/users/${userId}`, {
    method: 'PUT',
    headers: { apikey: SERVICE, Authorization: `Bearer ${SERVICE}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email_confirm: true }),
  });
  check('S4. 이메일 확인 처리 (메일 링크 클릭 재현)', res.ok, `status=${res.status}`);

  // S5. 확인 후 로그인 → 세션 발급
  res = await fetch(`${SB}/auth/v1/token?grant_type=password`, {
    method: 'POST',
    headers: { apikey: ANON, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  body = await res.json();
  const token = body.access_token;
  check('S5. 메일 확인 후 로그인 성공', res.status === 200 && !!token, `status=${res.status}`);

  if (token) {
    // S6. login.html completePendingRegistration과 동일: users INSERT
    let r = await rest(token, 'POST', '/rest/v1/users', {
      user_id: userId, email, name: '플로우검증', role: 'customer', is_active: true,
    });
    check('S6. 첫 로그인 시 users 저장 (보류 프로필)', r.status === 201, `status=${r.status} ${JSON.stringify(r.data || '').slice(0, 100)}`);

    // S7. customers INSERT (보류된 회사 정보)
    r = await rest(token, 'POST', '/rest/v1/customers', {
      user_id: userId, email,
      company_name: '플로우검증주식회사', company_name_en: 'Flow Verify Inc.',
      business_number: '222-22-22222', ceo_name: '플로우대표',
      industry: null, founded_date: null, phone: null,
    });
    check('S7. 첫 로그인 시 customers 저장 (회사 정보)', r.status === 201, `status=${r.status} ${JSON.stringify(r.data || '').slice(0, 100)}`);

    // S8. login.html 역할 조회와 동일
    r = await rest(token, 'GET', `/rest/v1/users?user_id=eq.${userId}&select=role,is_active`);
    check('S8. 로그인 후 역할 조회 (mypage 진입 조건)', r.status === 200 && r.data?.[0]?.role === 'customer' && r.data?.[0]?.is_active === true, `role=${r.data?.[0]?.role}, active=${r.data?.[0]?.is_active}`);
  } else {
    check('S6~S8', false, 'S5 실패로 건너뜀'); fail += 2;
  }

  // 정리
  await mgmt(`DELETE FROM customers WHERE email = '${email}'`);
  await mgmt(`DELETE FROM users WHERE email = '${email}'`);
  await mgmt(`DELETE FROM auth.users WHERE email = '${email}'`);
  console.log('   (테스트 계정/데이터 정리 완료)');

  console.log(`\n=== 결과: ${pass} PASS / ${fail} FAIL ===`);
  process.exit(fail > 0 ? 1 : 0);
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
