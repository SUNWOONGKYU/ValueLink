# S2BA3 Verification

## 검증 대상

- **Task ID**: S2BA3
- **Task Name**: 문서 및 보고서 API
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **TypeScript 빌드 성공** (`npm run type-check`)
- [ ] **Next.js 빌드 성공** (`npm run build`)
- [ ] **ESLint 경고 0개** (`npm run lint`)

---

### 2. 파일 생성 확인

- [ ] **`app/api/documents/route.ts` 존재** - 파일 업로드 API
- [ ] **`app/api/drafts/route.ts` 존재** - 초안 관리 API
- [ ] **`app/api/revisions/route.ts` 존재** - 수정 요청 API
- [ ] **`app/api/reports/route.ts` 존재** - 최종 보고서 API

---

### 3. 핵심 기능 테스트

#### 3.1 Documents API (파일 업로드)

- [ ] **POST /api/documents**
  - FormData 파싱 (`file`, `project_id`, `document_type`)
  - Supabase Storage 업로드 (`valuation-documents` 버킷)
  - 파일 경로: `projects/{project_id}/documents/{fileName}`
  - `documents` 테이블에 메타데이터 저장
  - 201 Created 응답

- [ ] **필수 필드 검증**
  - `file`, `project_id`, `document_type` 누락 시 400 에러

- [ ] **파일 정보 저장**
  - `file_name`, `file_path`, `file_size` 저장 확인

#### 3.2 Drafts API (초안 관리)

- [ ] **POST /api/drafts**
  - 초안 생성
  - 필수 필드: `project_id`, `draft_content`
  - `draft_version` 기본값: 1
  - `status: 'pending'` 자동 설정
  - 201 Created 응답

- [ ] **GET /api/drafts**
  - 프로젝트별 초안 조회
  - Query Parameter: `project_id`
  - 버전 내림차순 정렬 (`draft_version DESC`)

#### 3.3 Revisions API (수정 요청)

- [ ] **POST /api/revisions**
  - 수정 요청 생성
  - 필수 필드: `draft_id`, `revision_request`
  - `status: 'pending'` 자동 설정
  - 201 Created 응답

#### 3.4 Reports API (최종 보고서)

- [ ] **POST /api/reports**
  - 최종 보고서 생성
  - 필수 필드: `project_id`, `report_content`
  - HTML 저장 (`projects/{project_id}/reports/final_report.html`)
  - `status: 'final'` 자동 설정
  - 201 Created 응답

- [ ] **GET /api/reports**
  - 보고서 다운로드 URL 생성
  - Query Parameter: `project_id`
  - Signed URL 생성 (1시간 유효)
  - `createSignedUrl()` 메서드 사용

---

### 4. 통합 테스트

#### 4.1 선행 Task 호환

- [ ] **S1BI1 (Supabase Storage) 의존성 충족**
  - `valuation-documents` 버킷 존재
  - Storage 접근 가능

- [ ] **S1D1 (Database) 의존성 충족**
  - `documents` 테이블 존재
  - `drafts` 테이블 존재
  - `revisions` 테이블 존재
  - `reports` 테이블 존재

#### 4.2 데이터 흐름 검증

- [ ] **파일 업로드 → 메타데이터 저장**
  - Storage 업로드 성공 시 documents 테이블에 저장
  - `file_path` 정확히 저장됨

- [ ] **초안 → 수정 요청 → 보고서 흐름**
  - 초안 생성 (`drafts`)
  - 수정 요청 생성 (`revisions`)
  - 최종 보고서 생성 (`reports`)

---

### 5. Blocker 확인

- [ ] **Supabase Storage 설정** 완료
  - `valuation-documents` 버킷 생성
  - 버킷 정책 설정 (public/private)

- [ ] **테이블 접근** 가능
  - documents, drafts, revisions, reports 테이블

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **모든 파일 생성 완료** ✅ (4개 파일)
3. **파일 업로드 API 동작** ✅
4. **초안 관리 API 동작** ✅
5. **보고서 다운로드 URL 생성** ✅

### 권장 (Nice to Pass)

1. **PDF 생성 라이브러리 연동** ✨ (puppeteer, jspdf)
2. **파일 타입 검증** ✨ (MIME type 체크)
3. **파일 크기 제한** ✨ (10MB 등)

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **Supabase Storage**
   - 버킷 이름: `valuation-documents`
   - 파일 경로: `projects/{project_id}/documents/{fileName}`
   - Signed URL 유효 시간: 3600초 (1시간)

2. **FormData 파싱**
   - `file` 타입: File
   - `project_id`, `document_type` 타입: string

3. **에러 처리**
   - 필수 필드 누락 시 400 에러
   - Storage 업로드 실패 시 500 에러
   - 보고서 없음 시 404 에러

4. **PDF 생성**
   - 현재는 HTML 저장만 구현
   - 향후 PDF 라이브러리 연동 필요

---

## 참조

- Task Instruction: `task-instructions/S2BA3_instruction.md`
- Supabase Storage: https://supabase.com/docs/guides/storage

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
