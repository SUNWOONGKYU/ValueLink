/**
 * @task S2F7
 * @description Register Page - Multi-step registration (3 steps)
 *
 * Step 1: Basic info (name, email, password, password confirm)
 * Step 2: Role selection (customer, accountant, admin, investor)
 * Step 3: Role-specific additional info
 *
 * After registration:
 * 1. supabase.auth.signUp
 * 2. Insert into users table (user_id, email, name, role, is_active)
 * 3. If customer -> insert customers table
 * 4. If accountant -> insert accountants table
 *
 * Schema: users.name (NOT full_name), users.company_name (NOT company_name_kr)
 * Korean language UI, ARIA attributes, responsive Tailwind CSS
 */

'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { createBrowserClient } from '@supabase/ssr'
import Link from 'next/link'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

// Admin code is verified server-side via /api/auth/verify-admin-code

type Role = 'customer' | 'accountant' | 'admin' | 'investor'

interface RoleOption {
  value: Role
  label: string
  description: string
  icon: string
}

const ROLE_OPTIONS: RoleOption[] = [
  { value: 'customer', label: '고객', description: '평가 신청', icon: 'M3 21V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v16l-7-3.5L7 21V5' },
  { value: 'accountant', label: '공인회계사', description: '평가 수행', icon: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M12 7a4 4 0 1 0-8 0 4 4 0 0 0 8 0M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75' },
  { value: 'admin', label: '관리자', description: '플랫폼 관리', icon: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z' },
  { value: 'investor', label: '투자자', description: '투자 검토', icon: 'M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6' },
]

const STEP_LABELS = ['기본 정보', '역할 선택', '추가 정보']

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function RegisterPage() {
  const router = useRouter()
  const supabase = createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY)

  // ---- Step state ----
  const [currentStep, setCurrentStep] = useState(1)

  // ---- Step 1: Basic info ----
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')

  // ---- Step 2: Role ----
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)

  // ---- Step 3: Customer fields ----
  const [companyName, setCompanyName] = useState('')
  const [companyNameEn, setCompanyNameEn] = useState('')
  const [businessNumber, setBusinessNumber] = useState('')
  const [ceoName, setCeoName] = useState('')
  const [industry, setIndustry] = useState('')
  const [foundedDate, setFoundedDate] = useState('')
  const [phone, setPhone] = useState('')

  // ---- Step 3: Accountant fields ----
  const [licenseNumber, setLicenseNumber] = useState('')
  const [accountantPhone, setAccountantPhone] = useState('')
  const [educationList, setEducationList] = useState<string[]>([''])
  const [careerList, setCareerList] = useState<string[]>([''])
  const [specialization, setSpecialization] = useState('')

  // ---- Step 3: Admin fields ----
  const [adminCode, setAdminCode] = useState('')

  // ---- Form state ----
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [globalError, setGlobalError] = useState<string | null>(null)

  // ---------------------------------------------------------------------------
  // Validation
  // ---------------------------------------------------------------------------

  function validateStep1(): boolean {
    const newErrors: Record<string, string> = {}

    if (!name.trim()) newErrors.name = '이름을 입력해주세요'
    if (!email.trim()) {
      newErrors.email = '이메일을 입력해주세요'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = '올바른 이메일 형식이 아닙니다'
    }
    if (!password) {
      newErrors.password = '비밀번호를 입력해주세요'
    } else if (password.length < 8) {
      newErrors.password = '비밀번호는 최소 8자 이상이어야 합니다'
    }
    if (!passwordConfirm) {
      newErrors.passwordConfirm = '비밀번호 확인을 입력해주세요'
    } else if (password !== passwordConfirm) {
      newErrors.passwordConfirm = '비밀번호가 일치하지 않습니다'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  function validateStep2(): boolean {
    const newErrors: Record<string, string> = {}
    if (!selectedRole) newErrors.role = '역할을 선택해주세요'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  function validateStep3(): boolean {
    const newErrors: Record<string, string> = {}

    if (selectedRole === 'customer') {
      if (!companyName.trim()) newErrors.companyName = '회사명(국문)을 입력해주세요'
      if (!companyNameEn.trim()) newErrors.companyNameEn = '회사명(영문)을 입력해주세요'
      if (!businessNumber.trim()) newErrors.businessNumber = '사업자등록번호를 입력해주세요'
      if (!ceoName.trim()) newErrors.ceoName = '대표자명을 입력해주세요'
    }

    if (selectedRole === 'accountant') {
      if (!licenseNumber.trim()) newErrors.licenseNumber = '면허번호를 입력해주세요'
    }

    if (selectedRole === 'admin') {
      if (!adminCode.trim()) newErrors.adminCode = '관리자 인증 코드를 입력해주세요'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // ---------------------------------------------------------------------------
  // Step Navigation
  // ---------------------------------------------------------------------------

  function goNext() {
    setGlobalError(null)
    if (currentStep === 1 && validateStep1()) setCurrentStep(2)
    else if (currentStep === 2 && validateStep2()) setCurrentStep(3)
  }

  function goPrev() {
    setErrors({})
    setGlobalError(null)
    if (currentStep > 1) setCurrentStep(currentStep - 1)
  }

  // ---------------------------------------------------------------------------
  // Education / Career array helpers
  // ---------------------------------------------------------------------------

  function addEducation() {
    setEducationList([...educationList, ''])
  }

  function removeEducation(index: number) {
    if (educationList.length <= 1) return
    setEducationList(educationList.filter((_, i) => i !== index))
  }

  function updateEducation(index: number, value: string) {
    const updated = [...educationList]
    updated[index] = value
    setEducationList(updated)
  }

  function addCareer() {
    setCareerList([...careerList, ''])
  }

  function removeCareer(index: number) {
    if (careerList.length <= 1) return
    setCareerList(careerList.filter((_, i) => i !== index))
  }

  function updateCareer(index: number, value: string) {
    const updated = [...careerList]
    updated[index] = value
    setCareerList(updated)
  }

  // ---------------------------------------------------------------------------
  // Submit
  // ---------------------------------------------------------------------------

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setGlobalError(null)

    if (!validateStep3()) return
    if (!selectedRole) return

    // Admin code verification (server-side)
    if (selectedRole === 'admin') {
      try {
        const verifyRes = await fetch('/api/auth/verify-admin-code', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: adminCode }),
        })
        const verifyData = await verifyRes.json()
        if (!verifyData.valid) {
          setErrors({ adminCode: verifyData.error || '관리자 인증 코드가 올바르지 않습니다' })
          return
        }
      } catch {
        setErrors({ adminCode: '관리자 코드 검증 중 오류가 발생했습니다' })
        return
      }
    }

    setIsLoading(true)

    try {
      // 1. Supabase Auth sign up
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: email.trim(),
        password,
      })

      if (authError) throw authError
      if (!authData.user) throw new Error('회원가입에 실패했습니다')

      const userId = authData.user.id

      // 2. Insert into users table
      const { error: userError } = await supabase.from('users').insert([
        {
          user_id: userId,
          email: email.trim(),
          name: name.trim(),
          role: selectedRole,
          phone: selectedRole === 'customer' ? phone.trim() || null : selectedRole === 'accountant' ? accountantPhone.trim() || null : null,
          company_name: selectedRole === 'customer' ? companyName.trim() : null,
          is_active: true,
        },
      ])

      if (userError) throw userError

      // 3. Role-specific table inserts
      if (selectedRole === 'customer') {
        const { error: custError } = await supabase.from('customers').insert([
          {
            customer_id: 'CUS' + Date.now().toString().slice(-8),
            user_id: userId,
            email: email.trim(),
            company_name: companyName.trim(),
            company_name_en: companyNameEn.trim(),
            business_number: businessNumber.trim(),
            ceo_name: ceoName.trim(),
            industry: industry.trim() || null,
            founded_date: foundedDate || null,
            phone: phone.trim() || null,
          },
        ])
        if (custError) throw custError
      }

      if (selectedRole === 'accountant') {
        const filteredEducation = educationList.filter((v) => v.trim())
        const filteredCareer = careerList.filter((v) => v.trim())
        const parsedSpecialization = specialization
          .split(',')
          .map((s) => s.trim())
          .filter((s) => s)

        const { error: accError } = await supabase.from('accountants').insert([
          {
            accountant_id: 'ACC' + Date.now().toString().slice(-8),
            user_id: userId,
            license_number: licenseNumber.trim(),
            education: filteredEducation.length > 0 ? filteredEducation : null,
            career: filteredCareer.length > 0 ? filteredCareer : null,
            specialization: parsedSpecialization.length > 0 ? parsedSpecialization : null,
            rating: 0.0,
            total_projects: 0,
            is_available: true,
          },
        ])
        if (accError) throw accError
      }

      // 4. Success -> redirect to login
      router.push('/login?registered=true')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '회원가입 중 오류가 발생했습니다'

      if (message.includes('already registered') || message.includes('already been registered')) {
        setGlobalError('이미 등록된 이메일입니다. 로그인 페이지에서 로그인해주세요.')
      } else {
        setGlobalError(message)
      }
    } finally {
      setIsLoading(false)
    }
  }

  // ---------------------------------------------------------------------------
  // Sub-components
  // ---------------------------------------------------------------------------

  function FieldError({ field }: { field: string }) {
    return errors[field] ? (
      <p className="mt-1.5 text-xs text-red-500" role="alert">
        {errors[field]}
      </p>
    ) : null
  }

  function inputClass(field: string) {
    return `w-full px-4 py-3 text-sm border-2 rounded-xl transition-all focus:outline-none focus:ring-0 ${
      errors[field]
        ? 'border-red-400 focus:border-red-500'
        : 'border-gray-200 focus:border-blue-600 focus:shadow-[0_0_0_3px_rgba(219,234,254,1)]'
    }`
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-700 to-blue-900 flex items-center justify-center px-4 py-8">
      <div className="bg-white rounded-2xl shadow-2xl max-w-[600px] w-full overflow-hidden">
        {/* Card Header */}
        <div className="bg-gradient-to-br from-blue-700 to-blue-900 text-white px-10 py-8 text-center">
          <h1 className="text-3xl font-bold mb-2">ValueLink 회원가입</h1>
          <p className="text-blue-200 text-sm">프로젝트 평가를 시작하세요</p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white px-10 py-6 border-b border-gray-200">
          <div className="flex justify-between items-start relative">
            {/* Progress line background */}
            <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200" />
            {/* Progress line active */}
            <div
              className="absolute top-5 left-0 h-0.5 bg-blue-700 transition-all duration-300"
              style={{ width: `${((currentStep - 1) / 2) * 100}%` }}
            />

            {STEP_LABELS.map((label, idx) => {
              const stepNum = idx + 1
              const isActive = stepNum === currentStep
              const isCompleted = stepNum < currentStep

              return (
                <div
                  key={label}
                  className="flex flex-col items-center relative z-10"
                >
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm mb-2 transition-all ${
                      isCompleted
                        ? 'bg-emerald-500 border-2 border-emerald-500 text-white'
                        : isActive
                        ? 'bg-blue-700 border-2 border-blue-700 text-white'
                        : 'bg-gray-100 border-2 border-gray-200 text-gray-400'
                    }`}
                    aria-current={isActive ? 'step' : undefined}
                  >
                    {isCompleted ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      stepNum
                    )}
                  </div>
                  <span
                    className={`text-xs font-medium ${
                      isActive ? 'text-blue-700 font-semibold' : 'text-gray-400'
                    }`}
                  >
                    {label}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Form */}
        <div className="px-10 py-8">
          {/* Global Error */}
          {globalError && (
            <div
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm"
              role="alert"
            >
              {globalError}
            </div>
          )}

          {/* ================================================================ */}
          {/* STEP 1: Basic Info */}
          {/* ================================================================ */}
          {currentStep === 1 && (
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-1">기본 정보</h2>
              <p className="text-sm text-gray-500 mb-7">먼저 기본 정보를 입력해주세요</p>

              {/* Name */}
              <div className="mb-5">
                <label htmlFor="reg-name" className="block text-sm font-semibold text-gray-700 mb-2">
                  이름 <span className="text-red-500">*</span>
                </label>
                <input
                  id="reg-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="홍길동"
                  autoComplete="name"
                  aria-required="true"
                  className={inputClass('name')}
                />
                <FieldError field="name" />
              </div>

              {/* Email */}
              <div className="mb-5">
                <label htmlFor="reg-email" className="block text-sm font-semibold text-gray-700 mb-2">
                  이메일 <span className="text-red-500">*</span>
                </label>
                <input
                  id="reg-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="example@email.com"
                  autoComplete="email"
                  aria-required="true"
                  className={inputClass('email')}
                />
                <p className="mt-1.5 text-xs text-gray-400">로그인 ID로 사용됩니다</p>
                <FieldError field="email" />
              </div>

              {/* Password */}
              <div className="mb-5">
                <label htmlFor="reg-password" className="block text-sm font-semibold text-gray-700 mb-2">
                  비밀번호 <span className="text-red-500">*</span>
                </label>
                <input
                  id="reg-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="영문, 숫자 포함 8자 이상"
                  autoComplete="new-password"
                  aria-required="true"
                  className={inputClass('password')}
                />
                <FieldError field="password" />
              </div>

              {/* Password Confirm */}
              <div className="mb-5">
                <label htmlFor="reg-password-confirm" className="block text-sm font-semibold text-gray-700 mb-2">
                  비밀번호 확인 <span className="text-red-500">*</span>
                </label>
                <input
                  id="reg-password-confirm"
                  type="password"
                  value={passwordConfirm}
                  onChange={(e) => setPasswordConfirm(e.target.value)}
                  placeholder="비밀번호를 다시 입력하세요"
                  autoComplete="new-password"
                  aria-required="true"
                  className={inputClass('passwordConfirm')}
                />
                <FieldError field="passwordConfirm" />
              </div>

              {/* Next Button */}
              <div className="mt-8">
                <button
                  type="button"
                  onClick={goNext}
                  className="w-full py-3.5 text-sm font-semibold text-white bg-blue-700 rounded-xl transition-all hover:bg-blue-800 hover:-translate-y-0.5 hover:shadow-lg"
                >
                  다음 단계
                </button>
              </div>

              <div className="text-center mt-6 pt-6 border-t border-gray-200 text-sm text-gray-500">
                이미 계정이 있으신가요?{' '}
                <Link href="/login" className="font-semibold text-blue-700 hover:underline">
                  로그인
                </Link>
              </div>
            </div>
          )}

          {/* ================================================================ */}
          {/* STEP 2: Role Selection */}
          {/* ================================================================ */}
          {currentStep === 2 && (
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-1">역할 선택</h2>
              <p className="text-sm text-gray-500 mb-7">서비스 이용 목적을 선택해주세요</p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
                {ROLE_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    htmlFor={`role-${opt.value}`}
                    className={`relative flex flex-col items-center p-6 border-2 rounded-xl cursor-pointer transition-all ${
                      selectedRole === opt.value
                        ? 'border-blue-700 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/50'
                    }`}
                  >
                    <input
                      id={`role-${opt.value}`}
                      type="radio"
                      name="role"
                      value={opt.value}
                      checked={selectedRole === opt.value}
                      onChange={() => setSelectedRole(opt.value)}
                      className="sr-only"
                      aria-required="true"
                    />
                    {/* Checkmark */}
                    {selectedRole === opt.value && (
                      <div className="absolute top-2 right-2 w-6 h-6 bg-blue-700 text-white rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    )}
                    {/* Icon */}
                    <div className="w-12 h-12 mb-3 text-blue-700">
                      <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d={opt.icon} />
                      </svg>
                    </div>
                    <span className="text-sm font-semibold text-gray-900 mb-1">{opt.label}</span>
                    <span className="text-xs text-gray-500">{opt.description}</span>
                  </label>
                ))}
              </div>

              <FieldError field="role" />

              {/* Buttons */}
              <div className="flex gap-3 mt-8">
                <button
                  type="button"
                  onClick={goPrev}
                  className="flex-1 py-3.5 text-sm font-semibold text-gray-700 bg-gray-100 rounded-xl transition-all hover:bg-gray-200"
                >
                  이전
                </button>
                <button
                  type="button"
                  onClick={goNext}
                  className="flex-1 py-3.5 text-sm font-semibold text-white bg-blue-700 rounded-xl transition-all hover:bg-blue-800 hover:-translate-y-0.5 hover:shadow-lg"
                >
                  다음 단계
                </button>
              </div>
            </div>
          )}

          {/* ================================================================ */}
          {/* STEP 3: Role-Specific Info */}
          {/* ================================================================ */}
          {currentStep === 3 && (
            <form onSubmit={handleSubmit} noValidate>
              {/* ---- Customer Fields ---- */}
              {selectedRole === 'customer' && (
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-1">회사 정보</h2>
                  <p className="text-sm text-gray-500 mb-7">회사의 기본 정보를 입력해주세요</p>

                  <div className="mb-5">
                    <label htmlFor="company-name" className="block text-sm font-semibold text-gray-700 mb-2">
                      회사명 (국문) <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="company-name"
                      type="text"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="예: 삼성전자"
                      className={inputClass('companyName')}
                    />
                    <FieldError field="companyName" />
                  </div>

                  <div className="mb-5">
                    <label htmlFor="company-name-en" className="block text-sm font-semibold text-gray-700 mb-2">
                      회사명 (영문) <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="company-name-en"
                      type="text"
                      value={companyNameEn}
                      onChange={(e) => setCompanyNameEn(e.target.value)}
                      placeholder="예: Samsung Electronics"
                      className={inputClass('companyNameEn')}
                    />
                    <p className="mt-1.5 text-xs text-gray-400">
                      영문명이 없으면 한글 발음을 로마자로 입력
                    </p>
                    <FieldError field="companyNameEn" />
                  </div>

                  <div className="mb-5">
                    <label htmlFor="business-number" className="block text-sm font-semibold text-gray-700 mb-2">
                      사업자등록번호 <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="business-number"
                      type="text"
                      value={businessNumber}
                      onChange={(e) => setBusinessNumber(e.target.value)}
                      placeholder="000-00-00000"
                      className={inputClass('businessNumber')}
                    />
                    <FieldError field="businessNumber" />
                  </div>

                  <div className="mb-5">
                    <label htmlFor="ceo-name" className="block text-sm font-semibold text-gray-700 mb-2">
                      대표자명 <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="ceo-name"
                      type="text"
                      value={ceoName}
                      onChange={(e) => setCeoName(e.target.value)}
                      placeholder="대표이사 성명"
                      className={inputClass('ceoName')}
                    />
                    <FieldError field="ceoName" />
                  </div>

                  <div className="mb-5">
                    <label htmlFor="industry" className="block text-sm font-semibold text-gray-700 mb-2">
                      업종
                    </label>
                    <input
                      id="industry"
                      type="text"
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      placeholder="예: 소프트웨어 개발업"
                      className={inputClass('industry')}
                    />
                  </div>

                  <div className="mb-5">
                    <label htmlFor="founded-date" className="block text-sm font-semibold text-gray-700 mb-2">
                      설립일
                    </label>
                    <input
                      id="founded-date"
                      type="date"
                      value={foundedDate}
                      onChange={(e) => setFoundedDate(e.target.value)}
                      className={inputClass('foundedDate')}
                    />
                  </div>

                  <div className="mb-5">
                    <label htmlFor="phone" className="block text-sm font-semibold text-gray-700 mb-2">
                      전화번호
                    </label>
                    <input
                      id="phone"
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="02-1234-5678"
                      className={inputClass('phone')}
                    />
                  </div>
                </div>
              )}

              {/* ---- Accountant Fields ---- */}
              {selectedRole === 'accountant' && (
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-1">공인회계사 정보</h2>
                  <p className="text-sm text-gray-500 mb-7">자격 및 경력 정보를 입력해주세요</p>

                  <div className="mb-5">
                    <label htmlFor="license-number" className="block text-sm font-semibold text-gray-700 mb-2">
                      공인회계사 면허번호 <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="license-number"
                      type="text"
                      value={licenseNumber}
                      onChange={(e) => setLicenseNumber(e.target.value)}
                      placeholder="예: 12345"
                      className={inputClass('licenseNumber')}
                    />
                    <p className="mt-1.5 text-xs text-gray-400">금융감독원 공인회계사 등록번호</p>
                    <FieldError field="licenseNumber" />
                  </div>

                  <div className="mb-5">
                    <label htmlFor="accountant-phone" className="block text-sm font-semibold text-gray-700 mb-2">
                      전화번호
                    </label>
                    <input
                      id="accountant-phone"
                      type="tel"
                      value={accountantPhone}
                      onChange={(e) => setAccountantPhone(e.target.value)}
                      placeholder="010-1234-5678"
                      className={inputClass('accountantPhone')}
                    />
                  </div>

                  {/* Education array */}
                  <div className="mb-5">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">학력</label>
                    <div className="space-y-2">
                      {educationList.map((edu, idx) => (
                        <div key={idx} className="flex gap-2">
                          <input
                            type="text"
                            value={edu}
                            onChange={(e) => updateEducation(idx, e.target.value)}
                            placeholder="예: 연세대학교 경영학과 졸업 (2010)"
                            className="flex-1 px-4 py-3 text-sm border-2 border-gray-200 rounded-xl transition-all focus:outline-none focus:ring-0 focus:border-blue-600"
                          />
                          <button
                            type="button"
                            onClick={() => removeEducation(idx)}
                            disabled={educationList.length <= 1}
                            className="px-4 py-3 bg-red-500 text-white rounded-xl text-sm hover:bg-red-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            aria-label="학력 삭제"
                          >
                            삭제
                          </button>
                        </div>
                      ))}
                    </div>
                    <button
                      type="button"
                      onClick={addEducation}
                      className="mt-2 w-full py-2.5 text-sm font-semibold text-blue-700 bg-blue-50 border-2 border-dashed border-blue-700 rounded-xl hover:bg-blue-700 hover:text-white transition-colors"
                    >
                      + 학력 추가
                    </button>
                  </div>

                  {/* Career array */}
                  <div className="mb-5">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">경력</label>
                    <div className="space-y-2">
                      {careerList.map((career, idx) => (
                        <div key={idx} className="flex gap-2">
                          <input
                            type="text"
                            value={career}
                            onChange={(e) => updateCareer(idx, e.target.value)}
                            placeholder="예: 삼일회계법인 (2010-2015)"
                            className="flex-1 px-4 py-3 text-sm border-2 border-gray-200 rounded-xl transition-all focus:outline-none focus:ring-0 focus:border-blue-600"
                          />
                          <button
                            type="button"
                            onClick={() => removeCareer(idx)}
                            disabled={careerList.length <= 1}
                            className="px-4 py-3 bg-red-500 text-white rounded-xl text-sm hover:bg-red-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            aria-label="경력 삭제"
                          >
                            삭제
                          </button>
                        </div>
                      ))}
                    </div>
                    <button
                      type="button"
                      onClick={addCareer}
                      className="mt-2 w-full py-2.5 text-sm font-semibold text-blue-700 bg-blue-50 border-2 border-dashed border-blue-700 rounded-xl hover:bg-blue-700 hover:text-white transition-colors"
                    >
                      + 경력 추가
                    </button>
                  </div>

                  {/* Specialization */}
                  <div className="mb-5">
                    <label htmlFor="specialization" className="block text-sm font-semibold text-gray-700 mb-2">
                      전문 분야
                    </label>
                    <textarea
                      id="specialization"
                      value={specialization}
                      onChange={(e) => setSpecialization(e.target.value)}
                      placeholder="예: DCF평가, IPO 준비, M&A 자문"
                      rows={3}
                      className="w-full px-4 py-3 text-sm border-2 border-gray-200 rounded-xl transition-all focus:outline-none focus:ring-0 focus:border-blue-600 resize-vertical"
                    />
                    <p className="mt-1.5 text-xs text-gray-400">쉼표(,)로 구분하여 입력</p>
                  </div>
                </div>
              )}

              {/* ---- Admin Fields ---- */}
              {selectedRole === 'admin' && (
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-1">관리자 인증</h2>
                  <p className="text-sm text-gray-500 mb-7">관리자 인증 코드를 입력해주세요</p>

                  <div className="mb-5">
                    <label htmlFor="admin-code" className="block text-sm font-semibold text-gray-700 mb-2">
                      관리자 인증 코드 <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="admin-code"
                      type="password"
                      value={adminCode}
                      onChange={(e) => setAdminCode(e.target.value)}
                      placeholder="관리자 인증 코드"
                      className={inputClass('adminCode')}
                    />
                    <p className="mt-1.5 text-xs text-gray-400">관리자로부터 받은 인증 코드를 입력하세요</p>
                    <FieldError field="adminCode" />
                  </div>
                </div>
              )}

              {/* ---- Investor Fields ---- */}
              {selectedRole === 'investor' && (
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-1">투자자 정보</h2>
                  <p className="text-sm text-gray-500 mb-7">
                    추가 정보 없이 바로 가입할 수 있습니다.
                  </p>
                  <div className="p-4 bg-blue-50 rounded-xl text-sm text-blue-700">
                    가입 완료 후 마이페이지에서 추가 정보를 입력할 수 있습니다.
                  </div>
                </div>
              )}

              {/* Buttons */}
              <div className="flex gap-3 mt-8">
                <button
                  type="button"
                  onClick={goPrev}
                  className="flex-1 py-3.5 text-sm font-semibold text-gray-700 bg-gray-100 rounded-xl transition-all hover:bg-gray-200"
                >
                  이전
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  aria-busy={isLoading}
                  className="flex-1 py-3.5 text-sm font-semibold text-white bg-blue-700 rounded-xl transition-all hover:bg-blue-800 hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isLoading ? '가입 처리 중...' : '회원가입 완료'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
