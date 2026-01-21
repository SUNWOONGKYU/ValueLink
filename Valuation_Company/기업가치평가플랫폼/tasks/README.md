# 기업가치평가 플랫폼 - 작업지시서 목록

## 개요

이 디렉토리는 기업가치평가 플랫폼 프로젝트의 모든 작업지시서를 포함합니다.
총 8개 Phase, 8개 영역, 64개 작업으로 구성되어 있습니다.

**생성일**: 2025-10-18
**프로젝트 그리드**: `G:\내 드라이브\Content\기업가치평가플랫폼\13DGC-AODM_Grid\project_grid_v2.0_valuation_platform.csv`

---

## Phase 구조

### Phase 1: 코어 엔진 개발 (완료)
- **상태**: 100% 완료
- **작업**: P1F1, P1B1, P1D1, P1E1, P1C1, P1T1, P1A1, P1S1
- **주요 성과**:
  - DCF 엔진 개발 완료 (오차율 0.71%)
  - 웹사이트 목업 HTML 생성 완료
  - 인간 승인 시스템 기반 구축 (22개 판단 포인트)

### Phase 2: 웹 인터페이스 구축 (대기)
- **목표**: React 기반 웹 애플리케이션 구축
- **작업**: P2F1, P2B1, P2D1, P2E1, P2C1, P2T1, P2A1, P2S1
- **주요 내용**:
  - React 랜딩 페이지 구현
  - API Route 설계 및 구현
  - Supabase 데이터베이스 설정
  - 인증 시스템 구축

### Phase 3: 문서 처리 자동화 (대기)
- **목표**: 재무제표 자동 파싱 시스템
- **작업**: P3F1, P3B1, P3D1, P3E1, P3C1, P3T1, P3A1, P3S1
- **주요 내용**:
  - 드래그앤드롭 파일 업로드 UI
  - PDF/Excel 파싱 엔진 (OCR/표 인식)
  - OAuth 소셜 로그인
  - 파일 업로드 보안

### Phase 4: 인간 승인 시스템 (대기)
- **목표**: 22개 판단 포인트 승인 시스템
- **작업**: P4F1, P4B1, P4D1, P4E1, P4C1, P4T1, P4A1, P4S1
- **주요 내용**:
  - 인간 승인 대시보드 UI
  - 승인 API 및 상태 관리
  - 평가자 권한 관리
  - CI/CD 파이프라인 구축

### Phase 5: 보고서 생성 (대기)
- **목표**: 80페이지 PDF 보고서 자동 생성
- **작업**: P5F1, P5B1, P5D1, P5E1, P5C1, P5T1, P5A1, P5S1
- **주요 내용**:
  - 평가 진행 모니터링 UI
  - 보고서 생성 엔진 (PDF)
  - 보고서 다운로드 권한
  - 모니터링 시스템 (Sentry/LogRocket)

### Phase 6: 테스트 & 검증 (대기)
- **목표**: 품질 보증 및 성능 최적화
- **작업**: P6F1, P6B1, P6D1, P6E1, P6C1, P6T1, P6A1, P6S1
- **주요 내용**:
  - 반응형 디자인 최적화
  - 이메일 발송 시스템
  - 데이터베이스 성능 개선
  - 부하 테스트 (동시 100명)

### Phase 7: 배포 & 운영 (대기)
- **목표**: 프로덕션 환경 배포
- **작업**: P7F1, P7B1, P7D1, P7E1, P7C1, P7T1, P7A1, P7S1
- **주요 내용**:
  - 프로덕션 빌드 최적화
  - Vercel/Railway 배포
  - 백업 자동화
  - 보안 체크리스트 검증

### Phase 8: 고도화 (대기)
- **목표**: 고급 기능 및 AI 통합
- **작업**: P8F1, P8B1, P8D1, P8E1, P8C1, P8T1, P8A1, P8S1
- **주요 내용**:
  - 고급 차트/그래프 라이브러리
  - AI 협력 시스템 (Claude/Gemini)
  - 멀티 테넌시 RLS
  - 성능 벤치마크 (60분 이내)

---

## 영역별 분류

### Frontend (F)
웹 인터페이스 및 사용자 경험
- P1F1, P2F1, P3F1, P4F1, P5F1, P6F1, P7F1, P8F1

### Backend (B)
API 및 비즈니스 로직
- P1B1, P2B1, P3B1, P4B1, P5B1, P6B1, P7B1, P8B1

### Database (D)
데이터베이스 스키마 및 최적화
- P1D1, P2D1, P3D1, P4D1, P5D1, P6D1, P7D1, P8D1

### RLS Policies (E)
보안 정책 및 접근 제어
- P1E1, P2E1, P3E1, P4E1, P5E1, P6E1, P7E1, P8E1

### Authentication (C)
인증 및 인가 시스템
- P1C1, P2C1, P3C1, P4C1, P5C1, P6C1, P7C1, P8C1

### Test & QA (T)
테스트 및 품질 보증
- P1T1, P2T1, P3T1, P4T1, P5T1, P6T1, P7T1, P8T1

### DevOps & Infra (A)
인프라 및 배포 자동화
- P1A1, P2A1, P3A1, P4A1, P5A1, P6A1, P7A1, P8A1

### Security (S)
보안 감사 및 취약점 관리
- P1S1, P2S1, P3S1, P4S1, P5S1, P6S1, P7S1, P8S1

---

## 작업지시서 형식

각 작업지시서는 다음 구조를 따릅니다:

