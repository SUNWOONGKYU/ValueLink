/**
 * @task S2F5
 * @description Step 3 - 서류 제출 완료 페이지
 *
 * 제출된 서류 목록 및 상태 표시
 * 회계사 검토 대기 안내
 */

'use client'

import { useSearchParams } from 'next/navigation'
import { useState, useEffect, Suspense } from 'react'
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

interface SubmittedDocument {
  id: string
  file_name: string
  file_type: string
  file_size: number
  uploaded_at: string
  status: 'pending' | 'accepted' | 'rejected'
}

// ---------------------------------------------------------------------------
// 파일 크기 포맷
// ---------------------------------------------------------------------------

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// ---------------------------------------------------------------------------
// 상태 뱃지
// ---------------------------------------------------------------------------

function DocumentStatusBadge({ status }: { status: SubmittedDocument['status'] }) {
  const config = {
    pending: { label: '검토 중', className: 'bg-yellow-50 text-yellow-700' },
    accepted: { label: '승인', className: 'bg-green-50 text-green-700' },
    rejected: { label: '반려', className: 'bg-red-50 text-red-700' },
  }

  const { label, className } = config[status]

  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${className}`}
    >
      {label}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Step 3 콘텐츠
// ---------------------------------------------------------------------------

function Step3Content() {
  const searchParams = useSearchParams()
  const projectId = searchParams!.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [documents, setDocuments] = useState<SubmittedDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchData() {
      try {
        const [projRes, docsRes] = await Promise.all([
          fetch(`/api/projects/${projectId}`),
          fetch(`/api/projects/${projectId}/documents`),
        ])

        if (!projRes.ok) throw new Error('프로젝트를 불러올 수 없습니다.')

        const projData: ProjectData = await projRes.json()
        setProject(projData)

        if (docsRes.ok) {
          const docsData: SubmittedDocument[] = await docsRes.json()
          setDocuments(docsData)
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [projectId])

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={3}
        stepNumber={3}
        stepTitle="서류 제출 완료"
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
        currentStep={3}
        stepNumber={3}
        stepTitle="서류 제출 완료"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={3}
      stepTitle="서류 제출 완료"
      companyName={project.company_name_kr}
      projectStatus={project.status}
    >
      {/* 완료 안내 */}
      <div className="rounded-xl border border-green-200 bg-green-50 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-green-100">
            <svg
              className="h-5 w-5 text-green-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4.5 12.75l6 6 9-13.5"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-green-800">
              서류 제출이 완료되었습니다
            </h3>
            <p className="mt-1 text-sm text-green-700">
              담당 회계사가 제출하신 서류를 검토 중입니다.
              검토가 완료되면 다음 단계로 자동 진행됩니다.
            </p>
          </div>
        </div>
      </div>

      {/* 제출 서류 목록 */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-100 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">제출된 서류</h2>
            <span className="text-sm text-gray-500">
              총 {documents.length}건
            </span>
          </div>
        </div>

        {documents.length > 0 ? (
          <ul className="divide-y divide-gray-100">
            {documents.map((doc) => (
              <li key={doc.id} className="flex items-center justify-between px-6 py-4">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-gray-100">
                    <svg
                      className="h-5 w-5 text-gray-500"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth={1.5}
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
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {doc.file_name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(doc.file_size)} &middot;{' '}
                      {new Date(doc.uploaded_at).toLocaleDateString('ko-KR')}
                    </p>
                  </div>
                </div>
                <DocumentStatusBadge status={doc.status} />
              </li>
            ))}
          </ul>
        ) : (
          <div className="px-6 py-12 text-center">
            <p className="text-sm text-gray-500">제출된 서류가 없습니다.</p>
          </div>
        )}
      </div>

      {/* 대기 안내 */}
      <div className="mt-8 rounded-xl border border-gray-200 bg-gray-50 p-6 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 mb-3">
          <svg
            className="h-6 w-6 text-blue-600"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.5}
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-sm font-semibold text-gray-900 mb-1">
          담당 회계사가 서류를 검토 중입니다
        </h3>
        <p className="text-sm text-gray-600">
          서류 검토에는 보통 1~2 영업일이 소요됩니다.
          검토 완료 시 이메일로 알림을 보내드립니다.
        </p>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step3Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step3Content />
    </Suspense>
  )
}
