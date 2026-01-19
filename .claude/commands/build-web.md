# 웹 배포 파일 빌드

웹사이트에 반영될 배포 파일들을 빌드합니다.

## 실행할 작업

다음 명령을 실행하세요:

```bash
node Production/build-web-assets.js
```

## 빌드 대상

| 소스 | 출력 |
|------|------|
| Order Sheet 템플릿 (*.md) | ordersheets.js |
| 안내문 HTML (*.html) | guides.js |
| PROJECT_SAL_GRID_MANUAL.md | HTML 변환 |

## 빌드 완료 후

빌드 결과를 사용자에게 보고하세요:
- 성공/실패 여부
- 생성된 파일 목록
- 소요 시간
