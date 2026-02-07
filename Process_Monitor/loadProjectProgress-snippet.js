/**
 * loadProjectProgress - DB에서 사용자별 진행률 조회
 *
 * index.html에 추가할 함수 스니펫
 * 기존 loadProjectProgress 함수를 이 코드로 교체
 */

// 프로젝트 진행률 로드
// DB에서 사용자별 진행률 조회 (git commit 시 자동 업로드됨)
async function loadProjectProgress(projectName) {
    console.log('📊 프로젝트 진행률 로드:', projectName);

    try {
        // 로그인 사용자 확인
        const { data: { session } } = await window.supabaseClient.auth.getSession();
        if (!session || !session.user) {
            console.log('📊 로그인 필요 - 진행률 0%');
            resetAllProgressToZero();
            return;
        }

        // 이메일에서 project_id 생성 (upload-progress.js와 동일 로직)
        const email = session.user.email;
        const username = email.split('@')[0] || 'user';
        const projectId = `${username}_PROJECT`;
        console.log('📊 조회할 Project ID:', projectId);

        // DB에서 진행률 조회
        const { data, error } = await window.supabaseClient
            .from('project_phase_progress')
            .select('*')
            .eq('project_id', projectId);

        if (error) {
            console.warn('📊 DB 조회 오류:', error);
            resetAllProgressToZero();
            return;
        }

        if (!data || data.length === 0) {
            console.log('📊 DB에 진행률 데이터 없음 - 0%');
            resetAllProgressToZero();
            return;
        }

        // 진행률 적용
        data.forEach(phase => {
            const progress = phase.progress || 0;
            const code = phase.phase_code;

            if (code === 'P0' || code === 'S0') {
                updateSpecialProgress(code, progress);
            } else if (code.startsWith('P')) {
                updatePrepProgressByCode(code, progress);
            } else if (code.startsWith('S')) {
                updateStageProgress(code, progress);
            }
        });

        console.log('📊 DB에서 진행률 로드 완료:', data.length + '개 단계');
    } catch (e) {
        console.warn('📊 진행률 로드 오류:', e);
        resetAllProgressToZero();
    }
}
