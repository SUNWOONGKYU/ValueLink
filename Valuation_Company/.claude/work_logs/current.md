# 작업 로그

## 2026-01-26: Phase 0 - 전체 구조 재설계 (여러 평가법 동시 신청)

### 작업 상태: ✅ 완료

---

## 작업 내용

### Phase 0-1: 데이터베이스 수정 ✅
- Supabase projects 테이블에 평가법별 상태 필드 추가 (10개 필드)
  - `dcf_status`, `dcf_step`
  - `relative_status`, `relative_step`
  - `intrinsic_status`, `intrinsic_step`
  - `asset_status`, `asset_step`
  - `inheritance_tax_status`, `inheritance_tax_step`
- 제약조건 추가 (상태 값, 단계 범위)
- 인덱스 생성 (조회 성능 향상)
- Supabase CLI로 마이그레이션 실행 완료

**파일**:
- `backend/database/migrations/add_method_status_fields.sql`
- `backend/database/migrations/run_migration.py`
- `backend/database/migrations/run_migration_rest.py`
- `backend/database/migrations/verify_simple.py`

### Phase 0-2: 공통 컴포넌트 생성 ✅
**1. project-status-checker.js**
- 평가법별 상태 확인 함수
- 프로젝트 정보 조회
- 상태 업데이트 함수
- 승인된 평가법 목록 조회

**2. common-sidebar.js**
- 14단계 프로세스 사이드바 렌더링
- 프로젝트 정보 표시 (평가법 + 상태)
- 담당 공인회계사 섹션
- 단계별 접근 권한 제어

**3. method-content.json**
- 5개 평가법별 상세 정보
- 가이드 컨텐츠
- 필요 데이터, 소요 기간, 가격 범위

**파일**:
- `frontend/app/components/project-status-checker.js`
- `frontend/app/components/common-sidebar.js`
- `frontend/app/data/method-content.json`

### Phase 0-3: 홈 화면 수정 ✅
- `valuation.html`에 14단계 프로세스 사이드바 적용
- 공통 컴포넌트 import 및 초기화
- "평가 시작하기" 버튼 추가 (Hero 섹션)
- 로그인 상태별 사이드바 표시 처리

**파일**:
- `frontend/app/valuation.html`

### Phase 0-4: 평가 신청 페이지 수정 ✅
- 라디오 버튼 → 체크박스 변경 (여러 평가법 동시 선택)
- 평가법 값 변경 (DC→dcf, RV→relative, IV→intrinsic, AV→asset, TX→inheritance_tax)
- 아이콘 업데이트 (일관성 유지)
- JavaScript 수정:
  - `getMethodCode()`: 첫 번째 선택된 평가법 코드 반환
  - `createProject()`: 선택된 평가법별 상태 설정
- 프로젝트 생성 후 `approval-waiting.html`로 리다이렉트
- 체크 표시 CSS 추가

**파일**:
- `frontend/app/projects/project-create.html`

### Phase 0-5: 승인 대기 페이지 생성 ✅
- 3단계 (관리자 승인 대기) 페이지
- 프로젝트 정보 카드 (번호, 회사명, 평가 기준일, 신청 일시)
- 신청한 평가법 목록 표시
- 평가법별 승인 상태 표시:
  - 🟢 승인됨 → "평가 진행하기" 버튼
  - 🟡 대기중 → 상태만 표시
  - ⚫ 신청안함 → 목록에서 제외
- 14단계 프로세스 사이드바
- 로딩 상태, 빈 상태 처리

**파일**:
- `frontend/app/approval-waiting.html`

---

## 핵심 변경사항

### 설계 철학
```
이전: 하나의 프로젝트 = 하나의 평가법
이후: 하나의 프로젝트 = 여러 평가법 (동시 신청 가능)

홈 화면 (1~3단계): 공통 프로세스
  1단계: 서비스 안내
  2단계: 평가 신청 (여러 평가법 체크박스 선택)
  3단계: 관리자 승인 대기

평가법별 페이지 (4~14단계): 개별 프로세스
  - 승인된 평가법만 진행 가능
  - 각 평가법별 독립적 진행
  - 평가법 상태: not_requested, pending, approved, in_progress, completed
```

