# ValueLink Frontend 프로토타입

**작성일**: 2026-02-05
**버전**: 1.0
**상태**: 85% 완성 (목업 단계)

---

## 개요

본 폴더는 ValueLink 플랫폼의 **기존 72개 HTML 페이지**를 보관합니다.

### 현재 상태

```
✅ 72개 HTML 페이지 완성
✅ Vanilla JavaScript + Tailwind CSS
✅ Supabase 일부 연동
✅ 14단계 워크플로우 구현
✅ 5개 평가 방법 화면 구성
```

### 재구축 계획

```
기존 HTML → 디자인 참조용 목업
         ↓
Next.js 14 + React + TypeScript로 재구축
         ↓
Supabase 완전 연동
```

---

## 폴더 구조

```
Frontend/
├── app/                        # 기존 HTML 페이지
│   ├── auth/                  # 인증 (4개)
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── forgot-password.html
│   │   └── reset-password.html
│   │
│   ├── projects/              # 프로젝트 관리 (4개)
│   │   ├── index.html
│   │   ├── create.html
│   │   ├── detail.html
│   │   └── edit.html
│   │
│   ├── workflow/              # 14단계 워크플로우 (14개)
│   │   ├── step-01-request.html
│   │   ├── step-02-quote.html
│   │   ├── step-03-review.html
│   │   ├── step-04-negotiation.html
│   │   ├── step-05-contract.html
│   │   ├── step-06-payment.html
│   │   ├── step-07-document-upload.html
│   │   ├── step-08-data-extraction.html
│   │   ├── step-09-draft-generation.html
│   │   ├── step-10-approval-points.html
│   │   ├── step-11-revision.html
│   │   ├── step-12-final-report.html
│   │   ├── step-13-delivery.html
│   │   └── step-14-feedback.html
│   │
│   ├── valuation/             # 평가 (15개)
│   │   ├── dcf/
│   │   │   ├── guide.html
│   │   │   ├── submit.html
│   │   │   └── result.html
│   │   ├── relative/
│   │   │   ├── guide.html
│   │   │   ├── submit.html
│   │   │   └── result.html
│   │   ├── asset/
│   │   │   ├── guide.html
│   │   │   ├── submit.html
│   │   │   └── result.html
│   │   ├── intrinsic/
│   │   │   ├── guide.html
│   │   │   ├── submit.html
│   │   │   └── result.html
│   │   └── tax/
│   │       ├── guide.html
│   │       ├── submit.html
│   │       └── result.html
│   │
│   ├── dashboard/             # 대시보드 (4개)
│   │   ├── customer.html
│   │   ├── accountant.html
│   │   ├── admin.html
│   │   └── investor.html
│   │
│   ├── admin/                 # 관리자 패널 (6개)
│   │   ├── projects.html
│   │   ├── users.html
│   │   ├── accountants.html
│   │   ├── payments.html
│   │   ├── analytics.html
│   │   └── settings.html
│   │
│   ├── service/               # 서비스 페이지 (6개)
│   │   ├── index.html
│   │   ├── pricing.html
│   │   ├── faq.html
│   │   ├── contact.html
│   │   ├── blog.html
│   │   └── blog-post.html
│   │
│   ├── investment-tracker/    # 투자 추적 (4개)
│   │   ├── index.html
│   │   ├── add.html
│   │   ├── detail.html
│   │   └── analytics.html
│   │
│   ├── profile/               # 프로필 (3개)
│   │   ├── index.html
│   │   ├── edit.html
│   │   └── settings.html
│   │
│   └── other/                 # 기타 (12개)
│       ├── index.html         # 메인
│       ├── about.html
│       ├── features.html
│       ├── terms.html
│       ├── privacy.html
│       ├── refund.html
│       ├── 404.html
│       ├── 500.html
│       ├── maintenance.html
│       ├── notifications.html
│       ├── help.html
│       └── onboarding.html
│
├── assets/                    # 정적 자산
│   ├── css/
│   │   └── styles.css         # 커스텀 스타일
│   ├── js/
│   │   ├── main.js           # 공통 JavaScript
│   │   ├── auth.js           # 인증 로직
│   │   ├── supabase.js       # Supabase 클라이언트
│   │   └── charts.js         # Chart.js 래퍼
│   └── images/
│       └── logo.png
│
└── README.md                  # 이 파일
```

---

## 페이지 인벤토리 (72개)

### 1. 인증 (4개)

| # | 파일명 | 기능 | Supabase 연동 | 재구축 우선순위 |
|---|--------|------|--------------|---------------|
| 1 | auth/login.html | 로그인 | ✅ | P0 |
| 2 | auth/signup.html | 회원가입 | ✅ | P0 |
| 3 | auth/forgot-password.html | 비밀번호 찾기 | ✅ | P1 |
| 4 | auth/reset-password.html | 비밀번호 재설정 | ✅ | P1 |

