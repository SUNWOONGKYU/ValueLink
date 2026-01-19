# Project SAL Grid Viewer 구현 가이드

> **목적:** 다른 Claude Code가 이 문서만 보고 SAL Grid Viewer를 처음부터 구현할 수 있도록 함
> **버전:** 2.0 (완전판)
> **최종 수정:** 2025-12-26

---

## 1. 개요

### 1.1 Viewer란?

Project SAL Grid의 Task 목록을 시각화하는 HTML 기반 대시보드입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                      SAL Grid Viewer                        │
├─────────────────────────────────────────────────────────────┤
│  [Stage Tabs]  S1 | S2 | S3 | S4 | S5                       │
├─────────────────────────────────────────────────────────────┤
│  [Stats Bar]   Total: 50 | Completed: 30 | In Progress: 10  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ Task Card        │  │ Task Card        │                 │
│  │ - Task ID        │  │ - Task ID        │                 │
│  │ - Status         │  │ - Status         │                 │
│  │ - Progress       │  │ - Progress       │                 │
│  └──────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 두 가지 방식

| 구분 | DB 방식 | CSV 방식 |
|------|---------|----------|
| **데이터 소스** | Supabase DB (실시간) | 로컬 CSV 파일 (정적) |
| **인터넷 필요** | O | X |
| **실시간 업데이트** | O | X (빌드 필요) |
| **Stage Gate 저장** | DB에 저장 | localStorage |
| **적합 환경** | 온라인, 팀 협업 | 오프라인, 개인 개발 |

### 1.3 Viewer 4종

| 파일명 | 방식 | 플랫폼 | 위치 |
|--------|------|--------|------|
| `viewer_database.html` | DB | PC | S0_Project-SAL-Grid_생성/ |
| `viewer_csv.html` | CSV | PC | S0_Project-SAL-Grid_생성/ |
| `viewer_mobile_database.html` | DB | Mobile | S0_Project-SAL-Grid_생성/ |
| `viewer_mobile_csv.html` | CSV | Mobile | S0_Project-SAL-Grid_생성/ |

---

## 2. 파일 구조

```
프로젝트 루트/
│
├── S0_Project-SAL-Grid_생성/
│   ├── viewer_database.html        ← DB 방식 PC Viewer
│   ├── viewer_csv.html             ← CSV 방식 PC Viewer
│   ├── viewer_mobile_database.html ← DB 방식 Mobile Viewer
│   ├── viewer_mobile_csv.html      ← CSV 방식 Mobile Viewer
│   ├── build-sal-grid-csv.js       ← CSV 빌드 스크립트
│   ├── data/
│   │   └── sal_grid.csv            ← CSV 데이터 파일
│   └── 07_Viewer_Implementation_Guide.md
│
└── index.html                      ← 메인 대시보드 (Viewer 링크 포함)
```

---

## 3. 완전한 CSV 방식 Viewer 구현

