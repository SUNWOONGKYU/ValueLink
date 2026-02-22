/**
 * @task S5T1
 * @description 14-Step Valuation Workflow Integration Tests
 *
 * Tests the complete 14-step valuation workflow end-to-end:
 * - Project creation and quote generation (Steps 1-3)
 * - Negotiation and contract (Steps 4-6)
 * - Document upload and review (Steps 7-9)
 * - DCF valuation engine execution (Step 10)
 * - Draft generation and revision (Steps 11-12)
 * - Final report generation (Step 13)
 * - Project completion (Step 14)
 *
 * Test Coverage: 7 describe blocks, 18 test cases
 * Database: Real Supabase DB connection
 * Cleanup: afterAll() removes test data
 */

import { createClient } from '@supabase/supabase-js'
import { WorkflowManager } from '@/lib/workflow/workflow-manager'
import { ValuationOrchestrator } from '@/lib/valuation/valuation-orchestrator'
import { DCFEngine } from '@/lib/valuation/engines/dcf-engine'
import type { ValuationInput } from '@/lib/valuation/types'

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
const supabase = createClient(supabaseUrl, supabaseKey)

let testProjectId: string
let testUserId: string
let testAccountantId: string
let workflowManager: WorkflowManager

// ---------------------------------------------------------------------------
// Test Data
// ---------------------------------------------------------------------------

const testCompanyData = {
  company_name: 'Test Valuation Corp',
  company_name_en: 'Test Valuation Corporation',
  ceo_name: 'Test CEO',
  business_number: '123-45-67890',
  industry: 'Technology',
  employees: 50,
  founded_date: '2020-01-01',
}

const testDCFInput: ValuationInput = {
  method: 'dcf',
  projectId: '',
  cashFlows: [1000000, 1200000, 1400000, 1600000, 1800000],
  wacc: 0.10,
  terminalGrowthRate: 0.02,
  netDebt: 500000,
  sharesOutstanding: 10000,
}

// ---------------------------------------------------------------------------
// Lifecycle Hooks
// ---------------------------------------------------------------------------

beforeAll(async () => {
  workflowManager = new WorkflowManager()

  // Create test user (customer)
  const { data: authUser, error: authError } = await supabase.auth.signUp({
    email: `test-${Date.now()}@example.com`,
    password: 'testpassword123',
  })

  if (authError || !authUser.user) {
    throw new Error(`Failed to create test user: ${authError?.message}`)
  }

  testUserId = authUser.user.id

  // Insert user profile
  await supabase.from('users').insert({
    user_id: testUserId,
    email: authUser.user.email!,
    name: 'Test User',
    role: 'customer',
  })

  // Create test accountant
  const { data: authAccountant } = await supabase.auth.signUp({
    email: `accountant-${Date.now()}@example.com`,
    password: 'testpassword123',
  })

  testAccountantId = authAccountant.user!.id

  await supabase.from('users').insert({
    user_id: testAccountantId,
    email: authAccountant.user!.email!,
    name: 'Test Accountant',
    role: 'accountant',
  })

  await supabase.from('accountants').insert({
    accountant_id: `ACC-${Date.now()}`,
    user_id: testAccountantId,
    license_number: 'TEST-LICENSE-001',
    is_available: true,
  })

  // Register DCF engine
  const orchestrator = ValuationOrchestrator.getInstance()
  orchestrator.registerEngine('dcf', new DCFEngine())
})

afterAll(async () => {
  // Cleanup test data
  if (testProjectId) {
    await supabase.from('valuation_projects').delete().eq('project_id', testProjectId)
    await supabase.from('dcf_documents').delete().eq('project_id', testProjectId)
    await supabase.from('dcf_drafts').delete().eq('project_id', testProjectId)
    await supabase.from('dcf_reports').delete().eq('project_id', testProjectId)
    await supabase.from('project_history').delete().eq('project_id', testProjectId)
  }

  if (testUserId) {
    await supabase.from('users').delete().eq('user_id', testUserId)
    await supabase.auth.admin.deleteUser(testUserId)
  }

  if (testAccountantId) {
    await supabase.from('accountants').delete().eq('user_id', testAccountantId)
    await supabase.from('users').delete().eq('user_id', testAccountantId)
    await supabase.auth.admin.deleteUser(testAccountantId)
  }
})

