# Process Monitor - 진행률 자동 업로드

> git commit 시 P0~S5 진행률을 자동 계산하여 DB에 업로드

---

## 데이터 흐름

```
git commit
    ↓
build-progress.js (진행률 계산)
    ↓
phase_progress.json (로컬 저장)
    ↓
upload-progress.js (DB 업로드)
    ↓
웹에서 진행률 표시
```

---

## 파일 구성

```
Process_Monitor/
├── README.md                      ← 이 문서
├── build-progress.js              ← 진행률 계산 스크립트
├── upload-progress.js             ← DB 업로드 스크립트 (scripts/에 복사)
├── create_table.sql               ← Supabase 테이블 생성 SQL
├── pre-commit-hook-example.sh     ← pre-commit hook 예시
├── loadProjectProgress-snippet.js ← 웹에서 DB 조회 함수
└── data/
    └── phase_progress.json        ← 출력 파일
```

---

## 설정 방법

### 1. 테이블 생성

Supabase Dashboard에서 `create_table.sql` 실행

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일 생성:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3. 스크립트 복사 + 경로 수정

```bash
cp Process_Monitor/upload-progress.js scripts/
```

**⚠️ 경로 수정 필수!** `scripts/upload-progress.js` 열어서:
```javascript
// 18-20행 수정
const PROGRESS_JSON_PATH = path.join(PROJECT_ROOT, '{실제 폴더명}', 'data', 'phase_progress.json');
const ENV_PATH = path.join(PROJECT_ROOT, '.env');
```

### 4. Pre-commit Hook 설정

`.git/hooks/pre-commit` 파일 생성:
```bash
#!/bin/sh
PROJECT_ROOT="$(git rev-parse --show-toplevel)"

echo "📊 진행률 빌드 중..."
node "$PROJECT_ROOT/Process_Monitor/build-progress.js"

git add "$PROJECT_ROOT/Process_Monitor/data/phase_progress.json" 2>/dev/null

echo "📤 진행률 DB 업로드 중..."
node "$PROJECT_ROOT/scripts/upload-progress.js"

echo "✅ 진행률 처리 완료!"
exit 0
```

### 5. 웹에서 조회

`loadProjectProgress-snippet.js` 내용을 index.html에 추가

---

## 진행률 계산 방식

| 단계 | 계산 방식 |
|------|----------|
| P0~S0 | 폴더 내 파일 존재 여부 |
| S1~S5 | grid_records/*.json에서 Completed Task 비율 |

---

## Project ID 규칙

```
git config user.email = dev@example.com
                          ↓
project_id = dev_PROJECT
```

- 이메일 @ 앞 부분 + "_PROJECT"
- 동일 이메일 = 동일 project_id

---

## 작동 확인

1. `git commit` 실행
2. 콘솔에서 "📤 Progress Uploader" 메시지 확인
3. Supabase에서 `project_phase_progress` 테이블 조회
4. 웹에서 진행률 표시 확인

---

## 주의사항

- `.env` 파일은 `.gitignore`에 추가 (보안)
- Supabase 설정 없으면 업로드 건너뜀 (커밋은 진행)
- 로그인하지 않은 사용자는 0% 표시
