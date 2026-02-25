# S5M2 Verification Instruction

## Task 정보
- **Task ID**: S5M2
- **Task Name**: 코드 품질 및 가독성 향상
- **Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 파일 생성 확인

- [ ] `Process/S5_개발_마무리/Documentation/docs/code-style-guide.md` 존재
- [ ] `Process/S5_개발_마무리/Documentation/docs/user-guide-enhanced.md` 존재
- [ ] `Process/S5_개발_마무리/Documentation/docs/sample-datasets.md` 존재
- [ ] 총 3개 파일 생성 확인

---

### 2. 코드 스타일 가이드 검증

#### 2.1 문서 구조
- [ ] 6개 주요 섹션 존재
  1. 파일 헤더 주석
  2. 변수명 규칙
  3. 함수 주석
  4. 파일 구조 규칙
  5. TypeScript 타입 규칙
  6. 에러 처리 규칙

#### 2.2 각 섹션 내용
- [ ] **변수명 규칙**: camelCase, PascalCase, UPPER_SNAKE_CASE 예시
- [ ] **함수 주석**: JSDoc 형식 예시, 복잡한 로직에만 주석 원칙
- [ ] **파일 구조**: import 순서 (React → 외부 → 내부 → 타입 → 스타일)
- [ ] **타입 규칙**: any 금지, 명시적 타입 선언
- [ ] **에러 처리**: try-catch 필수 (async 함수)

#### 2.3 코드 예시 품질
- [ ] 모든 섹션에 ✅ Good / ❌ Bad 예시 포함
- [ ] 코드 예시 문법 오류 없음
- [ ] 실행 가능한 코드 (복사-붙여넣기 가능)

**검증 방법:**
```bash
# Markdown 렌더링 확인
cat docs/code-style-guide.md | grep "## [1-6]"

# 예상 결과
## 1. 파일 헤더 주석
## 2. 변수명 규칙
## 3. 함수 주석
## 4. 파일 구조 규칙
## 5. TypeScript 타입 규칙
## 6. 에러 처리 규칙
```

---

### 3. 향상된 사용자 가이드 검증

#### 3.1 문서 구조
- [ ] 3개 주요 섹션 존재
  1. 14단계 워크플로우 상세 가이드
  2. 자주 묻는 질문 (FAQ)
  3. 문제 해결 가이드

#### 3.2 14단계 워크플로우 가이드
- [ ] 14개 Step 모두 설명 (Step 1-14)
- [ ] 각 Step마다 다음 정보 포함:
  - 목적
  - 필수 정보/필드
  - 화면 예시 (ASCII 다이어그램 또는 스크린샷)
  - 다음 단계

#### 3.3 FAQ
- [ ] 10개 이상의 FAQ
- [ ] 표 형식으로 정리된 비교 (평가 방법, 평가 기간 등)
- [ ] 실용적인 답변 (구체적 예시 포함)

#### 3.4 문제 해결 가이드
- [ ] 5개 이상의 일반적인 문제
- [ ] 각 문제마다 해결 방법 단계별 제시

**검증 방법:**
```markdown
# user-guide-enhanced.md 확인

## 1. 14단계 워크플로우 상세 가이드

### Step 1: 평가 의뢰 생성
**목적**: ...
**필수 정보**: ...
**화면 예시**: ...

### Step 2: 견적 제시
...

## 2. 자주 묻는 질문 (FAQ)

### Q1: 평가 방법을 어떻게 선택해야 하나요?
**A**: ...

| 평가 방법 | 적합한 경우 | 예시 |
|----------|------------|------|
...

## 3. 문제 해결 가이드

### 문제 1: "견적이 너무 높아요"
**해결 방법**:
1. ...
2. ...
```

---

### 4. 샘플 데이터 세트 검증

#### 4.1 문서 구조
- [ ] 3개 산업별 샘플 데이터
  1. IT 스타트업 (DCF 평가)
  2. 제조업 (Relative 평가)
  3. 부동산 (Asset 평가)

#### 4.2 각 샘플 내용
- [ ] **회사 정보**: 회사명, 산업, 매출, 성장률, 직원수
- [ ] **재무 데이터**: JSON 형식 템플릿
- [ ] **계산 과정**: 단계별 설명 (5단계 이상)
- [ ] **결론**: 최종 평가 금액

#### 4.3 DCF 계산 과정 상세성
- [ ] Step 1: 5년 매출 예측
- [ ] Step 2: FCF 계산 (EBIT, NOPAT, CapEx, NWC)
- [ ] Step 3: DCF 현재가치 할인
- [ ] Step 4: Terminal Value 계산
- [ ] Step 5: 기업가치 & 주주가치

**검증 방법:**
```markdown
# sample-datasets.md 확인

## 1. IT 스타트업 (DCF 평가)

### 회사 정보
- **회사명**: 테크이노 주식회사
- **산업**: IT - 인공지능
- **매출**: 50억원

### 재무 데이터
```json
{
  "revenue_current": 5000000000,
  "growth_rate": 0.3,
  "wacc": 0.15,
  ...
}
```

### DCF 계산 과정

#### Step 1: 5년 매출 예측
Year 1: 50억 × (1 + 0.3) = 65억
...

#### Step 5: 기업가치 & 주주가치
Enterprise Value = 91.4억
Equity Value = 96.4억
```

---

### 5. 내부 링크 검증

- [ ] 문서 간 상호 참조 링크 작동
- [ ] 목차 (TOC) 링크 작동
- [ ] 코드 예시 링크 작동

**검증 방법:**
```bash
# 깨진 링크 확인
grep -r "\[.*\](.*)" docs/*.md | grep -v "http"
```