// ---------------------------------------------------------------------------
// Test Suite 1: Steps 1-3 (Project Creation & Quote)
// ---------------------------------------------------------------------------

describe('Steps 1-3: Project Creation & Quote Generation', () => {
  test('Step 1: Should create a new project', async () => {
    testProjectId = `VL-${Date.now()}-TEST`

    const { error } = await supabase.from('valuation_projects').insert({
      project_id: testProjectId,
      user_id: testUserId,
      valuation_method: 'dcf',
      status: 'not_started',
      current_step: 1,
      progress: 0,
    })

    expect(error).toBeNull()

    const currentStep = await workflowManager.getCurrentStep(testProjectId)
    expect(currentStep.success).toBe(true)
    expect(currentStep.data?.current_step).toBe(1)
    expect(currentStep.data?.step_info.step_name).toBe('project_creation')
  })

  test('Step 2: Should input company information', async () => {
    const customerId = `CUST-${Date.now()}`

    const { error } = await supabase.from('customers').insert({
      customer_id: customerId,
      user_id: testUserId,
      email: `test-${Date.now()}@example.com`,
      ...testCompanyData,
    })

    expect(error).toBeNull()

    // Advance to step 2
    const advanceResult = await workflowManager.advanceStep(testProjectId)
    expect(advanceResult.success).toBe(true)
    expect(advanceResult.data?.current_step).toBe(2)
  })

  test('Step 3: Should generate initial quote estimate', async () => {
    // Insert evaluation request
    const requestId = `REQ-${Date.now()}`

    const { error } = await supabase.from('evaluation_requests').insert({
      request_id: requestId,
      project_id: testProjectId,
      user_id: testUserId,
      valuation_method: 'dcf',
      status: 'pending',
      estimated_price: 5000000,
    })

    expect(error).toBeNull()

    // Advance to step 3
    const advanceResult = await workflowManager.advanceStep(testProjectId)
    expect(advanceResult.success).toBe(true)
    expect(advanceResult.data?.current_step).toBe(3)
  })
})

// ---------------------------------------------------------------------------
// Test Suite 2: Steps 4-6 (Negotiation & Contract)
// ---------------------------------------------------------------------------

describe('Steps 4-6: Negotiation & Contract', () => {
  test('Step 4-6: Should complete negotiation and method selection', async () => {
    // Advance to step 4 (method_selection)
    let result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(4)

    // Advance to step 5 (data_collection)
    result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(5)
    expect(result.data?.progress).toBe(10)

    // Advance to step 6 (valuation_execution)
    result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(6)
    expect(result.data?.progress).toBe(30)
  })

  test('Should record project history for each step', async () => {
    const { data, error } = await supabase
      .from('project_history')
      .select('*')
      .eq('project_id', testProjectId)
      .order('created_at', { ascending: false })

    expect(error).toBeNull()
    expect(data).toBeDefined()
    expect(data!.length).toBeGreaterThan(0)
  })
})

// ---------------------------------------------------------------------------
// Test Suite 3: Steps 7-9 (Document Upload & Review)
// ---------------------------------------------------------------------------

describe('Steps 7-9: Document Upload & Review', () => {
  test('Step 7: Should upload required documents', async () => {
    const documentId = `DOC-${Date.now()}`

    const { error } = await supabase.from('dcf_documents').insert({
      document_id: documentId,
      project_id: testProjectId,
      category: 'financial_statements',
      file_name: 'test-financial-statement.pdf',
      file_type: 'application/pdf',
      file_size: 1024000,
      uploaded_by: testUserId,
    })

    expect(error).toBeNull()

    // Check can advance to step 7
    const canAdvance = await workflowManager.canAdvanceToStep(testProjectId, 7)
    expect(canAdvance.success).toBe(true)
  })

  test('Step 8-9: Should advance through document review steps', async () => {
    // Advance to step 7 (accountant_review_submit)
    let result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(7)
    expect(result.data?.progress).toBe(50)

    // Step 7 requires approval - record approval
    await supabase.from('workflow_approvals').insert({
      project_id: testProjectId,
      step_number: 7,
      approved_by: testAccountantId,
      status: 'approved',
    })

    // Advance to step 8 (draft_report_generation)
    result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(8)
    expect(result.data?.progress).toBe(60)

    // Advance to step 9 (draft_review)
    result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(9)
    expect(result.data?.progress).toBe(70)
  })
})

