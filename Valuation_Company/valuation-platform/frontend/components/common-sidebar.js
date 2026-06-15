/**
 * Common Sidebar Component
 * 15단계 프로세스 사이드바 동적 생성
 *
 * 역할별 접근 제어:
 * - customer (고객 기업): 고객 액션 단계만 클릭 가능, 내부 단계는 프로세스만 표시
 * - accountant (회계사): 내부 단계도 클릭하여 작업 가능
 * - admin (관리자): 모든 단계 클릭 가능
 */

/**
 * 관리자 이메일 목록
 * ⚠️ 클라이언트에 관리자 이메일을 하드코딩하지 않는다(PII 노출 + 클라이언트 역할 판별 금지).
 * 역할은 DB(users.role)와 로그인 시 저장된 localStorage('userRole')로만 결정한다.
 */
const ADMIN_EMAILS = [];

/**
 * 회계사 이메일 목록 (하드코딩)
 */
const ACCOUNTANT_EMAILS = [];

/**
 * 이메일 기반 역할 판별
 * @param {string} email - 사용자 이메일
 * @returns {string} 'admin' | 'accountant' | 'customer'
 */
function getRoleByEmail(email) {
    if (!email) return 'customer';
    const lowerEmail = email.toLowerCase();
    if (ADMIN_EMAILS.includes(lowerEmail)) return 'admin';
    if (ACCOUNTANT_EMAILS.includes(lowerEmail)) return 'accountant';
    return 'customer';
}

/**
 * 현재 사용자 역할 감지 (동기)
 * localStorage 캐시 → ADMIN_EMAILS 폴백 순으로 확인
 * @returns {string} 'admin' | 'accountant' | 'customer'
 */
export function getUserRole() {
    try {
        if (localStorage.getItem('loggedOut')) return 'customer';
        const stored = localStorage.getItem('userRole');
        if (stored && ['admin', 'accountant', 'customer'].includes(stored)) {
            return stored;
        }
    } catch (e) {}
    return 'customer';
}

/**
 * Supabase 세션에서 이메일 확인하여 역할 감지 (비동기)
 * 페이지 로드 시 호출하여 localStorage에 역할 저장
 * @returns {Promise<string>} 역할
 */
export async function detectAndStoreUserRole() {
    try {
        // Supabase 세션에서 이메일 가져오기
        const { createClient } = await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm');
        const supabase = createClient(
            'https://arxrfetgaitkgiiqabap.supabase.co',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0'
        );
        const { data: { session } } = await supabase.auth.getSession();

        if (session && session.user && session.user.email) {
            const role = getRoleByEmail(session.user.email);
            localStorage.setItem('userRole', role);
            localStorage.setItem('userEmail', session.user.email);
            return role;
        }
    } catch (e) {
        console.warn('Supabase 세션 확인 실패, 기존 역할 유지:', e.message);
    }

    return getUserRole();
}

/**
 * 평가법 이름 매핑
 */
const METHOD_NAMES = {
    dcf: 'DCF평가법',
    relative: '상대가치평가법',
    intrinsic: '본질가치평가법',
    asset: '자산가치평가법',
    inheritance_tax: '상증세법평가법'
};

/**
 * 상태 정보 표시
 */
function getStatusDisplay(status) {
    const statusMap = {
        'not_requested': { text: '미신청', color: '#6B7280', icon: '⏸' },
        'pending': { text: '승인 대기', color: '#F59E0B', icon: '⏳' },
        'approved': { text: '승인됨', color: '#10B981', icon: '✅' },
        'in_progress': { text: '진행 중', color: '#3B82F6', icon: '⚡' },
        'completed': { text: '완료', color: '#166534', icon: '🎉' }
    };
    return statusMap[status] || statusMap['not_requested'];
}

/**
 * 15단계 프로세스 정의
 */
/**
 * 역할별 접근 규칙:
 * - visible: true  → 고객 액션 단계 (고객이 직접 수행)
 * - visible: false → 내부 프로세스 단계 (회계사/시스템 작업)
 *
 * 모든 사용자가 15단계 전체 프로세스를 볼 수 있음.
 * 단, 내부 단계(visible:false)는 회계사/관리자만 클릭하여 접근 가능.
 * 고객에게는 내부 단계가 "진행 상태 표시"로만 보임 (클릭 불가).
 */

