// 백호 작전 Phase 5 — RLS 적용 후 검증 (anon 차단 + 정상 기능 회귀)
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
  console.log('=== [A] anon 차단 테스트 ===');
  let r = await rest(ANON, 'GET', '/rest/v1/users?select=email&limit=5');
  check('A1. anon users 조회 차단', r.status === 200 && Array.isArray(r.data) && r.data.length === 0, `status=${r.status}, rows=${r.data?.length}`);

  r = await rest(ANON, 'GET', '/rest/v1/customers?select=email&limit=5');
  check('A2. anon customers 조회 차단', r.status === 200 && r.data.length === 0, `rows=${r.data?.length}`);

  r = await rest(ANON, 'GET', '/rest/v1/projects?select=project_id&limit=5');
  check('A3. anon projects 조회 차단', r.status === 200 && r.data.length === 0, `rows=${r.data?.length}`);

  r = await rest(ANON, 'GET', '/rest/v1/newsletter_subscribers?select=email&limit=5');
  check('A4. anon 뉴스레터 구독자 조회 차단', r.status === 200 && r.data.length === 0, `rows=${r.data?.length}`);

  r = await rest(ANON, 'PATCH', '/rest/v1/users?role=eq.customer', { name: 'HACKED' }, { Prefer: 'return=representation' });
  check('A5. anon users 변조 차단', (r.status === 200 || r.status === 204) ? (Array.isArray(r.data) && r.data.length === 0) : true, `status=${r.status}, affected=${Array.isArray(r.data) ? r.data.length : 'err'}`);

  r = await rest(ANON, 'POST', '/rest/v1/users', { user_id: '00000000-0000-4000-8000-000000000001', email: 'rls-test-admin@test.invalid', name: 'x', role: 'admin' });
  check('A6. anon admin 계정 삽입 차단', r.status === 401 || r.status === 403, `status=${r.status}`);

  r = await rest(ANON, 'PATCH', '/rest/v1/accountants?id=gt.0', { bio: 'HACKED' }, { Prefer: 'return=representation' });
  check('A7. anon accountants 변조 차단', (r.status === 200 || r.status === 204) ? (Array.isArray(r.data) && r.data.length === 0) : true, `status=${r.status}, affected=${Array.isArray(r.data) ? r.data.length : 'err'}`);

  console.log('\n=== [B] 공개 유지 기능 ===');
  r = await rest(ANON, 'GET', '/rest/v1/accountants?select=name&limit=2');
  check('B1. anon 회계사 프로필 공개 조회 유지', r.status === 200, `status=${r.status}, rows=${r.data?.length}`);

  r = await rest(ANON, 'GET', '/rest/v1/valuation_reports?select=id&limit=2');
  check('B2. anon 공개 기업목록(link.html) 유지', r.status === 200, `status=${r.status}, rows=${r.data?.length}`);

  const nlEmail = `rls-verify-${Date.now()}@test.invalid`;
  r = await rest(ANON, 'POST', '/rest/v1/newsletter_subscribers', { email: nlEmail });
  check('B3. anon 뉴스레터 구독 INSERT 유지', r.status === 201, `status=${r.status}`);

  r = await rest(ANON, 'DELETE', `/rest/v1/newsletter_subscribers?email=eq.${nlEmail}`, null, { Prefer: 'return=representation' });
  check('B4. anon 뉴스레터 구독자 DELETE 차단', (r.status === 200 || r.status === 204) ? (Array.isArray(r.data) && r.data.length === 0) : true, `status=${r.status}, affected=${Array.isArray(r.data) ? r.data.length : 'err'}`);

  r = await rest(ANON, 'PATCH', `/rest/v1/newsletter_subscribers?email=eq.${nlEmail}`, { email: 'hacked@test.invalid' }, { Prefer: 'return=representation' });
  check('B5. anon 뉴스레터 구독자 변조(PATCH) 차단', (r.status === 200 || r.status === 204) ? (Array.isArray(r.data) && r.data.length === 0) : true, `status=${r.status}, affected=${Array.isArray(r.data) ? r.data.length : 'err'}`);
  await mgmt(`DELETE FROM newsletter_subscribers WHERE email = '${nlEmail}'`); // 테스트 행 정리

  console.log('\n=== [C] admin 회귀 테스트 ===');
  const admin = await login('e2e-admin@valuelink.test', 'E2ETest123!@#');
  r = await rest(admin.token, 'GET', `/rest/v1/users?user_id=eq.${admin.userId}&select=role,is_active`);
  check('C1. 로그인 흐름: 본인 role 조회', r.status === 200 && r.data[0]?.role === 'admin', `role=${r.data?.[0]?.role}`);

  r = await rest(admin.token, 'GET', '/rest/v1/users?select=email&limit=100');
  check('C2. admin 전체 회원 목록 (mypage-admin)', r.status === 200 && r.data.length > 1, `rows=${r.data?.length}`);

  r = await rest(admin.token, 'GET', '/rest/v1/customers?select=email&limit=100');
  check('C3. admin 고객사 전체 조회', r.status === 200, `rows=${r.data?.length}`);

  r = await rest(admin.token, 'GET', '/rest/v1/projects?select=project_id&limit=100');
  check('C4. admin 프로젝트 전체 조회', r.status === 200, `rows=${r.data?.length}`);

  console.log('\n=== [D] accountant 회귀 + 셀프 승격 차단 ===');
  const acc = await login('e2e-accountant@valuelink.test', 'E2ETest123!@#');
  r = await rest(acc.token, 'GET', `/rest/v1/users?user_id=eq.${acc.userId}&select=role`);
  check('D1. accountant 본인 role 조회', r.status === 200 && r.data[0]?.role === 'accountant', `role=${r.data?.[0]?.role}`);

  r = await rest(acc.token, 'PATCH', `/rest/v1/users?user_id=eq.${acc.userId}`, { role: 'admin' }, { Prefer: 'return=representation' });
  const blocked = r.status === 401 || r.status === 403 || (Array.isArray(r.data) && r.data.length === 0);
  check('D2. 셀프 role 승격(admin) 차단', blocked, `status=${r.status}`);

  r = await rest(acc.token, 'GET', `/rest/v1/users?user_id=eq.${acc.userId}&select=role`);
  check('D3. 승격 시도 후 role 불변 확인', r.data?.[0]?.role === 'accountant', `role=${r.data?.[0]?.role}`);

  r = await rest(acc.token, 'GET', '/rest/v1/customers?select=email&limit=5');
  check('D4. accountant 고객사 조회 (평가 업무)', r.status === 200, `rows=${r.data?.length}`);

  r = await rest(acc.token, 'GET', '/rest/v1/users?select=email&limit=100');
  check('D5. accountant는 타인 계정 목록 비노출', r.status === 200 && r.data.length === 1, `rows=${r.data?.length} (본인 1행만)`);

  console.log('\n=== [E] v3 보강 검증 (security 에이전트 지적 반영) ===');
  // E1. anon이 accountant 역할로 자기가입 시도 → 화이트리스트 차단
  r = await rest(ANON, 'POST', '/rest/v1/users', { user_id: '00000000-0000-4000-8000-000000000002', email: 'rls-test-acc@test.invalid', name: 'x', role: 'accountant' });
  check('E1. anon accountant 역할 자기가입 차단', r.status === 401 || r.status === 403, `status=${r.status}`);

  // E2. 화이트리스트 역할(investor)은 RLS는 통과해야 함
  // (representation 요청 금지: RETURNING이 SELECT 권한을 요구해 가짜 거부 발생.
  //  실제 가입 코드(register.html)도 representation 없이 INSERT함.
  //  FK 위반(23503)=RLS 통과 증거, 201이면 행 정리)
  r = await rest(ANON, 'POST', '/rest/v1/users', { user_id: '00000000-0000-4000-8000-000000000003', email: 'rls-test-inv@test.invalid', name: 'x', role: 'investor' });
  const e2RlsAllowed = r.status === 201 || (r.status === 409 && r.data?.code === '23503');
  check('E2. 화이트리스트 역할(investor) 가입 INSERT는 RLS 통과', e2RlsAllowed, `status=${r.status}, code=${r.data?.code || '-'}`);
  if (r.status === 201) await mgmt(`DELETE FROM users WHERE email = 'rls-test-inv@test.invalid'`);

  // E3. accountant(비admin 인증 사용자)의 타인 accountants 프로필 변조 차단
  r = await rest(acc.token, 'PATCH', '/rest/v1/accountants?id=gt.0', { bio: 'HACKED-BY-AUTH' }, { Prefer: 'return=representation' });
  check('E3. 인증 사용자(비admin) accountants 변조 차단', (r.status === 200 || r.status === 204) ? (Array.isArray(r.data) && r.data.length === 0) : true, `status=${r.status}, affected=${Array.isArray(r.data) ? r.data.length : 'err'}`);

  // E4~E5. 인증 사용자(비admin)의 customers 변조/삭제 차단 — 던지기용 행 생성 후 표적 시험
  const probe = await mgmt(`INSERT INTO customers (customer_id, email, company_name, ceo_name, business_number) VALUES ('RLS-PROBE-1', 'rls-probe-${Date.now()}@test.invalid', 'RLS-PROBE', 'RLS-PROBE', '000-00-00000') RETURNING customer_id`);
  const probeId = Array.isArray(probe) ? probe[0]?.customer_id : undefined;
  if (probeId !== undefined) {
    r = await rest(acc.token, 'PATCH', `/rest/v1/customers?customer_id=eq.${probeId}`, { company_name: 'HACKED' }, { Prefer: 'return=representation' });
    check('E4. 인증 사용자(비admin) customers 변조 차단', (r.status === 200 || r.status === 204) ? (Array.isArray(r.data) && r.data.length === 0) : true, `status=${r.status}, affected=${Array.isArray(r.data) ? r.data.length : 'err'}`);

    r = await rest(acc.token, 'DELETE', `/rest/v1/customers?customer_id=eq.${probeId}`, null, { Prefer: 'return=representation' });
    check('E5. 인증 사용자(비admin) customers 삭제 차단', (r.status === 200 || r.status === 204) ? (Array.isArray(r.data) && r.data.length === 0) : true, `status=${r.status}, affected=${Array.isArray(r.data) ? r.data.length : 'err'}`);
    await mgmt(`DELETE FROM customers WHERE company_name = 'RLS-PROBE'`); // 프로브 행 정리
  } else {
    check('E4. 인증 사용자(비admin) customers 변조 차단', false, '프로브 행 생성 실패: ' + JSON.stringify(probe).slice(0, 120));
    check('E5. 인증 사용자(비admin) customers 삭제 차단', false, '프로브 행 생성 실패');
  }

  // E6. admin은 accountants 수정 가능 (무손실 no-op PATCH)
  let cur = await rest(admin.token, 'GET', '/rest/v1/accountants?select=id,is_active&limit=1');
  if (cur.status === 200 && cur.data?.length === 1) {
    const { id, is_active } = cur.data[0];
    r = await rest(admin.token, 'PATCH', `/rest/v1/accountants?id=eq.${id}`, { is_active }, { Prefer: 'return=representation' });
    check('E6. admin accountants 수정 가능 (no-op)', (r.status === 200 || r.status === 204) && Array.isArray(r.data) && r.data.length === 1, `status=${r.status}, affected=${r.data?.length}`);
  } else {
    check('E6. admin accountants 수정 가능 (no-op)', false, 'accountants 조회 실패');
  }

  // E7. anon count 질의로 행 수 유출 차단 (Content-Range)
  const headRes = await fetch(`${SB}/rest/v1/users?select=user_id`, {
    method: 'HEAD',
    headers: { apikey: ANON, Authorization: `Bearer ${ANON}`, Prefer: 'count=exact' },
  });
  const cr = headRes.headers.get('content-range') || '';
  check('E7. anon users count 유출 차단', /\/0$/.test(cr.trim()), `Content-Range=${cr}`);

  console.log(`\n=== 결과: ${pass} PASS / ${fail} FAIL ===`);
  process.exit(fail > 0 ? 1 : 0);
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
