# ValueLink 프로젝트 P0 재구축 계획

**작성일**: 2026-02-05
**버전**: 1.0
**프로젝트**: ValueLink - AI 기반 기업가치평가 플랫폼
**상태**: P0 검증 완료, P1 진행 대기

---

## 개요

**현재 상태:**
- ValueLink 기업가치평가 플랫폼 85% 완성 (목업 단계)
- 8,504줄 Python 코드 (5개 평가 엔진)
- 28개 HTML 평가 워크플로우 페이지
- 14개 데이터베이스 테이블
- Supabase 백엔드 연동 작동 중

**목표:**
SAL Grid 방법론을 따라 P0부터 체계적으로 재구축: P0 → P1 → P2 → P3 → S0 → S1-S5

---

## 단계별 실행 계획

### P0: 디렉토리 구조 검증 ✅ 완료

**작업 내용:**
1. `Process/` 폴더 구조 확인 ✅
2. P1-P3, S1-S5 폴더 검증 ✅
3. 기존 자산 파악 ✅
   - 126개 Python 파일
   - 72개 HTML 페이지
   - 5개 평가 엔진 (DCF, Relative, Asset, Intrinsic, Tax)
   - WHITE_PAPER v1.0
   - 플랫폼개발계획서
4. 프로젝트 상태 문서 갱신 ✅

**산출물:**
- `Process/P0_작업_디렉토리_구조_생성/Project_Status.md` 업데이트 ✅
- `Process/P0_작업_디렉토리_구조_생성/Project_Directory_Structure.md` 업데이트 예정

**검증 기준:**
- [x] 모든 필수 폴더 존재 확인
- [x] 기존 자산 파악 완료
- [ ] Project_Directory_Structure.md 업데이트

---

### P1: 사업계획 문서화

**핵심 원칙:** 기존 자산 활용 (플랫폼개발계획서 존재)

**작업 내용:**

#### Vision_Mission + Business_Model
- `Process/P1_사업계획/Vision_Mission/vision-statement.md`
  - "기업가치평가를 넘어 투자 생태계를 연결하는 플랫폼"
  - AI + Human 전문성 모델
- `Process/P1_사업계획/Business_Model/business-model-canvas.md`
  - 수익 모델: DCF 800만원, Relative 500만원, Tax 1,000만원, IPO 2,000만원, Asset 600만원
  - AI Avatar IR: 월 200만원
  - 플랫폼 중개 수수료: 1-3%

#### Market_Analysis
- `Process/P1_사업계획/Market_Analysis/market-size-analysis.md`
  - TAM/SAM/SOM 분석 (한국 스타트업 평가 시장)
  - 경쟁사 분석 (vs. 전통 회계법인)
  - 타겟 고객: 기업, 투자자, 회계사

#### Patent + IP Strategy
- `Process/P1_사업계획/Patent/ip-strategy.md`
  - 5개 평가 엔진을 영업 비밀로 보호
  - IP 목록: 3,559줄 Python 코드 (DCF/Relative/IPO/Asset/Tax)

#### BusinessPlan 통합
- `Process/P1_사업계획/BusinessPlan/executive-summary.md`
- `Process/P1_사업계획/BusinessPlan/financial-projections.md`
  - 3개월: 기업 30개, 투자자 50명
  - 1년: 기업 100개, 투자자 200명, 월 5,000만원
  - 3년: 기업 300개, 투자자 600명, 월 1억원

**검증 기준:**
- [ ] 5개 하위 폴더에 각각 최소 1개 문서
- [ ] 비즈니스 모델 명확히 정의
- [ ] 시장 기회 정량적으로 제시
- [ ] 재무 예측 포함

**참조 파일:**
- `C:\ValueLink\Valuation_Company\플랫폼개발계획\valuation.ai.kr_홈페이지_개발계획서.md`

---

### P2: 프로젝트 기획

**핵심 전략:** 기존 코드에서 역공학으로 요구사항 추출

**작업 내용:**

#### Requirements
- `Process/P2_프로젝트_기획/Requirements/functional-requirements.md`
  - FR-001: 5개 평가 방법 (DCF, Relative, Tax, IPO, Asset)
  - FR-002: 사용자 역할 (고객, 회계사, 관리자)
  - FR-003: 14단계 워크플로우
  - FR-004: 22개 AI 승인 포인트
- `Process/P2_프로젝트_기획/Requirements/non-functional-requirements.md`
  - 성능, 보안, 확장성 요구사항

**추출 소스:**
```python
# backend/app/services/valuation_orchestrator.py (워크플로우)
# backend/app/services/valuation_engine/* (5개 엔진)
# backend/database/create_tables.sql (approval_points 테이블)
```

