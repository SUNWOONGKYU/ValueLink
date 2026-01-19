# 06. 검증 규칙

> Task 검증, Stage Gate 검증, PO 승인 기준

---

## 0. 상태 전이 규칙 (Status Transition Rules) ⭐ NEW

### task_status (작업 상태)

| 상태 | 설명 | 전이 조건 |
|------|------|----------|
| **Pending** | 작업 시작 전 | 초기 상태 |
| **In Progress** | 작업 진행 중 | Pending → In Progress (작업 시작) |
| **Executed** | 파일 생성 완료 | In Progress → Executed (파일 생성 완료) |
| **Completed** | 모든 과정 완료 | Executed → Completed (검증 통과 + 수정 반영) |

### verification_status (검증 상태)

| 상태 | 설명 | 전이 조건 |
|------|------|----------|
| **Not Verified** | 검증 시작 전 | 초기 상태 |
| **In Review** | 검증 진행 중 | Not Verified → In Review (검증 시작) |
| **Needs Fix** | 수정 필요 | In Review → Needs Fix (이슈 발견) |
| **Verified** | 검증 통과 | In Review → Verified (통과) 또는 Needs Fix → Verified (수정 후 재검증 통과) |

### 상태 조합표

```
┌─────────────────┬──────────────────┬───────────────────┬─────────────┐
│ task_status     │ verification_    │ fixes_required    │ 의미        │
│                 │ status           │                   │             │
├─────────────────┼──────────────────┼───────────────────┼─────────────┤
│ Pending         │ Not Verified     │ false             │ 시작 전      │
│ In Progress     │ Not Verified     │ false             │ 작업 중      │
│ Executed        │ Not Verified     │ false             │ 파일 완료    │
│ Executed        │ In Review        │ false             │ 검증 중      │
│ Executed        │ Needs Fix        │ true              │ 수정 필요    │
│ Executed        │ Verified         │ false             │ 검증 통과    │
│ Completed       │ Verified         │ false             │ 최종 완료    │
└─────────────────┴──────────────────┴───────────────────┴─────────────┘
```

### ⛔ 완료 조건 (CRITICAL)

**Completed로 변경하려면:**
1. `verification_status`가 `Verified`여야 함
2. [16-19] Verification Execution 필드가 모두 채워져 있어야 함
3. `comprehensive_verification`이 `Passed`여야 함

**CSV 업데이트 시 검증:**
- `task_status`를 `Completed`로 변경 전 반드시 `verification_status`가 `Verified`인지 확인
- 이 규칙을 지키지 않으면 데이터 무결성 문제 발생

---

## 1. Task 검증 항목

### Test Result (#16)
| 항목 | 설명 | 기준 |
|------|------|------|
| unit_test | 단위 테스트 | 모든 함수/컴포넌트 테스트 |
| integration_test | 통합 테스트 | API 연동, DB 연동 테스트 |
| edge_cases | 엣지 케이스 | 예외 상황 처리 테스트 |
| manual_test | 수동 테스트 | UI/UX 직접 확인 |

### Build Verification (#17)
| 항목 | 설명 | 기준 |
|------|------|------|
| compile | 컴파일 | 에러 없이 빌드 완료 |
| lint | 린트 | ESLint 에러 0개 |
| deploy | 배포 | Vercel 배포 성공 |
| runtime | 런타임 | 실행 시 에러 없음 |

### Integration Verification (#18)
| 항목 | 설명 | 기준 |
|------|------|------|
| dependency_propagation | 의존성 전파 | 선행 Task 결과 정상 사용 |
| cross_task_connection | Task 간 연결 | 다른 Task와 충돌 없음 |
| data_flow | 데이터 흐름 | 입출력 데이터 정상 |

### Blockers (#19)
| 항목 | 설명 | 확인 사항 |
|------|------|----------|
| dependency | 의존성 차단 | 선행 Task 미완료 |
| environment | 환경 차단 | 설정/키 미설정 |
| external_api | 외부 API 차단 | API 오류/제한 |

---

## 2. Stage Gate 검증 기준

### 필수 확인 항목

```
[Stage Gate 체크리스트]

□ Stage 내 모든 Task가 '완료' 상태인가?
□ 모든 Task의 comprehensive_verification이 'Passed'인가?
□ Blocker가 0개인가?
□ 전체 빌드가 성공하는가?
□ 전체 테스트가 통과하는가?
□ 의존성 체인이 완결되었는가?
```

