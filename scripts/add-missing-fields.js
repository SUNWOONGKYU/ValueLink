/**
 * add-missing-fields.js
 *
 * Grid JSON 파일에 누락된 필드 추가
 * - tools
 * - execution_type
 */

const fs = require('fs');
const path = require('path');

const GRID_RECORDS_PATH = path.join(__dirname, '..', 'Process', 'S0_Project-SAL-Grid_생성', 'method', 'json', 'data', 'grid_records');

// Task별 execution_type 정의
const EXECUTION_TYPES = {
    // S1
    'S1BI1': 'Human-AI',  // Supabase 환경변수 설정 필요
    'S1D1': 'AI-Only',
    'S1M1': 'AI-Only',
    'S1M2': 'AI-Only',

    // S2
    'S2F1': 'AI-Only',
    'S2F2': 'AI-Only',
    'S2F3': 'AI-Only',
    'S2F4': 'AI-Only',
    'S2F5': 'AI-Only',
    'S2F6': 'AI-Only',
    'S2F7': 'AI-Only',
    'S2BA1': 'AI-Only',
    'S2BA2': 'AI-Only',
    'S2BA3': 'AI-Only',
    'S2BA4': 'Human-AI',  // Resend API 키 필요
    'S2M1': 'AI-Only',

    // S3
    'S3BA1': 'AI-Only',
    'S3BA2': 'AI-Only',
    'S3BA3': 'AI-Only',
    'S3BA4': 'AI-Only',

    // S4
    'S4F1': 'AI-Only',
    'S4E1': 'AI-Only',
    'S4E2': 'AI-Only',
    'S4E3': 'AI-Only',
    'S4E4': 'Human-AI',  // Enkino API 설정
    'S4O1': 'Human-AI',  // Vercel Cron 설정

    // S5
    'S5O1': 'Human-AI',  // Vercel 배포, GitHub Actions
    'S5T1': 'AI-Only',
    'S5M1': 'AI-Only'
};

// Task별 tools 정의
const TOOLS = {
    // S1
    'S1BI1': ['Read', 'Write', 'Bash'],
    'S1D1': ['Read', 'Write'],
    'S1M1': ['Read', 'Write', 'Grep'],
    'S1M2': ['Read', 'Write'],

    // S2 Frontend
    'S2F1': ['Read', 'Write'],
    'S2F2': ['Read', 'Write'],
    'S2F3': ['Read', 'Write'],
    'S2F4': ['Read', 'Write'],
    'S2F5': ['Read', 'Write'],
    'S2F6': ['Read', 'Write'],
    'S2F7': ['Read', 'Write'],

    // S2 Backend
    'S2BA1': ['Read', 'Write', 'Task'],
    'S2BA2': ['Read', 'Write'],
    'S2BA3': ['Read', 'Write'],
    'S2BA4': ['Read', 'Write', 'Bash'],
    'S2M1': ['Read', 'Write'],

    // S3
    'S3BA1': ['Read', 'Write'],
    'S3BA2': ['Read', 'Write'],
    'S3BA3': ['Read', 'Write'],
    'S3BA4': ['Read', 'Write'],

    // S4
    'S4F1': ['Read', 'Write'],
    'S4E1': ['Read', 'Write'],
    'S4E2': ['Read', 'Write'],
    'S4E3': ['Read', 'Write', 'Bash'],
    'S4E4': ['Read', 'Write', 'Bash'],
    'S4O1': ['Read', 'Write', 'Bash'],

    // S5
    'S5O1': ['Read', 'Write', 'Bash'],
    'S5T1': ['Read', 'Write', 'Bash'],
    'S5M1': ['Read', 'Write', 'Grep']
};

function updateJsonFiles() {
    console.log('🔄 Grid JSON 파일 업데이트 시작...\n');

    let updatedCount = 0;

    const files = fs.readdirSync(GRID_RECORDS_PATH);

    for (const file of files) {
        if (!file.endsWith('.json') || file.startsWith('_')) {
            continue;
        }

        const filePath = path.join(GRID_RECORDS_PATH, file);
        const taskData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        const taskId = taskData.task_id;

        // tools 추가
        if (!taskData.tools && TOOLS[taskId]) {
            taskData.tools = TOOLS[taskId];
        }

        // execution_type 추가
        if (!taskData.execution_type && EXECUTION_TYPES[taskId]) {
            taskData.execution_type = EXECUTION_TYPES[taskId];
        }

        // 파일 저장 (pretty print)
        fs.writeFileSync(filePath, JSON.stringify(taskData, null, 2), 'utf-8');

        console.log(`✅ ${taskId}: tools=${JSON.stringify(taskData.tools)}, execution_type=${taskData.execution_type}`);
        updatedCount++;
    }

    console.log(`\n✅ ${updatedCount}개 파일 업데이트 완료!`);
}

// 실행
try {
    updateJsonFiles();
} catch (err) {
    console.error('❌ 업데이트 실패:', err.message);
    process.exit(1);
}
