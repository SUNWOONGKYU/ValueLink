# S2BA3: Documents & Reports API (마이그레이션)

## Task 정보

- **Task ID**: S2BA3
- **Task Name**: 문서 및 보고서 API 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (Supabase Storage 설정), S1D1 (documents 테이블)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**Valuation_Company의 Python/FastAPI 문서 관리 API를 Next.js TypeScript로 마이그레이션하고 개선**

- 기존 Python 로직을 참고하여 TypeScript로 변환
- 파일 업로드(Supabase Storage), 초안/수정/최종 보고서 관리 시스템
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, API 설계)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ 파일 업로드 검증 (파일 타입, 크기 제한)
- ✅ 악성 파일 차단 (허용된 MIME 타입만)
- ✅ 파일명 sanitization (경로 조작 공격 방지)
- ✅ Signed URL 보안 (시간 제한, 권한 확인)
- ✅ 본인 프로젝트 파일만 접근

### 2️⃣ 성능 최적화 (Performance)
- ✅ 파일 스트리밍 업로드 (대용량 파일)
- ✅ 썸네일 생성 (이미지 파일)
- ✅ CDN 활용 (Supabase Storage)
- ✅ 메타데이터만 조회 (파일 목록)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 파일 처리 에러 핸들링 강화
- ✅ JSDoc 주석으로 함수 문서화
- ✅ 테스트 가능한 구조

### 4️⃣ API 설계 개선 (API Design)
- ✅ RESTful 원칙 준수
- ✅ 일관된 응답 형식
- ✅ 파일 다운로드 URL 생성
- ✅ 버전 관리 (초안 v1, v2, ...)

---

## 작업 방식

### Step 1: 기존 Python 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/backend/
├── routers/documents.py (파일 업로드 API)
├── routers/drafts.py (초안 관리 API)
├── routers/revisions.py (수정 요청 API)
├── routers/reports.py (보고서 API)
├── services/file_storage.py (파일 저장 서비스)
└── services/pdf_generator.py (PDF 생성)
```

**분석 항목:**
1. 파일 업로드 로직 (S3 → Supabase Storage)
2. 초안 버전 관리 로직
3. 수정 요청 처리 흐름
4. 보고서 생성 및 다운로드 로직
5. 에러 처리 방식

### Step 2: Python → TypeScript 변환

**변환 가이드:**

| Python | TypeScript |
|--------|------------|
| `file = request.files.get('file')` | `const file = formData.get('file') as File` |
| `s3.upload_file(file, path)` | `await supabase.storage.from('bucket').upload(path, file)` |
| `def generate_signed_url(path):` | `const { data } = await supabase.storage.from('bucket').createSignedUrl(path, 3600)` |
| `return {"download_url": url}` | `return NextResponse.json({ download_url: url })` |

**주의사항:**
- Python의 파일 객체 → TypeScript File 객체
- S3 → Supabase Storage API 차이
- 경로 구조 일관성 유지

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```typescript
// ❌ 목업: 파일 타입 검증 없음
const file = formData.get('file') as File
await supabase.storage.from('bucket').upload(path, file)

// ✅ 개선: 파일 타입 및 크기 검증
const file = formData.get('file') as File

const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // xlsx
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // docx
  'image/jpeg',
  'image/png',
]

const MAX_SIZE = 50 * 1024 * 1024 // 50MB

if (!file) {
  return NextResponse.json({ error: 'File is required' }, { status: 400 })
}

if (!ALLOWED_TYPES.includes(file.type)) {
  return NextResponse.json(
    { error: 'Invalid file type. Allowed: PDF, XLSX, DOCX, JPG, PNG' },
    { status: 400 }
  )
}

if (file.size > MAX_SIZE) {
  return NextResponse.json(
    { error: 'File size exceeds 50MB limit' },
    { status: 400 }
  )
}
```

```typescript
// ❌ 목업: 파일명 sanitization 없음 (경로 조작 공격 가능)
const filePath = `projects/${project_id}/documents/${file.name}`

// ✅ 개선: 파일명 sanitization
function sanitizeFileName(fileName: string): string {
  // 경로 구분자 제거
  const sanitized = fileName.replace(/[\/\\]/g, '_')
  // 특수문자 제거 (알파벳, 숫자, 점, 하이픈, 언더스코어만 허용)
  return sanitized.replace(/[^a-zA-Z0-9._-]/g, '_')
}

const timestamp = Date.now()
const sanitizedName = sanitizeFileName(file.name)
const filePath = `projects/${project_id}/documents/${timestamp}-${sanitizedName}`
```

```typescript
// ❌ 목업: PDF 생성 로직 미완성
const report_file_path = `projects/${project_id}/reports/final_report.html`

// ✅ 개선: PDF 생성 (puppeteer 또는 jspdf 사용)
import puppeteer from 'puppeteer'

async function generatePDF(htmlContent: string): Promise<Buffer> {
  const browser = await puppeteer.launch()
  const page = await browser.newPage()
  await page.setContent(htmlContent)
  const pdfBuffer = await page.pdf({ format: 'A4' })
  await browser.close()
  return pdfBuffer
}

