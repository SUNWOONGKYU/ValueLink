/**
 * @description 3개 기업 평가 결과를 Supabase DB에 저장
 *
 * test-results/companies/ 폴더의 JSON 파일을 읽어서
 * test_valuation_results 테이블에 저장
 */

const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

// .env.local 파일 로드
require('dotenv').config({ path: path.join(__dirname, '../.env.local') });

// 색상 출력
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Supabase 클라이언트 초기화 (Service Role Key 사용 - RLS 우회)
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  log('❌ Supabase 환경 변수가 설정되지 않았습니다.', 'red');
  log('   .env.local 파일에 다음 변수를 설정해주세요:', 'yellow');
  log('   - NEXT_PUBLIC_SUPABASE_URL', 'yellow');
  log('   - SUPABASE_SERVICE_ROLE_KEY (Settings → API → service_role key)', 'yellow');
  process.exit(1);
}

log('🔐 Service Role Key 사용 (프로덕션 보안 방식)\n', 'green');

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// ============================================================================
// JSON 파일 읽기
// ============================================================================

function loadResults() {
  const resultsDir = path.join(__dirname, '../test-results/companies');
  const companies = ['company1', 'company2', 'company3'];
  const methods = ['dcf', 'asset', 'relative', 'intrinsic', 'tax'];

  const allResults = [];

  companies.forEach(companyId => {
    methods.forEach(method => {
      const jsonPath = path.join(resultsDir, companyId, `${method}_result.json`);

      if (fs.existsSync(jsonPath)) {
        const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
        allResults.push(data);
      } else {
        log(`⚠️  파일을 찾을 수 없습니다: ${jsonPath}`, 'yellow');
      }
    });
  });

  return allResults;
}

// ============================================================================
// DB에 저장
// ============================================================================

async function saveToDatabase(results) {
  log('\n🗄️  Supabase DB에 평가 결과 저장 중...\n', 'cyan');

  let successCount = 0;
  let failCount = 0;

  for (const result of results) {
    const { company, method, valuationResult, draftSections } = result;

    try {
      // 기존 데이터 삭제 (중복 방지)
      const { error: deleteError } = await supabase
        .from('test_valuation_results')
        .delete()
        .eq('company_id', company.id)
        .eq('method', method);

      if (deleteError && deleteError.code !== 'PGRST116') { // PGRST116 = no rows found
        throw deleteError;
      }

      // 새 데이터 삽입
      const { data, error } = await supabase
        .from('test_valuation_results')
        .insert({
          company_id: company.id,
          company_name: company.name,
          industry: company.industry,
          situation: company.situation,
          method: method,
          enterprise_value: valuationResult.enterpriseValue,
          equity_value: valuationResult.equityValue,
          share_price: valuationResult.sharePrice,
          details: valuationResult.details,
          draft_sections: draftSections,
          duration_ms: valuationResult.duration,
        })
        .select();

      if (error) throw error;

      log(`  ✅ ${company.name} - ${method.toUpperCase()}: 저장 완료`, 'green');
      successCount++;

    } catch (error) {
      log(`  ❌ ${company.name} - ${method.toUpperCase()}: ${error.message}`, 'red');
      failCount++;
    }
  }

  log('\n' + '='.repeat(70), 'cyan');
  log(`✅ 성공: ${successCount}/${results.length}`, 'green');
  log(`❌ 실패: ${failCount}/${results.length}`, failCount > 0 ? 'red' : 'green');
  log('='.repeat(70), 'cyan');

  return { successCount, failCount };
}

// ============================================================================
// DB 조회 및 확인
// ============================================================================

async function verifyData() {
  log('\n🔍 저장된 데이터 확인 중...\n', 'blue');

  try {
    const { data, error } = await supabase
      .from('test_valuation_results')
      .select('company_id, company_name, method, share_price')
      .order('company_id', { ascending: true })
      .order('method', { ascending: true });

    if (error) throw error;

    if (!data || data.length === 0) {
      log('⚠️  저장된 데이터가 없습니다.', 'yellow');
      return;
    }

    log(`총 ${data.length}개 레코드 조회:\n`, 'cyan');

    let currentCompany = null;
    data.forEach(row => {
      if (row.company_id !== currentCompany) {
        currentCompany = row.company_id;
        log(`\n[${row.company_name}]`, 'magenta');
      }
      log(`  ${row.method.toUpperCase()}: ${row.share_price.toLocaleString()}원`, 'green');
    });

  } catch (error) {
    log(`❌ 조회 실패: ${error.message}`, 'red');
  }
}

// ============================================================================
// 메인 실행
// ============================================================================

async function main() {
  log('\n🚀 3개 기업 평가 결과 DB 저장 시작\n', 'cyan');

  // 1. JSON 파일 로드
  log('📁 JSON 파일 로드 중...', 'blue');
  const results = loadResults();
  log(`✅ ${results.length}개 결과 로드 완료\n`, 'green');

  // 2. DB에 저장
  const { successCount, failCount } = await saveToDatabase(results);

  // 3. 저장된 데이터 확인
  if (successCount > 0) {
    await verifyData();
  }

  // 4. 최종 메시지
  if (failCount === 0) {
    log('\n🎉 모든 데이터가 성공적으로 DB에 저장되었습니다!', 'green');
  } else {
    log('\n⚠️  일부 데이터 저장에 실패했습니다. 로그를 확인해주세요.', 'yellow');
  }
}

// 실행
main().catch(error => {
  log(`\n💥 치명적 오류: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});
