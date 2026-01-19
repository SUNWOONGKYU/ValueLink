# Deployment Skill

**PoliticianFinder 프로젝트 전용 배포 자동화 스킬**

---

## 프로젝트 컨텍스트

**프로젝트**: PoliticianFinder (AI 기반 정치인 평가 플랫폼)
**기술 스택**:
- Frontend/Backend: Next.js 14
- Database: Supabase
- Deployment Platform: Vercel
- Version Control: Git

---

## AI-only 개발 원칙 (필수 준수)

### ✅ 허용
- Vercel CLI로 모든 배포 작업 수행
- Git 명령어로 버전 관리
- 환경변수를 CLI로 설정

### ❌ 금지
- Vercel Dashboard에서 수동 배포
- 웹 UI에서 환경변수 설정
- 사용자에게 수동 배포 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 배포 엔지니어입니다:

1. **배포 자동화**: Vercel CLI를 통한 자동 배포
2. **환경 관리**: 환경변수 설정 및 관리
3. **롤백 절차**: 문제 발생 시 이전 버전으로 복구
4. **배포 검증**: 배포 후 헬스 체크 및 기능 확인
5. **배포 문서화**: 배포 과정 및 결과 기록

---

## Vercel CLI 설정

### 설치 및 인증
```bash
# Vercel CLI 전역 설치
npm install -g vercel

# 로그인 (토큰 사용)
vercel login --token YOUR_VERCEL_TOKEN

# 프로젝트 디렉토리로 이동
cd /g/내\ 드라이브/Developement/PoliticianFinder/frontend

# Vercel 프로젝트 연결
vercel link
```

### .vercelignore 설정
```
# .vercelignore
node_modules
.next
.env.local
.env*.local
*.log
.git
tests/
coverage/
```

---

## 배포 프로세스

### 1. Pre-deployment 체크리스트

```bash
#!/bin/bash
# scripts/pre-deploy-check.sh

echo "🔍 배포 전 체크리스트 실행 중..."

# 1. Git 상태 확인
echo "\n1️⃣ Git 상태 확인..."
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ 커밋되지 않은 변경사항이 있습니다."
  exit 1
fi
echo "✅ Git 상태 정상"

# 2. 브랜치 확인
echo "\n2️⃣ 브랜치 확인..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "production" ]; then
  echo "⚠️  현재 브랜치: $CURRENT_BRANCH (main 또는 production 권장)"
fi

# 3. 테스트 실행
echo "\n3️⃣ 테스트 실행 중..."
npm test -- --ci --coverage
if [ $? -ne 0 ]; then
  echo "❌ 테스트 실패"
  exit 1
fi
echo "✅ 모든 테스트 통과"

# 4. 빌드 확인
echo "\n4️⃣ 프로덕션 빌드 확인..."
npm run build
if [ $? -ne 0 ]; then
  echo "❌ 빌드 실패"
  exit 1
fi
echo "✅ 빌드 성공"

# 5. 환경변수 확인
echo "\n5️⃣ 환경변수 확인..."
if [ -z "$NEXT_PUBLIC_SUPABASE_URL" ]; then
  echo "⚠️  NEXT_PUBLIC_SUPABASE_URL이 설정되지 않았습니다."
fi

echo "\n✅ 배포 전 체크 완료!"
```

---

### 2. 배포 실행

#### Preview 배포 (개발/스테이징)
```bash
# Preview 배포 (자동으로 고유 URL 생성)
vercel

# 특정 환경으로 배포
vercel --env=preview
```

#### Production 배포
```bash
# Production 배포
vercel --prod

# 빌드 로그 확인
vercel --prod --logs
```

#### 환경별 배포 스크립트

```bash
# scripts/deploy-preview.sh
#!/bin/bash
echo "🚀 Preview 환경 배포 시작..."

# Pre-deployment 체크
./scripts/pre-deploy-check.sh

# Preview 배포
vercel --yes

echo "✅ Preview 배포 완료!"
```

