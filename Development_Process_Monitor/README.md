# Development Process Monitor - DB 업로드 방식 (필수)

> 프로젝트 P0~S5 진행률을 사이드바에 표시하는 시스템
> **버전:** 3.0 (DB 업로드 필수)
> **최종 수정일:** 2025-12-31

---

## 개요

Development Process Monitor는 빌드 시점에 진행률을 계산하여 **DB에 업로드**하고, 런타임에 DB에서 조회하여 사이드바에 표시하는 **DB 업로드 방식** 시스템입니다.

> **⚠️ DB 업로드가 필수입니다!**
> - 로컬 JSON만 생성하면 웹에서 개인별 진행률 표시 불가
> - 반드시 DB_Method 설정을 완료해야 함

---

## 핵심 특징

| 항목 | 내용 |
|------|------|
| **방식** | DB 업로드 방식 (Push) |
| **데이터 소스** | Supabase `project_phase_progress` 테이블 |
| **DB 실시간 조회** | **필수** |
| **업데이트 시점** | git commit 시 자동 업로드 |

---

## 데이터 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                    빌드 시점 (Build Time)                        │
│          node Development_Process_Monitor/build-progress.js     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  P0~S0: 폴더/파일 존재 여부로 진행률 계산                         │
│       ↓                                                         │
│  S1~S5: sal_grid.csv에서 Task 완료율로 진행률 계산               │
│       ↓                                                         │
│  프로젝트 루트/data/phase_progress.json 파일 생성 (로컬 백업)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DB 업로드 (필수!)                             │
│          node scripts/upload-progress.js                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  phase_progress.json 읽기                                       │
│       ↓                                                         │
│  Supabase project_phase_progress 테이블에 UPSERT                │
│       ↓                                                         │
│  사용자별 project_id로 구분 저장                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    런타임 시점 (Runtime)                         │
│                    index.html                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  loadProjectProgress() 호출                                     │
│       ↓                                                         │
│  Supabase DB에서 해당 project_id 진행률 조회                    │
│       ↓                                                         │
│  사이드바 진행률 표시                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 관련 파일

| 파일 | 위치 | 역할 |
|------|------|------|
| `build-progress.js` | Development_Process_Monitor/ | 빌드 스크립트 (JSON 생성) |
| `upload-progress.js` | scripts/ (복사) | **DB 업로드 스크립트 (필수!)** |
| `sal_grid.csv` | S0_Project-SAL-Grid_생성/data/ | S1~S5 Task 데이터 (입력) |
| `phase_progress.json` | 프로젝트 루트/data/ | 진행률 데이터 (로컬 백업) |
| `index.html` | 프로젝트 루트 | 사이드바 표시 (DB 조회) |

### DB_Method 파일 (필수 설정)

| 파일 | 역할 |
|------|------|
| `DB_Method/README.md` | DB Method 상세 설명 |
| `DB_Method/create_table.sql` | Supabase 테이블 생성 SQL |
| `DB_Method/upload-progress.js` | DB 업로드 스크립트 (scripts/에 복사) |
| `DB_Method/pre-commit-hook-example.sh` | pre-commit hook 예시 |
| `DB_Method/loadProjectProgress-snippet.js` | index.html 함수 스니펫 |

---

## 1. 빌드 스크립트: build-progress.js

**위치:** `Development_Process_Monitor/build-progress.js`

### 전체 코드

