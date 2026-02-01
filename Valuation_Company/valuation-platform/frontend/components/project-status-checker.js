/**
 * Project Status Checker
 * 평가법별 상태 확인 및 프로젝트 정보 조회
 */

import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

// Supabase 클라이언트 초기화
const SUPABASE_URL = 'https://arxrfetgaitkgiiqabap.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

/**
 * 평가법 코드 매핑
 */
export const METHOD_CODES = {
    dcf: 'dcf',
    relative: 'relative',
    intrinsic: 'intrinsic',
    asset: 'asset',
    inheritance_tax: 'inheritance_tax'
};

/**
 * 평가법 이름 매핑
 */
export const METHOD_NAMES = {
    dcf: '현금흐름할인법 (DCF)',
    relative: '상대가치평가법',
    intrinsic: '본질가치평가법',
    asset: '자산가치평가법',
    inheritance_tax: '상속세및증여세법'
};

/**
 * 상태 값 정의
 */
export const STATUS = {
    NOT_REQUESTED: 'not_requested',  // 신청 안 함
    PENDING: 'pending',              // 승인 대기 중
    APPROVED: 'approved',            // 승인됨
    IN_PROGRESS: 'in_progress',      // 진행 중
    COMPLETED: 'completed'           // 완료
};

/**
 * 현재 로그인한 사용자의 프로젝트 정보 가져오기
 */
export async function getCurrentProject() {
    try {
        // 1. 로그인 체크
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();

        if (sessionError || !session) {
            console.warn('Not logged in');
            return null;
        }

        // 2. 사용자의 프로젝트 조회 (가장 최근 프로젝트)
        const { data: projects, error: projectError } = await supabase
            .from('projects')
            .select('*')
            .eq('user_id', session.user.id)
            .order('created_at', { ascending: false })
            .limit(1);

        if (projectError) {
            console.error('Error fetching project:', projectError);
            return null;
        }

        if (!projects || projects.length === 0) {
            console.warn('No project found for user');
            return null;
        }

        return projects[0];

    } catch (error) {
        console.error('Error in getCurrentProject:', error);
        return null;
    }
}

/**
 * 특정 평가법의 상태 확인
 * @param {string} projectId - 프로젝트 ID
 * @param {string} method - 평가법 코드 (dcf, relative, intrinsic, asset, inheritance_tax)
 * @returns {Object} { status, step }
 */
export async function checkMethodStatus(projectId, method) {
    try {
        if (!METHOD_CODES[method]) {
            throw new Error(`Invalid method: ${method}`);
        }

        // 프로젝트 정보 조회
        const { data: project, error } = await supabase
            .from('projects')
            .select(`${method}_status, ${method}_step`)
            .eq('project_id', projectId)
            .single();

        if (error) {
            console.error(`Error checking ${method} status:`, error);
            return {
                status: STATUS.NOT_REQUESTED,
                step: 1
            };
        }

        return {
            status: project[`${method}_status`] || STATUS.NOT_REQUESTED,
            step: project[`${method}_step`] || 1
        };

    } catch (error) {
        console.error('Error in checkMethodStatus:', error);
        return {
            status: STATUS.NOT_REQUESTED,
            step: 1
        };
    }
}

/**
 * 모든 평가법의 상태 확인
 * @param {string} projectId - 프로젝트 ID
 * @returns {Object} 평가법별 상태 객체
 */
export async function checkAllMethodsStatus(projectId) {
    try {
        const { data: project, error } = await supabase
            .from('projects')
            .select('*')
            .eq('project_id', projectId)
            .single();

        if (error) {
            console.error('Error fetching project:', error);
            return null;
        }

        return {
            dcf: {
                status: project.dcf_status,
                step: project.dcf_step
            },
            relative: {
                status: project.relative_status,
                step: project.relative_step
            },
            intrinsic: {
                status: project.intrinsic_status,
                step: project.intrinsic_step
            },
            asset: {
                status: project.asset_status,
                step: project.asset_step
            },
            inheritance_tax: {
                status: project.inheritance_tax_status,
                step: project.inheritance_tax_step
            }
        };

    } catch (error) {
        console.error('Error in checkAllMethodsStatus:', error);
        return null;
    }
}

/**
 * 평가법 상태 업데이트
 * @param {string} projectId - 프로젝트 ID
 * @param {string} method - 평가법 코드
 * @param {string} status - 새 상태
 * @param {number} step - 새 단계 (선택)
 */
export async function updateMethodStatus(projectId, method, status, step = null) {
    try {
        const updateData = {
            [`${method}_status`]: status
        };

        if (step !== null) {
            updateData[`${method}_step`] = step;
        }

        const { error } = await supabase
            .from('projects')
            .update(updateData)
            .eq('project_id', projectId);

        if (error) {
            console.error(`Error updating ${method} status:`, error);
            return false;
        }

        console.log(`✅ ${method} status updated:`, status, step);
        return true;

    } catch (error) {
        console.error('Error in updateMethodStatus:', error);
        return false;
    }
}

/**
 * 승인된 평가법 목록 가져오기
 * @param {string} projectId - 프로젝트 ID
 * @returns {Array} 승인된 평가법 코드 배열
 */
export async function getApprovedMethods(projectId) {
    try {
        const allStatus = await checkAllMethodsStatus(projectId);
        if (!allStatus) return [];

        const approvedMethods = [];
        for (const [method, info] of Object.entries(allStatus)) {
            if (info.status === STATUS.APPROVED ||
                info.status === STATUS.IN_PROGRESS ||
                info.status === STATUS.COMPLETED) {
                approvedMethods.push(method);
            }
        }

        return approvedMethods;

    } catch (error) {
        console.error('Error in getApprovedMethods:', error);
        return [];
    }
}

/**
 * 상태에 따른 UI 표시 정보
 */
export function getStatusDisplay(status) {
    const displays = {
        [STATUS.NOT_REQUESTED]: {
            icon: '⚫',
            text: '신청 안 함',
            color: '#9CA3AF',
            canAccess: false
        },
        [STATUS.PENDING]: {
            icon: '🟡',
            text: '승인 대기 중',
            color: '#F59E0B',
            canAccess: false
        },
        [STATUS.APPROVED]: {
            icon: '🟢',
            text: '승인됨',
            color: '#10B981',
            canAccess: true
        },
        [STATUS.IN_PROGRESS]: {
            icon: '🔵',
            text: '진행 중',
            color: '#3B82F6',
            canAccess: true
        },
        [STATUS.COMPLETED]: {
            icon: '✅',
            text: '완료',
            color: '#059669',
            canAccess: true
        }
    };

    return displays[status] || displays[STATUS.NOT_REQUESTED];
}
