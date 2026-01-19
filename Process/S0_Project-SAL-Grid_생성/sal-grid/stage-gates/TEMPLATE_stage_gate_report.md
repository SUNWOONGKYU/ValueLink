# Stage Gate Verification Report Template

---

## 📌 필수 참조 규칙 파일 (2025-12-19)

> **⚠️ Stage Gate 검증 전 반드시 확인하세요!**

| 규칙 파일 | 내용 | 용도 |
|----------|------|------|
| `.claude/rules/05_execution-process.md` | 6단계 실행 프로세스 | Stage Gate 검증 절차 |
| `.claude/rules/06_verification.md` | Stage Gate 검증 기준 | **핵심 참조** |

---

## Stage Gate 검증 리포트 - S{N}GATE

> **Stage**: Stage {N} - {Stage Name}
> **검증자**: Main Agent (Claude Code)
> **검증일**: YYYY-MM-DD

---

## 1. Stage 완료 현황

### 1.1 Task 완료 상태

| Task ID | Task Name | Task Status | Verification Status |
|---------|-----------|-------------|---------------------|
| S{N}M1 | ... | Completed | Passed |
| S{N}F1 | ... | Completed | Passed |
| ... | ... | ... | ... |

**완료율**: {완료 Task 수}/{전체 Task 수} (100%)

### 1.2 미완료 Task (있을 경우)

```
없음 (모든 Task 완료)
```

---

## 2. 빌드 검증

### 2.1 빌드 결과

```
✅ 빌드 성공
- 빌드 도구: npm run build
- 빌드 시간: XX초
- 번들 크기: XXX KB
- 오류: 0개
- 경고: 0개
```

### 2.2 린트 검사

```
✅ ESLint 통과
- 오류: 0개
- 경고: 0개
```

---

## 3. 테스트 검증

### 3.1 단위 테스트

```
✅ Unit Tests: XX/XX passed
- 테스트 파일: XX개
- 테스트 케이스: XX개
- 커버리지: XX%
```

### 3.2 통합 테스트

```
✅ Integration Tests: XX/XX passed
- API 연동: ✅
- DB 연동: ✅
```

### 3.3 E2E 테스트

```
✅ E2E Tests: XX/XX passed
- 주요 플로우: ✅
```

---

## 4. 의존성 체인 검증

### 4.1 Task 간 의존성

```
✅ 모든 의존성 체인 완결
- 순환 의존성: 없음
- 미해결 의존성: 없음
```

### 4.2 외부 의존성

```
✅ 외부 패키지 검증 완료
- 보안 취약점: 0개
- 업데이트 필요: 0개
```

---

## 5. 산출물 검증

### 5.1 필수 산출물 확인

| 산출물 | 상태 | 비고 |
|--------|------|------|
| 문서화 | ✅ | 요구사항, API 명세 등 |
| 코드 | ✅ | Frontend, Backend, DB |
| 테스트 | ✅ | Unit, Integration, E2E |
| 설정 파일 | ✅ | 환경변수, 배포 설정 |

### 5.2 Generated Files 확인

```
총 XX개 파일 생성됨
- Documentation: XX개
- Frontend: XX개
- Backend: XX개
- Database: XX개
```

---

## 6. 블로커 확인

```
✅ 블로커 없음

- 의존성 블로커: 없음
- 환경 설정 블로커: 없음
- 외부 API 블로커: 없음
```

---

## 7. 종합 판정

### 7.1 체크리스트

- [x] Stage 내 모든 핵심 Task 완료
- [x] 전체 빌드 성공
- [x] 통합 테스트 통과
- [x] 의존성 체인 완결성
- [x] 산출물 완성도
- [x] 문서화 완료
- [x] 블로커 없음

### 7.2 최종 판정

```
┌─────────────────────────────────────────────┐
│  ✅ Stage {N} Gate - AI 검증 통과           │
│                                             │
│  - 모든 검증 항목 통과                      │
│  - 다음 Stage 진행 가능                     │
│  - Project Owner 최종 승인 대기             │
└─────────────────────────────────────────────┘
```

---

## 8. 다음 Stage 준비 상태

### 8.1 준비 완료 항목

- ✅ Stage {N+1} Task Instruction 확인
- ✅ 필요한 환경 설정 완료
- ✅ 의존성 데이터 준비됨

### 8.2 참고 사항

```
- (다음 Stage 작업 시 참고할 사항 기록)
```

---

**검증 완료**: Main Agent (Claude Code)
**검증일시**: YYYY-MM-DD HH:MM:SS
**다음 단계**: Project Owner 수동 검증 대기