```javascript
/**
 * build-progress.js
 * P0~S0: 폴더/파일 구조에서 진행률 계산
 * S1~S5: sal_grid.csv에서 Task 완료율 계산
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');

// P0~S0 Phase 정의
const PHASES = {
    'P0': { folder: 'P0_작업_디렉토리_구조_생성', name: '작업 디렉토리 구조 생성' },
    'P1': { folder: 'P1_사업계획', name: '사업계획' },
    'P2': { folder: 'P2_프로젝트_기획', name: '프로젝트 기획' },
    'P3': { folder: 'P3_프로토타입_제작', name: '프로토타입 제작' },
    'S0': { folder: 'S0_Project-SAL-Grid_생성', name: 'Project SAL Grid 생성' }
};

// 폴더 안에 파일이 1개 이상 있는지 확인
function hasFiles(folderPath) {
    try {
        const items = fs.readdirSync(folderPath);
        return items.some(item => {
            const itemPath = path.join(folderPath, item);
            try {
                return fs.statSync(itemPath).isFile();
            } catch (e) {
                return false;
            }
        });
    } catch (e) {
        return false;
    }
}

// P0~S0 진행률 계산 (폴더/파일 기반)
function calculatePhaseProgress(phaseCode, phasePath) {
    try {
        const items = fs.readdirSync(phasePath);

        // 하위 폴더 목록 (숨김 폴더 제외)
        const subfolders = items.filter(item => {
            if (item.startsWith('.') || item.startsWith('_')) return false;
            const itemPath = path.join(phasePath, item);
            try {
                return fs.statSync(itemPath).isDirectory();
            } catch (e) {
                return false;
            }
        });

        const total = subfolders.length;
        const completed = subfolders.filter(folder =>
            hasFiles(path.join(phasePath, folder))
        ).length;

        const progress = total > 0 ? Math.round(completed / total * 100) : 0;

        return { completed, total, progress };
    } catch (e) {
        return { completed: 0, total: 0, progress: 0 };
    }
}

// S1~S5 진행률 계산 (CSV 기반)
function calculateStageProgressFromCSV(csvPath) {
    const stageProgress = {
        'S1': { name: '개발 준비', progress: 0, completed: 0, total: 0 },
        'S2': { name: '개발 1차', progress: 0, completed: 0, total: 0 },
        'S3': { name: '개발 2차', progress: 0, completed: 0, total: 0 },
        'S4': { name: '개발 3차', progress: 0, completed: 0, total: 0 },
        'S5': { name: '개발 마무리', progress: 0, completed: 0, total: 0 }
    };

    try {
        if (!fs.existsSync(csvPath)) {
            console.warn('sal_grid.csv not found');
            return stageProgress;
        }

        const csvContent = fs.readFileSync(csvPath, 'utf-8');
        const lines = csvContent.trim().split('\n');

        if (lines.length < 2) return stageProgress;

        // 헤더에서 stage, task_status 인덱스 찾기
        const headers = lines[0].split(',').map(h => h.trim());
        const stageIndex = headers.indexOf('stage');
        const statusIndex = headers.indexOf('task_status');

        if (stageIndex === -1 || statusIndex === -1) return stageProgress;

        // 데이터 파싱
        for (let i = 1; i < lines.length; i++) {
            const values = parseCSVLine(lines[i]);
            const stage = values[stageIndex];
            const status = values[statusIndex];

            const stageKey = `S${stage}`;
            if (stageProgress[stageKey]) {
                stageProgress[stageKey].total++;
                if (status === 'Completed') {
                    stageProgress[stageKey].completed++;
                }
            }
        }

        // 진행률 계산
        Object.keys(stageProgress).forEach(key => {
            const s = stageProgress[key];
            s.progress = s.total > 0 ? Math.round(s.completed / s.total * 100) : 0;
        });

        return stageProgress;
    } catch (e) {
        console.error('Error reading CSV:', e.message);
        return stageProgress;
    }
}

// CSV 라인 파싱 (쉼표 포함 값 처리)
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current.trim());
    return result;
}

// 메인 실행
function main() {
    console.log('📊 Progress Builder\n');

    const result = {
        project_id: 'YOUR_PROJECT',
        updated_at: new Date().toISOString(),
        phases: {}
    };

    // P0~S0 계산
    Object.entries(PHASES).forEach(([code, config]) => {
        const phasePath = path.join(PROJECT_ROOT, config.folder);
        const progress = calculatePhaseProgress(code, phasePath);
        result.phases[code] = {
            name: config.name,
            progress: progress.progress,
            completed: progress.completed,
            total: progress.total
        };
        console.log(`${code}: ${progress.completed}/${progress.total} = ${progress.progress}%`);
    });

    // S1~S5 계산
    const csvPath = path.join(PROJECT_ROOT, 'S0_Project-SAL-Grid_생성', 'data', 'sal_grid.csv');
    const stageProgress = calculateStageProgressFromCSV(csvPath);
    Object.entries(stageProgress).forEach(([code, data]) => {
        result.phases[code] = data;
        console.log(`${code}: ${data.completed}/${data.total} = ${data.progress}%`);
    });

    // JSON 저장 (프로젝트 루트/data/)
    const outputDir = path.join(PROJECT_ROOT, 'data');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    const outputPath = path.join(outputDir, 'phase_progress.json');
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2), 'utf-8');
    console.log(`\n✅ 저장: ${outputPath}`);
}

main();
```

