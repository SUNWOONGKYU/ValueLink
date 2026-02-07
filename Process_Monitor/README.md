# Process Monitor - SSAL Works 진행률 자동 업로드

> git commit 시 P0~S5 진행률을 자동 계산하여 **SSAL Works DB**에 업로드
> SSAL Works 플랫폼(ssalworks.com)에서 진행률 표시

---

## 데이터 흐름

```
git commit
    ↓
build-progress.js (진행률 계산)
    ↓
phase_progress.json (로컬 저장)
    ↓
upload-progress.js (SSAL Works DB에 업로드)
    ↓
SSAL Works 플랫폼에서 진행률 표시
```

---

## 파일 구성

```
Process_Monitor/
├── README.md                      ← 이 문서
├── build-progress.js              ← 진행률 계산 스크립트
├── upload-progress.js             ← DB 업로드 스크립트 (scripts/에 복사)
├── create_table.sql               ← 테이블 생성 SQL (SSAL Works 전용)
├── pre-commit-hook-example.sh     ← pre-commit hook 예시
├── loadProjectProgress-snippet.js ← 웹 조회 함수 (SSAL Works 전용)
└── data/
    └── phase_progress.json        ← 출력 파일
```

---

## 설정 방법

### 1. SSAL Works 키 받기

SSAL Works 팀에서 제공하는 키를 받습니다:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일 생성:
```
# SSAL Works에서 제공받은 키
SUPABASE_URL=https://zwjmfewyshhwpgwdtrus.supabase.co
SUPABASE_SERVICE_ROLE_KEY=제공받은_키

# SSAL Works 프로젝트 ID (프로젝트 등록 시 부여받은 ID)
PROJECT_ID=2512000006TH-P001
```

### 3. 스크립트 복사 + 경로 수정

```bash
cp Process_Monitor/upload-progress.js scripts/
```

**⚠️ 경로 수정 필수!** `scripts/upload-progress.js` 열어서:
```javascript
// 18-20행 수정
const PROGRESS_JSON_PATH = path.join(PROJECT_ROOT, 'Process_Monitor', 'data', 'phase_progress.json');
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

echo "📤 SSAL Works DB 업로드 중..."
node "$PROJECT_ROOT/scripts/upload-progress.js"

echo "✅ 진행률 처리 완료!"
exit 0
```

### 5. SSAL Works 플랫폼에서 확인

1. ssalworks.com 로그인
2. 사이드바에서 진행률 확인

---

## 진행률 계산 방식

| 단계 | 계산 방식 |
|------|----------|
| P0~S0 | 폴더 내 파일 존재 여부 |
| S1~S5 | grid_records/*.json에서 Completed Task 비율 |

---

## Project ID

SSAL Works에서 프로젝트 등록 시 부여받은 ID를 사용합니다.

```
예: 2512000006TH-P001
```

- `.env`에 `PROJECT_ID` 설정 필수
- SSAL Works 플랫폼에서 이 ID로 진행률 조회

---

## 작동 확인

1. `git commit` 실행
2. 콘솔에서 "📤 Progress Uploader" 메시지 확인
3. ssalworks.com 로그인
4. 사이드바에서 진행률 표시 확인

---

## 주의사항

- `.env` 파일은 `.gitignore`에 추가 (SSAL Works 키 보호)
- SSAL Works 키 없으면 업로드 실패 (커밋은 진행)
- SSAL Works에 로그인하지 않으면 0% 표시
- git 이메일과 SSAL Works 로그인 이메일이 같아야 함