const PROCESS_STEPS = [
    // --- 고객에게 보이는 단계 ---
    { step: 1,  name: '서비스 안내문 보기',           page: 'guide',              visible: true },
    { step: 2,  name: '평가 신청하기',               page: 'project-create',      visible: true },
    { step: 3,  name: '관리자 승인 확인하기',         page: 'approval-waiting',    visible: true },
    { step: 4,  name: '계약금 결제하기',             page: 'deposit-payment',     visible: true },
    { step: 5,  name: '평가 기초자료 제출하기',       page: 'portal',             visible: true },
    // --- 내부 프로세스 (고객에게 숨김) ---
    { step: 6,  name: '데이터 수집 중',              page: 'data-collection',     visible: false },
    { step: 7,  name: '평가 진행 중',               page: 'evaluation-progress', visible: false },
    { step: 8,  name: '공인회계사 검토 중',           page: 'accountant-review',   visible: false },
    { step: 9,  name: '평가보고서 초안 생성',         page: 'draft-generation',    visible: false },
    // --- 고객에게 보이는 단계 ---
    { step: 10, name: '평가보고서 초안 확인하기',     page: 'report-draft',    visible: true },
    { step: 11, name: '평가보고서 초안 수정 요청하기', page: 'revision-request',    visible: true },
    // --- 내부 프로세스 (고객에게 숨김) ---
    { step: 12, name: '평가보고서 최종안 작성',       page: 'final-preparation',   visible: false },
    // --- 고객에게 보이는 단계 ---
    { step: 13, name: '평가보고서 최종안 확인하기',   page: 'report-final',    visible: true },
    { step: 14, name: '잔금 결제하기',               page: 'balance-payment',     visible: true },
    { step: 15, name: '평가보고서 수령하기',          page: 'report-download',     visible: true }
];

/**
 * 현재 경로에서 app 폴더까지의 상대 경로 계산
 * @returns {string} basePath
 */
function getBasePath() {
    const currentPath = window.location.pathname;

    if (currentPath.includes('/valuation/guides/')) {
        return '../../';  // guides -> valuation -> app
    } else if (currentPath.includes('/valuation/results/')) {
        return '../../';  // results -> valuation -> app
    } else if (currentPath.includes('/valuation/portals/')) {
        return '../../';  // portals -> valuation -> app
    } else if (currentPath.includes('/valuation/submissions/')) {
        return '../../';  // submissions -> valuation -> app
    } else if (currentPath.includes('/valuation/')) {
        return '../';     // valuation -> app
    } else if (currentPath.includes('/app/')) {
        return '';        // app 폴더 내부
    } else {
        return 'app/';    // app 폴더 외부
    }
}

/**
 * 단계별 URL 생성
 * @param {object} stepInfo - 단계 정보 객체
 * @param {string} method - 평가법 코드 (dcf, relative 등)
 * @param {string} projectId - 프로젝트 ID
 * @returns {string|null} URL 또는 null
 */
function getStepUrl(stepInfo, method, projectId) {
    const { page, params } = stepInfo;

    const basePath = getBasePath();

    // 페이지별 URL 매핑
    switch (page) {
        case 'guide':
            // 1단계: 서비스 안내
            return basePath + 'service-guide.html';

        case 'project-create':
            // 2단계: 평가 신청
            return basePath + 'projects/project-create.html';

        case 'approval-waiting':
            // 3단계: 관리자 승인 대기
            return basePath + 'approval-waiting.html';

        case 'portal':
            // 4단계: 평가 기초자료 제출 (평가법별)
            if (method) {
                const submissionMethod = method === 'inheritance_tax' ? 'tax' : method;
                return basePath + `valuation/submissions/${submissionMethod}-submission.html${projectId ? '?projectId=' + projectId : ''}`;
            }
            return null;

        case 'data-collection':
            // 6단계: 데이터 수집
            return basePath + `valuation/data-collection.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        case 'evaluation-progress':
            // 7단계: 평가 진행
            return basePath + `valuation/evaluation-progress.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        case 'accountant-review':
        case 'draft-generation':
        case 'final-preparation':
            // 8, 9, 12단계: 공인회계사 검토, 초안 생성, 최종안 작성
            return basePath + `valuation/${page}.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        case 'report-draft':
            // 10단계: 평가보고서 초안 확인
            return basePath + `valuation/report-draft.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        case 'report-final':
            // 13단계: 평가보고서 최종안 확인
            return basePath + `valuation/report-final.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        case 'revision-request':
            // 11단계: 수정 요청
            return basePath + `valuation/revision-request.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        case 'deposit-payment':
            // 4단계: 계약금 결제하기
            return basePath + `valuation/deposit-payment.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        case 'balance-payment':
            // 14단계: 잔금 결제하기
            return basePath + `valuation/balance-payment.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        case 'report-download':
            // 15단계: 평가보고서 수령
            return basePath + `valuation/report-download.html${projectId ? '?projectId=' + projectId + (method ? '&method=' + method : '') : (method ? '?method=' + method : '')}`;

        default:
            return null;
    }
}

