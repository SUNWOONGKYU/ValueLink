/**
 * @task S5T1
 * @description Jest configuration for ValueLink integration tests
 */

const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleDirectories: ['node_modules', '<rootDir>/'],
  testMatch: [
    '<rootDir>/tests/integration/**/*.test.ts',
    '<rootDir>/tests/integration/**/*.test.tsx',
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/tests/e2e/', // E2E tests use Playwright, not Jest
  ],
  collectCoverageFrom: [
    'app/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    'Process/S2_개발-1차/Backend_APIs/**/*.{ts,tsx}',
    'Process/S3_개발-2차/Backend_APIs/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/.next/**',
  ],
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80,
    },
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^@/lib/(.*)$': '<rootDir>/Process/S2_개발-1차/Backend_APIs/lib/$1',
    '^@/lib/valuation/(.*)$': '<rootDir>/Process/S3_개발-2차/Backend_APIs/valuation/$1',
  },
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
