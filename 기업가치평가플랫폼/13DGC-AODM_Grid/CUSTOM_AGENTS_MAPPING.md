# 커스텀 서브 에이전트 매핑 (기업가치평가 플랫폼)

**프로젝트**: 기업가치평가 플랫폼 (Valuation Platform)
**버전**: 2.0
**작성일**: 2025-10-18
**방법론**: 13DGC-AODM (13-Dimensional Grid-Controlled AI-Only Development Management)

---

## 📋 커스텀 에이전트 목록 (14개)

### 1. **valuation-engineer** ⭐ (신규 추가)
**역할**: 기업가치평가 엔진 개발 및 재무 분석 전문가

**전문 분야**:
- 5가지 평가 엔진 개발 (DCF, 상대가치, NAV, 배당할인, 청산가치)
- 재무 모델링 (FCFF, WACC, Terminal Value, CAPM)
- 데이터 검증 (오차율 ±5% 이내)
- 실제 평가보고서 비교 검증

**담당 작업**:
- P1B1: 5가지 평가 엔진 개발 ✅ 완료 (DCF 검증 완료: 오차율 0.71%)
- 향후 평가 엔진 관련 모든 백엔드 작업

---

### 2. **api-designer**
**역할**: RESTful API 설계 전문가

**전문 분야**:
- RESTful API 아키텍처 설계
- OpenAPI/Swagger 문서 작성
- HTTP 메서드/상태 코드 표준화
- API 버저닝 전략

**담당 작업**:
- P2B1: API Route 설계 (/api/valuation 엔드포인트)
- API 스키마 및 에러 처리 표준화

---

### 3. **ui-designer**
**역할**: UI/UX 디자인 전문가

**전문 분야**:
- 컴포넌트 디자인 (shadcn/ui, Tailwind CSS)
- 접근성 (WCAG 2.1 AA)
- 반응형 디자인
- 사용자 경험 최적화

**담당 작업**:
- P1F1: 웹사이트 목업 HTML 생성 ✅ 완료 (5가지 평가법 HTML 데모)
- P3F1: 문서 업로드 UI (드래그앤드롭)
- P4F1: 인간 승인 대시보드 UI (22개 판단 포인트)
- P6F1: 반응형 디자인 최적화

---

### 4. **frontend-developer**
**역할**: 프론트엔드 개발 전문가

**전문 분야**:
- React/Next.js 개발
- TypeScript
- 상태 관리 (Zustand, React Query)
- 클라이언트 사이드 로직

**담당 작업**:
- P2F1: React 기반 랜딩 페이지
- P5F1: 평가 진행 상황 실시간 모니터링 UI
- P8F1: 고급 차트/그래프 통합

---

### 5. **backend-developer**
**역할**: 백엔드 개발 전문가

**전문 분야**:
- API Route 구현
- 비즈니스 로직
- 서버 사이드 처리
- 데이터 검증

**담당 작업**:
- P3B1: 문서 파싱 엔진 (PDF/Excel 자동 추출)
- P4B1: 인간 승인 시스템 백엔드
- P5B1: 보고서 생성 엔진 (80페이지 PDF)
- P6B1: 이메일 발송 시스템
- P8B1: AI 협력 시스템 통합
- P2C1, P3C1, P4C1: Supabase Auth 설정 및 OAuth

---

### 6. **database-developer**
**역할**: 데이터베이스 설계 및 최적화 전문가

**전문 분야**:
- Supabase PostgreSQL 스키마 설계
- 인덱스 최적화
- 쿼리 성능 튜닝
- 테이블 관계 설계

**담당 작업**:
- P1D1: 데이터베이스 스키마 설계 ✅ 완료
- P2D1: Supabase 테이블 설계 (companies/valuations/documents)
- P3D1: 문서 메타데이터 테이블
- P4D1: 인간 승인 상태 테이블
- P5D1: 보고서 생성 로그 테이블
- P8D1: 데이터 분석 테이블