---

## 2. 출력 파일: phase_progress.json

**위치:** `프로젝트 루트/data/phase_progress.json`

### 구조

```json
{
  "project_id": "YOUR_PROJECT",
  "updated_at": "2025-12-26T00:00:00.000Z",
  "phases": {
    "P0": { "name": "작업 디렉토리 구조 생성", "progress": 100, "completed": 2, "total": 2 },
    "P1": { "name": "사업계획", "progress": 100, "completed": 5, "total": 5 },
    "P2": { "name": "프로젝트 기획", "progress": 100, "completed": 8, "total": 8 },
    "P3": { "name": "프로토타입 제작", "progress": 100, "completed": 3, "total": 3 },
    "S0": { "name": "Project SAL Grid 생성", "progress": 100, "completed": 4, "total": 4 },
    "S1": { "name": "개발 준비", "progress": 100, "completed": 9, "total": 9 },
    "S2": { "name": "개발 1차", "progress": 100, "completed": 16, "total": 16 },
    "S3": { "name": "개발 2차", "progress": 100, "completed": 6, "total": 6 },
    "S4": { "name": "개발 3차", "progress": 100, "completed": 21, "total": 21 },
    "S5": { "name": "개발 마무리", "progress": 100, "completed": 9, "total": 9 }
  }
}
```

---

## 3. 사이드바 HTML 구조 (완전판)

### 단일 process-item 구조

```html
<!-- P0 특별단계 (파란색) -->
<div class="process-item">
    <div class="process-special-major" onclick="toggleProcess(this)" data-progress="0">
        <div class="process-header">
            <span class="process-icon">P0.</span>
            <span class="process-name">작업 디렉토리 구조 생성</span>
            <span class="process-arrow">▶</span>
        </div>
        <div class="process-progress-container">
            <div class="process-progress">
                <div class="process-progress-fill" style="width: 0%"></div>
            </div>
            <span class="process-percent">0%</span>
        </div>
    </div>
    <div class="process-small-list">
        <!-- 하위 항목들 -->
    </div>
</div>

<!-- P1~P3, S1~S5 일반단계 (녹색) -->
<div class="process-item">
    <div class="process-major" onclick="toggleProcess(this)" data-progress="0">
        <div class="process-header">
            <span class="process-icon">S1.</span>
            <span class="process-name">개발 준비</span>
            <span class="process-arrow">▶</span>
        </div>
        <div class="process-progress-container">
            <div class="process-progress">
                <div class="process-progress-fill" style="width: 0%"></div>
            </div>
            <span class="process-percent">0%</span>
        </div>
    </div>
    <div class="process-small-list">
        <!-- 하위 항목들 -->
    </div>
</div>
```

### 전체 사이드바 구조

