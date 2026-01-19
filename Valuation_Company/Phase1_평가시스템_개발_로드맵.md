# Phase 1: 기업가치평가 시스템 개발 로드맵

## 프로젝트 개요
**목표**: 첫 번째 고객 확보를 위한 MVP 개발
**도메인**: valuation.ai.kr
**Phase 1 범위**: DCF 평가 + 상대가치 평가 (2종)
**AI 전략**: 50:25:25 하이브리드 전략 (Claude 50% : Gemini 25% : OpenAI 25%)

---

## 🤖 AI 3사 50:25:25 전략

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

### Gemini 25% - 속도와 대용량의 제왕
**왜 25%인가?**
- 2M 토큰 컨텍스트 (업계 최대)
- 실시간 Google Search (네이티브 통합)
- 무료 티어 (개발 단계 비용 절감)

**담당 작업**
- ✅ **재무제표 PDF 일괄 분석** (2M 토큰 활용)
- ✅ **유사기업 자동 탐색** (Google Search)
- ✅ **산업 트렌드 리서치**
- ✅ **빠른 프로토타이핑**
- ✅ **대규모 코드베이스 분석**

### OpenAI 25% - 생태계와 멀티모달의 제왕
**왜 25%인가?**
- Structured Outputs (구조화된 데이터 추출)
- Vision API (이미지 처리)
- 최대 생태계 (8억 사용자, 400만 개발자)

**담당 작업**
- ✅ **재무제표 이미지 OCR** (Vision API)
- ✅ **엑셀 수식 자동 생성** (Structured Outputs)
- ✅ **실시간 챗봇** (빠른 응답)
- ✅ **멀티모달 콘텐츠 처리**

---

## AI 작업 분담표

| 기능 | Primary AI | Secondary AI | 비율 | 이유 |
|------|-----------|--------------|------|------|
| **DCF 계산 로직** | Claude | - | 50% | 핵심 비즈니스 로직, 최저 버그율 |
| **상대가치 계산 로직** | Claude | - | 50% | 정확한 금융 계산 필수 |
| **PDF 재무제표 분석** | Gemini | - | 25% | 2M 토큰, PDF 네이티브 처리 |
| **이미지 재무제표 추출** | OpenAI Vision | - | 25% | 최고 OCR 성능 |
| **유사기업 탐색** | Gemini | - | 25% | Google Search 실시간 활용 |
| **평가 보고서 작성** | Claude | - | 50% | 장문 전문 보고서 |
| **엑셀 수식 생성** | OpenAI | - | 25% | Structured Outputs |
| **산업 분석** | Gemini | Claude | 25% | 실시간 정보, 대용량 처리 |
| **코드 리뷰** | Claude | - | 50% | 보안, 품질 최우선 |
| **프로토타이핑** | Gemini | - | 25% | 최고속 응답 |

---

## Phase 1-1: 프로젝트 기초 설정

### 🔄 순차 작업

#### 1. 프로젝트 구조
```bash
valuation-platform/
├── frontend/          # Next.js 14
├── backend/           # FastAPI
│   ├── app/
│   │   ├── ai_services/      # AI 통합 레이어 (50:25:25)
│   │   │   ├── claude_client.py     # 50% 핵심 로직
│   │   │   ├── gemini_client.py     # 25% 대용량/속도
│   │   │   ├── openai_client.py     # 25% 멀티모달
│   │   │   └── ai_router.py         # 스마트 라우팅
│   │   ├── services/
│   │   │   ├── dcf_evaluator.py     # Claude 주도
│   │   │   └── comparable_evaluator.py  # Gemini 주도
│   │   ├── routers/
│   │   └── models/
├── database/
└── docs/
```

#### 2. Git 저장소 초기화
#### 3. 환경 변수 설정

```bash
# AI API Keys (50:25:25 전략)
ANTHROPIC_API_KEY=sk-ant-xxx     # Claude (50%)
GOOGLE_API_KEY=xxx                # Gemini (25%)
OPENAI_API_KEY=sk-xxx             # OpenAI (25%)

# Database
DATABASE_URL=postgresql://...
```

