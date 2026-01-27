/**
 * Common Sidebar Component
 * 14단계 프로세스 사이드바 동적 생성
 */

/**
 * 평가법 이름 매핑
 */
const METHOD_NAMES = {
    dcf: '현금흐름할인법 (DCF)',
    relative: '상대가치평가법',
    intrinsic: '본질가치평가법',
    asset: '자산가치평가법',
    inheritance_tax: '상속세및증여세법'
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
 * 14단계 프로세스 정의
 */
const PROCESS_STEPS = [
    { step: 1, name: '서비스 안내', page: 'guide' },
    { step: 2, name: '평가 신청', page: 'project-create' },
    { step: 3, name: '관리자 승인 대기', page: 'approval-waiting' },
    { step: 4, name: '평가 기초자료 제출', page: 'portal' },
    { step: 5, name: '데이터 수집 중', page: 'data-collection' },
    { step: 6, name: '평가 진행 중', page: 'evaluation-progress' },
    { step: 7, name: '공인회계사 검토 중', page: 'accountant-review' },
    { step: 8, name: '평가보고서 초안 생성', page: 'draft-generation' },
    { step: 9, name: '평가보고서 초안 확인', page: 'result', params: 'mode=draft' },
    { step: 10, name: '수정 요청', page: 'revision-request' },
    { step: 11, name: '평가보고서 최종안 작성', page: 'final-preparation' },
    { step: 12, name: '평가보고서 최종안 확인', page: 'result', params: 'mode=final' },
    { step: 13, name: '결제하기', page: 'payment' },
    { step: 14, name: '평가보고서 수령', page: 'report-download' }
];

/**
 * 단계별 URL 생성
 * @param {object} stepInfo - 단계 정보 객체
 * @param {string} method - 평가법 코드 (dcf, relative 등)
 * @param {string} projectId - 프로젝트 ID
 * @returns {string|null} URL 또는 null
 */
function getStepUrl(stepInfo, method, projectId) {
    const { page, params } = stepInfo;

    // 기본 경로 (현재 위치에서 상대 경로)
    let basePath = '../';

    // 페이지별 URL 매핑
    switch (page) {
        case 'guide':
            // 1단계: 서비스 안내 (valuation 홈)
            return basePath + 'valuation.html';

        case 'project-create':
            // 2단계: 평가 신청
            return basePath + 'projects/project-create.html';

        case 'approval-waiting':
            // 3단계: 관리자 승인 대기
            return basePath + 'approval-waiting.html';

        case 'portal':
            // 4단계: 평가 기초자료 제출 (평가법별)
            if (method) {
                return basePath + `valuation/portals/${method}-portal.html${projectId ? '?projectId=' + projectId : ''}`;
            }
            return null;

        case 'data-collection':
        case 'evaluation-progress':
            // 5~6단계: 데이터 수집, 평가 진행
            return basePath + `valuation/evaluation-progress.html${projectId ? '?projectId=' + projectId : ''}`;

        case 'accountant-review':
        case 'draft-generation':
        case 'final-preparation':
            // 7, 8, 11단계: 공인회계사 검토, 초안 생성, 최종안 작성
            return basePath + `valuation/${page}.html${projectId ? '?projectId=' + projectId : ''}`;

        case 'result':
            // 9, 12단계: 평가보고서 확인 (초안/최종안)
            if (method) {
                return basePath + `valuation/results/${method}-valuation.html${projectId ? '?projectId=' + projectId : ''}${params ? '&' + params : ''}`;
            }
            return null;

        case 'revision-request':
            // 10단계: 수정 요청
            return basePath + `valuation/revision-request.html${projectId ? '?projectId=' + projectId : ''}`;

        case 'payment':
            // 13단계: 결제하기
            return basePath + `valuation/balance-payment.html${projectId ? '?projectId=' + projectId : ''}`;

        case 'report-download':
            // 14단계: 평가보고서 수령
            return basePath + `valuation/report-download.html${projectId ? '?projectId=' + projectId : ''}`;

        default:
            return null;
    }
}

/**
 * 14단계 프로세스 사이드바 렌더링
 * @param {number} currentStep - 현재 단계 (1~14)
 * @param {string} methodStatus - 평가법 상태 (approved, in_progress 등)
 * @param {string} method - 평가법 코드 (dcf, relative 등) - 4단계부터 필요
 * @param {string} projectId - 프로젝트 ID
 * @returns {string} HTML 문자열
 */
export function renderSidebar(currentStep, methodStatus, method = null, projectId = null, startStep = 1, endStep = 14) {
    const statusInfo = getStatusDisplay(methodStatus);

    let html = `
        <div class="sidebar">
            <!-- 프로젝트 정보 (4단계부터 표시) -->
            ${currentStep >= 4 && method ? renderProjectInfo(method, methodStatus, projectId) : ''}

            <!-- 진행 단계 -->
            <div class="sidebar-title">진행 단계</div>
            <div class="process-steps">
    `;

    PROCESS_STEPS.forEach(stepInfo => {
        // 범위 필터링: startStep ~ endStep만 표시
        if (stepInfo.step < startStep || stepInfo.step > endStep) {
            return;
        }

        const isActive = stepInfo.step === currentStep;
        const isAccessible = shouldStepBeAccessible(stepInfo.step, currentStep, methodStatus);
        const url = getStepUrl(stepInfo, method, projectId);

        // 표시 번호: startStep부터 시작하여 1번부터 다시 매김
        const displayNumber = stepInfo.step - startStep + 1;

        // 접근 가능한 단계는 링크로, 잠긴 단계는 div로 렌더링
        if (isAccessible && url) {
            html += `
                <a href="${url}" class="process-step ${isActive ? 'active' : ''} accessible">
                    <div class="step-number">${displayNumber}</div>
                    <div class="step-content">
                        <div class="step-name">${stepInfo.name}</div>
                        ${isActive ? '<div class="step-indicator">→ 현재 단계</div>' : ''}
                    </div>
                </a>
            `;
        } else {
            html += `
                <div class="process-step ${isActive ? 'active' : ''} ${isAccessible ? 'accessible' : 'locked'}">
                    <div class="step-number">${displayNumber}</div>
                    <div class="step-content">
                        <div class="step-name">${stepInfo.name}</div>
                        ${isActive ? '<div class="step-indicator">→ 현재 단계</div>' : ''}
                    </div>
                </div>
            `;
        }
    });

    html += `
            </div>

            <!-- 담당 공인회계사 (4단계부터 표시) -->
            ${currentStep >= 4 ? renderAccountantSection() : ''}
        </div>
    `;

    return html;
}

/**
 * 프로젝트 정보 섹션 렌더링 (평가법 표시)
 */
function renderProjectInfo(method, methodStatus, projectId = null) {
    const methodName = METHOD_NAMES[method] || method;
    const statusInfo = getStatusDisplay(methodStatus);

    return `
        <div class="project-info-section">
            <div class="sidebar-title">진행 중인 평가</div>
            ${projectId ? `<div class="project-id">프로젝트 ID: ${projectId}</div>` : ''}
            <div class="method-badge">
                <span class="method-icon">${getMethodIcon(method)}</span>
                <div class="method-details">
                    <div class="method-name">${methodName}</div>
                    <div class="method-status" style="color: ${statusInfo.color}">
                        ${statusInfo.icon} ${statusInfo.text}
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * 담당 공인회계사 섹션 렌더링
 */
function renderAccountantSection() {
    return `
        <div class="accountant-section">
            <div class="sidebar-title">담당 공인회계사</div>
            <a href="../../accountant-profile.html" class="accountant-link">
                <span class="accountant-icon">👤</span>
                <span class="accountant-name">선웅규 회계사</span>
                <span class="arrow">→</span>
            </a>
        </div>
    `;
}

/**
 * 단계 접근 가능 여부 판단
 */
function shouldStepBeAccessible(stepNumber, currentStep, methodStatus) {
    // 1~3단계: 항상 접근 가능 (홈 프로세스)
    if (stepNumber <= 3) {
        return true;
    }

    // 4~14단계: 승인되어야 접근 가능
    if (methodStatus === 'approved' ||
        methodStatus === 'in_progress' ||
        methodStatus === 'completed') {
        // 현재 단계 이하만 접근 가능
        return stepNumber <= currentStep;
    }

    return false;
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
            font-size: 14px;
            font-weight: 700;
            color: #6B7280;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* 프로젝트 정보 */
        .project-info-section {
            margin-bottom: 32px;
        }

        .project-id {
            font-size: 13px;
            color: #6B7280;
            margin-bottom: 12px;
            padding: 8px 12px;
            background: #F3F4F6;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
        }

        .method-badge {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: #F9FAFB;
            border: 2px solid var(--deep-green);
            border-radius: 12px;
        }

        .method-icon {
            font-size: 28px;
        }

        .method-details {
            flex: 1;
        }

        .method-name {
            font-size: 15px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 4px;
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
            font-size: 12px;
            color: var(--deep-green);
            margin-top: 4px;
            font-weight: 600;
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
export function injectSidebar(containerId, currentStep, methodStatus, method = null, projectId = null, startStep = 1, endStep = 14) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container #${containerId} not found`);
        return;
    }

    // 스타일 주입 (한 번만)
    if (!document.getElementById('sidebar-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'sidebar-styles';
        styleElement.innerHTML = SIDEBAR_STYLES;
        document.head.appendChild(styleElement);
    }

    // 사이드바 HTML 주입
    container.innerHTML = renderSidebar(currentStep, methodStatus, method, projectId, startStep, endStep);
}