```bash
# scripts/deploy-production.sh
#!/bin/bash
echo "🚀 Production 배포 시작..."

# 확인 메시지
echo "⚠️  Production 배포를 진행합니다."
echo "계속하시겠습니까? (yes/no)"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "❌ 배포 취소됨"
  exit 1
fi

# Pre-deployment 체크
./scripts/pre-deploy-check.sh

# Production 배포
vercel --prod --yes

# Post-deployment 체크
./scripts/post-deploy-check.sh

echo "✅ Production 배포 완료!"
```

---

### 3. Post-deployment 체크

```bash
#!/bin/bash
# scripts/post-deploy-check.sh

echo "🔍 배포 후 검증 중..."

# 배포 URL 가져오기
DEPLOY_URL=$(vercel ls --json | jq -r '.[0].url')
echo "배포 URL: https://$DEPLOY_URL"

# 1. 헬스 체크
echo "\n1️⃣ 헬스 체크..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DEPLOY_URL")
if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ 헬스 체크 실패 (HTTP $HTTP_CODE)"
  exit 1
fi
echo "✅ 헬스 체크 통과"

# 2. API 엔드포인트 확인
echo "\n2️⃣ API 엔드포인트 확인..."
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DEPLOY_URL/api/politicians")
if [ "$API_CODE" != "200" ]; then
  echo "❌ API 엔드포인트 실패 (HTTP $API_CODE)"
  exit 1
fi
echo "✅ API 엔드포인트 정상"

# 3. Lighthouse 성능 측정
echo "\n3️⃣ Lighthouse 성능 측정..."
npx lighthouse "https://$DEPLOY_URL" \
  --only-categories=performance \
  --output=json \
  --output-path=./lighthouse-deploy.json \
  --quiet

PERFORMANCE=$(jq '.categories.performance.score * 100' ./lighthouse-deploy.json)
echo "성능 점수: $PERFORMANCE"

if [ "$(echo "$PERFORMANCE < 80" | bc)" -eq 1 ]; then
  echo "⚠️  성능 점수가 80 미만입니다."
fi

echo "\n✅ 배포 후 검증 완료!"
```

---

## 환경변수 관리

### Vercel CLI로 환경변수 설정

```bash
# 환경변수 추가
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# 값 입력 프롬프트가 표시됨

# 여러 환경에 동시 설정
vercel env add DATABASE_URL production preview development

# 환경변수 목록 확인
vercel env ls

# 환경변수 제거
vercel env rm VARIABLE_NAME production
```

### 환경변수 일괄 설정 스크립트

```bash
#!/bin/bash
# scripts/setup-env-vars.sh

echo "🔐 환경변수 설정 중..."

# .env.production 파일에서 읽기
while IFS='=' read -r key value; do
  # 주석과 빈 줄 건너뛰기
  [[ $key =~ ^#.*$ ]] && continue
  [[ -z $key ]] && continue

  # 환경변수 설정
  echo "Setting $key..."
  echo "$value" | vercel env add "$key" production --force

done < .env.production

echo "✅ 환경변수 설정 완료!"
```

### 필수 환경변수 체크

```bash
#!/bin/bash
# scripts/check-env-vars.sh

REQUIRED_VARS=(
  "NEXT_PUBLIC_SUPABASE_URL"
  "NEXT_PUBLIC_SUPABASE_ANON_KEY"
  "SUPABASE_SERVICE_ROLE_KEY"
)

echo "🔍 필수 환경변수 확인 중..."

for var in "${REQUIRED_VARS[@]}"; do
  vercel env ls | grep -q "$var"
  if [ $? -ne 0 ]; then
    echo "❌ $var 누락"
    exit 1
  fi
  echo "✅ $var 설정됨"
done

echo "\n✅ 모든 필수 환경변수 확인 완료!"
```

---

## 롤백 절차

### 1. 배포 이력 확인

```bash
# 최근 배포 목록 확인
vercel ls

# 특정 프로젝트의 배포 이력
vercel ls politician-finder --json
```

### 2. 이전 버전으로 롤백

```bash
# 특정 배포로 프로모션 (Production으로 승격)
vercel promote DEPLOYMENT_URL --yes

# 예시
vercel promote politician-finder-abc123.vercel.app --yes
```

