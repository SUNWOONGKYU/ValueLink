/**
 * build-sal-grid-csv.js
 *
 * Supabase project_sal_grid 테이블에서 데이터를 가져와 CSV 파일 생성
 * S1~S5 Task 목록을 CSV로 저장
 *
 * 사용법: node build-sal-grid-csv.js
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Supabase 설정
const SUPABASE_URL = 'https://zwjmfewyshhwpgwdtrus.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3am1mZXd5c2hod3Bnd2R0cnVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1NzE1NTEsImV4cCI6MjA3OTE0NzU1MX0.AJy34h5VR8QS6WFEcUcBeJJu8I3bBQ6UCk1I84Wb7y4';

// CSV에 포함할 컬럼
const CSV_COLUMNS = [
    'task_id',
    'task_name',
    'stage',
    'area',
    'task_status',
    'task_progress',
    'verification_status',
    'dependencies',
    'generated_files',
    'remarks'
];

// HTTP 요청 함수
function fetchFromSupabase(endpoint) {
    return new Promise((resolve, reject) => {
        const url = new URL(endpoint, SUPABASE_URL);

        const options = {
            hostname: url.hostname,
            path: url.pathname + url.search,
            method: 'GET',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                'Content-Type': 'application/json'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    resolve(json);
                } catch (e) {
                    reject(new Error('JSON parse error: ' + e.message));
                }
            });
        });

        req.on('error', (e) => {
            reject(e);
        });

        req.end();
    });
}

// CSV 값 이스케이프
function escapeCSV(value) {
    if (value === null || value === undefined) {
        return '';
    }

    const str = String(value);

    // 쉼표, 따옴표, 줄바꿈이 포함되면 따옴표로 감싸기
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return '"' + str.replace(/"/g, '""') + '"';
    }

    return str;
}

// 데이터를 CSV로 변환
function convertToCSV(data) {
    // 헤더
    const header = CSV_COLUMNS.join(',');

    // 데이터 행
    const rows = data.map(row => {
        return CSV_COLUMNS.map(col => escapeCSV(row[col])).join(',');
    });

    return [header, ...rows].join('\n');
}

// 메인 실행
async function main() {
    console.log('📊 SAL Grid CSV Builder\n');
    console.log('Supabase에서 project_sal_grid 데이터 가져오는 중...\n');

    try {
        // Supabase에서 데이터 가져오기
        const endpoint = '/rest/v1/project_sal_grid?select=*&order=stage.asc,task_id.asc';
        const data = await fetchFromSupabase(endpoint);

        if (!Array.isArray(data)) {
            throw new Error('Invalid response from Supabase');
        }

        console.log(`✅ ${data.length}개 Task 로드 완료\n`);

        // Stage별 통계
        const stageStats = {};
        data.forEach(task => {
            const stage = `S${task.stage}`;
            if (!stageStats[stage]) {
                stageStats[stage] = { total: 0, completed: 0 };
            }
            stageStats[stage].total++;
            if (task.task_status === 'Completed') {
                stageStats[stage].completed++;
            }
        });

        console.log('=== Stage별 현황 ===');
        Object.entries(stageStats).forEach(([stage, stats]) => {
            const progress = Math.round(stats.completed / stats.total * 100);
            const status = progress === 100 ? '✅' : progress > 0 ? '🔄' : '⏳';
            console.log(`${status} ${stage}: ${stats.completed}/${stats.total} = ${progress}%`);
        });

        // CSV 변환
        const csv = convertToCSV(data);

        // 저장 (S0_Project-SAL-Grid_생성/data/ 폴더에 저장)
        const outputDir = path.join(__dirname, 'data');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        const outputPath = path.join(outputDir, 'sal_grid.csv');
        fs.writeFileSync(outputPath, csv, 'utf-8');

        console.log(`\n✅ CSV 저장 완료: ${outputPath}`);
        console.log(`   총 ${data.length}개 Task, ${CSV_COLUMNS.length}개 컬럼`);

    } catch (error) {
        console.error('❌ 오류 발생:', error.message);
        process.exit(1);
    }
}

// 실행
main();