#### User_Flows + UI_UX_Mockup
- `Process/P2_프로젝트_기획/User_Flows/customer-journey.md`
  - 평가 요청 → 견적 → 협상 → 서류 업로드 → 초안 생성 → 수정 → 최종 보고서
- `Process/P2_프로젝트_기획/UI_UX_Mockup/page-inventory.md`
  - **기존 72개 HTML 페이지를 목업으로 활용** (재설계 불필요)
  - 각 페이지 스크린샷 및 기능 설명

#### Design_System
- `Process/P2_프로젝트_기획/Design_System/design-tokens.md`
  - 컬러: Primary #DC2626, 보조색 추출
  - 타이포그래피: Pretendard 폰트
  - 컴포넌트: 버튼, 카드, 테이블 스타일

#### Tech_Stack + Database ERD
- `Process/P2_프로젝트_기획/Tech_Stack/architecture.md`
  - Frontend: Next.js 14, TypeScript, Tailwind CSS
  - Backend: Supabase (PostgreSQL), FastAPI (Python)
  - AI: Claude (60%), Gemini (20%), ChatGPT (20%)
- `Process/P2_프로젝트_기획/Tech_Stack/database-erd.md`
  - **역공학:** `backend/create_tables.sql`에서 9개 핵심 테이블 추출
  - projects, quotes, negotiations, documents, approval_points, valuation_results, drafts, revisions, reports

#### Project_Plan + Workflows
- `Process/P2_프로젝트_기획/Project_Plan/timeline-milestones.md`
  - 프로젝트 일정 및 마일스톤 (P0-S5)
- `Process/P2_프로젝트_기획/Workflows/development-workflow.md`
  - Git 전략, 리뷰 프로세스, 배포 워크플로우

**검증 기준:**
- [ ] 모든 기능 요구사항 문서화 완료
- [ ] ERD에 9개 이상 테이블 정의
- [ ] 72개 HTML 페이지 목록 작성
- [ ] 기술 스택 명확히 정의
- [ ] 프로젝트 일정 수립 완료

**참조 파일:**
- `C:\ValueLink\Valuation_Company\valuation-platform\ARCHITECTURE.md`
- `C:\ValueLink\Valuation_Company\valuation-platform\backend\create_tables.sql`
- `C:\ValueLink\Valuation_Company\valuation-platform\backend\app\services\valuation_orchestrator.py`

---

### P3: 프로토타입 정리

**현황:** P3는 이미 85% 완료 - 조직화만 필요

**작업 내용:**

#### Frontend 인벤토리
```bash
# 기존 페이지 복사
cp -r Valuation_Company/valuation-platform/frontend/app/* \
      Process/P3_프로토타입_제작/Frontend/
```
- `Process/P3_프로토타입_제작/Frontend/README.md`
  - 72개 HTML 페이지 목록
  - 작동 상태 (완전히 작동 / 부분 작동 / 목업만)
  - Supabase 통합 상태

#### Database + Documentation
- `Process/P3_프로토타입_제작/Database/complete-schema.sql`
  - 모든 SQL 파일 통합
  - 25개 테스트 프로젝트 데이터 익스포트
- `Process/P3_프로토타입_제작/Database/table-relationships.md`
  - 테이블 간 관계 문서화
- `Process/P3_프로토타입_제작/Documentation/prototype-overview.md`
  - 프로토타입 개요
  - 작동하는 기능 vs. 목업만 있는 기능
  - API 명세 (FastAPI 엔드포인트 추출)
  - 5개 평가 엔진 문서화

**검증 기준:**
- [x] 모든 목업 완료 (72개 HTML 페이지)
- [x] 데이터베이스 스키마 정의 (9개 테이블)
- [x] 핵심 워크플로우 작동 확인
- [x] 기술 스택 검증 완료
- [ ] P3 문서화 완료

**참조 파일:**
- `C:\ValueLink\Valuation_Company\valuation-platform\frontend\app\` (전체 폴더)
- `C:\ValueLink\Valuation_Company\valuation-platform\backend\create_tables.sql`
- `C:\ValueLink\Valuation_Company\valuation-platform\backend\app\services\valuation_engine\` (5개 엔진)

---

### S0: SAL Grid 생성

**목표:** Task 정의 및 JSON 구조 설정

**예상 Task 수:** 66개 정도 (분석 결과에 따라 변경될 수 있음)

**작업 내용:**

#### Step 1: 코드베이스 분석 및 Task 식별
- 기존 72개 HTML 페이지 분석
- 126개 Python 파일 분석
- 각 기능별로 필요한 작업 목록 추출
- Area별 그룹핑 (F, BA, S, BI, E, D, T, O, M, U, C)
- Stage별 배치 (S1-S5)
- Task ID 부여 (S{Stage}{Area}{Number})

**Task 분포 예시 (검토 결과에 따라 변경될 수 있음):**
```
S1 (개발 준비):
  - Database Migration 스크립트
  - Supabase/Vercel 설정
  - OAuth Provider 설정
  - CI/CD 파이프라인
  - TypeScript/ESLint 설정

