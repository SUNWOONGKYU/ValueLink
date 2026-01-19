/**
 * upload-progress.js
 *
 * phase_progress.json을 읽어서 Supabase project_phase_progress 테이블에 업로드
 * Pre-commit Hook에서 자동 호출됨
 *
 * 사용법: node scripts/upload-progress.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ============================================
// 설정
// ============================================

const PROJECT_ROOT = path.join(__dirname, '..');
const PROGRESS_JSON_PATH = path.join(PROJECT_ROOT, 'Development_Process_Monitor', 'data', 'phase_progress.json');
const ENV_PATH = path.join(PROJECT_ROOT, 'P3_프로토타입_제작', 'Database', '.env');

// ============================================
// 환경변수 로드
// ============================================

function loadEnv() {
    try {
        const envContent = fs.readFileSync(ENV_PATH, 'utf-8');
        const env = {};

        envContent.split('\n').forEach(line => {
            const trimmed = line.trim();
            if (trimmed && !trimmed.startsWith('#')) {
                const [key, ...valueParts] = trimmed.split('=');
                if (key && valueParts.length > 0) {
                    env[key.trim()] = valueParts.join('=').trim();
                }
            }
        });

        return env;
    } catch (e) {
        console.error('❌ .env 파일 로드 실패:', e.message);
        process.exit(1);
    }
}

// ============================================
// Git 사용자 이메일 가져오기
// ============================================

function getGitUserEmail() {
    try {
        const email = execSync('git config user.email', { encoding: 'utf-8' }).trim();
        return email || 'unknown@localhost';
    } catch (e) {
        console.warn('⚠️ Git user.email 가져오기 실패, 기본값 사용');
        return 'unknown@localhost';
    }
}

// ============================================
// Project ID 생성 (이메일 기반)
// ============================================

function generateProjectId(email) {
    // 이메일에서 @ 앞 부분 추출
    const username = email.split('@')[0] || 'user';
    // 날짜 (YYMMDD 형식)
    const date = new Date().toISOString().slice(2, 10).replace(/-/g, '');
    // Project ID: {email_prefix}_{date}
    return `${username}_PROJECT`;
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
// Supabase UPSERT (REST API)
// ============================================

async function upsertToSupabase(env, projectId, phases) {
    const url = `${env.SUPABASE_URL}/rest/v1/project_phase_progress?on_conflict=project_id,phase_code`;
    const headers = {
        'apikey': env.SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal,resolution=merge-duplicates'
    };

    // 각 Phase별로 UPSERT
    const results = [];

    for (const [phaseCode, phaseData] of Object.entries(phases)) {
        const record = {
            project_id: projectId,
            phase_code: phaseCode,
            phase_name: phaseData.name,
            progress: phaseData.progress,
            completed_items: phaseData.completed,
            total_items: phaseData.total,
            status: phaseData.progress === 100 ? 'completed' : phaseData.progress > 0 ? 'in_progress' : 'pending',
            updated_at: new Date().toISOString()
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(record)
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ ${phaseCode} UPSERT 실패:`, errorText);
                results.push({ phase: phaseCode, success: false, error: errorText });
            } else {
                results.push({ phase: phaseCode, success: true });
            }
        } catch (e) {
            console.error(`❌ ${phaseCode} 요청 실패:`, e.message);
            results.push({ phase: phaseCode, success: false, error: e.message });
        }
    }

    return results;
}

// ============================================
// 메인 실행
// ============================================

async function main() {
    console.log('📤 Progress Uploader - DB 업로드 시작\n');

    // 1. 환경변수 로드
    const env = loadEnv();
    if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY) {
        console.error('❌ SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY 없음');
        process.exit(1);
    }
    console.log('✅ 환경변수 로드 완료');

    // 2. Git 사용자 이메일 가져오기
    const email = getGitUserEmail();
    const projectId = generateProjectId(email);
    console.log(`📧 사용자: ${email}`);
    console.log(`🆔 Project ID: ${projectId}`);

    // 3. phase_progress.json 읽기
    const progressData = readProgressJson();
    if (!progressData || !progressData.phases) {
        console.log('⚠️ 업로드할 데이터 없음 - 종료');
        process.exit(0);
    }
    console.log(`📊 Phase 데이터: ${Object.keys(progressData.phases).length}개`);

    // 4. Supabase에 업로드
    console.log('\n🔄 Supabase에 업로드 중...');
    const results = await upsertToSupabase(env, projectId, progressData.phases);

    // 5. 결과 출력
    const successCount = results.filter(r => r.success).length;
    const failCount = results.filter(r => !r.success).length;

    console.log(`\n📊 업로드 결과: ${successCount}/${results.length} 성공`);

    if (failCount > 0) {
        console.log(`⚠️ 실패: ${failCount}개`);
        results.filter(r => !r.success).forEach(r => {
            console.log(`   - ${r.phase}: ${r.error}`);
        });
    }

    console.log('\n✅ Progress 업로드 완료');
}

// 실행
main().catch(e => {
    console.error('❌ 실행 오류:', e.message);
    process.exit(1);
});