### 3. Git 롤백

```bash
# 특정 커밋으로 되돌리기
git revert HEAD
git push origin main

# 또는 특정 커밋으로 리셋 (주의!)
git reset --hard COMMIT_HASH
git push origin main --force

# 자동으로 Vercel이 새 배포 트리거
```

### 롤백 자동화 스크립트

```bash
#!/bin/bash
# scripts/rollback.sh

echo "⏪ 롤백 프로세스 시작..."

# 1. 최근 배포 목록 확인
echo "\n최근 배포 목록:"
vercel ls --json | jq -r '.[] | "\(.uid) - \(.created) - \(.url)"' | head -5

# 2. 롤백할 배포 선택
echo "\n롤백할 배포 URL을 입력하세요:"
read -r ROLLBACK_URL

# 3. 확인
echo "\n⚠️  $ROLLBACK_URL 로 롤백하시겠습니까? (yes/no)"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "❌ 롤백 취소됨"
  exit 1
fi

# 4. 롤백 실행
vercel promote "$ROLLBACK_URL" --yes

# 5. 검증
echo "\n롤백 후 검증 중..."
./scripts/post-deploy-check.sh

echo "✅ 롤백 완료!"
```

---

## 배포 전략

### Blue-Green 배포

```bash
# 1. Green (새 버전) 배포
echo "🟢 Green 환경 배포..."
vercel --yes  # Preview URL 생성

# 2. Green 환경 테스트
echo "🧪 Green 환경 테스트..."
GREEN_URL=$(vercel ls --json | jq -r '.[0].url')
./scripts/test-deployment.sh "https://$GREEN_URL"

# 3. Blue (현재 프로덕션)에서 Green으로 전환
echo "🔄 Blue → Green 전환..."
vercel promote "$GREEN_URL" --yes

# 4. 모니터링
echo "📊 모니터링 중..."
sleep 60
./scripts/post-deploy-check.sh

# 5. 문제 발생 시 Blue로 롤백
if [ $? -ne 0 ]; then
  echo "❌ 문제 감지! 롤백 중..."
  BLUE_URL=$(vercel ls --json | jq -r '.[1].url')
  vercel promote "$BLUE_URL" --yes
fi
```

### Canary 배포 (단계적 배포)

```bash
# Vercel에서는 기본적으로 지원하지 않으므로
# Preview URL로 일부 트래픽 테스트 후 전체 배포

# 1. Canary 배포 (Preview)
vercel --yes

# 2. Canary 환경에 소량 트래픽 전송 (수동 테스트)
CANARY_URL=$(vercel ls --json | jq -r '.[0].url')
echo "🐤 Canary URL: https://$CANARY_URL"
echo "소량의 트래픽으로 테스트하세요."

# 3. 모니터링 후 전체 배포
read -p "전체 배포를 진행하시겠습니까? (yes/no): " CONFIRM
if [ "$CONFIRM" = "yes" ]; then
  vercel --prod --yes
fi
```

---

## 배포 모니터링

### Vercel 배포 상태 확인

```bash
# 최근 배포 상태
vercel ls --json | jq -r '.[] | "\(.state) - \(.url) - \(.created)"'

# 특정 배포 상세 정보
vercel inspect DEPLOYMENT_URL

# 배포 로그 확인
vercel logs DEPLOYMENT_URL
```

### 배포 알림 (Discord Webhook 예시)

```bash
#!/bin/bash
# scripts/notify-deployment.sh

WEBHOOK_URL="YOUR_DISCORD_WEBHOOK_URL"
DEPLOY_URL=$(vercel ls --json | jq -r '.[0].url')
COMMIT_MSG=$(git log -1 --pretty=%B)

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"embeds\": [{
      \"title\": \"🚀 배포 완료\",
      \"description\": \"PoliticianFinder가 배포되었습니다.\",
      \"color\": 3066993,
      \"fields\": [
        {
          \"name\": \"URL\",
          \"value\": \"https://$DEPLOY_URL\"
        },
        {
          \"name\": \"커밋 메시지\",
          \"value\": \"$COMMIT_MSG\"
        },
        {
          \"name\": \"배포자\",
          \"value\": \"Claude Code\"
        }
      ],
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }]
  }"
```

