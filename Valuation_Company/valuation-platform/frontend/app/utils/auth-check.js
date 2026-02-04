/**
 * Auth Check Utility - RBAC Middleware
 *
 * 페이지 접근 권한 확인 및 사용자 정보 조회
 *
 * 사용법:
 * <script src="../utils/auth-check.js"></script>
 * <script>
 *   AuthCheck.requireRole(['customer', 'admin'])
 *     .then(user => {
 *       console.log('Authorized user:', user);
 *     })
 *     .catch(error => {
 *       // 자동으로 에러 페이지 또는 로그인 페이지로 리다이렉트됨
 *     });
 * </script>
 */

const AuthCheck = (function() {
    // Supabase 설정
    const SUPABASE_URL = 'https://arxrfetgaitkgiiqabap.supabase.co';
    const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0';

    let supabaseClient = null;

    /**
     * 현재 페이지 깊이 기반 상대경로 prefix 계산
     * app/ 하위 어느 페이지에서든 app/ 상위(frontend root)까지의 ../를 반환
     */
    function getRelativePrefix() {
        const depth = window.location.pathname.split('/app/')[1];
        const levels = depth ? depth.split('/').length - 1 : 0;
        return levels > 0 ? '../'.repeat(levels) + '../' : '../';
    }

    /**
     * Supabase 클라이언트 초기화
     */
    function initSupabase() {
        if (!supabaseClient) {
            if (typeof window.supabase === 'undefined') {
                throw new Error('Supabase SDK가 로드되지 않았습니다. <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>를 추가하세요.');
            }
            supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        }
        return supabaseClient;
    }

    /**
     * 현재 로그인한 사용자 정보 조회 (users 테이블 포함)
     * @returns {Promise<Object>} { user, userData }
     */
    async function getCurrentUser() {
        const supabase = initSupabase();

        // 1. Supabase Auth 사용자 확인
        const { data: { user }, error: authError } = await supabase.auth.getUser();

        if (authError || !user) {
            throw new Error('로그인이 필요합니다');
        }

        // 2. users 테이블에서 role 및 추가 정보 조회
        const { data: userData, error: userError } = await supabase
            .from('users')
            .select('*')
            .eq('user_id', user.id)
            .single();

        if (userError) {
            if (userError.code === 'PGRST116') {
                throw new Error('사용자 프로필이 설정되지 않았습니다');
            }
            throw new Error(`사용자 정보 조회 실패: ${userError.message}`);
        }

        if (!userData) {
            throw new Error('사용자 정보를 찾을 수 없습니다');
        }

        // 3. 계정 활성화 여부 확인
        if (!userData.is_active) {
            throw new Error('비활성화된 계정입니다');
        }

        return { user, userData };
    }

    /**
     * 특정 역할(들)만 접근 가능하도록 체크
     * @param {string|string[]} allowedRoles - 허용할 역할 (예: 'customer' 또는 ['customer', 'admin'])
     * @param {Object} options - 옵션 { redirectOnFail: '/login', showAlert: true }
     * @returns {Promise<Object>} { user, userData }
     */
    async function requireRole(allowedRoles, options = {}) {
        const defaultOptions = {
            redirectOnFail: getRelativePrefix() + 'app/login.html',
            showAlert: true
        };
        const opts = { ...defaultOptions, ...options };

        // allowedRoles를 배열로 변환
        const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];

        try {
            const { user, userData } = await getCurrentUser();

            // 역할 체크 (admin은 모든 페이지 접근 가능)
            if (userData.role !== 'admin' && !roles.includes(userData.role)) {
                throw new Error(`접근 권한이 없습니다. (필요한 역할: ${roles.join(', ')})`);
            }

            return { user, userData };

        } catch (error) {
            console.error('Auth check failed:', error);

            if (opts.showAlert) {
                alert(error.message);
            }

            if (opts.redirectOnFail) {
                window.location.href = opts.redirectOnFail;
            }

            throw error;
        }
    }

    /**
     * 로그인 여부만 체크 (역할 무관)
     * @param {Object} options - 옵션
     * @returns {Promise<Object>} { user, userData }
     */
    async function requireLogin(options = {}) {
        const defaultOptions = {
            redirectOnFail: getRelativePrefix() + 'app/login.html',
            showAlert: true
        };
        const opts = { ...defaultOptions, ...options };

        try {
            const { user, userData } = await getCurrentUser();
            return { user, userData };

        } catch (error) {
            console.error('Login check failed:', error);

            if (opts.showAlert) {
                alert(error.message);
            }

            if (opts.redirectOnFail) {
                window.location.href = opts.redirectOnFail;
            }

            throw error;
        }
    }

    /**
     * 고객(company) 전용 데이터 조회
     * users 테이블에서 role이 'customer'인 경우, customers 테이블 정보 조회
     * @returns {Promise<Object>} { user, userData, customerData }
     */
    async function getCustomerData() {
        const { user, userData } = await requireRole(['customer', 'admin']);

        const supabase = initSupabase();

        // customers 테이블에서 데이터 조회
        const { data: customerData, error: customerError } = await supabase
            .from('customers')
            .select('*')
            .eq('user_id', user.id)
            .single();

        if (customerError) {
            console.warn('Customer data fetch warning:', customerError);
            return { user, userData, customerData: null };
        }

        return { user, userData, customerData };
    }

    /**
     * 회계사 전용 데이터 조회
     * users 테이블에서 role이 'accountant'인 경우, accountants 테이블 정보 조회
     * @returns {Promise<Object>} { user, userData, accountantData }
     */
    async function getAccountantData() {
        const { user, userData } = await requireRole(['accountant', 'admin']);

        const supabase = initSupabase();

        // accountants 테이블에서 데이터 조회
        const { data: accountantData, error: accountantError } = await supabase
            .from('accountants')
            .select('*')
            .eq('user_id', user.id)
            .single();

        if (accountantError) {
            console.warn('Accountant data fetch warning:', accountantError);
            return { user, userData, accountantData: null };
        }

        return { user, userData, accountantData };
    }

    /**
     * 로그아웃
     */
    async function logout() {
        const supabase = initSupabase();
        const { error } = await supabase.auth.signOut();

        if (error) {
            console.error('Logout error:', error);
            throw error;
        }

        window.location.href = getRelativePrefix() + 'index.html';
    }

    // Public API
    return {
        getCurrentUser,
        requireRole,
        requireLogin,
        getCustomerData,
        getAccountantData,
        logout
    };
})();

// 전역으로 노출 (필요 시)
if (typeof window !== 'undefined') {
    window.AuthCheck = AuthCheck;
}
