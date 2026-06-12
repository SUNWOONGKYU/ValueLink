// Playwright 설정 — Echo 분대 런타임 실증용
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: 'C:\\ValueLink\\tests',
  timeout: 30000,
  retries: 1,
  use: {
    headless: true,
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    // 네트워크 요청 실패(Supabase 등 외부 API)는 테스트 실패로 처리하지 않음
    // 정적 HTML 자체 렌더링만 검증
  },
  reporter: [
    ['list'],
    ['json', { outputFile: 'C:\\ValueLink\\tests\\echo-test-results.json' }],
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
