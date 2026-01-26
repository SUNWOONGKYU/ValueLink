/**
 * Supabase SQL 직접 실행 스크립트
 * PostgreSQL 클라이언트를 사용해서 SQL 파일 실행
 */

import pg from 'pg';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const { Client } = pg;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Supabase PostgreSQL 연결 정보
const DB_URL = 'postgresql://postgres.arxrfetgaitkgiiqabap:ValueLink2025!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres';

async function runSQL() {
    const client = new Client({
        connectionString: DB_URL,
        ssl: { rejectUnauthorized: false }
    });

    try {
        console.log('📊 Supabase PostgreSQL 연결 중...\n');
        await client.connect();
        console.log('✅ 연결 성공!\n');

        // Step 1: 테이블 생성
        console.log('1️⃣ valuation_reports 테이블 생성 중...');
        const createTableSQL = fs.readFileSync(
            path.join(__dirname, 'create_valuation_reports_table.sql'),
            'utf-8'
        );

        await client.query(createTableSQL);
        console.log('✅ 테이블 생성 완료!\n');

        // Step 2: 기존 데이터 확인
        console.log('2️⃣ 기존 데이터 확인 중...');
        const countResult = await client.query('SELECT COUNT(*) FROM valuation_reports');
        const existingCount = parseInt(countResult.rows[0].count);
        console.log(`   기존 데이터: ${existingCount}개\n`);

        if (existingCount > 0) {
            console.log('⚠️  데이터가 이미 존재합니다. 삭제 후 진행합니다...');
            await client.query('DELETE FROM valuation_reports');
            console.log('✅ 기존 데이터 삭제 완료!\n');
        }

        // Step 3: 샘플 데이터 삽입
        console.log('3️⃣ 샘플 데이터 (12개 기업) 삽입 중...');
        const insertSQL = fs.readFileSync(
            path.join(__dirname, 'insert_sample_valuation_reports.sql'),
            'utf-8'
        );

        await client.query(insertSQL);
        console.log('✅ 샘플 데이터 삽입 완료!\n');

        // Step 4: 최종 확인
        console.log('4️⃣ 최종 데이터 확인...');
        const finalResult = await client.query(
            'SELECT company_name, valuation_method, valuation_amount_display FROM valuation_reports ORDER BY id'
        );

        console.log(`\n📊 총 ${finalResult.rows.length}개 기업 등록:\n`);
        finalResult.rows.forEach((row, index) => {
            console.log(`   ${index + 1}. ${row.company_name} (${row.valuation_method}): ${row.valuation_amount_display}`);
        });

        console.log('\n✅ 모든 작업 완료! 🎉\n');

    } catch (error) {
        console.error('❌ 오류 발생:', error.message);
        if (error.code) {
            console.error('   에러 코드:', error.code);
        }
        process.exit(1);
    } finally {
        await client.end();
    }
}

runSQL();