```html
<div class="process-list">
    <!-- P0. 작업 디렉토리 구조 생성 (특별단계) -->
    <div class="process-item">
        <div class="process-special-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">P0.</span>
                <span class="process-name">작업 디렉토리 구조 생성</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- P1 사업계획 -->
    <div class="process-item">
        <div class="process-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">P1.</span>
                <span class="process-name">사업계획</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- P2 프로젝트 기획 -->
    <div class="process-item">
        <div class="process-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">P2.</span>
                <span class="process-name">프로젝트 기획</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- P3. 프로토타입 제작 -->
    <div class="process-item">
        <div class="process-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">P3.</span>
                <span class="process-name">프로토타입 제작</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- S0. Project SAL Grid 생성 (특별단계) -->
    <div class="process-item">
        <div class="process-special-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">S0.</span>
                <span class="process-name">Project SAL Grid 생성</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- S1. 개발 준비 -->
    <div class="process-item">
        <div id="process-s1" class="process-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">S1.</span>
                <span class="process-name">개발 준비</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- S2. 개발 1차 -->
    <div class="process-item">
        <div id="process-s2" class="process-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">S2.</span>
                <span class="process-name">개발 1차</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- S3. 개발 2차 -->
    <div class="process-item">
        <div id="process-s3" class="process-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">S3.</span>
                <span class="process-name">개발 2차</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- S4. 개발 3차 -->
    <div class="process-item">
        <div id="process-s4" class="process-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">S4.</span>
                <span class="process-name">개발 3차</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>

    <!-- S5. 개발 마무리 -->
    <div class="process-item">
        <div id="process-s5" class="process-major" onclick="toggleProcess(this)" data-progress="0">
            <div class="process-header">
                <span class="process-icon">S5.</span>
                <span class="process-name">개발 마무리</span>
                <span class="process-arrow">▶</span>
            </div>
            <div class="process-progress-container">
                <div class="process-progress">
                    <div class="process-progress-fill" style="width: 0%"></div>
                </div>
                <span class="process-percent">0%</span>
            </div>
        </div>
        <div class="process-small-list"></div>
    </div>
</div>
```

---

## 4. CSS 스타일 (완전판)

### CSS 변수

```css
:root {
    --success: #10b981;  /* 녹색 - 일반단계 */
    --primary: #3b82f6;  /* 파란색 - 특별단계 */
}
```

### 기본 process-item 스타일

```css
.process-item {
    margin-bottom: 2px;
}

/* P1~S5 기본 스타일 (녹색) */
.process-major {
    display: flex;
    flex-direction: column;
    gap: 1px;
    padding: 3px 10px;
    background: rgba(16, 185, 129, 0.05);
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}

/* P1~S5 0% 상태: 아주 연한 녹색 */
.process-major[data-progress="0"] {
    background: rgba(16, 185, 129, 0.05) !important;
    border: 1px solid rgba(16, 185, 129, 0.15) !important;
}

/* P1~S5 진행 중 (1-99%): 좀 더 진한 녹색 */
.process-major[data-progress]:not([data-progress="0"]):not(.completed) {
    background: rgba(16, 185, 129, 0.12) !important;
    border: 1px solid rgba(16, 185, 129, 0.3) !important;
}

/* P1~S5 완료 (100%): 더 진한 녹색 */
.process-major.completed {
    background: rgba(16, 185, 129, 0.20) !important;
    border: 1px solid rgba(16, 185, 129, 0.45) !important;
}

/* 호버 시 진한 초록색 */
.process-major:hover {
    background: var(--success) !important;
    color: white !important;
}

.process-major:hover .process-icon,
.process-major:hover .process-status {
    filter: brightness(2);
}
```

### 헤더 스타일

```css
.process-header {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
}

.process-icon {
    font-weight: 600;
    font-size: 12px;
    color: var(--success);
    min-width: 24px;
}

.process-name {
    flex: 1;
    font-size: 12px;
    font-weight: 500;
    color: #374151;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.process-arrow {
    font-size: 10px;
    color: #9ca3af;
    transition: transform 0.2s ease;
}
```

### 진행률 바 스타일

