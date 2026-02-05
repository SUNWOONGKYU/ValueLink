# S1M2 Verification

## 검증 대상

- **Task ID**: S1M2
- **Task Name**: 개발 워크플로우 가이드 작성
- **Stage**: S1 (Development Setup - 개발 준비)
- **Area**: M (Documentation)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 파일 생성 확인

#### 1.1 문서 파일 존재

- [ ] **`docs/development-guide.md` 파일 존재**
  - 명령어: `ls docs/development-guide.md`
  - 파일 크기: ~500줄 예상

- [ ] **`docs/coding-standards.md` 파일 존재**
  - 명령어: `ls docs/coding-standards.md`
  - 파일 크기: ~400줄 예상

---

### 2. 개발 워크플로우 가이드 내용 검증 (`development-guide.md`)

#### 2.1 Git 전략 섹션 확인

- [ ] **브랜치 전략 다이어그램 포함**
  - `main` (프로덕션)
  - `develop` (개발 통합)
  - `feature/*` (기능 개발)
  - `hotfix/*` (긴급 수정)

#### 2.2 브랜치 명명 규칙 확인

- [ ] **Feature 브랜치 명명 규칙**
  - 형식: `task/{TaskID}-{간단한-설명}`
  - 예시: `task/S2F1-valuation-results-pages`

- [ ] **Hotfix 브랜치 명명 규칙**
  - 형식: `hotfix/{issue-번호}-{간단한-설명}`
  - 예시: `hotfix/issue-42-login-error`

#### 2.3 Commit 메시지 규칙 확인

- [ ] **Conventional Commits 형식**
  - 형식: `<type>(<TaskID>): <subject>`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

- [ ] **좋은 예시 포함**
  ```
  feat(S2F1): 평가 결과 페이지 템플릿 구현

  - 공통 템플릿 컴포넌트 생성
  - 5개 평가 방법별 페이지 구현
  - Recharts 그래프 통합

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

- [ ] **나쁜 예시 포함**
  - `❌ update files`
  - `❌ fixed bug`
  - `❌ WIP`

#### 2.4 Pull Request 프로세스 확인

- [ ] **PR 프로세스 6단계 문서화**
  1. Feature 브랜치 생성
  2. 작업 및 커밋
  3. Push 및 PR 생성
  4. PR 템플릿 작성
  5. Code Review
  6. Merge

- [ ] **PR 템플릿 포함**
  - Task 정보
  - 변경 사항
  - 테스트
  - 스크린샷 (UI 변경 시)
  - 관련 Task
  - 검토 요청사항

- [ ] **리뷰어 체크리스트 포함**
  - 코드가 Task Instruction 따르는가?
  - TypeScript 타입 올바른가?
  - 에러 처리 적절한가?
  - 테스트 통과하는가?
  - 보안 이슈 없는가?
  - 성능 이슈 없는가?
  - 문서화 적절한가?

#### 2.5 CI/CD 파이프라인 확인

- [ ] **GitHub Actions Workflow 예시 포함**
  - `on: pull_request, push`
  - Jobs: `test` (TypeScript, ESLint, Test, Build)

#### 2.6 환경 분리 확인

- [ ] **3개 환경 정의**
  | 환경 | 브랜치 | URL | 용도 |
  |------|--------|-----|------|
  | Production | main | valuation.ai.kr | 실서비스 |
  | Staging | develop | staging.valuation.ai.kr | 통합 테스트 |
  | Local | feature/* | localhost:3000 | 개발 |

#### 2.7 Hotfix 프로세스 확인

- [ ] **Hotfix 프로세스 문서화**
  - main에서 hotfix 브랜치 생성
  - 수정 및 커밋
  - main과 develop 모두에 merge
  - hotfix 브랜치 삭제

#### 2.8 배포 프로세스 확인

- [ ] **Develop → Staging 자동 배포**
  - develop 브랜치 push 시 자동 배포

- [ ] **Main → Production 배포**
  - Release PR 생성
  - Tag 생성 (`v1.0.0`)
  - 자동 배포

#### 2.9 Rollback 절차 확인

- [ ] **Rollback 절차 문서화**
  - 이전 태그로 체크아웃
  - Force push to main
  - Vercel 자동 롤백

---

### 3. 코딩 표준 가이드 내용 검증 (`coding-standards.md`)

#### 3.1 TypeScript 명명 규칙 확인

- [ ] **변수/함수: camelCase**
  - 예시: `const userName = 'John'`

- [ ] **타입/인터페이스: PascalCase**
  - 예시: `interface ProjectData { }`

- [ ] **상수: UPPER_SNAKE_CASE**
  - 예시: `const MAX_RETRY_COUNT = 3`

- [ ] **Private 멤버: _prefix**
  - 예시: `private _internalCache`

#### 3.2 파일 구조 확인

- [ ] **폴더 구조 정의**
  ```
  src/
  ├── app/
  ├── components/
  │   ├── ui/
  │   └── features/
  ├── lib/
  ├── types/
  └── hooks/
  ```

#### 3.3 Import 순서 확인

- [ ] **Import 순서 5단계 정의**
  1. React / Next.js
  2. 외부 라이브러리
  3. 내부 모듈
  4. 타입
  5. 스타일

#### 3.4 함수 작성 규칙 확인

- [ ] **함수는 한 가지 일만 수행**
  - 좋은 예시 / 나쁜 예시 포함

- [ ] **함수는 짧게 (20줄 이하 권장)**
  - 가이드라인 제시

- [ ] **조기 반환 (Early Return) 패턴**
  - 좋은 예시 / 나쁜 예시 포함

#### 3.5 타입 안전성 확인

- [ ] **`any` 사용 금지**
  - 좋은 예시 / 나쁜 예시 포함

- [ ] **Optional Chaining 사용**
  - 좋은 예시: `user?.profile?.name ?? 'Unknown'`

#### 3.6 에러 처리 확인

- [ ] **Try-Catch 사용 예시**
  - async 함수 에러 처리

- [ ] **에러 타입 지정**
  - `if (error instanceof Error)` 패턴

#### 3.7 React 컴포넌트 규칙 확인

- [ ] **함수형 컴포넌트 사용**
  - 좋은 예시 / 나쁜 예시 (클래스 컴포넌트 금지)

- [ ] **Props 타입 정의**
  - Interface 사용 예시

#### 3.8 주석 작성 확인

- [ ] **JSDoc 주석 예시**
  - 함수 설명, 파라미터, 반환값, 예외

- [ ] **TODO 주석 형식**
  - `// TODO(S3BA3): ...` 형식

