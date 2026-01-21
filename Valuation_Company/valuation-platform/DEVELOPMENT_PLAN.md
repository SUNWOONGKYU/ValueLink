# 개발 우선 플로우 계획 (보안 제외)

## 📋 개발 방향

**원칙**: 보안은 나중에 → 지금은 기능 구현 우선

---

## 🎯 현재 19개 페이지 역할별 용도 정리

### 공개/공통 페이지 (7개)
```
1. index.html - 통합 대시보드 (전체 시작점)
2. mockup-valuation.html - 평가법 소개
3. mockup-deal.html - Deal 정보
4. test-api.html - API 테스트
5-9. *-valuation.html (5개) - 평가법 설명
```

### 고객용 페이지 (7개)
```
10. project-create.html - 신규 프로젝트 생성
11-15. *-portal.html (5개) - 평가법별 자료 제출
    - dcf-portal.html
    - relative-portal.html
    - ipo-portal.html
    - asset-portal.html
    - tax-portal.html
16. customer-portal.html - 고객 포털 (자료 제출 통합)
```

### 회계사/관리자 공용 (5개)
```
17. valuation-list.html - 전체 프로젝트 목록 (Supabase 연동)
18. project-dashboard.html - 프로젝트 대시보드
19. project-detail.html - 프로젝트 상세
```

---

## 🔄 역할별 플로우 (보안 제외, 기능 우선)

### 👤 고객 플로우
```
index.html (통합 대시보드)
    │
    ├─→ [평가 방법 알아보기]
    │   → mockup-valuation.html
    │   → dcf-valuation.html (상세 설명)
    │
    ├─→ [신규 평가 신청]
    │   → project-create.html
    │   → dcf-portal.html (자료 제출)
    │   → customer-portal.html (제출 현황)
    │
    └─→ [투자 정보]
        → mockup-deal.html
```

### 📊 회계사 플로우 (현재 작업 페이지 없음 → 추후 추가)
```
index.html
    │
    ├─→ [프로젝트 목록]
    │   → valuation-list.html
    │   → project-detail.html
    │
    └─→ [작업 공간] ← 추후 추가 필요
        → accountant-workbench.html (미생성)
```

### 🔧 관리자 플로우
```
index.html
    │
    ├─→ [전체 프로젝트]
    │   → valuation-list.html
    │   → project-dashboard.html
    │   → project-detail.html
    │
    ├─→ [투자 정보]
    │   → mockup-deal.html
    │
    └─→ [시스템 관리]
        → test-api.html
```

---

## 🔗 현재 19개 페이지 연결 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    index.html (통합 대시보드)                 │
│              모든 역할이 여기서 시작 (역할 구분 X)            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼──────────────────────┐
        │                     │                      │
        ↓                     ↓                      ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ mockup-          │  │ valuation-       │  │ mockup-          │
│ valuation.html   │  │ list.html        │  │ deal.html        │
│ (평가법 소개)    │  │ (전체 목록)      │  │ (Deal)           │
└──────────────────┘  └──────────────────┘  └──────────────────┘
        │                     │
        │                     │
        ↓                     ↓
┌──────────────────┐  ┌──────────────────┐
│ 5개 평가법       │  │ 프로젝트 관리    │
│ 설명 페이지      │  │                  │
├──────────────────┤  ├──────────────────┤
│ • dcf-valuation  │  │ • project-detail │
│ • relative-      │  │ • project-       │
│ • ipo-           │  │   dashboard      │
│ • asset-         │  └──────────────────┘
│ • tax-           │
└──────────────────┘
        │
        ↓
┌──────────────────┐
│ project-create   │
│ (신규 프로젝트)  │
└──────────────────┘
        │
        ↓
┌──────────────────┐
│ 5개 평가법       │
│ 자료 제출        │
├──────────────────┤
│ • dcf-portal     │
│ • relative-      │
│ • ipo-           │
│ • asset-         │
│ • tax-           │
└──────────────────┘
        │
        ↓
┌──────────────────┐
│ customer-portal  │
│ (제출 현황)      │
└──────────────────┘
```

---

## 📝 헤더 네비게이션 통일 (모든 페이지)

### 공통 헤더 구조
```html
<header>
    <a href="../index.html" class="logo">
        <svg>...</svg>
        <span>ValueLink</span>
    </a>
    <nav class="main-nav">
        <a href="mockup-valuation.html">📚 평가방법</a>
        <a href="valuation-list.html">📊 프로젝트 목록</a>
        <a href="project-create.html">➕ 신규</a>
        <a href="mockup-deal.html">🤝 Deal</a>
    </nav>