### 2. 프로젝트 관리 (4개)

| # | 파일명 | 기능 | Supabase 연동 | 재구축 우선순위 |
|---|--------|------|--------------|---------------|
| 5 | projects/index.html | 프로젝트 목록 | ✅ | P0 |
| 6 | projects/create.html | 프로젝트 생성 | ✅ | P0 |
| 7 | projects/detail.html | 프로젝트 상세 | ✅ | P0 |
| 8 | projects/edit.html | 프로젝트 수정 | ✅ | P1 |

### 3. 14단계 워크플로우 (14개)

| # | 파일명 | 단계 | Supabase 연동 | 재구축 우선순위 |
|---|--------|------|--------------|---------------|
| 9 | workflow/step-01-request.html | 평가 요청 | ✅ | P0 |
| 10 | workflow/step-02-quote.html | 견적 제공 | ✅ | P0 |
| 11 | workflow/step-03-review.html | 견적 검토 | ✅ | P0 |
| 12 | workflow/step-04-negotiation.html | 협상 | ✅ | P1 |
| 13 | workflow/step-05-contract.html | 계약 | ✅ | P0 |
| 14 | workflow/step-06-payment.html | 결제 | ⏳ Stripe | P0 |
| 15 | workflow/step-07-document-upload.html | 서류 업로드 | ✅ | P0 |
| 16 | workflow/step-08-data-extraction.html | 데이터 추출 | ✅ AI | P0 |
| 17 | workflow/step-09-draft-generation.html | 초안 생성 | ✅ AI | P0 |
| 18 | workflow/step-10-approval-points.html | 승인 포인트 | ✅ | P0 |
| 19 | workflow/step-11-revision.html | 수정 | ✅ | P0 |
| 20 | workflow/step-12-final-report.html | 최종 보고서 | ✅ | P0 |
| 21 | workflow/step-13-delivery.html | 납품 | ✅ | P0 |
| 22 | workflow/step-14-feedback.html | 피드백 | ✅ | P1 |

### 4. 평가 (15개)

#### DCF (3개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 23 | valuation/dcf/guide.html | DCF 가이드 | P1 |
| 24 | valuation/dcf/submit.html | DCF 정보 입력 | P0 |
| 25 | valuation/dcf/result.html | DCF 결과 | P0 |

#### Relative (3개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 26 | valuation/relative/guide.html | 상대가치 가이드 | P1 |
| 27 | valuation/relative/submit.html | 상대가치 정보 입력 | P0 |
| 28 | valuation/relative/result.html | 상대가치 결과 | P0 |

#### Asset (3개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 29 | valuation/asset/guide.html | 자산가치 가이드 | P1 |
| 30 | valuation/asset/submit.html | 자산가치 정보 입력 | P0 |
| 31 | valuation/asset/result.html | 자산가치 결과 | P0 |

#### Intrinsic (3개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 32 | valuation/intrinsic/guide.html | 본질가치 가이드 | P1 |
| 33 | valuation/intrinsic/submit.html | 본질가치 정보 입력 | P0 |
| 34 | valuation/intrinsic/result.html | 본질가치 결과 | P0 |

#### Tax (3개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 35 | valuation/tax/guide.html | 상증법 가이드 | P1 |
| 36 | valuation/tax/submit.html | 상증법 정보 입력 | P0 |
| 37 | valuation/tax/result.html | 상증법 결과 | P0 |

### 5. 대시보드 (4개)

| # | 파일명 | 역할 | Supabase 연동 | 재구축 우선순위 |
|---|--------|------|--------------|---------------|
| 38 | dashboard/customer.html | 고객 | ✅ | P0 |
| 39 | dashboard/accountant.html | 회계사 | ✅ | P0 |
| 40 | dashboard/admin.html | 관리자 | ✅ | P0 |
| 41 | dashboard/investor.html | 투자자 | ⏳ | P3 |

### 6. 관리자 패널 (6개)

| # | 파일명 | 탭 | 재구축 우선순위 |
|---|--------|-----|---------------|
| 42 | admin/projects.html | 프로젝트 관리 | P1 |
| 43 | admin/users.html | 사용자 관리 | P1 |
| 44 | admin/accountants.html | 회계사 관리 | P1 |
| 45 | admin/payments.html | 결제 관리 | P1 |
| 46 | admin/analytics.html | 통계 분석 | P1 |
| 47 | admin/settings.html | 시스템 설정 | P1 |

### 7. 서비스 페이지 (6개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 48 | service/index.html | 서비스 소개 | P1 |
| 49 | service/pricing.html | 가격 안내 | P0 |
| 50 | service/faq.html | FAQ | P2 |
| 51 | service/contact.html | 문의하기 | P2 |
| 52 | service/blog.html | 블로그 목록 | P3 |
| 53 | service/blog-post.html | 블로그 상세 | P3 |