### 3.1 전체 HTML 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project SAL Grid Viewer (CSV)</title>
    <!-- 3D View용 Three.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div class="sidebar-overlay" onclick="closeSidebar()"></div>

    <header>
        <button class="close-btn" onclick="window.history.length > 1 ? history.back() : window.close()">✕ 닫기</button>
        <h1>Project SAL Grid Viewer (CSV)</h1>
        <p>로컬 CSV 파일 기반 | 22 Attributes | 5 Stages | 11 Areas</p>
        <div class="view-switch">
            <button class="active" onclick="switchView('2d')">2D Card View</button>
            <button onclick="switchView('3d')">3D Block View</button>
        </div>
        <div class="connection-status">
            <span class="status-dot"></span>
            <span id="connectionStatus">CSV 파일 로딩 준비 중...</span>
        </div>
    </header>

    <!-- 2D View -->
    <div id="view-2d">
        <div class="toolbar">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Task ID 또는 업무명 검색...">
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <div style="display: flex; gap: 5px;">
                    <strong>Task Status:</strong>
                    <button class="filter-btn active" data-filter-type="status" data-filter="all">전체</button>
                    <button class="filter-btn" data-filter-type="status" data-filter="Pending">Pending</button>
                    <button class="filter-btn" data-filter-type="status" data-filter="In Progress">In Progress</button>
                    <button class="filter-btn" data-filter-type="status" data-filter="Executed">Executed</button>
                    <button class="filter-btn" data-filter-type="status" data-filter="Completed">Completed</button>
                </div>
                <div style="display: flex; gap: 5px;">
                    <strong>Verification Status:</strong>
                    <button class="filter-btn active" data-filter-type="verification" data-filter="all">전체</button>
                    <button class="filter-btn" data-filter-type="verification" data-filter="Not Verified">Not Verified</button>
                    <button class="filter-btn" data-filter-type="verification" data-filter="Passed">Passed</button>
                </div>
            </div>
        </div>

        <div class="content-2d">
            <div class="stage-tabs" id="stageTabs"></div>

            <!-- Stage Gate Panel -->
            <div id="stageGatePanel" style="display: none; background: linear-gradient(135deg, #fff9e6 0%, #ffe5b4 100%); border: 2px solid #FFD700; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 id="gateTitle" style="color: #FF8C00;">🔐 Stage Gate</h3>
                    <span id="gateStatusDisplay" style="padding: 6px 12px; border-radius: 20px; background: #fff3cd; color: #856404;">Not Started</span>
                </div>
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    <!-- AI 검증 영역 -->
                    <div style="flex: 1; min-width: 280px; background: white; padding: 15px; border-radius: 10px;">
                        <div style="font-weight: 600; margin-bottom: 10px;">🤖 AI 검증</div>
                        <textarea id="aiVerificationNote" style="width: 100%; min-height: 80px; padding: 8px; border: 1px solid #dee2e6; border-radius: 6px;" placeholder="AI 검증 의견..."></textarea>
                        <input id="aiReportPath" type="text" style="width: 100%; margin-top: 8px; padding: 8px; border: 1px solid #dee2e6; border-radius: 6px;" placeholder="검증 리포트 경로" />
                        <button onclick="saveAIVerification()" style="width: 100%; margin-top: 10px; padding: 10px; background: #2C4A8A; color: white; border: none; border-radius: 6px; cursor: pointer;">💾 AI 검증 저장</button>
                    </div>
                    <!-- PO 승인 영역 -->
                    <div style="flex: 1; min-width: 280px; background: white; padding: 15px; border-radius: 10px;">
                        <div style="font-weight: 600; margin-bottom: 10px;">👤 PO 승인</div>
                        <select id="gateApprovalStatus" style="width: 100%; padding: 8px; border: 1px solid #dee2e6; border-radius: 6px;">
                            <option value="">-- 선택 --</option>
                            <option value="승인">✅ 승인</option>
                            <option value="거부">❌ 거부</option>
                        </select>
                        <input id="gateApprovalUser" type="text" style="width: 100%; margin-top: 8px; padding: 8px; border: 1px solid #dee2e6; border-radius: 6px;" placeholder="승인자" />
                        <textarea id="gateApprovalNote" style="width: 100%; margin-top: 8px; min-height: 60px; padding: 8px; border: 1px solid #dee2e6; border-radius: 6px;" placeholder="승인/거부 사유..."></textarea>
                        <button onclick="submitGateApproval()" style="width: 100%; margin-top: 10px; padding: 10px; background: #FF8C00; color: white; border: none; border-radius: 6px; cursor: pointer;">💾 승인 저장</button>
                    </div>
                </div>
            </div>

            <!-- 통계 바 -->
            <div class="stats-bar" style="margin-bottom: 15px;">
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    <div>Total: <span class="stat-value" id="totalTasks">0</span></div>
                    <div>Pending: <span class="stat-value" id="pendingTasks">0</span></div>
                    <div>In Progress: <span class="stat-value" id="inProgressTasks">0</span></div>
                    <div>Executed: <span class="stat-value" id="executedTasks">0</span></div>
                    <div>Completed: <span class="stat-value" id="completedTasks">0</span></div>
                </div>
            </div>

            <div id="gridContent"></div>
        </div>
    </div>

    <!-- 3D View -->
    <div id="view-3d">
        <div id="info-3d">
            <h2>3D Block View</h2>
            <p><strong>X축</strong>: Stage (1-5)</p>
            <p><strong>Y축</strong>: Task Number</p>
            <p><strong>Z축</strong>: Area (11개)</p>
            <p style="font-size: 0.8em;">드래그: 회전 | 휠: 줌 | 클릭: 상세보기</p>
        </div>
        <div class="controls-3d">
            <button class="btn-3d" onclick="resetCamera()">카메라 리셋</button>
            <button class="btn-3d" onclick="toggleAutoRotate()">자동 회전</button>
        </div>
        <div class="legend-3d">
            <strong>Task Status</strong>
            <div class="legend-item"><div class="legend-color" style="background: #6c757d;"></div>Pending</div>
            <div class="legend-item"><div class="legend-color" style="background: #ffc107;"></div>In Progress</div>
            <div class="legend-item"><div class="legend-color" style="background: #3B82F6;"></div>Executed</div>
            <div class="legend-item"><div class="legend-color" style="background: #28a745;"></div>Completed</div>
        </div>
        <div id="canvas-container"></div>
    </div>

    <!-- Modal -->
    <div class="modal" id="taskPopup" onclick="if(event.target === this) closePopup()">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="popupTitle">Task 상세 (22개 속성)</h2>
                <button class="modal-close-btn" onclick="closePopup()">&times;</button>
            </div>
            <div id="popupContent"></div>
        </div>
    </div>
