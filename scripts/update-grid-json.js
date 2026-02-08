/**
 * REVISED Task Instruction 반영 - Grid JSON 일괄 업데이트 스크립트
 * 2026-02-08
 */
const fs = require('fs');
const path = require('path');

const GRID_DIR = path.join(__dirname, '..', 'Process', 'S0_Project-SAL-Grid_생성', 'method', 'json', 'data', 'grid_records');
const TODAY = '2026-02-08';

// REVISED에서 변경된 내용 매핑
const updates = {
  // === S2 Stage ===
  S2F1: {
    task_name: '평가 결과 페이지 템플릿 및 5개 방법별 페이지 마이그레이션',
  },
  S2F2: {
    task_name: '평가 신청 폼 템플릿 및 5개 방법별 페이지 마이그레이션',
  },
  S2F3: {
    task_name: '평가 방법 가이드 템플릿 및 5개 가이드 페이지 마이그레이션',
  },
  S2F4: {
    task_name: '역할별 마이페이지 템플릿 및 6개 역할 페이지 마이그레이션',
  },
  S2F5: {
    task_name: '프로세스 단계 템플릿 및 12개 워크플로우 페이지 마이그레이션',
  },
  S2F6: {
    task_name: '프로젝트 관리 페이지 (목록, 상세, 생성) 마이그레이션',
    dependencies: 'S1BI1, S2BA2',
  },
  S2F7: {
    task_name: '인증 페이지 및 랜딩 페이지 마이그레이션',
    dependencies: 'S1BI1, S2S1',
  },
  S2BA1: {
    task_name: '평가 프로세스 API 및 14단계 워크플로우 마이그레이션',
  },
  S2BA2: {
    task_name: '프로젝트 및 평가 요청 API 마이그레이션',
  },
  S2BA3: {
    task_name: '문서 및 보고서 API 마이그레이션',
    dependencies: 'S1BI1, S1D1',
  },
  S2BA4: {
    task_name: 'AI 클라이언트 및 이메일 서비스 마이그레이션',
  },
  S2M1: {
    task_name: '사용자 매뉴얼 및 FAQ 마이그레이션',
    dependencies: 'S2F1, S2F2, S2F3, S2F4, S2F5, S2F6, S2F7',
  },

  // === S3 Stage ===
  S3BA1: {
    task_name: '평가 엔진 오케스트레이터 구현',
    dependencies: 'S2BA2, S1D1',
  },
  S3BA2: {
    task_name: '재무 수학 라이브러리 구현',
  },
  S3BA3: {
    task_name: 'DCF 평가 엔진 및 민감도 분석 구현',
  },
  S3BA4: {
    task_name: '4개 평가 엔진 구현 (Relative, Asset, Intrinsic, Tax)',
    dependencies: 'S3BA1, S3BA2, S3BA3',
  },

  // === S4 Stage ===
  S4F1: {
    task_name: 'Deal 뉴스 트래커 및 투자 모니터 마이그레이션',
    dependencies: 'S1BI1, S4E2',
  },
  S4E1: {
    task_name: '뉴스 크롤러 인프라 구현',
  },
  S4E2: {
    task_name: '뉴스 파서 및 데이터 추출 구현',
  },
  S4E3: {
    task_name: '6개 투자 뉴스 사이트별 크롤러',
  },
  S4E4: {
    task_name: 'DCF 평가 엔진 검증',
  },
  S4O1: {
    task_name: '주간 뉴스 수집 스케줄러',
    dependencies: 'S4E1, S4E2',
  },

  // === S5 Stage ===
  S5O1: {
    task_name: '배포 설정 및 CI/CD 파이프라인',
    dependencies: 'S2F1, S2F2, S2F3, S2F4, S2F5, S2F6, S2F7, S2BA1, S2BA2, S2BA3, S2BA4, S2M1, S3BA1, S3BA2, S3BA3, S3BA4, S4F1, S4E1, S4E2, S4E3, S4E4, S4O1',
  },
  S5T1: {
    task_name: '통합 테스트 및 품질 보증',
    dependencies: 'S2F1, S2F2, S2F3, S2F4, S2F5, S2F6, S2F7, S2BA1, S2BA2, S2BA3, S2BA4, S2M1, S3BA1, S3BA2, S3BA3, S3BA4, S4F1, S4E1, S4E2, S4E3, S4E4, S4O1',
  },
  S5M1: {
    task_name: '최종 문서화 및 핸드북',
    dependencies: 'S1BI1, S1D1, S1M1, S1M2, S2F1, S2F2, S2F3, S2F4, S2F5, S2F6, S2F7, S2BA1, S2BA2, S2BA3, S2BA4, S2M1, S3BA1, S3BA2, S3BA3, S3BA4, S4F1, S4E1, S4E2, S4E3, S4E4, S4O1',
  },
};

let successCount = 0;
let failCount = 0;
const changes = [];

for (const [taskId, newFields] of Object.entries(updates)) {
  const filePath = path.join(GRID_DIR, `${taskId}.json`);

  try {
    const raw = fs.readFileSync(filePath, 'utf-8');
    const data = JSON.parse(raw);

    const before = {};
    const after = {};

    for (const [key, value] of Object.entries(newFields)) {
      if (data[key] !== value) {
        before[key] = data[key];
        after[key] = value;
        data[key] = value;
      }
    }

    // updated_at 갱신
    data.updated_at = TODAY;

    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');

    const changedFields = Object.keys(after);
    if (changedFields.length > 0) {
      changes.push({ taskId, changedFields, before, after });
    }

    successCount++;
    console.log(`✅ ${taskId}: ${changedFields.length > 0 ? changedFields.join(', ') + ' 수정' : 'updated_at만 갱신'}`);
  } catch (err) {
    failCount++;
    console.error(`❌ ${taskId}: ${err.message}`);
  }
}

console.log(`\n=== 결과 ===`);
console.log(`성공: ${successCount}개`);
console.log(`실패: ${failCount}개`);
console.log(`변경된 필드가 있는 Task: ${changes.length}개`);

console.log(`\n=== 변경 상세 ===`);
for (const c of changes) {
  console.log(`\n[${c.taskId}]`);
  for (const field of c.changedFields) {
    const bVal = String(c.before[field]).substring(0, 60);
    const aVal = String(c.after[field]).substring(0, 60);
    console.log(`  ${field}: "${bVal}" → "${aVal}"`);
  }
}
