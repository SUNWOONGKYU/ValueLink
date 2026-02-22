/**
 * @description auth.users 테이블의 E2E 계정 확인
 */

require('dotenv').config({ path: '.env.local' })

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY

async function checkAuthUsers() {
  const response = await fetch(`${SUPABASE_URL}/auth/v1/admin/users`, {
    headers: {
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      apikey: SUPABASE_SERVICE_ROLE_KEY,
    },
  })

  if (!response.ok) {
    console.error('❌ Failed to fetch users:', await response.text())
    process.exit(1)
  }

  const data = await response.json()
  const e2eUsers = data.users.filter((u) => u.email?.includes('e2e-'))

  console.log('\n📊 E2E Test Accounts in auth.users:\n')
  console.table(
    e2eUsers.map((u) => ({
      email: u.email,
      id: u.id?.substring(0, 8) + '...',
      role: u.app_metadata?.role || 'N/A',
      confirmed: u.email_confirmed_at ? '✓' : '✗',
    }))
  )

  console.log(`\nTotal: ${e2eUsers.length} users\n`)
}

checkAuthUsers().catch(console.error)