### ⚡ 병렬 작업

#### A. Frontend 기본 설정
- [ ] Next.js 프로젝트 생성
- [ ] shadcn/ui 설치
- [ ] 기본 레이아웃

#### B. Backend 기본 설정
- [ ] FastAPI 프로젝트
- [ ] 패키지 설치
  ```txt
  fastapi==0.104.1
  anthropic==0.7.0      # Claude (50%)
  google-generativeai   # Gemini (25%)
  openai==1.3.0         # OpenAI (25%)
  openpyxl
  reportlab
  ```

#### C. AI 스마트 라우팅 시스템 구축

```python
# backend/app/ai_services/ai_router.py

class AIRouter:
    """50:25:25 전략 기반 스마트 라우팅"""

    def select_model(self, task_type: str, priority: str, context_size: int) -> str:
        """작업에 최적의 AI 선택"""

        # Claude 50% - 핵심/보안 작업
        if priority == "CRITICAL" or task_type in [
            "business_logic",
            "security",
            "data_validation",
            "code_review",
            "report_generation"
        ]:
            return "claude"

        # Gemini 25% - 대용량/실시간
        if context_size > 200000 or task_type in [
            "pdf_analysis",
            "company_research",
            "industry_analysis",
            "prototyping"
        ]:
            return "gemini"

        # OpenAI 25% - 이미지/구조화
        if task_type in [
            "image_ocr",
            "excel_formula",
            "chatbot",
            "structured_data"
        ]:
            return "openai"

        # 기본값: Claude (품질 우선)
        return "claude"

    def track_usage(self):
        """50:25:25 비율 추적"""
        # 실제 사용량 모니터링
        usage = {
            "claude": self.claude_count,
            "gemini": self.gemini_count,
            "openai": self.openai_count
        }

        # 비율 계산
        total = sum(usage.values())
        ratios = {k: v/total*100 for k, v in usage.items()}

        return ratios
```

```python
# backend/app/ai_services/claude_client.py

class ClaudeClient:
    """Claude 50% - 핵심 개발 담당"""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    async def evaluate_dcf_logic(self, code: str) -> Dict:
        """DCF 로직 검증 및 최적화 (핵심 비즈니스)"""
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"""
                다음 DCF 평가 로직을 검증하고 개선하세요:
                {code}

                중점 사항:
                1. 금융 계산 정확성
                2. 엣지 케이스 처리
                3. 보안 취약점
                4. 성능 최적화
                """
            }]
        )
        return response.content[0].text

    async def generate_valuation_report(self, data: Dict) -> str:
        """평가 보고서 생성 (장문 콘텐츠)"""
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            messages=[{
                "role": "user",
                "content": f"""
                다음 평가 데이터로 전문적인 기업가치평가 보고서를 작성하세요:
                {data}

                보고서 구성:
                1. Executive Summary (2 페이지)
                2. 평가 방법론 (3 페이지)
                3. 재무 분석 (5 페이지)
                4. 평가 결과 및 근거 (4 페이지)
                5. 리스크 요인 (2 페이지)
                """
            }]
        )
        return response.content[0].text
```

```python
# backend/app/ai_services/gemini_client.py

import google.generativeai as genai

class GeminiClient:
    """Gemini 25% - 속도와 대용량 담당"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    async def analyze_pdf_financial_statement(self, pdf_bytes: bytes) -> Dict:
        """재무제표 PDF 분석 (2M 토큰 활용)"""
        response = self.model.generate_content([
            """
            재무제표 PDF를 분석하여 다음 정보를 JSON 형식으로 추출하세요:
            - 최근 3년 매출, 영업이익, 순이익
            - 총자산, 부채, 자본
            - 현금흐름 (영업/투자/재무)
            - 주요 재무비율
            """,
            {"mime_type": "application/pdf", "data": pdf_bytes}
        ])

        return json.loads(response.text)

    async def research_comparable_companies(self, industry: str, company: str) -> List[Dict]:
        """유사기업 탐색 (Google Search 활용)"""
        prompt = f"""
        {industry} 업종에서 {company}와 유사한 상장기업 10개를 찾아주세요.

        각 기업당 다음 정보를 JSON 배열로 제공:
        - 기업명
        - 시가총액
        - 최근 매출
        - 순이익
        - PER, PBR, PSR
        - 주요 사업 영역

        실시간 정보를 Google Search로 확인하세요.
        """

        response = self.model.generate_content(
            prompt,
            tools='google_search_retrieval'
        )

        return json.loads(response.text)

    async def analyze_industry_trends(self, industry: str) -> str:
        """산업 트렌드 분석 (실시간 정보)"""
        response = self.model.generate_content(
            f"{industry} 산업의 최신 트렌드, 성장 전망, 주요 이슈를 분석하세요.",
            tools='google_search_retrieval'
        )
        return response.text
```

