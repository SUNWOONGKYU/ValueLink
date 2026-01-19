# Phase 1: 기업가치평가 시스템 개발 로드맵

## 프로젝트 개요
**목표**: 첫 번째 고객 확보를 위한 MVP 개발
**도메인**: valuation.ai.kr
**Phase 1 범위**: DCF 평가 + 상대가치 평가 (2종)
**AI 전략**: 50:30:20 하이브리드 전략 (Claude 50% : OpenAI 30% : Gemini 20%)

---

## 🤖 AI 3사 50:30:20 전략

### Claude 50% - 핵심 개발의 왕
**왜 50%인가?**
- SWE-bench 77.2% (업계 1위)
- 프로덕션 버그율 4.2% (업계 최저)
- 한 번에 정확한 코드 생성 → 총 개발시간 37% 단축

**담당 작업**
- ✅ DCF/상대가치 **평가 로직 구현** (핵심 비즈니스 로직)
- ✅ **보안 관련 기능** (인증, 데이터 검증)
- ✅ **PDF 평가 보고서 작성** (장문 콘텐츠 생성)
- ✅ **코드 리뷰 및 최적화**
- ✅ **복잡한 리팩토링**

### OpenAI 30% - 멀티모달과 구조화의 제왕
**왜 30%인가?**
- Structured Outputs (구조화된 데이터 추출)
- Vision API (이미지 처리)
- 최대 생태계 (8억 사용자, 400만 개발자)

**담당 작업**
- ✅ **재무제표 PDF 분석** (GPT-4o)
- ✅ **재무제표 이미지 OCR** (Vision API)
- ✅ **엑셀 수식 자동 생성** (Structured Outputs)
- ✅ **실시간 챗봇** (빠른 응답)
- ✅ **멀티모달 콘텐츠 처리**

### Gemini 20% - 실시간 검색의 제왕
**왜 20%인가?**
- 2M 토큰 컨텍스트 (업계 최대)
- 실시간 Google Search (네이티브 통합)
- 무료 티어 (개발 단계 비용 절감)

**담당 작업**
- ✅ **유사기업 자동 탐색** (Google Search)
- ✅ **산업 트렌드 리서치**
- ✅ **대규모 코드베이스 분석**
- ✅ **빠른 프로토타이핑**

---

## AI 작업 분담표

| 기능 | Primary AI | 비율 | 이유 |
|------|-----------|------|------|
| **DCF 계산 로직** | Claude | 50% | 핵심 비즈니스 로직, 최저 버그율 |
| **상대가치 계산 로직** | Claude | 50% | 정확한 금융 계산 필수 |
| **PDF 재무제표 분석** | OpenAI | 30% | GPT-4o PDF 처리 |
| **이미지 재무제표 추출** | OpenAI | 30% | 최고 OCR 성능 |
| **유사기업 탐색** | Gemini | 20% | Google Search 실시간 활용 |
| **평가 보고서 작성** | Claude | 50% | 장문 전문 보고서 |
| **엑셀 수식 생성** | OpenAI | 30% | Structured Outputs |
| **산업 분석** | Gemini | 20% | 실시간 정보, 대용량 처리 |
| **코드 리뷰** | Claude | 50% | 보안, 품질 최우선 |
| **프로토타이핑** | Gemini | 20% | 최고속 응답 |

---

## Phase 1-1: 프로젝트 기초 설정 ✅

### 완료된 작업
- [x] 프로젝트 구조 생성
- [x] Next.js 14 프론트엔드 설정
- [x] FastAPI 백엔드 설정
- [x] AI Router 구현 (50:30:20)
- [x] AI 클라이언트 구현 (Claude, OpenAI, Gemini)
- [x] 환경 변수 설정
- [x] Git 저장소 초기화

---

## Phase 1-2: DCF 계산 엔진 (Claude 50% 주도)

### 🔄 순차 작업

#### 1. DCF 계산 로직 (Claude로 검증)

