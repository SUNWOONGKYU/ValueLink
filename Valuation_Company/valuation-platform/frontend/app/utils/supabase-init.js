/**
 * Supabase 안전 초기화
 * CDN 로드 실패 시에도 페이지가 정상 작동하도록 보장
 */
(function() {
    const SUPABASE_URL = 'https://arxrfetgaitkgiiqabap.supabase.co';
    const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0';

    try {
        if (window.supabase && typeof window.supabase.createClient === 'function') {
            window.supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
            console.log('Supabase 초기화 성공');
        } else {
            console.warn('Supabase SDK 미로드 - 테스트 모드로 작동');
            window.supabaseClient = null;
        }
    } catch (e) {
        console.warn('Supabase 초기화 실패 - 테스트 모드로 작동:', e.message);
        window.supabaseClient = null;
    }
})();