</header>
```

**적용 대상**: 19개 모든 페이지

---

## 🎯 페이지별 상세 연결 계획

### 1. index.html → 7개 섹션 카드

```javascript
[평가 방법론] → mockup-valuation.html
[프로젝트 목록] → valuation-list.html
[신규 프로젝트] → project-create.html
[프로젝트 대시보드] → project-dashboard.html
[고객 포털] → customer-portal.html
[Deal] → mockup-deal.html
[API 테스트] → test-api.html
```

### 2. mockup-valuation.html → 5개 평가법 카드

```javascript
[DCF 카드] → dcf-valuation.html
[상대가치 카드] → relative-valuation.html
[본질가치 카드] → ipo-valuation.html
[자산가치 카드] → asset-valuation.html
[상증세법 카드] → tax-valuation.html
```

### 3. 각 *-valuation.html → 평가 신청

```javascript
[평가 신청하기] → *-portal.html
예: dcf-valuation.html → dcf-portal.html
```

### 4. project-create.html → 평가법 선택

```javascript
평가법 선택 시 해당 portal로 이동:
- DCF 선택 → dcf-portal.html
- 상대가치 선택 → relative-portal.html
- 본질가치 선택 → ipo-portal.html
- 자산가치 선택 → asset-portal.html
- 상증세법 선택 → tax-portal.html
```

### 5. 각 *-portal.html → 제출 완료

```javascript
[자료 제출 완료] → customer-portal.html
[목록으로] → valuation-list.html
```

### 6. customer-portal.html → 프로젝트 확인

```javascript
[프로젝트 카드 클릭] → project-detail.html
```

### 7. valuation-list.html → 프로젝트 상세

```javascript
[+ 신규 프로젝트] → project-create.html
[카드 클릭] → project-detail.html
[대시보드] → project-dashboard.html
```

### 8. project-dashboard.html → 프로젝트 상세

```javascript
[프로젝트 카드] → project-detail.html
```

### 9. project-detail.html → 다른 페이지

```javascript
[목록으로] → valuation-list.html
[대시보드] → project-dashboard.html
[자료 추가] → customer-portal.html
```

---

## 🛠️ 구현 작업 순서

### Phase 1: 공통 헤더 통일 (1시간)
```
✅ 모든 19개 페이지에 동일한 헤더 적용
✅ 로고 클릭 → index.html
✅ 4개 메뉴 (평가방법, 프로젝트 목록, 신규, Deal)
```

### Phase 2: index.html 확장 (30분)
```
✅ 7개 카드 추가
✅ 각 카드에 링크 연결
```

### Phase 3: 평가법 3단계 연결 (1시간)
```
✅ mockup-valuation → 5개 *-valuation
✅ 각 *-valuation → 각 *-portal
✅ 각 *-portal → customer-portal
```

### Phase 4: 프로젝트 관리 연결 (1시간)
```
✅ valuation-list → project-create, project-detail
✅ project-create → 5개 *-portal
✅ project-dashboard → project-detail
✅ project-detail → 양방향 네비게이션
```

### Phase 5: Breadcrumb 추가 (선택, 30분)
```
예: 홈 > 평가방법 > DCF평가법 > DCF 자료제출
```

---

## 📊 추후 추가 필요 페이지 (보안 설정 후)

### 인증 관련 (2개)
```
- login.html - 로그인
- signup.html - 회원가입
```

### 역할별 대시보드 (3개)
```
- client-dashboard.html - 고객 대시보드
- accountant-dashboard.html - 회계사 대시보드
- admin-dashboard.html - 관리자 대시보드
```

### 회계사 작업 (5개)
```
- accountant-workbench.html - 작업 워크벤치
- accountant-calculation.html - 평가 계산
- accountant-report.html - 보고서 작성
- accountant-review.html - 자료 검토
- accountant-task-list.html - 작업 목록
```

### 관리자 관리 (4개)
```
- admin-project-manage.html - 프로젝트 관리
- admin-assign.html - 회계사 배정
- admin-user-manage.html - 사용자 관리
- admin-stats.html - 통계 대시보드
```

**총 14개 추가 필요** (현재 19개 → 최종 33개)

---

## 🔒 보안 TODO (나중에 한 번에 처리)

```sql
-- 1. Supabase RLS 설정
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- 2. 역할별 정책
CREATE POLICY "client_own_projects" ON projects
    FOR SELECT USING (auth.uid() = client_id);

CREATE POLICY "accountant_assigned_projects" ON projects
    FOR SELECT USING (auth.uid() = accountant_id);

CREATE POLICY "admin_all_projects" ON projects
    FOR SELECT USING (
        (auth.jwt() ->> 'role') = 'admin'
    );
```

```javascript
// 3. Frontend 라우팅 가드
function checkUserRole() {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = '/login.html';
        return;
    }
    // 역할별 리다이렉트
}
```

**처리 시점**: 전체 페이지 개발 완료 후

---

## ✅ 현재 작업 우선순위

### 우선순위 1: 페이지 연결 (오늘)
- [ ] 공통 헤더 통일 (19개 페이지)
- [ ] index.html 카드 연결 (7개)
- [ ] 평가법 3단계 연결
- [ ] 프로젝트 관리 연결

### 우선순위 2: 누락 기능 구현 (1주)
- [ ] project-create.html에 평가법 선택 기능 추가
- [ ] valuation-list.html에 "신규 프로젝트" 버튼 추가
- [ ] project-detail.html에 양방향 네비게이션 추가

### 우선순위 3: 회계사/관리자 페이지 추가 (2주)
- [ ] accountant-workbench.html 등 5개
- [ ] admin-project-manage.html 등 4개

### 우선순위 4: 보안 설정 (3주차)
- [ ] Supabase RLS 설정
- [ ] 로그인 시스템
- [ ] 역할별 대시보드

---

## 📝 개발 원칙

```
1. 보안은 나중에 → 지금은 기능 구현
2. 모든 페이지 연결 우선
3. 역할별 플로우 고려 (접근 제어는 나중)
4. 단계별 점진적 개발
```

---

## 🎯 최종 목표

**현재**: 19개 페이지 (부분 연결)
**1단계**: 19개 페이지 (완전 연결) ← 오늘
**2단계**: 33개 페이지 (역할별 페이지 추가) ← 2주
**3단계**: 보안 설정 (RLS + 인증) ← 3주

---

이 계획대로 진행하면 **보안 걱정 없이 기능 개발에 집중**할 수 있습니다!
