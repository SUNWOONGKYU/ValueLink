/**
 * @description E2E 테스트 계정 확인 스크립트
 * public.users 테이블의 E2E 계정 데이터를 조회합니다.
 */

require('dotenv').config({ path: '.env.local' })

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY

async function checkE2EUsers() {
  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/users?email=like.*e2e-*@valuelink.test&select=user_id,email,name,role,is_active`,
    {
      headers: {
        Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
        apikey: SUPABASE_SERVICE_ROLE_KEY,
      },
    }
  )

  if (!response.ok) {
    console.error('❌ Failed to fetch users:', await response.text())
    process.exit(1)
  }

  const users = await response.json()

  console.log('\n📊 E2E Test Accounts in public.users:\n')
  console.table(
    users.map((u) => ({
      email: u.email,
      name: u.name,
      role: u.role,
      is_active: u.is_active,
      user_id: u.user_id?.substring(0, 8) + '...',
    }))
  )

  console.log(`\nTotal: ${users.length} users\n`)
}

checkE2EUsers().catch(console.error)
