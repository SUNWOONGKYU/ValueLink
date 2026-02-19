/**
 * @task S2F5
 * @description Step 2 - 서류 제출 요청 페이지
 *
 * 평가 방법별 필요 서류 목록 표시
 * 업로드 안내 및 서류 업로드 링크 제공
 */

'use client'

import { useSearchParams } from 'next/navigation'
import { useState, useEffect, Suspense } from 'react'
import Link from 'next/link'
import ProcessStepTemplate from '@/components/process-step-template'

// ---------------------------------------------------------------------------
// 타입
// ---------------------------------------------------------------------------

interface ProjectData {
  project_id: string
  company_name_kr: string
  requested_methods: string[] | null
  status: string
  current_step: number
}

// ---------------------------------------------------------------------------
// 방법별 필요 서류
// ---------------------------------------------------------------------------

interface RequiredDocument {
  name: string
  description: string
  required: boolean
}

const METHOD_DOCUMENTS: Record<string, RequiredDocument[]> = {
  dcf: [
    { name: '최근 3개년 재무제표', description: '감사보고서 포함', required: true },
    { name: '향후 5개년 사업계획서', description: '매출 및 비용 추정', required: true },
    { name: '자본 구조 정보', description: '차입금, 자본금 내역', required: true },
    { name: '업종 분류 정보', description: '한국표준산업분류 코드', required: false },
    { name: '경쟁사 리스트', description: '주요 경쟁 기업 목록', required: false },
  ],
  relative: [
    { name: '최근 3개년 재무제표', description: '감사보고서 포함', required: true },
    { name: '유사 기업 목록', description: '상장 유사 기업 리스트', required: false },
    { name: '업종 분류 정보', description: '한국표준산업분류 코드', required: true },
    { name: '주주 구성 현황', description: '지분율 포함', required: false },
  ],
  asset: [
    { name: '최근 재무상태표', description: '가장 최근 기준일', required: true },
    { name: '자산 상세 내역서', description: '유형/무형자산 목록', required: true },
    { name: '부동산 감정평가서', description: '보유 부동산이 있는 경우', required: false },
    { name: '부채 상세 내역서', description: '차입금, 충당부채 등', required: true },
    { name: '재고자산 명세', description: '재고 평가 근거', required: false },
  ],
  intrinsic: [
    { name: '최근 3개년 재무제표', description: '감사보고서 포함', required: true },
    { name: '순자산가치 산출 근거', description: '자산/부채 시가 자료', required: true },
    { name: '업종 분류 정보', description: '자본시장법 업종 코드', required: true },
    { name: '배당 이력', description: '최근 3년 배당 내역', required: false },
  ],
  tax: [
    { name: '최근 3개년 재무제표', description: '감사보고서 포함', required: true },
    { name: '법인세 신고서', description: '최근 3개년', required: true },
    { name: '주주 명부', description: '지분율 포함', required: true },
    { name: '자산/부채 상세', description: '장부가액 기준', required: true },
    { name: '비과세/면세 소득 내역', description: '해당 시', required: false },
  ],
}

const METHOD_LABELS: Record<string, string> = {
  dcf: 'DCF (현금흐름할인법)',
  relative: '상대가치평가',
  asset: '자산가치평가',
  intrinsic: '본질가치평가',
  tax: '세법상 평가',
}

// ---------------------------------------------------------------------------
// Step 2 콘텐츠
// ---------------------------------------------------------------------------

function Step2Content() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchProject() {
      try {
        const res = await fetch(`/api/projects/${projectId}`)
        if (!res.ok) throw new Error('프로젝트를 불러올 수 없습니다.')
        const data: ProjectData = await res.json()
        setProject(data)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchProject()
  }, [projectId])

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={2}
        stepNumber={2}
        stepTitle="서류 제출 요청"
      >
        <div className="flex items-center justify-center py-16">
          <div className="flex items-center gap-3 text-gray-500">
            <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span className="text-sm">로딩 중...</span>
          </div>
        </div>
      </ProcessStepTemplate>
    )
  }

  if (error || !project) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={2}
        stepNumber={2}
        stepTitle="서류 제출 요청"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  // 선택된 방법론에 따른 필요 서류 수집
  const methods = project.requested_methods ?? []

  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={2}
      stepTitle="서류 제출 요청"
      companyName={project.company_name_kr}
      projectStatus={project.status}
    >
      {/* 안내 메시지 */}
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-blue-100">
            <svg
              className="h-5 w-5 text-blue-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-blue-800">
              서류 제출이 필요합니다
            </h3>
            <p className="mt-1 text-sm text-blue-700">
              선택하신 평가 방법에 따라 아래 서류를 준비하여 업로드해 주세요.
              <span className="font-medium"> 필수 서류</span>가 모두 제출되어야
              평가를 진행할 수 있습니다.
            </p>
          </div>
        </div>
      </div>

      {/* 방법론별 필요 서류 목록 */}
      <div className="space-y-6">
        {methods.length > 0 ? (
          methods.map((method) => {
            const docs = METHOD_DOCUMENTS[method] ?? []
            return (
              <div
                key={method}
                className="rounded-xl border border-gray-200 bg-white shadow-sm"
              >
                <div className="border-b border-gray-100 px-6 py-4">
                  <h2 className="text-base font-semibold text-gray-900">
                    {METHOD_LABELS[method] ?? method} - 필요 서류
                  </h2>
                </div>
                <div className="px-6 py-4">
                  <ul className="divide-y divide-gray-100">
                    {docs.map((doc) => (
                      <li
                        key={doc.name}
                        className="flex items-start gap-3 py-3"
                      >
                        <span
                          className={`mt-0.5 inline-flex h-5 w-5 flex-shrink-0 items-center justify-center rounded text-xs font-bold ${
                            doc.required
                              ? 'bg-red-100 text-red-700'
                              : 'bg-gray-100 text-gray-500'
                          }`}
                        >
                          {doc.required ? '필' : '선'}
                        </span>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {doc.name}
                          </p>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {doc.description}
                          </p>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )
          })
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white p-6 text-center">
            <p className="text-sm text-gray-500">
              선택된 평가 방법이 없습니다. 프로젝트 설정을 확인해 주세요.
            </p>
          </div>
        )}
      </div>

      {/* 업로드 안내 */}
      <div className="mt-8 rounded-xl border border-gray-200 bg-gray-50 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">
          서류 제출 안내
        </h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            파일 형식: PDF, Excel, Word 파일을 지원합니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            파일 크기: 개별 파일 최대 50MB, 전체 최대 200MB까지 업로드 가능합니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            보안: 업로드된 서류는 암호화되어 안전하게 보관됩니다.
          </li>
        </ul>
      </div>

      {/* 서류 업로드 버튼 */}
      <div className="mt-8 flex flex-col items-center gap-4">
        <Link
          href={`/valuation/process/documents/upload?project_id=${projectId}`}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-700 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
            />
          </svg>
          서류 업로드
        </Link>
        <p className="text-xs text-gray-500">
          업로드 페이지에서 서류를 첨부한 후 제출을 완료해 주세요.
        </p>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step2Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step2Content />
    </Suspense>
  )
}
