/**
 * @description 누락된 E2E 테스트 계정 수동 추가
 * auth.users에서 user_id를 조회하고 public.users에 추가합니다.
 */

require('dotenv').config({ path: '.env.local' })

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY

const MISSING_ACCOUNTS = [
  {
    email: 'e2e-accountant@valuelink.test',
    name: 'E2E Test Accountant',
    role: 'accountant',
  },
  {
    email: 'e2e-admin@valuelink.test',
    name: 'E2E Test Admin',
    role: 'admin',
  },
]

async function getUserIdByEmail(email) {
  // Fetch ALL users and filter client-side for exact match
  const response = await fetch(`${SUPABASE_URL}/auth/v1/admin/users`, {
    headers: {
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      apikey: SUPABASE_SERVICE_ROLE_KEY,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch users: ${await response.text()}`)
  }

  const data = await response.json()
  const user = data.users.find((u) => u.email === email)

  if (!user) {
    throw new Error(`User not found in auth.users: ${email}`)
  }

  return user.id
}

async function insertIntoPublicUsers(userId, email, name, role) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/users`, {
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
      name,
      role,
      is_active: true,
    }),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to insert into public.users: ${error}`)
  }
}

async function fixE2EUsers() {
  console.log('🔧 Fixing missing E2E accounts...\n')

  for (const account of MISSING_ACCOUNTS) {
    try {
      console.log(`Processing ${account.email}...`)

      // Step 1: Get user_id from auth.users
      const userId = await getUserIdByEmail(account.email)
      console.log(`  ✓ Found user_id: ${userId.substring(0, 8)}...`)

      // Step 2: Insert into public.users
      await insertIntoPublicUsers(userId, account.email, account.name, account.role)
      console.log(`  ✓ Inserted into public.users with role: ${account.role}`)

      console.log(`✅ ${account.email} fixed!\n`)
    } catch (error) {
      console.error(`❌ Failed to fix ${account.email}:`, error.message)
    }
  }

  console.log('✨ Done! Run: node scripts/check-e2e-users.js')
}

fixE2EUsers().catch(console.error)