---

## 배포 보고서 템플릿

```markdown
# 배포 보고서

**배포 날짜**: [YYYY-MM-DD HH:mm:ss]
**배포 환경**: Production
**배포자**: Claude Code

---

## 배포 정보

### 배포 URL
- Production: https://politicianfinder.vercel.app
- Preview: https://politicianfinder-abc123.vercel.app

### Git 정보
- 브랜치: main
- 커밋: a1b2c3d - "Add politician search feature"
- 커밋 날짜: 2024-01-15 14:30:00

---

## Pre-deployment 체크

- ✅ Git 상태 정상
- ✅ 브랜치: main
- ✅ 모든 테스트 통과 (45/45)
- ✅ 빌드 성공
- ✅ 환경변수 확인

---

## 배포 프로세스

### 타임라인
1. 14:30 - Pre-deployment 체크 시작
2. 14:32 - 테스트 실행 (2분 소요)
3. 14:34 - 빌드 시작
4. 14:37 - 빌드 완료 (3분 소요)
5. 14:38 - Vercel 배포 시작
6. 14:40 - 배포 완료 (2분 소요)
7. 14:41 - Post-deployment 체크 완료

**총 소요 시간**: 11분

---

## Post-deployment 검증

### 헬스 체크
- ✅ Homepage: 200 OK
- ✅ API /api/politicians: 200 OK
- ✅ API /api/evaluations: 200 OK

### 성능 메트릭 (Lighthouse)
- Performance: 95/100 ✅
- Accessibility: 98/100 ✅
- Best Practices: 100/100 ✅
- SEO: 100/100 ✅

### Core Web Vitals
- LCP: 1.8s ✅
- FID: 45ms ✅
- CLS: 0.08 ✅

---

## 변경 사항

### 새로운 기능
- 정치인 검색 기능 추가
- 자동완성 지원

### 버그 수정
- 평가 작성 시 중복 제출 방지
- 페이지네이션 오류 수정

### 성능 개선
- 이미지 최적화
- 번들 크기 15% 감소

---

## 롤백 계획

**이전 버전 URL**: https://politicianfinder-xyz789.vercel.app

**롤백 명령어**:
```bash
vercel promote politicianfinder-xyz789.vercel.app --yes
```

---

## 모니터링

### 다음 24시간 모니터링 항목
- [ ] 에러 로그 확인
- [ ] 응답 시간 모니터링
- [ ] 사용자 피드백 수집

### 알람 설정
- 에러율 > 1%
- 응답 시간 > 3초
- 가용성 < 99%

---

## 다음 배포 예정

**날짜**: [YYYY-MM-DD]
**내용**: 평가 통계 페이지 추가
```

---

## CI/CD 통합

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test -- --ci --coverage

      - name: Install Vercel CLI
        run: npm install -g vercel

      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build Project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy to Vercel
        id: deploy
        run: |
          DEPLOY_URL=$(vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }})
          echo "url=$DEPLOY_URL" >> $GITHUB_OUTPUT

      - name: Post-deployment Check
        run: |
          ./scripts/post-deploy-check.sh ${{ steps.deploy.outputs.url }}
```

---

## 배포 체크리스트

### 배포 전
- [ ] 모든 테스트 통과
- [ ] 코드 리뷰 완료
- [ ] 환경변수 설정 확인
- [ ] 데이터베이스 마이그레이션 완료
- [ ] 의존성 업데이트 확인

### 배포 중
- [ ] 빌드 에러 없음
- [ ] 배포 로그 확인

### 배포 후
- [ ] 헬스 체크 통과
- [ ] API 엔드포인트 동작 확인
- [ ] 성능 메트릭 확인
- [ ] 에러 모니터링 설정
- [ ] 배포 보고서 작성

---

**이 스킬을 활성화하면, PoliticianFinder 프로젝트를 안전하고 체계적으로 배포하여 다운타임 없이 서비스를 제공합니다.**