---

### 6. Markdown 문법 검증

- [ ] 헤더 레벨 일관성 (# → ## → ###)
- [ ] 코드 블록 언어 명시 (```typescript, ```json)
- [ ] 표 형식 정확 (|로 구분)
- [ ] 리스트 일관성 (-, *, 1.)

**검증 방법:**
```bash
# Markdown 렌더링 테스트 (VS Code Markdown Preview)
# 또는 markdownlint 실행
npx markdownlint docs/code-style-guide.md
npx markdownlint docs/user-guide-enhanced.md
npx markdownlint docs/sample-datasets.md
```

---

### 7. 코드 예시 실행 가능성 검증

#### 7.1 TypeScript 예시
- [ ] 모든 TypeScript 코드 예시 문법 오류 없음
- [ ] import 문 정확
- [ ] 타입 정의 정확

**검증 방법:**
```bash
# 코드 예시 추출 후 타입 체크
# (수동: 코드 예시를 임시 .ts 파일로 복사 후 tsc 실행)
```

#### 7.2 JSON 예시
- [ ] 모든 JSON 예시 문법 오류 없음
- [ ] 중괄호, 쉼표 올바름

**검증 방법:**
```bash
# JSON 유효성 검증
# (수동: JSON 예시를 jq로 파싱 가능한지 확인)
echo '{"revenue_current": 5000000000}' | jq .
```

---

### 8. 문서 길이 및 완성도

- [ ] `code-style-guide.md`: 최소 300줄
- [ ] `user-guide-enhanced.md`: 최소 400줄
- [ ] `sample-datasets.md`: 최소 300줄

**검증 방법:**
```bash
wc -l docs/code-style-guide.md
wc -l docs/user-guide-enhanced.md
wc -l docs/sample-datasets.md
```

---

## 검증 결과 기록 형식

### Test Result
```json
{
  "unit_test": "PASS/FAIL - 코드 스타일 가이드 6개 섹션 완성",
  "integration_test": "PASS/FAIL - 사용자 가이드 14단계 + FAQ + 문제 해결",
  "edge_cases": "PASS/FAIL - 샘플 데이터 3개 산업, DCF 계산 과정",
  "manual_test": "PASS/FAIL - Markdown 렌더링, 링크 작동"
}
```

### Build Verification
```json
{
  "compile": "PASS/FAIL - Markdown 문법 검증",
  "lint": "PASS/FAIL - markdownlint 0 warnings",
  "deploy": "N/A - Documentation",
  "runtime": "N/A - Documentation"
}
```

### Integration Verification
```json
{
  "dependency_propagation": "PASS/FAIL - S5M1 문서 확장",
  "cross_task_connection": "PASS/FAIL - S5T1, S5T2 참조",
  "data_flow": "PASS/FAIL - 샘플 데이터 → 계산 과정 → 결론"
}
```

### Blockers
```json
{
  "dependency": "None/WARNING - 설명",
  "environment": "None/WARNING - 설명",
  "external_api": "None/WARNING - 설명",
  "status": "No Blockers / N Blockers"
}
```

### Comprehensive Verification
```json
{
  "task_instruction": "PASS/FAIL - 3개 파일 생성",
  "test": "PASS/FAIL - 6개 섹션, 14단계, 3개 샘플",
  "build": "PASS/FAIL - Markdown 문법, markdownlint",
  "integration": "PASS/FAIL - 내부 링크, 코드 예시 실행 가능",
  "blockers": "None/N개",
  "final": "Verified / Needs Fix"
}
```

---

## PO 테스트 가이드

### 테스트 전 준비
1. VS Code Markdown Preview 확장 설치
2. 문서 파일 열기

### 테스트 시나리오

#### 시나리오 1: 코드 스타일 가이드 확인
1. `docs/code-style-guide.md` 열기
2. Markdown Preview 실행 (Ctrl+Shift+V)
3. 6개 섹션 목차 확인
4. 각 섹션 ✅ Good / ❌ Bad 예시 확인
5. 코드 예시 복사 → 임시 .ts 파일에 붙여넣기 → 타입 체크

**예상 결과**: 모든 코드 예시 실행 가능 ✅

#### 시나리오 2: 사용자 가이드 확인
1. `docs/user-guide-enhanced.md` 열기
2. Markdown Preview 실행
3. 14단계 워크플로우 각 단계 읽기
4. FAQ 10개 이상 확인
5. 문제 해결 가이드 5개 이상 확인

**예상 결과**: 모든 단계 명확하게 설명됨 ✅

#### 시나리오 3: 샘플 데이터 확인
1. `docs/sample-datasets.md` 열기
2. Markdown Preview 실행
3. IT 스타트업 DCF 계산 과정 읽기
4. JSON 데이터 복사 → jq로 유효성 검증
5. 계산 과정 수동 검증 (계산기 사용)

**예상 결과**: 모든 계산 과정 정확함 ✅

---

## 승인 기준

- ✅ 3개 파일 생성 완료
- ✅ 코드 스타일 가이드 6개 섹션 완성
- ✅ 사용자 가이드 14단계 + FAQ + 문제 해결
- ✅ 샘플 데이터 3개 산업, DCF 계산 과정
- ✅ Markdown 문법 오류 없음
- ✅ 코드 예시 실행 가능
- ✅ JSON 예시 유효
- ✅ 내부 링크 작동
- ✅ 문서 길이 충분 (총 1,000줄 이상)

**최종 판정**: Verified / Needs Fix

---

**작성자**: Main Agent
**작성일**: 2026-02-23
**버전**: 1.0