### 검증 리포트 형식

```markdown
# S{N} Stage Gate Verification Report

## 1. Task 완료 현황
| Task ID | Task Name | Status | Verification |
|---------|-----------|--------|--------------|
| S2F1 | Google 로그인 UI | ✅ 완료 | ✅ Passed |
| S2BA1 | 구독 취소 API | ✅ 완료 | ✅ Passed |
| ... | ... | ... | ... |

## 2. 빌드/테스트 결과
- 전체 빌드: ✅ 성공
- 단위 테스트: 24/24 통과
- 통합 테스트: 5/5 통과

## 3. Blockers
- 없음 ✅

## 4. AI 검증 의견
[종합 의견 작성]

## 5. PO 테스트 가이드
[테스트 방법 안내]
```

### 리포트 저장 위치

```
S0_Project-SAL-Grid_생성/sal-grid/stage-gates/
├── S1GATE_verification_report.md
├── S2GATE_verification_report.md
├── S3GATE_verification_report.md
├── S4GATE_verification_report.md
└── S5GATE_verification_report.md
```

---

## 3. PO 테스트 가이드 형식

### 필수 포함 항목

```markdown
## PO 테스트 가이드

### 1. 테스트 전 확인사항
- [ ] 외부 서비스 설정 완료
- [ ] 환경 변수 설정 완료
- [ ] 로컬 서버 실행 (필요 시)

### 2. 기능별 테스트

#### [기능 1: 기능명]
- **파일 위치:** `Production/Frontend/pages/...`
- **테스트 방법:**
  1. 브라우저에서 파일 열기
  2. [버튼/링크] 클릭
  3. [동작] 확인
- **예상 결과:** [정상 동작 설명]
- **필요 설정:** [설정 항목] ✅/❌

#### [기능 2: 기능명]
...

### 3. 테스트 결과 기록
| 기능 | 테스트 결과 | 비고 |
|------|------------|------|
| 기능1 | ✅/❌ | |
| 기능2 | ✅/❌ | |
```

---

## 4. Human-AI Task 검증

### Human-AI Task란?
- `execution_type: 'Human-AI'` 또는 `'Human-Assisted'`
- AI가 혼자 완료할 수 없고 PO의 직접 작업이 필요한 Task

### 완료 기준

| 단계 | 수행자 | 필수 여부 |
|------|--------|----------|
| 1. 설정 가이드 작성 | AI | ✅ |
| 2. PO에게 설정 요청 | AI | ✅ |
| 3. 외부 서비스 설정 | **PO** | ✅ 필수 |
| 4. 설정 완료 확인 | AI + PO | ✅ |
| 5. **실제 작동 테스트** | AI + PO | ✅ 필수 |
| 6. 테스트 성공 시 "완료" | AI | ✅ |

**금지:**
- ❌ 가이드 문서만 작성하고 "완료" 처리
- ❌ 실제 작동 테스트 없이 Task 완료

---

## 5. 최종 승인 프로세스

```
┌─────────────────────────────────────────────────────────────────┐
│                        최종 승인 프로세스                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AI 검증 완료                                                    │
│      ↓                                                          │
│  PO 테스트 가이드 제공                                           │
│      ↓                                                          │
│  PO 직접 테스트 수행                                             │
│      ↓                                                          │
│  ┌─────────────┐                                                │
│  │ 테스트 통과? │                                                │
│  └──────┬──────┘                                                │
│         │                                                       │
│    Yes  │  No                                                   │
│    ↓    ↓                                                       │
│  승인   거부 + 사유                                              │
│    ↓    ↓                                                       │
│  다음   문제 해결 후                                             │
│  Stage  재테스트                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 체크리스트

### Task 검증
- [ ] unit_test 결과가 있는가?
- [ ] build 결과가 성공인가?
- [ ] blockers가 없는가?
- [ ] comprehensive_verification이 Passed인가?

### Stage Gate 검증
- [ ] 모든 Task가 완료 상태인가?
- [ ] 검증 리포트를 생성했는가?
- [ ] PO 테스트 가이드를 작성했는가?

### PO 승인
- [ ] PO가 직접 테스트했는가?
- [ ] 모든 기능이 정상 작동하는가?
- [ ] 승인/거부 결정을 받았는가?