/**
 * 15단계 프로세스 사이드바 렌더링
 * @param {number} currentStep - 현재 단계 (1~15)
 * @param {string} methodStatus - 평가법 상태 (approved, in_progress 등)
 * @param {string} method - 평가법 코드 (dcf, relative 등) - 4단계부터 필요
 * @param {string} projectId - 프로젝트 ID
 * @returns {string} HTML 문자열
 */
export function renderSidebar(currentStep, methodStatus, method = null, projectId = null, startStep = 1, endStep = 15, userRole = 'customer') {
    const statusInfo = getStatusDisplay(methodStatus);

    let html = `
        <div class="sidebar">
            <!-- 프로젝트 정보 (4단계부터 표시) -->
            ${currentStep >= 4 && method ? renderProjectInfo(method, methodStatus, projectId, 'FinderWorld') : ''}

            <!-- Valuation 진행 단계 -->
            <div class="sidebar-title">Valuation 진행 단계</div>
            <div class="process-steps">
    `;

    let displayNumber = 0; // 고객 액션 단계(visible: true)만 번호 부여

    PROCESS_STEPS.forEach(stepInfo => {
        // 범위 필터링: startStep ~ endStep만 표시
        if (stepInfo.step < startStep || stepInfo.step > endStep) {
            return;
        }

        const isActive = stepInfo.step === currentStep;
        const isCompleted = stepInfo.step < currentStep;
        const url = getStepUrl(stepInfo, method, projectId);

        // 내부 프로세스 단계 (visible: false) — 번호 없음, 역할별 분기
        if (stepInfo.visible === false) {
            const canAccess = (userRole === 'accountant' || userRole === 'admin');

            if (canAccess && url) {
                // 회계사/관리자: 내부 단계 클릭 가능 (링크)
                html += `
                    <a href="${url}" class="process-step internal-step ${isActive ? 'internal-active' : ''} ${isCompleted ? 'internal-completed' : ''} accessible">
                        <div class="internal-icon">${isCompleted ? '✓' : '⚙'}</div>
                        <div class="step-content">
                            <div class="step-name">${stepInfo.name}</div>
                        </div>
                    </a>
                `;
            } else {
                // 고객: 내부 단계 보이지만 클릭 불가 (프로세스 인지만)
                html += renderInternalStep(stepInfo, isActive, isCompleted);
            }
            return;
        }

        // 고객 액션 단계 (visible: true) — 번호 부여
        displayNumber++;
        const isAccessible = shouldStepBeAccessible(stepInfo.step, currentStep, methodStatus);

        if (isAccessible && url) {
            html += `
                <a href="${url}" class="process-step ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} accessible">
                    <div class="step-number">${isCompleted ? '✓' : displayNumber}</div>
                    <div class="step-content">
                        <div class="step-name">${stepInfo.name}</div>
                    </div>
                </a>
            `;
        } else {
            html += `
                <div class="process-step ${isActive ? 'active' : ''} ${isAccessible ? 'accessible' : 'locked'}">
                    <div class="step-number">${displayNumber}</div>
                    <div class="step-content">
                        <div class="step-name">${stepInfo.name}</div>
                    </div>
                </div>
            `;
        }
    });

    html += `
            </div>

            <!-- 담당 공인회계사 (4단계부터 표시) -->
            ${currentStep >= 4 ? renderAccountantSection(getBasePath()) : ''}
        </div>
    `;

    return html;
}

