/**
 * upload-progress-ssal.js
 *
 * phase_progress.json을 SSAL Works DB에 자동 업로드
 * Pre-commit Hook에서 자동 실행
 *
 * 사용법: node scripts/upload-progress-ssal.js
 */

const fs = require('fs');
const path = require('path');

// ============================================
// 설정 (SSAL Works)
// ============================================

const SUPABASE_URL = 'https://zwjmfewyshhwpgwdtrus.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3am1mZXd5c2hod3Bnd2R0cnVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzU3MTU1MSwiZXhwIjoyMDc5MTQ3NTUxfQ.ZMNl9_lCJQMG8lC0MEQjHrLEuYbCFJYsVsBIzvwnj1s';
const PROJECT_ID = '2512000006TH-P001';

const PROJECT_ROOT = path.join(__dirname, '..');
const PROGRESS_JSON_PATH = path.join(PROJECT_ROOT, 'Process_Monitor', 'data', 'phase_progress.json');

// ============================================
// phase_progress.json 읽기
// ============================================

function readProgressJson() {
    try {
        if (!fs.existsSync(PROGRESS_JSON_PATH)) {
            console.log('⚠️ phase_progress.json 없음 - build-progress-json.js 먼저 실행');
            return null;
        }
        const content = fs.readFileSync(PROGRESS_JSON_PATH, 'utf-8');
        return JSON.parse(content);
    } catch (e) {
        console.error('❌ phase_progress.json 읽기 실패:', e.message);
        return null;
    }
}

// ============================================
// Supabase 업데이트 (fetch 사용)
// ============================================

async function updateProgress(phaseCode, progress) {
    const url = `${SUPABASE_URL}/rest/v1/project_phase_progress?project_id=eq.${PROJECT_ID}&phase_code=eq.${phaseCode}`;

    try {
        const response = await fetch(url, {
            method: 'PATCH',
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ progress: progress })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`❌ ${phaseCode} 업데이트 실패:`, errorText);
            return false;
        }
        return true;
    } catch (e) {
        console.error(`❌ ${phaseCode} 요청 실패:`, e.message);
        return false;
    }
}

// ============================================
// 메인 실행
// ============================================

async function main() {
    console.log('📤 SSAL Works DB 업로드 시작\n');

    // 1. phase_progress.json 읽기
    const progressData = readProgressJson();
    if (!progressData || !progressData.phases) {
        console.log('⚠️ 업로드할 데이터 없음');
        process.exit(0);
    }

    // 2. 각 Phase 업데이트
    let successCount = 0;
    let totalCount = 0;

    for (const [phaseCode, phaseData] of Object.entries(progressData.phases)) {
        totalCount++;
        const success = await updateProgress(phaseCode, phaseData.progress);
        if (success) {
            successCount++;
            const status = phaseData.progress === 100 ? '✅' : phaseData.progress > 0 ? '🔄' : '⏳';
            console.log(`${status} ${phaseCode}: ${phaseData.progress}%`);
        }
    }

    console.log(`\n📊 업로드 완료: ${successCount}/${totalCount}`);
}

// 실행
main().catch(e => {
    console.error('❌ 실행 오류:', e.message);
    process.exit(1);
});
