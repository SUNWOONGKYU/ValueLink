/**
 * Phase 1 Migration Runner
 *
 * Phase 1 SQL 파일들을 순서대로 실행합니다.
 *
 * 사용법:
 *   npm install pg
 *   node run-phase1-migrations.js
 */

const { Client } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

// PostgreSQL 연결 설정
const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
    console.error('❌ DATABASE_URL이 .env 파일에 설정되지 않았습니다.');
    process.exit(1);
}

// SQL 파일 순서
const sqlFiles = [
    'create_users_table.sql',
    'create_accountants_table.sql',
    'alter_customers_table.sql',
    'alter_projects_table.sql'
];

// SQL 실행 함수
async function executeSql(client, filename) {
    try {
        const sqlPath = path.join(__dirname, filename);
        const sql = fs.readFileSync(sqlPath, 'utf-8');

        console.log(`\n📄 Executing: ${filename}...`);

        await client.query(sql);

        console.log(`✅ Success: ${filename}`);
        return true;

    } catch (error) {
        console.error(`❌ Error in ${filename}:`);
        console.error(error.message);
        return false;
    }
}

// 메인 함수
async function runMigrations() {
    const client = new Client({ connectionString });

    try {
        console.log('🚀 Phase 1 Migration 시작...');
        console.log('📁 Database: Supabase PostgreSQL');
        console.log('');

        // 연결
        await client.connect();
        console.log('✅ Database 연결 성공\n');

        let successCount = 0;
        let failCount = 0;

        for (const filename of sqlFiles) {
            const success = await executeSql(client, filename);
            if (success) {
                successCount++;
            } else {
                failCount++;
                break; // 실패 시 중단
            }
        }

        console.log('\n' + '='.repeat(50));
        console.log(`✅ Success: ${successCount} files`);
        console.log(`❌ Failed: ${failCount} files`);
        console.log('='.repeat(50));

        if (failCount > 0) {
            console.log('\n⚠️  Migration이 실패했습니다.');
            console.log('💡 오류를 확인하고 다시 시도하거나,');
            console.log('   Supabase Dashboard (https://app.supabase.com) → SQL Editor에서 수동으로 실행해주세요.\n');
            console.log('순서:');
            sqlFiles.forEach((file, index) => {
                console.log(`   ${index + 1}. ${file}`);
            });
            process.exit(1);
        } else {
            console.log('\n🎉 모든 migration이 성공적으로 완료되었습니다!');
            process.exit(0);
        }

    } catch (error) {
        console.error('\n❌ Migration 실행 중 오류 발생:');
        console.error(error.message);
        console.log('\n💡 .env 파일의 DATABASE_URL을 확인해주세요.');
        process.exit(1);

    } finally {
        await client.end();
    }
}

// 실행
runMigrations();
