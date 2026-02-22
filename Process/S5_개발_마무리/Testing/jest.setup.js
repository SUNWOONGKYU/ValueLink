/**
 * @task S5T1
 * @description Jest setup file - runs before all tests
 */

// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Mock environment variables
process.env.NEXT_PUBLIC_SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://test.supabase.co'
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'test-anon-key'

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