S2 (Auth & Registration):
  - 로그인/회원가입 페이지
  - Auth API
  - 사용자 관리
  - 역할 기반 대시보드

S3 (평가 코어):
  - 프로젝트 워크플로우
  - 5개 평가 엔진 통합
  - 22개 AI 승인 포인트
  - 보고서 생성

S4 (플랫폼 기능):
  - 결제 시스템 (Stripe)
  - 관리자 패널
  - 랭킹 시스템
  - AI Avatar
  - 투자 매칭

S5 (마무리):
  - Production 배포
  - 모니터링/로깅
  - E2E 테스트
  - 보안 감사
  - 최종 문서화
```

**실제 Task 수는 분석 후 TASK_PLAN.md에 확정됨**

#### Step 2: Task Instructions 작성 (각 Task마다)
- `Process/S0_Project-SAL-Grid_생성/sal-grid/task-instructions/{TaskID}_instruction.md`
- Step 1에서 확정된 Task 수만큼 작성

**템플릿:**
```markdown
# {TaskID}: {Task Name}

## Task 정보
- Task ID: {TaskID}
- Task Name: {Task Name}
- Stage: S{N}
- Area: {Area}
- Dependencies: {선행 Task}

## 목표
{한 문장 목표}

## 상세 지시사항
1. {구체적 단계 1}
2. {구체적 단계 2}
...

## 기술 스택
- {언어/프레임워크 버전}

## 생성/수정 파일
- `{정확한 파일 경로}`

## 완료 기준
- [ ] {측정 가능한 기준 1}
- [ ] {측정 가능한 기준 2}

## 참조
- {디자인 목업}
- {API 문서}
```

#### Step 3: Verification Instructions 작성 (각 Task마다)
- `Process/S0_Project-SAL-Grid_생성/sal-grid/verification-instructions/{TaskID}_verification.md`
- Step 1에서 확정된 Task 수만큼 작성

#### Step 4: JSON 구조 설정
- `Process/S0_Project-SAL-Grid_생성/method/json/data/index.json`
```json
{
  "project_id": "valuelink-reconstruction",
  "project_name": "ValueLink Platform",
  "total_tasks": N,  // Step 1에서 확정된 수
  "task_ids": ["S1BI1", "S1BI2", "S1D1", ...]
}
```

- `Process/S0_Project-SAL-Grid_생성/method/json/data/grid_records/{TaskID}.json` (확정된 Task 수만큼)

- Viewer 테스트: `viewer/viewer_json.html` 접속 확인

**검증 기준:**
- [ ] 코드베이스 분석 완료 (72 HTML + 126 Python 파일)
- [ ] TASK_PLAN.md에 모든 Task 정의 완료
- [ ] 모든 Task Instruction 작성 완료
- [ ] 모든 Verification Instruction 작성 완료
- [ ] index.json에 모든 task_ids 등록
- [ ] grid_records/에 모든 JSON 파일 생성
- [ ] Viewer에서 정상 표시 확인
- [ ] 의존성 검증 통과 (역방향 의존성 없음)

---

### S1-S5: 개발 실행

**실행 패턴:**
```
각 Task마다:
  1. Task Instruction 읽기
  2. 실행 (task_agent 서브에이전트)
  3. task_status → "Executed"
  4. 검증 (verification_agent 서브에이전트)
  5. verification_status → "Verified"
  6. JSON 업데이트
  7. task_status → "Completed"

Stage 완료 시:
  8. Stage Gate 검증
  9. PO 승인
  10. 다음 Stage 진행
