# PoliticianFinder Skills 사용 가이드

**AI 기반 정치인 평가 플랫폼 개발을 위한 전문 스킬 모음**

---

## 📚 스킬 개요

이 디렉토리에는 PoliticianFinder 프로젝트 개발을 위한 15개의 전문 스킬이 포함되어 있습니다. 각 스킬은 특정 개발 영역에 특화되어 있으며, Claude Code와 함께 사용하여 효율적인 개발을 지원합니다.

---

## 🎯 스킬이란?

**스킬(Skill)**은 Claude Code가 특정 작업을 수행할 때 참조하는 전문 지식과 가이드라인입니다. 스킬을 활성화하면:

1. 해당 분야의 모범 사례를 자동으로 적용
2. 프로젝트별 컨텍스트와 제약사항 준수
3. 일관된 코드 품질 및 문서화 유지
4. AI-only 개발 원칙 자동 준수

---

## 📋 스킬 목록

### 개발 관련 (4개)

| 스킬 | 파일 | 설명 |
|------|------|------|
| **풀스택 개발** | `fullstack-dev.md` | Frontend + Backend + Database 통합 개발 |
| **API 구축** | `api-builder.md` | RESTful API 엔드포인트 설계 및 구현 |
| **UI 구축** | `ui-builder.md` | React 컴포넌트 및 페이지 개발 |
| **DB 스키마** | `db-schema.md` | 데이터베이스 설계 및 마이그레이션 |

### 품질 관리 (3개)

| 스킬 | 파일 | 설명 |
|------|------|------|
| **코드 리뷰** | `code-review.md` | 코드 품질 검토 및 개선 제안 |
| **보안 감사** | `security-audit.md` | 보안 취약점 검사 및 OWASP 준수 |
| **성능 검사** | `performance-check.md` | 성능 분석 및 최적화 제안 |

### 테스트 (3개)

| 스킬 | 파일 | 설명 |
|------|------|------|
| **테스트 실행** | `test-runner.md` | 자동화 테스트 실행 및 보고 |
| **E2E 테스트** | `e2e-test.md` | End-to-End 테스트 작성 및 실행 |
| **API 테스트** | `api-test.md` | API 엔드포인트 테스트 전문 |

### DevOps (3개)

| 스킬 | 파일 | 설명 |
|------|------|------|
| **배포** | `deployment.md` | Vercel 배포 자동화 |
| **문제 해결** | `troubleshoot.md` | 디버깅 및 이슈 해결 |
| **CI/CD 설정** | `cicd-setup.md` | GitHub Actions 파이프라인 구성 |

### 프로젝트 관리 (2개)

| 스킬 | 파일 | 설명 |
|------|------|------|
| **프로젝트 기획** | `project-plan.md` | 요구사항 분석 및 작업 분해 |
| **문서 작성** | `doc-writer.md` | 기술 문서 및 API 문서 작성 |

---

## 🚀 스킬 사용 방법

### Claude Code에서 스킬 활성화

**중요**: Claude Code는 현재 스킬을 자동으로 인식하지 않습니다. 대신 다음과 같은 방법으로 사용하세요:

#### 방법 1: 작업 시작 시 명시
```
사용자: "fullstack-dev 스킬을 사용해서 정치인 목록 API를 구현해주세요"
```

#### 방법 2: 파일 경로 참조
```
사용자: ".claude/skills/fullstack-dev.md 파일의 가이드라인을 따라 개발해주세요"
```

#### 방법 3: Task 에이전트 활용
```
메인 에이전트: "fullstack-dev 스킬을 참조하여 P2A1 작업을 수행해주세요"
→ Task 에이전트 실행
```

---

## 📖 스킬 사용 예시

### 예시 1: API 개발

**시나리오**: 정치인 목록 조회 API 구현

```
사용자: "api-builder 스킬을 사용해서 다음 API를 구현해주세요:
- GET /api/politicians
- 페이지네이션 지원 (page, limit)
- 필터링 (party, region)
- 정렬 (avg_rating)"
```

