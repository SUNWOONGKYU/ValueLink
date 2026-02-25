# S5 PO 테스트 체크리스트

**테스트 대상**: S5M1, S5T1, S5O1
**예상 소요시간**: 2-3시간
**테스트 담당**: PO (Product Owner)

---

## 📋 사전 준비 (30분)

### 필수 설정

- [ ] **Vercel 계정 생성 및 CLI 설치**
  ```bash
  npm install -g vercel
  vercel login
  ```

- [ ] **GitHub Secrets 설정** (리포지토리 Settings → Secrets and variables → Actions)
  ```
  VERCEL_TOKEN: Vercel 계정 토큰
  VERCEL_ORG_ID: Organization ID
  VERCEL_PROJECT_ID: Project ID
  ```

- [ ] **테스트용 Supabase 프로젝트 생성** (프로덕션과 분리)
  - Supabase 콘솔 → Create new project
  - Project name: "ValueLink-Test"

- [ ] **.env.local 파일 생성**
  ```
  SUPABASE_URL=https://xxx.supabase.co
  SUPABASE_ANON_KEY=eyJ...
  SUPABASE_SERVICE_ROLE_KEY=eyJ...
  ```

- [ ] **npm 패키지 설치**
  ```bash
  npm install
  ```

---

## 🧪 테스트 1: 배포 설정 (S5O1) - 30분

### 테스트 1-1: CI/CD 파이프라인 자동화

**절차**:
1. 코드 변경 후 git push
2. GitHub 리포지토리 → Actions 탭 확인
3. 워크플로우 실행 대기

**검증 체크리스트**:
- [ ] CI 워크플로우 실행 (lint → type-check → build → test)
- [ ] 모든 단계 ✅ 통과
- [ ] main 브랜치 merge 후 CD 워크플로우 자동 실행
- [ ] 배포 완료 확인

**예상 결과**:
- 녹색 체크 표시 (✅ All checks passed)
- 배포 소요시간: 3-5분

---

### 테스트 1-2: Vercel 배포

**절차**:
```bash
# 1. Preview 배포 (테스트용)
vercel --preview

# 2. Production 배포
vercel --prod
```

**검증 체크리스트**:
- [ ] Preview URL 생성됨
- [ ] Preview URL 접속 가능
- [ ] Production URL 접속 가능
- [ ] 페이지 로딩 정상 (3초 이내)
- [ ] 보안 헤더 확인 (브라우저 DevTools → Network → Response Headers)
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY
  - [ ] X-XSS-Protection: 1; mode=block
  - [ ] Referrer-Policy: strict-origin-when-cross-origin
  - [ ] Permissions-Policy: microphone=(), camera=()

**예상 결과**:
- Preview URL: `https://{project}-{random}.vercel.app`
- Production URL: `https://valuelink.vercel.app` (또는 커스텀 도메인)
- 모든 보안 헤더 적용됨

**필요 설정 확인**:
- [ ] Vercel Dashboard → Project Settings → Environment Variables (5개)
- [ ] GitHub Secrets 설정 완료

---

## 🧪 테스트 2: 통합 테스트 (S5T1) - 45분

### 테스트 2-1: 통합 테스트 실행

**절차**:
```bash
# 통합 테스트 실행
npm run test

# 커버리지 리포트 생성
npm run test:coverage
```

**검증 체크리스트**:
- [ ] 18/18 통합 테스트 통과
- [ ] 커버리지 87.3% (목표 80% 초과)
- [ ] `coverage/` 폴더에 리포트 생성
- [ ] coverage/index.html 브라우저로 열어 상세 확인

**예상 결과**:
```
PASS: 18 tests
Coverage Summary:
  Statements   : 87.3%
  Branches     : 82.1%
  Functions    : 89.5%
  Lines        : 86.8%
```

---

### 테스트 2-2: E2E 테스트 실행

**절차**:
```bash
# E2E 테스트 실행
npm run test:e2e

# 또는 UI 모드 (디버깅용)
npm run test:e2e:ui
```

**검증 체크리스트**:
- [ ] 3개 사용자 여정 테스트 실행
  - [ ] 고객 여정 (회원가입 → 프로젝트 생성 → 평가 → 보고서)
  - [ ] 회계사 여정 (승인 → 문서 검토)
  - [ ] 관리자 여정 (대시보드 관리)
- [ ] 모든 테스트 통과 (✅ PASS)
- [ ] 브라우저 자동 실행 및 조작 정상

**예상 결과**:
- 6/6 E2E 테스트 통과
- 자동 브라우저 테스트 완료 (소요시간: 3-5분)

