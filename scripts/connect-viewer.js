/**
 * connect-viewer.js
 *
 * GitHub 레포지토리 URL을 SSAL Works users 테이블에 등록
 * "Viewer 연결해줘" 명령어로 실행됨
 *
 * 사용법: node scripts/connect-viewer.js
 *
 * 동작:
 * 1. git remote get-url origin으로 GitHub URL 확인
 * 2. .ssal-project.json에서 owner_email 확인
 * 3. Supabase users 테이블에 github_repo_url UPDATE
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ============================================
// 설정
// ============================================

const PROJECT_ROOT = path.join(__dirname, '..');
const ENV_PATH = path.join(PROJECT_ROOT, '.env');
const PROJECT_CONFIG_PATH = path.join(PROJECT_ROOT, '.ssal-project.json');

// ============================================
// 환경변수 로드
// ============================================

function loadEnv() {
    try {
        if (!fs.existsSync(ENV_PATH)) {
            console.error('❌ .env 파일이 없습니다.');
            console.log('💡 프로젝트 등록 시 자동 생성되는 .env 파일이 필요합니다.');
            process.exit(1);
        }

        const envContent = fs.readFileSync(ENV_PATH, 'utf-8');
        const env = {};

        envContent.split('
').forEach(line => {
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
// .ssal-project.json에서 owner_email 읽기
// ============================================

function getOwnerEmail() {
    try {
        if (!fs.existsSync(PROJECT_CONFIG_PATH)) {
            console.error('❌ .ssal-project.json 파일이 없습니다.');
            console.log('💡 프로젝트 등록 시 자동 생성되는 파일입니다.');
            process.exit(1);
        }

        const config = JSON.parse(fs.readFileSync(PROJECT_CONFIG_PATH, 'utf-8'));

        if (!config.owner_email) {
            console.error('❌ .ssal-project.json에 owner_email이 없습니다.');
            process.exit(1);
        }

        return config.owner_email;
    } catch (e) {
        console.error('❌ .ssal-project.json 읽기 실패:', e.message);
        process.exit(1);
    }
}

// ============================================
// Git Remote URL 확인
// ============================================

function getGitRemoteUrl() {
    try {
        const output = execSync('git remote get-url origin', {
            cwd: PROJECT_ROOT,
            encoding: 'utf-8'
        });

        const url = output.trim();

        if (!url || !url.includes('github.com')) {
            console.error('❌ GitHub 레포지토리가 아닙니다.');
            console.log('💡 GitHub에 레포지토리를 먼저 생성하고 push 해주세요.');
            process.exit(1);
        }

        return url;
    } catch (e) {
        console.error('❌ Git remote URL 확인 실패:', e.message);
        console.log('💡 git remote add origin {GitHub URL}을 먼저 실행해주세요.');
        process.exit(1);
    }
}

// ============================================
// Supabase users 테이블 UPDATE
// ============================================

async function updateGithubUrl(env, ownerEmail, githubUrl) {
    const apiKey = env.SUPABASE_ANON_KEY;

    if (!apiKey) {
        console.error('❌ SUPABASE_ANON_KEY가 .env에 없습니다.');
        process.exit(1);
    }

    const url = `${env.SUPABASE_URL}/rest/v1/users?email=eq.${encodeURIComponent(ownerEmail)}`;
    const headers = {
        'apikey': apiKey,
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    };

    const body = JSON.stringify({
        github_repo_url: githubUrl,
        updated_at: new Date().toISOString()
    });

    try {
        const response = await fetch(url, {
            method: 'PATCH',
            headers: headers,
            body: body
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Supabase UPDATE 실패:', errorText);
            console.log('💡 이메일이 SSAL Works 플랫폼에 등록되어 있는지 확인해주세요.');
            process.exit(1);
        }

        const result = await response.json();

        if (!result || result.length === 0) {
            console.error('❌ 해당 이메일의 사용자를 찾을 수 없습니다.');
            console.log('💡 SSAL Works 플랫폼에서 먼저 회원가입 해주세요.');
            process.exit(1);
        }

        return result[0];
    } catch (e) {
        console.error('❌ Supabase 요청 실패:', e.message);
        process.exit(1);
    }
}

// ============================================
// 메인 실행
// ============================================

async function main() {
    console.log('🔗 Viewer 연결 시작
');

    // 1. 환경변수 로드
    const env = loadEnv();
    if (!env.SUPABASE_URL || !env.SUPABASE_ANON_KEY) {
        console.error('❌ SUPABASE_URL 또는 SUPABASE_ANON_KEY 없음');
        console.log('💡 .env 파일을 확인해주세요.');
        process.exit(1);
    }
    console.log('✅ 환경변수 로드 완료');

    // 2. Owner Email 확인
    const ownerEmail = getOwnerEmail();
    console.log(`📧 Owner Email: ${ownerEmail}`);

    // 3. Git Remote URL 확인
    const githubUrl = getGitRemoteUrl();
    console.log(`🔗 GitHub URL: ${githubUrl}`);

    // 4. Supabase users 테이블 UPDATE
    console.log('
🔄 SSAL Works 플랫폼에 연결 중...');
    const result = await updateGithubUrl(env, ownerEmail, githubUrl);

    console.log('
✅ Viewer 연결 완료!');
    console.log('
📊 이제 SSAL Works 플랫폼에서 프로젝트 진행 현황을 확인할 수 있습니다.');
    console.log('   메인 화면 하단 "Project SAL Grid" 섹션에서');
    console.log('   "{프로젝트명}(진행중) Viewer 열기" 버튼을 클릭하세요.');
}

// 실행
main().catch(e => {
    console.error('❌ 실행 오류:', e.message);
    process.exit(1);
});