---

### 7. **security-auditor**
**역할**: 보안 감사 및 RLS 정책 전문가

**전문 분야**:
- Row Level Security (RLS) 정책
- JWT 보안 검증
- 인증/인가 시스템 감사
- OWASP 준수

**담당 작업**:
- P1E1: 인간 승인 시스템 완성 ✅ 완료 (22개 판단 포인트)
- P2E1~P8E1: RLS 정책 설계 (사용자별 데이터 격리)
- P1C1: 인증 시스템 설계 ✅ 완료
- P5C1: 세션 관리 및 JWT 검증
- P6C1: 2FA 도입
- P7C1: SSO 기업용
- P8C1: 생체 인증 (WebAuthn)
- P2S1: API 보안 검토 (Rate Limiting, CORS, CSP)
- P4S1: 인증/인가 보안 감사
- P6S1, P7S1: OWASP ZAP 취약점 스캔

---

### 8. **security-specialist**
**역할**: 고급 보안 전문가

**전문 분야**:
- 데이터 암호화
- 악성 파일 검증
- 보안 아키텍처
- OWASP Top 10 대응

**담당 작업**:
- P1S1: 보안 요구사항 정의 (OWASP Top 10) ✅ 완료
- P3S1: 파일 업로드 보안 (악성 파일 검증, 바이러스 스캔)
- P5S1: 데이터 암호화 (재무 데이터 AES-256)

---

### 9. **test-engineer**
**역할**: 테스트 자동화 전문가

**전문 분야**:
- 유닛 테스트 (Jest, Pytest)
- 통합 테스트 (Supertest)
- E2E 테스트 (Puppeteer)
- 품질 검증

**담당 작업**:
- P1T1: 5개 엔진 유닛 테스트 ✅ 완료 (DCF 검증: 오차율 0.71%)
- P2T1: API 통합 테스트
- P3T1: 문서 파싱 정확도 테스트
- P4T1: 인간 승인 시스템 E2E 테스트
- P5T1: 보고서 생성 품질 검증
- P6T1: 부하 테스트 (동시 100명)

---

### 10. **devops-troubleshooter**
**역할**: DevOps 및 인프라 전문가

**전문 분야**:
- CI/CD 파이프라인 (GitHub Actions)
- Vercel/Railway 배포
- 모니터링 (Sentry, LogRocket)
- 백업 자동화

**담당 작업**:
- P1A1: 프로젝트 초기 설정 ✅ 완료
- P2A1~P8A1: 모든 DevOps & Infra 작업
- P6D1: 인덱스 최적화 및 쿼리 성능 개선
- P7D1: 백업 자동화 시스템
- P7B1: 프로덕션 서버 배포
- P7T1: 프로덕션 스모크 테스트
- P8S1: 보안 패치 자동화 (Dependabot)

---

### 11. **performance-optimizer**
**역할**: 성능 최적화 전문가

**전문 분야**:
- Lighthouse 성능 튜닝
- 번들 사이즈 최적화
- 쿼리 최적화
- 캐싱 전략

**담당 작업**:
- P6D1: 인덱스 최적화 및 쿼리 성능 개선
- P7F1: 프로덕션 빌드 최적화 및 CDN 연동
- P8T1: 성능 벤치마크 (평가 1건당 60분 이내 목표)

---

### 12. **code-reviewer**
**역할**: 코드 품질 검토 전문가

**전문 분야**:
- 코드 리뷰
- 베스트 프랙티스 검증
- 리팩토링 제안
- 코드 품질 표준 유지

**담당 작업**:
- 모든 Phase에서 코드 리뷰 수행 (필요 시 호출)

---

### 13. **test-simple**
**역할**: 간단한 테스트 전문가

**전문 분야**:
- 빠른 스모크 테스트
- 기본 기능 검증
- 회귀 테스트

**담당 작업**:
- 필요 시 간단한 테스트 수행