---

### 테스트 2-3: 14단계 워크플로우 검증

**절차**:
로컬 또는 배포된 사이트에서 실제 작동 확인

1. [ ] **Step 1**: 프로젝트 생성
   - 기업명, 업종 입력
   - "생성" 버튼 클릭

2. [ ] **Step 2**: 기초 정보 입력
   - 설립일, 직원수, 매출액 입력

3. [ ] **Step 3**: 가치평가 방법 선택
   - 5가지 평가법 중 선택

4. [ ] **Step 4-7**: 평가 엔진 실행
   - DCF, 시뮬레이션, 비교분석 실행
   - ⏱️ 로딩 인디케이터 표시 확인 (S5F8)

5. [ ] **Step 8**: 임시 보고서 생성
   - 평가 결과 표시

6. [ ] **Step 9**: 회계사 초대
   - 이메일 입력 후 초대

7. [ ] **Step 10**: 회계사 승인
   - 승인/반려 선택

8. [ ] **Step 11**: 최종 보고서 생성
   - 평가 결과 다운로드

9. [ ] **Step 12-14**: 추가 기능
   - 뉴스 자동 수집 확인
   - 정기 알림 설정

**예상 결과**: 모든 단계 정상 작동

---

## 🧪 테스트 3: 문서화 (S5M1) - 30분

### 테스트 3-1: README.md 확인

**절차**:
1. README.md 열기
2. 목차(Table of Contents) 확인
3. 설치 가이드 따라 실행

**검증 체크리스트**:
- [ ] README.md 렌더링 정상
- [ ] 목차 링크 모두 작동
- [ ] 설치 가이드 명확
- [ ] 프로젝트 구조(폴더 트리) 정확

---

### 테스트 3-2: architecture.md 확인

**절차**:
1. docs/architecture.md 열기
2. 10개 섹션 검토

**검증 체크리스트**:
- [ ] 시스템 개요 이해 가능
- [ ] 기술 스택 명확 (Next.js 14, React 18, TypeScript)
- [ ] 아키텍처 다이어그램(Mermaid) 렌더링 정상
- [ ] 41개 테이블 설명 정확

---

### 테스트 3-3: maintenance-guide.md 확인

**절차**:
1. docs/maintenance-guide.md 열기
2. SQL 쿼리 중 하나 실행 테스트

**검증 체크리스트**:
- [ ] 일상 점검 항목 명확 (매일/주간/월간)
- [ ] DB 관리 가이드 명확
- [ ] 제공된 SQL 쿼리 실행 가능
- [ ] 백업/복구 절차 명확

---

### 테스트 3-4: troubleshooting.md 확인

**절차**:
1. docs/troubleshooting.md 열기
2. 8개 카테고리 검토

**검증 체크리스트**:
- [ ] 8개 카테고리 모두 포함 (일반/빌드/런타임/DB/인증/크롤러/배포/성능)
- [ ] 각 문제별 원인 → 해결책 명확
- [ ] ❌ Bad vs ✅ Good 코드 비교 유용
- [ ] 24개 문제 모두 검토 가능

---

## ✅ 최종 검증 - 10분

### 전체 체크리스트

| 항목 | 상태 | 비고 |
|------|------|------|
| CI/CD 파이프라인 | ✅/❌ | |
| Vercel 배포 | ✅/❌ | |
| 보안 헤더 | ✅/❌ | |
| 통합 테스트 | ✅/❌ | 18/18 통과 |
| E2E 테스트 | ✅/❌ | 6/6 통과 |
| 14단계 워크플로우 | ✅/❌ | 모든 단계 정상 |
| README | ✅/❌ | |
| Architecture | ✅/❌ | |
| Maintenance | ✅/❌ | |
| Troubleshooting | ✅/❌ | |

### 전체 판정

- [ ] **✅ 모든 테스트 통과** → 프로덕션 배포 승인
- [ ] **❌ 일부 테스트 실패** → 버그 수정 필요 (이슈 번호: ___)

---

## 📞 문제 발생 시

**테스트 중 문제 발생 시 다음 정보 제공**:

1. **문제 설명**: 어디서, 무엇이?
2. **스크린샷/비디오**: 증거 자료
3. **로그**: 에러 메시지, 브라우저 콘솔 로그
4. **환경**: OS, Node.js 버전, npm 버전

```bash
# 환경 정보 수집
node --version
npm --version
cat .env.local
```

---

**예상 완료 시간**: 2-3시간
**테스트 완료 후**: "PO 테스트 완료" 보고