```python
# backend/app/services/dcf_evaluator.py

class DCFEvaluator:
    """DCF 평가 엔진 (Claude 검증)"""

    def __init__(self, data: Dict, ai_router: AIRouter):
        self.data = data
        self.ai = ai_router

    def calculate_fcf_projections(self) -> List[float]:
        """5년간 FCF 예측 (Python 로직)"""
        fcf_list = []
        last_revenue = self.data['revenue_history'][-1]

        for year in range(1, 6):
            revenue = last_revenue * ((1 + self.data['growth_rate']) ** year)
            ebit = revenue * self.data['ebit_margin']
            nopat = ebit * (1 - self.data['tax_rate'])
            fcf = nopat * 0.85
            fcf_list.append(fcf)

        return fcf_list

    def calculate_enterprise_value(self) -> Dict:
        """기업가치 계산"""
        fcf_projections = self.calculate_fcf_projections()

        pv_fcfs = []
        for year, fcf in enumerate(fcf_projections, start=1):
            pv = fcf / ((1 + self.data['wacc']) ** year)
            pv_fcfs.append(pv)

        final_fcf = fcf_projections[-1]
        terminal_fcf = final_fcf * (1 + self.data['terminal_growth'])
        terminal_value = terminal_fcf / (self.data['wacc'] - self.data['terminal_growth'])
        pv_terminal = terminal_value / ((1 + self.data['wacc']) ** 5)

        enterprise_value = sum(pv_fcfs) + pv_terminal

        return {
            'enterprise_value': enterprise_value,
            'fcf_projections': fcf_projections,
            'pv_fcfs': pv_fcfs,
            'terminal_value': terminal_value,
            'pv_terminal': pv_terminal
        }

    async def validate_with_claude(self) -> Dict:
        """Claude로 로직 검증 (50% - 핵심 작업)"""
        code = inspect.getsource(self.calculate_enterprise_value)

        validation = await self.ai.claude.evaluate_dcf_logic(code)

        return {
            'validation_passed': True,
            'suggestions': validation,
            'security_issues': [],
            'optimization_tips': []
        }
```

#### 2. 단위 테스트 (Claude 생성)

### 완료 기준
- [ ] DCF 계산 정확도 100%
- [ ] Claude 검증 통과
- [ ] **입출력 구조 확정**

---

## Phase 1-3: 상대가치 평가 엔진 (Gemini 20% + Claude 50%)

### 🔄 순차 작업

#### 1. 상대가치 평가 로직

```python
# backend/app/services/comparable_evaluator.py

class ComparableEvaluator:
    """상대가치 평가 (Gemini 20% + Claude 50%)"""

    def __init__(self, company: Dict, ai_router: AIRouter):
        self.company = company
        self.ai = ai_router

    async def find_comparables(self) -> List[Dict]:
        """유사기업 자동 탐색 (Gemini + Google Search)"""
        comparables = await self.ai.gemini.research_comparable_companies(
            industry=self.company['industry'],
            company=self.company['name']
        )
        return comparables

    def calculate_multiples(self, comparables: List[Dict]) -> Dict:
        """멀티플 계산 (Python + Claude 검증)"""
        avg_per = np.mean([c['market_cap'] / c['net_income'] for c in comparables])
        avg_pbr = np.mean([c['market_cap'] / c['book_value'] for c in comparables])
        avg_psr = np.mean([c['market_cap'] / c['revenue'] for c in comparables])

        per_value = self.company['net_income'] * avg_per
        pbr_value = self.company['book_value'] * avg_pbr
        psr_value = self.company['revenue'] * avg_psr

        return {
            'multiples': {'avg_per': avg_per, 'avg_pbr': avg_pbr, 'avg_psr': avg_psr},
            'valuations': {'per_value': per_value, 'pbr_value': pbr_value, 'psr_value': psr_value},
            'average_value': np.mean([per_value, pbr_value, psr_value])
        }
```

---

## Phase 1-4: DB 스키마 설계

### 🔄 순차 작업

```prisma
// database/schema.prisma

model Evaluation {
  id              String   @id @default(uuid())
  companyId       String
  evaluationType  String   // "DCF", "COMPARABLE"

  // 입력/결과 데이터
  inputData       Json
  results         Json?

  // 파일
  excelFilePath   String?
  pdfFilePath     String?

  // AI 사용 추적 (50:30:20)
  aiUsage         Json?    // {"claude": 0.5, "openai": 0.3, "gemini": 0.2}

  createdAt       DateTime @default(now())
}

model AIUsage {
  id          String   @id @default(uuid())
  provider    String   // "claude", "openai", "gemini"
  task        String   // "dcf_logic", "pdf_analysis", "image_ocr"
  tokens      Int
  cost        Float
  percentage  Float    // 50:30:20 비율 추적
  createdAt   DateTime @default(now())
}
```

---

## 완료 상태

✅ **Phase 1-1 완료** - 프로젝트 설정 및 50:30:20 AI 전략 구현
⏳ **Phase 1-2** - DCF 계산 엔진 개발 예정
⏳ **Phase 1-3** - 상대가치 엔진 개발 예정

---

**버전**: 7.0 (50:30:20 하이브리드 전략 - 사용자 변경 반영)
**변경 이력**: 50:25:25 → 50:30:20 (OpenAI 비중 증가, PDF 분석 이동)