### DB 구조
```sql
projects 테이블:
  dcf_status TEXT DEFAULT 'not_requested'
  dcf_step INTEGER DEFAULT 1
  relative_status TEXT DEFAULT 'not_requested'
  relative_step INTEGER DEFAULT 1
  intrinsic_status TEXT DEFAULT 'not_requested'
  intrinsic_step INTEGER DEFAULT 1
  asset_status TEXT DEFAULT 'not_requested'
  asset_step INTEGER DEFAULT 1
  inheritance_tax_status TEXT DEFAULT 'not_requested'
  inheritance_tax_step INTEGER DEFAULT 1
```

### 사용자 시나리오
```
1. valuation.html → "평가 시작하기" 클릭
2. project-create.html → DCF + 상대가치 체크박스 선택 → "프로젝트 생성"
3. DB 저장:
   dcf_status = 'pending'
   relative_status = 'pending'
   intrinsic_status = 'not_requested'
   ...
4. approval-waiting.html로 리다이렉트
5. 화면 표시:
   💰 DCF: 🟡 승인 대기 중
   ⚖️ 상대가치: 🟡 승인 대기 중
6. 관리자가 DCF 승인 (Supabase에서 수동)
7. 새로고침:
   💰 DCF: 🟢 승인됨 [평가 진행하기 →]
   ⚖️ 상대가치: 🟡 승인 대기 중
8. "평가 진행하기" 클릭 → guide-dcf.html (4단계부터 진행)
```

---

## 생성/수정된 파일 (13개)

### 생성된 파일 (8개)
1. `valuation-platform/backend/database/migrations/add_method_status_fields.sql`
2. `valuation-platform/backend/database/migrations/run_migration.py`
3. `valuation-platform/backend/database/migrations/run_migration_rest.py`
4. `valuation-platform/backend/database/migrations/verify_simple.py`
5. `valuation-platform/frontend/app/components/project-status-checker.js`
6. `valuation-platform/frontend/app/components/common-sidebar.js`
7. `valuation-platform/frontend/app/data/method-content.json`
8. `valuation-platform/frontend/app/approval-waiting.html`

### 수정된 파일 (5개)
1. `valuation-platform/frontend/app/valuation.html`
2. `valuation-platform/frontend/app/projects/project-create.html`
3. `supabase/migrations/20260126000001_add_method_status_fields.sql` (복사본)
4. `Human_ClaudeCode_Bridge/Reports/Phase0_전체구조_재설계_계획서_v2.md`

---

## 다음 단계

### Phase 1: 기존 페이지 수정 (5개 가이드 페이지)
- guide-dcf.html, guide-relative.html, guide-intrinsic.html, guide-asset.html, guide-tax.html
- 공통 사이드바 컴포넌트 적용
- 평가법별 상태 체크 로직 추가
- 승인되지 않은 평가법 접근 시 안내 메시지

### Phase 2: 신규 페이지 생성 (7개)
- data-collection.html (5단계)
- evaluation-progress.html (6단계)
- accountant-review.html (7단계)
- draft-generation.html (8단계)
- revision-request.html (10단계)
- final-preparation.html (11단계)
- payment.html (13단계)
- report-download.html (14단계)

### Phase 3: 백엔드 연동
- 평가 엔진 연결 (Option 1: 단일 엔드포인트 + Enum)
- API 엔드포인트 생성
- 상태 업데이트 로직

---

## 2026-01-25: 투자 뉴스 스크래핑 시스템 구축

### 작업 상태: ✅ 완료

---

## 작업 내용

