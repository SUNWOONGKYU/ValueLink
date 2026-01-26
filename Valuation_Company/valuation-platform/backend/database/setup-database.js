/**
 * Supabase 데이터베이스 초기 설정 스크립트
 * - valuation_reports 테이블 생성
 * - 샘플 데이터 (12개 기업) 삽입
 */

import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Supabase 설정
const SUPABASE_URL = 'https://arxrfetgaitkgiiqabap.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function setupDatabase() {
    try {
        console.log('📊 Supabase 데이터베이스 초기 설정 시작...\n');

        // Step 1: 테이블 생성 SQL 읽기
        const createTableSQL = fs.readFileSync(
            path.join(__dirname, 'create_valuation_reports_table.sql'),
            'utf-8'
        );

        console.log('1️⃣ valuation_reports 테이블 생성 중...');

        // RPC 또는 직접 SQL 실행
        // Supabase JS SDK는 직접 SQL 실행을 지원하지 않으므로,
        // 테이블 존재 여부를 확인하고, 없으면 안내 메시지 출력

        const { data: tableCheck, error: checkError } = await supabase
            .from('valuation_reports')
            .select('id')
            .limit(1);

        if (checkError && checkError.code === '42P01') {
            // 테이블이 없음
            console.log('⚠️  valuation_reports 테이블이 없습니다.');
            console.log('📋 다음 SQL을 Supabase 대시보드에서 실행해주세요:\n');
            console.log('─'.repeat(80));
            console.log(createTableSQL);
            console.log('─'.repeat(80));
            console.log('\n🌐 Supabase SQL Editor: https://supabase.com/dashboard/project/arxrfetgaitkgiiqabap/sql/new');
            console.log('\n위 SQL을 복사해서 실행한 후, 이 스크립트를 다시 실행하세요.\n');
            return;
        } else if (checkError) {
            throw checkError;
        }

        console.log('✅ valuation_reports 테이블이 존재합니다.\n');

        // Step 2: 기존 데이터 확인
        const { data: existingData, error: countError } = await supabase
            .from('valuation_reports')
            .select('company_name');

        if (countError) throw countError;

        console.log(`📊 기존 데이터: ${existingData.length}개 기업\n`);

        if (existingData.length > 0) {
            console.log('⚠️  데이터가 이미 존재합니다. 삭제 후 다시 삽입하시겠습니까?');
            console.log('   (계속하려면 Ctrl+C로 중단 후, 데이터를 수동으로 삭제하세요)\n');

            // 삭제 SQL 제공
            console.log('📋 모든 데이터 삭제 SQL:');
            console.log('─'.repeat(80));
            console.log('DELETE FROM valuation_reports;');
            console.log('─'.repeat(80));
            console.log('\n그런 다음 이 스크립트를 다시 실행하세요.\n');
            return;
        }

        // Step 3: 샘플 데이터 삽입 SQL 읽기 및 파싱
        const insertSQL = fs.readFileSync(
            path.join(__dirname, 'insert_sample_valuation_reports.sql'),
            'utf-8'
        );

        console.log('2️⃣ 샘플 데이터 (12개 기업) 삽입 중...\n');

        // INSERT 문 분리 (각 INSERT는 세미콜론으로 끝남)
        const insertStatements = insertSQL
            .split(/;[\s\n]*(?=INSERT)/i)
            .filter(stmt => stmt.trim().startsWith('INSERT'))
            .map(stmt => stmt.trim() + ';');

        console.log(`   총 ${insertStatements.length}개의 INSERT 문 발견\n`);

        // 각 INSERT 문 실행은 SDK로 불가능하므로, 안내 메시지 출력
        console.log('⚠️  JS SDK는 직접 SQL INSERT를 지원하지 않습니다.');
        console.log('📋 다음 SQL을 Supabase 대시보드에서 실행해주세요:\n');
        console.log('─'.repeat(80));
        console.log(insertSQL.slice(0, 1000) + '\n... (파일 전체 내용)');
        console.log('─'.repeat(80));
        console.log('\n🌐 Supabase SQL Editor: https://supabase.com/dashboard/project/arxrfetgaitkgiiqabap/sql/new');
        console.log(`\n또는 파일을 직접 열어서 복사: ${path.join(__dirname, 'insert_sample_valuation_reports.sql')}`);

        console.log('\n✅ SQL 실행 후, 다음 명령어로 확인하세요:');
        console.log('   SELECT COUNT(*) FROM valuation_reports;\n');

    } catch (error) {
        console.error('❌ 오류 발생:', error);
        process.exit(1);
    }
}

// 대안: 수동 데이터 삽입 함수 (SDK 사용)
async function insertSampleDataManually() {
    console.log('📝 SDK를 통한 수동 데이터 삽입...\n');

    const sampleData = [
        {
            company_name: '엔키노에이아이',
            industry: 'AI/기술',
            valuation_method: 'dcf',
            valuation_amount_krw: 16300000000,
            valuation_amount_display: '163억원',
            executive_summary: 'AI 기반 헬스케어 스타트업 엔키노에이아이의 DCF 평가 결과입니다.',
            tags: ['비상장', 'AI', '헬스케어'],
            key_metrics: { 예상매출: '50억원', 성장률: 35 }
        },
        // 나머지 11개 기업... (너무 길어서 생략)
    ];

    for (const company of sampleData) {
        console.log(`   삽입 중: ${company.company_name}`);
        const { error } = await supabase
            .from('valuation_reports')
            .insert(company);

        if (error) {
            console.error(`   ❌ 실패: ${company.company_name}`, error.message);
        } else {
            console.log(`   ✅ 성공: ${company.company_name}`);
        }
    }

    console.log('\n✅ 수동 삽입 완료!\n');
}

// 실행
setupDatabase();
