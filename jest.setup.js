/**
 * @task S5T1
 * @description Jest setup file - runs before all tests
 */

// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Polyfill fetch for Node.js < 18
if (!globalThis.fetch) {
  globalThis.fetch = require('whatwg-fetch').fetch
}

// Load environment variables from .env.local
require('dotenv').config({ path: '.env.local' })

// Use real Supabase for integration tests (not mocked)
if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
  console.warn('⚠️  NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY not set. Tests may fail.')
}

// Extend Jest matchers
expect.extend({
  toBeCloseTo(received, expected, precision = 2) {
    const pass = Math.abs(received - expected) < Math.pow(10, -precision) / 2
    if (pass) {
      return {
        message: () => `expected ${received} not to be close to ${expected}`,
        pass: true,
      }
    } else {
      return {
        message: () => `expected ${received} to be close to ${expected}`,
        pass: false,
      }
    }
  },
})