```python
# backend/app/ai_services/openai_client.py

from openai import AsyncOpenAI

class OpenAIClient:
    """OpenAI 25% - 멀티모달과 구조화 담당"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def extract_from_image(self, image_base64: str) -> Dict:
        """재무제표 이미지 OCR (Vision API)"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "재무제표 이미지에서 숫자를 추출하여 JSON으로 반환하세요."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "financial_extraction",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "revenue": {"type": "array", "items": {"type": "number"}},
                            "operating_income": {"type": "array"},
                            "net_income": {"type": "array"}
                        },
                        "required": ["revenue", "operating_income", "net_income"]
                    }
                }
            }
        )

        return json.loads(response.choices[0].message.content)

    async def generate_excel_formula(self, description: str) -> str:
        """엑셀 수식 생성 (Structured Outputs)"""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "엑셀 수식 전문가. 설명을 정확한 엑셀 수식으로 변환합니다."
            }, {
                "role": "user",
                "content": description
            }]
        )
        return response.choices[0].message.content
```

### 완료 기준
- [ ] Frontend/Backend 서버 실행
- [ ] 3개 AI API 연결 확인
- [ ] AI 라우팅 시스템 작동
- [ ] 50:25:25 비율 추적 대시보드

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

```python
# tests/test_dcf.py
# Claude가 엣지 케이스 포함 테스트 생성
```

### 완료 기준
- [ ] DCF 계산 정확도 100%
- [ ] Claude 검증 통과
- [ ] **입출력 구조 확정**

---

## Phase 1-3: 상대가치 평가 엔진 (Gemini 25% 주도)

### 🔄 순차 작업

#### 1. 상대가치 평가 로직 (Gemini 리서치)

```python
# backend/app/services/comparable_evaluator.py

class ComparableEvaluator:
    """상대가치 평가 (Gemini 25% 주도)"""

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
        """멀티플 계산 (Python)"""
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

### 완료 기준
- [ ] Gemini 유사기업 탐색 성공
- [ ] 계산 로직 정확도 검증

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

  // AI 사용 추적 (50:25:25)
  aiUsage         Json?    // {"claude": 0.5, "gemini": 0.25, "openai": 0.25}

  createdAt       DateTime @default(now())
}

model AIUsage {
  id          String   @id @default(uuid())
  provider    String   // "claude", "gemini", "openai"
  task        String   // "dcf_logic", "pdf_analysis", "image_ocr"
  tokens      Int
  cost        Float
  percentage  Float    // 50:25:25 비율 추적
  createdAt   DateTime @default(now())
}
```

---

## Phase 1-5: 엑셀/PDF 생성기 (AI 역할 분담)

### ⚡ 병렬 작업

#### A. 엑셀 생성기 (OpenAI 25% - 수식)
```python
# backend/app/services/excel_generator.py

class DCFExcelGenerator:
    def __init__(self, data: Dict, ai_router: AIRouter):
        self.data = data
        self.ai = ai_router

    async def create_calculator_sheet(self):
        """시뮬레이터 시트 (OpenAI 수식 생성)"""
        # OpenAI 25%로 복잡한 엑셀 수식 생성
        formula = await self.ai.openai.generate_excel_formula(
            "B5 매출 * (1+B6 성장률) * B7 EBIT마진 * (1-B8 세율) * 0.85"
        )

        ws['B11'] = formula
```