---

### 14. **fullstack-developer** (예비)
**역할**: 풀스택 개발 전문가 (범용)

**전문 분야**:
- Frontend + Backend + Database
- 빠른 프로토타이핑
- 작은 기능 구현

**담당 작업**:
- 예비 인력 (특정 작업 없음, 필요 시 투입)

---

## 📊 영역별 담당 에이전트 요약

| 영역 | Phase 1 담당 | Phase 2+ 주요 담당 |
|------|-------------|-------------------|
| **Frontend** | ui-designer ✅ | ui-designer, frontend-developer |
| **Backend** | valuation-engineer ✅ | api-designer, backend-developer, valuation-engineer |
| **Database** | database-developer ✅ | database-developer, performance-optimizer |
| **RLS Policies** | security-auditor ✅ | security-auditor |
| **Authentication** | security-auditor ✅ | backend-developer, security-auditor |
| **Test & QA** | test-engineer ✅ | test-engineer, devops-troubleshooter, performance-optimizer |
| **DevOps & Infra** | devops-troubleshooter ✅ | devops-troubleshooter |
| **Security** | security-specialist ✅ | security-auditor, security-specialist |

---

## ✅ Phase 1 완료 현황

| 작업 | 담당 AI | 진도 | 상태 | 비고 |
|------|---------|------|------|------|
| P1F1 | ui-designer | 100% | ✅ 완료 (2025-10-17 10:15) | 5가지 평가법 HTML 데모 완성 |
| P1B1 | valuation-engineer | 100% | ✅ 완료 (2025-10-18 12:00) | DCF 검증 완료 (오차율 0.71%) |
| P1D1 | database-developer | 100% | ✅ 완료 (2025-10-17 09:00) | 파일 기반 설계 완료 |
| P1E1 | security-auditor | 100% | ✅ 완료 (2025-10-17 12:30) | 22개 판단 포인트 완성 |
| P1C1 | security-auditor | 100% | ✅ 완료 (2025-10-17 08:30) | 인증 시스템 설계 완료 |
| P1T1 | test-engineer | 100% | ✅ 완료 (2025-10-18 13:00) | DCF 엔진 유닛 테스트 통과 |
| P1A1 | devops-troubleshooter | 100% | ✅ 완료 (2025-10-17 08:00) | 프로젝트 구조 완성 |
| P1S1 | security-specialist | 100% | ✅ 완료 (2025-10-18 14:00) | OWASP Top 10 체크리스트 완성 |

**Phase 1 완료율**: 100% (8/8 작업 완료) ✅

---

## 🎯 Phase 2 시작 준비 사항

1. **작업지시서 생성**: tasks/P2F1.md ~ tasks/P2S1.md 생성 필요
2. **Supabase 프로젝트 생성**: Phase 2부터 데이터베이스 도입
3. **환경 변수 설정**: .env.example 파일 준비
4. **API 스펙 설계**: OpenAPI 문서 작성 (api-designer 담당)

---

## 📝 에이전트 호출 예시

### 평가 엔진 개발 시
```
/task valuation-engineer "DCF 엔진의 Terminal Value 계산 로직 개선"
```

### API 설계 시
```
/task api-designer "5가지 평가법을 위한 RESTful API 엔드포인트 설계"
```

### UI 디자인 시
```
/task ui-designer "22개 판단 포인트 대시보드 UI 디자인"
```

### 보안 검토 시
```
/task security-auditor "RLS 정책 및 JWT 토큰 검증 로직 보안 감사"
```

---

## 🔄 업데이트 이력

- **2025-10-18**: v2.0 - 커스텀 에이전트 14개 완전 반영, Phase 1 완료율 100% 달성
- **2025-10-17**: v1.0 - 초안 작성 (fullstack-developer 중심)

---

**버전**: 2.0
**작성자**: Claude (Main Agent)
**프로젝트**: 기업가치평가 플랫폼
