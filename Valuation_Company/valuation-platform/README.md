# 기업가치평가 플랫폼 (Valuation Platform)

AI 기반 기업가치평가 시스템 - Phase 1 MVP

## 🎯 프로젝트 개요

**50:30:20 AI 하이브리드 전략**을 활용한 기업가치평가 플랫폼입니다.

- **Claude 50%**: 핵심 비즈니스 로직 (DCF 계산, 상대가치 분석, 보안)
- **ChatGPT 30%**: 멀티모달 분석 (PDF 분석, 이미지 OCR, 챗봇)
- **Gemini 20%**: 실시간 리서치 (기업 조사, 산업 분석, 대용량 처리)

## 📋 Phase 1 기능

### 평가 방법
1. **DCF 평가** (Discounted Cash Flow)
   - 현금흐름할인법 기반 기업가치 계산
   - WACC, 터미널 가치, 주당 가치 산출

2. **상대가치 평가** (Comparable Company Analysis)
   - 유사 기업 비교 기반 평가
   - P/E, P/B, EV/EBITDA 멀티플 분석

## 🏗 기술 스택

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase)
- **ORM**: Prisma

### AI Integration
- **Claude 3.5 Sonnet** (50%) - Anthropic API
- **GPT-4o** (30%) - OpenAI API
- **Gemini 1.5 Pro** (20%) - Google AI API

## 📦 프로젝트 구조

```
valuation-platform/
├── frontend/                 # Next.js 프론트엔드
│   ├── app/                 # App Router 페이지
│   ├── components/          # React 컴포넌트
│   ├── lib/                 # 유틸리티 함수
│   └── package.json
│
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py         # FastAPI 앱
│   │   ├── core/           # 핵심 설정
│   │   │   ├── config.py   # 환경 변수 설정
│   │   │   └── ai_router.py # AI 라우터 (50:30:20)
│   │   ├── services/       # 비즈니스 로직
│   │   │   └── ai_client.py # AI 클라이언트
│   │   └── api/            # API 엔드포인트
│   └── requirements.txt
│
└── shared/                  # 공유 타입/유틸
```

## 🚀 시작하기

### 1. 환경 변수 설정

**Backend** (`backend/.env`)
```bash
# AI API Keys - 50:30:20 전략
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Claude (50%)
OPENAI_API_KEY=sk-xxxxx          # ChatGPT (30%)
GOOGLE_API_KEY=AIza-xxxxx        # Gemini (20%)

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/valuation_db

# Application
DEBUG=True
SECRET_KEY=your-secret-key
```

**Frontend** (`frontend/.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Backend 실행

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000
문서: http://localhost:8000/docs

### 3. Frontend 실행

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

웹사이트: http://localhost:3000

## 🤖 AI 라우터 전략

### 작업별 AI 모델 선택

| 작업 유형 | AI 모델 | 비율 | 이유 |
|----------|---------|------|------|
| DCF 계산 | Claude | 50% | 최고 정확도, 논리적 추론 |
| 상대가치 분석 | Claude | 50% | 복잡한 금융 계산 |
| 보안 검증 | Claude | 50% | 낮은 버그율 (4.2%) |
| PDF 분석 | OpenAI | 30% | GPT-4o Vision API |
| 이미지 OCR | OpenAI | 30% | 멀티모달 처리 |
| 챗봇 | OpenAI | 30% | 자연스러운 대화 |
| 기업 리서치 | Gemini | 20% | Google Search 통합 |
| 산업 분석 | Gemini | 20% | 실시간 데이터 |
| 대용량 문서 | Gemini | 20% | 2M 토큰 컨텍스트 |

### AI Router 사용 예시

```python
from app.core.ai_router import ai_router, TaskType, TaskPriority

# DCF 계산 - Claude 자동 선택
model = ai_router.select_model(
    task_type=TaskType.DCF_CALCULATION,
    priority=TaskPriority.CRITICAL
)
# Returns: "claude"

# PDF 분석 - OpenAI 자동 선택
model = ai_router.select_model(
    task_type=TaskType.PDF_ANALYSIS
)
# Returns: "openai"

# 기업 리서치 - Gemini 자동 선택
model = ai_router.select_model(
    task_type=TaskType.COMPANY_RESEARCH
)
# Returns: "gemini"
```

## 📊 비용 분석

### 월별 예상 비용 (50:30:20 전략)

- **Claude (50%)**: $100/월
- **OpenAI (30%)**: $60/월
- **Gemini (20%)**: $40/월
- **합계**: $200/월

### 단일 모델 대비 절감

- Claude 단독: $250/월 → **20% 절감**
- 품질은 유지하면서 비용 최적화

## 🛠 개발 로드맵

### Phase 1-1: 프로젝트 설정 ✅
- [x] Next.js 14 프론트엔드 구조
- [x] FastAPI 백엔드 구조
- [x] AI Router 구현 (50:30:20)
- [x] 환경 설정 파일

### Phase 1-2: DCF 계산 엔진 (다음 단계)
- [ ] DCF 계산 로직 (Claude)
- [ ] WACC 계산
- [ ] 터미널 가치 계산
- [ ] 단위 테스트

### Phase 1-3: 상대가치 계산 엔진
- [ ] 멀티플 계산 (P/E, P/B, EV/EBITDA)
- [ ] 유사 기업 선정 로직
- [ ] 단위 테스트

### Phase 1-4: 데이터베이스 설계
- [ ] Prisma 스키마 정의
- [ ] 마이그레이션 실행
- [ ] DB 연결 테스트

### Phase 1-5: API 개발
- [ ] DCF API 엔드포인트
- [ ] 상대가치 API 엔드포인트
- [ ] API 문서화

### Phase 1-6: 프론트엔드 개발
- [ ] DCF 입력 폼
- [ ] 상대가치 입력 폼
- [ ] 결과 표시 화면

### Phase 1-7: AI 기능 통합
- [ ] PDF 재무제표 분석 (OpenAI)
- [ ] 기업 정보 수집 (Gemini)
- [ ] 계산 검증 (Claude)

### Phase 1-8: 보고서 생성
- [ ] PDF 보고서 템플릿 (Claude)
- [ ] 차트 및 그래프
- [ ] 다운로드 기능

### Phase 1-9: 테스트 및 QA
- [ ] 통합 테스트
- [ ] E2E 테스트
- [ ] 성능 테스트

### Phase 1-10: 배포
- [ ] Vercel 배포 (Frontend)
- [ ] Railway 배포 (Backend)
- [ ] 도메인 연결

## 📝 API 문서

백엔드 실행 후 다음 URL에서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔒 보안

- API 키는 환경 변수로 관리
- `.env` 파일은 `.gitignore`에 포함
- CORS 설정으로 허용된 도메인만 접근
- 입력 데이터 검증 (Pydantic)

## 🤝 기여

Phase 1 MVP 개발 중입니다. 기여는 Phase 2부터 받을 예정입니다.

## 📄 라이선스

MIT License

## 📞 문의

프로젝트 관련 문의: [이메일 주소]

---

**🎯 Current Status**: Phase 1-1 완료 ✅ | Next: Phase 1-2 DCF 계산 엔진 개발