### 8. 투자 추적 (4개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 54 | investment-tracker/index.html | 투자 추적 메인 | P2 |
| 55 | investment-tracker/add.html | 투자 정보 등록 | P2 |
| 56 | investment-tracker/detail.html | 투자 상세 | P2 |
| 57 | investment-tracker/analytics.html | 투자 분석 | P2 |

### 9. 프로필 (3개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 58 | profile/index.html | 프로필 조회 | P1 |
| 59 | profile/edit.html | 프로필 수정 | P1 |
| 60 | profile/settings.html | 계정 설정 | P1 |

### 10. 기타 (12개)

| # | 파일명 | 기능 | 재구축 우선순위 |
|---|--------|------|---------------|
| 61 | other/index.html | 메인 페이지 | P0 |
| 62 | other/about.html | 회사 소개 | P1 |
| 63 | other/features.html | 주요 기능 | P1 |
| 64 | other/terms.html | 이용약관 | P2 |
| 65 | other/privacy.html | 개인정보처리방침 | P2 |
| 66 | other/refund.html | 환불 정책 | P2 |
| 67 | other/404.html | 페이지 없음 | P2 |
| 68 | other/500.html | 서버 오류 | P2 |
| 69 | other/maintenance.html | 점검 중 | P2 |
| 70 | other/notifications.html | 알림 목록 | P2 |
| 71 | other/help.html | 도움말 센터 | P2 |
| 72 | other/onboarding.html | 온보딩 투어 | P2 |

---

## 기술 스택 (현재)

### Frontend

| 기술 | 버전 | 용도 |
|------|------|------|
| **HTML5** | - | 마크업 |
| **Vanilla JavaScript** | ES6+ | 로직 |
| **Tailwind CSS** | 3.x | 스타일링 |
| **Chart.js** | 4.x | 차트 |
| **Supabase JS** | 2.38+ | Backend 연동 |

### Supabase 연동

```javascript
// assets/js/supabase.js
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://xxx.supabase.co';
const supabaseAnonKey = 'eyJhbG...';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

**연동된 기능**:
- ✅ 인증 (로그인, 회원가입, 비밀번호 재설정)
- ✅ 프로젝트 CRUD
- ✅ 파일 업로드 (Supabase Storage)
- ✅ 실시간 구독 (일부)

**연동 필요**:
- ⏳ Stripe (결제)
- ⏳ Resend (이메일)
- ⏳ AI APIs (Claude, Gemini, GPT-4)

---

## 재구축 전략

### Phase 1: S2 - 핵심 기능 (28페이지)

**우선순위 P0**:
1. 인증 (4개)
2. 프로젝트 관리 (4개)
3. 14단계 워크플로우 (14개)
4. 대시보드 (3개)
5. 메인/가격 (2개)

### Phase 2: S3 - 평가 기능 (15페이지)

**우선순위 P0 + P1**:
6. 평가 제출 (5개)
7. 평가 결과 (5개)
8. 평가 가이드 (5개)

### Phase 3: S4 - 플랫폼 기능 (21페이지)

**우선순위 P1 + P2**:
9. 관리자 패널 (6개)
10. 프로필 (3개)
11. 서비스 페이지 (4개)
12. 기타 (8개)

### Phase 4: S4-S5 - 확장 기능 (8페이지)

**우선순위 P2 + P3**:
13. 투자 추적 (4개)
14. 투자자 대시보드 (1개)
15. 블로그 (2개)
16. 온보딩 (1개)

---

## 주요 컴포넌트 추출

### 1. 공통 레이아웃

```html
<!-- Header -->
<header class="bg-white border-b border-gray-200">
  <nav class="container mx-auto px-4">
    <div class="flex items-center justify-between h-16">
      <div class="flex items-center">
        <a href="/" class="text-xl font-bold text-primary-600">ValueLink</a>
      </div>
      <div class="flex items-center space-x-4">
        <a href="/dashboard" class="text-gray-700 hover:text-primary-600">대시보드</a>
        <a href="/projects" class="text-gray-700 hover:text-primary-600">프로젝트</a>
        <button id="logout" class="btn-secondary">로그아웃</button>
      </div>
    </div>
  </nav>
</header>

<!-- Sidebar (Dashboard) -->
<aside class="w-64 bg-gray-50 border-r border-gray-200 h-screen">
  <nav class="p-4">
    <a href="/dashboard" class="block p-2 rounded hover:bg-gray-100">대시보드</a>
    <a href="/projects" class="block p-2 rounded hover:bg-gray-100">프로젝트</a>
    <a href="/profile" class="block p-2 rounded hover:bg-gray-100">프로필</a>
  </nav>
</aside>

