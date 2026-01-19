# Pre-commit Hook 자동화 목록

> git commit 실행 시 자동으로 실행되는 8가지 자동화

---

## 자동화 항목 (8개)

| # | 자동화 내용 | 소스 파일 | 출력 파일 |
|---|------------|----------|----------|
| 1 | Order Sheets MD → JS 번들링 | `Briefings_OrderSheets/OrderSheet_Templates/*.md` | `ordersheets.js` |
| 2 | Briefings (상황별 안내문) MD → JS 번들링 | `Briefings_OrderSheets/Briefings/**/*.md` | `guides.js` |
| 3 | 외부 연동 설정 가이드 MD → JS 번들링 | `부수적_고유기능/콘텐츠/외부_연동_설정_Guide/*.md` | `service-guides.js` |
| 4 | 서비스 소개 모달 MD → index.html 삽입 | `P2_.../Service_Introduction/서비스_소개.md` | `index.html` |
| 5 | SAL Grid 매뉴얼 MD → HTML 변환 | `S0_.../manual/PROJECT_SAL_GRID_MANUAL.md` | `참고자료/*.html` |
| 6 | 빌더 계정 매뉴얼 MD → HTML 변환 | `P2_.../Service_Introduction/빌더용_사용_매뉴얼.md` | `Production/pages/mypage/manual.html` |
| 7 | P0~S5 진행률 → JSON 생성 | `P0~S0 폴더`, `sal_grid.csv` | `data/phase_progress.json` |
| 8 | Stage 폴더 → 배포 폴더 자동 복사 | `S?_*/Frontend/`, `S?_*/Backend_APIs/` 등 | `pages/`, `api/` |

---

## 스크립트 위치

### 개별 폴더 스크립트 (3개)

| # | 스크립트 | 위치 |
|---|---------|------|
| 1 | `generate-ordersheets-js.js` | `Briefings_OrderSheets/OrderSheet_Templates/` |
| 2 | `generate-briefings-js.js` | `Briefings_OrderSheets/Briefings/` |
| 3 | `generate-service-guides-js.js` | `부수적_고유기능/콘텐츠/외부_연동_설정_Guide/` |

### 루트 scripts/ 폴더 스크립트 (2개)

| # | 스크립트 | 담당 |
|---|---------|------|
| 1-7 | `build-web-assets.js` | 1~7번 통합 실행 (4-7번 내장) |
| 8 | `sync-to-root.js` | Stage → Root 자동 복사 |

---

## Stage → Root 매핑 (8번 자동화)

| Area | Stage 폴더 | Root 폴더 |
|------|-----------|----------|
| F | `S?_*/Frontend/` | `pages/` |
| BA | `S?_*/Backend_APIs/` | `api/Backend_APIs/` |
| S | `S?_*/Security/` | `api/Security/` |
| BI | `S?_*/Backend_Infra/` | `api/Backend_Infra/` |
| E | `S?_*/External/` | `api/External/` |

---

## Pre-commit Hook 설정

**Hook 파일:** `.git/hooks/pre-commit`

```bash
#!/bin/sh
echo "🔄 Pre-commit Hook 실행 중..."

# 1-6번: 웹 자산 빌드
node scripts/build-web-assets.js
if [ $? -ne 0 ]; then
    echo "❌ 빌드 실패!"
    exit 1
fi

# 7번: Stage → Root 동기화
node scripts/sync-to-root.js
if [ $? -ne 0 ]; then
    echo "❌ 동기화 실패!"
    exit 1
fi

# 변경된 파일 스테이징
git add -A

echo "✅ Pre-commit Hook 완료!"
```

---

## 관련 문서

- 저장 위치 규칙: `.claude/rules/02_save-location.md`
- 패키지 구조: `공개_전환_업무/04_패키지_표준_디렉토리_구조.md`
- 필수 도구 설치: `공개_전환_업무/08_필수_도구_설치_안내문.md`