```

**Stage별 예상 Task 수 (검토 후 변경 가능):**
- S1: 13개 정도 (인프라 설정)
- S2: 18개 정도 (인증 시스템)
- S3: 15개 정도 (평가 엔진 통합)
- S4: 15개 정도 (플랫폼 기능)
- S5: 10개 정도 (배포 및 QA)

**S3 평가 엔진 마이그레이션 전략:**

**옵션 B (권장):** Python (FastAPI) 유지 + Edge Function 래퍼
- 장점: 기존 로직 보존, 빠른 배포
- 단점: 2개 런타임
- 이유: 가장 빠른 프로덕션 경로, 3,559줄 Python 코드 보존

**검증 기준 (각 Stage):**
- [ ] 모든 Task가 "Completed" 상태
- [ ] comprehensive_verification 모두 "Passed"
- [ ] Blocker 0개
- [ ] 전체 빌드 성공
- [ ] 전체 테스트 통과
- [ ] 의존성 체인 완결

**Stage Gate 리포트:**
- `Process/S0_Project-SAL-Grid_생성/sal-grid/stage-gates/S{N}GATE_verification_report.md`

---

## 위험 관리

### 위험 1: 기존 진행 상황 손실
**완화:**
- 모든 코드를 안전한 위치에 복사
- Git 브랜치 전략
- 작동하는 프로토타입 유지

### 위험 2: 불완전한 요구사항
**완화:**
- 코드를 문서로 활용 (역공학)
- AI로 기존 코드 분석
- 반복적 개선

### 위험 3: 의존성 충돌
**완화:**
- 의존성 시각화
- 정방향 규칙 엄격히 적용
- 자동 의존성 검사기

### 위험 4: SAL Grid 오버헤드
**완화:**
- Claude Code 자동화
- 템플릿 재사용
- 공통 작업 도구화

### 위험 5: 범위 확대
**완화:**
- 재구축 범위 동결
- 단계별 게이팅
- 공식 변경 통제
- MVP 집중

---

## 작업 복잡도

### 간단한 작업 (기존 자산 활용)
1. P1 사업계획 - 기획서에서 추출
2. P2 아키텍처 - ARCHITECTURE.md 복사
3. P2 데이터베이스 ERD - SQL에서 역공학
4. P3 Frontend - 72개 HTML 페이지 복사
5. P3 Database - SQL 파일 통합

### 복잡한 작업 (새로운 작업 필요)
1. P2 요구사항 - 126개 Python 파일 상세 분석
2. S0 코드베이스 분석 - Task 식별 및 정의
3. S0 Task Instructions - 각 Task마다 작성
4. S0 Verification Instructions - 각 Task마다 작성
5. S3 엔진 마이그레이션 - 5개 엔진 포팅/래핑
6. S4 플랫폼 기능 - 랭킹, AI Avatar, 매칭

---

## 핵심 참조 파일

| 파일 경로 | 용도 | 단계 |
|----------|------|------|
| `Valuation_Company/WHITE_PAPER_v1.0.md` | 전체 시스템 개요 | 전체 참조 |
| `Valuation_Company/플랫폼개발계획/valuation.ai.kr_홈페이지_개발계획서.md` | 사업 계획 | P1 |
| `Valuation_Company/valuation-platform/ARCHITECTURE.md` | 기술 스택 | P2 |
| `Valuation_Company/valuation-platform/backend/create_tables.sql` | DB 스키마 | P2, P3 |
| `Valuation_Company/valuation-platform/backend/app/services/valuation_orchestrator.py` | 워크플로우 로직 | P2 |
| `Valuation_Company/valuation-platform/backend/app/services/valuation_engine/*` | 5개 평가 엔진 | P1 IP, S3 |
| `Valuation_Company/valuation-platform/frontend/app/*` | 72개 HTML 페이지 | P2, P3 |
| `.claude/rules/*.md` | SAL Grid 규칙 | S0-S5 |
| `Process/S0_Project-SAL-Grid_생성/manual/PROJECT_SAL_GRID_MANUAL.md` | SAL Grid 매뉴얼 | S0-S5 |

---

## 성공 지표

- SAL Grid 준수: 100% (모든 Task가 22개 속성 형식)
- 문서화 커버리지: 100% (모든 Task가 Instruction 보유)
- 코드 재사용률: >80% (기존 엔진 보존)

---

## 다음 단계

1. **P0 완료:** Project_Directory_Structure.md 업데이트
2. **P1 시작:** Vision/Mission 문서 작성
3. **단계별 게이트:** 각 단계 완료 후 검증 및 승인

---

## 주요 권장사항

1. **보존, 재구축 아님:** 85% 완성도는 상당함 - 활용할 것
2. **기존 HTML을 목업으로 사용:** 디자인 작업 절약
3. **요구사항 역공학:** 코드가 가장 정확한 문서
4. **P3 이미 완료:** 조직화만 필요
5. **Python 엔진 유지:** 초기에는 포팅하지 말고 래핑
6. **SAL Grid 자동화:** JSON 업데이트에 Claude Code 사용
7. **단계별 검증:** 각 단계 완료 후 검증 및 승인

---

**작성자**: Claude Code
**버전**: 1.0
**최종 수정**: 2026-02-05
