/**
 * build-progress-json.js
 *
 * JSON 기반 진행률 계산 (sal_grid.csv 대신 grid_records/*.json 사용)
 *
 * 사용법: node build-progress-json.js
 */

const fs = require('fs');
const path = require('path');

// 프로젝트 루트 경로
const PROJECT_ROOT = path.join(__dirname, '..');

// Phase 정의 (P0~S0) - Process 폴더 안에 있음
const PHASES = {
    'P0': {
        folder: 'Process/P0_작업_디렉토리_구조_생성',
        name: '작업 디렉토리 구조 생성'
    },
    'P1': {
        folder: 'Process/P1_사업계획',
        name: '사업계획'
    },
    'P2': {
        folder: 'Process/P2_프로젝트_기획',
        name: '프로젝트 기획'
    },
    'P3': {
        folder: 'Process/P3_프로토타입_제작',
        name: '프로토타입 제작'
    },
    'S0': {
        folder: 'Process/S0_Project-SAL-Grid_생성',
        name: 'Project SAL Grid 생성'
    }
};

// Stage 정의 (S1~S5)
const STAGES = {
    'S1': { name: '개발 준비', stageNum: 1 },
    'S2': { name: '개발 1차', stageNum: 2 },
    'S3': { name: '개발 2차', stageNum: 3 },
    'S4': { name: '개발 3차', stageNum: 4 },
    'S5': { name: '개발 마무리', stageNum: 5 }
};

// 폴더 안에 파일이 1개 이상 있는지 확인
function hasFiles(folderPath) {
    try {
        const items = fs.readdirSync(folderPath);
        return items.some(item => {
            const itemPath = path.join(folderPath, item);
            try {
                const stats = fs.statSync(itemPath);
                if (stats.isFile() && !item.startsWith('.') && !item.startsWith('_')) {
                    return true;
                }
                if (stats.isDirectory() && !item.startsWith('.') && !item.startsWith('_')) {
                    return hasFiles(itemPath);
                }
                return false;
            } catch (e) {
                return false;
            }
        });
    } catch (e) {
        return false;
    }
}

// Phase 진행률 계산 (폴더 기반)
function calculatePhaseProgress(phaseCode, phasePath) {
    try {
        if (!fs.existsSync(phasePath)) {
            return { completed: 0, total: 0, progress: 0 };
        }

        const items = fs.readdirSync(phasePath);
        const subfolders = items.filter(item => {
            if (item.startsWith('.') || item.startsWith('_')) return false;
            const itemPath = path.join(phasePath, item);
            try {
                return fs.statSync(itemPath).isDirectory();
            } catch (e) {
                return false;
            }
        });

        if (subfolders.length === 0) {
            // 파일 기반
            const files = items.filter(item => {
                if (item.startsWith('.') || item.startsWith('_')) return false;
                try {
                    return fs.statSync(path.join(phasePath, item)).isFile();
                } catch (e) {
                    return false;
                }
            });
            const completed = files.filter(f => {
                try {
                    return fs.statSync(path.join(phasePath, f)).size > 0;
                } catch (e) {
                    return false;
                }
            }).length;
            return {
                completed,
                total: files.length,
                progress: files.length > 0 ? Math.round(completed / files.length * 100) : 0
            };
        }

        // 폴더 기반
        const completed = subfolders.filter(folder => hasFiles(path.join(phasePath, folder))).length;
        return {
            completed,
            total: subfolders.length,
            progress: subfolders.length > 0 ? Math.round(completed / subfolders.length * 100) : 0
        };
    } catch (e) {
        console.error(`Error calculating progress for ${phaseCode}:`, e.message);
        return { completed: 0, total: 0, progress: 0 };
    }
}