### 1. 프로젝트 설정 ✅ 완료
- 폴더 생성: `scripts/investment-news-scraper/`
- 파일 7개 생성:
  - `PROJECT_PLAN.md` (프로젝트 계획서)
  - `create_tables.sql` (테이블 생성 SQL)
  - `scrape_investment_news.py` (스크래핑 스크립트)
  - `requirements.txt` (패키지 목록)
  - `.env.example` (환경변수 예시)
  - `.env` (실제 환경변수 - Supabase 연결)
  - `README.md` (사용 가이드)
  - `.gitignore` (보안 설정)

### 2. Supabase 테이블 생성 ✅ 완료
- `investment_news_articles` 테이블 생성
- `investment_news_ranking` 테이블 생성
- 19개 사이트 초기 데이터 INSERT
- 함수 및 뷰 생성 (`update_news_ranking()`, `v_latest_ranking`)

### 3. 환경 설정 ✅ 완료
- Python 패키지 설치 완료
- .env 파일 생성 (기존 Supabase 연결 정보 사용)

### 4. 테스트 실행 ✅ 완료
- 스크립트 실행: `python scrape_investment_news.py`
- 결과: **0건 수집** (예상된 결과)
- 원인: 범용 템플릿 함수가 실제 사이트 HTML 구조와 불일치

### 5. 재미나 ICI 작업 요청서 작성 ✅ 완료
- 파일: `REQUEST_TO_JEMINA_ICI.md`
- 내용:
  - 현재 상황 설명
  - 문제점 분석
  - 수정 방법 상세 가이드
  - 테스트 방법
  - 주의사항

---

## 다음 단계

### 재미나 ICI 작업 (데이터 수집)
1. 각 사이트 HTML 구조 분석
2. 사이트별 스크래핑 함수 커스터마이징
3. 테스트 및 데이터 수집
4. Supabase 데이터 확인

### 데이터 분석 (재미나 ICI)
1. `SELECT update_news_ranking();` 실행
2. 랭킹 조회 및 결과 도출
3. 사용자에게 최종 보고

---

## 파일 위치

**프로젝트 폴더**:
```
C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\
```

**생성된 파일**:
- PROJECT_PLAN.md
- create_tables.sql
- scrape_investment_news.py
- requirements.txt
- .env
- .env.example
- README.md
- .gitignore
- REQUEST_TO_JEMINA_ICI.md
- scraping_log.txt (자동 생성)

---

## 기술 스택

- Python 3.8+
- requests, beautifulsoup4, lxml
- supabase-py
- python-dotenv
- Supabase (PostgreSQL)

---

## 대상 사이트 (19개)

8-26번 사이트 (더브이씨, 벤처스퀘어, 플래텀 등)

---

## 비고

- 스크래핑 스크립트는 범용 템플릿으로 작성됨
- 실제 데이터 수집을 위해서는 사이트별 커스터마이징 필수
- 재미나 ICI가 HTML 구조 분석 및 수정 담당

---

## 2026-01-26: 평가법별 14단계 프로세스 구현

### 작업 상태: 🟡 진행 중 (Phase 1 시작 예정)

---

## 완료된 작업

### 1. 담당 공인회계사 섹션 추가 ✅
- 5개 평가법 가이드 페이지 사이드바에 "담당 공인회계사" 섹션 추가
- 파일 생성:
  - `accountant-profile.html` (회계사 프로필 페이지)
  - `create_accountants_table.sql` (Supabase 테이블)
  - `update_accountants_table.sql` (데이터 업데이트)
- 회계사 정보: 선웅규 (CPA 2353), 연세대 경영학과, 4개 회계법인 경력
- 색상: 파란색 계열로 통일
- 커밋: `feacca6`

### 2. 프로세스 용어 연구 및 확정 ✅
- general-purpose 에이전트로 고객 관점 용어 연구
- 금융/컨설팅/법무 서비스 벤치마크
- 14단계 프로세스 최종 확정
- 용어 원칙:
  - 고객이 하는 단계: 능동형 ("신청", "제출", "확인")
  - 대기/진행 단계: 진행형 ("~중")
  - "회사"/"기업" 생략으로 간결화