</body>
</html>
```

---

### 3.2 전체 CSS 스타일

```css
<style>
    :root {
        --primary: #10B981;
        --primary-dark: #059669;
        --secondary: #2C4A8A;
        --secondary-dark: #1F3563;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
        font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
        background: linear-gradient(135deg, var(--secondary) 0%, var(--secondary-dark) 100%);
        overflow-x: hidden;
    }

    /* Header */
    header {
        background: linear-gradient(135deg, var(--secondary) 0%, var(--secondary-dark) 100%);
        color: white;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        position: relative;
    }
    header h1 { font-size: 1.6em; margin-bottom: 10px; }

    .close-btn {
        position: absolute;
        top: 15px;
        right: 20px;
        padding: 10px 14px;
        min-height: 44px;
        border-radius: 4px;
        border: 1px solid rgba(255,255,255,0.5);
        background: rgba(255,255,255,0.15);
        color: white;
        cursor: pointer;
    }
    .close-btn:hover { background: rgba(255,255,255,0.3); }

    /* View Switch */
    .view-switch { display: flex; justify-content: center; gap: 10px; margin-top: 15px; }
    .view-switch button {
        padding: 12px 30px;
        background: rgba(255,255,255,0.2);
        color: white;
        border: 2px solid white;
        border-radius: 25px;
        font-size: 1em;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    .view-switch button.active { background: white; color: var(--secondary); }

    /* Connection Status */
    .connection-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: 600;
        margin-top: 10px;
        background: #ffc107;
        color: #333;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: currentColor;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

    /* 2D View */
    #view-2d { display: block; background: white; min-height: calc(100vh - 200px); }
    #view-2d.hidden { display: none; }

    /* Toolbar */
    .toolbar {
        display: flex;
        gap: 15px;
        padding: 20px;
        background: white;
        flex-wrap: wrap;
        align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .search-box input {
        width: 100%;
        min-width: 250px;
        padding: 12px 20px;
        border: 2px solid #dee2e6;
        border-radius: 25px;
        font-size: 1em;
    }
    .filter-btn {
        padding: 10px 20px;
        border: 2px solid #dee2e6;
        background: white;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .filter-btn.active { background: var(--primary); color: white; border-color: var(--primary); }

    /* Stats Bar */
    .stats-bar {
        display: flex;
        gap: 20px;
        padding: 15px 20px;
        background: #f8f9fa;
        overflow-x: auto;
    }
    .stat-value { font-weight: bold; font-size: 1.1em; color: var(--primary); }

    /* Stage Tabs */
    .content-2d { padding: 20px; }
    .stage-tabs { display: flex; gap: 10px; margin-bottom: 20px; overflow-x: auto; }
    .stage-tab {
        padding: 12px 25px;
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s;
        white-space: nowrap;
    }
    .stage-tab.active { background: var(--primary); color: white; border-color: var(--primary); }
    .stage-tab.gate-tab {
        background: linear-gradient(135deg, #fff9e6 0%, #ffe5b4 100%);
        border-color: #FFD700;
    }
    .stage-tab.gate-tab.approved {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-color: var(--primary);
    }

    /* Area Section */
    .area-section {
        margin-bottom: 25px;
        border: 2px solid #dee2e6;
        border-radius: 15px;
        overflow: hidden;
    }
    .area-header {
        background: linear-gradient(135deg, var(--secondary) 0%, var(--secondary-dark) 100%);
        color: white;
        padding: 15px 20px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .area-content {
        padding: 20px;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
        gap: 20px;
    }
    .area-content.collapsed { display: none; }

    /* Task Card */
    .task-card {
        background: white;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s;
        position: relative;
    }
    .task-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        border-radius: 12px 0 0 12px;
    }
    .task-card.status-Completed::before { background: #28a745; }
    .task-card.status-Executed::before { background: #3B82F6; }
    .task-card.status-In-Progress::before { background: #ffc107; }
    .task-card.status-Pending::before { background: #6c757d; }
    .task-card.status-Fixing::before { background: #dc3545; }
    .task-card:hover { box-shadow: 0 5px 20px rgba(0,0,0,0.15); transform: translateY(-3px); }

    .task-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e9ecef;
    }
    .task-id { font-size: 1.3em; font-weight: bold; color: var(--secondary); }
    .task-status { padding: 5px 12px; border-radius: 15px; font-size: 0.85em; font-weight: bold; }

    .status-Completed { background: #d4edda; color: #155724; }
    .status-Executed { background: #dbeafe; color: #1e40af; }
    .status-In-Progress { background: #fff3cd; color: #856404; }
    .status-Pending { background: #e2e3e5; color: #383d41; }
    .status-Fixing { background: #f8d7da; color: #721c24; }

    .task-title { font-size: 1.15em; font-weight: 600; margin-bottom: 15px; color: #333; }

    .task-attributes { display: grid; gap: 10px; font-size: 0.9em; }
    .attr-row {
        display: grid;
        grid-template-columns: 130px 1fr;
        gap: 10px;
        padding: 8px;
        background: #f8f9fa;
        border-radius: 6px;
    }
    .attr-label { font-weight: 600; color: var(--secondary); }
    .attr-value { color: #333; word-break: break-word; }

    .agent-badge {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        display: inline-block;
    }
    .progress-bar { width: 100%; height: 10px; background: #e9ecef; border-radius: 5px; overflow: hidden; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%); }

    .action-buttons { display: flex; gap: 10px; margin-top: 15px; }
    .action-btn {
        flex: 1;
        padding: 10px 15px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 0.9em;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    .action-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); }
    .action-btn.secondary { background: #6c757d; }

    /* 3D View */
    #view-3d { display: none; position: relative; height: calc(100vh - 150px); }
    #view-3d.active { display: block; }
    #canvas-container { width: 100%; height: 100%; }

    #info-3d {
        position: absolute;
        top: 20px;
        left: 20px;
        background: rgba(0, 0, 0, 0.85);
        padding: 20px;
        border-radius: 10px;
        max-width: 320px;
        color: white;
        border: 2px solid var(--primary);
    }
    #info-3d h2 { color: var(--primary); margin-bottom: 15px; }

    .controls-3d { position: absolute; top: 20px; right: 20px; display: flex; flex-direction: column; gap: 10px; }
    .btn-3d {
        padding: 12px 24px;
        background: rgba(0, 0, 0, 0.85);
        color: white;
        border: 2px solid var(--primary);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .btn-3d:hover { background: var(--primary); }

    .legend-3d {
        position: absolute;
        top: 140px;
        right: 20px;
        background: rgba(0, 0, 0, 0.85);
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    .legend-item { display: flex; align-items: center; gap: 10px; margin: 5px 0; }
    .legend-color { width: 20px; height: 20px; border-radius: 4px; }

    /* Modal */
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        z-index: 1000;
        align-items: center;
        justify-content: center;
    }
    .modal.active { display: flex; }
    .modal-content {
        background: white;
        padding: 30px;
        border-radius: 12px;
        max-width: 900px;
        width: 90%;
        max-height: 85vh;
        overflow-y: auto;
    }
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #e9ecef;
    }
    .modal-header h2 { color: var(--secondary); }
    .modal-close-btn { background: none; border: none; font-size: 2em; color: #6c757d; cursor: pointer; }
    .modal-close-btn:hover { color: #dc3545; }

    /* 모바일 반응형 */
    @media (max-width: 768px) {
        header h1 { font-size: 1.2em; padding: 0 60px; }
        .view-switch button { padding: 8px 16px; font-size: 0.9em; }
        .toolbar { flex-direction: column; gap: 12px; padding: 12px; }
        .search-box input { min-width: 100%; width: 100%; }
        .filter-btn { padding: 8px 12px; font-size: 0.85em; }
        .stage-tabs { flex-wrap: nowrap; overflow-x: auto; }
        .stage-tab { padding: 10px 14px; font-size: 0.85em; }
        .area-content { grid-template-columns: 1fr; }
        .attr-row { grid-template-columns: 1fr; }
        .task-card { padding: 15px; }
        .action-buttons { flex-direction: column; }
        #info-3d { max-width: 200px; padding: 12px; font-size: 0.85em; }
        .controls-3d { top: 10px; right: 10px; }
        .btn-3d { padding: 8px 12px; font-size: 0.85em; }
    }
</style>
```

---

### 3.3 전체 JavaScript 코드

```javascript
<script>
    // ================================================================
    // 상수 정의
    // ================================================================

    // Area 이름 매핑 (11개)
    const AREA_NAMES = {
        'M': 'Documentation (문서화)',
        'U': 'Design (UI/UX 디자인)',
        'F': 'Frontend (프론트엔드)',
        'BI': 'Backend Infrastructure (백엔드 기반)',
        'BA': 'Backend APIs (백엔드 API)',
        'D': 'Database (데이터베이스)',
        'S': 'Security (보안/인증/인가)',
        'T': 'Testing (테스트)',
        'O': 'DevOps (운영/배포)',
        'E': 'External (외부 연동)',
        'C': 'Content System (콘텐츠 시스템)'
    };

    // Stage 이름 매핑 (5개)
    const STAGE_NAMES = {
        1: '개발 준비 (Development Setup)',
        2: '개발 1차 (Core Development)',
        3: '개발 2차 (Advanced Features)',
        4: '개발 3차 (QA & Optimization)',
        5: '운영 (Operations)'
    };

    // ================================================================
    // 전역 변수
    // ================================================================

    let allTasks = [];
    let filteredTasks = [];
    let stageGates = [];
    let currentView = '2d';
    let currentStage = 'all';
    let currentStatusFilter = 'all';
    let currentVerificationFilter = 'all';
    let currentGateStage = null;

    // 3D 관련
    let scene, camera, renderer;
    let taskObjects = [];
    let autoRotate = false;

    // ================================================================
    // View 전환
    // ================================================================

    function switchView(view) {
        currentView = view;
        document.querySelectorAll('.view-switch button').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');

        if (view === '2d') {
            document.getElementById('view-2d').classList.remove('hidden');
            document.getElementById('view-3d').classList.remove('active');
        } else {
            document.getElementById('view-2d').classList.add('hidden');
            document.getElementById('view-3d').classList.add('active');
            if (!scene) init3D();
        }
    }

    // ================================================================
    // CSV 파싱 함수
    // ================================================================

    // CSV 라인 파싱 (쉼표, 따옴표 처리)
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

    // CSV 전체 파싱
    function parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        if (lines.length < 2) return [];

        const headers = parseCSVLine(lines[0]);
        const data = [];

        for (let i = 1; i < lines.length; i++) {
            const values = parseCSVLine(lines[i]);
            const row = {};
            headers.forEach((header, idx) => {
                let value = values[idx] || '';
                // stage, task_progress는 숫자로 변환
                if (header === 'stage' || header === 'task_progress') {
                    value = parseInt(value) || 0;
                }
                row[header] = value;
            });
            data.push(row);
        }

        return data;
    }

    // ================================================================
    // 데이터 로드
    // ================================================================

    async function loadTasks() {
        try {
            document.getElementById('connectionStatus').textContent = 'CSV 파일 로딩 중...';

            // CSV 파일 로드
            const response = await fetch('data/sal_grid.csv');
            if (!response.ok) {
                throw new Error(`CSV 파일 로드 실패: ${response.status}`);
            }

            const csvText = await response.text();
            const data = parseCSV(csvText);

            // 정렬: stage → area → task_id
            data.sort((a, b) => {
                if (a.stage !== b.stage) return a.stage - b.stage;
                if (a.area !== b.area) return a.area.localeCompare(b.area);
                return a.task_id.localeCompare(b.task_id);
            });

            allTasks = data;
            filteredTasks = [...allTasks];
            render2D();
            updateStats();

            document.getElementById('connectionStatus').textContent = `CSV 로드 완료 (${allTasks.length}개 Task)`;
            document.querySelector('.connection-status').style.background = '#28a745';

            stageGates = [];
            renderStageGates();
        } catch (err) {
            console.error('Load error:', err);
            document.getElementById('connectionStatus').textContent = 'CSV 로드 실패: ' + err.message;
            document.querySelector('.connection-status').style.background = '#dc3545';
        }
    }

    function renderStageGates() {
        // CSV 버전에서는 Stage Gate 정보를 localStorage에서 로드
    }

    // ================================================================
    // 2D 렌더링
    // ================================================================

    function render2D() {
        renderStageTabs();
        renderGrid();
    }

    function renderStageTabs() {
        let html = '<button class="stage-tab active" onclick="selectStage(\'all\')">전체</button>';

        for (let s = 1; s <= 5; s++) {
            const count = allTasks.filter(t => t.stage === s).length;
            html += `<button class="stage-tab" onclick="selectStage(${s})">S${s}: ${STAGE_NAMES[s]} (${count})</button>`;
            html += `<button class="stage-tab gate-tab" onclick="showGatePanel(${s})">🔐 Gate ${s}</button>`;
        }

        document.getElementById('stageTabs').innerHTML = html;
    }

    function renderGrid() {
        const gridContent = document.getElementById('gridContent');

        let tasksToShow = filteredTasks.filter(task => {
            const stageMatch = currentStage === 'all' || task.stage === currentStage;
            const statusMatch = currentStatusFilter === 'all' || task.task_status === currentStatusFilter;
            const verificationMatch = currentVerificationFilter === 'all' || task.verification_status === currentVerificationFilter;
            return stageMatch && statusMatch && verificationMatch;
        });

        if (tasksToShow.length === 0) {
            gridContent.innerHTML = '<div style="text-align:center; padding:60px; color:#6c757d;">검색 결과가 없습니다</div>';
            return;
        }

        // Area별 그룹핑
        const groupedByArea = {};
        tasksToShow.forEach(task => {
            if (!groupedByArea[task.area]) groupedByArea[task.area] = [];
            groupedByArea[task.area].push(task);
        });

        // Area 정렬 순서
        const areaOrder = ['M', 'U', 'F', 'BI', 'BA', 'D', 'S', 'T', 'O', 'E', 'C'];
        const sortedAreas = Object.keys(groupedByArea).sort((a, b) => {
            return areaOrder.indexOf(a) - areaOrder.indexOf(b);
        });

        let html = '';
        sortedAreas.forEach(area => {
            const tasks = groupedByArea[area];
            const areaName = AREA_NAMES[area] || area;
            const completed = tasks.filter(t => t.task_status === 'Completed').length;

            html += `
                <div class="area-section">
                    <div class="area-header" onclick="toggleArea('${area}')">
                        <div><strong>${areaName} (${area})</strong></div>
                        <div>전체: ${tasks.length} | 완료: ${completed}</div>
                    </div>
                    <div class="area-content" id="area-${area}">
            `;
            tasks.forEach(task => html += createTaskCard(task));
            html += '</div></div>';
        });

        gridContent.innerHTML = html;
    }

    function createTaskCard(task) {
        const statusClass = task.task_status.replace(' ', '-');
        const progress = task.task_progress || 0;

        return `
            <div class="task-card status-${statusClass}">
                <div class="task-header">
                    <div class="task-id">${task.task_id}</div>
                    <div class="task-status status-${statusClass}">${task.task_status}</div>
                </div>
                <div class="task-title">${task.task_name}</div>

                <div class="task-attributes">
                    <div class="attr-row">
                        <div class="attr-label">Stage</div>
                        <div class="attr-value">S${task.stage}: ${STAGE_NAMES[task.stage]}</div>
                    </div>
                    <div class="attr-row">
                        <div class="attr-label">작업 에이전트</div>
                        <div class="attr-value"><span class="agent-badge">${task.task_agent || '-'}</span></div>
                    </div>
                    <div class="attr-row">
                        <div class="attr-label">의존성</div>
                        <div class="attr-value">${task.dependencies || '없음'}</div>
                    </div>
                    <div class="attr-row">
                        <div class="attr-label">진행률</div>
                        <div class="attr-value">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${progress}%"></div>
                            </div>
                            <small>${progress}%</small>
                        </div>
                    </div>
                    <div class="attr-row">
                        <div class="attr-label">검증 상태</div>
                        <div class="attr-value">${task.verification_status}</div>
                    </div>
                </div>

                <div class="action-buttons">
                    <button class="action-btn" onclick="openFile('${task.task_instruction}')">작업지시서</button>
                    <button class="action-btn secondary" onclick="showFullDetail('${task.task_id}')">전체 속성 (22개)</button>
                </div>
            </div>
        `;
    }

    // ================================================================
    // 통계 업데이트
    // ================================================================

    function updateStats() {
        const tasksForStats = currentStage === 'all'
            ? allTasks
            : allTasks.filter(t => t.stage === currentStage);

        const total = tasksForStats.length;
        const pending = tasksForStats.filter(t => t.task_status === 'Pending').length;
        const inProgress = tasksForStats.filter(t => t.task_status === 'In Progress').length;
        const executed = tasksForStats.filter(t => t.task_status === 'Executed').length;
        const completed = tasksForStats.filter(t => t.task_status === 'Completed').length;

        document.getElementById('totalTasks').textContent = total;
        document.getElementById('pendingTasks').textContent = pending;
        document.getElementById('inProgressTasks').textContent = inProgress;
        document.getElementById('executedTasks').textContent = executed;
        document.getElementById('completedTasks').textContent = completed;
    }

    // ================================================================
    // Stage 선택 및 Area 토글
    // ================================================================

    function selectStage(stage) {
        currentStage = stage;
        document.querySelectorAll('.stage-tab').forEach(tab => tab.classList.remove('active'));
        event.target.classList.add('active');
        hideGatePanel();
        renderGrid();
        updateStats();
    }

    function toggleArea(area) {
        document.getElementById(`area-${area}`).classList.toggle('collapsed');
    }

    // ================================================================
    // Stage Gate 패널
    // ================================================================

    function showGatePanel(stageNum) {
        const panel = document.getElementById('stageGatePanel');
        currentGateStage = stageNum;
        document.getElementById('gateTitle').innerHTML = `🔐 Stage ${stageNum} Gate - ${STAGE_NAMES[stageNum]}`;
        panel.style.display = 'block';
    }

    function hideGatePanel() {
        document.getElementById('stageGatePanel').style.display = 'none';
        currentGateStage = null;
    }

    async function submitGateApproval() {
        if (!currentGateStage) return;

        const status = document.getElementById('gateApprovalStatus').value;
        const user = document.getElementById('gateApprovalUser').value;
        const note = document.getElementById('gateApprovalNote').value;

        if (!status || !user) {
            alert('승인 상태와 승인자를 입력해주세요.');
            return;
        }

        // CSV 버전: localStorage에 저장
        localStorage.setItem(`stage${currentGateStage}_gate`, JSON.stringify({
            approval_status: status === '승인' ? 'Approved' : 'Rejected',
            approval_note: note,
            approval_user: user,
            approval_date: new Date().toISOString()
        }));

        alert(`Stage ${currentGateStage} Gate 승인 정보가 로컬에 저장되었습니다.\n(CSV 버전은 DB 저장을 지원하지 않습니다)`);
    }

    async function saveAIVerification() {
        if (!currentGateStage) return;

        const note = document.getElementById('aiVerificationNote').value;
        const reportPath = document.getElementById('aiReportPath').value;

        if (!note) {
            alert('검증 의견을 입력해주세요.');
            return;
        }

        // CSV 버전: localStorage에 저장
        localStorage.setItem(`stage${currentGateStage}_ai_verification`, JSON.stringify({
            ai_verification_note: note,
            verification_report_path: reportPath,
            ai_verification_date: new Date().toISOString()
        }));

        alert(`Stage ${currentGateStage} AI 검증 정보가 로컬에 저장되었습니다.`);
    }

    // ================================================================
    // 파일 열기 및 상세 보기
    // ================================================================

    function openFile(path) {
        if (!path || path === '-') {
            alert('파일 경로가 없습니다.');
            return;
        }
        alert(`파일: ${path}\n\n실제 프로젝트에서 해당 경로의 파일을 열어주세요.`);
    }

    function showFullDetail(taskId) {
        const task = allTasks.find(t => t.task_id === taskId);
        if (!task) return;

        document.getElementById('popupTitle').textContent = `${task.task_id}: ${task.task_name}`;
        document.getElementById('popupContent').innerHTML = `
            <div class="task-attributes">
                <h3 style="margin: 15px 0 10px; color: #667eea;">[1-4] Basic Info</h3>
                <div class="attr-row"><div class="attr-label">1. Stage</div><div class="attr-value">S${task.stage}: ${STAGE_NAMES[task.stage]}</div></div>
                <div class="attr-row"><div class="attr-label">2. Area</div><div class="attr-value">${task.area}: ${AREA_NAMES[task.area]}</div></div>
                <div class="attr-row"><div class="attr-label">3. Task ID</div><div class="attr-value">${task.task_id}</div></div>
                <div class="attr-row"><div class="attr-label">4. Task Name</div><div class="attr-value">${task.task_name}</div></div>

                <h3 style="margin: 15px 0 10px; color: #667eea;">[5-9] Task Definition</h3>
                <div class="attr-row"><div class="attr-label">5. Task Instruction</div><div class="attr-value">${task.task_instruction || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">6. Task Agent</div><div class="attr-value">${task.task_agent || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">7. Tools</div><div class="attr-value">${task.tools || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">8. Execution Type</div><div class="attr-value">${task.execution_type || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">9. Dependencies</div><div class="attr-value">${task.dependencies || '없음'}</div></div>

                <h3 style="margin: 15px 0 10px; color: #667eea;">[10-13] Task Execution</h3>
                <div class="attr-row"><div class="attr-label">10. Task Progress</div><div class="attr-value">${task.task_progress}%</div></div>
                <div class="attr-row"><div class="attr-label">11. Task Status</div><div class="attr-value">${task.task_status}</div></div>
                <div class="attr-row"><div class="attr-label">12. Generated Files</div><div class="attr-value">${task.generated_files || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">13. Modification History</div><div class="attr-value">${task.modification_history || '-'}</div></div>

                <h3 style="margin: 15px 0 10px; color: #667eea;">[14-15] Verification Definition</h3>
                <div class="attr-row"><div class="attr-label">14. Verification Instruction</div><div class="attr-value">${task.verification_instruction || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">15. Verification Agent</div><div class="attr-value">${task.verification_agent || '-'}</div></div>

                <h3 style="margin: 15px 0 10px; color: #667eea;">[16-19] Verification Execution</h3>
                <div class="attr-row"><div class="attr-label">16. Test</div><div class="attr-value">${task.test || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">17. Build</div><div class="attr-value">${task.build || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">18. Integration</div><div class="attr-value">${task.integration_verification || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">19. Blockers</div><div class="attr-value">${task.blockers || '-'}</div></div>

                <h3 style="margin: 15px 0 10px; color: #667eea;">[20-22] Verification Completion</h3>
                <div class="attr-row"><div class="attr-label">20. Comprehensive</div><div class="attr-value">${task.comprehensive_verification || '-'}</div></div>
                <div class="attr-row"><div class="attr-label">21. Verification Status</div><div class="attr-value">${task.verification_status}</div></div>
                <div class="attr-row"><div class="attr-label">22. Remarks</div><div class="attr-value">${task.remarks || '-'}</div></div>
            </div>
        `;
        document.getElementById('taskPopup').classList.add('active');
    }

    function closePopup() {
        document.getElementById('taskPopup').classList.remove('active');
    }

    // ================================================================
    // 3D View
    // ================================================================

    function init3D() {
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf5f5f5);

        camera = new THREE.PerspectiveCamera(75, window.innerWidth / (window.innerHeight - 150), 0.1, 1000);
        camera.position.set(25, 20, 35);
        camera.lookAt(15, 5, 15);

        renderer = new THREE.WebGLRenderer({ antialias: true });
        const container = document.getElementById('canvas-container');
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        // 조명
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        scene.add(directionalLight);

        // 축
        createAxis(50, 0, 0, 0x00ff00);
        createAxis(0, 50, 0, 0x0000ff);
        createAxis(0, 0, 50, 0xff0000);

        // 마우스 컨트롤
        let isDragging = false, previousMousePosition = { x: 0, y: 0 };

        renderer.domElement.addEventListener('mousedown', (e) => {
            isDragging = true;
            previousMousePosition = { x: e.clientX, y: e.clientY };
        });
        renderer.domElement.addEventListener('mouseup', () => { isDragging = false; });
        renderer.domElement.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;
                camera.position.x += deltaX * 0.05;
                camera.position.y -= deltaY * 0.05;
                camera.lookAt(15, 5, 15);
                previousMousePosition = { x: e.clientX, y: e.clientY };
            }
        });
        renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            camera.position.z += e.deltaY * 0.02;
        });

        // 클릭으로 Task 선택
        renderer.domElement.addEventListener('click', (e) => {
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(taskObjects);

            if (intersects.length > 0) {
                showFullDetail(intersects[0].object.userData.task_id);
            }
        });

        create3DBlocks();
        animate();
    }

    function createAxis(x, y, z, color) {
        const material = new THREE.LineBasicMaterial({ color: color });
        const geometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(x, y, z)
        ]);
        const line = new THREE.Line(geometry, material);
        scene.add(line);
    }

    function create3DBlocks() {
        const areaMap = { 'M': 0, 'U': 1, 'F': 2, 'BI': 3, 'BA': 4, 'D': 5, 'S': 6, 'T': 7, 'O': 8, 'E': 9, 'C': 10 };

        allTasks.forEach(task => {
            const geometry = new THREE.BoxGeometry(3, 3, 3);

            // 상태별 색상
            const colorValue = task.task_status === 'Completed' ? 0x28a745 :
                               task.task_status === 'Executed' ? 0x3B82F6 :
                               task.task_status === 'In Progress' ? 0xffc107 :
                               task.task_status === 'Fixing' ? 0xdc3545 : 0xd0d0d0;

            const material = new THREE.MeshLambertMaterial({ color: colorValue });
            const block = new THREE.Mesh(geometry, material);

            // 위치: X=Stage, Y=같은위치Task수, Z=Area
            const posX = task.stage * 6;
            const sameLocationTasks = allTasks.filter(t =>
                t.stage === task.stage && t.area === task.area &&
                allTasks.indexOf(t) < allTasks.indexOf(task)
            );
            const posY = sameLocationTasks.length * 4;
            const posZ = (areaMap[task.area] || 0) * 4;

            block.position.set(posX, posY, posZ);
            block.userData = task;

            scene.add(block);
            taskObjects.push(block);
        });
    }

    function animate() {
        requestAnimationFrame(animate);
        if (autoRotate) {
            camera.position.x = Math.cos(Date.now() * 0.0005) * 40 + 15;
            camera.position.z = Math.sin(Date.now() * 0.0005) * 40 + 15;
            camera.lookAt(15, 5, 15);
        }
        renderer.render(scene, camera);
    }

    function resetCamera() {
        camera.position.set(25, 20, 35);
        camera.lookAt(15, 5, 15);
    }

    function toggleAutoRotate() {
        autoRotate = !autoRotate;
    }

    // ================================================================
    // 이벤트 리스너
    // ================================================================

    // 검색
    document.getElementById('searchInput').addEventListener('input', (e) => {
        const search = e.target.value.toLowerCase();
        filteredTasks = search ? allTasks.filter(t =>
            t.task_id.toLowerCase().includes(search) ||
            t.task_name.toLowerCase().includes(search)
        ) : [...allTasks];
        renderGrid();
    });

    // 필터
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const filterType = btn.dataset.filterType;
            const filterValue = btn.dataset.filter;

            document.querySelectorAll(`.filter-btn[data-filter-type="${filterType}"]`).forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (filterType === 'status') {
                currentStatusFilter = filterValue;
            } else if (filterType === 'verification') {
                currentVerificationFilter = filterValue;
            }
            renderGrid();
        });
    });

    // 윈도우 리사이즈
    window.addEventListener('resize', () => {
        if (scene) {
            const container = document.getElementById('canvas-container');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }
    });

    // 초기화
    window.onload = loadTasks;
</script>
```

---

## 4. DB 방식 구현 (차이점만)

### 4.1 Supabase 연결 추가

```html
<head>
    <!-- Supabase JS SDK -->
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
</head>
```

```javascript
// Supabase Configuration
const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_KEY = 'your-anon-key';

let supabaseClient = null;
try {
    const { createClient } = supabase;
    supabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY);
} catch (e) {
    console.error('Supabase 연결 실패:', e);
}
```

### 4.2 loadTasks() 함수 (DB 버전)

```javascript
async function loadTasks() {
    if (!supabaseClient) {
        document.getElementById('connectionStatus').textContent = 'Supabase 연결 실패';
        return;
    }

    try {
        const { data, error } = await supabaseClient
            .from('project_sal_grid')
            .select('*')
            .order('stage', { ascending: true })
            .order('area', { ascending: true })
            .order('task_id', { ascending: true });

        if (error) throw error;

        allTasks = data || [];
        filteredTasks = [...allTasks];
        render2D();
        updateStats();

        document.getElementById('connectionStatus').textContent =
            `Supabase 연결됨 (${allTasks.length}개 Task)`;

    } catch (err) {
        console.error('Load error:', err);
    }
}
```

### 4.3 Stage Gate DB 저장 (DB 버전)

```javascript
async function submitGateApproval() {
    const { error } = await supabaseClient
        .from('stage_verification')
        .update({
            po_approval_status: 'Approved',
            po_approval_note: note,
            po_approval_user: user,
            po_approval_date: new Date().toISOString(),
            stage_gate_status: 'Approved'
        })
        .eq('stage_name', `Stage ${currentGateStage}`);

    if (error) throw error;
    await loadStageGates();
}
```

---

## 5. CSV 빌드 스크립트

### 5.1 build-sal-grid-csv.js 전체 코드

```javascript
/**
 * build-sal-grid-csv.js
 * Supabase에서 데이터를 가져와 CSV 파일로 저장
 */

const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../P3_프로토타입_제작/Database/.env') });

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

// CSV 컬럼 정의
const CSV_COLUMNS = [
    'task_id', 'task_name', 'stage', 'area',
    'task_status', 'task_progress', 'verification_status',
    'dependencies', 'task_agent', 'task_instruction',
    'execution_type', 'generated_files', 'remarks'
];

// CSV 이스케이프
function escapeCSV(value) {
    if (value === null || value === undefined) return '';
    const str = String(value);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
}

// Supabase에서 데이터 가져오기
async function fetchFromSupabase(endpoint) {
    const response = await fetch(`${SUPABASE_URL}${endpoint}`, {
        headers: {
            'apikey': SUPABASE_KEY,
            'Authorization': `Bearer ${SUPABASE_KEY}`
        }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
}

// CSV 변환
function convertToCSV(data) {
    const header = CSV_COLUMNS.join(',');
    const rows = data.map(row => {
        return CSV_COLUMNS.map(col => escapeCSV(row[col])).join(',');
    });
    return [header, ...rows].join('\n');
}

// 메인 실행
async function main() {
    console.log('📊 SAL Grid CSV Builder\n');

    try {
        // 데이터 가져오기
        const data = await fetchFromSupabase('/rest/v1/project_sal_grid?select=*&order=stage.asc,task_id.asc');
        console.log(`✅ ${data.length}개 Task 로드`);

        // CSV 변환
        const csv = convertToCSV(data);

        // 저장
        const outputDir = path.join(__dirname, 'data');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        const outputPath = path.join(outputDir, 'sal_grid.csv');
        fs.writeFileSync(outputPath, csv, 'utf-8');

        console.log(`\n✅ 저장 완료: ${outputPath}`);
    } catch (err) {
        console.error('❌ 오류:', err.message);
    }
}

main();
```

### 5.2 실행 방법

```bash
node S0_Project-SAL-Grid_생성/build-sal-grid-csv.js
```

---

## 6. DB 테이블 구조

### 6.1 project_sal_grid 테이블 (22개 컬럼)

| # | 컬럼명 | 타입 | 설명 |
|---|--------|------|------|
| 1 | task_id | text | Primary Key (S1M1, S2F1 등) |
| 2 | task_name | text | Task 이름 |
| 3 | stage | integer | Stage 번호 (1-5) |
| 4 | area | text | Area 코드 (M, U, F, BI, BA, D, S, T, O, E, C) |
| 5 | task_status | text | Pending, In Progress, Executed, Completed, Fixing |
| 6 | task_progress | integer | 진행률 (0-100) |
| 7 | verification_status | text | Not Verified, In Review, Verified, Needs Fix |
| 8 | dependencies | text | 선행 Task ID (쉼표 구분) |
| 9 | task_instruction | text | Task 수행 지침 파일 경로 |
| 10 | task_agent | text | 담당 Agent |
| 11 | tools | text | 사용 도구 |
| 12 | execution_type | text | AI-Only, Human-AI, Human-Assisted |
| 13 | generated_files | text | 생성된 파일 목록 |
| 14 | modification_history | jsonb | 수정 이력 |
| 15 | verification_instruction | text | 검증 지침 파일 경로 |
| 16 | verification_agent | text | 검증 Agent |
| 17 | test | jsonb | 테스트 결과 |
| 18 | build | jsonb | 빌드 결과 |
| 19 | integration_verification | jsonb | 통합 검증 결과 |
| 20 | blockers | jsonb | 차단 요소 |
| 21 | comprehensive_verification | text | 종합 검증 결과 |
| 22 | remarks | text | 비고 |

### 6.2 stage_verification 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| stage_name | text | 'Stage 1' ~ 'Stage 5' |
| stage_gate_status | text | Not Started, AI Verified, Approved, Rejected |
| ai_verification_note | text | AI 검증 의견 |
| ai_verification_date | timestamp | AI 검증 일시 |
| verification_report_path | text | 검증 리포트 경로 |
| po_approval_status | text | PO 승인 상태 |
| po_approval_user | text | 승인자 |
| po_approval_note | text | 승인 의견 |
| po_approval_date | timestamp | 승인 일시 |

---

## 7. 구현 체크리스트

### CSV 방식 체크리스트

- [ ] data/sal_grid.csv 파일 준비
- [ ] parseCSVLine() 함수 구현
- [ ] parseCSV() 함수 구현
- [ ] loadTasks() 함수 구현 (fetch + parse)
- [ ] AREA_NAMES, STAGE_NAMES 상수 정의
- [ ] renderStageTabs() 함수 구현
- [ ] renderGrid() 함수 구현
- [ ] createTaskCard() 함수 구현
- [ ] updateStats() 함수 구현
- [ ] selectStage() 함수 구현
- [ ] toggleArea() 함수 구현
- [ ] showFullDetail() 함수 구현
- [ ] 검색 기능 구현
- [ ] 필터 기능 구현
- [ ] Stage Gate 패널 (localStorage 저장)
- [ ] 3D View (선택)

### DB 방식 추가 체크리스트

- [ ] Supabase JS SDK CDN 추가
- [ ] SUPABASE_URL, SUPABASE_KEY 설정
- [ ] supabaseClient 초기화
- [ ] loadTasks() DB 버전 구현
- [ ] loadStageGates() 구현
- [ ] submitGateApproval() DB 저장 구현

---

## 8. 문제 해결

### CSV 로드 실패

```
원인: 파일 경로 오류 또는 CORS 문제
해결:
1. data/sal_grid.csv 파일 존재 확인
2. 로컬 서버로 실행 (file:// 프로토콜 문제)
   python -m http.server 8000
   또는
   npx serve .
```

### Supabase 연결 실패

```
원인: SUPABASE_KEY가 잘못되었거나 RLS 정책 문제
해결:
1. SUPABASE_URL, SUPABASE_KEY 확인
2. Supabase Dashboard에서 anon key 복사
3. RLS 정책 확인 (SELECT 권한)
```

### 3D View 작동 안 함

```
원인: Three.js 로드 실패
해결:
1. CDN URL 확인
2. 브라우저 콘솔에서 에러 확인
3. WebGL 지원 여부 확인
```

---

**문서 끝**
