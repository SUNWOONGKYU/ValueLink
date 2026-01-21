# 역할 기반 플로우 분석 및 재설계

## 📊 현재 19개 페이지 역할별 접근 권한 매트릭스

| # | 페이지 | 고객 | 회계사 | 관리자 | 현재 문제점 |
|---|--------|------|--------|--------|------------|
| 1 | index.html | ✅ | ✅ | ✅ | 역할 구분 없음 |
| 2 | valuation-list.html | ❌ | ✅ | ✅ | 고객이 다른 프로젝트 볼 필요 없음 |
| 3 | mockup-valuation.html | ✅ | ✅ | ✅ | OK - 공개 정보 |
| 4 | mockup-deal.html | ✅ | ✅ | ✅ | OK - 공개 정보 |
| 5 | test-api.html | ❌ | ❌ | ✅ | OK - 관리자 전용 |
| 6 | dcf-portal.html | ✅ | ❌ | ❌ | 고객 자료 제출 |
| 7 | relative-portal.html | ✅ | ❌ | ❌ | 고객 자료 제출 |
| 8 | ipo-portal.html | ✅ | ❌ | ❌ | 고객 자료 제출 |
| 9 | asset-portal.html | ✅ | ❌ | ❌ | 고객 자료 제출 |
| 10 | tax-portal.html | ✅ | ❌ | ❌ | 고객 자료 제출 |
| 11 | dcf-valuation.html | ✅ | ✅ | ✅ | OK - 공개 정보 |
| 12 | relative-valuation.html | ✅ | ✅ | ✅ | OK - 공개 정보 |
| 13 | ipo-valuation.html | ✅ | ✅ | ✅ | OK - 공개 정보 |
| 14 | asset-valuation.html | ✅ | ✅ | ✅ | OK - 공개 정보 |
| 15 | tax-valuation.html | ✅ | ✅ | ✅ | OK - 공개 정보 |
| 16 | project-create.html | ✅ | ❌ | ✅ | 고객과 관리자만 |
| 17 | project-dashboard.html | ❌ | ✅ | ✅ | **문제**: 역할별 뷰 필요 |
| 18 | project-detail.html | ✅ | ✅ | ✅ | **문제**: 역할별 뷰 필요 |
| 19 | customer-portal.html | ✅ | ❌ | ❌ | OK - 고객 전용 |

---

## ❌ 발견된 문제점

### 문제 1: 역할별 진입점(Landing Page) 구분 없음
**현재**: index.html이 모든 역할의 공통 진입점
**문제**: 고객/회계사/관리자가 동일한 대시보드를 봄

### 문제 2: project-dashboard.html의 역할 모호성
**현재**: 하나의 대시보드
**문제**:
- 고객: 본인 프로젝트만 보고 싶음
- 회계사: 배정된 프로젝트만 보고 싶음
- 관리자: 전체 프로젝트를 보고 싶음

### 문제 3: project-detail.html의 기능 중복
**현재**: 하나의 상세 페이지
**문제**:
- 고객: 진행 현황만 보면 됨 (Read-only)
- 회계사: 평가 작업 + 보고서 작성 필요
- 관리자: 프로젝트 배정, 진행 모니터링

### 문제 4: valuation-list.html 접근 권한
**현재**: Supabase 전체 프로젝트 25개 표시
**문제**: 고객이 다른 기업의 프로젝트를 볼 필요 없음

### 문제 5: 회계사 작업 페이지 부재
**현재**: 회계사가 평가 작업할 페이지가 없음
**필요**:
- 평가 계산 워크시트
- 보고서 작성 에디터
- 자료 검토 페이지

### 문제 6: 관리자 관리 기능 부재
**현재**: 관리자 전용 기능이 test-api.html 밖에 없음
**필요**:
- 회계사 배정 기능
- 프로젝트 상태 관리
- 사용자 관리

---

## 🏗️ 재설계 방안

### 방안 1: 역할별 진입점 분리 ⭐ 추천

```
index.html (공개 랜딩) → 로그인
    ↓
역할 확인
    ↓
    ├─→ client-dashboard.html (고객 대시보드)
    ├─→ accountant-dashboard.html (회계사 대시보드)
    └─→ admin-dashboard.html (관리자 대시보드)
```

### 방안 2: 동적 권한 제어 (Dynamic Role-based UI)

```
index.html (통합)
    ↓
역할에 따라 UI 동적 변경
    - 고객: 특정 메뉴 숨김
    - 회계사: 평가 작업 메뉴 표시
    - 관리자: 관리 메뉴 표시
```

**추천**: 방안 1 (명확하고 보안 강화)

---

## 📋 필요한 추가 페이지 목록

### 고객용 (3개)
```
20. client-dashboard.html - 고객 대시보드 (본인 프로젝트만)
21. client-project-status.html - 진행 현황 (Read-only)
22. client-document-upload.html - 추가 자료 제출
```

