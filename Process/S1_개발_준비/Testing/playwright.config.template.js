/**
 * Playwright Configuration Template
 *
 * 사용법:
 * 1. 이 파일을 playwright.config.js로 복사
 * 2. 프로젝트에 맞게 경로/URL 수정
 * 3. npm install @playwright/test --save-dev
 * 4. npx playwright install
 */

const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
    // 테스트 디렉토리
    testDir: './tests/e2e',

    // 병렬 실행
    fullyParallel: true,

    // CI 환경에서 재시도 금지
    forbidOnly: !!process.env.CI,

    // 재시도 횟수
    retries: process.env.CI ? 2 : 0,

    // 병렬 워커 수
    workers: process.env.CI ? 1 : undefined,

    // 리포터
    reporter: 'html',

    // 공통 설정
    use: {
        // 기본 URL
        baseURL: 'http://localhost:3000',

        // 실패 시 스크린샷
        screenshot: 'only-on-failure',

        // 실패 시 비디오 녹화
        video: 'retain-on-failure',

        // 트레이스 수집
        trace: 'on-first-retry',
    },

    // 브라우저별 프로젝트
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
        {
            name: 'firefox',
            use: { ...devices['Desktop Firefox'] },
        },
        {
            name: 'webkit',
            use: { ...devices['Desktop Safari'] },
        },

        // 모바일 뷰포트 테스트
        {
            name: 'Mobile Chrome',
            use: { ...devices['Pixel 5'] },
        },
        {
            name: 'Mobile Safari',
            use: { ...devices['iPhone 12'] },
        },
    ],

    // 테스트 전 로컬 서버 실행 (선택)
    // webServer: {
    //     command: 'npm run dev',
    //     url: 'http://localhost:3000',
    //     reuseExistingServer: !process.env.CI,
    // },
});
