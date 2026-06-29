// Supabase Management API로 DDL(SQL 파일) 적용 — 검증된 경로
//
// 사용법:
//   node apply-ddl-management-api.js <SQL파일경로>
//
// PAT(sbp_...) 전달 경로 (둘 중 하나, 우선순위 순):
//   1) 환경변수 SUPABASE_ACCESS_TOKEN
//   2) 임시 파일 C:\Users\선웅규\AppData\Local\Temp\sb_token.txt (한 줄)
//
// PAT은 비밀: 커밋/로그 금지. 이 스크립트는 PAT을 출력하지 않는다.
// 발급: https://supabase.com/dashboard/account/tokens

const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: 'C:/ValueLink/.env.local' });

const PROJECT_REF = 'arxrfetgaitkgiiqabap';
const TMP_TOKEN = 'C:/Users/선웅규/AppData/Local/Temp/sb_token.txt';

function readPat() {
  if (process.env.SUPABASE_ACCESS_TOKEN) return process.env.SUPABASE_ACCESS_TOKEN.trim();
  if (process.env.SUPABASE_PAT) return process.env.SUPABASE_PAT.trim();
  try {
    const t = fs.readFileSync(TMP_TOKEN, 'utf-8').trim();
    if (t) return t;
  } catch { /* 파일 없음 */ }
  return null;
}

async function runQuery(pat, query) {
  const res = await fetch(`https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${pat}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
    signal: AbortSignal.timeout(30000),
  });
  let body;
  try { body = await res.json(); } catch { body = await res.text(); }
  return { ok: res.ok, status: res.status, body };
}

(async () => {
  const sqlPath = process.argv[2];
  if (!sqlPath) {
    console.error('❌ SQL 파일 경로를 인자로 주세요: node apply-ddl-management-api.js <파일>');
    process.exit(1);
  }
  const sql = fs.readFileSync(sqlPath, 'utf-8');

  const pat = readPat();
  if (!pat) {
    console.error('❌ PAT 없음. SUPABASE_ACCESS_TOKEN 환경변수 또는 임시 토큰 파일이 필요합니다.');
    console.error('   발급: https://supabase.com/dashboard/account/tokens');
    process.exit(2);
  }
  if (!pat.startsWith('sbp_')) {
    console.error('⚠️  PAT 형식이 sbp_ 로 시작하지 않습니다. 올바른 Personal Access Token인지 확인하세요.');
  }

  console.log(`=== DDL 적용: ${path.basename(sqlPath)} (project ${PROJECT_REF}) ===`);

  // 1) 적용
  const apply = await runQuery(pat, sql);
  if (!apply.ok) {
    console.error(`❌ 적용 실패 (HTTP ${apply.status}):`, JSON.stringify(apply.body).slice(0, 500));
    process.exit(3);
  }
  console.log('✅ SQL 적용 성공');

  // 2) 검증 — valuation_reports 정책 목록
  const verify = await runQuery(
    pat,
    "SELECT policyname, cmd FROM pg_policies WHERE tablename='valuation_reports' ORDER BY policyname;"
  );
  if (verify.ok) {
    console.log('\n=== valuation_reports 정책 현황 ===');
    console.log(JSON.stringify(verify.body, null, 2));
  } else {
    console.log('검증 쿼리 실패:', verify.status, JSON.stringify(verify.body).slice(0, 300));
  }

  // 3) user_id 컬럼 확인
  const col = await runQuery(
    pat,
    "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='valuation_reports' AND column_name='user_id';"
  );
  if (col.ok) {
    console.log('\n=== user_id 컬럼 ===');
    console.log(JSON.stringify(col.body));
  }
})();