#### 3.9 ESLint 설정 확인

- [ ] **`.eslintrc.json` 설정 예시**
  - `@typescript-eslint/no-explicit-any: error`
  - `@typescript-eslint/no-unused-vars: error`
  - `prefer-const: error`
  - `no-console: warn`

#### 3.10 Prettier 설정 확인

- [ ] **`.prettierrc` 설정 예시**
  - `semi: false`
  - `singleQuote: true`
  - `tabWidth: 2`
  - `trailingComma: es5`
  - `printWidth: 80`

#### 3.11 테스트 작성 규칙 확인

- [ ] **테스트 파일 위치**
  - 같은 폴더에 `.test.tsx` 파일

- [ ] **테스트 작성 예시**
  - Jest + React Testing Library 예시

---

### 4. 문서 품질 검증

#### 4.1 Markdown 문법 검증

- [ ] **Markdown Linter 통과**
  - 도구: `markdownlint`
  - 문법 에러 없음 확인

#### 4.2 코드 블록 하이라이팅

- [ ] **TypeScript 코드 블록**
  - ```typescript ... ``` 형식 사용

- [ ] **bash 코드 블록**
  - ```bash ... ``` 형식 사용

- [ ] **JSON 코드 블록**
  - ```json ... ``` 형식 사용

#### 4.3 표(Table) 형식 확인

- [ ] **표가 올바르게 렌더링**
  - 환경 분리 테이블
  - 명명 규칙 테이블

#### 4.4 다이어그램 확인

- [ ] **브랜치 전략 다이어그램**
  - ASCII 또는 Mermaid 형식

---

### 5. 문서 완성도 검증

#### 5.1 모든 필수 섹션 포함

**development-guide.md 필수 섹션**:
- [ ] Git 전략
- [ ] 브랜치 명명 규칙
- [ ] Commit 메시지 규칙
- [ ] Pull Request 프로세스
- [ ] CI/CD 파이프라인
- [ ] 환경 분리
- [ ] Hotfix 프로세스
- [ ] 배포 프로세스
- [ ] Rollback 절차

