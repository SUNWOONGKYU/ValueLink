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
├── pre-commit-hook-example.sh     ← pre-commit hook 예시
├── loadProjectProgress-snippet.js ← 웹 조회 함수 (SSAL Works 전용)
└── data/
    └── phase_progress.json        ← 출력 파일
```

---

## 설정 방법

### 1. SSAL Works에서 프로젝트 등록

1. ssalworks.com 접속 및 로그인
2. 프로젝트 등록
3. `.ssal-project.json` 파일이 자동 생성됨:
   ```json
   {
       "project_id": "2512000006TH-P001",
       "project_name": "프로젝트명",
       "owner_email": "user@example.com"
   }
   ```

### 2. 스크립트 복사

```bash
cp Process_Monitor/upload-progress.js scripts/
```

### 3. Pre-commit Hook 설정

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

### 4. SSAL Works 플랫폼에서 확인

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

`.ssal-project.json`에서 자동으로 읽어옵니다.

```json
{
    "project_id": "2512000006TH-P001"
}
```

- SSAL Works 프로젝트 등록 시 자동 생성
- 별도 설정 불필요

---

## 작동 확인

1. `git commit` 실행
2. 콘솔에서 "📤 SSAL Works 진행률 업로드" 메시지 확인
3. ssalworks.com 로그인
4. 사이드바에서 진행률 표시 확인

---

## 주의사항

- `.ssal-project.json` 파일이 있어야 업로드 가능
- SSAL Works에 로그인하지 않으면 0% 표시
- git 이메일과 SSAL Works 로그인 이메일이 같아야 함