```css
.process-progress-container {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
}

.process-progress {
    flex: 1;
    height: 5px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
}

.process-progress-fill {
    height: 100%;
    background: #34D399;
    transition: width 0.3s ease;
}

.process-percent {
    font-size: 11px;
    font-weight: 500;
    color: #6b7280;
    min-width: 30px;
    text-align: right;
}

/* 진행률 > 0%일 때 퍼센티지 진한 녹색 */
.process-major[data-progress]:not([data-progress="0"]):not(.completed) .process-percent {
    color: var(--success);
    font-weight: 600;
}

.process-major.completed .process-percent {
    color: var(--success);
}

/* 진행률 > 0%일 때 진행률 바 진한 녹색 */
.process-major[data-progress]:not([data-progress="0"]):not(.completed) .process-progress-fill {
    background: var(--success);
}

.process-major.completed .process-progress-fill {
    background: var(--success);
}
```

### 특별단계 스타일 (P0, S0 - 파란색)

```css
/* P0, S0 특별단계: 파란색 계열 */
.process-special-major {
    display: flex;
    flex-direction: column;
    gap: 1px;
    padding: 3px 10px;
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}

/* P0, S0 0% 상태: 회색 */
.process-special-major[data-progress="0"] {
    background: #f8f9fa !important;
    border: 1px solid #dee2e6 !important;
}

.process-special-major[data-progress="0"] .process-icon,
.process-special-major[data-progress="0"] .process-arrow {
    color: #6c757d;
}

.process-special-major[data-progress="0"] .process-progress-fill {
    background: #dee2e6;
}

/* P0, S0 진행 중 (1-99%): 파란색 */
.process-special-major[data-progress]:not([data-progress="0"]):not(.completed) {
    background: rgba(59, 130, 246, 0.12) !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
}

.process-special-major[data-progress]:not([data-progress="0"]):not(.completed) .process-icon,
.process-special-major[data-progress]:not([data-progress="0"]):not(.completed) .process-arrow {
    color: #3b82f6;
}

.process-special-major[data-progress]:not([data-progress="0"]):not(.completed) .process-progress-fill {
    background: #3b82f6;
}

/* P0, S0 완료 (100%): 좀 더 진한 청색 */
.process-special-major.completed {
    background: rgba(59, 130, 246, 0.20) !important;
    border: 1px solid rgba(59, 130, 246, 0.45) !important;
}

.process-special-major.completed .process-icon,
.process-special-major.completed .process-arrow {
    color: #3b82f6;
}

.process-special-major.completed .process-progress-fill {
    background: #3b82f6;
}

/* P0, S0 호버 시 파란색 */
.process-special-major:hover {
    background: #2563eb !important;
    color: white !important;
}

.process-special-major:hover .process-icon,
.process-special-major:hover .process-arrow,
.process-special-major:hover .process-name {
    color: white !important;
}

/* 특별단계 진행률 바 */
.process-special-major .process-progress {
    flex: 1;
    height: 5px;
    background: rgba(37, 99, 235, 0.2);
    border-radius: 4px;
    overflow: hidden;
}

.process-special-major .process-progress-fill {
    height: 100%;
    background: #2563eb;
    border-radius: 4px;
    transition: width 0.3s ease;
}
```

### 반응형 스타일

```css
/* 모바일 */
@media (max-width: 768px) {
    .process-major, .process-special-major {
        padding: 10px 12px;
        min-height: 44px;
    }
    .process-name {
        font-size: 12px;
    }
}

/* 터치 장치 */
@media (hover: none) and (pointer: coarse) {
    .process-major, .process-special-major {
        min-height: 44px;
        display: flex;
        align-items: center;
    }
}
```

---

## 5. JavaScript 함수 (완전판)

### loadPhaseProgressFromDB() - JSON 로드 및 적용

