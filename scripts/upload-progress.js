/**
 * upload-progress.js
 *
 * phase_progress.json을 읽어서 SSAL Works Supabase에 업로드
 * SSAL Works 플랫폼(ssalworks.com)에서 진행률 표시용
 * Pre-commit Hook에서 자동 호출됨
 *
 * 사용법: node scripts/upload-progress.js
 */

const fs = require('fs');
const path = require('path');

// ============================================
// 설정
// ============================================

const PROJECT_ROOT = path.join(__dirname, '..');
const PROGRESS_JSON_PATH = path.join(PROJECT_ROOT, 'Process_Monitor', 'data', 'phase_progress.json');
const SSAL_PROJECT_PATH = path.join(PROJECT_ROOT, '.ssal-project.json');

// SSAL Works Supabase 설정 (고정)
const SUPABASE_URL = 'https://zwjmfewyshhwpgwdtrus.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3am1mZXd5c2hod3Bnd2R0cnVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzU3MTU1MSwiZXhwIjoyMDc5MTQ3NTUxfQ.ZMNl9_lCJQMG8lC0MEQjHrLEuYbCFJYsVsBIzvwnj1s';

// ============================================
// .ssal-project.json에서 Project ID 읽기
// ============================================

function getProjectId() {
    try {
        if (!fs.existsSync(SSAL_PROJECT_PATH)) {
            console.error('❌ .ssal-project.json 없음');
            process.exit(1);
        }
        const content = fs.readFileSync(SSAL_PROJECT_PATH, 'utf-8');
        const config = JSON.parse(content);

        if (!config.project_id) {
            console.error('❌ .ssal-project.json에 project_id 없음');
            process.exit(1);
        }
        return config.project_id;
    } catch (e) {
        console.error('❌ .ssal-project.json 읽기 실패:', e.message);
        process.exit(1);
    }
}

// ============================================
// phase_progress.json 읽기
// ============================================

function readProgressJson() {
    try {
        if (!fs.existsSync(PROGRESS_JSON_PATH)) {
            console.log('⚠️ phase_progress.json 없음 - build-progress.js 먼저 실행 필요');
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
// SSAL Works DB 업로드
// ============================================

async function uploadToSSALWorks(projectId, phases) {
    const results = [];

    for (const [phaseCode, phaseData] of Object.entries(phases)) {
        const url = `${SUPABASE_URL}/rest/v1/project_phase_progress?project_id=eq.${projectId}&phase_code=eq.${phaseCode}`;

        try {
            const response = await fetch(url, {
                method: 'PATCH',
                headers: {
                    'apikey': SUPABASE_KEY,
                    'Authorization': `Bearer ${SUPABASE_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ progress: phaseData.progress })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ ${phaseCode} 업로드 실패:`, errorText);
                results.push({ phase: phaseCode, success: false });
            } else {
                results.push({ phase: phaseCode, success: true });
            }
        } catch (e) {
            console.error(`❌ ${phaseCode} 요청 실패:`, e.message);
            results.push({ phase: phaseCode, success: false });
        }
    }

    return results;
}

// ============================================
// 메인 실행
// ============================================

async function main() {
    console.log('📤 SSAL Works 진행률 업로드\n');

    // 1. Project ID 가져오기
    const projectId = getProjectId();
    console.log(`🆔 Project ID: ${projectId}`);

    // 2. phase_progress.json 읽기
    const progressData = readProgressJson();
    if (!progressData || !progressData.phases) {
        console.log('⚠️ 업로드할 데이터 없음');
        process.exit(0);
    }
    console.log(`📊 Phase 데이터: ${Object.keys(progressData.phases).length}개\n`);

    // 3. SSAL Works DB에 업로드
    const results = await uploadToSSALWorks(projectId, progressData.phases);

    // 4. 결과 출력
    const successCount = results.filter(r => r.success).length;
    results.forEach(r => {
        const status = r.success ? '✅' : '❌';
        console.log(`${status} ${r.phase}`);
    });

    console.log(`\n📊 업로드 완료: ${successCount}/${results.length}`);
}

// 실행
main().catch(e => {
    console.error('❌ 실행 오류:', e.message);
    process.exit(1);
});