<!-- Footer -->
<footer class="bg-gray-900 text-gray-300 py-12">
  <div class="container mx-auto px-4">
    <div class="grid grid-cols-4 gap-8">
      <div>
        <h3 class="font-bold text-white mb-4">ValueLink</h3>
        <p class="text-sm">AI 기반 기업가치평가 플랫폼</p>
      </div>
      <div>
        <h4 class="font-semibold text-white mb-4">서비스</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="/service">서비스 소개</a></li>
          <li><a href="/pricing">가격 안내</a></li>
        </ul>
      </div>
      <div>
        <h4 class="font-semibold text-white mb-4">고객지원</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="/faq">FAQ</a></li>
          <li><a href="/contact">문의하기</a></li>
        </ul>
      </div>
      <div>
        <h4 class="font-semibold text-white mb-4">법적 고지</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="/terms">이용약관</a></li>
          <li><a href="/privacy">개인정보처리방침</a></li>
        </ul>
      </div>
    </div>
  </div>
</footer>
```

### 2. 버튼 스타일

```html
<!-- Primary Button -->
<button class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
  버튼 텍스트
</button>

<!-- Secondary Button -->
<button class="px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
  버튼 텍스트
</button>

<!-- Tertiary Button -->
<button class="px-4 py-2 text-primary-600 hover:text-primary-700">
  버튼 텍스트
</button>
```

### 3. 카드 스타일

```html
<div class="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
  <h3 class="text-lg font-semibold text-gray-900 mb-2">카드 제목</h3>
  <p class="text-sm text-gray-600">카드 내용</p>
</div>
```

### 4. 폼 스타일

```html
<form>
  <div class="mb-4">
    <label class="block text-sm font-medium text-gray-700 mb-1">라벨</label>
    <input
      type="text"
      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
      placeholder="입력하세요"
    />
    <p class="mt-1 text-sm text-red-600">에러 메시지</p>
  </div>
  <button type="submit" class="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
    제출
  </button>
</form>
```

### 5. Progress Bar (14 Steps)

```html
<div class="mb-8">
  <div class="flex items-center justify-between">
    <div class="flex-1">
      <div class="flex items-center">
        <div class="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center">
          1
        </div>
        <div class="flex-1 h-1 bg-primary-600 mx-2"></div>
      </div>
      <p class="text-xs text-gray-600 mt-1">평가 요청</p>
    </div>
    <div class="flex-1">
      <div class="flex items-center">
        <div class="w-8 h-8 rounded-full bg-gray-300 text-gray-600 flex items-center justify-center">
          2
        </div>
        <div class="flex-1 h-1 bg-gray-300 mx-2"></div>
      </div>
      <p class="text-xs text-gray-600 mt-1">견적 제공</p>
    </div>
    <!-- ... 14 steps ... -->
  </div>
</div>
```

---

## Supabase 연동 예시

### 1. 로그인

```javascript
// assets/js/auth.js
async function login(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    console.error('Login error:', error.message);
    return;
  }

  // 대시보드로 이동
  window.location.href = '/dashboard/customer.html';
}
```

### 2. 프로젝트 생성

```javascript
// assets/js/main.js
async function createProject(projectData) {
  const { data, error } = await supabase
    .from('projects')
    .insert([projectData])
    .select();

  if (error) {
    console.error('Create project error:', error.message);
    return;
  }

  console.log('Project created:', data[0]);
  return data[0];
}
```

### 3. 파일 업로드

```javascript
// assets/js/main.js
async function uploadFile(projectId, file) {
  const fileName = `${projectId}/${Date.now()}_${file.name}`;

  const { data, error } = await supabase.storage
    .from('documents')
    .upload(fileName, file);

  if (error) {
    console.error('Upload error:', error.message);
    return;
  }

  // documents 테이블에 메타데이터 저장
  await supabase
    .from('documents')
    .insert([{
      project_id: projectId,
      file_name: file.name,
      file_path: fileName,
      file_size: file.size,
      file_type: file.type,
    }]);

  return data;
}
```

---

## 참조 파일

| 파일 | 경로 | 용도 |
|------|------|------|
| **원본 HTML** | `Valuation_Company/valuation-platform/frontend/app/` | 기존 페이지 |
| **페이지 인벤토리** | `P2_프로젝트_기획/UI_UX_Mockup/page-inventory.md` | 72페이지 목록 |
| **디자인 시스템** | `P2_프로젝트_기획/Design_System/design-tokens.md` | 스타일 가이드 |
| **기능 요구사항** | `P2_프로젝트_기획/Requirements/functional-requirements.md` | 기능 명세 |

---

## 다음 단계

```
P3 완료 후:
  → S0: SAL Grid 생성 (66 Tasks 정의)
  → S1: 개발 준비
  → S2: Next.js로 재구축 시작 (28페이지)
```

**작성자**: Claude Code
**버전**: 1.0
**작성일**: 2026-02-05