### 회계사용 (5개)
```
23. accountant-dashboard.html - 회계사 대시보드 (배정된 프로젝트)
24. accountant-workbench.html - 평가 작업 워크벤치
25. accountant-calculation.html - 평가 계산 시트
26. accountant-report.html - 보고서 작성
27. accountant-review.html - 자료 검토
```

### 관리자용 (4개)
```
28. admin-dashboard.html - 관리자 대시보드 (전체 현황)
29. admin-project-manage.html - 프로젝트 관리
30. admin-assign.html - 회계사 배정
31. admin-user-manage.html - 사용자 관리
```

---

## 🔄 역할별 플로우 재설계

### 👤 고객 플로우

```
[로그인] → client-dashboard.html
    │
    ├─→ [신규 평가 신청]
    │       ↓
    │   mockup-valuation.html (평가법 선택)
    │       ↓
    │   dcf-valuation.html (설명 읽기)
    │       ↓
    │   project-create.html (프로젝트 정보 입력)
    │       ↓
    │   dcf-portal.html (자료 제출)
    │       ↓
    │   customer-portal.html (제출 현황)
    │
    ├─→ [진행 중인 프로젝트 확인]
    │       ↓
    │   client-project-status.html (진행 상황)
    │       ↓
    │   client-document-upload.html (추가 자료 제출)
    │
    └─→ [완료된 프로젝트]
            ↓
        보고서 다운로드
```

### 📊 회계사 플로우

```
[로그인] → accountant-dashboard.html
    │
    ├─→ [배정된 프로젝트 목록]
    │       ↓
    │   프로젝트 선택
    │       ↓
    │   accountant-review.html (자료 검토)
    │       ↓
    │   accountant-calculation.html (평가 계산)
    │       ↓
    │   accountant-workbench.html (작업 공간)
    │       ↓
    │   accountant-report.html (보고서 작성)
    │       ↓
    │   제출 → 관리자 검토 대기
    │
    ├─→ [진행 중인 작업]
    │       ↓
    │   accountant-workbench.html
    │
    └─→ [완료된 프로젝트]
            ↓
        실적 확인
```

### 🔧 관리자 플로우

```
[로그인] → admin-dashboard.html
    │
    ├─→ [전체 프로젝트 현황]
    │       ↓
    │   admin-project-manage.html
    │       ↓
    │   프로젝트 선택
    │       ↓
    │   project-detail.html (전체 정보)
    │
    ├─→ [신규 프로젝트 배정]
    │       ↓
    │   admin-assign.html
    │       ↓
    │   회계사 선택 → 배정
    │
    ├─→ [회계사 관리]
    │       ↓
    │   admin-user-manage.html
    │       ↓
    │   회계사 추가/수정/삭제
    │
    ├─→ [통계 및 분석]
    │       ↓
    │   valuation-list.html (전체 프로젝트)
    │       ↓
    │   mockup-deal.html (Deal 정보)
    │
    └─→ [시스템 관리]
            ↓
        test-api.html (API 테스트)
```

---

## 🎯 개선된 전체 구조 (31개 페이지)

### 공개 페이지 (2개)
```
1. index.html - 랜딩 페이지 (로그인 전)
2. login.html - 로그인 페이지 (신규 추가 필요)
```

### 공통 정보 페이지 (6개)
```
3. mockup-valuation.html - 평가법 소개
4. mockup-deal.html - Deal 정보
5-9. *-valuation.html (5개) - 평가법 설명
```

### 고객 전용 (8개)
```
10. client-dashboard.html - 고객 대시보드
11. client-project-status.html - 진행 현황
12. client-document-upload.html - 자료 제출
13. project-create.html - 신규 프로젝트
14-18. *-portal.html (5개) - 평가법별 자료 제출
19. customer-portal.html - 제출 현황 통합
```

### 회계사 전용 (5개)
```
20. accountant-dashboard.html - 회계사 대시보드
21. accountant-workbench.html - 작업 워크벤치
22. accountant-calculation.html - 평가 계산
23. accountant-report.html - 보고서 작성
24. accountant-review.html - 자료 검토
```

### 관리자 전용 (5개)
```
25. admin-dashboard.html - 관리자 대시보드
26. admin-project-manage.html - 프로젝트 관리
27. admin-assign.html - 회계사 배정
28. admin-user-manage.html - 사용자 관리
29. test-api.html - API 테스트
```

### 공통 상세 페이지 (3개)
```
30. project-dashboard.html - 프로젝트 대시보드 (역할별 뷰)
31. project-detail.html - 프로젝트 상세 (역할별 권한)
32. valuation-list.html - 프로젝트 목록 (관리자/회계사만)
```

---

## 🔐 보안 및 접근 제어