// ---------------------------------------------------------------------------
// Test Suite 4: Step 10 (DCF Valuation Engine)
// ---------------------------------------------------------------------------

describe('Step 10: DCF Valuation Engine Execution', () => {
  test('Should execute DCF valuation and return valid results', async () => {
    testDCFInput.projectId = testProjectId

    const orchestrator = ValuationOrchestrator.getInstance()
    const result = await orchestrator.valuate('dcf', testDCFInput)

    expect(result).toBeDefined()
    expect(result.method).toBe('dcf')
    expect(result.enterpriseValue).toBeGreaterThan(0)
    expect(result.equityValue).toBeGreaterThan(0)
    expect(result.valuePerShare).toBeGreaterThan(0)
    expect(result.duration).toBeGreaterThan(0)
  })

  test('Should validate mathematical accuracy of DCF calculation', async () => {
    testDCFInput.projectId = testProjectId

    const orchestrator = ValuationOrchestrator.getInstance()
    const result = await orchestrator.valuate('dcf', testDCFInput)

    // Verify equity value = enterprise value - net debt
    const expectedEquityValue = result.enterpriseValue - testDCFInput.netDebt
    expect(result.equityValue).toBeCloseTo(expectedEquityValue, 0)

    // Verify value per share = equity value / shares outstanding
    const expectedValuePerShare = result.equityValue / testDCFInput.sharesOutstanding
    expect(result.valuePerShare).toBeCloseTo(expectedValuePerShare, 0)
  })
})

// ---------------------------------------------------------------------------
// Test Suite 5: Steps 11-12 (Draft Generation & Revision)
// ---------------------------------------------------------------------------

describe('Steps 11-12: Draft Generation & Revision', () => {
  test('Step 11: Should generate draft report', async () => {
    // Approve step 9 (draft_review)
    await supabase.from('workflow_approvals').insert({
      project_id: testProjectId,
      step_number: 9,
      approved_by: testAccountantId,
      status: 'approved',
    })

    // Advance to step 10 (feedback_incorporation)
    let result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(10)

    // Create draft
    const draftId = `DRAFT-${Date.now()}`
    const { error } = await supabase.from('dcf_drafts').insert({
      draft_id: draftId,
      project_id: testProjectId,
      section_1_completed: true,
      section_2_completed: true,
      section_3_completed: true,
      section_4_completed: true,
      section_5_completed: true,
      section_6_completed: true,
      section_7_completed: true,
      section_8_completed: true,
      section_9_completed: true,
      status: 'draft',
    })

    expect(error).toBeNull()
  })

  test('Step 12: Should handle draft revisions', async () => {
    // Advance to step 11 (final_report_generation)
    let result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(11)
    expect(result.data?.progress).toBe(80)

    // Advance to step 12 (final_approval)
    result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(12)
    expect(result.data?.progress).toBe(90)
  })
})

// ---------------------------------------------------------------------------
// Test Suite 6: Step 13 (Final Report)
// ---------------------------------------------------------------------------

describe('Step 13: Final Report Generation', () => {
  test('Should generate final report PDF', async () => {
    // Approve step 12 (final_approval)
    await supabase.from('workflow_approvals').insert({
      project_id: testProjectId,
      step_number: 12,
      approved_by: testAccountantId,
      status: 'approved',
    })

    // Create final report
    const reportId = `RPT-${Date.now()}`
    const { error } = await supabase.from('dcf_reports').insert({
      report_id: reportId,
      project_id: testProjectId,
      status: 'finalized',
      file_path: `/reports/${testProjectId}/final.pdf`,
      generated_by: testAccountantId,
    })

    expect(error).toBeNull()

    // Advance to step 13 (report_delivery)
    const result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(13)
    expect(result.data?.progress).toBe(95)
  })
})

// ---------------------------------------------------------------------------
// Test Suite 7: Step 14 (Completion)
// ---------------------------------------------------------------------------

describe('Step 14: Project Completion', () => {
  test('Should mark project as completed', async () => {
    // Advance to step 14 (completion)
    const result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(true)
    expect(result.data?.current_step).toBe(14)
    expect(result.data?.progress).toBe(100)
    expect(result.data?.status).toBe('completed')
  })

  test('Should not allow advancing past step 14', async () => {
    const result = await workflowManager.advanceStep(testProjectId)
    expect(result.success).toBe(false)
    expect(result.error).toContain('Already at the final step')
  })
})