```markdown
# [작업ID]: [작업 제목]

**Phase**: [Phase 번호] - [Phase 이름]
**영역**: [영역 이름]
**담당 AI**: [담당 AI 역할]
**작업 ID**: [작업ID]

---

## 작업 개요
## 작업 목표
## 상세 요구사항
## 기술 스택
## 산출물
## 완료 기준
## 의존 작업
## 비고
## 작업 이력
```

---

## 담당 AI 역할

### 설계 및 개발
- **ui-designer**: UI/UX 설계 및 프로토타입
- **frontend-developer**: React/Next.js 프론트엔드 개발
- **backend-developer**: API 및 비즈니스 로직 개발
- **database-developer**: 데이터베이스 설계 및 최적화
- **valuation-engineer**: 평가 엔진 개발 (전문)

### 보안 및 인프라
- **security-auditor**: 보안 감사 및 RLS 정책
- **security-specialist**: 보안 강화 및 취약점 관리
- **devops-troubleshooter**: 인프라 및 배포 자동화

### 품질 보증
- **test-engineer**: 테스트 설계 및 실행
- **performance-optimizer**: 성능 최적화 및 벤치마크
- **api-designer**: API 설계 및 문서화

---

## 작업 진행 상황

| Phase | Frontend | Backend | Database | RLS | Auth | Test | DevOps | Security | 전체 |
|-------|----------|---------|----------|-----|------|------|--------|----------|------|
| **P1** | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | **100%** |
| **P2** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | **0%** |
| **P3** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | **0%** |
| **P4** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | **0%** |
| **P5** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | **0%** |
| **P6** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | **0%** |
| **P7** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | **0%** |
| **P8** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | **0%** |

**전체 프로젝트 진도**: 8/64 작업 완료 (12.5%)

---

## 작업 의존성 체인

### 주요 의존성 흐름

#### Frontend 체인
P1F1 → P2F1 → P3F1 → P4F1 → P5F1 → P6F1 → P7F1 → P8F1

#### Backend 체인
P1B1 → P2B1 → P3B1 → P4B1 → P5B1 → P6B1 → P7B1 → P8B1

#### Database 체인
P1D1 → P2D1 → P3D1 → P4D1 → P5D1 → P6D1 → P7D1 → P8D1

#### 크로스 의존성
- P2F1은 P1F1과 P1B1에 의존
- P3F1은 P2F1과 P2B1에 의존
- P4F1은 P3F1, P3B1, P1E1에 의존
- P6T1은 P5T1에 의존
- P7T1은 P7B1에 의존

---

## 핵심 기술 스택

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **UI Library**: React 18+, TypeScript
- **Styling**: Tailwind CSS, shadcn/ui
- **State**: React Context API, Zustand

### Backend
- **Framework**: Next.js API Routes, Python 3.10+
- **Database**: Supabase PostgreSQL
- **Authentication**: Supabase Auth, JWT
- **Libraries**: pandas, numpy, pdfplumber

### DevOps
- **Hosting**: Vercel (Frontend), Railway (Backend)
- **Database**: Supabase
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry, LogRocket
- **CDN**: Cloudflare

### Security
- **Scanning**: OWASP ZAP, Snyk
- **Dependency**: Dependabot
- **Secrets**: Vercel Environment Variables

---

## 다음 단계

### Phase 2 시작 조건
Phase 1의 모든 작업이 완료되었으므로, Phase 2를 시작할 수 있습니다.

**우선 착수 작업 (의존성 없음)**:
1. **P2A1**: Vercel/Railway 프로젝트 생성
2. **P2D1**: Supabase 데이터베이스 설계

**순차 착수 작업**:
3. **P2E1**: RLS 정책 설계 (P2D1 완료 후)
4. **P2C1**: Supabase Auth 설정 (P2D1 완료 후)
5. **P2B1**: API Route 설계 (P1B1 완료)
6. **P2F1**: React 랜딩 페이지 (P1F1, P1B1 완료)
7. **P2T1**: API 통합 테스트 (P2B1 완료 후)
8. **P2S1**: API 보안 검토 (P2B1 완료 후)

---

## 품질 기준

### 코드 품질
- TypeScript 타입 안전성 100%
- ESLint 규칙 준수
- 코드 커버리지 80% 이상

### 성능 목표
- Lighthouse 성능 점수 90+
- API 응답 시간 < 500ms
- 평가 1건당 처리 시간 < 60분

### 보안 기준
- OWASP Top 10 체크리스트 통과
- 취약점 스캔 정기 실행
- RLS 정책 100% 커버리지

### 테스트 기준
- 유닛 테스트 커버리지 80%+
- 통합 테스트 통과율 100%
- E2E 테스트 주요 시나리오 커버

---

## 참고 자료

### 프로젝트 문서
- **프로젝트 그리드**: `G:\내 드라이브\Content\기업가치평가플랫폼\13DGC-AODM_Grid\project_grid_v2.0_valuation_platform.csv`
- **백엔드 서비스**: `G:\내 드라이브\Developement\Valuation_Company\valuation-platform\backend\app\services`
- **에이전트 설정**: `G:\내 드라이브\Developement\Valuation_Company\valuation-platform\.claude\agents`

### 검증 자료
- **DCF 검증 보고서**: `G:/내 드라이브/Content/기업가치평가플랫폼/validation/dcf/verify_enkinoai_dcf.md`
- **실제 평가보고서**: `FY25 엔키노에이아이 기업가치 평가보고서 0826 (1).pdf`

---

## 연락처

**프로젝트 관리**: Claude Code AI System
**생성 스크립트**: `generate_task_instructions.py`
**최종 업데이트**: 2025-10-18

---

## 버전 이력

- **v2.0** (2025-10-18): Phase 2~8 작업지시서 56개 생성
- **v1.0** (2025-10-17): Phase 1 작업지시서 8개 생성