### 3. 평가법 정보 정리 ✅
- 본질가치평가법 영문명: Intrinsic Value Method
- 프로젝트 코드 변경: `IP` → `IV`
- 파일명 변경 예정:
  - `ipo-portal.html` → `intrinsic-portal.html`
  - `ipo-valuation.html` → `intrinsic-valuation.html`

### 4. 프로젝트 ID 부여 방식 확인 ✅
- 형식: `[회사영문명5글자]-[YYMMDDHHmm]-[평가법코드]`
- 예시: `APPLE-2601261530-DC`

### 5. 평가 엔진 확인 ✅
- 위치: `backend/app/services/valuation_engine/`
- 5개 엔진 모두 존재 확인 (dcf, relative, intrinsic, asset, tax)

### 6. 업무인수인계서 작성 ✅
- 파일: `Human_ClaudeCode_Bridge/Reports/평가법별_14단계_프로세스_구현_인수인계서.md`
- 내용:
  - 완료된 작업 정리
  - 확정된 14단계 프로세스
  - 평가법별 매핑 정보
  - 앞으로 해야 할 작업 (Phase 1-5)
  - 구현 우선순위
  - 주요 결정사항
  - 참고 자료

---

## 확정된 14단계 프로세스

| # | 단계명 | 담당 | 기존 페이지 | 작업 |
|---|--------|------|------------|------|
| 1 | 서비스 안내 | 고객 | mockup-valuation.html | URL 수정 |
| 2 | 평가 신청 | 고객 | project-create.html | 평가법 파라미터 |
| 3 | 관리자 승인 대기 | 관리자 | ❌ | **신규 생성** |
| 4 | 평가 기초자료 제출 | 고객 | {method}-portal.html | 링크 연결 |
| 5 | 데이터 수집 중 | AI | ❌ | **신규 생성** |
| 6 | 평가 진행 중 | 엔진 | ❌ | **신규 생성** |
| 7 | 공인회계사 검토 중 | 회계사 | ❌ | **신규 생성** |
| 8 | 평가보고서 초안 생성 | AI | ❌ | **신규 생성** |
| 9 | 평가보고서 초안 확인 | 고객 | {method}-valuation.html | 초안 모드 |
| 10 | 수정 요청 | 고객 | project-detail.html | 수정 탭 |
| 11 | 평가보고서 최종안 작성 | 회계사 | ❌ | **신규 생성** |
| 12 | 평가보고서 최종안 확인 | 고객 | {method}-valuation.html | 최종안 모드 |
| 13 | 결제하기 | 고객 | ❌ | **신규 생성** |
| 14 | 평가보고서 수령 | 고객 | ❌ | **신규 생성** |

---

## 다음 작업 (Phase 1 - 즉시 시작)

### 1. 본질가치평가법 파일명 변경
- [ ] `ipo-portal.html` → `intrinsic-portal.html`
- [ ] `ipo-valuation.html` → `intrinsic-valuation.html`
- [ ] `project-create.html`에서 `IP` → `IV` 변경
- [ ] DB methodCodeMap 수정

### 2. 가이드 페이지에 평가법 표시 추가
- [ ] `guide-dcf.html`
- [ ] `guide-relative.html`
- [ ] `guide-intrinsic.html`
- [ ] `guide-asset.html`
- [ ] `guide-tax.html`

### 3. 사이드바 동적 링크 JavaScript 작성
- [ ] 공통 JavaScript 함수 (`sidebar-links.js`)
- [ ] 5개 가이드 페이지에 스크립트 포함

---

## 참고 문서

- **인수인계서**: `Human_ClaudeCode_Bridge/Reports/평가법별_14단계_프로세스_구현_인수인계서.md`
- **시스템 구성도**: `기업가치평가_시스템_구성도.svg`
- **회계사 프로필**: `accountant-profile.html`

---

## 2026-01-26: Phase 1 - 가이드 페이지 수정 (공통 사이드바 적용)

