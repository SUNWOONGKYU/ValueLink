// 백호 작전 Phase 5 후속 — SAL Grid 기록 (S1D1/S2F7/S5T1, 루트 + Process 원본 동시)
const fs = require('fs');

const ROOTS = [
  'method/json/data/grid_records',
  'Process/S0_Project-SAL-Grid_생성/method/json/data/grid_records',
];

const TODAY = '2026-06-12';

const PATCHES = {
  S1D1: {
    appendGeneratedFiles: ', database/rls_remediation_delta_v2.sql, database/rls_remediation_delta_v3.sql',
    historyEntry:
      '2026-06-12: 백호 작전 Phase 5 — RLS 치유 SQL v2+v3 실DB 적용(Management API 단일 트랜잭션). ' +
      'v2: users/accountants/레거시7테이블 RLS 활성화 + get_my_role() SECURITY DEFINER 함수(무한재귀 방지) + 셀프 role 승격 차단 + customers/newsletter_subscribers 공개 SELECT 차단. ' +
      'v3(security 에이전트 Needs Fix H-1/H-2/M-2 반영): 가입 역할 화이트리스트 customer/investor/partner/supporter(회계사·관리자 자기가입 차단, PO 승인), accountants·customers 쓰기 admin 전용. ' +
      'M-1(뉴스레터 anon INSERT 스팸)은 의도된 공개 기능으로 위험 수용, 앱 레벨 rate limiting 후속 과제. ' +
      '런타임 검증 28/28 PASS(scripts/rls-verify.js) + security 에이전트 재검증 Verified. 롤백 SQL 동봉.',
  },
  S2F7: {
    historyEntry:
      '2026-06-12: 백호 작전 Phase 5 후속 — 정적 register.html에서 공인회계사/관리자 역할 카드 + 추가정보 폼 + saveAccountantData/saveAdminData/학력·경력 헬퍼 데드코드 제거 ' +
      '(RLS v3 가입 화이트리스트와 동기화, 회계사·관리자 계정은 관리자가 부여). 실브라우저 검증 7/7 PASS(tests/verify-register-role-removal.js).',
  },
  S5T1: {
    historyEntry:
      '2026-06-12: RLS 검증 스위트 보강 — scripts/rls-verify.js 19→28건(뉴스레터 anon DELETE/PATCH 차단, 비admin 인증 사용자의 accountants/customers 변조·삭제 차단, ' +
      'anon count 유출 차단, 가입 역할 화이트리스트 통과/차단, B3 고정 이메일 버그 수정) + tests/verify-register-role-removal.js 신규(register.html 역할 제거 검증 7/7 PASS).',
  },
};

for (const root of ROOTS) {
  for (const [taskId, patch] of Object.entries(PATCHES)) {
    const p = `${root}/${taskId}.json`;
    const j = JSON.parse(fs.readFileSync(p, 'utf-8'));

    if (patch.appendGeneratedFiles && !j.generated_files.includes('rls_remediation_delta_v3')) {
      j.generated_files += patch.appendGeneratedFiles;
    }
    if (j.modification_history && j.modification_history.length > 0) {
      if (!j.modification_history.includes(patch.historyEntry)) {
        j.modification_history += '\n' + patch.historyEntry;
      }
    } else {
      j.modification_history = patch.historyEntry;
    }
    j.updated_at = TODAY;

    fs.writeFileSync(p, JSON.stringify(j, null, 2) + '\n', 'utf-8');
    console.log(`updated: ${p}`);
  }
}
console.log('done');
