/**
 * @task S5T1
 * @description Minimal Integration Tests (2 core tests)
 *
 * Simplified integration tests to avoid rate limits and complexity:
 * - DCF Valuation Engine (core functionality)
 * - Valuation Orchestrator (engine registration)
 *
 * Full workflow testing → E2E tests (Playwright)
 *
 * Test Coverage: 2 core tests
 * No database required for these tests
 */

import { ValuationOrchestrator } from '@/lib/valuation/valuation-orchestrator'
import DCFEngine from '@/lib/valuation/engines/dcf-engine'
import type { ValuationInput } from '@/lib/valuation/types'

// ---------------------------------------------------------------------------
// Test 1: DCF Valuation Engine Execution
// ---------------------------------------------------------------------------

describe('DCF Valuation Engine', () => {
  test('Should calculate enterprise value correctly', async () => {
    const input: ValuationInput = {
      method: 'dcf',
      projectId: 'TEST-001',
      cashFlows: [1000000, 1200000, 1400000, 1600000, 1800000],
      wacc: 0.10,
      terminalGrowthRate: 0.02,
      netDebt: 500000,
      sharesOutstanding: 10000,
    }

    const engine = new DCFEngine()
    const result = await engine.calculate(input)

    // Assertions
    expect(result).toBeDefined()
    expect(result.method).toBe('DCF') // Uppercase as returned by DCF engine directly
    expect(result.enterpriseValue).toBeGreaterThan(0)
    expect(result.equityValue).toBeGreaterThan(0)
    expect(result.sharePrice).toBeGreaterThan(0)
    expect(result.details).toBeDefined()
    expect(result.timestamp).toBeDefined()

    // Mathematical accuracy
    const expectedEquityValue = result.enterpriseValue - 500000
    expect(result.equityValue).toBe(expectedEquityValue)

    const expectedSharePrice = expectedEquityValue / 10000
    expect(result.sharePrice).toBeCloseTo(expectedSharePrice, 0) // Allow integer rounding

    console.log('✅ DCF Calculation Result:', {
      enterpriseValue: result.enterpriseValue.toLocaleString(),
      equityValue: result.equityValue.toLocaleString(),
      sharePrice: result.sharePrice.toLocaleString(),
    })
  })

  test('Should handle invalid input gracefully', async () => {
    const invalidInput: ValuationInput = {
      method: 'dcf',
      projectId: 'TEST-002',
      cashFlows: [], // Empty cash flows
      wacc: 0.10,
      terminalGrowthRate: 0.02,
      netDebt: 500000,
      sharesOutstanding: 10000,
    }

    const engine = new DCFEngine()

    await expect(engine.calculate(invalidInput)).rejects.toThrow()
  })
})

// ---------------------------------------------------------------------------
// Test 2: Valuation Orchestrator
// ---------------------------------------------------------------------------

describe('Valuation Orchestrator', () => {
  test('Should register and list engines correctly', () => {
    const orchestrator = ValuationOrchestrator.getInstance()

    // Register DCF engine
    const dcfEngine = new DCFEngine()
    orchestrator.registerEngine('dcf', dcfEngine)

    // List engines
    const engines = orchestrator.getSupportedMethods()

    expect(engines).toContain('dcf')
    expect(engines.length).toBeGreaterThan(0)

    console.log('✅ Registered Engines:', engines)
  })

  test('Should execute valuation through orchestrator', async () => {
    const orchestrator = ValuationOrchestrator.getInstance()

    // Ensure DCF engine is registered
    if (!orchestrator.getSupportedMethods().includes('dcf')) {
      orchestrator.registerEngine('dcf', new DCFEngine())
    }

    const input: ValuationInput = {
      method: 'dcf',
      projectId: 'TEST-003',
      cashFlows: [500000, 600000, 720000],
      wacc: 0.12,
      terminalGrowthRate: 0.03,
      netDebt: 200000,
      sharesOutstanding: 5000,
    }

    const result = await orchestrator.valuate('dcf', input)

    expect(result).toBeDefined()
    expect(result.method).toBe('dcf') // Lowercase as returned by engine
    expect(result.enterpriseValue).toBeGreaterThan(0)

    console.log('✅ Orchestrator Execution Result:', {
      method: result.method,
      enterpriseValue: result.enterpriseValue.toLocaleString(),
      duration: result.duration + 'ms',
    })
  })
})

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

afterAll(() => {
  console.log('\n' + '='.repeat(70))
  console.log('✅ Integration Tests Complete')
  console.log('   - DCF Engine: 2 tests')
  console.log('   - Orchestrator: 2 tests')
  console.log('   - Total: 4 tests')
  console.log('='.repeat(70))
})