### 작업 상태: ✅ 완료

---

## 작업 내용

5개 평가법 가이드 페이지를 모두 공통 사이드바 컴포넌트를 사용하도록 수정했습니다.

### 수정된 페이지 (5개)
1. ✅ `guide-dcf.html` (수동 수정)
2. ✅ `guide-relative.html` (Task 에이전트)
3. ✅ `guide-intrinsic.html` (Task 에이전트)
4. ✅ `guide-asset.html` (Task 에이전트)
5. ✅ `guide-tax.html` (Task 에이전트)

### 각 파일의 공통 변경사항

#### 1. 하드코딩된 사이드바 HTML 제거
```html
<!-- Before: 150+ 줄의 하드코딩된 HTML -->
<aside class="sidebar">
  <div class="sidebar-title">평가 프로세스</div>
  <div class="process-steps">
    <div class="process-step active">
      <!-- 8단계 프로세스 -->
    </div>
  </div>
  <div class="accountant-section">
    <!-- 담당 공인회계사 섹션 -->
  </div>
</aside>

<!-- After: 단일 컨테이너 -->
<aside id="sidebar-container" class="sidebar-wrapper"></aside>
```

#### 2. 사이드바 관련 CSS 제거
**제거된 클래스**:
- `.sidebar`, `.sidebar-title`
- `.process-steps`, `.process-step`, `.step-number`, `.step-label`
- `.btn-mypage`
- `.accountant-section`, `.accountant-header`, `.accountant-profile`, `.accountant-info`

**유지된 클래스**:
```css
.sidebar-wrapper {
    width: 320px;
    flex-shrink: 0;
}

@media (max-width: 1024px) {
    .sidebar-wrapper {
        width: 100%;
    }
}
```

#### 3. 모듈 스크립트 추가
각 가이드 페이지에 평가법별 상태 확인 로직 추가:

```javascript
<script type="module">
    import { injectSidebar } from '../../components/common-sidebar.js';
    import { checkMethodStatus, getCurrentProject, STATUS } from '../../components/project-status-checker.js';

    async function initPage() {
        // 1. URL 파라미터에서 projectId 가져오기
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get('projectId');

        // 2. 로그인 체크
        const supabaseClient = /* ... */;
        const { data: { session } } = await supabaseClient.auth.getSession();
        if (!session) {
            showNotLoggedIn(); // 🔒 로그인 필요
            return;
        }

        // 3. 평가법 상태 확인 (평가법별로 다름)
        const methodStatus = await checkMethodStatus(projectId, 'dcf'); // 또는 'relative', 'intrinsic', 'asset', 'inheritance_tax'

        // 4. 상태별 처리
        if (methodStatus.status === STATUS.NOT_REQUESTED) {
            showNotRequested(); // ⚫ 신청하지 않음
            return;
        } else if (methodStatus.status === STATUS.PENDING) {
            showPendingApproval(); // 🟡 승인 대기 중
            return;
        }

        // 5. 승인된 경우 → 14단계 사이드바 표시
        injectSidebar(
            'sidebar-container',  // 컨테이너 ID
            1,                    // 현재 단계 (서비스 안내)
            methodStatus.status,  // 상태
            'dcf',               // 평가법 코드
            projectId            // 프로젝트 ID
        );
    }

    initPage();
</script>
```

### 평가법별 메서드 코드

| 파일 | 메서드 코드 | 평가법 이름 |
|------|-----------|------------|
| guide-dcf.html | `'dcf'` | 현금흐름할인법 (DCF) |
| guide-relative.html | `'relative'` | 상대가치평가법 |
| guide-intrinsic.html | `'intrinsic'` | 내재가치평가법 |
| guide-asset.html | `'asset'` | 자산가치평가법 |
| guide-tax.html | `'inheritance_tax'` | 상속세법 |

⚠️ **주의**: guide-tax.html은 DB 필드명인 `inheritance_tax` 사용 (tax 아님)

### 4가지 상태 처리

