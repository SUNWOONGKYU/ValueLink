# S2F6 Verification

## 검증 대상

- **Task ID**: S2F6
- **Task Name**: 프로젝트 관리 페이지 (목록, 상세, 생성)
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)

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

- [ ] **`app/projects/list/page.tsx` 존재** - 프로젝트 목록
- [ ] **`app/projects/[id]/page.tsx` 존재** - 프로젝트 상세
- [ ] **`app/projects/create/page.tsx` 존재** - 프로젝트 생성

---

### 3. 핵심 기능 테스트

#### 3.1 프로젝트 목록 페이지

- [ ] **프로젝트 목록 표시**
  - Supabase에서 본인 프로젝트 조회
  - 프로젝트명, 평가방법, 상태, 진행단계 표시

- [ ] **검색 기능**
  - 프로젝트명으로 검색
  - 실시간 필터링

- [ ] **필터 기능**
  - 상태별 필터 (전체, 대기 중, 진행 중, 완료)
  - Supabase 쿼리에 필터 적용

- [ ] **빈 상태 표시**
  - 프로젝트가 없을 때 안내 메시지
  - "프로젝트 만들기" 버튼

- [ ] **"새 프로젝트" 버튼**
  - `/projects/create` 페이지로 이동

#### 3.2 프로젝트 상세 페이지

- [ ] **프로젝트 정보 표시**
  - 평가 방법, 상태, 현재 단계, 생성일, 수정일

- [ ] **진행 상황 표시**
  - 진행률 바 (current_step / 14)
  - 퍼센트 표시

- [ ] **"진행 상황 보기" 버튼**
  - `/valuation/evaluation-progress?project_id={id}` 이동

- [ ] **빠른 액션 링크**
  - 평가 결과 보기
  - 보고서 다운로드

- [ ] **담당 회계사 정보**
  - 배정 대기 중 표시

- [ ] **Dynamic Route 동작**
  - `[id]` 폴더 구조
  - `params.id`로 project_id 접근

#### 3.3 프로젝트 생성 페이지

- [ ] **프로젝트명 입력**
  - 필수 필드 검증
  - 빈 값 제출 방지

- [ ] **평가 방법 선택**
  - 5개 방법 라디오 버튼
  - 선택된 항목 하이라이트 (빨간 테두리)
  - 각 방법의 가격 표시

- [ ] **폼 제출**
  - Supabase에 프로젝트 생성
  - `status: 'pending'`, `current_step: 1` 자동 설정
  - 생성 후 프로젝트 상세 페이지로 리디렉션

- [ ] **로딩 상태**
  - 제출 중 버튼 비활성화
  - "생성 중..." 텍스트 표시

---

### 4. 통합 테스트

#### 4.1 선행 Task 호환

- [ ] **S1BI1 (Supabase 클라이언트) 의존성 충족**
  - `@/lib/supabase/client` import 가능

- [ ] **S1D1 (Database Schema) 의존성 충족**
  - `projects` 테이블 존재
  - RLS 정책 적용

#### 4.2 후행 Task 준비

- [ ] **S2BA2 (Projects API) 연결 준비**
  - API 없이도 UI 정상 렌더링

#### 4.3 데이터 흐름 검증

- [ ] **프로젝트 생성 → 목록 → 상세**
  - 생성 후 목록에 표시
  - 목록에서 클릭 시 상세 페이지 이동

- [ ] **RLS 보안**
  - 본인이 생성한 프로젝트만 조회
  - user_id 자동 연결

---

### 5. Blocker 확인

- [ ] **S1BI1 완료 확인** - Supabase 클라이언트
- [ ] **lucide-react 패키지 설치** 확인
- [ ] **Supabase 연결** - projects 테이블 접근 가능

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **모든 파일 생성 완료** ✅ (3개 파일)
3. **프로젝트 CRUD 정상 동작** ✅
4. **검색 및 필터 기능** ✅
5. **Dynamic Routes 동작** ✅

### 권장 (Nice to Pass)

1. **페이지네이션** ✨
2. **정렬 기능** ✨
3. **프로젝트 삭제 기능** ✨

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

**검증일**: _______________

**검증자**: _______________

---

## 주의사항

1. **RLS 보안**
   - 본인 프로젝트만 조회/생성
   - user_id 자동 연결

2. **Dynamic Routes**
   - `[id]` 폴더로 동적 라우팅
   - params.id로 project_id 접근

3. **사용자 경험**
   - 빈 상태 명확히 표시
   - 로딩 상태 표시
   - 에러 핸들링

---

## 참조

- Task Instruction: `task-instructions/S2F6_instruction.md`
- 기존 프로토타입: `Valuation_Company/valuation-platform/frontend/app/core/project-list.html`

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