const pdfBuffer = await generatePDF(report_content)
const report_file_path = `projects/${project_id}/reports/final_report_${Date.now()}.pdf`

const { error: uploadError } = await supabase.storage
  .from('valuation-documents')
  .upload(report_file_path, pdfBuffer, {
    contentType: 'application/pdf',
  })
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- FormData 처리
- File 업로드
- Signed URL 생성

**TypeScript 타입 안전성:**
```typescript
// ✅ 파일 업로드 타입
export interface FileUploadRequest {
  project_id: string
  document_type: 'input_data' | 'financial_statement' | 'supporting_doc'
  file: File
}

export interface FileUploadResponse {
  document_id: string
  file_name: string
  file_path: string
  file_size: number
  uploaded_at: string
}

// ✅ 초안 타입
export interface Draft {
  draft_id: string
  project_id: string
  draft_content: string
  draft_version: number
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Supabase Storage 설정 완료
- `valuation-documents` 버킷 생성

**S1D1 완료 확인:**
- `documents`, `drafts`, `revisions`, `reports` 테이블 존재

---

## 생성 파일 (4개)

### 1. app/api/documents/route.ts

**목표:** 파일 업로드 API

**참고 파일:** `backend/routers/documents.py`

**개선 사항:**
- ✅ 파일 타입 검증 (PDF, XLSX, DOCX, JPG, PNG만)
- ✅ 파일 크기 제한 (50MB)
- ✅ 파일명 sanitization
- ✅ Supabase Storage 업로드

### 2. app/api/drafts/route.ts

**목표:** 초안 관리 API

**참고 파일:** `backend/routers/drafts.py`

**개선 사항:**
- ✅ 버전 관리 (자동 증가)
- ✅ 초안 조회 (최신순)
- ✅ 승인/거절 로직

### 3. app/api/revisions/route.ts

**목표:** 수정 요청 API

**참고 파일:** `backend/routers/revisions.py`

**개선 사항:**
- ✅ 초안 연결 (draft_id)
- ✅ 수정 요청 내용 저장
- ✅ 상태 관리 (pending, completed)

### 4. app/api/reports/route.ts

**목표:** 최종 보고서 API

**참고 파일:** `backend/routers/reports.py`

**개선 사항:**
- ✅ PDF 생성 (puppeteer)
- ✅ Signed URL 생성 (1시간 유효)
- ✅ 다운로드 이력 기록

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 Python 파일 읽고 로직 분석 완료
- [ ] 파일 업로드 API 구현 (타입/크기 검증)
- [ ] 초안 관리 API 구현 (버전 관리)
- [ ] 수정 요청 API 구현
- [ ] 보고서 다운로드 API 구현 (Signed URL)

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] 파일 업로드 동작 확인
- [ ] 초안 생성/조회 동작 확인
- [ ] Signed URL 생성 및 다운로드 확인

### 개선 항목 (Improvement)
- [ ] 보안: 파일 검증, sanitization, Signed URL
- [ ] 성능: 스트리밍 업로드, CDN
- [ ] 코드 품질: JSDoc, 에러 처리
- [ ] API 설계: 일관된 응답 형식

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/backend/routers/documents.py`
- `Valuation_Company/valuation-platform/backend/routers/drafts.py`
- `Valuation_Company/valuation-platform/backend/routers/revisions.py`
- `Valuation_Company/valuation-platform/backend/routers/reports.py`
- `Valuation_Company/valuation-platform/backend/services/file_storage.py`

**분석 포인트:**
1. 파일 업로드는 어떻게 구현되어 있는가?
2. 초안 버전 관리는 어떻게 되어 있는가?
3. PDF 생성 로직은 있는가? (개선 필요)
4. 보안 검증은 있는가? (개선 필요)

### 관련 Task
- **S1BI1**: Supabase Storage 설정
- **S1D1**: documents, drafts, revisions, reports 테이블

---

## 주의사항

### ⚠️ 목업의 한계

1. **보안 취약점**
   - 파일 타입 검증 부족
   - 파일명 sanitization 없음
   - 크기 제한 없음

2. **PDF 생성 미완성**
   - HTML만 저장
   - 실제 PDF 변환 로직 없음

3. **Best Practice 적용 필요**
   - Signed URL 시간 제한
   - 권한 확인 강화

### 🔒 보안

1. **파일 업로드 검증**
   - 허용된 MIME 타입만 (PDF, XLSX, DOCX, JPG, PNG)
   - 크기 제한 (50MB)
   - 파일명 sanitization

2. **Signed URL 보안**
   - 1시간 유효
   - 본인 프로젝트 파일만 다운로드

### ⚡ 성능

1. **대용량 파일 처리**
   - 스트리밍 업로드
   - 청크 단위 처리

2. **CDN 활용**
   - Supabase Storage CDN
   - 캐시 헤더 설정

---

## 예상 소요 시간

**작업 복잡도**: High
**파일 수**: 4개
**라인 수**: ~360줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
