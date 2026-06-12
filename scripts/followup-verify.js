// 백호 후속과제 v1 검증 — 고객 가입 customers 저장 + 뉴스레터 rate limiting
// (테스트 데이터는 *.test.invalid 이메일만 사용, 종료 시 전부 정리)
const fs = require('fs');
const os = require('os');
const path = require('path');

const PAT = fs.readFileSync(path.join(os.tmpdir(), 'sb_token.txt'), 'utf-8').trim();
const REF = 'arxrfetgaitkgiiqabap';
const SB = `https://${REF}.supabase.co`;
const ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0';

let pass = 0, fail = 0;
function check(name, ok, detail) {
  console.log(`${ok ? '✅ PASS' : '❌ FAIL'} | ${name}${detail ? ' — ' + detail : ''}`);
  ok ? pass++ : fail++;
}

async function rest(token, method, pathname, body, extraHeaders = {}) {
  const res = await fetch(`${SB}${pathname}`, {
    method,
    headers: {
      apikey: ANON,
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...extraHeaders,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = null;
  try { data = await res.json(); } catch {}
  return { status: res.status, data };
}

async function login(email, password) {
  const res = await fetch(`${SB}/auth/v1/token?grant_type=password`, {
    method: 'POST',
    headers: { apikey: ANON, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(`로그인 실패(${email}): ${JSON.stringify(data).slice(0, 150)}`);
  return { token: data.access_token, userId: data.user.id };
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
  const custEmail = `followup-cust-${stamp}@test.invalid`;

  console.log('=== [F] 과제 2 — 고객 가입 → customers 저장 플로우 (register.html 모사) ===');

  // F1. 테스트 계정 생성 — /auth/v1/signup은 Supabase 플랫폼 자체 rate limit(429)에
  // 걸릴 수 있어, admin API로 생성 후 비밀번호 로그인으로 가입 직후 세션을 재현
  const SERVICE = fs.readFileSync(path.join(os.tmpdir(), 'sb_service.txt'), 'utf-8').trim();
  const suRes = await fetch(`${SB}/auth/v1/admin/users`, {
    method: 'POST',
    headers: { apikey: SERVICE, Authorization: `Bearer ${SERVICE}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: custEmail, password: 'FollowUp123!@#', email_confirm: true }),
  });
  const su = await suRes.json();
  let custToken = null, custId = su.id || su.user?.id;
  if (suRes.ok && custId) {
    try {
      const lg = await login(custEmail, 'FollowUp123!@#');
      custToken = lg.token;
    } catch (e) { /* check에서 실패 처리 */ }
  }
  check('F1. 테스트 고객 계정 생성 + 세션 발급', !!custToken && !!custId, `status=${suRes.status}${custToken ? '' : ', 세션 발급 실패'}`);

  if (custToken && custId) {
    // F2. users 테이블 INSERT (role=customer)
    let r = await rest(custToken, 'POST', '/rest/v1/users', {
      user_id: custId, email: custEmail, name: '후속검증', role: 'customer', is_active: true,
    });
    check('F2. users INSERT(role=customer) 성공', r.status === 201, `status=${r.status} ${JSON.stringify(r.data || '').slice(0, 120)}`);

    // F3. customers INSERT — register.html saveCustomerData와 동일 페이로드
    r = await rest(custToken, 'POST', '/rest/v1/customers', {
      user_id: custId,
      email: custEmail,
      company_name: '후속검증주식회사',
      company_name_en: 'FollowUp Verify Inc.',
      business_number: '000-00-00001',
      ceo_name: '검증대표',
      industry: null, founded_date: null, phone: null,
    });
    check('F3. customers INSERT(회사 추가정보) 성공 ⭐핵심', r.status === 201, `status=${r.status} ${JSON.stringify(r.data || '').slice(0, 200)}`);

    // F4. customer_id DEFAULT 자동 생성 + 본인 행 조회(select_own)
    r = await rest(custToken, 'GET', `/rest/v1/customers?email=eq.${custEmail}&select=customer_id,company_name,company_name_en,user_id`);
    const row = r.data?.[0];
    check('F4. customer_id 자동 생성 + 본인 행 조회 가능', r.status === 200 && !!row?.customer_id && row?.company_name_en === 'FollowUp Verify Inc.', `customer_id=${row?.customer_id}, en=${row?.company_name_en}`);

    // F4.5(M-1 보강). 동일 user_id로 두 번째 customers 행 생성 시도 → UNIQUE 차단
    r = await rest(custToken, 'POST', '/rest/v1/customers', {
      user_id: custId,
      email: `followup-dup-${stamp}@test.invalid`,
      company_name: '중복생성시도', ceo_name: 'x', business_number: '111-11-11111',
    });
    check('F7. 동일 user_id 복수 행 생성 차단 (M-1)', r.status === 409 && r.data?.code === '23505', `status=${r.status}, code=${r.data?.code || '-'}`);

    // F5. 타인 user_id로 customers 행 생성 시도 → 차단
    r = await rest(custToken, 'POST', '/rest/v1/customers', {
      user_id: '00000000-0000-4000-8000-0000000000ff',
      email: `followup-evil-${stamp}@test.invalid`,
      company_name: 'EVIL', ceo_name: 'EVIL', business_number: '999-99-99999',
    });
    check('F5. 타인 user_id 행 생성 차단', r.status === 401 || r.status === 403 || r.status === 409, `status=${r.status}, code=${r.data?.code || '-'}`);
  } else {
    check('F2~F5', false, 'F1 실패로 건너뜀');
    fail += 3;
  }

  // F6. customer 아닌 역할(accountant)은 본인 user_id로도 customers INSERT 불가
  const acc = await login('e2e-accountant@valuelink.test', 'E2ETest123!@#');
  let r = await rest(acc.token, 'POST', '/rest/v1/customers', {
    user_id: acc.userId,
    email: `followup-acc-${stamp}@test.invalid`,
    company_name: 'ACC-EVIL', ceo_name: 'x', business_number: '888-88-88888',
  });
  check('F6. 비customer 역할(accountant) customers INSERT 차단', r.status === 401 || r.status === 403, `status=${r.status}, code=${r.data?.code || '-'}`);

  // F-정리
  await mgmt(`DELETE FROM customers WHERE email LIKE 'followup-%@test.invalid'`);
  await mgmt(`DELETE FROM users WHERE email = '${custEmail}'`);
  await mgmt(`DELETE FROM auth.users WHERE email = '${custEmail}'`);
  console.log('   (테스트 데이터 정리 완료)');

  console.log('\n=== [G] 과제 1 — 뉴스레터 IP rate limiting (1시간 5회 제한) ===');
  // 깨끗한 상태에서 시작 (이전 테스트 시도 기록 제거)
  await mgmt(`DELETE FROM newsletter_subscribe_attempts`);

  let okCount = 0, blockedAt = null, lastErr = null;
  for (let i = 1; i <= 6; i++) {
    const r2 = await rest(ANON, 'POST', '/rest/v1/newsletter_subscribers', { email: `followup-nl-${stamp}-${i}@test.invalid` });
    if (r2.status === 201) okCount++;
    else { blockedAt = i; lastErr = r2; break; }
  }
  check('G1. 5회까지 구독 INSERT 허용', okCount === 5, `성공=${okCount}회`);
  check('G2. 6회째 구독 차단 (rate limit 발동) ⭐핵심', blockedAt === 6 && lastErr && JSON.stringify(lastErr.data).includes('rate_limit_exceeded'), `blockedAt=${blockedAt}, err=${JSON.stringify(lastErr?.data || '').slice(0, 150)}`);

  // G3. 시도 기록 테이블은 외부에서 조회 불가 (RLS 정책 없음)
  r = await rest(ANON, 'GET', '/rest/v1/newsletter_subscribe_attempts?select=ip&limit=5');
  check('G3. 시도 기록(IP) 외부 조회 차단', (r.status === 200 && Array.isArray(r.data) && r.data.length === 0) || r.status === 401 || r.status === 403 || r.status === 404, `status=${r.status}, rows=${Array.isArray(r.data) ? r.data.length : '-'}`);

  // G-정리 (테스트 구독 행 + 내 IP 시도 기록 제거 → 회귀 테스트 영향 차단)
  await mgmt(`DELETE FROM newsletter_subscribers WHERE email LIKE 'followup-nl-%@test.invalid'`);
  await mgmt(`DELETE FROM newsletter_subscribe_attempts`);
  console.log('   (테스트 데이터 정리 완료)');

  console.log(`\n=== 결과: ${pass} PASS / ${fail} FAIL ===`);
  process.exit(fail > 0 ? 1 : 0);
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