**coding-standards.md 필수 섹션**:
- [ ] TypeScript 명명 규칙
- [ ] 파일 구조
- [ ] Import 순서
- [ ] 함수 작성 규칙
- [ ] 타입 안전성
- [ ] 에러 처리
- [ ] React 컴포넌트 규칙
- [ ] 주석 작성
- [ ] ESLint 설정
- [ ] Prettier 설정
- [ ] 테스트 작성 규칙

#### 5.2 예시 코드 포함

- [ ] **좋은 예시 (✅ Good) 포함**
- [ ] **나쁜 예시 (❌ Bad) 포함**
- [ ] **예시 코드가 실제 실행 가능**

#### 5.3 실용성 확인

- [ ] **신규 개발자가 이해 가능**
  - 명확한 설명
  - 풍부한 예시

- [ ] **실제 프로젝트에 적용 가능**
  - 추상적이지 않음
  - 구체적인 가이드

---

### 6. Blocker 확인

#### 6.1 의존성 차단

- [ ] **S1M2는 선행 Task 없음**
  - 독립적으로 완료 가능

#### 6.2 환경 차단

- [ ] **환경 차단 없음**
  - 순수 문서 작성 작업

#### 6.3 외부 API 차단

- [ ] **외부 API 호출 없음**
  - 문서 작성만 수행

---

### 7. 도구 설정 파일 (권장)

#### 7.1 ESLint 설정 파일 (선택 사항)

- [ ] **`.eslintrc.json` 파일 생성 (선택)**
  - 문서에 명시된 설정대로 작성

#### 7.2 Prettier 설정 파일 (선택 사항)

- [ ] **`.prettierrc` 파일 생성 (선택)**
  - 문서에 명시된 설정대로 작성

#### 7.3 Pre-commit Hook (선택 사항)

- [ ] **Husky 설정 (선택)**
  - Lint 및 Format 자동 실행

---

## 합격 기준

### 필수 (Must Pass)

1. **2개 문서 파일 모두 생성** ✅
   - `development-guide.md`
   - `coding-standards.md`

2. **Git 전략 문서화** ✅
   - 브랜치 전략, 명명 규칙

3. **Commit 메시지 규칙 정의** ✅
   - Conventional Commits 형식

4. **Pull Request 프로세스 문서화** ✅
   - 6단계 프로세스, PR 템플릿

5. **코딩 표준 정의** ✅
   - TypeScript 명명 규칙, 함수 작성 규칙 등

6. **좋은/나쁜 예시 포함** ✅
   - 각 규칙마다 예시 코드

7. **Markdown 문법 에러 없음** ✅
   - Markdown Linter 통과

### 권장 (Nice to Pass)

1. **VS Code 설정 파일 추가** ✨
   - `.vscode/settings.json`

2. **Pre-commit Hook 스크립트** ✨
   - Husky + lint-staged 설정

3. **실제 ESLint/Prettier 설정 파일 생성** ✨
   - 문서대로 설정 파일 작성

---

## 검증 결과

### Pass/Fail

**Status**: [ ] Pass / [ ] Fail

**검증일**: _______________

**검증자**: _______________

### 발견 사항

#### 🟢 통과 항목

- (통과한 항목 나열)

#### 🔴 실패 항목

- (실패한 항목 나열 및 수정 필요 사항)

#### 🟡 경고 사항

- (경고 또는 개선 권장 사항)

---

## 주의사항

1. **실제 프로세스 반영**
   - 팀의 실제 작업 방식에 맞게 조정
   - 문서와 실제 프로세스 일치 유지

2. **도구 설정 동기화**
   - ESLint, Prettier 설정 파일 실제 생성
   - VS Code 설정 공유

3. **지속적 업데이트**
   - 프로세스 변경 시 문서 업데이트
   - 팀원 피드백 반영

4. **접근성**
   - 신규 개발자도 이해 가능하도록 작성
   - 예시 코드 풍부하게 제공

5. **실용성 우선**
   - 추상적인 원칙보다 구체적인 예시
   - 실제 프로젝트에 바로 적용 가능

---

## 참조

- Task Instruction: `task-instructions/S1M2_instruction.md`
- Conventional Commits: https://www.conventionalcommits.org/
- Git Flow: https://nvie.com/posts/a-successful-git-branching-model/
- TypeScript Style Guide: https://google.github.io/styleguide/tsguide.html

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
