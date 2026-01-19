/**
 * Jest Configuration Template
 *
 * 사용법:
 * 1. 이 파일을 jest.config.js로 복사
 * 2. 프로젝트에 맞게 경로 수정
 * 3. npm install jest --save-dev
 */

module.exports = {
    // 테스트 환경
    testEnvironment: 'jsdom',  // 브라우저 환경 시뮬레이션
    // testEnvironment: 'node',  // Node.js 환경

    // 테스트 파일 패턴
    testMatch: [
        '**/tests/unit/**/*.test.js',
        '**/tests/**/*.spec.js'
    ],

    // 모듈 경로 별칭 (선택)
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
        '^@components/(.*)$': '<rootDir>/src/components/$1',
        '^@utils/(.*)$': '<rootDir>/src/utils/$1'
    },

    // 커버리지 수집 대상
    collectCoverageFrom: [
        'src/**/*.js',
        'api/**/*.js',
        '!**/node_modules/**',
        '!**/vendor/**'
    ],

    // 커버리지 임계값
    coverageThreshold: {
        global: {
            branches: 70,
            functions: 70,
            lines: 70,
            statements: 70
        }
    },

    // 커버리지 리포터
    coverageReporters: ['text', 'lcov', 'html'],

    // 커버리지 출력 디렉토리
    coverageDirectory: 'coverage',

    // 테스트 전 설정 파일
    setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],

    // 변환 무시 패턴
    transformIgnorePatterns: [
        '/node_modules/',
        '\\.css$'
    ],

    // 상세 출력
    verbose: true,

    // 타임아웃 (ms)
    testTimeout: 10000,

    // 글로벌 변수 (선택)
    globals: {
        API_URL: 'http://localhost:3000',
        TEST_MODE: true
    }
};