```javascript
async function loadPhaseProgressFromDB(projectId = null) {
    try {
        // JSON 파일에서 진행률 데이터 로드
        const response = await fetch('data/phase_progress.json');
        if (!response.ok) {
            console.warn('📊 phase_progress.json 로드 실패:', response.status);
            resetAllProgressToZero();
            return;
        }

        const jsonData = await response.json();

        // 프로젝트 이름 업데이트
        updateCurrentProjectName(jsonData.project_id || 'YOUR_PROJECT');
        console.log('📊 프로젝트:', jsonData.project_id, '/ 업데이트:', jsonData.updated_at);

        // phases 객체에서 진행률 적용
        if (jsonData.phases) {
            Object.entries(jsonData.phases).forEach(([code, phaseData]) => {
                const progress = phaseData.progress || 0;

                // P0, S0는 특별단계
                if (code === 'P0' || code === 'S0') {
                    updateSpecialProgress(code, progress);
                }
                // P1, P2, P3는 예비단계
                else if (code.startsWith('P')) {
                    updatePrepProgressByCode(code, progress);
                }
                // S1~S5는 개발단계
                else if (code.startsWith('S')) {
                    updateStageProgress(code, progress);
                }
            });
            console.log('📊 Phase 진행률 JSON 로드 완료:', Object.keys(jsonData.phases).length + '개 단계');
        } else {
            console.log('📊 Phase 진행률 데이터 없음');
            resetAllProgressToZero();
        }
    } catch (e) {
        console.warn('Phase 진행률 로드 오류:', e);
        resetAllProgressToZero();
    }
}
```

### updateStageProgress() - 일반단계 업데이트 (P1~P3, S1~S5)

```javascript
function updateStageProgress(stageId, progress) {
    const processItems = document.querySelectorAll('.process-item');
    processItems.forEach(item => {
        const header = item.querySelector('.process-icon');
        if (header && header.textContent.includes(stageId)) {
            const progressFill = item.querySelector('.process-progress-fill');
            const percentText = item.querySelector('.process-percent');
            const majorDiv = item.querySelector('.process-major, .process-special-major');

            if (progressFill) progressFill.style.width = progress + '%';
            if (percentText) percentText.textContent = progress + '%';
            if (majorDiv) {
                majorDiv.setAttribute('data-progress', progress);
                if (progress === 100) {
                    majorDiv.classList.add('completed');
                } else {
                    majorDiv.classList.remove('completed');
                }
            }
        }
    });
}
```

### updateSpecialProgress() - 특별단계 업데이트 (P0, S0)

```javascript
function updateSpecialProgress(stageId, progress) {
    // P0. 또는 S0. 아이콘을 가진 요소 찾기
    const iconText = stageId + '.';
    document.querySelectorAll('.process-special-major').forEach(el => {
        const iconEl = el.querySelector('.process-icon');
        if (iconEl && iconEl.textContent === iconText) {
            el.setAttribute('data-progress', progress);
            const fillEl = el.querySelector('.process-progress-fill');
            if (fillEl) fillEl.style.width = `${progress}%`;
            const percentEl = el.querySelector('.process-percent');
            if (percentEl) percentEl.textContent = `${progress}%`;
            if (progress === 100) {
                el.classList.add('completed');
            } else {
                el.classList.remove('completed');
            }
        }
    });
}
```

### updatePrepProgressByCode() - 예비단계 업데이트

```javascript
function updatePrepProgressByCode(phaseCode, progress) {
    // P1, P2, P3도 updateStageProgress와 동일한 로직 사용
    updateStageProgress(phaseCode, progress);
}
```

### resetAllProgressToZero() - 전체 초기화

```javascript
function resetAllProgressToZero() {
    // 모든 progress-fill 너비를 0%로
    const progressFills = document.querySelectorAll('.process-progress-fill');
    progressFills.forEach(fill => {
        fill.style.width = '0%';
    });

    // 모든 percent 텍스트를 0%로
    const percentTexts = document.querySelectorAll('.process-percent');
    percentTexts.forEach(text => {
        text.textContent = '0%';
    });

    // data-progress도 0으로 + inline style 제거 (CSS가 적용되도록)
    const progressItems = document.querySelectorAll('.process-major, .process-special-major');
    progressItems.forEach(item => {
        item.setAttribute('data-progress', '0');
        // 모든 inline style 제거 (background, backgroundColor, border, borderColor)
        item.style.background = '';
        item.style.backgroundColor = '';
        item.style.border = '';
        item.style.borderColor = '';
    });

    // completed 클래스 제거 (색상 원복)
    const completedItems = document.querySelectorAll('.process-major.completed, .process-special-major.completed');
    completedItems.forEach(item => {
        item.classList.remove('completed');
    });

    console.log('📊 진행 프로세스 0%로 초기화됨');
}
```