### Frontend 라우팅 가드
```javascript
// 페이지 로드 시 역할 확인
function checkUserRole() {
    const user = getCurrentUser(); // Supabase Auth
    if (!user) {
        window.location.href = '/login.html';
        return;
    }

    const role = user.role; // 'client', 'accountant', 'admin'
    const currentPage = window.location.pathname;

    // 페이지별 허용 역할
    const pagePermissions = {
        '/client-dashboard.html': ['client'],
        '/accountant-dashboard.html': ['accountant'],
        '/admin-dashboard.html': ['admin'],
        '/valuation-list.html': ['accountant', 'admin'],
        // ...
    };

    if (!pagePermissions[currentPage]?.includes(role)) {
        window.location.href = `/${role}-dashboard.html`;
    }
}
```

### Backend Row Level Security (RLS)
```sql
-- 고객은 본인 프로젝트만 조회
CREATE POLICY "client_own_projects" ON projects
    FOR SELECT USING (
        auth.uid() = client_id
    );

-- 회계사는 배정된 프로젝트만 조회
CREATE POLICY "accountant_assigned_projects" ON projects
    FOR SELECT USING (
        auth.uid() = accountant_id
    );

-- 관리자는 모든 프로젝트 조회
CREATE POLICY "admin_all_projects" ON projects
    FOR SELECT USING (
        auth.jwt() ->> 'role' = 'admin'
    );
```

---

## 📊 역할별 네비게이션 메뉴

### 고객 메뉴
```html
<nav>
    <a href="client-dashboard.html">🏠 내 대시보드</a>
    <a href="project-create.html">➕ 신규 평가</a>
    <a href="customer-portal.html">📁 자료 제출</a>
    <a href="mockup-valuation.html">📚 평가 방법</a>
    <a href="mockup-deal.html">🤝 Deal</a>
</nav>
```

### 회계사 메뉴
```html
<nav>
    <a href="accountant-dashboard.html">🏠 내 대시보드</a>
    <a href="accountant-workbench.html">💼 작업 공간</a>
    <a href="valuation-list.html">📊 프로젝트 목록</a>
    <a href="mockup-valuation.html">📚 평가 방법</a>
</nav>
```

### 관리자 메뉴
```html
<nav>
    <a href="admin-dashboard.html">🏠 관리자 대시보드</a>
    <a href="admin-project-manage.html">📊 프로젝트 관리</a>
    <a href="admin-assign.html">👥 회계사 배정</a>
    <a href="admin-user-manage.html">⚙️ 사용자 관리</a>
    <a href="valuation-list.html">📋 전체 목록</a>
    <a href="mockup-deal.html">🤝 Deal</a>
    <a href="test-api.html">🧪 API 테스트</a>
</nav>
```

---

## ⚠️ 현재 구조의 심각한 보안 문제

### 문제 1: 인증/인가 없음
**현재**: 누구나 모든 페이지 접근 가능
**위험**: 고객이 다른 고객의 재무 정보 열람 가능

### 문제 2: Supabase RLS 미설정
**현재**: Anon Key로 모든 데이터 조회 가능
**위험**: 데이터베이스 전체 노출

### 문제 3: 역할 구분 없음
**현재**: 고객/회계사/관리자 구분 없음
**위험**: 권한 관리 불가

---

## ✅ 우선순위 개선 작업

### Phase 1: 긴급 (보안) ⚠️
```
1. Supabase RLS 설정
2. 인증 시스템 구축 (login.html)
3. 역할 기반 리다이렉트
```

### Phase 2: 핵심 기능
```
4. client-dashboard.html 생성
5. accountant-dashboard.html 생성
6. admin-dashboard.html 생성
7. 역할별 네비게이션 메뉴 분리
```

### Phase 3: 세부 기능
```
8. 회계사 작업 페이지 (5개)
9. 관리자 관리 페이지 (4개)
10. 고객 추가 기능 (2개)
```

---

## 🎯 최종 권장 사항

### 즉시 수정 필요 (보안)
1. ❌ **valuation-list.html**: 고객 접근 차단 필요
2. ❌ **Supabase Anon Key**: RLS 설정 필수
3. ❌ **인증 시스템**: 로그인 페이지 추가 필수

### 구조 개선 필요
1. ⚠️ **project-dashboard.html**: 역할별 3개로 분리 (client/accountant/admin)
2. ⚠️ **project-detail.html**: 역할별 권한 제어 추가
3. ⚠️ **index.html**: 공개 랜딩으로 변경, 로그인 후 역할별 대시보드로

### 추가 개발 필요
1. ➕ 회계사 작업 페이지 5개
2. ➕ 관리자 관리 페이지 4개
3. ➕ 인증/인가 시스템

---

## 📝 결론

**현재 구조의 가장 큰 문제점:**
1. 역할 구분이 전혀 없음 → **보안 위험**
2. 인증 시스템 부재 → **누구나 접근 가능**
3. 회계사/관리자 작업 페이지 부재 → **업무 불가능**

**필수 조치:**
- Supabase RLS 즉시 설정
- 로그인 시스템 구축
- 역할별 대시보드 분리

**권장 방향:**
- 현재 19개 페이지 → 32개 페이지로 확장
- 역할별 완전 분리된 플로우 구축
- 보안 우선 개발