#### 상태 1: 로그인 안 함
```
🔒 로그인이 필요합니다

{평가법명} 가이드를 보려면 먼저 로그인해주세요.

[로그인 하기]
```

#### 상태 2: 신청 안 함 (not_requested)
```
⚫ {평가법명}을 신청하지 않았습니다

이 평가법을 사용하려면 먼저 프로젝트를 생성하고
{평가법명}을 선택해주세요.

[새 프로젝트 만들기]
```

#### 상태 3: 승인 대기 (pending)
```
🟡 {평가법명} 신청이 접수되었습니다

관리자 승인을 기다리고 있습니다.
승인이 완료되면 평가를 시작할 수 있습니다.

[승인 대기 페이지로 이동]
```

#### 상태 4: 승인됨 (approved+)
- 14단계 프로세스 사이드바 표시
- 현재 단계 하이라이트
- 프로젝트 정보 표시 (평가법 + 상태)
- 담당 공인회계사 섹션
- 단계별 링크 활성화

---

## 기술적 개선사항

### 1. 컴포넌트 재사용
- **Before**: 5개 파일 × 150줄 = 750줄 중복 코드
- **After**: 공통 컴포넌트 1개 + 각 파일 100줄 = 약 90% 코드 감소

### 2. 유지보수성
- 사이드바 수정 시 1개 파일만 수정 (common-sidebar.js)
- 평가법별 차이는 메서드 코드 1개로 처리

### 3. 확장성
- 새 평가법 추가 시 DB 필드 + 가이드 페이지만 추가
- 14단계 프로세스 변경 시 공통 컴포넌트만 수정

---

## 생성/수정된 파일 (5개)

### 수정된 파일
1. `valuation-platform/frontend/app/valuation/guides/guide-dcf.html`
2. `valuation-platform/frontend/app/valuation/guides/guide-relative.html`
3. `valuation-platform/frontend/app/valuation/guides/guide-intrinsic.html`
4. `valuation-platform/frontend/app/valuation/guides/guide-asset.html`
5. `valuation-platform/frontend/app/valuation/guides/guide-tax.html`

---

## 다음 단계 (Phase 2)

### 신규 페이지 생성 (7개)
4~14단계 중 기존 페이지가 없는 단계들을 신규 생성:

| # | 단계명 | 파일명 | 설명 |
|---|--------|--------|------|
| 5 | 데이터 수집 중 | data-collection.html | AI가 데이터 수집 중 |
| 6 | 평가 진행 중 | evaluation-progress.html | 엔진이 평가 진행 중 |
| 7 | 공인회계사 검토 중 | accountant-review.html | 회계사 검토 중 |
| 8 | 평가보고서 초안 생성 | draft-generation.html | AI가 초안 생성 중 |
| 10 | 수정 요청 | revision-request.html | 고객이 수정 요청 |
| 11 | 평가보고서 최종안 작성 | final-preparation.html | 회계사가 최종안 작성 |
| 13 | 결제하기 | payment.html | 결제 진행 |
| 14 | 평가보고서 수령 | report-download.html | 보고서 다운로드 |

**페이지 공통 구조**:
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <!-- ... -->
</head>
<body>
    <!-- 헤더 -->
    <div id="header-container"></div>

    <div class="container">
        <!-- 메인 컨텐츠 -->
        <main class="main-content">
            <h1>{단계명}</h1>
            <!-- 단계별 고유 컨텐츠 -->
        </main>

        <!-- 14단계 사이드바 -->
        <aside id="sidebar-container" class="sidebar-wrapper"></aside>
    </div>

    <script type="module">
        import { injectSidebar } from './components/common-sidebar.js';
        // 평가법별 상태 확인 및 사이드바 주입
    </script>
</body>
</html>
```

---

**최종 업데이트**: 2026-01-26
**Phase 1 상태**: ✅ 완료
**Phase 2 상태**: ⏳ 대기 중
**예상 완료**: 1주 (Phase 2)
