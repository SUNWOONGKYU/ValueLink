/**
 * sync-to-root.js
 *
 * Stage folder to Root folder auto-sync script
 * Executed by Pre-commit Hook
 *
 * Mapping (Next.js App Router):
 *   Frontend/ → root (app/, components/, types/ etc.)
 *   Backend_APIs/app/api/ → app/api/
 *   Backend_APIs/lib/ → lib/
 *   Security → api/Security
 *   Backend_Infra → api/Backend_Infra
 *   External → api/External
 *   S0 viewer → viewer
 *   S0 method/json/data → method/json/data
 */

const fs = require('fs');
const path = require('path');

// 프로젝트 루트 경로
const PROJECT_ROOT = path.resolve(__dirname, '..');
const PROCESS_DIR = path.join(PROJECT_ROOT, 'Process');

// Stage 폴더 패턴 (S1 ~ S5)
const STAGE_FOLDERS = [
    'S1_개발_준비',
    'S2_개발-1차',
    'S3_개발-2차',
    'S4_개발-3차',
    'S5_개발_마무리'
];

// Area → Root 매핑 ('' = project root)
const AREA_MAPPING = {
    'Frontend': '',
    'Security': 'api/Security',
    'Backend_Infra': 'api/Backend_Infra',
    'External': 'api/External'
};

// Backend_APIs는 특수 처리 (app/api/ → app/api/, lib/ → lib/)
const BACKEND_API_SUBFOLDERS = {
    'app/api': 'app/api',
    'lib': 'lib'
};

// 콘솔 출력 헬퍼
const log = {
    info: (msg) => console.log(`\x1b[36mℹ️  ${msg}\x1b[0m`),
    success: (msg) => console.log(`\x1b[32m✅ ${msg}\x1b[0m`),
    error: (msg) => console.log(`\x1b[31m❌ ${msg}\x1b[0m`),
    warn: (msg) => console.log(`\x1b[33m⚠️  ${msg}\x1b[0m`),
    header: (msg) => console.log(`\n\x1b[33m${'='.repeat(50)}\n🔄 ${msg}\n${'='.repeat(50)}\x1b[0m\n`)
};

// 디렉토리 재귀 생성
function ensureDir(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

// 파일 복사 (재귀)
function copyRecursive(src, dest, stats = { copied: 0, skipped: 0 }) {
    if (!fs.existsSync(src)) {
        return stats;
    }

    const stat = fs.statSync(src);

    if (stat.isDirectory()) {
        ensureDir(dest);
        const items = fs.readdirSync(src);

        for (const item of items) {
            // 숨김 파일, node_modules 제외
            if (item.startsWith('.') || item === 'node_modules') {
                continue;
            }
            copyRecursive(
                path.join(src, item),
                path.join(dest, item),
                stats
            );
        }
    } else if (stat.isFile()) {
        // 대상 디렉토리 생성
        ensureDir(path.dirname(dest));

        // 파일이 변경되었는지 확인
        let shouldCopy = true;
        if (fs.existsSync(dest)) {
            const srcStat = fs.statSync(src);
            const destStat = fs.statSync(dest);
            // 수정 시간이 같으면 건너뜀
            if (srcStat.mtimeMs <= destStat.mtimeMs) {
                shouldCopy = false;
                stats.skipped++;
            }
        }

        if (shouldCopy) {
            fs.copyFileSync(src, dest);
            stats.copied++;
            log.info(`복사: ${path.relative(PROJECT_ROOT, src)} → ${path.relative(PROJECT_ROOT, dest)}`);
        }
    }

    return stats;
}

// 메인 동기화 함수
function syncToRoot() {
    log.header('Stage → Root 동기화');

    let totalCopied = 0;
    let totalSkipped = 0;

    // S1~S5 Stage 폴더 동기화
    for (const stageFolder of STAGE_FOLDERS) {
        const stagePath = path.join(PROCESS_DIR, stageFolder);

        if (!fs.existsSync(stagePath)) {
            continue;
        }

        // 일반 Area 매핑 (Frontend, Security, Backend_Infra, External)
        for (const [areaFolder, rootTarget] of Object.entries(AREA_MAPPING)) {
            const srcPath = path.join(stagePath, areaFolder);
            const destPath = path.join(PROJECT_ROOT, rootTarget);

            if (!fs.existsSync(srcPath)) {
                continue;
            }

            const stats = copyRecursive(srcPath, destPath);
            totalCopied += stats.copied;
            totalSkipped += stats.skipped;
        }

        // Backend_APIs 특수 처리 (app/api/ → app/api/, lib/ → lib/)
        const backendPath = path.join(stagePath, 'Backend_APIs');
        if (fs.existsSync(backendPath)) {
            for (const [subFolder, rootTarget] of Object.entries(BACKEND_API_SUBFOLDERS)) {
                const srcPath = path.join(backendPath, subFolder);
                const destPath = path.join(PROJECT_ROOT, rootTarget);

                if (!fs.existsSync(srcPath)) {
                    continue;
                }

                const stats = copyRecursive(srcPath, destPath);
                totalCopied += stats.copied;
                totalSkipped += stats.skipped;
            }
        }
    }

    // S0 SAL Grid 동기화 (viewer + JSON)
    log.info('\n🔍 S0 SAL Grid 동기화 중...');
    const s0Path = path.join(PROJECT_ROOT, 'Process', 'S0_Project-SAL-Grid_생성');

    if (fs.existsSync(s0Path)) {
        // viewer 폴더 복사
        const viewerSrc = path.join(s0Path, 'viewer');
        const viewerDest = path.join(PROJECT_ROOT, 'viewer');
        if (fs.existsSync(viewerSrc)) {
            const viewerStats = copyRecursive(viewerSrc, viewerDest);
            totalCopied += viewerStats.copied;
            totalSkipped += viewerStats.skipped;
            log.success(`Viewer 복사: ${viewerStats.copied}개 파일`);
        }

        // method/json/data 폴더 복사
        const jsonSrc = path.join(s0Path, 'method', 'json', 'data');
        const jsonDest = path.join(PROJECT_ROOT, 'method', 'json', 'data');
        if (fs.existsSync(jsonSrc)) {
            const jsonStats = copyRecursive(jsonSrc, jsonDest);
            totalCopied += jsonStats.copied;
            totalSkipped += jsonStats.skipped;
            log.success(`JSON 복사: ${jsonStats.copied}개 파일`);
        }
    } else {
        log.warn('S0 폴더를 찾을 수 없습니다.');
    }

    // 결과 출력
    console.log('\n' + '='.repeat(50));
    console.log('📊 동기화 결과');
    console.log('='.repeat(50));
    console.log(`  복사된 파일: ${totalCopied}개`);
    console.log(`  건너뛴 파일: ${totalSkipped}개 (변경 없음)`);
    console.log('='.repeat(50) + '\n');

    if (totalCopied > 0) {
        log.success(`${totalCopied}개 파일 동기화 완료!`);
    } else {
        log.info('동기화할 변경 사항 없음');
    }

    return true;
}

// 실행
try {
    const success = syncToRoot();
    process.exit(success ? 0 : 1);
} catch (err) {
    log.error(`동기화 실패: ${err.message}`);
    process.exit(1);
}