/**
 * 내부 프로세스 단계 렌더링 (작은 회색 참고 표시)
 * - 번호 없음, 클릭 불가
 * - 12px 글씨, 회색(#9CA3AF), 들여쓰기
 * - 현재 활성 단계면 파란색 하이라이트
 */
function renderInternalStep(stepInfo, isActive, isCompleted = false) {
    const activeClass = isActive ? 'internal-active' : '';
    const completedClass = isCompleted ? 'internal-completed' : '';
    const icon = isCompleted ? '✓' : '⚙';
    return `
        <div class="process-step internal-step ${activeClass} ${completedClass}">
            <div class="internal-icon">${icon}</div>
            <div class="step-content">
                <div class="step-name">${stepInfo.name}</div>
            </div>
        </div>
    `;
}

/**
 * 프로젝트 정보 섹션 렌더링 (평가법 표시)
 */
function renderProjectInfo(method, methodStatus, projectId = null, customerName = null) {
    const methodName = METHOD_NAMES[method] || method;

    // projectId가 없으면 아무것도 표시하지 않음
    if (!projectId) {
        return '';
    }

    return `
        <div class="project-info-section">
            <div class="sidebar-title">진행 중인 Valuation</div>
            <div class="project-info-simple">
                ${customerName ? `<div class="info-row">회사: ${customerName}</div>` : ''}
                <div class="info-row">프로젝트 ID: ${projectId}</div>
                <div class="info-row">평가방법: ${methodName}</div>
            </div>
        </div>
    `;
}

/**
 * 담당 공인회계사 섹션 렌더링
 * @param {string} basePath - app 폴더까지의 상대 경로
 */
function renderAccountantSection(basePath) {
    return `
        <div class="accountant-section">
            <div class="sidebar-title">담당 공인회계사</div>
            <a href="${basePath}accountant-profile.html" class="accountant-link">
                <span class="accountant-icon">👤</span>
                <span class="accountant-name">이지훈 회계사</span>
                <span class="arrow">→</span>
            </a>
        </div>
    `;
}

/**
 * 단계 접근 가능 여부 판단
 */
function shouldStepBeAccessible(stepNumber, currentStep, methodStatus) {
    // 테스트 단계: 모든 단계 항상 접근 가능
    return true;
}

/**
 * 평가법별 아이콘
 */
function getMethodIcon(method) {
    const icons = {
        dcf: '💰',
        relative: '⚖️',
        intrinsic: '💎',
        asset: '🏦',
        inheritance_tax: '📋'
    };
    return icons[method] || '📊';
}

/**
 * 사이드바 CSS 스타일
 */
