/**
 * @description E2E 테스트 계정 자동 생성 스크립트
 *
 * Supabase Admin API를 사용하여 3개의 고정 테스트 계정을 생성합니다:
 * - e2e-customer@valuelink.test (customer)
 * - e2e-accountant@valuelink.test (accountant)
 * - e2e-admin@valuelink.test (admin)
 *
 * 사용법: node scripts/setup-e2e-users.js
 */

require('dotenv').config({ path: '.env.local' })

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('❌ Error: Missing Supabase credentials in .env.local')
  console.error('   Required: NEXT_PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY')
  process.exit(1)
}

// F-4: 실계정(wksun999@hanmail.net 등) 목록 제거 — 전용 e2e 계정만 사용
// (실계정이 들어 있으면 스크립트가 실제 사용자 데이터를 건드릴 위험이 있음)
const TEST_PASSWORD = process.env.E2E_PASSWORD || 'E2ETest123!@#'

const TEST_ACCOUNTS = [
  {
    email: 'e2e-customer@valuelink.test',
    password: TEST_PASSWORD,
    role: 'customer',
    metadata: {
      name: 'E2E Customer',
      company_name: 'Test Company',
    },
  },
  {
    email: 'e2e-accountant@valuelink.test',
    password: TEST_PASSWORD,
    role: 'accountant',
    metadata: {
      name: 'E2E Accountant',
      license_number: 'E2E-12345',
    },
  },
  {
    email: 'e2e-admin@valuelink.test',
    password: TEST_PASSWORD,
    role: 'admin',
    metadata: {
      name: 'E2E Admin',
    },
  },
]

async function createUser(account) {
  const { email, password, role, metadata } = account

  try {
    let userId = null
    let userExisted = false

    // Step 1: Create or get user from auth.users
    const authResponse = await fetch(`${SUPABASE_URL}/auth/v1/admin/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
        apikey: SUPABASE_SERVICE_ROLE_KEY,
      },
      body: JSON.stringify({
        email,
        password,
        email_confirm: true,
        user_metadata: metadata,
        app_metadata: { role },
      }),
    })

    if (!authResponse.ok) {
      const error = await authResponse.json()

      if (
        error.code === 'user_already_exists' ||
        error.error_code === 'email_exists' ||
        error.msg?.includes('already registered')
      ) {
        // User exists - fetch user_id via Admin API
        userExisted = true
        console.log(`   Auth user exists, fetching user_id for ${email}...`)

        const listUsersResponse = await fetch(
          `${SUPABASE_URL}/auth/v1/admin/users?email=${encodeURIComponent(email)}`,
          {
            headers: {
              Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
              apikey: SUPABASE_SERVICE_ROLE_KEY,
            },
          }
        )

        if (listUsersResponse.ok) {
          const listData = await listUsersResponse.json()
          // ⚠️ Admin API가 email 쿼리 필터를 무시하고 전체 목록을 반환할 수 있음.
          // users[0]을 그대로 쓰면 다른 사용자의 user_id가 들어가는 사고 발생
          // (실제로 e2e-customer에 e2e-admin의 auth id가 들어갔던 전례 있음).
          // 반드시 이메일 일치를 검증한다.
          const found = (listData.users || []).find(
            (u) => u.email?.toLowerCase() === email.toLowerCase()
          )
          if (found) {
            userId = found.id
            console.log(`   Found user_id: ${userId.substring(0, 8)}...`)
          } else {
            throw new Error('User exists but not found in list')
          }
        } else {
          throw new Error('Failed to fetch existing user')
        }
      } else {
        throw new Error(`HTTP ${authResponse.status}: ${JSON.stringify(error)}`)
      }
    } else {
      const authData = await authResponse.json()
      userId = authData.id
    }

    if (!userId) {
      throw new Error('Could not determine user_id')
    }

    // Step 2: Insert or update public.users table
    const checkUserResponse = await fetch(
      `${SUPABASE_URL}/rest/v1/users?user_id=eq.${userId}&select=user_id`,
      {
        headers: {
          Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
          apikey: SUPABASE_SERVICE_ROLE_KEY,
        },
      }
    )

    const existingUsers = await checkUserResponse.json()

    if (existingUsers.length === 0) {
      // Insert into public.users
      const insertResponse = await fetch(`${SUPABASE_URL}/rest/v1/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
          apikey: SUPABASE_SERVICE_ROLE_KEY,
          Prefer: 'return=minimal',
        },
        body: JSON.stringify({
          user_id: userId,
          email,
          name: metadata.name,
          role,
          company_name: metadata.company_name || null,
          is_active: true,
        }),
      })

      if (!insertResponse.ok) {
        const error = await insertResponse.text()
        throw new Error(`Failed to insert into users table: ${error}`)
      }

      console.log(
        `✅ Created user: ${email} (role: ${role}, user_id: ${userId.substring(0, 8)}...)`
      )
    } else {
      console.log(`⚠️  User already in public.users: ${email}`)
    }

    return { success: true, existed: userExisted }
  } catch (error) {
    console.error(`❌ Failed to create ${email}:`, error.message)
    return { success: false, error: error.message }
  }
}

async function setupE2EUsers() {
  console.log('🚀 Setting up E2E test accounts...\n')

  const results = []
  for (const account of TEST_ACCOUNTS) {
    const result = await createUser(account)
    results.push({ email: account.email, ...result })

    // Rate limit 방지를 위한 딜레이
    await new Promise((resolve) => setTimeout(resolve, 500))
  }

  console.log('\n📊 Summary:')
  const created = results.filter((r) => r.success && !r.existed).length
  const existed = results.filter((r) => r.success && r.existed).length
  const failed = results.filter((r) => !r.success).length

  console.log(`   ✅ Created: ${created}`)
  console.log(`   ⚠️  Already existed: ${existed}`)
  console.log(`   ❌ Failed: ${failed}`)

  if (failed > 0) {
    console.log('\n❌ Some accounts failed to create. Check errors above.')
    process.exit(1)
  }

  console.log('\n✨ E2E test accounts ready!')
  console.log('\nNext step: npm run test:e2e')
}

// Run
setupE2EUsers().catch((error) => {
  console.error('❌ Fatal error:', error)
  process.exit(1)
})
