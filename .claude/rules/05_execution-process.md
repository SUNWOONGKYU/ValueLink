# 05. 실행 프로세스 규칙

> Task 실행부터 PO 최종 승인까지 6단계 프로세스

---

## 전체 프로세스 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                      6단계 실행 프로세스                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [1단계] Task 실행 ─────────────── 서브에이전트                  │
│      ↓                                                          │
│  [2단계] PO 도움 요청 (필요 시) ─── AI → PO                      │
│      ↓                                                          │
│  [3단계] Task 검증 ─────────────── 서브에이전트                  │
│      ↓                                                          │
│  [4단계] Stage Gate 검증 ───────── Main Agent                   │
│      ↓                                                          │
│  [5단계] PO 테스트 가이드 제공 ─── Main Agent → PO              │
│      ↓                                                          │
│  [6단계] PO 최종 승인 ──────────── PO                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1단계: Task 실행

**수행자:** Task Agent 서브에이전트

```
Main Agent → Task Agent 서브에이전트 투입 (Task tool 사용)
           → 서브에이전트가 작업 수행
           → 결과 반환
           → Main Agent가 Grid에 기록 (#10-13)
```

**기록 항목:**
- #10 task_agent: 사용된 Agent
- #11 generated_files: 생성된 파일 목록
- #12 duration: 소요 시간
- #13 build_result: 빌드 결과

**금지:**
- ❌ Main Agent가 직접 Task 작업 수행
- ❌ Task Agent가 검증까지 수행

---

## 2단계: PO 도움 요청 (필요 시)

**수행자:** AI → PO

**요청이 필요한 상황:**
- 외부 서비스 API 키 필요 (Resend, Stripe, OpenAI 등)
- OAuth Provider 설정 필요 (Google, GitHub, Kakao 등)
- 환경 변수 설정 필요 (Vercel, DB 등)
- 외부 대시보드 접속 필요

**요청 형식:**
```
"이 기능을 구현하려면 [설정 항목]이 필요합니다.

필요한 설정:
1. [설정 단계 1]
2. [설정 단계 2]
3. [설정 단계 3]

설정 완료 후 알려주시면 진행하겠습니다."
```

**금지:**
- ❌ 작업 완료 후에야 "설정 필요합니다" 알림
- ❌ 테스트 시점에 "설정해야 해요" 발언
- ❌ 외부 설정 필요한데 코드만 작성하고 "완료" 보고

---

## 3단계: Task 검증

**수행자:** Verification Agent 서브에이전트

```
Main Agent → Verification Agent 서브에이전트 투입 (Task tool 사용)
           → 서브에이전트가 검증 수행
           → 결과 반환
           → Main Agent가 Grid에 기록 (#16-21)
```

**기록 항목:**
- #16 test_result: 테스트 결과
- #17 build_verification: 빌드 검증
- #18 integration_verification: 통합 검증
- #19 blockers: 차단 요소
- #20 comprehensive_verification: 종합 검증
- #21 ai_verification_note: AI 검증 의견

**핵심 원칙:** Task Agent ≠ Verification Agent

---

## 4단계: Stage Gate 검증

**수행자:** Main Agent (직접 수행)

```
Main Agent가 직접 검증:
    → Stage 내 모든 Task 완료 확인
    → 전체 빌드/테스트 통과 확인
    → 의존성 체인 완결성 확인
    → 검증 리포트 생성
```

**리포트 저장:**
- 위치: `S0_Project-SAL-Grid_생성/sal-grid/stage-gates/`
- 파일명: `S{N}GATE_verification_report.md`

**JSON 기록:**
- JSON 파일의 `stage_gate_status` 필드 업데이트
- 검증 관련 필드 업데이트

---

## 5단계: PO 테스트 가이드 제공

**수행자:** Main Agent → PO

**제공 항목:**

### 1) 테스트 가능 조건
```
- 필요한 외부 설정: [완료/미완료]
- 서버 실행 필요 여부: [예/아니오]
- 환경 변수 설정: [완료/미완료]
```

### 2) 기능별 테스트 가이드
```
[기능 1: Google 로그인]
- 테스트 파일: Production/Frontend/pages/auth/google-login.html
- 테스트 방법: 브라우저에서 열고 버튼 클릭
- 예상 결과: Google 로그인 페이지로 이동
- 필요 설정: OAuth Provider 활성화 ✅
```

### 3) 설정 완료 체크리스트
```
- [ ] Google OAuth 설정 완료
- [ ] Resend API 키 설정 완료
- [ ] 환경 변수 배포 완료
```

**금지:**
- ❌ AI 검증만 하고 "Stage Gate 통과" 선언
- ❌ 테스트 방법 없이 "확인해보세요" 요청

---

## 6단계: PO 최종 승인

**수행자:** PO

```
PO가 수행:
    → AI 검증 리포트 검토
    → 테스트 가이드 따라 직접 테스트
    → 기능 정상 작동 확인
    → 승인 또는 거부
```

**결과:**
- 승인: `stage_gate_status: 'Approved'`
- 거부: `stage_gate_status: 'Rejected'` + 사유

---

## 요약표

| 단계 | 수행자 | 내용 | 기록 위치 |
|------|--------|------|----------|
| 1 | 서브에이전트 | Task 실행 | Grid #10-13 |
| 2 | AI → PO | 외부 설정 요청 | - |
| 3 | 서브에이전트 | Task 검증 | Grid #16-21 |
| 4 | Main Agent | Stage Gate 검증 | stage-gates/ |
| 5 | Main Agent → PO | 테스트 가이드 | - |
| 6 | PO | 최종 승인 | CSV stage_gate_status |

---

## 체크리스트

- [ ] Task 실행을 서브에이전트에게 위임했는가?
- [ ] PO 도움이 필요하면 작업 전에 요청했는가?
- [ ] Task 검증을 다른 서브에이전트에게 위임했는가?
- [ ] Stage Gate 검증 리포트를 생성했는가?
- [ ] PO 테스트 가이드를 제공했는가?
- [ ] PO 승인을 받았는가?