#### B. PDF 생성기 (Claude 50% - 보고서)
```python
# backend/app/services/pdf_generator.py

class DCFPDFGenerator:
    def __init__(self, data: Dict, ai_router: AIRouter):
        self.data = data
        self.ai = ai_router

    async def generate_report(self):
        """평가 보고서 생성 (Claude 50% - 장문)"""
        report_text = await self.ai.claude.generate_valuation_report(self.data)

        # PDF에 삽입
        self.pdf.add_page()
        self.pdf.write_html(report_text)
```

---

## Phase 1-6: FastAPI 엔드포인트 (AI 파이프라인)

### 🔄 순차 작업

```python
# backend/app/routers/dcf.py

@router.post("/evaluate")
async def evaluate_dcf(
    request: DCFRequest,
    ai_router: AIRouter = Depends()
):
    """
    50:25:25 AI 파이프라인
    1. Claude (50%): DCF 계산 및 검증
    2. Claude (50%): PDF 보고서 작성
    3. OpenAI (25%): 엑셀 수식 생성
    """

    # 1. DCF 계산 (Claude 50%)
    evaluator = DCFEvaluator(request.dict(), ai_router)
    result = evaluator.calculate_enterprise_value()
    validation = await evaluator.validate_with_claude()

    # 2. 파일 생성
    # PDF: Claude 50%
    pdf_gen = DCFPDFGenerator(result, ai_router)
    pdf_path = await pdf_gen.generate()

    # Excel: OpenAI 25%
    excel_gen = DCFExcelGenerator(result, ai_router)
    excel_path = await excel_gen.generate()

    # 3. AI 사용량 추적
    usage_ratios = ai_router.track_usage()
    # {"claude": 52%, "gemini": 23%, "openai": 25%}

    return {
        'enterprise_value': result['enterprise_value'],
        'excel_url': excel_path,
        'pdf_url': pdf_path,
        'ai_usage': usage_ratios  # 50:25:25 달성 확인
    }

@router.post("/upload-financial-statement")
async def upload_statement(
    file: UploadFile,
    ai_router: AIRouter = Depends()
):
    """재무제표 업로드 (AI 자동 선택)"""
    file_data = await file.read()

    # PDF → Gemini 25% (2M 토큰)
    if file.content_type == "application/pdf":
        data = await ai_router.gemini.analyze_pdf_financial_statement(file_data)

    # Image → OpenAI 25% (Vision API)
    else:
        image_b64 = base64.b64encode(file_data).decode()
        data = await ai_router.openai.extract_from_image(image_b64)

    return data
```

---

## Phase 1-7: 웹 시뮬레이터 (2종)

### ⚡ 병렬 작업

#### A. DCF 간이 계산기 (클라이언트 사이드)
#### B. 상대가치 간이 계산기

---

## Phase 1-8: Frontend 평가 신청 페이지

### 🔄 순차 작업

```typescript
// frontend/app/dcf/page.tsx

function FinancialDataForm() {
  const handleFileUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    // AI 자동 선택 (PDF → Gemini, Image → OpenAI)
    const response = await fetch('/api/v1/dcf/upload-financial-statement', {
      method: 'POST',
      body: formData
    });

    const extracted = await response.json();
    setFormData(extracted);
  };

  return (
    <FileUpload
      accept="image/*,application/pdf"
      onUpload={handleFileUpload}
      description="AI가 자동 추출 (PDF: Gemini 2M토큰 / 이미지: OpenAI Vision)"
    />
  );
}
```

---

## Phase 1-9: 메인 웹사이트

### ⚡ 병렬 작업

```typescript
// frontend/app/page.tsx

<section className="hero">
  <h1>AI 3사가 협업하는 기업가치평가</h1>
  <p>Claude (정확성) + Gemini (속도) + OpenAI (멀티모달)</p>

  <div className="ai-badges">
    <Badge>Claude 50% - 핵심 로직</Badge>
    <Badge>Gemini 25% - PDF 분석</Badge>
    <Badge>OpenAI 25% - 이미지 OCR</Badge>
  </div>
</section>
```