### 페이지 로드 시 호출

```javascript
// 페이지 로드 시 진행률 자동 업데이트 (JSON 파일에서 로드)
window.addEventListener('load', () => {
    setTimeout(() => {
        loadPhaseProgressFromDB();
    }, 500);  // JSON 파일은 빠르게 로드 가능
});
```

---

## 6. sal_grid.csv 구조

**위치:** `S0_Project-SAL-Grid_생성/data/sal_grid.csv`

**생성:** build-sal-grid-csv.js 스크립트로 생성 (별도 참조)

| 컬럼 | 설명 | 진행률 계산 사용 |
|------|------|:----------------:|
| task_id | Task ID | |
| task_name | Task 이름 | |
| stage | Stage 번호 (1~5) | ✅ |
| area | Area 코드 | |
| task_status | 작업 상태 | ✅ |
| task_progress | 진행률 | |
| verification_status | 검증 상태 | |
| dependencies | 선행 Task | |
| execution_type | 실행 유형 | |
| remarks | 비고 | |

### 진행률 계산 로직

```
completed = task_status === 'Completed' 인 Task 수
total = 해당 Stage의 전체 Task 수
progress = Math.round(completed / total * 100)
```

---

## 7. 실행 방법

```bash
# 빌드 실행
node Development_Process_Monitor/build-progress.js

# 예상 출력
📊 Progress Builder

P0: 2/2 = 100%
P1: 5/5 = 100%
P2: 8/8 = 100%
P3: 3/3 = 100%
S0: 4/4 = 100%
S1: 9/9 = 100%
S2: 16/16 = 100%
S3: 6/6 = 100%
S4: 21/21 = 100%
S5: 9/9 = 100%

✅ 저장: /프로젝트/data/phase_progress.json
```

**전제 조건:**
- `S0_Project-SAL-Grid_생성/data/sal_grid.csv` 파일이 존재해야 함
- P0~S0 폴더 구조가 존재해야 함

---

## 8. 새 프로젝트 적용 가이드

### Step 1: DB Method 설정 (필수!) ⭐

> **반드시 먼저 설정해야 함!**

1. **테이블 생성**: `DB_Method/create_table.sql`을 Supabase Dashboard에서 실행
2. **환경변수 설정**: 프로젝트 루트에 `.env` 파일 생성
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```
3. **업로드 스크립트 배치**: `DB_Method/upload-progress.js`를 `scripts/`에 복사
4. **pre-commit hook 설정**: `.git/hooks/pre-commit`에 업로드 명령 추가

**상세 설명:** `DB_Method/README.md` 참조

### Step 2: build-progress.js 수정

| 항목 | 위치 | 수정 내용 |
|------|------|----------|
| 프로젝트 ID | `main()` 함수 | `project_id` 값 변경 |
| Phase 폴더명 | `PHASES` 객체 | `folder` 값을 프로젝트 구조에 맞게 변경 |
| Stage 수 | `calculateStageProgressFromCSV()` | `stageProgress` 객체 수정 |
| CSV 경로 | `main()` 함수 | `csvPath` 변수를 프로젝트 구조에 맞게 수정 |
| JSON 출력 경로 | `main()` 함수 | `outputPath` 변수를 원하는 위치로 수정 |

### Step 3: HTML 사이드바 추가

1. 위의 HTML 구조를 index.html에 추가
2. 단계 수에 맞게 process-item 복사/수정

### Step 4: CSS 추가

1. 위의 CSS 스타일을 `<style>` 태그 또는 별도 CSS 파일에 추가

### Step 5: JavaScript 추가 (DB 조회 버전)

1. `DB_Method/loadProjectProgress-snippet.js` 내용을 index.html에 추가
2. 페이지 로드 시 `loadProjectProgress()` 호출 확인

### Step 6: 빌드 및 업로드 확인

```bash
# 빌드 실행
node Development_Process_Monitor/build-progress.js