**결과**:
- API Route 파일 생성 (`app/api/politicians/route.ts`)
- 표준 응답 형식 적용
- 에러 핸들링 포함
- Zod 검증 추가
- 완료 보고서 생성

---

### 예시 2: 코드 리뷰

**시나리오**: Phase 2 코드 검토

```
사용자: "code-review 스킬을 사용해서 app/api/politicians/ 디렉토리의 코드를 리뷰해주세요"
```

**결과**:
- 코드 품질 평가 (A/B/C/D/F)
- 우선순위별 개선 사항 (P0-P3)
- 베스트 프랙티스 준수 여부
- 구체적인 수정 제안

---

### 예시 3: 테스트 실행

**시나리오**: 전체 테스트 스위트 실행

```
사용자: "test-runner 스킬을 사용해서 모든 테스트를 실행하고 결과를 보고해주세요"
```

**결과**:
- 단위 테스트 실행 (Jest)
- E2E 테스트 실행 (Playwright)
- 커버리지 리포트
- 실패한 테스트 분석
- 상세 보고서

---

## 🔧 스킬 조합 사용

여러 스킬을 순차적으로 사용하여 복잡한 작업 수행:

### 워크플로우 예시: 새 기능 개발

```markdown
1. **기획 단계**
   스킬: project-plan.md
   작업: 요구사항 분석, 작업 분해, 일정 수립

2. **개발 단계**
   스킬: fullstack-dev.md, api-builder.md, ui-builder.md
   작업: API + UI 구현

3. **품질 검증**
   스킬: code-review.md, security-audit.md
   작업: 코드 리뷰, 보안 검사

4. **테스트**
   스킬: test-runner.md, api-test.md
   작업: 자동화 테스트 실행

5. **배포**
   스킬: deployment.md
   작업: Vercel 배포

6. **문서화**
   스킬: doc-writer.md
   작업: API 문서, README 업데이트
```

---

## 🎓 스킬별 주요 사용 시나리오

### fullstack-dev.md
- 완전한 기능 구현 (Frontend + Backend)
- CRUD 작업
- 인증 시스템 통합

### api-builder.md
- RESTful API 엔드포인트 구축
- 데이터 검증 및 에러 핸들링
- API 문서 생성

### ui-builder.md
- React 컴포넌트 개발
- 페이지 레이아웃
- 반응형 디자인

### db-schema.md
- 새 테이블 설계
- 마이그레이션 작성
- RLS 정책 설정

### code-review.md
- PR 리뷰
- 리팩토링 제안
- 기술 부채 식별

### security-audit.md
- 배포 전 보안 검사
- 취약점 스캔
- OWASP Top 10 검증

### performance-check.md
- 느린 쿼리 분석
- Bundle 크기 최적화
- Core Web Vitals 개선

### test-runner.md
- CI/CD 파이프라인에서 테스트
- 커버리지 확인
- 회귀 테스트

### e2e-test.md
- 사용자 시나리오 테스트
- 크로스 브라우저 테스트
- Visual regression

### api-test.md
- API 계약 검증
- 성능 테스트
- 부하 테스트

### deployment.md
- 프로덕션 배포
- 환경변수 관리
- 롤백 절차

### troubleshoot.md
- 프로덕션 이슈 해결
- 로그 분석
- 긴급 패치

### cicd-setup.md
- GitHub Actions 설정
- 자동화 파이프라인
- 보안 스캔 통합

### project-plan.md
- Phase 기획
- WBS 작성
- 리소스 할당

### doc-writer.md
- README 작성
- API 레퍼런스
- 아키텍처 문서

---

## ⚠️ 주의사항

### AI-only 원칙 준수

모든 스킬은 다음 원칙을 따릅니다:

✅ **허용**:
- CLI 명령어
- 코드/설정 파일
- API/SDK 사용
- 자동화 스크립트