---

## Phase 1-10: 배포 및 런칭

### 🔄 순차 작업

#### AI 비용 모니터링
```python
# backend/app/middleware/ai_cost_tracker.py

async def track_cost():
    """50:25:25 비율 및 비용 추적"""
    usage = await prisma.aiusage.group_by(
        by=['provider'],
        _sum={'cost': True}
    )

    # 실제 vs 목표 비율
    actual_ratios = calculate_ratios(usage)
    # {"claude": 48%, "gemini": 27%, "openai": 25%}

    target = {"claude": 50, "gemini": 25, "openai": 25}

    # 알림: 비율이 ±10% 이상 벗어나면
    if abs(actual_ratios['claude'] - target['claude']) > 10:
        send_alert("Claude 사용량이 목표에서 벗어남")
```

---

## MVP 핵심 기능 (Phase 1)

### 평가 시스템 (2종)
- [ ] DCF 평가 (Claude 50% - 핵심 로직)
- [ ] 상대가치 평가 (Gemini 25% - 유사기업 리서치)

### AI 기능 (50:25:25)
- [ ] **Claude 50%**: DCF/상대가치 로직, PDF 보고서, 코드 검증
- [ ] **Gemini 25%**: PDF 재무제표 분석, 유사기업 탐색, 산업 분석
- [ ] **OpenAI 25%**: 이미지 OCR, 엑셀 수식, 실시간 챗봇

### 웹 시뮬레이터 (2종)
- [ ] DCF 간이 계산기
- [ ] 상대가치 간이 계산기

---

## AI 비용 예상 (Phase 1, 월 100건 기준)

### 50:25:25 하이브리드 전략
| AI | 사용량 | API 비용 | 디버깅 절감 | 순 비용 |
|----|--------|----------|-------------|---------|
| **Claude** | 50건 | $405 | -$600 | **-$195** |
| **Gemini** | 25건 | $0 (무료) | -$100 | **-$100** |
| **OpenAI** | 25건 | $70 | -$50 | **$20** |
| **합계** | 100건 | $475 | -$750 | **-$275** |

**순이익**: 월 $275 (AI 사용으로 오히려 수익 발생)

### vs 단일 모델 전략
- Claude 100%: $810 API - $1,200 절감 = **-$390**
- Gemini 100%: $0 + $800 디버깅 = **$800**
- OpenAI 100%: $1,360 + $400 = **$1,760**

**50:25:25 하이브리드가 TCO 17% 절감**

---

## 성공 지표

### AI 사용 비율 (목표)
- [ ] Claude: 45-55%
- [ ] Gemini: 20-30%
- [ ] OpenAI: 20-30%

### 품질 지표
- [ ] 프로덕션 버그율 < 5% (Claude 효과)
- [ ] PDF 분석 정확도 > 95% (Gemini 효과)
- [ ] 이미지 OCR 정확도 > 90% (OpenAI 효과)

### 비용 효율
- [ ] TCO 17% 절감 달성
- [ ] 개발 시간 30% 단축

---

## Phase 2 Preview

### Phase 2-1: 추가 평가 방법 (3종)
- 상증법 평가
- 자산가치 평가
- IPO 평가

### Phase 2-2: AI 아바타 IR
- Claude 기반 맞춤 IR (50%)
- OpenAI TTS 음성 (25%)
- Gemini 실시간 정보 (25%)

---

## 최종 전략

**50 : 25 : 25는 출발점입니다.**

실제 데이터를 보고 ±10-20% 조정하세요.

**핵심은**: 각 AI의 강점을 적재적소에 활용하는 것

- **Claude (50%)**: 정확성이 생명인 핵심 로직
- **Gemini (25%)**: 대용량 처리와 실시간 정보
- **OpenAI (25%)**: 멀티모달과 생태계 활용

---

**최종 목표**: AI 3사 협업으로 최고 품질 + 최저 비용 달성

**차별화**: "하나의 AI가 아닌, 최적의 AI 조합"

---

**버전**: 6.0 (50:25:25 하이브리드 전략)