# DB 업로드 테스트
node scripts/upload-progress.js

# git commit 시 자동 실행되는지 확인
git commit -m "test"
```

---

## 9. 폴더 구조

```
Development_Process_Monitor/
├── build-progress.js                      # 진행률 빌드 스크립트
├── README.md                              # 이 파일 (DB 필수 버전)
├── DEVELOPMENT_PROCESS_WORKFLOW.md        # 개발 프로세스 워크플로우
└── DB_Method/                             # ⭐ DB 업로드 설정 (필수!)
    ├── README.md                          # DB Method 상세 설명
    ├── create_table.sql                   # 테이블 생성 SQL
    ├── upload-progress.js                 # DB 업로드 스크립트
    ├── pre-commit-hook-example.sh         # pre-commit hook 예시
    └── loadProjectProgress-snippet.js     # index.html 함수 스니펫

scripts/
└── upload-progress.js                     # DB_Method에서 복사 (필수!)

data/
└── phase_progress.json                    # 빌드 출력 (로컬 백업)

S0_Project-SAL-Grid_생성/
└── data/
    └── sal_grid.csv                       # S1~S5 진행률 입력
```

---

## 10. 구현 체크리스트

### 빌드 스크립트 (build-progress.js)
- [ ] PHASES 객체에 P0~S0 폴더 매핑
- [ ] calculatePhaseProgress() 함수 구현
- [ ] calculateStageProgressFromCSV() 함수 구현
- [ ] parseCSVLine() 함수 구현 (쉼표 포함 값 처리)
- [ ] JSON 출력 경로 설정

### HTML (index.html)
- [ ] process-list 컨테이너 추가
- [ ] P0, S0 특별단계 (process-special-major) 추가
- [ ] P1~P3, S1~S5 일반단계 (process-major) 추가
- [ ] 각 단계에 process-progress-fill 포함

### CSS
- [ ] CSS 변수 (--success, --primary) 정의
- [ ] process-item 기본 스타일
- [ ] process-major (녹색) 스타일
- [ ] process-special-major (파란색) 스타일
- [ ] data-progress 속성 기반 색상 변화
- [ ] completed 클래스 스타일
- [ ] 호버 스타일

### JavaScript
- [ ] loadPhaseProgressFromDB() 함수
- [ ] updateStageProgress() 함수
- [ ] updateSpecialProgress() 함수
- [ ] updatePrepProgressByCode() 함수
- [ ] resetAllProgressToZero() 함수
- [ ] 페이지 로드 시 loadPhaseProgressFromDB() 호출

### 테스트
- [ ] build-progress.js 실행 → phase_progress.json 생성 확인
- [ ] index.html 로드 → 진행률 표시 확인
- [ ] 진행률 0% → 연한 색상
- [ ] 진행률 1-99% → 중간 색상
- [ ] 진행률 100% → 완료 색상

---

## 11. 트러블슈팅

### 진행률이 표시되지 않음

1. **data/phase_progress.json 파일 확인**
   ```bash
   cat data/phase_progress.json
   ```

2. **브라우저 콘솔 확인**
   - `📊 Phase 진행률 JSON 로드 완료` 메시지 확인
   - 404 에러 시 JSON 파일 경로 확인

3. **CORS 문제 (로컬 파일)**
   - 로컬 서버로 실행 필요
   ```bash
   npx http-server -p 8080
   ```

### 색상이 변경되지 않음

1. **data-progress 속성 확인**
   ```javascript
   document.querySelectorAll('.process-major').forEach(el => {
       console.log(el.getAttribute('data-progress'));
   });
   ```

2. **CSS 우선순위 확인**
   - `!important` 규칙 확인
   - 인라인 스타일 제거

### CSV 파싱 오류

1. **CSV 형식 확인**
   - 쉼표 포함 값은 따옴표로 감싸기
   - 개행 문자 확인

2. **헤더 확인**
   - `stage`, `task_status` 컬럼 존재 확인

---

**작성일:** 2025-12-26
**버전:** 2.0 (완전판)