❌ **금지**:
- Dashboard/Console 수동 클릭
- GUI 도구 사용
- 수동 데이터베이스 조작
- 사용자에게 수동 작업 요청

### 스킬 충돌 방지

- 한 번에 하나의 주요 스킬만 활성화
- 보조 스킬은 병행 사용 가능 (예: fullstack-dev + code-review)
- 스킬 간 충돌 시 더 구체적인 스킬 우선

---

## 📊 스킬 효과 측정

### 개발 속도
- 표준 템플릿 사용으로 30-50% 빠른 개발
- 반복 작업 자동화
- 일관된 코드 구조

### 코드 품질
- 베스트 프랙티스 자동 적용
- 보안 취약점 조기 발견
- 유지보수성 향상

### 문서화
- 자동 문서 생성
- 일관된 문서 형식
- 최신 상태 유지

---

## 🔄 스킬 업데이트

### 스킬 개선 제안
1. 문제점 발견 시 기록
2. 개선 사항 문서화
3. 스킬 파일 업데이트
4. 팀원과 공유

### 새 스킬 추가
1. 반복되는 작업 패턴 식별
2. 기존 스킬 참조하여 작성
3. 테스트 및 검증
4. 이 README에 추가

---

## 🆘 문제 해결

### "스킬을 찾을 수 없습니다"
→ 파일 경로 확인: `.claude/skills/[skill-name].md`

### "스킬이 적용되지 않습니다"
→ 명시적으로 스킬 이름 언급: "XXX 스킬을 사용해서..."

### "여러 스킬 중 어떤 것을 사용해야 할까요?"
→ 아래 의사결정 트리 참조

---

## 🌳 스킬 선택 의사결정 트리

```
개발 작업인가?
├─ Yes → Frontend + Backend?
│   ├─ Yes → fullstack-dev
│   ├─ API만? → api-builder
│   ├─ UI만? → ui-builder
│   └─ DB만? → db-schema
└─ No → 어떤 작업?
    ├─ 코드 검토 → code-review
    ├─ 보안 검사 → security-audit
    ├─ 성능 분석 → performance-check
    ├─ 테스트 작성/실행 → test-runner/e2e-test/api-test
    ├─ 배포 → deployment
    ├─ 문제 해결 → troubleshoot
    ├─ CI/CD → cicd-setup
    ├─ 기획 → project-plan
    └─ 문서 → doc-writer
```

---

## 📈 다음 단계

1. **학습**: 각 스킬 파일을 읽고 구조 파악
2. **실습**: 간단한 작업에 스킬 적용
3. **평가**: 스킬 사용 전후 비교
4. **개선**: 피드백 반영 및 스킬 업데이트
5. **확장**: 새로운 스킬 추가

---

## 📞 문의 및 피드백

스킬 관련 문의:
- 프로젝트 관리자에게 문의
- `.claude/skills/` 디렉토리에 개선 제안 작성
- 팀 회의에서 논의

---

## 📚 추가 리소스

- [프로젝트 매뉴얼](../../3DProjectGrid_v7.0_WORK/기획문서/)
- [AI-only 개발 원칙](../../3DProjectGrid_v7.0_WORK/기획문서/AI-only_개발_원칙.md)
- [메인 에이전트 역할](../../3DProjectGrid_v7.0_WORK/기획문서/메인에이전트_역할정의.md)

---

## ✅ 체크리스트: 스킬 활용 준비

- [ ] 모든 스킬 파일 읽어보기
- [ ] AI-only 개발 원칙 숙지
- [ ] 프로젝트 구조 이해
- [ ] 첫 번째 스킬 시도 (fullstack-dev 추천)
- [ ] 결과 평가 및 피드백

---

**Happy Coding with Skills! 🚀**

*마지막 업데이트: 2025-10-23*
*버전: 1.0*
*PoliticianFinder 프로젝트 전용*