export const SIDEBAR_STYLES = `
        :root {
            --deep-green: #166534;
            --light-green: #DCFCE7;
            --deep-blue: #1D4ED8;
            --light-blue: #DBEAFE;
        }

        .sidebar {
            width: 320px;
            background: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .sidebar-title {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: 900;
            color: #1F2937;
            margin-bottom: 16px;
        }

        /* 프로젝트 정보 */
        .project-info-section {
            margin-bottom: 32px;
        }

        .project-info-simple {
            font-size: 13px;
            color: #374151;
            line-height: 1.8;
        }

        .info-row {
            margin-bottom: 8px;
        }

        .info-row:last-child {
            margin-bottom: 0;
        }

        .method-status {
            font-size: 13px;
            font-weight: 600;
        }

        /* 프로세스 단계 */
        .process-steps {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 32px;
        }

        .process-step {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            border-radius: 8px;
            transition: all 0.2s ease;
            text-decoration: none;
            color: inherit;
        }

        .process-step.accessible {
            cursor: pointer;
        }

        .process-step.accessible:hover {
            background: #F3F4F6;
        }

        .process-step.locked {
            opacity: 0.4;
            cursor: not-allowed;
        }

        .process-step.active {
            background: var(--light-green);
            border: 2px solid var(--deep-green);
        }

        .step-number {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: #E5E7EB;
            color: #6B7280;
            font-size: 14px;
            font-weight: 700;
            flex-shrink: 0;
        }

        .process-step.active .step-number {
            background: var(--deep-green);
            color: white;
        }

        .process-step.accessible .step-number {
            background: #D1D5DB;
            color: #374151;
        }

        .step-content {
            flex: 1;
        }

        .step-name {
            font-size: 14px;
            font-weight: 600;
            color: #374151;
            line-height: 1.4;
        }

        .process-step.active .step-name {
            color: var(--deep-green);
            font-weight: 700;
        }

        .step-indicator {
            font-size: 13px;
            color: var(--deep-blue);
            margin-top: 4px;
            font-weight: 700;
            background: #DBEAFE;
            padding: 2px 8px;
            border-radius: 4px;
        }

        /* 내부 프로세스 단계 (작은 회색 참고 표시) */
        .process-step.internal-step {
            padding: 4px 12px 4px 20px;
            border-left: 2px solid #E5E7EB;
            margin-left: 16px;
            cursor: default;
            opacity: 0.7;
            gap: 8px;
        }

        .process-step.internal-step .internal-icon {
            font-size: 11px;
            color: #9CA3AF;
            flex-shrink: 0;
            width: 16px;
            text-align: center;
        }

        .process-step.internal-step .step-name {
            font-size: 12px;
            font-weight: 500;
            color: #9CA3AF;
        }

        .process-step.internal-step:not(.accessible):hover {
            background: transparent;
        }

        /* 회계사/관리자: 내부 단계 클릭 가능 스타일 */
        a.process-step.internal-step.accessible {
            text-decoration: none;
            color: inherit;
            cursor: pointer;
            opacity: 0.85;
        }

        a.process-step.internal-step.accessible:hover {
            background: #F3F4F6;
            opacity: 1;
        }

        a.process-step.internal-step.accessible .step-name {
            color: #4B5563;
        }

        .process-step.internal-step.internal-active {
            border-left-color: #3B82F6;
            opacity: 1;
        }

        .process-step.internal-step.internal-active .internal-icon {
            color: #3B82F6;
        }

        .process-step.internal-step.internal-active .step-name {
            color: #3B82F6;
            font-weight: 600;
        }

        /* 완료된 내부 단계 */
        .process-step.internal-step.internal-completed {
            opacity: 0.6;
        }

        .process-step.internal-step.internal-completed .internal-icon {
            color: #10B981;
        }

        .process-step.internal-step.internal-completed .step-name {
            color: #6B7280;
        }

        /* 완료된 고객 단계 */
        .process-step.completed .step-number {
            background: #10B981;
            color: white;
        }

        /* 담당 공인회계사 */
        .accountant-section {
            margin-top: 32px;
            padding-top: 32px;
            border-top: 1px solid #E5E7EB;
        }

        .accountant-link {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .accountant-link:hover {
            background: var(--light-blue);
            border-color: #BFDBFE;
        }

        .accountant-icon {
            font-size: 24px;
        }

        .accountant-name {
            flex: 1;
            font-size: 15px;
            font-weight: 600;
            color: #111827;
        }

        .arrow {
            color: #9CA3AF;
            font-size: 18px;
        }
`;

/**
 * 사이드바를 DOM에 주입
 * @param {string} containerId - 사이드바를 넣을 컨테이너 ID
 * @param {number} currentStep - 현재 단계
 * @param {string} methodStatus - 평가법 상태
 * @param {string} method - 평가법 코드
 * @param {string} projectId - 프로젝트 ID
 */
export function injectSidebar(containerId, currentStep, methodStatus, method = null, projectId = null, startStep = 1, endStep = 15, userRole = null) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container #${containerId} not found`);
        return;
    }

    // 역할 자동 감지 (명시적으로 전달되지 않은 경우)
    const resolvedRole = userRole || getUserRole();

    // 스타일 주입 (한 번만)
    if (!document.getElementById('sidebar-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'sidebar-styles';
        styleElement.innerHTML = SIDEBAR_STYLES;
        document.head.appendChild(styleElement);
    }

    // 사이드바 HTML 주입 (userRole에 따라 내부 단계 활성화/비활성화)
    container.innerHTML = renderSidebar(currentStep, methodStatus, method, projectId, startStep, endStep, resolvedRole);

    // 비동기로 Supabase 세션 확인 → 역할이 다르면 재렌더링
    detectAndStoreUserRole().then(detectedRole => {
        if (detectedRole && detectedRole !== resolvedRole) {
            container.innerHTML = renderSidebar(currentStep, methodStatus, method, projectId, startStep, endStep, detectedRole);
        }
    }).catch(() => {}); // 실패 시 기존 렌더 유지
}