// JSON 파일에서 S1~S5 진행률 계산
function calculateStageProgressFromJSON() {
    const stageProgress = {};
    Object.entries(STAGES).forEach(([code, config]) => {
        stageProgress[code] = { name: config.name, progress: 0, completed: 0, total: 0 };
    });

    // JSON 파일 경로들 (우선순위)
    const jsonPaths = [
        path.join(PROJECT_ROOT, 'method', 'json', 'data'),
        path.join(PROJECT_ROOT, 'Process', 'S0_Project-SAL-Grid_생성', 'method', 'json', 'data')
    ];

    let gridRecordsPath = null;
    for (const basePath of jsonPaths) {
        const testPath = path.join(basePath, 'grid_records');
        if (fs.existsSync(testPath)) {
            gridRecordsPath = testPath;
            break;
        }
    }

    if (!gridRecordsPath) {
        console.warn('grid_records 폴더를 찾을 수 없습니다.');
        return stageProgress;
    }

    console.log(`JSON 경로: ${gridRecordsPath}`);

    try {
        const files = fs.readdirSync(gridRecordsPath);
        const jsonFiles = files.filter(f => f.endsWith('.json') && !f.startsWith('_'));

        jsonFiles.forEach(file => {
            try {
                const filePath = path.join(gridRecordsPath, file);
                const content = fs.readFileSync(filePath, 'utf-8');
                const task = JSON.parse(content);

                const stageNum = task.stage;
                const stageKey = `S${stageNum}`;

                if (stageProgress[stageKey]) {
                    stageProgress[stageKey].total++;
                    if (task.task_status === 'Completed') {
                        stageProgress[stageKey].completed++;
                    }
                }
            } catch (e) {
                // Skip invalid JSON files
            }
        });

        // 진행률 계산
        Object.keys(stageProgress).forEach(key => {
            const s = stageProgress[key];
            s.progress = s.total > 0 ? Math.round(s.completed / s.total * 100) : 0;
        });

        return stageProgress;
    } catch (e) {
        console.error('Error reading JSON files:', e.message);
        return stageProgress;
    }
}

// 메인 실행
function main() {
    console.log('📊 Progress Builder (JSON 버전) - P0~S5 진행률 계산\n');

    const result = {
        project_id: 'ValueLink',
        updated_at: new Date().toISOString(),
        phases: {}
    };

    // P0~S0 진행률 계산 (폴더/파일 기반)
    console.log('=== P0~S0 (폴더/파일 기반) ===');
    Object.entries(PHASES).forEach(([code, config]) => {
        const phasePath = path.join(PROJECT_ROOT, config.folder);
        const progress = calculatePhaseProgress(code, phasePath);

        result.phases[code] = {
            name: config.name,
            progress: progress.progress,
            completed: progress.completed,
            total: progress.total
        };

        const status = progress.progress === 100 ? '✅' : progress.progress > 0 ? '🔄' : '⏳';
        console.log(`${status} ${code}: ${progress.completed}/${progress.total} = ${progress.progress}%`);
    });

    // S1~S5 진행률 계산 (JSON 기반)
    console.log('\n=== S1~S5 (JSON 기반) ===');
    const stageProgress = calculateStageProgressFromJSON();

    Object.entries(stageProgress).forEach(([code, data]) => {
        result.phases[code] = {
            name: data.name,
            progress: data.progress,
            completed: data.completed,
            total: data.total
        };

        const status = data.progress === 100 ? '✅' : data.progress > 0 ? '🔄' : '⏳';
        console.log(`${status} ${code}: ${data.completed}/${data.total} = ${data.progress}%`);
    });

    // JSON 파일 저장
    const outputDir = path.join(__dirname, 'data');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const outputPath = path.join(outputDir, 'phase_progress.json');
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2), 'utf-8');
    console.log(`\n✅ 저장 완료: ${outputPath}`);

    // 루트 method/json/data에도 저장 (GitHub용)
    const githubOutputPath = path.join(PROJECT_ROOT, 'method', 'json', 'data', 'phase_progress.json');
    fs.writeFileSync(githubOutputPath, JSON.stringify(result, null, 2), 'utf-8');
    console.log(`✅ GitHub용 저장: ${githubOutputPath}`);

    return result;
}

// 실행
main();
